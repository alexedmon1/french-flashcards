# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A French language learning application with multiple components:

### Flashcard Trainers
1. **Simple trainer** (`simple/flashcards.py`) - Basic vocabulary practice with CSV-based word lists
2. **Current trainer** (`flashcards.py`) - Advanced version with SRS, typing modes, progress tracking, and interactive prompts

### Additional Components
3. **Conjugation trainer** (`conjugations.py`) - Verb conjugation practice for 5 tenses with tier system
4. **Conjugation engine** (`conjugation_engine.py`) - Core conjugation logic module
5. **Verb data** (`conjugation_data/verbs.json`) - External JSON database of verbs
6. **Grammar trainer** (`grammar.py`) - Fill-in-the-blank grammar exercises with SRS support
7. **Grammar data** (`grammar_data/`) - JSON exercise files, auto-discovered by the trainer
8. **Master vocabulary** (`master_vocabulary.csv`) - Combined file with all vocabulary from individual CSVs with category tags
9. **CSV combiner** (`combine_csvs.py`) - Tool to regenerate master vocabulary file

### Unified Daily Trainer
10. **Daily trainer** (`daily_trainer.py`) - Textual TUI combining all 3 trainers into one daily session
11. **SRS core** (`srs_core.py`) - Shared SM-2 algorithm and utilities used by all trainers
12. **Exercise types** (`exercise_types.py`) - Unified exercise abstraction and session loader

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
Practice French verb conjugations across **5 tenses** with **93 verbs** organized by tier, and optional **SRS support**.

**Tenses available:**
- Présent (present)
- Futur simple (future)
- Imparfait (imparfait)
- Passé composé (past)
- Conditionnel présent (conditional)

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
Textual TUI that combines vocabulary, conjugation, and grammar into a single daily practice session. Pulls due items from all 3 SRS pools and presents them in a mixed flow.

**Screens:**
- **Dashboard**: Shows due counts per type (vocabulary/conjugation/grammar), streak, estimated time. Press `s` to start, `q` to quit.
- **Exercise**: Mixed session of up to 25 items, balanced equally across the 3 types (~8 each). Progress bar and timer at top. Type answer and press Enter. Type `h` for a hint. Press Escape to end early. After 15 minutes, suggests a stopping point.
- **Summary**: Time elapsed, accuracy, per-type breakdown, missed items list, streak update. Press `d` for dashboard, `q` to quit.

**Exercise behavior:**
- **Vocabulary**: Random direction per card (French->English or English->French). Fuzzy matching with 85% similarity threshold. Parenthetical parts are optional (e.g., "to sit down" matches "to sit (down)").
- **Conjugation**: Single random pronoun per card (not all 6) for faster pace.
- **Grammar**: Fill-in-the-blank, same as standalone grammar trainer.
- **Quality ratings**: Auto-calculated (correct=Good/2, wrong=Wrong/0) — no manual rating step.

**Session algorithm:**
- Collects due items from all 3 pools (overdue + due today + new)
- Balanced round-robin: each type gets ~1/3 of session slots
- New items capped at 5 per session to avoid overwhelm
- Overdue items prioritized within each type

**Data:**
- SRS data shared with standalone trainers (same `.flashcard_data/`, `.conjugation_data/`, `.grammar_data/` directories)
- Session history and streak in `.daily_trainer_data/progress.json`

**Examples:**
```bash
# Launch the TUI
python3 daily_trainer.py
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
- `vocabulary/flashcards.csv` - General vocabulary (5 words)
- `vocabulary/verbs.csv` - Infinitive verbs (48 words)
- `vocabulary/weather.csv` - Weather-related terms (27 words)
- `vocabulary/clothing.csv` - Clothing vocabulary (26 words)
- `vocabulary/locations.csv` - Places and locations (27 words)
- `vocabulary/prepositions.csv` - Prepositions (27 words)
- `vocabulary/questions.csv` - Question words/phrases (35 words)
- `vocabulary/routine.csv` - Daily routine vocabulary (43 words)
- `vocabulary/freq_words.csv` - Frequently used words (498 words)

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
- **5 tenses**: présent, futur simple, imparfait, passé composé, conditionnel présent
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
- **VocabularyExercise**: Wraps a vocab card with random direction (French->English or English->French). Fuzzy matching with parenthetical expansion and 85% similarity threshold.
- **ConjugationExercise**: Wraps a verb+tense+single random pronoun. Exact match checking.
- **GrammarExercise**: Wraps a grammar exercise dict. Exact match with alternatives.
- **load_all_due()**: Factory that loads due items from all 3 SRS pools with balanced round-robin sampling across types
- **get_due_counts()**: Lightweight counter for dashboard display
- **_fuzzy_match() / _expand_parens()**: Answer matching helpers for vocabulary

### daily_trainer.py
- **Textual TUI app**: Entry point for unified daily practice
- **DashboardScreen**: Shows due counts, streak, estimated time. Keybindings: `s` start, `q` quit.
- **ExerciseScreen**: Presents exercises one at a time with progress bar and timer. Keybindings: `h` hint (via input), Escape to end early. Auto-advances after Enter on feedback.
- **SummaryScreen**: Shows results, per-type breakdown, missed items, streak. Keybindings: `d` dashboard, `q` quit.
- **Session persistence**: `.daily_trainer_data/progress.json` for streak and session history
- **SRS updates**: Writes to the same per-type stats files used by standalone trainers
- **CSS**: Inline Textual CSS for layout and color-coded type labels (cyan=vocab, magenta=conjugation, yellow=grammar)

## Development Notes

- **Python version**: Requires Python 3.13+ (see `pyproject.toml`)
- **Dependencies**: `spyder-kernels>=3.1.0` (for development environment), `textual>=8.0.0` (TUI framework for daily trainer)
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
- Delete `.daily_trainer_data/` directory to reset daily trainer streak and session history
- Note: Daily trainer shares SRS data with standalone trainers, so resetting any of the above affects both
