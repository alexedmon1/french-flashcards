#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
French Conjugation Trainer with SRS support

Practice French verb conjugations across 5 tenses:
- Présent (present)
- Futur simple (future)
- Imparfait (imparfait)
- Passé composé (past)
- Conditionnel présent (conditional)

Supports 93 verbs organized by tier (core, intermediate, advanced)
and type (regular -ER, regular -IR, irregular).
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

# Import from the conjugation engine
from conjugation_engine import (
    conjugate,
    get_all_verbs,
    get_verbs_by_type,
    get_verbs_by_tier,
    get_translation,
    get_tense_display_name,
    get_all_tenses,
    get_random_pronouns,
)

# ----------------------------------------------------------------------
# SRS Configuration
# ----------------------------------------------------------------------
DATA_DIR = Path(".conjugation_data")
STATS_FILE = DATA_DIR / "conjugation_stats.json"
PROGRESS_FILE = DATA_DIR / "conjugation_progress.json"

# Tense code to display name mapping
TENSE_NAMES = {
    "present": "présent",
    "future": "futur simple",
    "imparfait": "imparfait",
    "past": "passé composé",
    "conditional": "conditionnel présent",
}

# Valid tenses for --tense flag (short codes)
VALID_TENSE_FLAGS = ["present", "future", "past", "imparfait", "conditional"]


# ----------------------------------------------------------------------
# SRS Data Classes
# ----------------------------------------------------------------------
class ConjugationStats(SRSStats):
    """SRS stats for a verb-tense combination. Inherits all behavior from SRSStats."""
    pass


# ----------------------------------------------------------------------
# SRS Storage Functions
# ----------------------------------------------------------------------
def load_stats() -> dict[str, ConjugationStats]:
    """Load conjugation statistics from JSON file"""
    return _load_srs_stats(STATS_FILE, ConjugationStats)


def save_stats(stats: dict[str, ConjugationStats]):
    """Save conjugation statistics to JSON file"""
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
# SRS Helper Functions
# ----------------------------------------------------------------------
def get_due_combinations(verb_list: list[str], stats: dict[str, ConjugationStats],
                         filter_tense: str = None,
                         filter_tenses: list[str] = None) -> list[tuple[str, str]]:
    """
    Get list of (verb, tense) combinations that are due for review today.
    If no stats exist for a combination, it's considered due.

    Args:
        verb_list: List of verbs to check
        stats: Dictionary of conjugation statistics
        filter_tense: Optional single tense filter (legacy support)
        filter_tenses: Optional list of tenses to check
    """
    today = date.today().isoformat()
    due_combinations = []

    # Determine which tenses to check
    if filter_tense:
        tenses_to_check = [filter_tense]
    elif filter_tenses:
        tenses_to_check = filter_tenses
    else:
        tenses_to_check = get_all_tenses()

    for verb in verb_list:
        for tense in tenses_to_check:
            key = f"{verb}|{tense}"

            # If no stats, it's new and should be reviewed
            if key not in stats:
                due_combinations.append((verb, tense))
            else:
                stat = stats[key]
                # Check if due date is today or earlier
                if stat.due_date <= today:
                    due_combinations.append((verb, tense))

    return due_combinations


def calculate_quality_from_score(score: int, total: int) -> int:
    """
    Convert a score out of 6 to a quality rating (0-3) for SRS.
    6/6: Easy (3)
    5/6: Good (2)
    3-4/6: Hard (1)
    0-2/6: Wrong (0)
    """
    if score == total:
        return 3  # Easy
    elif score >= total - 1:
        return 2  # Good
    elif score >= total // 2:
        return 1  # Hard
    else:
        return 0  # Wrong


def ask_quality_rating(score: int, total: int) -> int:
    """
    Ask user for quality rating or auto-calculate from score.
    Returns quality (0=wrong, 1=hard, 2=good, 3=easy)
    """
    suggested = calculate_quality_from_score(score, total)
    quality_names = {0: "Wrong", 1: "Hard", 2: "Good", 3: "Easy"}

    print(f"\nSRS Quality Rating (suggested: {quality_names[suggested]})")
    print("  0 - Wrong (review soon)")
    print("  1 - Hard (review in 1 day)")
    print("  2 - Good (review in 3 days)")
    print("  3 - Easy (review in 1 week)")

    while True:
        choice = input(f"Rate this verb [0-3] or press Enter for {suggested}: ").strip()

        if choice == "":
            return suggested
        elif choice in "0123":
            return int(choice)
        else:
            print("Please enter 0, 1, 2, 3, or press Enter")


