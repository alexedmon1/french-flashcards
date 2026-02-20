#!/usr/bin/env python3
"""
Enhanced French-English Flashcard Trainer with SRS, Progress Tracking, and Multiple Modes

Features:
- Spaced Repetition System (SRS) for optimal retention
- Multiple difficulty modes (multiple choice, typing, exact match, timed)
- Progress tracking and statistics
- Gender learning support
- Session streaks and improvement metrics
"""

import csv
import json
import random
import sys
import time
from datetime import datetime, date
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

from srs_core import SRSStats, normalize_input
from srs_core import load_stats as _load_srs_stats
from srs_core import save_stats as _save_srs_stats

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
DATA_DIR = Path(".flashcard_data")
STATS_FILE = DATA_DIR / "card_stats.json"
PROGRESS_FILE = DATA_DIR / "progress.json"

# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------
class Card:
    def __init__(self, french: str, english: str, category: Optional[str] = None, gender: Optional[str] = None, synonyms: Optional[list[str]] = None):
        # Support multiple translations separated by '|'
        self.french_variants = [f.strip() for f in french.split('|')]
        self.english_variants = [e.strip() for e in english.split('|')]

        # Keep primary versions for display and key generation
        self.french = self.french_variants[0]
        self.english = self.english_variants[0]

        self.category = category.strip() if category else None
        self.gender = gender.strip().lower() if gender else None
        self.key = f"{self.french}|{self.english}"

        # Store French synonyms (different French words with same English meaning)
        # e.g., ["un slip", "une colette"] both mean "panties"
        self.french_synonyms = synonyms if synonyms else []

    def __repr__(self):
        return f"Card({self.french}, {self.english}, {self.category}, {self.gender})"


class CardStats(SRSStats):
    """SRS stats for a vocabulary card. Inherits all behavior from SRSStats."""
    pass


# ----------------------------------------------------------------------
# Storage Functions
# ----------------------------------------------------------------------
def load_stats() -> dict[str, CardStats]:
    """Load card statistics from JSON file"""
    return _load_srs_stats(STATS_FILE, CardStats)


def save_stats(stats: dict[str, CardStats]):
    """Save card statistics to JSON file"""
    _save_srs_stats(stats, STATS_FILE)


def load_progress() -> dict:
    """Load progress history"""
    if not PROGRESS_FILE.exists():
        return {"sessions": [], "streak": 0, "last_session": None}

    with PROGRESS_FILE.open() as f:
        return json.load(f)


def save_progress(progress: dict):
    """Save progress history"""
    DATA_DIR.mkdir(exist_ok=True)
    with PROGRESS_FILE.open("w") as f:
        json.dump(progress, f, indent=2)


