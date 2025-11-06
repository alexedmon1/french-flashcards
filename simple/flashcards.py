#!/usr/bin/env python3
"""
Simple French‑English flashcard trainer.

* Keep your vocabulary in `flashcards.csv` (comma‑separated, no header):
      french_word,english_translation
  Example:
      bonjour,hello
      chat,cat
      livre,book

* Run the script.  It will load the CSV, shuffle the cards,
  and present each French word.  Press <Enter> to see the answer,
  then type ‘y’ if you remembered it correctly or anything else to
  mark it as missed.

* At the end you get a short report and an optional `missed.csv`
  containing the words you got wrong – handy for focused review.
"""

import csv
import random
import sys
from pathlib import Path
from sys import argv

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
CSV_PATH = Path(argv[1])                    # Your vocab file
MISSED_PATH = Path("missed.csv")            # Where to store missed cards
if argv[2] == 'french':
    LANG_DIRECTION = 'french' #french or english. choice is what you want to guess.
    SHOW_ANSWER_PROMPT = "Appuyez sur 'enter' pour révéler la traduction française..."
    REPEAT_PROMPT = "\nL'avez-vous bien rappelé ? (y/N): "
else:
    LANG_DIRECTION = 'english'
    SHOW_ANSWER_PROMPT = "Press <Enter> to reveal the English translation…"
    REPEAT_PROMPT = "\nDid you recall it correctly? (y/N): "

# ----------------------------------------------------------------------
def load_cards(csv_path: Path) -> list[tuple[str, str]]:
    """
    Read the CSV and return a list of (french, english) tuples.
    Supports multiple translations separated by '|' character.
    """
    if not csv_path.is_file():
        sys.exit(f"❌  Vocabulary file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        cards = [(row[0].strip(), row[1].strip()) for row in reader if len(row) >= 2]

    if not cards:
        sys.exit("⚠️  No valid rows found in the CSV file.")
    return cards


def english_study(cards: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Run the interactive flashcard session and return missed cards."""
    random.shuffle(cards)               # Random order each run
    missed = []

    print("\n=== French Flashcard Trainer ===\n")
    for idx, (fr, en) in enumerate(cards, start=1):
        # Support multiple French variants separated by '|'
        french_variants = [f.strip() for f in fr.split('|')]
        display_french = " / ".join(french_variants) if len(french_variants) > 1 else fr

        # Support multiple English variants separated by '|'
        english_variants = [e.strip() for e in en.split('|')]
        display_english = " / ".join(english_variants) if len(english_variants) > 1 else en

        print(f"{idx}/{len(cards)} – French: {display_french}")
        input(SHOW_ANSWER_PROMPT)       # Wait for user to press Enter
        print(f"   → English: {display_english}")

        correct = input(REPEAT_PROMPT).strip().lower()
        if correct != "y":
            missed.append((fr, en))
        print("-" * 40)

    return missed


def french_study(cards: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Run the interactive flashcard session and return missed cards."""
    random.shuffle(cards)               # Random order each run
    missed = []

    print("\n=== Entraîneur de cartes mémoire en français ===\n")
    for idx, (fr, en) in enumerate(cards, start=1):
        # Support multiple English variants separated by '|'
        english_variants = [e.strip() for e in en.split('|')]
        display_english = " / ".join(english_variants) if len(english_variants) > 1 else en

        # Support multiple French variants separated by '|'
        french_variants = [f.strip() for f in fr.split('|')]
        display_french = " / ".join(french_variants) if len(french_variants) > 1 else fr

        print(f"{idx}/{len(cards)} – L'anglais: {display_english}")
        input(SHOW_ANSWER_PROMPT)       # Wait for user to press Enter
        print(f"   → Le français: {display_french}")

        correct = input(REPEAT_PROMPT).strip().lower()
        if correct != "y":
            missed.append((fr, en))
        print("-" * 40)

    return missed


def save_missed(missed: list[tuple[str, str]], path: Path) -> None:
    """Append missed cards to a CSV for later review."""
    if not missed:
        return

    # Preserve existing missed cards, if any
    existing = []
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as f:
            existing = list(csv.reader(f))

    # Write combined list (old + new) – duplicates are okay; you can clean later
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(existing + missed)


def main() -> None:
    cards = load_cards(CSV_PATH)
    if LANG_DIRECTION == "english":
        missed = english_study(cards)
    else:
        missed = french_study(cards)
    print("\n=== Session Summary ===")
    print(f"Total cards reviewed : {len(cards)}")
    print(f"Correctly recalled   : {len(cards) - len(missed)}")
    print(f"Missed / need review : {len(missed)}")

    if missed:
        save_missed(missed, MISSED_PATH)
        print(f"\n🗂️  Missed cards saved to: {MISSED_PATH}")
        print("You can re‑run the program later and focus on these entries.")
    else:
        # Clean up old missed file if everything was perfect
        if MISSED_PATH.is_file():
            MISSED_PATH.unlink()
            print("\n✅  No misses – previous missed list cleared.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋  Bye! Session interrupted.")
