#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified exercise abstraction for the daily trainer.

Provides Exercise ABC and concrete implementations for vocabulary,
conjugation, and grammar exercises, plus a factory to load all due items.
"""

import csv
import json
import random
import re
from abc import ABC, abstractmethod
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from srs_core import SRSStats, load_stats

import yaml

CONFIG_FILE = Path("daily_trainer_config.yaml")
_LEGACY_CONFIG_FILE = Path("daily_trainer_config.json")

ALL_BLOCKS = ("vocabulary", "conjugation", "grammar", "sentence", "conjugation_sentence")

# Defaults for session settings
_DEFAULTS = {
    "max_items": 100,
    "max_new": 10,
    "enabled_blocks": list(ALL_BLOCKS),
    "vocabulary_categories": [],
    "excluded_categories": [],
    "fuzzy_threshold": 0.85,
    "sentence_threshold": 0.80,
    "session_time_limit": 900,
}


def _load_config() -> dict:
    """Load configuration from YAML file, falling back to legacy JSON."""
    if CONFIG_FILE.is_file():
        with CONFIG_FILE.open(encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    elif _LEGACY_CONFIG_FILE.is_file():
        with _LEGACY_CONFIG_FILE.open(encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}
    return {**_DEFAULTS, **config}


def _load_enabled_blocks() -> set[str]:
    """Return the set of enabled block names (lowercased).

    A missing or empty `enabled_blocks` list defaults to all blocks enabled.
    """
    config = _load_config()
    blocks = config.get("enabled_blocks") or list(ALL_BLOCKS)
    return {str(b).strip().lower() for b in blocks}


def _is_block_enabled(type_name: str) -> bool:
    return type_name.lower() in _load_enabled_blocks()


def _load_vocab_filter() -> tuple[set[str], set[str]]:
    """Return (whitelist, blacklist) of vocabulary categories.

    Whitelist (`vocabulary_categories`) takes precedence when non-empty.
    `excluded_categories` is consulted as a legacy fallback.
    """
    config = _load_config()
    whitelist = {c.strip() for c in config.get("vocabulary_categories", []) if c.strip()}
    blacklist = {c.strip() for c in config.get("excluded_categories", []) if c.strip()}
    return whitelist, blacklist


def _vocab_category_allowed(category: str) -> bool:
    whitelist, blacklist = _load_vocab_filter()
    if whitelist:
        return category in whitelist
    return category not in blacklist


# ----------------------------------------------------------------------
# Exercise ABC
# ----------------------------------------------------------------------
class Exercise(ABC):
    """A single reviewable exercise."""

    key: str              # SRS tracking key
    type_name: str        # "Vocabulary" / "Conjugation" / "Grammar"
    stats_file: Path      # Which SRS stats file this belongs to

    @abstractmethod
    def get_prompt(self) -> str:
        """Question text to display."""

    @abstractmethod
    def get_correct(self) -> str:
        """Correct answer text (for display after answering)."""

    @abstractmethod
    def check(self, user_input: str) -> bool:
        """Check user's answer. Returns True if correct."""

    def get_hint(self) -> str | None:
        """Optional hint text."""
        return None


# ----------------------------------------------------------------------
# Fuzzy answer matching
# ----------------------------------------------------------------------
def _expand_parens(text: str) -> list[str]:
    """Expand parenthetical optional parts into all accepted forms.

    "to sit (down)" -> ["to sit (down)", "to sit down", "to sit"]
    "a (female) friend" -> ["a (female) friend", "a female friend", "a friend"]
    """
    forms = {text}
    # With parens removed entirely (optional part dropped)
    stripped = re.sub(r"\s*\([^)]*\)\s*", " ", text).strip()
    stripped = re.sub(r"  +", " ", stripped)
    forms.add(stripped)
    # With parens removed but content kept (user typed the full phrase)
    inlined = text.replace("(", "").replace(")", "").strip()
    inlined = re.sub(r"  +", " ", inlined)
    forms.add(inlined)
    return list(forms)