def show_stats_summary(stats: dict[str, ConjugationStats], verb_list: list[str] = None):
    """Display statistics summary"""
    if not stats:
        print("\nNo statistics yet. Start practicing to build your SRS data!")
        return

    total_combinations = len(stats)
    today = date.today().isoformat()

    # Count due items
    due_count = sum(1 for s in stats.values() if s.due_date <= today)

    # Calculate overall accuracy
    total_seen = sum(s.times_seen for s in stats.values())
    total_correct = sum(s.times_correct for s in stats.values())
    accuracy = (total_correct / total_seen * 100) if total_seen > 0 else 0

    print("\n=== Conjugation Practice Statistics ===")
    print(f"Total verb-tense combinations practiced: {total_combinations}")
    print(f"Due for review today: {due_count}")
    print(f"Total reviews: {total_seen}")
    print(f"Overall accuracy: {accuracy:.1f}%")

    # Count by tense
    tense_counts = {}
    for s in stats.values():
        tense = s.key.split('|')[1]
        if tense not in tense_counts:
            tense_counts[tense] = 0
        tense_counts[tense] += 1

    if tense_counts:
        print("\nCombinations by tense:")
        for tense, count in sorted(tense_counts.items()):
            display_name = TENSE_NAMES.get(tense, tense)
            print(f"  {display_name}: {count}")

    # Show most difficult verbs
    difficult = sorted(stats.values(),
                      key=lambda s: s.times_correct / s.times_seen if s.times_seen > 0 else 0)[:5]

    if difficult and difficult[0].times_seen > 0:
        print("\nMost challenging verb-tense combinations:")
        for s in difficult:
            if s.times_seen == 0:
                continue
            verb_tense = s.key.split('|')
            tense_name = TENSE_NAMES.get(verb_tense[1], verb_tense[1])
            acc = s.times_correct / s.times_seen * 100
            print(f"  {verb_tense[0]} ({tense_name}): {acc:.0f}% ({s.times_correct}/{s.times_seen})")



# ----------------------------------------------------------------------
# User Input Helpers (normalize_input imported from srs_core)
# ----------------------------------------------------------------------
def choose_tense() -> str:
    """Let user choose a tense to practice."""
    print("\nQuel temps voulez-vous réviser ?")
    print("  1 – Présent")
    print("  2 – Passé composé")
    print("  3 – Futur simple")
    print("  4 – Imparfait")
    print("  5 – Conditionnel présent")
    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        tense_map = {
            "1": "present",
            "2": "past",
            "3": "future",
            "4": "imparfait",
            "5": "conditional",
        }
        if c in tense_map:
            return tense_map[c]
        print("Choisissez un numéro de 1 à 5.")


def choose_verb_type(tier_filter: str = None) -> list:
    """
    Choose which type of verbs to practice. Returns a list of verbs.

    Args:
        tier_filter: If specified, only include verbs of this tier
    """
    # Get verb counts
    all_verbs = get_all_verbs()
    regular_er = get_verbs_by_type("regular_er")
    regular_ir = get_verbs_by_type("regular_ir")
    irregular = get_verbs_by_type("irregular")

    # Apply tier filter if specified
    if tier_filter:
        tier_verbs = set(get_verbs_by_tier(tier_filter))
        all_verbs = [v for v in all_verbs if v in tier_verbs]
        regular_er = [v for v in regular_er if v in tier_verbs]
        regular_ir = [v for v in regular_ir if v in tier_verbs]
        irregular = [v for v in irregular if v in tier_verbs]

    print("\nQuel type de verbes voulez-vous réviser ?")
    print(f"  1 – Regular -ER verbs ({len(regular_er)} verbs)")
    print(f"  2 – Regular -IR verbs ({len(regular_ir)} verbs)")
    print(f"  3 – Irregular verbs ({len(irregular)} verbs)")
    print(f"  4 – All verbs ({len(all_verbs)} verbs)")

    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        if c == "1":
            return regular_er
        elif c == "2":
            return regular_ir
        elif c == "3":
            return irregular
        elif c == "4":
            return all_verbs
        print("Choisissez 1, 2, 3 ou 4.")


