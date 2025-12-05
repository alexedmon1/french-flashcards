# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A French language learning application with multiple components:

### Flashcard Trainers
1. **Simple trainer** (`simple/flashcards.py`) - Basic vocabulary practice with CSV-based word lists
2. **Current trainer** (`flashcards.py`) - Advanced version with SRS, typing modes, progress tracking, and interactive prompts

### Additional Components
3. **Conjugation trainer** (`conjugations.py`) - Verb conjugation practice for present, future, and passé composé tenses
4. **Master vocabulary** (`master_vocabulary.csv`) - Combined file with all vocabulary from individual CSVs with category tags
5. **CSV combiner** (`combine_csvs.py`) - Tool to regenerate master vocabulary file

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
Practice French verb conjugations across three tenses (present, future, passé composé) with **91 verbs** and optional **SRS support**.

**Command-line options:**
- `--help`: Show detailed help message
- `--srs`: Spaced Repetition System (only reviews verb-tense combinations due today)
- `--stats`: Show progress statistics and exit

**Features:**
- Interactive verb type selection (regular -ER, regular -IR, irregular, or all)
- 91 total verbs (26 regular -ER, 20 regular -IR, 45 irregular)
- Randomized pronoun variations (il/elle/on, ils/elles) for natural practice
- Gender agreement for passé composé with être verbs
- SRS quality ratings (Wrong/Hard/Good/Easy) to optimize review schedule

**Examples:**
```bash
# Show help
python3 conjugations.py --help

# Normal practice mode (interactive)
python3 conjugations.py

# SRS mode - only practice due verbs
python3 conjugations.py --srs

# View your statistics
python3 conjugations.py --stats
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
- `missed.csv` - Auto-generated file tracking incorrectly recalled flashcards (root folder)

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
- **Spaced Repetition**: Simplified SM-2 algorithm with quality ratings (0-3)
- **Category filtering**: Interactive selection or command-line specification
- **Help system**: Built-in `--help` flag for detailed usage information
- **Backward compatible**: Works with all existing CSV formats (2, 3, or 4 columns)

### conjugations.py
- **Data-driven design**: Three dictionaries (PRESENT, FUTURE, PAST_COMPOSE) contain conjugation tables
- **Verb coverage**: 91 verbs total
  - **Regular -ER verbs (26)**: donner, trouver, penser, parler, aimer, passer, demander, laisser, porter, rester, tomber, montrer, écouter, dépenser, monter, dessiner, voler, raconter, quitter, garder, rencontrer, sembler, utiliser, travailler, couper, cuisiner
  - **Regular -IR verbs (20)**: finir, choisir, réussir, remplir, réfléchir, obéir, grandir, applaudir, établir, bâtir, agir, vieillir, grossir, maigrir, rougir, ralentir, avertir, guérir, saisir, nourrir
  - **Irregular verbs (45)**: être, avoir, faire, dire, aller, voir, savoir, pouvoir, vouloir, venir, devoir, prendre, mettre, croire, tenir, appeler, sortir, vivre, connaître, boire, écrire, lire, partir, dormir, ouvrir, recevoir, entendre, attendre, s'asseoir, se sentir, se quitter, obtenir, perdre, descendre, offrir, souffrir, découvrir, conduire, construire, produire, traduire, rire, suivre, naître, mourir, comprendre, apprendre
- **Passé composé structure**: Stored as tuples `(auxiliary_verb, [participle_forms])`
  - Auxiliary is either "être" or "avoir"
  - get_table() dynamically builds full conjugations from auxiliary + participle
- **Interactive loop**: User selects verb type and tense, random verb chosen, all 6 pronouns tested
- **SRS support**: ConjugationStats class tracks verb-tense combinations with SM-2 algorithm
  - Data persistence in `.conjugation_data/` directory
  - `conjugation_stats.json`: Per-combination SRS data (intervals, ease factors, due dates)
  - `conjugation_progress.json`: Session history and statistics
  - Quality ratings (0-3) determine next review interval
  - Filtering by due date when `--srs` flag is used

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

## Development Notes

- **Python version**: Requires Python 3.13+ (see `pyproject.toml`)
- **Dependencies**: `spyder-kernels>=3.1.0` (for development environment)
- **Package manager**: Uses `uv` (see `uv.lock`)
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
1. Add entries to PRESENT, FUTURE, and PAST_COMPOSE dictionaries in `conjugations.py`
2. For passé composé, specify correct auxiliary verb ("être" or "avoir")
3. Ensure all 6 pronoun forms are included in correct order: je, tu, il/elle/on, nous, vous, ils/elles
4. Add English translation to VERB_TRANSLATIONS dictionary
5. Add verb to appropriate category in VERB_TYPES ("regular_er", "regular_ir", or "irregular")
6. Update verb counts in choose_verb_type() function if needed

### Recommended Daily Practice
```bash
# Check vocabulary due today
python3 flashcards.py --stats

# Check conjugations due today
python3 conjugations.py --stats

# Practice flashcards with SRS
python3 flashcards.py --srs

# Practice conjugations with SRS
python3 conjugations.py --srs

# Or pre-select category without prompts (flashcards)
python3 flashcards.py --category=verbs --srs
```

### Resetting Progress
- Delete `.flashcard_data/` directory to reset flashcard SRS data and statistics
- Delete `.conjugation_data/` directory to reset conjugation SRS data and statistics