def _fuzzy_match(user: str, variants: list[str], threshold: float = 0.85) -> bool:
    """Check if user input matches any variant, with parenthetical expansion
    and fuzzy matching (85% similarity threshold)."""
    accepted: list[str] = []
    for v in variants:
        accepted.extend(_expand_parens(v.strip().lower()))

    # Exact match first
    if user in accepted:
        return True

    # Fuzzy match
    for answer in accepted:
        if SequenceMatcher(None, user, answer).ratio() >= threshold:
            return True

    return False


def _normalize_for_token_match(text: str) -> str:
    """Lowercase and split on punctuation for whole-token matching.

    Everything that isn't a letter (Latin + accents) or digit becomes a
    space, so apostrophes/hyphens ("j'ai", "peut-être") split into tokens
    and trailing punctuation ("vienne.") doesn't fuse to the verb. Accents
    are kept — they are meaningful in conjugation (parlé vs parle).
    """
    t = text.lower()
    t = re.sub(r"[^0-9a-zÀ-ſ]+", " ", t)
    return t.strip()


def verb_form_present(form: str, sentence: str) -> bool:
    """True if `form` appears as whole token(s) in `sentence`.

    Space-padded containment on normalized text gives word-boundary matching
    for single- and multi-word forms ("est allée", "me sens") without partial
    matches inside longer words. Shared by grading and the data validator so
    both agree on what counts as "the verb is present".
    """
    padded_sentence = f" {_normalize_for_token_match(sentence)} "
    padded_form = f" {_normalize_for_token_match(form)} "
    return padded_form in padded_sentence


# Register carried by the subject pronoun, used to disambiguate the English
# prompt: "you" -> tu (informal) / vous (formal); "we" -> on (informal) /
# nous (formal). Other pronouns carry no register marker.
_PRONOUN_REGISTER = {
    "tu": "informal",
    "on": "informal",
    "vous": "formal",
    "nous": "formal",
}


def register_for_pronoun(pronoun: str) -> str | None:
    """Return "informal"/"formal" for register-bearing pronouns, else None."""
    return _PRONOUN_REGISTER.get(pronoun.strip().lower())


# ----------------------------------------------------------------------
# Vocabulary Exercise
# ----------------------------------------------------------------------
FLASHCARD_STATS_FILE = Path(".flashcard_data/card_stats.json")


class VocabularyExercise(Exercise):
    type_name = "Vocabulary"
    stats_file = FLASHCARD_STATS_FILE

    def __init__(self, french: str, english: str, french_variants: list[str],
                 english_variants: list[str], french_synonyms: list[str],
                 direction: str, key: str,
                 example_sentence: dict | None = None):
        self.french = french
        self.english = english
        self.french_variants = french_variants
        self.english_variants = english_variants
        self.french_synonyms = french_synonyms
        self.direction = direction  # "french" or "english"
        self.key = key
        self.example_sentence = example_sentence

    def get_example(self) -> tuple[str, str] | None:
        """Return (sentence, translation) if an example is available."""
        if self.example_sentence:
            return (self.example_sentence["sentence"],
                    self.example_sentence["translation"])
        return None

    def get_prompt(self) -> str:
        if self.direction == "english":
            return self.french
        return self.english

    def get_correct(self) -> str:
        if self.direction == "english":
            return " / ".join(self.english_variants) if len(self.english_variants) > 1 else self.english
        all_french = self.french_variants + self.french_synonyms
        return " / ".join(all_french) if len(all_french) > 1 else self.french

    def check(self, user_input: str) -> bool:
        user = user_input.strip().lower()
        if self.direction == "english":
            variants = self.english_variants
        else:
            variants = self.french_variants + self.french_synonyms
        threshold = _load_config()["fuzzy_threshold"]
        return _fuzzy_match(user, variants, threshold=threshold)

    def get_hint(self) -> str | None:
        if self.direction == "english":
            answer = self.english
        else:
            answer = self.french
        # Show first letter and word length
        words = answer.split()
        hints = []
        for w in words:
            if len(w) <= 1:
                hints.append(w)
            else:
                hints.append(w[0] + "_" * (len(w) - 1))
        return " ".join(hints)


