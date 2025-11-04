# Master Vocabulary File Guide

## Overview

You now have a **master vocabulary file** (`master_vocabulary.csv`) that combines all your individual vocabulary CSV files into one convenient file. This makes it easier to:
- Upload to other platforms or apps
- Practice from your entire vocabulary set
- Filter by specific topics/categories
- Track overall progress

## How It Was Created

The `combine_csvs.py` script:
1. Reads all CSV files in the directory (except `missed.csv` and `master_vocabulary.csv`)
2. Adds a "category" column based on the source filename
3. Removes duplicate entries
4. Combines everything into `master_vocabulary.csv`

## File Format

**Master vocabulary format:**
```
french,english,category[,gender]
```

**Example:**
```csv
bonjour,hello,flashcards
il pleut,it's raining,weather
aimer,to like,verbs
```

## Using the Master File

### Practice All Vocabulary
```bash
# Practice all 736+ words together
python3 flashcards_v2.py master_vocabulary.csv english --srs
```

### List Available Categories
```bash
# See what categories are available
python3 flashcards_v2.py master_vocabulary.csv english --list-categories
```

**Output:**
```
📚 Available categories in master_vocabulary.csv:
   Total cards: 736

   • clothing             (26 cards)
   • flashcards           (5 cards)
   • freq_words           (498 cards)
   • locations            (27 cards)
   • prepositions         (27 cards)
   • questions            (35 cards)
   • routine              (43 cards)
   • verbs                (48 cards)
   • weather              (27 cards)
```

### Practice Specific Category
```bash
# Practice just weather vocabulary
python3 flashcards_v2.py master_vocabulary.csv english --category=weather

# Practice just verbs with SRS
python3 flashcards_v2.py master_vocabulary.csv french --category=verbs --srs

# Practice frequent words in expert mode
python3 flashcards_v2.py master_vocabulary.csv english --category=freq_words --mode=expert --srs
```

## Updating the Master File

Whenever you:
- Add new words to individual CSV files
- Create new CSV files
- Want to refresh the master file

Simply run:
```bash
python3 combine_csvs.py
```

This will:
- Re-scan all CSV files
- Remove duplicates
- Update `master_vocabulary.csv`

**Note:** This is safe to run multiple times. It overwrites the master file each time.

## Statistics

From your current vocabulary files:
- **Total entries**: 751 words/phrases
- **Duplicates removed**: 15
- **Unique entries**: 736
- **Categories**: 9

### Breakdown by Category:
| Category | Cards |
|----------|-------|
| freq_words | 498 |
| verbs | 48 |
| routine | 43 |
| questions | 35 |
| locations | 27 |
| prepositions | 27 |
| weather | 27 |
| clothing | 26 |
| flashcards | 5 |

## Benefits

### 1. **Easier to Share/Upload**
- Single file instead of 9+ separate files
- Can upload to Anki, Quizlet, or other platforms
- Easier to back up

### 2. **Flexible Practice**
- Practice everything together for comprehensive review
- Focus on specific topics when needed
- Mix and match with flags

### 3. **Better Progress Tracking**
- SRS tracks progress across all vocabulary
- See overall improvement, not just per-file
- One unified learning journey

### 4. **Category-Based Learning**
- Study thematically (all weather words together)
- Focus on weak areas (practice just verbs)
- Build knowledge systematically

## Example Workflows

### Daily Comprehensive Practice
```bash
# Review all cards due today across all categories
python3 flashcards_v2.py master_vocabulary.csv english --srs --mode=medium
```

### Topic-Focused Session
```bash
# Master weather vocabulary this week
python3 flashcards_v2.py master_vocabulary.csv english --category=weather --mode=hard
```

### Quick Reference Check
```bash
# See what topics you can practice
python3 flashcards_v2.py master_vocabulary.csv english --list-categories

# Check your progress
python3 flashcards_v2.py master_vocabulary.csv english --stats
```

### Exam Preparation
```bash
# Intense practice on frequent words
python3 flashcards_v2.py master_vocabulary.csv english --category=freq_words --mode=expert --srs
```

## Still Have Individual Files?

Yes! All your original CSV files are still there:
- `weather.csv`
- `verbs.csv`
- `clothing.csv`
- etc.

You can still use them individually:
```bash
python3 flashcards_v2.py weather.csv english
```

The master file is just an additional option, not a replacement.

## Technical Details

### Duplicate Handling
- Duplicates are identified by matching `french` + `english` text (case-insensitive)
- If the same word appears in multiple files, only one copy is kept
- The category from the first occurrence is used

### Category Names
- Automatically extracted from filename
- `weather.csv` → category: `weather`
- `freq_words.csv` → category: `freq_words`

### Gender Support
- If your individual CSVs have a 3rd gender column, it's preserved
- Format becomes: `french,english,category,gender`
- Currently your files don't have gender info, but the system supports it

## Adding Gender Information

If you want to add gender to your vocabulary:

1. **Edit individual CSV files:**
   ```csv
   chat,cat,m
   maison,house,f
   ```

2. **Re-run the combine script:**
   ```bash
   python3 combine_csvs.py
   ```

3. **Master file will include gender:**
   ```csv
   chat,cat,flashcards,m
   maison,house,flashcards,f
   ```

4. **Practice with gender:**
   ```bash
   python3 flashcards_v2.py master_vocabulary.csv english --gender
   ```

## Summary

✅ **Created**: `master_vocabulary.csv` with 736 unique entries
✅ **Tool**: `combine_csvs.py` to regenerate/update
✅ **Features**: Category filtering, list categories, full compatibility
✅ **Compatible**: Works with both `flashcards.py` and `flashcards_v2.py`

**Quick Commands:**
```bash
# Regenerate master file
python3 combine_csvs.py

# List categories
python3 flashcards_v2.py master_vocabulary.csv english --list-categories

# Practice specific category
python3 flashcards_v2.py master_vocabulary.csv english --category=verbs --srs

# Practice everything
python3 flashcards_v2.py master_vocabulary.csv english --srs
```

Happy learning! 🇫🇷📚
