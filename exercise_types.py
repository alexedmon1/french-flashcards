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


# ----------------------------------------------------------------------
# Vocabulary Exercise
# ----------------------------------------------------------------------
FLASHCARD_STATS_FILE = Path(".flashcard_data/card_stats.json")


class VocabularyExercise(Exercise):
    type_name = "Vocabulary"
    stats_file = FLASHCARD_STATS_FILE

    def __init__(self, french: str, english: str, french_variants: list[str],
                 english_variants: list[str], french_synonyms: list[str],
                 direction: str, key: str):
        self.french = french
        self.english = english
        self.french_variants = french_variants
        self.english_variants = english_variants
        self.french_synonyms = french_synonyms
        self.direction = direction  # "french" or "english"
        self.key = key

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
        return _fuzzy_match(user, variants)


# ----------------------------------------------------------------------
# Conjugation Exercise
# ----------------------------------------------------------------------
CONJUGATION_STATS_FILE = Path(".conjugation_data/conjugation_stats.json")


class ConjugationExercise(Exercise):
    type_name = "Conjugation"
    stats_file = CONJUGATION_STATS_FILE

    def __init__(self, verb: str, tense: str, tense_display: str,
                 pronoun: str, correct_form: str, translation: str, key: str):
        self.verb = verb
        self.tense = tense
        self.tense_display = tense_display
        self.pronoun = pronoun
        self.correct_form = correct_form
        self.translation = translation
        self.key = key

    def get_prompt(self) -> str:
        return f"{self.verb} ({self.translation}) — {self.tense_display}\n{self.pronoun} ..."

    def get_correct(self) -> str:
        return f"{self.pronoun} {self.correct_form}"

    def check(self, user_input: str) -> bool:
        return user_input.strip().lower() == self.correct_form.lower()

    def get_hint(self) -> str | None:
        if len(self.correct_form) >= 3:
            return f"Starts with: {self.correct_form[:2]}..."
        return None


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
        translation = self.data.get("translation", "")
        sentence = f"{topic_display}\n{before} __________ {after}".strip()
        if context:
            sentence += f"\n({context})"
        if translation and translation != context:
            sentence += f"\n{translation}"
        return sentence

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
# Factory: load all due exercises
# ----------------------------------------------------------------------
def _load_vocab_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load vocabulary cards and return exercises + their stats."""
    csv_path = Path("master_vocabulary.csv")
    if not csv_path.is_file():
        return [], {}

    stats = load_stats(FLASHCARD_STATS_FILE)

    # Read cards from CSV
    cards = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
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

        direction = random.choice(["english", "french"])
        exercises.append(VocabularyExercise(
            french=card["french"],
            english=card["english"],
            french_variants=card["french_variants"],
            english_variants=card["english_variants"],
            french_synonyms=list(synonyms),
            direction=direction,
            key=key,
        ))

    return exercises, stats


def _load_conjugation_exercises() -> tuple[list[Exercise], dict[str, SRSStats]]:
    """Load conjugation exercises and return exercises + their stats."""
    from conjugation_engine import (
        conjugate, get_all_verbs, get_translation,
        get_tense_display_name, get_all_tenses, get_random_pronouns,
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


def load_all_due(max_items: int = 60, max_new: int = 10) -> list[Exercise]:
    """
    Load all due exercises from all 3 pools.

    Session algorithm:
    1. Collect due items per type, categorized by priority
    2. Balanced round-robin across types (each gets ~max_items/3 slots)
    3. Within each type: overdue first, then due_today, then new
    4. New items capped at max_new total
    5. Shuffle final list
    """
    type_pools: dict[str, tuple[list[Exercise], dict[str, SRSStats]]] = {}
    for name, loader in [
        ("Vocabulary", _load_vocab_exercises),
        ("Conjugation", _load_conjugation_exercises),
        ("Grammar", _load_grammar_exercises),
    ]:
        exercises, stats = loader()
        type_pools[name] = (exercises, stats)

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


def get_due_counts() -> dict[str, int]:
    """Get count of due items per type without building full exercise objects."""
    today = date.today().isoformat()
    counts = {"Vocabulary": 0, "Conjugation": 0, "Grammar": 0}

    # Vocabulary
    csv_path = Path("master_vocabulary.csv")
    if csv_path.is_file():
        stats = load_stats(FLASHCARD_STATS_FILE)
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    french_variants = [v.strip() for v in row[0].split("|")]
                    english_variants = [v.strip() for v in row[1].split("|")]
                    key = f"{french_variants[0]}|{english_variants[0]}"
                    stat = stats.get(key)
                    if stat is None or stat.due_date <= today:
                        counts["Vocabulary"] += 1

    # Conjugation
    verb_data_path = Path("conjugation_data/verbs.json")
    if verb_data_path.is_file():
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
    if grammar_dir.exists():
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

    return counts