# ----------------------------------------------------------------------
# Conjugation Exercise
# ----------------------------------------------------------------------
CONJUGATION_STATS_FILE = Path(".conjugation_data/conjugation_stats.json")


class ConjugationExercise(Exercise):
    type_name = "Conjugation"
    stats_file = CONJUGATION_STATS_FILE

    def __init__(self, verb: str, tense: str, tense_display: str,
                 pronoun: str, correct_form: str, translation: str, key: str,
                 regularity: str = ""):
        self.verb = verb
        self.tense = tense
        self.tense_display = tense_display
        self.pronoun = pronoun
        self.correct_form = correct_form
        self.translation = translation
        self.key = key
        self.regularity = regularity

    def get_prompt(self) -> str:
        from conjugation_engine import je_elides_before
        subject = "j'" if (self.pronoun == "je" and je_elides_before(self.correct_form)) else f"{self.pronoun} "
        return f"{self.verb} ({self.translation}) — {self.tense_display}\n{subject}..."

    def get_correct(self) -> str:
        from conjugation_engine import join_pronoun
        return join_pronoun(self.pronoun, self.correct_form)

    def check(self, user_input: str) -> bool:
        return user_input.strip().lower() == self.correct_form.lower()

    def get_hint(self) -> str | None:
        from conjugation_engine import get_pattern_hint
        pattern = get_pattern_hint(self.verb, self.tense)
        if pattern:
            return pattern
        parts = []
        if self.regularity:
            parts.append(self.regularity)
        if len(self.correct_form) >= 3:
            parts.append(f"Starts with: {self.correct_form[:2]}...")
        return " — ".join(parts) if parts else None


# ----------------------------------------------------------------------
# Grammar Exercise
# ----------------------------------------------------------------------
GRAMMAR_STATS_FILE = Path(".grammar_data/grammar_stats.json")


class GrammarExercise(Exercise):
    type_name = "Grammar"
    stats_file = GRAMMAR_STATS_FILE

    def __init__(self, exercise_data: dict, topic_name: str, key: str):
        self.data = exercise_data
        self.topic_name = topic_name
        self.key = key

    def get_prompt(self) -> str:
        topic_display = self.topic_name.replace("_", " ").title()
        before = self.data.get("sentence_before", "")
        after = self.data.get("sentence_after", "")
        context = self.data.get("context", "")
        sentence = f"{topic_display}\n{before} __________ {after}".strip()
        # Show context only when it provides directional cues or
        # French-language context (not the full English translation).
        # The translation is shown after answering via get_translation().
        if context:
            sentence += f"\n({context})"
        return sentence

    def get_translation(self) -> str | None:
        """Return English translation for display after answering."""
        return self.data.get("translation")

    def get_correct(self) -> str:
        before = self.data.get("sentence_before", "")
        after = self.data.get("sentence_after", "")
        answer = self.data["answer"]
        return f"{before} {answer} {after}".strip()

    def check(self, user_input: str) -> bool:
        user = user_input.strip().lower()
        answer = self.data["answer"].lower()
        alternatives = [a.lower() for a in self.data.get("alternatives", [])]
        return user in [answer] + alternatives

    def get_hint(self) -> str | None:
        return self.data.get("hint")


# ----------------------------------------------------------------------
# Sentence Translation Exercise
# ----------------------------------------------------------------------
SENTENCE_STATS_FILE = Path(".sentence_data/sentence_stats.json")


