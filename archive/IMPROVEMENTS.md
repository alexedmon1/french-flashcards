# French Daily - Enhanced Version Documentation

## Overview

This document explains the improvements made to the French flashcard learning system in `flashcards_v2.py`. The enhanced version addresses all major learning challenges while maintaining backward compatibility with your existing CSV files.

---

## What's New

### 1. **Spaced Repetition System (SRS)**
*Improves long-term retention*

**Problem Solved**: Reviewing the same cards every time is inefficient. You waste time on words you already know and don't focus enough on difficult ones.

**How It Works**:
- Each card tracks: times seen, times correct, last review date, and difficulty level
- Cards you get wrong appear more frequently
- Cards you know well are shown less often (with increasing intervals: 1 day → 3 days → 1 week → etc.)
- Only reviews cards that are "due" on a given day
- Uses a simplified SM-2 algorithm (the same concept Anki uses)

**Usage**:
```bash
python flashcards_v2.py flashcards.csv english --srs
```

**Data Storage**:
- Creates `.flashcard_data/card_stats.json` to track each card's history
- Survives between sessions - your progress is saved!

---

### 2. **Typing Practice Mode**
*Makes practice more active and engaging*

**Problem Solved**: Just thinking the answer and pressing 'y' is passive. You might think you know it but can't actually produce the word.

**How It Works**:
- You must type the actual translation (not just y/N)
- Uses fuzzy matching to allow minor typos (85% similarity threshold)
- Gives immediate feedback on how close you were
- Multiple difficulty levels available

**Modes**:
- **Easy**: Multiple choice (4 options) - great for beginners
- **Medium** (default): Type answer, fuzzy matching - best for most learners
- **Hard**: Type answer, exact match required - for advanced learners
- **Expert**: Type answer, exact match, 10-second time limit - intense practice!

**Usage**:
```bash
# Medium (default) - forgiving typos
python flashcards_v2.py verbs.csv english

# Easy mode for new vocabulary
python flashcards_v2.py weather.csv french --mode=easy

# Hard mode for mastery
python flashcards_v2.py flashcards.csv english --mode=hard

# Expert mode with time pressure
python flashcards_v2.py freq_words.csv english --mode=expert
```

---

### 3. **Progress Tracking & Statistics**
*Visualize your improvement over time*

**Problem Solved**: No way to see if you're actually getting better or track consistency.

**What's Tracked**:
- Session history (date, cards studied, accuracy %)
- Daily streak counter
- Overall accuracy across all sessions
- Recent session performance

**Data Storage**:
- Creates `.flashcard_data/progress.json`

**Usage**:
```bash
# View your stats
python flashcards_v2.py flashcards.csv english --stats

# Stats are shown automatically at the start of each session
python flashcards_v2.py verbs.csv english --srs
```

**Example Output**:
```
=== Your Progress ===
🔥 Current streak: 5 day(s)
📊 Total sessions: 12

Recent sessions:
   2025-10-28: 45/50 (90.0%)
   2025-10-29: 38/42 (90.5%)
   2025-10-30: 47/48 (97.9%)

Overall accuracy: 87.3%
```

---

### 4. **Gender Learning Support**
*Practice masculine/feminine nouns*

**Problem Solved**: French noun genders are hard to remember, and there's no built-in practice.

**How It Works**:
- Supports optional 3rd column in CSV files: `french,english,gender`
- After correctly answering a card, asks bonus gender question
- Gender can be: `m`, `f`, `masculine`, `feminine`
- Fully backward compatible - works fine with 2-column CSVs (just skips gender)

**CSV Format**:
```csv
chat,cat,m
maison,house,f
livre,book,m
table,table,f
```

**Usage**:
```bash
python flashcards_v2.py flashcards.csv english --gender
```

**What It Looks Like**:
```
Translate: chat
Your answer: cat
✅ Correct!

Bonus: What's the gender of 'chat'?
(m/f): m
✅ Correct gender!
```

---

### 5. **Difficulty Level Modes**
*Adapt practice to your skill level*

**Problem Solved**: One-size-fits-all isn't ideal. Beginners need scaffolding; advanced learners need challenges.

