# French Daily 🇫🇷

A personal, offline, terminal-based French trainer built around a single **daily practice session**. It mixes vocabulary, verb conjugation, and *conjugation-in-context* into one spaced-repetition flow, so a few focused minutes a day steadily builds the skills that generic apps tend to gloss over.

The app has deliberately narrowed to the things that trip up intermediate learners:

- **Verb conjugation** across **8 tenses** — drilled both in isolation and by producing full French sentences from English prompts.
- **Connector / discourse vocabulary** (*donc, pourtant, d'ailleurs, …*) — the glue that makes speech flow, which flashcard apps rarely prioritize.

Everything is scheduled with spaced repetition, runs entirely offline, and stores your progress in plain JSON on your machine.

---

## Highlights

- **One command a day.** `daily_trainer.py` pulls everything due across all active blocks into one balanced session.
- **Conjugation you actually produce.** Type whole French sentences from English prompts; the verb form is checked exactly, the rest fuzzily.
- **Guaranteed-correct verb data.** Conjugations are *generated* by an engine, never hand-typed, and the sentence bank is machine-validated against it — so it can't drift.
- **Register-aware.** Prompts flag *informal* (tu/on) vs *formal* (vous/nous) so English "you" and "we" are never ambiguous.
- **Spaced repetition everywhere** (SM-2), shared between the daily trainer and the standalone trainers.
- **Configurable.** Turn blocks on/off and tune session size, categories, and thresholds in one YAML file.

---

## How it works

**Blocks.** The daily session is assembled from independent *blocks*, each with its own data source and spaced-repetition schedule. Currently active:

| Block | What you practice | Source |
|-------|-------------------|--------|
| **vocabulary** | Flashcards, random direction, fuzzy-matched | `master_vocabulary.csv` |
| **conjugation** | A verb + tense + one random pronoun | `conjugation_data/verbs.json` |
| **conjugation_sentence** | Translate an English sentence to French with the right conjugation | `conjugation_sentence_data/*.json` |

**Spaced repetition (SM-2).** Every item — a word, a verb-tense pair, a sentence — carries its own interval and due date. Correct answers push the next review further out; misses bring it back soon. Only what's *due* shows up, so sessions stay short and focused.

**The conjugation engine is the source of truth.** `conjugation_engine.py` generates every French verb form algorithmically (regular patterns + stored irregular stems/forms). The conjugation-sentence bank never stores a verb form — it's regenerated from `(verb, tense, pronoun)` at run time, and a validator rejects any authored sentence whose verb doesn't match the engine. That's what keeps the content accurate and reproducible.

**Config-driven.** `daily_trainer_config.yaml` decides which blocks run, how many items per session, which vocabulary categories are in scope, and the fuzzy-match thresholds.

---

## Requirements & setup

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — this project uses `uv` for everything. Always run scripts through it; don't use bare `python`/`pip`.

```bash
git clone https://github.com/alexedmon1/french-daily.git
cd french-daily
uv sync          # installs dependencies (textual, pyyaml)
```

Dependencies are managed in `pyproject.toml` / `uv.lock` — `uv` handles them for you.

---

## Daily use — the daily trainer

This is the main way to use the app:

```bash
uv run python daily_trainer.py
```

A terminal UI (built with [Textual](https://textual.textualize.io/)) opens on a **dashboard** showing what's due, your streak, and estimated time. Pick a mode:

| Key | Mode | What it does |
|-----|------|--------------|
| `1` | **Daily Mix** | Everything due, balanced across blocks — the recommended default |
| `2` | **Vocabulary** | Flashcards only |
| `3` | **Conjugation** | Verb conjugations (choose a tense first) |
| `4` | **Conjug. sentences** | English → French sentence production |
| `q` | Quit | |

**In an exercise:** read the prompt, type your answer, press **Enter**. Type **`h`** for a hint. Press **Esc** to end early. After each answer you see your input and the correct answer side by side. Around the 15-minute mark the app suggests a good stopping point.

**When you finish** you get a summary: time, accuracy, a per-type breakdown, the items you missed, and your updated streak.

Quality ratings are automatic in the daily trainer (correct = *Good*, wrong = *Wrong*) — no manual grading step.

---

## The exercise blocks in detail

### Vocabulary
Flashcards drawn from `master_vocabulary.csv`. Each card appears in a random direction (FR→EN or EN→FR). Answers are fuzzy-matched (85% by default), parenthetical parts are optional (*"to sit (down)"* accepts *"to sit"*), and synonyms across cards are accepted. The current focus is **connector and discourse vocabulary** plus common expressions and prepositions (set via the category whitelist in the config).

### Conjugation
A verb is shown with a tense and a single random pronoun; you type the conjugated form. Covers **8 tenses**:

`présent` · `futur proche` · `futur simple` · `imparfait` · `passé composé` · `conditionnel présent` · `conditionnel passé` · `subjonctif présent`

Hints show the ending pattern for regular verbs and the stem/auxiliary structure for irregulars.

### Conjugation in context
The block that makes conjugation stick. You get an **English sentence** (with the target tense and, for tu/vous/on/nous, an informal/formal cue) and type the **full French sentence**:

```
Translate to French — passé composé:
Yesterday, she went to the market.

> Hier, elle est allée au marché.   ✓
```

Grading has two gates: the whole sentence is fuzzy-matched, but the **conjugated verb must be exactly right** (accents included) — get the tense or person wrong and it fails even if the rest is perfect. Because the correct verb form comes from the engine, the answer key can never be wrong.

---

## Focused / standalone trainers

Prefer to drill one thing outside the TUI? Each block also has a command-line trainer that shares the same progress data:

```bash
# Verb conjugations
uv run python conjugations.py                 # interactive: pick tier, type, tense
uv run python conjugations.py --srs           # only what's due today
uv run python conjugations.py --srs --tense=conditional_past
uv run python conjugations.py --stats

# Vocabulary flashcards
uv run python flashcards.py                    # interactive
uv run python flashcards.py --srs --mode=medium
uv run python flashcards.py --stats
```

Both accept `--help`. The conjugation trainer supports tiers (**core / intermediate / advanced**) and per-tense SRS filtering; the flashcard trainer supports difficulty modes (easy / medium / hard / expert), categories, and gender practice.

---

## Configuration

`daily_trainer_config.yaml` controls the daily session:

```yaml
enabled_blocks:            # which blocks appear in the daily mix
  - vocabulary
  - conjugation
  - conjugation_sentence

vocabulary_categories:     # whitelist; empty = all categories
  - connectors
  - expressions
  - prepositions

max_items: 100             # max exercises per session
max_new: 40                # cap on new (unseen) items per session
fuzzy_threshold: 0.85      # vocabulary match strictness (0–1)
sentence_threshold: 0.80   # sentence match strictness (0–1)
session_time_limit: 900    # seconds before a "good stopping point" nudge
```

Disabling a block just removes it from the menu and mix — its code and data are untouched.

---

## Content & accuracy

- **Verbs:** 111 verbs organized by tier (20 core, 42 intermediate, 49 advanced), each conjugated across all 8 tenses by the engine.
- **Conjugation sentences:** 73 validated sentences (and growing) spanning every tense, varied pronouns, and informal/formal register.
- **Vocabulary:** ~770 words across many categories, with the daily focus currently on connectors/expressions/prepositions.

**Adding conjugation sentences** (the reproducible workflow):

1. Author a natural English/French pair in a file under `conjugation_sentence_data/`, tagged with the target `verb`, `tense`, and `pronoun`.
2. Validate against the engine:
   ```bash
   uv run python validate_conjugation_sentences.py
   ```
   Any sentence whose French verb form doesn't match the engine is rejected — so a wrong answer key can never ship.

Adding **vocabulary** or **verbs** is documented in detail in `CLAUDE.md`.

---

## Data & progress

Your progress lives in hidden folders in the project root (all git-ignored, all plain JSON):

| Folder | Holds |
|--------|-------|
| `.flashcard_data/` | Vocabulary SRS + stats |
| `.conjugation_data/` | Conjugation SRS + stats |
| `.conjugation_sentence_data/` | Conjugation-sentence SRS + stats |
| `.daily_trainer_data/` | Streak + session history |

To **back up or sync** across machines, copy these folders. To **reset** a pool, delete its folder. (The daily trainer and the standalone trainers share the same files, so a reset affects both.)

---

## Roadmap / future goals

- **Themed sentence sets** — travel, work, food, small talk — so conjugation practice doubles as situational vocabulary.
- **Deeper verb coverage** — extend the conjugation-sentence bank into the intermediate and advanced tiers (only core is heavily covered today).
- **Richer register & aspect** — more tu/vous and on/nous contrasts, and passé composé vs imparfait discrimination in context.
- **A standalone CLI runner** for the conjugation-sentence block, matching the other trainers.
- **Optional block revival** — the archived grammar and full-sentence-translation blocks can be brought back if the focus widens (see `archive/`).

---

## Project layout

```
french-daily/
├── daily_trainer.py                  # ⭐ unified daily TUI (start here)
├── daily_trainer_config.yaml         # session configuration
├── exercise_types.py                 # block abstraction + session loader
├── srs_core.py                       # shared SM-2 spaced-repetition core
│
├── conjugations.py                   # standalone conjugation trainer
├── conjugation_engine.py             # generates all verb forms (source of truth)
├── conjugation_data/verbs.json       # verb database (111 verbs)
├── conjugation_sentence_data/*.json  # English→French sentence bank
├── validate_conjugation_sentences.py # validates the bank against the engine
│
├── flashcards.py                     # standalone vocabulary trainer
├── master_vocabulary.csv             # combined vocabulary
├── vocabulary/                       # per-category source CSVs
├── combine_csvs.py / split_master.py # vocabulary sync tools
│
└── archive/                          # retired blocks (grammar, sentence translation)
```

---

## Documentation

- **README.md** (this file) — what the app is and how to use it.
- **CLAUDE.md** — full developer reference: architecture, data formats, and workflows for adding content.
- **archive/README.md** — what was retired and how to restore it.

---

**Bonne chance ! 🇫🇷**