class SentenceExercise(Exercise):
    type_name = "Sentence"
    stats_file = SENTENCE_STATS_FILE

    def __init__(self, sentence_data: dict, direction: str, key: str):
        self.data = sentence_data
        self.direction = direction  # "english" or "french"
        self.key = key

    def get_prompt(self) -> str:
        if self.direction == "english":
            return f"Translate to English:\n{self.data['french']}"
        return f"Translate to French:\n{self.data['english']}"

    def get_correct(self) -> str:
        if self.direction == "english":
            return self.data["english"]
        return self.data["french"]

    def check(self, user_input: str) -> bool:
        user = user_input.strip().lower()
        if self.direction == "english":
            variants = [self.data["english"]] + self.data.get("alternatives_en", [])
        else:
            variants = [self.data["french"]] + self.data.get("alternatives_fr", [])
        threshold = _load_config()["sentence_threshold"]
        return _fuzzy_match(user, variants, threshold=threshold)

    def get_hint(self) -> str | None:
        return self.data.get("hint")


# ----------------------------------------------------------------------
# Conjugation-in-context (English -> French sentence production)
# ----------------------------------------------------------------------
CONJ_SENTENCE_DATA_DIR = Path("conjugation_sentence_data")
CONJ_SENTENCE_STATS_FILE = Path(".conjugation_sentence_data/conjugation_sentence_stats.json")


class ConjugationSentenceExercise(Exercise):
    """Translate an English sentence to French, producing a target conjugation.

    The whole sentence is fuzzy-matched, but the conjugated verb form (derived
    from the engine, the single source of truth) must be present exactly —
    that is the part being drilled.
    """

    type_name = "ConjugationSentence"
    stats_file = CONJ_SENTENCE_STATS_FILE

    def __init__(self, sentence_data: dict, key: str):
        self.data = sentence_data
        self.key = key
        self._expected: str | None = None

    def expected_form(self) -> str:
        """The engine-generated verb form this sentence targets (cached)."""
        if self._expected is None:
            from conjugation_engine import conjugate_one
            self._expected = conjugate_one(
                self.data["verb"], self.data["tense"], self.data["pronoun"]
            )
        return self._expected

    def get_prompt(self) -> str:
        from conjugation_engine import get_tense_display_name
        tense = get_tense_display_name(self.data["tense"])
        # Register disambiguates "you" (tu/vous) and "we" (on/nous).
        register = self.data.get("register") or register_for_pronoun(self.data["pronoun"])
        reg = f", {register}" if register else ""
        return f"Translate to French — {tense}{reg}:\n{self.data['english']}"

    def get_correct(self) -> str:
        return self.data["french"]

    def check(self, user_input: str) -> bool:
        user = user_input.strip()
        # Strict: the target conjugated form must be present (accent-sensitive).
        if not verb_form_present(self.expected_form(), user):
            return False
        # Rest of the sentence: fuzzy match against the reference translation.
        variants = [self.data["french"]] + self.data.get("alternatives_fr", [])
        threshold = _load_config()["sentence_threshold"]
        return _fuzzy_match(user.lower(), variants, threshold=threshold)

    def get_hint(self) -> str | None:
        from conjugation_engine import (
            get_translation, get_pattern_hint, get_tense_display_name,
        )
        verb = self.data["verb"]
        tense = self.data["tense"]
        base = (f"{verb} ({get_translation(verb)}) — "
                f"{get_tense_display_name(tense)}, «{self.data['pronoun']}»")
        pattern = get_pattern_hint(verb, tense)
        return f"{base}\n{pattern}" if pattern else base


