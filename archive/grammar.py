#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
French Grammar Trainer with SRS support

Practice French grammar topics with fill-in-the-blank exercises.
Topics are auto-discovered from JSON files in grammar_data/.

Currently available:
- Pronoms relatifs (qui, que, où, dont, lequel, ce qui, ce que)
"""

import argparse
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from srs_core import SRSStats, normalize_input
from srs_core import load_stats as _load_srs_stats
from srs_core import save_stats as _save_srs_stats


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
GRAMMAR_DATA_DIR = Path("grammar_data")
SRS_DATA_DIR = Path(".grammar_data")
STATS_FILE = SRS_DATA_DIR / "grammar_stats.json"
PROGRESS_FILE = SRS_DATA_DIR / "grammar_progress.json"


# ----------------------------------------------------------------------
# Exercise Loading
# ----------------------------------------------------------------------
def discover_topics() -> dict[str, Path]:
    """Discover available grammar topics from JSON files in grammar_data/."""
    topics = {}
    if not GRAMMAR_DATA_DIR.exists():
        return topics
    for f in sorted(GRAMMAR_DATA_DIR.glob("*.json")):
        topics[f.stem] = f
    return topics


def load_topic(path: Path) -> dict:
    """Load a grammar topic from a JSON file."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_exercises(topic_data: dict, level: int = None) -> list[dict]:
    """Get exercises from topic data, optionally filtered by level."""
    exercises = topic_data.get("exercises", [])
    if level is not None:
        exercises = [e for e in exercises if e["level"] == level]
    return exercises


# ----------------------------------------------------------------------
# SRS Data Classes
# ----------------------------------------------------------------------
class GrammarStats(SRSStats):
    """SRS stats for a grammar exercise. Inherits all behavior from SRSStats."""
    pass


# ----------------------------------------------------------------------
# SRS Storage Functions
# ----------------------------------------------------------------------
def load_stats() -> dict[str, GrammarStats]:
    """Load grammar statistics from JSON file."""
    return _load_srs_stats(STATS_FILE, GrammarStats)


def save_stats(stats: dict[str, GrammarStats]):
    """Save grammar statistics to JSON file."""
    _save_srs_stats(stats, STATS_FILE)


def load_progress() -> dict:
    """Load progress history."""
    if not PROGRESS_FILE.exists():
        return {"sessions": [], "streak": 0, "last_session": None}
    with PROGRESS_FILE.open() as f:
        return json.load(f)


def save_progress(progress: dict):
    """Save progress history."""
    SRS_DATA_DIR.mkdir(exist_ok=True)
    with PROGRESS_FILE.open("w") as f:
        json.dump(progress, f, indent=2)


# ----------------------------------------------------------------------
# SRS Helper Functions
# ----------------------------------------------------------------------
def get_due_exercises(
    exercises: list[dict], topic_name: str, stats: dict[str, GrammarStats]
) -> list[dict]:
    """Get exercises that are due for review today."""
    today = date.today().isoformat()
    due = []
    for ex in exercises:
        key = f"{topic_name}|{ex['id']}"
        if key not in stats:
            due.append(ex)
        elif stats[key].due_date <= today:
            due.append(ex)
    return due


def ask_quality_rating(correct: bool) -> int:
    """
    Ask user for SRS quality rating.
    Returns quality (0=wrong, 1=hard, 2=good, 3=easy).
    """
    suggested = 3 if correct else 0
    quality_names = {0: "Wrong", 1: "Hard", 2: "Good", 3: "Easy"}

    print(f"\nSRS Quality Rating (suggested: {quality_names[suggested]})")
    print("  0 - Wrong (review soon)")
    print("  1 - Hard (review in 1 day)")
    print("  2 - Good (review in 3 days)")
    print("  3 - Easy (review in 1 week)")

    while True:
        choice = input(f"Rate [0-3] or Enter for {suggested}: ").strip()
        if choice == "":
            return suggested
        elif choice in "0123":
            return int(choice)
        else:
            print("Please enter 0, 1, 2, 3, or press Enter")