def choose_tier() -> str:
    """Let user choose a tier filter."""
    # Get tier counts
    core = get_verbs_by_tier("core")
    intermediate = get_verbs_by_tier("intermediate")
    advanced = get_verbs_by_tier("advanced")
    all_verbs = get_all_verbs()

    print("\nQuel niveau de verbes voulez-vous réviser ?")
    print(f"  1 – Core verbs ({len(core)} most essential verbs)")
    print(f"  2 – Intermediate verbs ({len(intermediate)} common verbs)")
    print(f"  3 – Advanced verbs ({len(advanced)} less common verbs)")
    print(f"  4 – All verbs ({len(all_verbs)} verbs)")

    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        if c == "1":
            return "core"
        elif c == "2":
            return "intermediate"
        elif c == "3":
            return "advanced"
        elif c == "4":
            return None  # No filter
        print("Choisissez 1, 2, 3 ou 4.")


# ----------------------------------------------------------------------
# Main Practice Functions
# ----------------------------------------------------------------------
def ask_one_verb(infinitive: str, tense: str) -> tuple[int, int, list]:
    """
    Practice a single verb conjugation.

    Returns (correct_count, total_count, missed_list)
    missed_list contains (pronoun, user_answer, correct_answer) tuples
    """
    # Get random pronoun variations
    selected_pronouns = get_random_pronouns()

    # Get the conjugation
    pronouns, correct_forms = conjugate(infinitive, tense, selected_pronouns)

    # Get translation
    translation = get_translation(infinitive)
    tense_name = get_tense_display_name(tense)

    print(f"\nConjuguez le verbe « {infinitive} » ({translation}) au {tense_name}:")

    answers = []
    for p in pronouns:
        ans = input(f"{p} ... ").strip()
        ans = normalize_input(ans)
        answers.append(ans)

    score = 0
    missed = []
    for i, (user_ans, correct_ans) in enumerate(zip(answers, correct_forms)):
        if user_ans.lower() == correct_ans.lower():
            print(f"  {pronouns[i]} {user_ans}")
            score += 1
        else:
            print(f"  {pronouns[i]} {user_ans} -> correct: {correct_ans}")
            missed.append((pronouns[i], user_ans, correct_ans))

    print(f"Score pour ce verbe ({tense_name}) : {score}/6")
    return score, 6, missed


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="French Conjugation Trainer with SRS support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tenses available:
  - present: Présent
  - future: Futur simple
  - imparfait: Imparfait
  - past: Passé composé
  - conditional: Conditionnel présent

Verb tiers:
  - core: Most essential verbs (~20 verbs)
  - intermediate: Common verbs (~35 verbs)
  - advanced: Less common verbs (~40 verbs)