# ----------------------------------------------------------------------
# Factory: load all due exercises
# ----------------------------------------------------------------------
def _load_vocab_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load vocabulary cards and return exercises + their stats."""
    csv_path = Path("master_vocabulary.csv")
    if not csv_path.is_file():
        return [], {}

    # Load example sentences
    examples_path = Path("example_sentences.json")
    examples: dict = {}
    if examples_path.is_file():
        with examples_path.open(encoding="utf-8") as f:
            examples = json.load(f)

    stats = load_stats(FLASHCARD_STATS_FILE)

    # Read cards from CSV
    cards = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                category = row[2].strip() if len(row) >= 3 else ""
                if not _vocab_category_allowed(category):
                    continue
                french = row[0]
                english = row[1]
                french_variants = [v.strip() for v in french.split("|")]
                english_variants = [v.strip() for v in english.split("|")]
                key = f"{french_variants[0]}|{english_variants[0]}"
                cards.append({
                    "french": french_variants[0],
                    "english": english_variants[0],
                    "french_variants": french_variants,
                    "english_variants": english_variants,
                    "key": key,
                })

    # Build synonym map: normalized_english -> list of French words
    english_to_french: dict[str, list[str]] = {}
    for card in cards:
        for eng in card["english_variants"]:
            norm_eng = eng.lower().strip()
            if norm_eng not in english_to_french:
                english_to_french[norm_eng] = []
            for fr in card["french_variants"]:
                if fr not in english_to_french[norm_eng]:
                    english_to_french[norm_eng].append(fr)

    exercises = []
    today = date.today().isoformat()
    for card in cards:
        key = card["key"]
        stat = stats.get(key)
        if stat and stat.due_date > today:
            continue

        # Build synonyms for this card
        synonyms = set()
        for eng in card["english_variants"]:
            for fr in english_to_french.get(eng.lower().strip(), []):
                if fr not in card["french_variants"]:
                    synonyms.add(fr)

        # Look up example sentence by lowercase French word
        example = examples.get(card["french"].lower())

        direction = random.choice(["english", "french"])
        exercises.append(VocabularyExercise(
            french=card["french"],
            english=card["english"],
            french_variants=card["french_variants"],
            english_variants=card["english_variants"],
            french_synonyms=list(synonyms),
            direction=direction,
            key=key,
            example_sentence=example,
        ))

    return exercises, stats


def _load_conjugation_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load conjugation exercises and return exercises + their stats."""
    from conjugation_engine import (
        conjugate, get_all_verbs, get_translation,
        get_tense_display_name, get_all_tenses, get_random_pronouns,
        get_verb_regularity,
    )

    verb_data_path = Path("conjugation_data/verbs.json")
    if not verb_data_path.is_file():
        return [], {}

    stats = load_stats(CONJUGATION_STATS_FILE)
    today = date.today().isoformat()
    all_verbs = get_all_verbs()
    all_tenses = get_all_tenses()

    exercises = []
    for verb in all_verbs:
        for tense in all_tenses:
            key = f"{verb}|{tense}"
            stat = stats.get(key)
            if stat and stat.due_date > today:
                continue

            # Pick a single random pronoun index
            pronoun_idx = random.randint(0, 5)
            selected_pronouns = get_random_pronouns()
            pronoun = selected_pronouns[pronoun_idx]

            _, forms = conjugate(verb, tense, selected_pronouns)
            correct_form = forms[pronoun_idx]

            exercises.append(ConjugationExercise(
                verb=verb,
                tense=tense,
                tense_display=get_tense_display_name(tense),
                pronoun=pronoun,
                correct_form=correct_form,
                translation=get_translation(verb),
                key=key,
                regularity=get_verb_regularity(verb, tense),
            ))

    return exercises, stats


def _load_grammar_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load grammar exercises and return exercises + their stats."""
    grammar_dir = Path("grammar_data")
    if not grammar_dir.exists():
        return [], {}

    stats = load_stats(GRAMMAR_STATS_FILE)
    today = date.today().isoformat()

    exercises = []
    for json_path in sorted(grammar_dir.glob("*.json")):
        topic_name = json_path.stem
        with json_path.open(encoding="utf-8") as f:
            topic_data = json.load(f)

        for ex in topic_data.get("exercises", []):
            key = f"{topic_name}|{ex['id']}"
            stat = stats.get(key)
            if stat and stat.due_date > today:
                continue

            exercises.append(GrammarExercise(
                exercise_data=ex,
                topic_name=topic_name,
                key=key,
            ))

    return exercises, stats


def _load_sentence_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load sentence translation exercises and return exercises + their stats."""
    sentence_dir = Path("sentence_data")
    if not sentence_dir.exists():
        return [], {}

    stats = load_stats(SENTENCE_STATS_FILE)
    today = date.today().isoformat()

    exercises = []
    for json_path in sorted(sentence_dir.glob("*.json")):
        with json_path.open(encoding="utf-8") as f:
            topic_data = json.load(f)

        for sent in topic_data.get("sentences", []):
            key = f"sentence|{sent['id']}"
            stat = stats.get(key)
            if stat and stat.due_date > today:
                continue

            direction = random.choice(["english", "french"])
            exercises.append(SentenceExercise(
                sentence_data=sent,
                direction=direction,
                key=key,
            ))

    return exercises, stats