**Mode Comparison**:

| Mode   | Answer Style | Matching | Time Limit | Best For |
|--------|-------------|----------|------------|----------|
| Easy   | Multiple choice (4 options) | Exact | None | New vocabulary, first exposure |
| Medium | Type answer | Fuzzy (85%) | None | Most learners, regular practice |
| Hard   | Type answer | Exact | None | Advanced learners, mastery |
| Expert | Type answer | Exact | 10 seconds | Fluency building, exam prep |

**Quality Scores** (affects SRS scheduling):
- Perfect answer quickly → "Easy" (longer interval)
- Correct answer → "Good" (normal interval)
- Close/typo answer → "Hard" (shorter interval)
- Wrong answer → Review again soon

---

## Complete Usage Examples

### Starting Out (New Vocabulary)
```bash
# Easy mode, see all words
python flashcards_v2.py weather.csv english --mode=easy
```

### Regular Practice (Recommended)
```bash
# SRS mode, medium difficulty, with gender practice
python flashcards_v2.py flashcards.csv english --srs --gender --mode=medium
```

### Advanced Practice
```bash
# Hard mode with SRS for serious retention
python flashcards_v2.py verbs.csv french --srs --mode=hard
```

### Building Fluency
```bash
# Expert mode with time pressure
python flashcards_v2.py freq_words.csv english --mode=expert --srs
```

### Check Your Progress
```bash
python flashcards_v2.py flashcards.csv english --stats
```

---

## How the SRS Algorithm Works

**Simplified SM-2 Implementation**:

1. **First Time**: Card starts with no history
2. **Get It Wrong**: Review again in the same session (interval = 0 days)
3. **Get It Right**:
   - First time: Review in 1-7 days (based on how easy it was)
   - Subsequent times: Interval multiplies by an "ease factor" (typically 2.5x)

**Example Timeline**:
```
Day 0:  Learn "chat" → Answer: GOOD
Day 3:  Review "chat" → Answer: EASY
Day 10: Review "chat" → Answer: GOOD
Day 28: Review "chat" → Answer: GOOD
... and so on with increasing intervals
```

**If You Get It Wrong**:
- Interval resets to 0
- Review again in the same session or tomorrow
- Ease factor decreases slightly (makes future intervals shorter)

---

## File Structure

```
french-daily/
├── flashcards.py          # Original version (unchanged)
├── flashcards_v2.py       # Enhanced version (NEW)
├── flashcards.csv         # Your vocabulary files
├── verbs.csv
├── weather.csv
├── ... (other CSV files)
├── missed.csv             # Auto-generated missed cards
└── .flashcard_data/       # Auto-generated data directory
    ├── card_stats.json    # SRS data for each card
    └── progress.json      # Session history and streaks
```

**Note**: The `.flashcard_data/` directory is created automatically. You can delete it to reset all progress.

---

## Migration Guide

### From Original to Enhanced Version

**Good News**: No migration needed! Your CSV files work as-is.

**Recommendations**:

1. **Start without SRS** to get familiar with new features:
   ```bash
   python flashcards_v2.py flashcards.csv english --mode=medium
   ```

2. **Add gender column** to your CSVs (optional but recommended):
   ```bash
   # Edit your CSV from:
   chat,cat

   # To:
   chat,cat,m
   ```

3. **Enable SRS** once you're comfortable:
   ```bash
   python flashcards_v2.py flashcards.csv english --srs --gender
   ```

4. **Start tracking progress** to build daily habit:
   - Run daily with `--srs` flag
   - Check `--stats` to see your streak

---

## Tips for Effective Learning

### 1. **Combine Modes**
- Use `easy` mode when first learning new vocabulary
- Graduate to `medium` mode for regular practice
- Use `hard` or `expert` mode before exams or for fluency