Examples:
  python3 conjugations.py                           # Normal practice mode
  python3 conjugations.py --srs                     # SRS mode (only review due verbs)
  python3 conjugations.py --srs --tense=present     # SRS mode for present tense only
  python3 conjugations.py --srs --tense=conditional # SRS mode for conditional only
  python3 conjugations.py --tier=core               # Practice only core verbs
  python3 conjugations.py --tier=core --srs         # SRS mode for core verbs only
  python3 conjugations.py --stats                   # Show statistics and exit
        """
    )
    parser.add_argument("--srs", action="store_true",
                       help="Enable Spaced Repetition System (only practice due verbs)")
    parser.add_argument("--tense", type=str, choices=VALID_TENSE_FLAGS,
                       help="Filter by specific tense (only works with --srs)")
    parser.add_argument("--tier", type=str, choices=["core", "intermediate", "advanced"],
                       help="Filter by verb tier (core=most essential, intermediate=common, advanced=less common)")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics summary and exit")

    args = parser.parse_args()

    # Validate arguments
    if args.tense and not args.srs:
        print("Warning: --tense option only works with --srs mode. It will be ignored.")
        print("Use: python3 conjugations.py --srs --tense=present\n")

    # Load SRS data
    stats = load_stats() if args.srs or args.stats else {}

    # Handle --stats flag
    if args.stats:
        show_stats_summary(stats)
        return

    total_ok = 0
    total_q = 0
    all_misses = []  # (infinitive, tense, missed_list)

    # Build title with active tenses
    tense_str = "5 tenses" if not args.tense else TENSE_NAMES.get(args.tense, args.tense)
    print(f"=== Test de conjugaison française ({tense_str}) ===")

    if args.srs:
        if args.tense:
            tense_name = TENSE_NAMES.get(args.tense, args.tense)
            print(f"Mode SRS: Practice {tense_name} verbs due for review today")
        else:
            print("Mode SRS: Practice verbs due for review today")

    if args.tier:
        tier_names = {"core": "essentiels", "intermediate": "intermédiaires", "advanced": "avancés"}
        print(f"Filtré par niveau: verbes {tier_names.get(args.tier, args.tier)}")

    print("Tapez 'q' à tout moment pour quitter.\n")

    # Choose tier interactively if not specified
    tier_filter = args.tier
    if not tier_filter and not args.srs:
        tier_filter = choose_tier()

    # Choose verb type
    verb_list = choose_verb_type(tier_filter)

    if not verb_list:
        print("Aucun verbe disponible avec ces filtres.")
        return

    # If SRS mode, get due combinations
    if args.srs:
        due_combinations = get_due_combinations(verb_list, stats, args.tense)
        if not due_combinations:
            print("\nAucun verbe à réviser aujourd'hui ! Excellent travail !")
            print("Revenez demain pour plus de pratique, ou lancez sans --srs pour pratiquer n'importe quel verbe.")
            return

        print(f"\n{len(due_combinations)} combinaisons verbe-temps à réviser aujourd'hui")
        print("Appuyez sur Entrée pour continuer...")
        input()

    while True:
        # Select verb and tense
        if args.srs:
            if not due_combinations:
                print("\nTous les verbes du jour sont terminés !")
                break

            # Pick a random due combination
            infinitive, tense = random.choice(due_combinations)
        else:
            # Normal mode: pick random verb and ask for tense
            tense = choose_tense()
            infinitive = random.choice(verb_list)

        try:
            ok, qty, missed = ask_one_verb(infinitive, tense)
        except (KeyboardInterrupt, EOFError):
            print("\nInterruption détectée – au revoir !")
            break

        total_ok += ok
        total_q += qty
        if missed:
            all_misses.append((infinitive, tense, missed))

        # SRS: Ask for quality rating and update stats
        if args.srs:
            quality = ask_quality_rating(ok, qty)

            # Update or create stats for this verb-tense combination
            key = f"{infinitive}|{tense}"
            if key not in stats:
                stats[key] = ConjugationStats(key)

            stats[key].update(quality)
            save_stats(stats)

            # Remove from due list if quality > 0 (will be reviewed later)
            if quality > 0:
                due_combinations.remove((infinitive, tense))

            # Show remaining count
            if due_combinations:
                print(f"\n{len(due_combinations)} combinaisons verbe-temps restantes aujourd'hui")

        nxt = input("\nUn autre verbe ? (Entrée=oui, q=quitter) ").strip().lower()
        if nxt == "q":
            break

    if total_q:
        pct = (total_ok / total_q) * 100
        print("\n--- Résultat final ---")
        print(f"Points obtenus : {total_ok}/{total_q}")
        print(f"Taux de réussite : {pct:.1f}%")

        # Show missed conjugations for review
        if all_misses:
            print("\n--- Erreurs à revoir ---")
            for infinitive, tense, missed in all_misses:
                tense_name = get_tense_display_name(tense)
                print(f"  {infinitive} ({tense_name}) :")
                for pronoun, user_ans, correct_ans in missed:
                    print(f"    {pronoun} {correct_ans}  (vous : {user_ans})")
    else:
        print("\nAucun point enregistré.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Erreur inattendue : {exc}", file=sys.stderr)
        sys.exit(1)