def show_stats_summary(stats: dict[str, GrammarStats]):
    """Display statistics summary."""
    if not stats:
        print("\nNo statistics yet. Start practicing to build your SRS data!")
        return

    today = date.today().isoformat()
    total_exercises = len(stats)
    due_count = sum(1 for s in stats.values() if s.due_date <= today)
    total_seen = sum(s.times_seen for s in stats.values())
    total_correct = sum(s.times_correct for s in stats.values())
    accuracy = (total_correct / total_seen * 100) if total_seen > 0 else 0

    print("\n=== Grammar Practice Statistics ===")
    print(f"Total exercises practiced: {total_exercises}")
    print(f"Due for review today: {due_count}")
    print(f"Total reviews: {total_seen}")
    print(f"Overall accuracy: {accuracy:.1f}%")

    # Count by topic
    topic_counts = {}
    for s in stats.values():
        topic = s.key.split("|")[0]
        if topic not in topic_counts:
            topic_counts[topic] = {"total": 0, "due": 0}
        topic_counts[topic]["total"] += 1
        if s.due_date <= today:
            topic_counts[topic]["due"] += 1

    if topic_counts:
        print("\nExercises by topic:")
        for topic, counts in sorted(topic_counts.items()):
            display = topic.replace("_", " ").title()
            print(f"  {display}: {counts['total']} practiced, {counts['due']} due")

    # Show most difficult exercises
    difficult = sorted(
        stats.values(),
        key=lambda s: s.times_correct / s.times_seen if s.times_seen > 0 else 0,
    )[:5]

    if difficult and difficult[0].times_seen > 0:
        print("\nMost challenging exercises:")
        for s in difficult:
            if s.times_seen == 0:
                continue
            acc = s.times_correct / s.times_seen * 100
            print(f"  {s.key}: {acc:.0f}% ({s.times_correct}/{s.times_seen})")



# ----------------------------------------------------------------------
# User Input Helpers (normalize_input imported from srs_core)
# ----------------------------------------------------------------------
def check_answer(user_input: str, exercise: dict) -> bool:
    """Check if the user's answer matches the expected answer or alternatives."""
    answer = exercise["answer"]
    alternatives = exercise.get("alternatives", [])

    # Build list of all accepted answers
    accepted = [answer.lower()] + [alt.lower() for alt in alternatives]

    return user_input.lower() in accepted


def format_sentence(exercise: dict, fill: str = "___") -> str:
    """Format the exercise sentence with the blank."""
    before = exercise["sentence_before"]
    after = exercise["sentence_after"]

    if before and after:
        return f"{before} {fill} {after}"
    elif before:
        return f"{before} {fill}"
    else:
        return f"{fill} {after}"


# ----------------------------------------------------------------------
# Interactive Menus
# ----------------------------------------------------------------------
def choose_topic(topics: dict[str, Path]) -> tuple[str, dict]:
    """Let user choose a grammar topic. Returns (topic_name, topic_data)."""
    topic_list = list(topics.items())

    if len(topic_list) == 1:
        name, path = topic_list[0]
        data = load_topic(path)
        print(f"\nTopic: {data.get('topic', name)}")
        print(f"  {data.get('description', '')}")
        return name, data

    print("\nQuel sujet voulez-vous réviser ?")
    for i, (name, path) in enumerate(topic_list, 1):
        data = load_topic(path)
        display = data.get("topic", name.replace("_", " ").title())
        desc = data.get("description", "")
        print(f"  {i} – {display}")
        if desc:
            print(f"      {desc}")

    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        try:
            idx = int(c) - 1
            if 0 <= idx < len(topic_list):
                name, path = topic_list[idx]
                return name, load_topic(path)
        except ValueError:
            pass
        print(f"Choisissez un numéro de 1 à {len(topic_list)}.")