### 2. **Daily Practice with SRS**
```bash
# Run this daily for best results
python flashcards_v2.py flashcards.csv english --srs --gender
```
- Only shows cards due for review (won't overwhelm you)
- Builds streak counter (motivating!)
- Optimal spacing for retention

### 3. **Focus on Weak Areas**
- Review `missed.csv` after each session
- Create a new CSV with just difficult words:
  ```bash
  cp missed.csv difficult_words.csv
  python flashcards_v2.py difficult_words.csv english --mode=hard
  ```

### 4. **Track Gender from the Start**
- Add gender column to all noun CSVs
- Use `--gender` flag in every session
- Gender is one of the hardest parts of French - practice it early!

### 5. **Mix Directions**
- Practice both directions for complete mastery:
  ```bash
  python flashcards_v2.py verbs.csv english  # French → English
  python flashcards_v2.py verbs.csv french   # English → French
  ```

### 6. **Regular Stats Check**
```bash
python flashcards_v2.py flashcards.csv english --stats
```
- Helps identify if accuracy is improving
- Streak counter motivates daily practice

---

## Technical Implementation Details

### Dependencies
No new dependencies! Uses only Python standard library:
- `csv` - CSV file parsing
- `json` - Stats/progress storage
- `difflib` - Fuzzy string matching
- `datetime` - Date tracking for SRS
- `time` - Timing for expert mode

### Data Structures

**CardStats** (per card):
```json
{
  "bonjour|hello": {
    "times_seen": 5,
    "times_correct": 4,
    "last_reviewed": "2025-10-30",
    "interval": 7,
    "ease_factor": 2.4,
    "due_date": "2025-11-06"
  }
}
```

**Progress** (overall):
```json
{
  "streak": 5,
  "last_session": "2025-10-30",
  "sessions": [
    {
      "date": "2025-10-30",
      "cards": 20,
      "correct": 18,
      "accuracy": 90.0
    }
  ]
}
```

### Fuzzy Matching Algorithm
Uses `difflib.SequenceMatcher`:
- Calculates similarity ratio (0.0 to 1.0)
- Threshold: 85% similarity = correct
- Example: "library" vs "librairy" = 93.3% similar (accepted)

---

## Troubleshooting

### "No cards due for review today"
- This is normal with SRS! It means you've reviewed everything recently
- Check when next cards are due: look at `.flashcard_data/card_stats.json`
- Or practice without SRS: remove `--srs` flag

### Streak Reset to 1
- You missed a day
- Streak counts consecutive days
- Just start again - consistency matters more than streak length!

### Want to Reset Progress
```bash
rm -rf .flashcard_data/
```
This deletes all SRS data and progress. Fresh start!

### Accuracy Seems Low
- Normal when starting out
- Try easier mode: `--mode=easy`
- Focus on smaller vocabulary sets
- Use SRS to focus on weak cards

---

## Future Enhancement Ideas

Ideas not yet implemented (you could add these!):

1. **Audio Mode**: Use text-to-speech for listening practice
2. **Cloze Deletion**: Fill-in-the-blank sentences
3. **Conjugation Integration**: Combine with `conjugations.py`
4. **Web Interface**: Flask/FastAPI web app version
5. **Mobile App**: Mobile-friendly version
6. **Shared Decks**: Export/import to share with friends
7. **Charts**: Visualize progress over time with graphs

---

## Summary

### Key Improvements

| Feature | Benefit | Usage |
|---------|---------|-------|
| SRS | Remember more with less study time | `--srs` |
| Typing Mode | Active recall (vs passive) | Default behavior |
| Progress Tracking | See improvement, build streaks | `--stats` |
| Gender Practice | Master masculine/feminine | `--gender` |
| Difficulty Modes | Adapt to your level | `--mode=easy/medium/hard/expert` |

### Recommended Daily Workflow

```bash
# Check progress
python flashcards_v2.py flashcards.csv english --stats

# Daily practice (5-10 minutes)
python flashcards_v2.py flashcards.csv english --srs --gender

# Review missed cards if needed
python flashcards_v2.py missed.csv english --mode=hard
```

### Quick Reference

```bash
# Basic usage
python flashcards_v2.py <csv_file> <direction>

# With all features
python flashcards_v2.py <csv_file> <direction> --srs --gender --mode=medium

# View progress
python flashcards_v2.py <csv_file> <direction> --stats
```

---

**Happy Learning! 🎓🇫🇷**

For questions or issues, check the code comments in `flashcards_v2.py` or modify the script to suit your needs.
