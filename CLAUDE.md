# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A French language learning application with multiple components:

### Flashcard Trainers
1. **Simple trainer** (`simple/flashcards.py`) - Basic vocabulary practice with CSV-based word lists
2. **Current trainer** (`flashcards.py`) - Advanced version with SRS, typing modes, progress tracking, and interactive prompts

### Additional Components
3. **Conjugation trainer** (`conjugations.py`) - Verb conjugation practice for 8 tenses with tier system
4. **Conjugation engine** (`conjugation_engine.py`) - Core conjugation logic module
5. **Verb data** (`conjugation_data/verbs.json`) - External JSON database of verbs
6. **Master vocabulary** (`master_vocabulary.csv`) - Combined file with all vocabulary from individual CSVs with category tags
7. **CSV combiner** (`combine_csvs.py`) - Tool to regenerate master vocabulary file
8. **Sentence conjugation validator** (`validate_conjugation_sentences.py`) - Verifies the conjugation-sentence bank against the engine

> **Archived** (`archive/`): the standalone grammar trainer (`grammar.py`), `grammar_data/`, and the sentence-translation bank (`sentence_data/`) were retired when the app narrowed to conjugation-focused practice. The `grammar`/`sentence` sections further down describe those archived blocks. See `archive/README.md`.

### Unified Daily Trainer
10. **Daily trainer** (`daily_trainer.py`) - Textual TUI combining all exercise blocks into one daily session
11. **SRS core** (`srs_core.py`) - Shared SM-2 algorithm and utilities used by all trainers
12. **Exercise types** (`exercise_types.py`) - Unified exercise abstraction and session loader
13. **Daily config** (`daily_trainer_config.yaml`) - Enables/disables blocks and tunes session settings

### Exercise Blocks
The daily trainer is organized into pluggable **blocks**, each backed by its own data source and SRS stats file. Blocks are toggled via `enabled_blocks` in `daily_trainer_config.yaml`.

**Active blocks:**
- **vocabulary** - flashcards from `master_vocabulary.csv` (`.flashcard_data/`)
- **conjugation** - verb-tense drills from `conjugation_data/verbs.json` (`.conjugation_data/`)
- **conjugation_sentence** - English→French sentence production targeting a specific conjugation, from `conjugation_sentence_data/*.json` (`.conjugation_sentence_data/`). Verb forms are machine-validated against the conjugation engine (see `validate_conjugation_sentences.py`).

**Archived blocks** (code retained in `exercise_types.py` but dormant; data moved to `archive/` — see `archive/README.md`):
- **grammar** - fill-in-the-blank (was `grammar_data/*.json`)
- **sentence** - full-sentence translation (was `sentence_data/*.json`)

Blocks are toggled via `enabled_blocks` in `daily_trainer_config.yaml`; disabling a block keeps its code and data intact. Vocabulary can be further narrowed by category whitelist/blacklist.

Supporting data:
- **`example_sentences.json`** - optional example sentence + translation per French word, shown after answering a vocabulary card.

## Running the Application

