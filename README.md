# French Daily 🇫🇷

A comprehensive French language learning application with intelligent flashcard trainers, spaced repetition system, and verb conjugation practice. Perfect for building vocabulary and improving French language skills.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Features](#features)
- [Understanding the Tools](#understanding-the-tools)
- [File Formats](#file-formats)
- [Tips for Effective Learning](#tips-for-effective-learning)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## Quick Start

**New to the project?** Just run this command and follow the prompts:

```bash
python3 flashcards.py
```

It will ask you:
1. Which direction to practice (French→English or English→French)
2. Which category to focus on (or practice all)

**For daily practice with spaced repetition:**

```bash
python3 flashcards.py --srs
```

This only shows cards that are due for review today, making practice sessions efficient and focused.

## Installation

### Prerequisites

- **Python 3.13 or higher** - Check your version:
  ```bash
  python3 --version
  ```

- **No external dependencies required!** This project uses only Python's standard library.

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alexedmon1/french-daily.git
   cd french-daily
   ```

2. **Verify it works:**
   ```bash
   python3 flashcards.py --help
   ```

3. **Start learning:**
   ```bash
   python3 flashcards.py
   ```

That's it! No installation, no packages, just run and learn.

## Usage Guide

### Main Flashcard Trainer (Recommended)

The main trainer (`flashcards.py`) is feature-rich with interactive prompts, spaced repetition, and multiple difficulty modes.

**Basic Usage:**
```bash
python3 flashcards.py
```

**With Options:**
```bash
# Practice with spaced repetition
python3 flashcards.py --srs

# Choose difficulty mode
python3 flashcards.py --mode=easy     # Multiple choice
python3 flashcards.py --mode=medium   # Type with fuzzy matching (default)
python3 flashcards.py --mode=hard     # Exact typing required
python3 flashcards.py --mode=expert   # Timed (10 seconds) + exact typing

# Practice specific category
python3 flashcards.py --category=verbs --srs

# Practice with gender questions
python3 flashcards.py --gender

# View your progress
python3 flashcards.py --stats

# List available categories
python3 flashcards.py --list-categories

# Use a different vocabulary file
python3 flashcards.py weather.csv
```

**Combining Options:**
```bash
# Expert mode with SRS and gender practice
python3 flashcards.py --srs --mode=expert --gender

# Hard mode focusing on verbs
python3 flashcards.py --category=verbs --mode=hard
```

### Simple Trainer

For quick, no-frills practice:

```bash
# French → English
python3 simple/flashcards.py flashcards.csv english

# English → French
python3 simple/flashcards.py verbs.csv french
```

### Conjugation Trainer

Practice verb conjugations with intelligent spaced repetition:

```bash
# Interactive practice (choose verb type and tense)
python3 conjugations.py

# Practice with SRS (only verbs due today)
python3 conjugations.py --srs

# Practice specific tense only with SRS
python3 conjugations.py --srs --tense=present
python3 conjugations.py --srs --tense=future
python3 conjugations.py --srs --tense=past

# View your conjugation statistics
python3 conjugations.py --stats

# Get help
python3 conjugations.py --help
```

**Features:**
- **91 French verbs** across 3 tenses (present, future, passé composé)
- **Spaced Repetition System** - Tracks each verb-tense combination separately
- **Quality ratings** - Rate difficulty (Wrong/Hard/Good/Easy) to optimize review schedule
- **Progress tracking** - View statistics and identify challenging verbs
- **Interactive selection** - Choose verb types: regular -ER (26), regular -IR (20), or irregular (45)

Includes all essential verbs (être, avoir, aller, faire), common regular verbs, and important irregular verbs (voir, dire, prendre, mettre, conduire, comprendre, etc.).

## Project Structure


```
french-daily/
├── flashcards.py         # Main trainer (interactive, SRS, progress tracking)
├── simple/               # Simple flashcard trainer
│   └── flashcards.py    # Basic trainer (command-line args)
├── vocabulary/          # Source vocabulary files (edit these!)
│   ├── flashcards.csv   # General vocabulary (5 words)
│   ├── verbs.csv        # Verb infinitives (48 words)
│   ├── weather.csv      # Weather terms (27 words)
│   ├── clothing.csv     # Clothing items (26 words)
│   ├── locations.csv    # Places and locations (27 words)
│   ├── prepositions.csv # Prepositions (27 words)
│   ├── questions.csv    # Question words (35 words)
│   ├── routine.csv      # Daily routine (43 words)
│   └── freq_words.csv   # Common words (498 words)
├── master_vocabulary.csv # Combined vocabulary (auto-generated)
├── combine_csvs.py      # Tool to regenerate master vocabulary
├── conjugations.py      # Verb conjugation practice with SRS
├── missed.csv           # Auto-generated: cards you got wrong
├── .flashcard_data/     # Auto-generated: flashcard progress
│   ├── card_stats.json  # SRS scheduling per card
│   └── progress.json    # Session history and streaks
└── .conjugation_data/   # Auto-generated: conjugation progress
    ├── conjugation_stats.json  # SRS scheduling per verb-tense
    └── conjugation_progress.json  # Conjugation practice history
```

## Features

### Current Trainer (`flashcards.py`)
 **Interactive prompts** - Asks for language direction and category
 **Spaced Repetition System (SRS)** - Optimal review scheduling
 **Multiple difficulty modes** - Easy, Medium, Hard, Expert
 **Progress tracking** - Streaks, statistics, session history
 **Category filtering** - Practice specific topics
 **Gender practice** - Learn masculine/feminine nouns
 **Help system** - Built-in documentation

### Simple Trainer (`simple/flashcards.py`)
- Basic flashcard practice with y/N self-assessment
- Lightweight and straightforward
- Good for quick reviews

### Conjugation Trainer (`conjugations.py`)
- **Spaced Repetition System** - Practice verbs due for review
- **91 verbs** included (26 regular -ER, 20 regular -IR, 45 irregular)
- **3 tenses** - Present, Future simple, Passé composé
- **Tense filtering** - Focus SRS practice on specific tense with `--tense`
- **Quality ratings** - Wrong/Hard/Good/Easy determine review schedule
- **Progress tracking** - View statistics and challenging verbs
- **Interactive selection** - Choose verb type and tense
- **Command-line options** - `--srs`, `--tense`, `--stats`, `--help`

## Vocabulary

**Master vocabulary**: 808 unique words across 9 categories:
- clothing (26 cards)
- flashcards (5 cards)
- freq_words (498 cards)
- locations (27 cards)
- prepositions (27 cards)
- questions (35 cards)
- routine (43 cards)
- verbs (120 cards)
- weather (27 cards)

## Documentation

- **CLAUDE.md** - Complete developer/AI assistant documentation
- **IMPROVEMENTS.md** - Detailed guide to current trainer features
- **MASTER_VOCABULARY.md** - Guide to using the master vocabulary file

## Daily Practice Workflow

```bash
# 1. Check your progress
python3 flashcards.py --stats
python3 conjugations.py --stats

# 2. Practice flashcards due today (5-10 minutes)
python3 flashcards.py --srs

# 3. Practice verb conjugations due today (5-10 minutes)
python3 conjugations.py --srs

# 4. Or focus on a specific tense
python3 conjugations.py --srs --tense=present
```

**Pro tip**: Consistent daily practice with SRS is more effective than long irregular sessions!

## Understanding the Tools

### What is Spaced Repetition (SRS)?

Spaced Repetition is a learning technique that shows you flashcards at increasing intervals:

- **New cards**: Review immediately
- **Easy cards**: Review after 1 day → 3 days → 1 week → 2 weeks → 1 month...
- **Hard cards**: Review more frequently until you master them
- **Forgotten cards**: Reset and review again

This is proven to be the most effective way to memorize vocabulary long-term. The app automatically schedules reviews for you!

### Difficulty Modes Explained

| Mode | Method | Best For | Challenge Level |
|------|--------|----------|-----------------|
| **Easy** | Multiple choice (4 options) | New vocabulary, beginners | ⭐ |
| **Medium** | Type answer (fuzzy matching) | Regular practice, typos OK | ⭐⭐ |
| **Hard** | Type answer (exact match) | Mastery, advanced learners | ⭐⭐⭐ |
| **Expert** | Type answer (exact, 10s timer) | Fluency building, exam prep | ⭐⭐⭐⭐ |

**Fuzzy matching** (Medium mode) means minor typos are accepted - "librairy" for "library" = ✓
**Exact matching** (Hard/Expert) requires perfect spelling.

### How Progress Tracking Works

Your progress is saved in `.flashcard_data/`:

- **card_stats.json**: Remembers when you last saw each card, how well you knew it, and when to show it again
- **progress.json**: Tracks your daily streak, session history, and accuracy over time

**Example:**
```
Session 1 (Oct 1): 45/50 cards correct (90%)
Session 2 (Oct 2): 42/45 cards correct (93%)  ← Streak: 2 days!
```

## File Formats

### CSV Vocabulary Files

**Basic format** (2 columns, no header):
```csv
bonjour,hello
chat,cat
livre,book
```

**With gender** (3 columns):
```csv
chat,cat,m
maison,house,f
table,table,f
```

**With multiple translations** (using `|` separator):
```csv
bonjour,hello|hi|good morning
merci,thank you|thanks
au revoir,goodbye|bye|see you later
```

The program will accept any of the alternatives as correct! This is especially useful for:
- Words with multiple valid translations
- Formal vs. informal expressions
- Regional variations

**Master vocabulary format** (with categories):
```csv
bonjour,hello,flashcards
il pleut,it's raining,weather
aimer,to like,verbs
```

### Creating Your Own Vocabulary

1. **Create a new CSV file:**
   ```csv
   pain,bread
   fromage,cheese
   vin,wine
   ```

2. **Use it directly:**
   ```bash
   python3 flashcards.py food.csv
   ```

3. **Or add to master vocabulary:**
   ```bash
   # Adds food.csv to master_vocabulary.csv with category="food"
   python3 combine_csvs.py
   ```

## Tips for Effective Learning

### 🎯 Daily Practice Routine

**5-10 minutes per day is better than 1 hour once a week!**

```bash
# Morning: Check what's due
python3 flashcards.py --stats
python3 conjugations.py --stats

# Flashcard practice (5-10 min)
python3 flashcards.py --srs --mode=medium

# Conjugation practice (5-10 min)
python3 conjugations.py --srs

# Or focus on one tense at a time
python3 conjugations.py --srs --tense=present
```

### 📈 Progression Path

1. **Week 1**: Use `--mode=easy` to get familiar with words
2. **Week 2-4**: Switch to `--mode=medium` for active recall
3. **Month 2+**: Try `--mode=hard` to perfect spelling
4. **Advanced**: Use `--mode=expert` for fluency under pressure

### 🔄 Both Directions

Practice both ways for complete mastery:
- **French → English**: Helps with reading and listening comprehension
- **English → French**: Essential for speaking and writing

### 📊 Track Your Progress

```bash
# Check your stats regularly
python3 flashcards.py --stats
```

Watch your accuracy improve over time!

### 💡 Pro Tips

- **Use categories** to focus on themes (e.g., study "weather" before a trip)
- **Enable `--gender`** to learn noun genders from the start
- **Review missed cards** immediately after a session (they're saved in `missed.csv`)
- **Don't break your streak!** Consistency is key to retention

## Troubleshooting

### "No cards due for review today"

This is **good**! It means you've reviewed everything recently. Either:
- Practice without `--srs` flag to review all cards
- Come back tomorrow when cards are due again
- Add new vocabulary to practice

### Cards showing up too frequently / not frequently enough

The SRS algorithm adjusts based on your performance:
- **Getting everything right?** Cards will space out more
- **Missing some?** They'll appear more often
- Give it a few sessions to calibrate to your level

### Reset All Progress

```bash
# Reset flashcard progress
rm -rf .flashcard_data/

# Reset conjugation progress
rm -rf .conjugation_data/

# Reset both
rm -rf .flashcard_data/ .conjugation_data/
```

This deletes all SRS scheduling and statistics. Fresh start!

### Import/Export Progress

The `.flashcard_data/` folder contains JSON files you can:
- **Backup**: Copy the folder elsewhere
- **Restore**: Copy it back to restore progress
- **Share**: Send to another device to sync progress

### Wrong Python Version

If you see "Python 3.13+ required":
```bash
# Check version
python3 --version

# Install newer Python (varies by OS)
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.13

# macOS (Homebrew):
brew install python@3.13
```

## Vocabulary Included

**808 unique words** across 9 categories:

| Category | Count | Description |
|----------|-------|-------------|
| freq_words | 498 | Most common French words - excellent starting point |
| verbs | 120 | Essential verb infinitives |
| routine | 43 | Daily routine and activities |
| questions | 35 | Question words and interrogative phrases |
| locations | 27 | Places, buildings, locations |
| prepositions | 27 | Prepositions and spatial words |
| weather | 27 | Weather terminology |
| clothing | 26 | Clothing and accessories |
| flashcards | 5 | Basic starter vocabulary |

**Total**: Enough vocabulary for basic conversational French!

## Documentation

- **README.md** (this file) - User guide and getting started
- **CLAUDE.md** - Complete developer/AI assistant documentation
- **IMPROVEMENTS.md** - Detailed feature guide for current trainer
- **MASTER_VOCABULARY.md** - Guide to the master vocabulary system

## Contributing

Want to add vocabulary?

1. Edit existing CSV files or create new ones
2. Run `python3 combine_csvs.py` to update master vocabulary
3. (Optional) Submit a pull request to share with others!

## Requirements

- **Python 3.13 or higher** (no external dependencies!)
- Works on: Windows (WSL), macOS, Linux
- ~5MB disk space (including all vocabulary)

## FAQ

**Q: Do I need internet?**
A: No! Everything works offline.

**Q: Where is my progress saved?**
A: In `.flashcard_data/` (flashcards) and `.conjugation_data/` (conjugations) folders (auto-created).

**Q: Can I practice on multiple devices?**
A: Yes! Copy the `.flashcard_data/` and `.conjugation_data/` folders between devices.

**Q: How long until I'm fluent?**
A: With 808 words + 91 verbs (273 verb-tense combinations) + daily practice, you'll have a solid foundation in 2-3 months. Fluency requires ongoing practice and immersion!

**Q: Can I add my own vocabulary?**
A: Absolutely! Just edit the CSV files or create new ones.

**Q: What if I make a typo?**
A: Use `--mode=medium` (default) which accepts minor typos.

## License

Personal learning project. Feel free to use and modify for your own French learning journey!

---

**Happy learning! Bonne chance! 🇫🇷**