# ----------------------------------------------------------------------
# Card Loading
# ----------------------------------------------------------------------
def load_cards(csv_path: Path, category_filter: Optional[str] = None) -> list[Card]:
    """
    Read the CSV and return a list of Card objects

    Supports multiple formats:
    - 2 columns: french,english
    - 3 columns: french,english,gender OR french,english,category
    - 4 columns: french,english,category,gender

    Automatically detects French synonyms (different French words with same English translation)
    and stores them so any variant is accepted as correct.
    """
    if not csv_path.is_file():
        sys.exit(f"❌  Vocabulary file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        cards = []
        for row in reader:
            if len(row) >= 2:
                french = row[0]
                english = row[1]
                category = None
                gender = None

                if len(row) == 3:
                    # Could be either category or gender
                    # If it's m/f/masculine/feminine, it's gender, otherwise category
                    third_col = row[2].strip().lower()
                    if third_col in ['m', 'f', 'masculine', 'feminine']:
                        gender = third_col
                    else:
                        category = row[2]
                elif len(row) >= 4:
                    # Both category and gender
                    category = row[2]
                    gender = row[3]

                # Filter by category if specified
                if category_filter and category and category.lower() != category_filter.lower():
                    continue

                cards.append(Card(french, english, category, gender))

    if not cards:
        if category_filter:
            sys.exit(f"⚠️  No cards found for category '{category_filter}'")
        else:
            sys.exit("⚠️  No valid rows found in the CSV file.")

    # Detect and group French synonyms (different French words with same English translation)
    # Build a mapping: normalized_english -> list of French words
    english_to_french = {}
    for card in cards:
        # Use all English variants to find matches
        for eng_variant in card.english_variants:
            normalized_eng = eng_variant.lower().strip()
            if normalized_eng not in english_to_french:
                english_to_french[normalized_eng] = []
            # Add all French variants
            for french_variant in card.french_variants:
                if french_variant not in english_to_french[normalized_eng]:
                    english_to_french[normalized_eng].append(french_variant)

    # Now assign synonyms to each card
    for card in cards:
        synonyms = set()
        for eng_variant in card.english_variants:
            normalized_eng = eng_variant.lower().strip()
            # Get all French words that match this English translation
            french_words = english_to_french.get(normalized_eng, [])
            # Add them all as synonyms (excluding the card's own French variants)
            for french_word in french_words:
                if french_word not in card.french_variants:
                    synonyms.add(french_word)

        card.french_synonyms = list(synonyms)

    return cards



# ----------------------------------------------------------------------
# Answer Checking (normalize_input imported from srs_core)
# ----------------------------------------------------------------------
def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate similarity between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def check_answer(user_input: str, correct_variants: list[str], mode: str) -> tuple[bool, float]:
    """
    Check if answer is correct based on mode
    Supports multiple valid answers (checks against all variants)
    Returns (is_correct, similarity_score)
    """
    user = user_input.strip().lower()

    # Check against all valid variants
    best_similarity = 0.0
    is_correct = False

    for correct in correct_variants:
        answer = correct.strip().lower()

        if mode == "exact":
            if user == answer:
                return (True, 1.0)
            best_similarity = max(best_similarity, 1.0 if user == answer else 0.0)
        elif mode == "typing":
            # Allow 85% similarity for typos
            sim = similarity_ratio(user, answer)
            best_similarity = max(best_similarity, sim)
            if sim >= 0.85:
                is_correct = True
        else:
            # Multiple choice - exact match required
            if user == answer:
                return (True, 1.0)
            best_similarity = max(best_similarity, 1.0 if user == answer else 0.0)

    return (is_correct, best_similarity)


# ----------------------------------------------------------------------
# Study Modes
# ----------------------------------------------------------------------
def multiple_choice_question(card: Card, all_cards: list[Card], lang_direction: str) -> bool:
    """Present a multiple choice question. Returns True if correct."""
    # Generate wrong answers
    if lang_direction == "english":
        question = card.french
        correct_answer = card.english
        correct_variants = card.english_variants
        # Exclude all variants of the current card from wrong pool
        wrong_pool = [c.english for c in all_cards if c.french != card.french]
    else:
        question = card.english
        correct_answer = card.french
        # Include French synonyms as valid answers
        correct_variants = card.french_variants + card.french_synonyms
        # Exclude all variants of the current card AND its synonyms from wrong pool
        all_valid_french = set(card.french_variants + card.french_synonyms)
        wrong_pool = [c.french for c in all_cards if c.french not in all_valid_french]

    # Pick 3 random wrong answers
    wrong_answers = random.sample(wrong_pool, min(3, len(wrong_pool)))
    options = [correct_answer] + wrong_answers
    random.shuffle(options)

    # Display question
    print(f"Question: {question}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")

    # Get answer
    while True:
        try:
            choice = input("\nYour answer (1-4): ").strip()
            if choice in "1234":
                idx = int(choice) - 1
                selected = options[idx]
                # Check against all valid variants
                is_correct = selected.lower() in [v.lower() for v in correct_variants]

                if is_correct:
                    print("✅ Correct!")
                else:
                    # Show all valid answers if multiple exist
                    if len(correct_variants) > 1:
                        all_answers = " / ".join(correct_variants)
                        print(f"❌ Wrong. Correct answers: {all_answers}")
                    else:
                        print(f"❌ Wrong. Correct answer: {correct_answer}")

                return is_correct
        except (ValueError, IndexError):
            print("Please enter 1, 2, 3, or 4")


def typing_question(card: Card, lang_direction: str, mode: str, time_limit: Optional[int] = None) -> tuple[bool, float]:
    """
    Present a typing question. Returns (is_correct, quality_score)
    quality_score: 0=wrong, 1=hard, 2=good, 3=easy
    """
    if lang_direction == "english":
        question = card.french
        correct_answer = card.english
        correct_variants = card.english_variants
    else:
        question = card.english
        correct_answer = card.french
        # Include French synonyms as valid answers
        correct_variants = card.french_variants + card.french_synonyms

    print(f"Translate: {question}")

    # Timed mode
    start_time = time.time()
    if time_limit:
        print(f"⏱️  You have {time_limit} seconds!")

    user_input = normalize_input(input("Your answer: "))
    elapsed = time.time() - start_time

    if time_limit and elapsed > time_limit:
        print(f"⏰ Time's up! ({elapsed:.1f}s)")
        # Show all valid answers if multiple exist
        if len(correct_variants) > 1:
            all_answers = " / ".join(correct_variants)
            print(f"Correct answers: {all_answers}")
        else:
            print(f"Correct answer: {correct_answer}")
        return False, 0

    # Check answer against all variants
    is_correct, similarity = check_answer(user_input, correct_variants, mode)

    if is_correct:
        if similarity >= 0.95 and (not time_limit or elapsed < time_limit * 0.5):
            print("✅ Perfect! (Easy)")
            return True, 3
        elif similarity >= 0.95:
            print("✅ Correct! (Good)")
            return True, 2
        else:
            print(f"✅ Close enough! ({similarity*100:.0f}% match) (Hard)")
            return True, 1
    else:
        # Show all valid answers if multiple exist
        if len(correct_variants) > 1:
            all_answers = " / ".join(correct_variants)
            print(f"❌ Wrong. Correct answers: {all_answers}")
        else:
            print(f"❌ Wrong. Correct answer: {correct_answer}")
        if similarity > 0.5:
            print(f"   (You were {similarity*100:.0f}% close)")
        return False, 0


def gender_question(card: Card) -> bool:
    """Quiz on the gender of a noun. Returns True if correct."""
    if not card.gender:
        return True  # Skip if no gender info

    print(f"\nBonus: What's the gender of '{card.french}'?")
    answer = input("(m/f): ").strip().lower()

    if answer in ['m', 'f']:
        is_correct = (answer == card.gender[0])  # First letter of gender
        if is_correct:
            print("✅ Correct gender!")
        else:
            expected = "masculine" if card.gender[0] == 'm' else "feminine"
            print(f"❌ Wrong. '{card.french}' is {expected}")
        return is_correct
    else:
        print("⏭️  Skipped")
        return True


# ----------------------------------------------------------------------
# Study Session
# ----------------------------------------------------------------------
def run_study_session(
    cards: list[Card],
    lang_direction: str,
    mode: str,
    use_srs: bool,
    practice_gender: bool
) -> dict:
    """
    Run a study session and return results
    mode: 'easy', 'medium', 'hard', 'expert'
    """
    stats = load_stats() if use_srs else {}

    # Filter cards due for review (SRS mode)
    if use_srs:
        today = date.today().isoformat()
        due_cards = [c for c in cards if stats.get(c.key, CardStats(c.key)).due_date <= today]

        if not due_cards:
            print("✅ No cards due for review today! Great job!")
            print(f"   Total cards in deck: {len(cards)}")
            return {"total": 0, "correct": 0}

        study_cards = due_cards
        print(f"📚 {len(study_cards)} cards due for review today (out of {len(cards)} total)")
    else:
        study_cards = cards
        random.shuffle(study_cards)

    correct_count = 0
    missed_cards = []

    print(f"\n=== Study Session ({mode.upper()} mode) ===\n")

    for idx, card in enumerate(study_cards, 1):
        print(f"\n[{idx}/{len(study_cards)}]")
        print("-" * 50)

        # Determine question and correct answer for miss tracking
        if lang_direction == "english":
            question_text = card.french
            answer_text = card.english
        else:
            question_text = card.english
            answer_text = card.french

        # Ask question based on mode
        if mode == "easy":
            is_correct = multiple_choice_question(card, cards, lang_direction)
            quality = 2 if is_correct else 0
        elif mode == "expert":
            is_correct, quality = typing_question(card, lang_direction, "exact", time_limit=10)
        elif mode == "hard":
            is_correct, quality = typing_question(card, lang_direction, "exact")
        else:  # medium (default)
            is_correct, quality = typing_question(card, lang_direction, "typing")

        # Gender quiz (optional)
        if practice_gender and card.gender and is_correct:
            gender_question(card)  # Doesn't affect main score

        if is_correct:
            correct_count += 1
        else:
            missed_cards.append((question_text, answer_text))

        # Update SRS
        if use_srs:
            if card.key not in stats:
                stats[card.key] = CardStats(card.key)
            stats[card.key].update(quality)

            # Show next review date for correct answers
            if quality > 0:
                next_review = stats[card.key].due_date
                days = stats[card.key].interval
                if days == 0:
                    print(f"📅 Review again this session")
                elif days == 1:
                    print(f"📅 Review again tomorrow")
                else:
                    print(f"📅 Next review in {days} days ({next_review})")

        print("-" * 50)

    # Save stats
    if use_srs:
        save_stats(stats)

    return {
        "total": len(study_cards),
        "correct": correct_count,
        "missed": missed_cards,
    }


# ----------------------------------------------------------------------
# Progress Tracking
# ----------------------------------------------------------------------
def update_progress(session_result: dict):
    """Update progress tracking with session results"""
    progress = load_progress()

    today = date.today().isoformat()
    accuracy = (session_result["correct"] / session_result["total"] * 100) if session_result["total"] > 0 else 0

    # Update streak
    if progress["last_session"]:
        from datetime import datetime, timedelta
        last = datetime.fromisoformat(progress["last_session"]).date()
        current = date.today()

        if (current - last).days == 1:
            progress["streak"] += 1
        elif (current - last).days > 1:
            progress["streak"] = 1
    else:
        progress["streak"] = 1

    progress["last_session"] = today

    # Add session
    progress["sessions"].append({
        "date": today,
        "cards": session_result["total"],
        "correct": session_result["correct"],
        "accuracy": round(accuracy, 1)
    })

    save_progress(progress)
    return progress


def show_progress_stats():
    """Display progress statistics"""
    progress = load_progress()

    if not progress["sessions"]:
        print("No previous sessions recorded.")
        return

    print("\n=== Your Progress ===")
    print(f"🔥 Current streak: {progress['streak']} day(s)")
    print(f"📊 Total sessions: {len(progress['sessions'])}")

    # Recent sessions
    recent = progress["sessions"][-5:]
    print("\n Recent sessions:")
    for session in recent:
        print(f"   {session['date']}: {session['correct']}/{session['cards']} ({session['accuracy']}%)")

    # Overall stats
    total_cards = sum(s["cards"] for s in progress["sessions"])
    total_correct = sum(s["correct"] for s in progress["sessions"])
    overall_accuracy = (total_correct / total_cards * 100) if total_cards > 0 else 0

    print(f"\n Overall accuracy: {overall_accuracy:.1f}%")
    print()


def list_available_categories(csv_path: Path):
    """List all available categories in the CSV file"""
    if not csv_path.is_file():
        sys.exit(f"❌  Vocabulary file not found: {csv_path}")

    categories = set()
    total_cards = 0

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                # Has category column
                category = row[2].strip()
                # Check if it's not a gender marker
                if category.lower() not in ['m', 'f', 'masculine', 'feminine']:
                    categories.add(category)
                    total_cards += 1

    if not categories:
        print("⚠️  No categories found in this file.")
        print("   This file may not have a category column.")
        return

    print(f"\n📚 Available categories in {csv_path.name}:")
    print(f"   Total cards: {total_cards}\n")

    # Count cards per category
    category_counts = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                category = row[2].strip()
                if category.lower() not in ['m', 'f', 'masculine', 'feminine']:
                    category_counts[category] = category_counts.get(category, 0) + 1

    # Display sorted by name
    for category in sorted(categories):
        count = category_counts.get(category, 0)
        print(f"   • {category:<20} ({count} cards)")

    print(f"\n💡 Use --category=<name> to practice just one category")
    print(f"   Example: --category=verbs")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def prompt_for_direction() -> str:
    """Interactively ask user which direction they want to practice."""
    print("\n🔄 Which direction do you want to practice?")
    print("  1. French → English (see French, recall English)")
    print("  2. English → French (see English, recall French)")

    while True:
        try:
            choice = input("\nSelect (1 or 2): ").strip()
            if choice == "1":
                return "english"
            elif choice == "2":
                return "french"
            else:
                print("Please enter 1 or 2")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Cancelled.")
            sys.exit(0)


def prompt_for_category(csv_path: Path) -> Optional[str]:
    """Interactively ask user which category they want to practice."""
    categories = []

    # Get available categories
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        categories_set = set()
        for row in reader:
            if len(row) >= 3:
                category = row[2].strip()
                if category.lower() not in ['m', 'f', 'masculine', 'feminine']:
                    categories_set.add(category)

    categories = sorted(categories_set)

    if not categories:
        return None  # No categories available

    print("\n📚 Available categories:")
    print("  0. All categories (no filter)")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")

    while True:
        try:
            choice = input("\nSelect a category (or press Enter for all): ").strip()

            if choice == "" or choice == "0":
                return None  # No filter

            idx = int(choice)
            if 1 <= idx <= len(categories):
                return categories[idx - 1]
            else:
                print(f"Please enter a number between 0 and {len(categories)}")
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Cancelled.")
            sys.exit(0)


def show_help():
    """Display help information."""
    print("""
French Flashcard Trainer - Enhanced Learning with SRS
======================================================

USAGE:
    python flashcards.py [csv_file] [options]

DESCRIPTION:
    Interactive flashcard trainer with spaced repetition, multiple difficulty
    modes, progress tracking, and category support.

    By default, runs in interactive mode - prompts you for language direction
    and category selection.

ARGUMENTS:
    csv_file        Optional CSV file path (default: master_vocabulary.csv)

OPTIONS:
    --help          Show this help message and exit
    --stats         Show progress statistics and exit
    --list-categories  Show available categories and exit

    --srs           Enable Spaced Repetition System (reviews cards due today)
    --gender        Practice noun genders (masculine/feminine)
    --mode=<mode>   Difficulty mode (default: medium)
                    - easy   : Multiple choice (4 options)
                    - medium : Type answer with fuzzy matching
                    - hard   : Type answer with exact matching
                    - expert : Timed (10s) with exact matching

    --category=<cat>  Pre-select category (skips interactive prompt)
                      Use --list-categories to see available options

EXAMPLES:
    # Interactive mode (simplest - prompts for everything)
    python flashcards.py

    # Interactive with SRS for daily practice
    python flashcards.py --srs

    # View your progress
    python flashcards.py --stats

    # See available categories
    python flashcards.py --list-categories

    # Non-interactive: pre-select category and options
    python flashcards.py --category=verbs --srs --mode=hard

    # Use different CSV file
    python flashcards.py weather.csv --mode=easy

FEATURES:
    ✓ Spaced Repetition System (SRS) for optimal retention
    ✓ Multiple difficulty modes (easy to expert)
    ✓ Progress tracking with streaks and statistics
    ✓ Category filtering for focused practice
    ✓ Gender practice for masculine/feminine nouns
    ✓ Interactive prompts for easy use

DATA STORAGE:
    .flashcard_data/card_stats.json  - SRS data per card
    .flashcard_data/progress.json    - Session history and streaks

For more information, see IMPROVEMENTS.md
""")


def main():
    # Check for help flag first
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        return

    # Get CSV file path (optional, defaults to master_vocabulary.csv)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        csv_path = Path(sys.argv[1])
    else:
        csv_path = Path("master_vocabulary.csv")

    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        print("\nRun 'python flashcards.py --help' for usage information")
        sys.exit(1)

    # Parse command-line options
    mode = "medium"
    use_srs = False
    practice_gender = False
    show_stats_only = False
    category_filter = None
    list_categories = False

    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1]
        elif arg == "--srs":
            use_srs = True
        elif arg == "--gender":
            practice_gender = True
        elif arg == "--stats":
            show_stats_only = True
        elif arg.startswith("--category="):
            category_filter = arg.split("=")[1]
        elif arg == "--list-categories":
            list_categories = True

    # List categories and exit
    if list_categories:
        list_available_categories(csv_path)
        return

    # Show stats and exit
    if show_stats_only:
        show_progress_stats()
        return

    # Validate mode
    if mode not in ["easy", "medium", "hard", "expert"]:
        print(f"❌ Invalid mode: {mode}")
        print("   Choose: easy, medium, hard, or expert")
        sys.exit(1)

    print(f"\n=== French Flashcard Trainer ===")
    print(f"📁 Using: {csv_path}")

    # Interactive prompts
    lang_direction = prompt_for_direction()

    # Prompt for category only if not specified via command line
    if category_filter is None:
        category_filter = prompt_for_category(csv_path)

    # Show progress stats
    show_progress_stats()

    # Load cards
    cards = load_cards(csv_path, category_filter)
    if category_filter:
        print(f"📚 Loaded {len(cards)} cards from {csv_path} (category: {category_filter})")
    else:
        print(f"📚 Loaded {len(cards)} cards from {csv_path}")

    # Run session
    result = run_study_session(cards, lang_direction, mode, use_srs, practice_gender)

    # Summary
    print("\n" + "=" * 50)
    print("=== Session Summary ===")
    print(f"Total cards reviewed : {result['total']}")
    print(f"Correctly answered   : {result['correct']}")
    missed_count = result['total'] - result['correct']
    print(f"Missed / need review : {missed_count}")

    if result['total'] > 0:
        accuracy = (result['correct'] / result['total']) * 100
        print(f"Accuracy             : {accuracy:.1f}%")

    # Show missed cards for review
    if result.get('missed'):
        print("\n--- Missed Cards ---")
        for question, answer in result['missed']:
            print(f"  {question}  ->  {answer}")

    # Update progress
    if result['total'] > 0:
        progress = update_progress(result)
        print(f"\n🔥 Current streak    : {progress['streak']} day(s)")

    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bye! Session interrupted.")