def choose_level(topic_data: dict) -> int | None:
    """Let user choose a difficulty level. Returns level number or None for all."""
    levels = topic_data.get("levels", {})
    if not levels:
        return None

    # Count exercises per level
    exercises = topic_data.get("exercises", [])
    level_counts = {}
    for ex in exercises:
        lvl = ex["level"]
        level_counts[lvl] = level_counts.get(lvl, 0) + 1

    print("\nQuel niveau voulez-vous réviser ?")
    sorted_levels = sorted(levels.items(), key=lambda x: int(x[0]))
    for key, desc in sorted_levels:
        count = level_counts.get(int(key), 0)
        print(f"  {key} – {desc} ({count} exercises)")
    all_count = len(exercises)
    print(f"  {len(sorted_levels) + 1} – All levels ({all_count} exercises)")

    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        try:
            val = int(c)
            if val == len(sorted_levels) + 1:
                return None  # All levels
            if str(val) in levels:
                return val
        except ValueError:
            pass
        print(f"Choisissez un numéro de 1 à {len(sorted_levels) + 1}.")


# ----------------------------------------------------------------------
# Main Practice Functions
# ----------------------------------------------------------------------
def ask_one_exercise(exercise: dict, exercise_num: int = None, total: int = None) -> bool:
    """
    Present a single fill-in-the-blank exercise.
    Returns True if answered correctly, False otherwise.
    """
    # Display header
    if exercise_num is not None and total is not None:
        print(f"\n--- Exercise {exercise_num}/{total} ---")
    else:
        print("\n---")

    # Display sentence with blank
    sentence = format_sentence(exercise, "__________")
    print(f"Complétez : {sentence}")

    # Show context if provided (essential information for answering)
    if exercise.get("context"):
        print(f"  ({exercise['context']})")

    # Get user input
    while True:
        user_input = input("\nVotre réponse (h=indice, q=quitter) : ").strip()
        user_input = normalize_input(user_input)

        if user_input.lower() == "q":
            raise KeyboardInterrupt

        if user_input.lower() == "h":
            print(f"  Indice : {exercise['hint']}")
            continue

        if not user_input:
            print("  Tapez votre réponse, 'h' pour un indice, ou 'q' pour quitter.")
            continue

        break

    # Check answer
    correct = check_answer(user_input, exercise)

    if correct:
        filled = format_sentence(exercise, exercise["answer"])
        print(f"  Correct ! {filled}")
    else:
        filled = format_sentence(exercise, exercise["answer"])
        print(f"  Incorrect. Réponse : {exercise['answer']}")
        print(f"  → {filled}")

    # Show explanation
    print(f"  Explication : {exercise['explanation']}")

    # Show translation if available
    if exercise.get("translation"):
        print(f"  Traduction : {exercise['translation']}")

    return correct


# ----------------------------------------------------------------------
# Session Summary
# ----------------------------------------------------------------------
def show_session_summary(correct: int, total: int, missed: list = None):
    """Display end-of-session summary."""
    if total == 0:
        print("\nAucun exercice complété.")
        return

    pct = (correct / total) * 100
    print("\n--- Résultat final ---")
    print(f"Score : {correct}/{total}")
    print(f"Taux de réussite : {pct:.1f}%")

    if pct == 100:
        print("Parfait !")
    elif pct >= 80:
        print("Très bien !")
    elif pct >= 60:
        print("Pas mal ! Continuez à pratiquer.")
    else:
        print("Continuez à pratiquer, vous allez vous améliorer !")

    # Show missed exercises for review
    if missed:
        print("\n--- Erreurs à revoir ---")
        for ex in missed:
            filled = format_sentence(ex, ex["answer"])
            print(f"  {filled}")
            if ex.get("explanation"):
                print(f"    -> {ex['explanation']}")


def update_progress(correct: int, total: int):
    """Update progress history after a session."""
    progress = load_progress()

    today = date.today().isoformat()
    session = {
        "date": today,
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total * 100, 1) if total > 0 else 0,
    }
    progress["sessions"].append(session)

    # Update streak
    if progress["last_session"] == today:
        pass  # Already practiced today
    elif progress["last_session"] == (date.today() - timedelta(days=1)).isoformat():
        progress["streak"] += 1
    else:
        progress["streak"] = 1
    progress["last_session"] = today

    save_progress(progress)