def _load_conjugation_sentence_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load conjugation-in-context sentences and return exercises + their stats."""
    if not CONJ_SENTENCE_DATA_DIR.exists():
        return [], {}

    stats = load_stats(CONJ_SENTENCE_STATS_FILE)
    today = date.today().isoformat()

    exercises = []
    for json_path in sorted(CONJ_SENTENCE_DATA_DIR.glob("*.json")):
        with json_path.open(encoding="utf-8") as f:
            topic_data = json.load(f)

        for sent in topic_data.get("sentences", []):
            key = f"conjsent|{sent['id']}"
            stat = stats.get(key)
            if stat and stat.due_date > today:
                continue

            exercises.append(ConjugationSentenceExercise(sent, key))

    return exercises, stats


def _balanced_sample(items_by_type: dict[str, list[Exercise]], budget: int) -> list[Exercise]:
    """Sample up to `budget` items, distributed equally across types.

    Does round-robin allocation: each type gets floor(budget / n_types),
    then remaining slots go to whichever types still have items.
    """
    types_with_items = {t: list(exs) for t, exs in items_by_type.items() if exs}
    if not types_with_items:
        return []

    for exs in types_with_items.values():
        random.shuffle(exs)

    n_types = len(types_with_items)
    per_type = budget // n_types
    remainder = budget % n_types

    selected: list[Exercise] = []
    leftover: list[Exercise] = []

    for exs in types_with_items.values():
        selected.extend(exs[:per_type])
        leftover.extend(exs[per_type:])

    # Distribute remainder slots from leftover pool
    random.shuffle(leftover)
    selected.extend(leftover[:remainder])

    return selected


def _prioritize_and_cap(
    exercises: list[Exercise],
    stats: dict[str, SRSStats],
    max_items: int = 60,
    max_new: int = 10,
) -> list[Exercise]:
    """Prioritize exercises: overdue > due_today > new, capped at max_items.

    New items are capped at max_new to avoid overwhelm.
    """
    today = date.today().isoformat()
    overdue = []
    due_today = []
    new_items = []

    for ex in exercises:
        stat = stats.get(ex.key)
        if stat is None:
            new_items.append(ex)
        elif stat.due_date < today:
            overdue.append(ex)
        else:
            due_today.append(ex)

    random.shuffle(overdue)
    random.shuffle(due_today)
    random.shuffle(new_items)

    new_items = new_items[:max_new]
    combined = overdue + due_today + new_items
    return combined[:max_items]


def load_all_due(max_items: int | None = None, max_new: int | None = None) -> list[Exercise]:
    """
    Load all due exercises from all 3 pools.

    Session algorithm:
    1. Collect due items per type, categorized by priority
    2. Balanced round-robin across types (each gets ~max_items/3 slots)
    3. Within each type: overdue first, then due_today, then new
    4. New items capped at max_new total
    5. Shuffle final list
    """
    config = _load_config()
    if max_items is None:
        max_items = config["max_items"]
    if max_new is None:
        max_new = config["max_new"]

    enabled = _load_enabled_blocks()
    type_pools: dict[str, tuple[list[Exercise], dict[str, SRSStats]]] = {}
    for block_id, loader in [
        ("vocabulary", _load_vocab_exercises),
        ("conjugation", _load_conjugation_exercises),
        ("grammar", _load_grammar_exercises),
        ("sentence", _load_sentence_exercises),
        ("conjugation_sentence", _load_conjugation_sentence_exercises),
    ]:
        if block_id not in enabled:
            continue
        exercises, stats = loader()
        type_pools[block_id] = (exercises, stats)

    today = date.today().isoformat()

    # For each type, build a priority-ordered list: overdue > due_today > new
    prioritized_by_type: dict[str, list[Exercise]] = {}
    total_new = 0

    for type_name, (exercises, stats) in type_pools.items():
        overdue = []
        due_today = []
        new_items = []

        for ex in exercises:
            stat = stats.get(ex.key)
            if stat is None:
                new_items.append(ex)
            elif stat.due_date < today:
                overdue.append(ex)
            else:
                due_today.append(ex)

        random.shuffle(overdue)
        random.shuffle(due_today)
        random.shuffle(new_items)

        # Cap new items per type (spread max_new across types)
        new_cap = max(1, max_new // max(1, len(type_pools)))
        remaining_new = max(0, max_new - total_new)
        new_items = new_items[:min(new_cap, remaining_new)]
        total_new += len(new_items)

        prioritized_by_type[type_name] = overdue + due_today + new_items

    session = _balanced_sample(prioritized_by_type, max_items)
    random.shuffle(session)
    return session


def load_vocab_due(max_items: int = 60) -> list[Exercise]:
    """Load due vocabulary exercises for focused practice."""
    exercises, stats = _load_vocab_exercises()
    result = _prioritize_and_cap(exercises, stats, max_items)
    random.shuffle(result)
    return result


def load_conjugation_due(tense_filter: str | None = None, max_items: int = 60) -> list[Exercise]:
    """Load due conjugation exercises, optionally filtered by tense."""
    exercises, stats = _load_conjugation_exercises()
    if tense_filter:
        exercises = [ex for ex in exercises if ex.tense == tense_filter]
    result = _prioritize_and_cap(exercises, stats, max_items)
    random.shuffle(result)
    return result


def load_grammar_due(topic_filter: str | None = None, max_items: int = 60) -> list[Exercise]:
    """Load due grammar exercises, optionally filtered by topic."""
    exercises, stats = _load_grammar_exercises()
    if topic_filter:
        exercises = [ex for ex in exercises if ex.topic_name == topic_filter]
    result = _prioritize_and_cap(exercises, stats, max_items)
    random.shuffle(result)
    return result


def get_grammar_due_by_topic() -> dict[str, int]:
    """Get count of due grammar exercises broken down by topic."""
    grammar_dir = Path("grammar_data")
    if not grammar_dir.exists():
        return {}

    stats = load_stats(GRAMMAR_STATS_FILE)
    today = date.today().isoformat()
    counts: dict[str, int] = {}

    for json_path in sorted(grammar_dir.glob("*.json")):
        topic_name = json_path.stem
        with json_path.open(encoding="utf-8") as f:
            topic_data = json.load(f)
        for ex in topic_data.get("exercises", []):
            key = f"{topic_name}|{ex['id']}"
            stat = stats.get(key)
            if stat is None or stat.due_date <= today:
                counts[topic_name] = counts.get(topic_name, 0) + 1

    return counts


def load_sentence_due(max_items: int = 60) -> list[Exercise]:
    """Load due sentence translation exercises for focused practice."""
    exercises, stats = _load_sentence_exercises()
    result = _prioritize_and_cap(exercises, stats, max_items)
    random.shuffle(result)
    return result


def load_conjugation_sentence_due(max_items: int = 60) -> list[Exercise]:
    """Load due conjugation-in-context sentences for focused practice."""
    exercises, stats = _load_conjugation_sentence_exercises()
    result = _prioritize_and_cap(exercises, stats, max_items)
    random.shuffle(result)
    return result


def get_conjugation_due_by_tense() -> dict[str, int]:
    """Get count of due conjugation exercises broken down by tense."""
    verb_data_path = Path("conjugation_data/verbs.json")
    if not verb_data_path.is_file():
        return {}

    from conjugation_engine import get_all_verbs, get_all_tenses

    stats = load_stats(CONJUGATION_STATS_FILE)
    today = date.today().isoformat()
    counts: dict[str, int] = {}

    for verb in get_all_verbs():
        for tense in get_all_tenses():
            key = f"{verb}|{tense}"
            stat = stats.get(key)
            if stat is None or stat.due_date <= today:
                counts[tense] = counts.get(tense, 0) + 1

    return counts


def get_due_counts() -> dict[str, int]:
    """Get count of due items per type without building full exercise objects.

    Disabled blocks always report 0 so dashboard layout stays stable.
    """
    today = date.today().isoformat()
    enabled = _load_enabled_blocks()
    counts = {"Vocabulary": 0, "Conjugation": 0, "Grammar": 0, "Sentence": 0,
              "ConjugationSentence": 0}

    # Vocabulary
    csv_path = Path("master_vocabulary.csv")
    if "vocabulary" in enabled and csv_path.is_file():
        stats = load_stats(FLASHCARD_STATS_FILE)
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    category = row[2].strip() if len(row) >= 3 else ""
                    if not _vocab_category_allowed(category):
                        continue
                    french_variants = [v.strip() for v in row[0].split("|")]
                    english_variants = [v.strip() for v in row[1].split("|")]
                    key = f"{french_variants[0]}|{english_variants[0]}"
                    stat = stats.get(key)
                    if stat is None or stat.due_date <= today:
                        counts["Vocabulary"] += 1

    # Conjugation
    verb_data_path = Path("conjugation_data/verbs.json")
    if "conjugation" in enabled and verb_data_path.is_file():
        from conjugation_engine import get_all_verbs, get_all_tenses
        stats = load_stats(CONJUGATION_STATS_FILE)
        for verb in get_all_verbs():
            for tense in get_all_tenses():
                key = f"{verb}|{tense}"
                stat = stats.get(key)
                if stat is None or stat.due_date <= today:
                    counts["Conjugation"] += 1

    # Grammar
    grammar_dir = Path("grammar_data")
    if "grammar" in enabled and grammar_dir.exists():
        stats = load_stats(GRAMMAR_STATS_FILE)
        for json_path in grammar_dir.glob("*.json"):
            topic_name = json_path.stem
            with json_path.open(encoding="utf-8") as f:
                topic_data = json.load(f)
            for ex in topic_data.get("exercises", []):
                key = f"{topic_name}|{ex['id']}"
                stat = stats.get(key)
                if stat is None or stat.due_date <= today:
                    counts["Grammar"] += 1

    # Sentence
    sentence_dir = Path("sentence_data")
    if "sentence" in enabled and sentence_dir.exists():
        stats = load_stats(SENTENCE_STATS_FILE)
        for json_path in sentence_dir.glob("*.json"):
            with json_path.open(encoding="utf-8") as f:
                topic_data = json.load(f)
            for sent in topic_data.get("sentences", []):
                key = f"sentence|{sent['id']}"
                stat = stats.get(key)
                if stat is None or stat.due_date <= today:
                    counts["Sentence"] += 1

    # Conjugation-in-context sentences
    if "conjugation_sentence" in enabled and CONJ_SENTENCE_DATA_DIR.exists():
        stats = load_stats(CONJ_SENTENCE_STATS_FILE)
        for json_path in CONJ_SENTENCE_DATA_DIR.glob("*.json"):
            with json_path.open(encoding="utf-8") as f:
                topic_data = json.load(f)
            for sent in topic_data.get("sentences", []):
                key = f"conjsent|{sent['id']}"
                stat = stats.get(key)
                if stat is None or stat.due_date <= today:
                    counts["ConjugationSentence"] += 1

    return counts