### Simple Flashcard Trainer
```bash
python simple/flashcards.py <csv_file> <direction>
```
- `<csv_file>`: Path to a CSV file (e.g., `flashcards.csv`, `verbs.csv`, `weather.csv`)
- `<direction>`: Either `french` or `english` (determines which language you're guessing)
  - `english`: Shows French word, you recall English translation
  - `french`: Shows English word, you recall French translation

Examples:
```bash
python simple/flashcards.py flashcards.csv english    # French → English
python simple/flashcards.py verbs.csv french          # English → French
python simple/flashcards.py weather.csv english       # Weather vocabulary
```

### Current Flashcard Trainer (Recommended)
```bash
python3 flashcards.py [csv_file] [options]
```
Advanced version with multiple features and **interactive prompts**:
- Automatically prompts for language direction (French→English or English→French)
- Interactively shows and lets you select categories
- Defaults to `master_vocabulary.csv` if no file specified

**Command-line options:**
- `--help`: Show detailed help message
- `--srs`: Spaced Repetition System (only shows cards due for review)
- `--mode=<mode>`: easy (multiple choice), medium (typing with fuzzy match), hard (exact typing), expert (timed)
- `--gender`: Practice masculine/feminine noun genders
- `--category=<cat>`: Pre-select category (skips interactive prompt)
- `--list-categories`: Show available categories and exit
- `--stats`: Show progress statistics and exit

Examples:
```bash
# Show help
python3 flashcards.py --help

# Interactive mode (simplest - just run it!)
python3 flashcards.py

# Interactive with SRS enabled
python3 flashcards.py --srs --mode=medium

# Specify file and options
python3 flashcards.py weather.csv --mode=hard

# Non-interactive with command-line category
python3 flashcards.py --category=verbs --srs

# View available categories
python3 flashcards.py --list-categories
```

### Conjugation Trainer
```bash
python3 conjugations.py [options]
```
Practice French verb conjugations across **8 tenses** with **93 verbs** organized by tier, and optional **SRS support**.

**Tenses available:**
- Présent (present)
- Futur proche (futur_proche)
- Futur simple (future)
- Imparfait (imparfait)
- Passé composé (past)
- Conditionnel présent (conditional)
- Conditionnel passé (conditional_past)
- Subjonctif présent (subjunctive)

**Command-line options:**
- `--help`: Show detailed help message
- `--srs`: Spaced Repetition System (only reviews verb-tense combinations due today)
- `--tense=<tense>`: Filter by specific tense - only works with --srs
- `--tier=<tier>`: Filter by verb tier (core, intermediate, advanced)
- `--stats`: Show progress statistics and exit

**Features:**
- Interactive verb type selection (regular -ER, regular -IR, irregular, or all)
- Interactive tier selection (core, intermediate, advanced, or all)
- 93 total verbs organized by tier:
  - **Core** (~20 verbs): Most essential verbs for beginners
  - **Intermediate** (~35 verbs): Common verbs for intermediate learners
  - **Advanced** (~40 verbs): Less common verbs for advanced learners
- Randomized pronoun variations (il/elle/on, ils/elles) for natural practice
- Gender agreement for passé composé with être verbs
- SRS quality ratings (Wrong/Hard/Good/Easy) to optimize review schedule
- External verb data in JSON format for easy additions

**Examples:**
```bash
# Show help
python3 conjugations.py --help

# Normal practice mode (interactive)
python3 conjugations.py

# Practice only core verbs
python3 conjugations.py --tier=core

# SRS mode - only practice due verbs
python3 conjugations.py --srs

# SRS mode - only practice present tense
python3 conjugations.py --srs --tense=present

# SRS mode - only practice conditional
python3 conjugations.py --srs --tense=conditional

# SRS mode for core verbs only
python3 conjugations.py --tier=core --srs

# View your statistics
python3 conjugations.py --stats
```

### Grammar Trainer
```bash
python3 grammar.py [options]
```
Practice French grammar with fill-in-the-blank exercises. Topics are auto-discovered from JSON files in `grammar_data/`.

**Currently available topics:**
- Pronoms relatifs (qui, que, où, dont, lequel, ce qui, ce que) — 61 exercises across 3 levels

**Levels (for pronoms relatifs):**
- **Level 1**: `qui` vs `que` (~18 exercises)
- **Level 2**: `qui`, `que`, `où`, `dont` (~23 exercises)
- **Level 3**: Pronoms composés (`lequel`, `laquelle`, etc.) + `ce qui`/`ce que` (~20 exercises)

**Command-line options:**
- `--help`: Show detailed help message
- `--srs`: Spaced Repetition System (only practice due exercises)
- `--level=<N>`: Filter by difficulty level (1, 2, or 3)
- `--stats`: Show progress statistics and exit

**Features:**
- Auto-discovers topics from JSON files in `grammar_data/`
- Interactive topic and level selection
- Hint system (type `h` during an exercise)
- Accent-sensitive answer checking (`où` ≠ `ou`)
- Alternative answers supported (e.g., `que`/`qu'`)
- SRS with SM-2 algorithm for spaced review
- Session summaries with accuracy stats

**Examples:**
```bash
# Show help
python3 grammar.py --help

# Interactive mode (simplest - just run it!)
python3 grammar.py

# Practice level 1 only (qui vs que)
python3 grammar.py --level=1

# SRS mode - only practice due exercises
python3 grammar.py --srs

# SRS mode for level 2 only
python3 grammar.py --srs --level=2

# View your statistics
python3 grammar.py --stats
```

### Daily Trainer (Recommended)
```bash
python3 daily_trainer.py
```
Textual TUI that combines all enabled exercise blocks into daily practice. The dashboard is a **mode selector**: run a mixed session across all types, or focus on a single block.

**Screens:**
- **Dashboard**: Mode menu with per-mode due counts and streak. Keys/buttons:
  - `1` **Daily Mix** — all enabled types combined (shows total due + estimated time)
  - `2` **Vocabulary** — flashcard review only
  - `3` **Conjugation** — verb conjugations (prompts for tense first)
  - `4` **Conjug. sentences** — English→French sentence production with the correct conjugation
  - `q` quit
- **Exercise**: Presents items one at a time with progress bar and timer. Type answer and press Enter. Type `h` for a hint. Press Escape to end early. Suggests a stopping point once the configured `session_time_limit` is reached.
- **Summary**: Time elapsed, accuracy, per-type breakdown, missed items list, streak update. Press `d` for dashboard, `q` to quit.

**Exercise behavior:**
- **Vocabulary**: Random direction per card (French->English or English->French). Fuzzy matching with configurable threshold (`fuzzy_threshold`, default 85%). Parenthetical parts are optional (e.g., "to sit down" matches "to sit (down)"). Cross-card synonyms are accepted. An example sentence is shown after answering when available.
- **Conjugation**: Single random pronoun per card (not all 6) for faster pace. `je` elides to `j'` before a vowel.
- **Grammar**: Fill-in-the-blank, same as standalone grammar trainer.
- **Sentence**: Full-sentence translation in a random direction, fuzzy-matched with its own threshold (`sentence_threshold`, default 80%) plus `alternatives_en`/`alternatives_fr`.
- **Conjugation sentence**: English prompt (with the target tense and, for tu/vous/on/nous, an informal/formal register cue) → you type the full French sentence. The whole sentence is fuzzy-matched (`sentence_threshold`), but the conjugated verb form must be present exactly (accent-sensitive) — that form is generated by the engine, not stored, so it can't drift. Wrong tense/person fails even if the rest of the sentence is fine. The register cue resolves English "you" (tu vs vous) and "we" (on vs nous).
- **Quality ratings**: Auto-calculated (correct=Good/2, wrong=Wrong/0) — no manual rating step.
- **Feedback display**: After each answer, shows your input and the correct answer on separate lines so you can compare (especially useful for fuzzy-matched items).

**Session algorithm (Daily Mix):**
- Collects due items from all enabled pools (overdue + due today + new)
- Balanced round-robin: each enabled type gets an equal share of session slots
- New items capped per session (`max_new`) to avoid overwhelm, spread across types
- Overdue items prioritized (overdue > due today > new) within each type
- Total session capped at `max_items`

**Data:**
- SRS data shared with standalone trainers (same `.flashcard_data/`, `.conjugation_data/`, `.grammar_data/`, `.sentence_data/` directories)
- Session history and streak in `.daily_trainer_data/progress.json`
- Session behavior configured in `daily_trainer_config.yaml` (see below)

**Examples:**
```bash
# Launch the TUI
python3 daily_trainer.py
```

### Daily Trainer Configuration (`daily_trainer_config.yaml`)
Controls which blocks run and how sessions are sized. Loaded by `exercise_types.py` (falls back to defaults, then to a legacy `daily_trainer_config.json` if present).

**Keys:**
- `enabled_blocks`: list of blocks to include (`vocabulary`, `conjugation`, `grammar`, `sentence`). Omit a block to disable it; empty/missing = all enabled.
- `vocabulary_categories`: whitelist of vocab categories (matches `category` column / `vocabulary/` filenames). Empty = all categories.
- `excluded_categories`: legacy blacklist, consulted only when the whitelist is empty.
- `max_items`: max exercises per session (default 100).
- `max_new`: max new (unseen) items per session (default 10; config ships with 40).
- `fuzzy_threshold`: vocabulary fuzzy-match threshold 0.0–1.0 (default 0.85).
- `sentence_threshold`: sentence fuzzy-match threshold 0.0–1.0 (default 0.80).
- `session_time_limit`: seconds before the TUI suggests stopping (default 900).

Example:
```yaml
enabled_blocks:
  - vocabulary
  - conjugation
vocabulary_categories:
  - connectors
  - expressions
  - prepositions
max_items: 100
max_new: 40
fuzzy_threshold: 0.85
sentence_threshold: 0.80
session_time_limit: 900
```

### Master Vocabulary Management

#### Combine: Individual CSVs → Master File
```bash
python3 combine_csvs.py
```
Combines all individual CSV files from `vocabulary/` folder into `master_vocabulary.csv` with category tags. Run this whenever you update individual CSV files.
- Automatically converts comma-separated alternatives to pipe format (e.g., `"as, like"` → `as|like`)
- Removes duplicate entries
- Adds category column based on filename

#### Split: Master File → Individual CSVs
```bash
python3 split_master.py [options]
```
Splits `master_vocabulary.csv` back into individual category files in `vocabulary/` folder. Useful when you've been editing the master file directly.

**Options:**
- `--clean`: Remove existing CSV files before writing (recommended to avoid old files)
- `--backup`: Create timestamped backup of vocabulary folder before splitting
- `--keep-pipes`: Keep pipe delimiters instead of converting back to commas

**Examples:**
```bash
# Basic split (converts pipes back to commas)
python3 split_master.py

# Clean split (removes old files first)
python3 split_master.py --clean

# Safe split with backup
python3 split_master.py --backup --clean
```

**Workflow:**
1. Edit `master_vocabulary.csv` directly (add/modify entries)
2. Run `python3 split_master.py --clean` to sync back to individual files
3. Individual files are now updated with your changes

## CSV Data Structure

### Individual Vocabulary Files
Standard format (2 columns):
- **No header row**
- **Format**: `french_word,english_translation`
- **UTF-8 encoding** (supports French accents)
- **Multiple answers**: Use comma-space separation (e.g., `"as, like"`) for multiple acceptable translations

Example:
```csv
bonjour,hello
chat,cat
livre,book
"comme","as, like"
"son","his, her, sound"
```

Optional 3-column format with gender:
```csv
chat,cat,m
maison,house,f
```

**Note on multiple answers**: When you use quoted fields with comma-separated alternatives (like `"as, like"`), the `combine_csvs.py` script automatically converts these to pipe-delimited format (`as|like`) in the master file, which the flashcard app recognizes as multiple valid answers. Any one of the alternatives will be accepted as correct.

### Master Vocabulary File
Combined format (3-4 columns):
- **Format**: `french,english,category[,gender]`
- Category is auto-generated from source filename
- Generated by `combine_csvs.py`
- **Multiple answers** are stored with pipe delimiter (`|`)

Example:
```csv
bonjour,hello,flashcards
il pleut,it's raining,weather
aimer,to like,verbs
comme,as|like,Common 1
son,his|her|sound,Common 1
```

### Available Vocabulary Files (in vocabulary/ folder)
- `vocabulary/adjectives.csv` - Adjectives (50 words)
- `vocabulary/emotions.csv` - Emotions and feelings (41 words)
- `vocabulary/flashcards.csv` - General vocabulary (5 words)
- `vocabulary/la description physique.csv` - Physical descriptions (50 words)
- `vocabulary/le corps humain.csv` - Body parts (25 words)
- `vocabulary/les jours de la semaine.csv` - Days of the week (10 words)
- `vocabulary/les lieux publics.csv` - Public places (27 words)
- `vocabulary/les vêtements.csv` - Clothing vocabulary (43 words)
- `vocabulary/les_meilleurs_amis.csv` - Story vocabulary (56 words)
- `vocabulary/months.csv` - Months of the year (12 words)
- `vocabulary/prepositions.csv` - Prepositions and adverbs (33 words)
- `vocabulary/questions.csv` - Question words/phrases (35 words)
- `vocabulary/routine.csv` - Daily routine vocabulary (27 words)
- `vocabulary/verbs.csv` - Infinitive verbs (136 words)
- `vocabulary/weather.csv` - Weather-related terms (15 words)

## Code Architecture

### simple/flashcards.py
- **Entry point**: `main()` function
- **Flow**: load_cards() → shuffle → [english_study() OR french_study()] → save_missed()
- **Key behavior**:
  - Missed cards are appended to `missed.csv` (preserves existing entries)
  - If perfect score, clears `missed.csv`
  - Language direction controls UI prompts and card presentation order
  - Uses command-line arguments (position-based, not flags)
- **Purpose**: Simple, lightweight version for basic flashcard practice

### flashcards.py
- **Enhanced features**: SRS algorithm, typing modes, progress tracking, category filtering, interactive prompts
- **Interactive UI**: Prompts for language direction and category selection on startup
- **Data persistence**: Uses `.flashcard_data/` directory for storing:
  - `card_stats.json`: Per-card SRS data (review intervals, ease factors, due dates)
  - `progress.json`: Session history, streaks, overall statistics
- **Card class**: Supports french, english, category, and gender fields
- **Multiple study modes**: Multiple choice, typing (fuzzy/exact), timed challenges
- **Spaced Repetition**: CardStats (inherits from SRSStats) with SM-2 algorithm
- **Category filtering**: Interactive selection or command-line specification
- **Help system**: Built-in `--help` flag for detailed usage information
- **Backward compatible**: Works with all existing CSV formats (2, 3, or 4 columns)

### conjugations.py
- **Refactored design**: Uses `conjugation_engine.py` for all conjugation logic
- **8 tenses**: présent, futur proche, futur simple, imparfait, passé composé, conditionnel présent, conditionnel passé, subjonctif présent
- **Tier system**: verbs organized into core (~20), intermediate (~35), advanced (~40)
- **Interactive loop**: User selects tier, verb type, and tense; random verb chosen, all 6 pronouns tested
- **SRS support**: ConjugationStats class (inherits from SRSStats) tracks verb-tense combinations
  - Data persistence in `.conjugation_data/` directory
  - `conjugation_stats.json`: Per-combination SRS data (intervals, ease factors, due dates)
  - `conjugation_progress.json`: Session history and statistics
  - Quality ratings (0-3) determine next review interval
  - Filtering by due date when `--srs` flag is used

### conjugation_engine.py
- **Core module**: Loads verb data and generates conjugations algorithmically
- **Regular verb patterns**: Generates -ER and -IR conjugations using pattern rules
- **Irregular verbs**: Uses stored stems and forms from JSON data
- **Key functions**:
  - `conjugate(verb, tense, pronouns)`: Returns (pronouns, conjugated_forms)
  - `get_all_verbs()`, `get_verbs_by_type()`, `get_verbs_by_tier()`: Verb filtering
  - `get_translation()`: English translation lookup
- **Tense generation**:
  - Present: stem + endings (regular) or explicit forms (irregular)
  - Future: future stem + future endings
  - Imparfait: imparfait stem + imparfait endings
  - Passé composé: avoir/être present + past participle with agreement
  - Conditional: future stem + conditional endings

### conjugation_data/verbs.json
- **External verb database**: All verb definitions in JSON format
- **Verb entry structure**:
  ```json
  {
    "parler": {
      "type": "regular_er",
      "tier": "core",
      "translation": "to speak / to talk",
      "auxiliary": "avoir"
    },
    "être": {
      "type": "irregular",
      "tier": "core",
      "translation": "to be",
      "auxiliary": "être",
      "past_participle": "été",
      "stems": { "future": "ser", "imparfait": "ét" },
      "forms": { "present": ["suis", "es", "est", "sommes", "êtes", "sont"] }
    }
  }
  ```
- **Regular verbs**: Only need type, tier, translation, auxiliary
- **Irregular verbs**: Add past_participle, stems, and/or explicit forms as needed
- **Tiers**: core (most essential), intermediate (common), advanced (less common)

### grammar.py
- **Grammar trainer**: Fill-in-the-blank exercises with SRS support
- **Auto-discovery**: Loads topics from JSON files in `grammar_data/`
- **CLI**: `python3 grammar.py [--srs] [--level=N] [--stats] [--help]`
- **GrammarStats class**: Inherits from SRSStats (shared SM-2 algorithm)
- **Data persistence**: Uses `.grammar_data/` directory for SRS data
- **Answer checking**: Exact match, case-insensitive, with alternatives list
- **Hint system**: Type `h` during an exercise to see a hint

### grammar_data/*.json
- **Exercise data files**: Auto-discovered by grammar.py
- **Exercise structure**:
  ```json
  {
    "id": "pr001",
    "level": 1,
    "sentence_before": "C'est le livre",
    "sentence_after": "est sur la table.",
    "answer": "qui",
    "alternatives": [],
    "hint": "Sujet du verbe 'est'",
    "explanation": "'Qui' remplace le sujet du verbe."
  }
  ```
- **Fields**: `id` (unique), `level` (1-3), `sentence_before`/`sentence_after` (text around blank), `answer`, `alternatives` (e.g., `["qu'"]` for `que`), `hint`, `explanation`
- **Adding new topics**: Create a new JSON file in `grammar_data/` with `topic`, `description`, `levels`, and `exercises` keys

### sentence_data/*.json
- **Sentence-translation data files**: Auto-discovered by the `sentence` block (loaded in `exercise_types._load_sentence_exercises()`)
- **File structure**: top-level `topic`, `description`, and a `sentences` array
- **Sentence structure**:
  ```json
  {
    "id": "st001",
    "level": 1,
    "french": "Comment tu t'appelles ?",
    "english": "What is your name?",
    "alternatives_en": ["What's your name?"],
    "alternatives_fr": ["Comment vous vous appelez ?"],
    "hint": "s'appeler — question d'identité"
  }
  ```
- **Fields**: `id` (unique), `level`, `french`/`english` (the two directions), `alternatives_en`/`alternatives_fr` (extra accepted translations), `hint`
- **Matching**: fuzzy, using `sentence_threshold` from the config, plus the alternatives list for the target direction

### conjugation_sentence_data/*.json
- **Conjugation-in-context data files**: Auto-discovered by the `conjugation_sentence` block (loaded in `exercise_types._load_conjugation_sentence_exercises()`)
- **File structure**: top-level `topic`, `description`, and a `sentences` array
- **Sentence structure**:
  ```json
  {
    "id": "cs_passecompose_01",
    "verb": "aller",
    "tense": "past",
    "pronoun": "elle",
    "english": "Yesterday, she went to the market.",
    "french": "Hier, elle est allée au marché.",
    "alternatives_fr": []
  }
  ```
- **Fields**: `id` (unique across all files), `verb`/`tense`/`pronoun` (the target conjugation — `tense` is any code from `get_all_tenses()`; `pronoun` is a concrete subject: je/tu/il/elle/on/nous/vous/ils/elles), `english` (prompt), `french` (reference translation containing the correct verb form), optional `alternatives_fr` (extra accepted full-sentence phrasings), optional `register` override
- **Register**: the prompt shows a register cue to disambiguate English "you"/"we" — `tu`/`on` are labelled *informal*, `vous`/`nous` *formal*; other pronouns get no label. Register is derived from `pronoun` (via `register_for_pronoun()`), so authors don't set it; the optional `register` field only overrides that default.
- **The French verb form is NOT stored** — it is generated from `(verb, tense, pronoun)` by the engine at load/grade time, so it cannot drift from the conjugation logic
- **Adding sentences**: author natural EN/FR pairs, tag the target `(verb, tense, pronoun)`, then run the validator (below). The engine is the source of truth — any authored French whose verb form doesn't match the engine is rejected before it ships.

### validate_conjugation_sentences.py
- **Purpose**: Guarantees the conjugation-sentence bank stays accurate and reproducible
- **Checks** every sentence in `conjugation_sentence_data/*.json`: required fields present, `id` unique, `verb`/`tense`/`pronoun` known to the engine, and the engine-generated verb form actually appears (whole-token, accent-sensitive) in the authored `french` sentence
- **Run**: `uv run python validate_conjugation_sentences.py` (exit 0 = all valid, 1 = problems listed). Re-run after adding sentences or changing verb data.

### combine_csvs.py
- **Purpose**: Combines all individual CSV files into master_vocabulary.csv
- **Process**: Reads all CSVs from vocabulary/ folder, adds category column (from filename), removes duplicates
- **Multiple answers**: Converts comma-separated alternatives to pipe format (e.g., `"as, like"` → `as|like`)
- **Duplicate detection**: Based on matching french + english text (case-insensitive)
- **Output**: Creates master_vocabulary.csv with format: french,english,category[,gender]
- **Safe to re-run**: Overwrites master file each time, excludes missed.csv and master_vocabulary.csv itself

### split_master.py
- **Purpose**: Splits master_vocabulary.csv back into individual category files
- **Process**: Groups entries by category, writes to vocabulary/<category>.csv
- **Multiple answers**: Converts pipe delimiters back to comma-space format by default
- **Options**: --clean (remove old files), --backup (create backup), --keep-pipes (preserve pipes)
- **Use case**: When you've been editing master_vocabulary.csv directly and want to sync changes back

### srs_core.py
- **Shared SRS module**: Extracted from duplicated code across all 3 trainers
- **SRSStats class**: Base class with `update(quality)`, `to_dict()`, `from_dict()` — implements simplified SM-2 algorithm
- **INTERVALS**: `{0: 0, 1: 1, 2: 3, 3: 7}` days mapping for quality ratings
- **normalize_input()**: Unicode cleanup for accented character input (backspace handling, NFC normalization, invisible character removal)
- **load_stats() / save_stats()**: Generic file I/O for any SRSStats subclass
- **Inheritance**: CardStats, ConjugationStats, GrammarStats all inherit from SRSStats

### exercise_types.py
- **Exercise ABC**: Abstract base with `get_prompt()`, `get_correct()`, `check()`, `get_hint()`
- **VocabularyExercise**: Wraps a vocab card with random direction (French->English or English->French). Fuzzy matching with parenthetical expansion and configurable similarity threshold. Accepts cross-card synonyms and carries an optional example sentence.
- **ConjugationExercise**: Wraps a verb+tense+single random pronoun. Exact match checking; pattern hint for regular verbs; `je`->`j'` elision in display.
- **GrammarExercise**: Wraps a grammar exercise dict. Exact match with alternatives.
- **SentenceExercise**: Wraps a sentence dict with random direction. Fuzzy matching against the sentence plus `alternatives_en`/`alternatives_fr`, using `sentence_threshold`.
- **ConjugationSentenceExercise**: English→French sentence production. Derives the target verb form from the engine (`conjugate_one(verb, tense, pronoun)`, cached), shows the tense in the prompt, and grades with two gates: `verb_form_present()` (strict, accent-sensitive) AND whole-sentence fuzzy match. Hint combines verb translation + tense + engine pattern hint.
- **verb_form_present() / _normalize_for_token_match()**: Whole-token matching (apostrophes split to spaces, accents kept) used by both grading and the data validator so they agree on "is the verb present".
- **Config loading**: `_load_config()` reads `daily_trainer_config.yaml` (legacy JSON fallback) merged over defaults; `_load_enabled_blocks()`, `_vocab_category_allowed()` gate which blocks/categories are loaded.
- **load_all_due()**: Factory that loads due items from all enabled SRS pools with priority ordering (overdue > due today > new) and balanced round-robin sampling across types.
- **load_vocab_due() / load_conjugation_due() / load_grammar_due() / load_sentence_due() / load_conjugation_sentence_due()**: Single-block loaders for the focused dashboard modes.
- **get_due_counts()**: Lightweight per-type counter for dashboard display (disabled blocks report 0).
- **_fuzzy_match() / _expand_parens()**: Answer matching helpers shared by vocabulary and sentence exercises.

### daily_trainer.py
- **Textual TUI app**: Entry point for unified daily practice
- **DashboardScreen**: Mode selector (`1` Daily Mix, `2` Vocabulary, `3` Conjugation, `4` Grammar, `5` Sentences, `q` quit) with per-mode due counts, streak, and estimated time.
- **TenseSelectScreen / GrammarTopicSelectScreen**: Sub-selectors shown before the Conjugation and Grammar focused modes.
- **ExerciseScreen**: Presents exercises one at a time with progress bar and timer; `mode` selects the loader (mix/vocab/conjugation/grammar/sentence). Keybindings: `h` hint (via input), Escape to end early. Auto-advances after Enter on feedback. Appends example sentences for vocabulary.
- **SummaryScreen**: Shows results, per-type breakdown, missed items, streak. Keybindings: `d` dashboard, `q` quit.
- **Session persistence**: `.daily_trainer_data/progress.json` for streak and session history
- **SRS updates**: Writes to the same per-type stats files used by standalone trainers (`.flashcard_data/`, `.conjugation_data/`, `.grammar_data/`, `.sentence_data/`)
- **Config-driven**: Reads `daily_trainer_config.yaml` via `exercise_types._load_config()` for enabled blocks, caps, thresholds, and time limit
- **CSS**: Inline Textual CSS for layout and color-coded type labels (cyan=vocab, magenta=conjugation, yellow=grammar, green=sentence)

## Development Notes

- **Python version**: Requires Python 3.13+ (see `pyproject.toml`)
- **Dependencies**: `spyder-kernels>=3.1.0` (for development environment), `textual>=8.0.0` (TUI framework for daily trainer), `pyyaml>=6.0.3` (reads `daily_trainer_config.yaml`)
- **Package manager**: Uses `uv` (see `uv.lock`). **Always use `uv` for all Python-related operations** (installing packages, running scripts, etc.). Never use `pip` or bare `python`/`python3` directly.
- **No tests**: Currently no test suite
- **main.py**: Placeholder file, not used

## Common Workflows

### Adding New Vocabulary (Method 1: Edit Individual Files)
1. Add words to existing CSV file in vocabulary/ folder OR create new CSV file there
2. Use quoted fields for multiple acceptable answers: `"comme","as, like"`
3. Regenerate master file: `python3 combine_csvs.py`
4. Practice new words: `python3 flashcards.py --srs`

### Adding New Vocabulary (Method 2: Edit Master File Directly)
1. Edit `master_vocabulary.csv` directly (add/modify entries)
2. Use pipe delimiter for multiple answers: `comme,as|like,Common 1`
3. Sync changes back to individual files: `python3 split_master.py --clean`
4. Practice new words: `python3 flashcards.py --srs`

**Note:** Both methods are equivalent. Method 1 is better for organized vocabulary collection. Method 2 is faster for quick edits.

### Adding Verbs to Conjugation Trainer
1. Edit `conjugation_data/verbs.json`
2. Add a new verb entry with required fields:
   - `type`: "regular_er", "regular_ir", or "irregular"
   - `tier`: "core", "intermediate", or "advanced"
   - `translation`: English translation
   - `auxiliary`: "avoir" or "être" (for passé composé)
3. For irregular verbs, add as needed:
   - `past_participle`: if different from regular pattern
   - `stems`: object with irregular stems for future/imparfait/conditional
   - `forms`: object with explicit conjugation arrays for irregular tenses
4. Example regular verb:
   ```json
   "danser": {
     "type": "regular_er",
     "tier": "intermediate",
     "translation": "to dance",
     "auxiliary": "avoir"
   }
   ```
5. Example irregular verb:
   ```json
   "courir": {
     "type": "irregular",
     "tier": "intermediate",
     "translation": "to run",
     "auxiliary": "avoir",
     "past_participle": "couru",
     "stems": { "future": "courr" },
     "forms": { "present": ["cours", "cours", "court", "courons", "courez", "courent"] }
   }
   ```

### Recommended Daily Practice
```bash
# BEST: Unified daily session (vocab + conjugation + grammar mixed together)
python3 daily_trainer.py

# Or use individual trainers for focused practice:

# Check vocabulary due today
python3 flashcards.py --stats

# Check conjugations due today
python3 conjugations.py --stats

# Practice flashcards with SRS
python3 flashcards.py --srs

# Practice conjugations with SRS
python3 conjugations.py --srs

# Practice only core verbs (easiest to start with)
python3 conjugations.py --tier=core --srs

# Practice specific tense only (conjugations)
python3 conjugations.py --srs --tense=present

# Practice conditional tense
python3 conjugations.py --srs --tense=conditional

# Or pre-select category without prompts (flashcards)
python3 flashcards.py --category=verbs --srs

# Check grammar exercises due today
python3 grammar.py --stats

# Practice grammar with SRS
python3 grammar.py --srs

# Practice level 1 only (easiest - qui vs que)
python3 grammar.py --level=1
```

### Adding Grammar Exercises
1. Create a new JSON file in `grammar_data/` (or edit an existing one)
2. Follow the exercise structure with `id`, `level`, `sentence_before`, `sentence_after`, `answer`, `alternatives`, `hint`, `explanation`
3. The trainer auto-discovers new JSON files — no code changes needed
4. Possible future topics: COD/COI, articles, subjunctive triggers

### Resetting Progress
- Delete `.flashcard_data/` directory to reset flashcard SRS data and statistics
- Delete `.conjugation_data/` directory to reset conjugation SRS data and statistics
- Delete `.grammar_data/` directory to reset grammar SRS data and statistics
- Delete `.sentence_data/` directory to reset sentence-translation SRS data and statistics
- Delete `.conjugation_sentence_data/` directory to reset conjugation-in-context SRS data and statistics
- Delete `.daily_trainer_data/` directory to reset daily trainer streak and session history
- Note: Daily trainer shares SRS data with standalone trainers, so resetting any of the above affects both