def _build_epilog() -> str:
    """Build dynamic help epilog from discovered topics."""
    lines = ["Topics are auto-discovered from JSON files in grammar_data/.\n"]
    topics = discover_topics()
    if topics:
        lines.append("Currently available:")
        for name, path in topics.items():
            data = load_topic(path)
            lines.append(f"  - {name}: {data.get('description', data.get('topic', name))}")
            levels = data.get("levels", {})
            if levels:
                for num, desc in sorted(levels.items(), key=lambda x: int(x[0])):
                    lines.append(f"      Level {num}: {desc}")
        lines.append("")
    lines.append("Examples:")
    lines.append("  python3 grammar.py                    # Interactive mode")
    lines.append("  python3 grammar.py --level=1          # Practice level 1 only")
    lines.append("  python3 grammar.py --srs              # SRS mode (only review due exercises)")
    lines.append("  python3 grammar.py --srs --level=2    # SRS mode for level 2 only")
    lines.append("  python3 grammar.py --stats            # Show statistics and exit")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="French Grammar Trainer with SRS support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_build_epilog(),
    )
    parser.add_argument(
        "--srs",
        action="store_true",
        help="Enable Spaced Repetition System (only practice due exercises)",
    )
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3],
        help="Filter by difficulty level (1=easiest, 3=hardest)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics summary and exit",
    )

    args = parser.parse_args()

    # Discover available topics
    topics = discover_topics()
    if not topics:
        print("Erreur : aucun fichier de données trouvé dans grammar_data/")
        print("Ajoutez des fichiers JSON dans grammar_data/ pour commencer.")
        sys.exit(1)

    # Load SRS data
    stats = load_stats() if args.srs or args.stats else {}

    # Handle --stats flag
    if args.stats:
        show_stats_summary(stats)
        return

    print("=== Exercices de grammaire française ===")
    if args.srs:
        print("Mode SRS : exercices à réviser aujourd'hui")
    print("Tapez 'h' pour un indice, 'q' pour quitter.\n")

    # Choose topic
    topic_name, topic_data = choose_topic(topics)

    # Choose level
    level = args.level
    if level is None and not args.srs:
        level = choose_level(topic_data)

    # Get exercises
    exercises = get_exercises(topic_data, level)
    if not exercises:
        print("Aucun exercice disponible avec ces filtres.")
        return

    # If SRS mode, filter to due exercises
    if args.srs:
        exercises = get_due_exercises(exercises, topic_name, stats)
        if not exercises:
            print("\nAucun exercice à réviser aujourd'hui ! Excellent travail !")
            print(
                "Revenez demain pour plus de pratique, ou lancez sans --srs pour "
                "pratiquer n'importe quel exercice."
            )
            return
        print(f"\n{len(exercises)} exercices à réviser aujourd'hui")

    # Shuffle exercises
    random.shuffle(exercises)

    total_exercises = len(exercises)
    total_correct = 0
    total_done = 0
    missed_exercises = []

    for i, exercise in enumerate(exercises, 1):
        try:
            correct = ask_one_exercise(exercise, i, total_exercises)
        except (KeyboardInterrupt, EOFError):
            print("\nInterruption détectée – au revoir !")
            break

        total_done += 1
        if correct:
            total_correct += 1
        else:
            missed_exercises.append(exercise)

        # SRS: ask for quality rating and update stats
        if args.srs:
            quality = ask_quality_rating(correct)
            key = f"{topic_name}|{exercise['id']}"
            if key not in stats:
                stats[key] = GrammarStats(key)
            stats[key].update(quality)
            save_stats(stats)

            remaining = total_exercises - i
            if remaining > 0:
                print(f"\n{remaining} exercices restants")

        # Ask to continue (unless it's the last exercise)
        if i < total_exercises:
            try:
                nxt = input("\nSuivant ? (Entrée=oui, q=quitter) ").strip().lower()
                if nxt == "q":
                    break
            except (KeyboardInterrupt, EOFError):
                print("\nInterruption détectée – au revoir !")
                break

    # Session summary
    show_session_summary(total_correct, total_done, missed_exercises)

    # Update progress if any exercises were done
    if total_done > 0:
        update_progress(total_correct, total_done)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Erreur inattendue : {exc}", file=sys.stderr)
        sys.exit(1)
