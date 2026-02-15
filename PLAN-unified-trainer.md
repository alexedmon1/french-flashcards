# Plan: Unified French Trainer

## Goal
Combine vocabulary flashcards, verb conjugations, and grammar exercises into a single program with a more engaging interface.

## Part 1: Unified Entry Point

Create a single `trainer.py` that:
- Presents a main menu to select activity type
- Shows SRS stats at a glance (cards due per category)
- Offers a **combined daily review** mode that mixes vocab, conjugation, and grammar cards into one SRS session based on what's due
- Preserves all existing CLI flags for power-user access (e.g. `--srs`, `--tense=present`, `--category=verbs`)
- Reuses existing logic from `flashcards.py`, `conjugations.py`, and `grammar.py`

## Part 2: UI Upgrade Options

### Option A: Textual TUI (Recommended starting point)
- **Library**: [Textual](https://textual.textualize.io/) (Python)
- **Pros**: Runs in terminal, rich UI (panels, tabs, progress bars, colors, keyboard nav), reuses all existing Python logic directly, no browser needed
- **Cons**: Still terminal-based, no mobile access
- **Effort**: Low-medium

### Option B: Flask Web App
- **Stack**: Flask/FastAPI backend + simple HTML/CSS/JS frontend
- **Pros**: Opens in browser, works on phone over local network, nice styling and animations, clickable buttons
- **Cons**: More code to write, need basic frontend work
- **Effort**: Medium

### Option C: Streamlit
- **Library**: [Streamlit](https://streamlit.io/)
- **Pros**: Almost zero frontend code, quick to prototype, web-based
- **Cons**: Feels "dashboardy", less control over UX, reruns script on interaction
- **Effort**: Low

### Option D: Progressive Web App
- **Stack**: Full web app with offline support, installable on phone
- **Pros**: Most engaging for daily use, practice anywhere, push notification reminders possible
- **Cons**: Significant frontend effort, would need to port or API-ify Python logic
- **Effort**: High

## Suggested Approach

1. **Phase 1**: Build unified `trainer.py` with combined SRS and menu system (CLI)
2. **Phase 2**: Wrap it in a Textual TUI for an immediate visual upgrade
3. **Phase 3** (optional): If mobile/browser access is wanted, build a Flask web frontend on top of the same backend logic

## Combined Daily Review Design

The key feature across all options:
- Pull due items from all three SRS systems (`.flashcard_data/`, `.conjugation_data/`, `.grammar_data/`)
- Interleave them randomly in one session
- Each card type renders appropriately (vocab = show word, conjugation = show verb+tense+pronoun, grammar = fill-in-the-blank)
- Unified session summary at the end (X vocab, Y conjugations, Z grammar reviewed)
- Single command to start: `python3 trainer.py --srs` or just launch the app

## Open Questions
- Should the unified trainer replace the individual scripts or coexist alongside them?
- Any preference on UI direction (terminal vs browser)?
- Want notification/reminder features for daily practice?
