#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Daily French Trainer — Textual TUI

Combines vocabulary, conjugation, and grammar practice into a single
daily session with SRS. Launch with: uv run python3 daily_trainer.py
"""

import json
import time
from datetime import date, timedelta
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Button, Footer, Header, Input, Label, ProgressBar, Static

from srs_core import SRSStats, load_stats, save_stats, normalize_input
from exercise_types import (
    Exercise, load_all_due, get_due_counts,
    FLASHCARD_STATS_FILE, CONJUGATION_STATS_FILE, GRAMMAR_STATS_FILE,
)

# ----------------------------------------------------------------------
# Session persistence
# ----------------------------------------------------------------------
DAILY_DATA_DIR = Path(".daily_trainer_data")
PROGRESS_FILE = DAILY_DATA_DIR / "progress.json"


def load_daily_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {"sessions": [], "streak": 0, "last_session": None}
    with PROGRESS_FILE.open() as f:
        return json.load(f)


def save_daily_progress(progress: dict):
    DAILY_DATA_DIR.mkdir(exist_ok=True)
    with PROGRESS_FILE.open("w") as f:
        json.dump(progress, f, indent=2)


def update_streak(progress: dict) -> dict:
    today = date.today().isoformat()
    if progress["last_session"]:
        last = date.fromisoformat(progress["last_session"])
        current = date.today()
        if (current - last).days == 1:
            progress["streak"] += 1
        elif (current - last).days > 1:
            progress["streak"] = 1
    else:
        progress["streak"] = 1
    progress["last_session"] = today
    return progress


# Type color labels
TYPE_COLORS = {
    "Vocabulary": "cyan",
    "Conjugation": "magenta",
    "Grammar": "yellow",
}


# ----------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------
APP_CSS = """
Screen {
    background: $surface;
}

#dashboard {
    align: center middle;
    width: 100%;
    height: 100%;
}

#dashboard-box {
    width: 60;
    height: auto;
    border: round $primary;
    padding: 1 2;
}

#dashboard-title {
    text-align: center;
    text-style: bold;
    color: $text;
    margin-bottom: 1;
}

.stat-row {
    height: 1;
    margin: 0 1;
}

.stat-label {
    width: 1fr;
    color: $text-muted;
}

.stat-value {
    width: auto;
    text-style: bold;
}

.vocab-count { color: cyan; }
.conj-count { color: magenta; }
.gram-count { color: yellow; }
.total-count { color: $success; text-style: bold; }

#dashboard-buttons {
    margin-top: 1;
    align: center middle;
    height: 3;
}

#dashboard-buttons Button {
    margin: 0 1;
}

/* Exercise screen */
#exercise-header {
    height: 3;
    dock: top;
    padding: 0 2;
}

#progress-row {
    height: 1;
    margin: 0 1;
}

#progress-label {
    width: auto;
    margin-right: 1;
}

#timer-label {
    width: auto;
    dock: right;
}

#exercise-progress {
    width: 1fr;
}

#exercise-body {
    align: center middle;
    width: 100%;
    height: 1fr;
}

#exercise-card {
    width: 70;
    height: auto;
    border: round $primary;
    padding: 1 2;
}

#type-label {
    text-style: bold;
    margin-bottom: 1;
}

#prompt-label {
    margin-bottom: 1;
}

#answer-input {
    margin-bottom: 1;
}

#feedback-label {
    height: auto;
    min-height: 2;
}

.correct { color: $success; }
.incorrect { color: $error; }

/* Summary screen */
#summary {
    align: center middle;
    width: 100%;
    height: 100%;
}

#summary-box {
    width: 65;
    height: auto;
    max-height: 90%;
    border: round $primary;
    padding: 1 2;
}

#summary-title {
    text-align: center;
    text-style: bold;
    color: $text;
    margin-bottom: 1;
}

#summary-scroll {
    height: auto;
    max-height: 30;
}

.summary-stat {
    height: 1;
    margin: 0 1;
}

.missed-header {
    text-style: bold;
    margin-top: 1;
    color: $error;
}

.missed-item {
    margin: 0 2;
    color: $text-muted;
}

#summary-buttons {
    margin-top: 1;
    align: center middle;
    height: 3;
}

#summary-buttons Button {
    margin: 0 1;
}

#hint-label {
    color: $text-muted;
    text-style: italic;
    height: auto;
}

#direction-label {
    color: $text-muted;
    margin-bottom: 0;
}
"""


# ======================================================================
# Dashboard Screen
# ======================================================================
class DashboardScreen(Screen):
    BINDINGS = [
        Binding("s", "start_session", "Start Session"),
        Binding("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Center(id="dashboard"):
            with Vertical(id="dashboard-box"):
                yield Label("Daily French Trainer", id="dashboard-title")
                yield Static(id="stats-display")
                with Center(id="dashboard-buttons"):
                    yield Button("Start Session (s)", id="btn-start", variant="primary")
                    yield Button("Quit (q)", id="btn-quit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_stats()

    def _refresh_stats(self) -> None:
        counts = get_due_counts()
        progress = load_daily_progress()

        total = sum(counts.values())
        est_minutes = max(1, round(total * 0.75))  # ~45s per item
        if total > 60:
            est_minutes = max(1, round(60 * 0.75))  # capped at session size

        lines = []
        lines.append(f"  Vocabulary:    [cyan]{counts['Vocabulary']}[/]")
        lines.append(f"  Conjugation:   [magenta]{counts['Conjugation']}[/]")
        lines.append(f"  Grammar:       [yellow]{counts['Grammar']}[/]")
        lines.append("")
        lines.append(f"  Total due:     [bold green]{total}[/]")
        session_size = min(total, 60)
        lines.append(f"  Session size:  {session_size} items (~{est_minutes} min)")
        lines.append(f"  Streak:        {progress['streak']} day(s)")

        widget = self.query_one("#stats-display", Static)
        widget.update("\n".join(lines))

    def action_start_session(self) -> None:
        self.app.push_screen(ExerciseScreen())

    def action_quit_app(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#btn-start")
    def on_start(self) -> None:
        self.action_start_session()

    @on(Button.Pressed, "#btn-quit")
    def on_quit(self) -> None:
        self.action_quit_app()


# ======================================================================
# Exercise Screen
# ======================================================================
class ExerciseScreen(Screen):
    BINDINGS = [
        Binding("escape", "end_session", "End Session"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.exercises: list[Exercise] = []
        self.current_idx = 0
        self.results: list[dict] = []  # {exercise, correct}
        self.session_start = 0.0
        self.waiting_for_next = False
        self._all_stats: dict[Path, dict[str, SRSStats]] = {}
        self._session_timer: Timer | None = None
        self._time_warning_shown = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="exercise-header"):
            with Horizontal(id="progress-row"):
                yield Label("0/0", id="progress-label")
                yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="exercise-progress")
                yield Label("0:00", id="timer-label")
        with Center(id="exercise-body"):
            with Vertical(id="exercise-card"):
                yield Label("", id="type-label")
                yield Label("", id="direction-label")
                yield Label("", id="prompt-label")
                yield Input(placeholder="Type your answer...", id="answer-input")
                yield Label("", id="hint-label")
                yield Label("", id="feedback-label")
        yield Footer()

    def on_mount(self) -> None:
        self.exercises = load_all_due()

        if not self.exercises:
            self.query_one("#type-label", Label).update("[bold green]All done![/]")
            self.query_one("#prompt-label", Label).update("No exercises due for review today.")
            self.query_one("#answer-input", Input).display = False
            return

        # Pre-load all stats files we'll need
        for stats_file in {FLASHCARD_STATS_FILE, CONJUGATION_STATS_FILE, GRAMMAR_STATS_FILE}:
            self._all_stats[stats_file] = load_stats(stats_file)

        self.session_start = time.monotonic()
        self._session_timer = self.set_interval(1.0, self._tick_timer)
        self._show_exercise()

    def _tick_timer(self) -> None:
        elapsed = time.monotonic() - self.session_start
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        label = self.query_one("#timer-label", Label)
        label.update(f"{minutes}:{seconds:02d}")

        # Show "good stopping point" after 15 minutes
        if elapsed >= 900 and not self._time_warning_shown:
            self._time_warning_shown = True
            feedback = self.query_one("#feedback-label", Label)
            feedback.update("[bold yellow]15 minutes reached — good stopping point! Press Esc to finish, or keep going.[/]")

    def _show_exercise(self) -> None:
        if self.current_idx >= len(self.exercises):
            self._end_session()
            return

        ex = self.exercises[self.current_idx]
        color = TYPE_COLORS.get(ex.type_name, "white")

        self.query_one("#type-label", Label).update(f"[{color} bold]{ex.type_name}[/]")
        self.query_one("#prompt-label", Label).update(ex.get_prompt())
        self.query_one("#feedback-label", Label).update("")
        self.query_one("#hint-label", Label).update("")

        # Show direction hint for vocabulary
        direction_label = self.query_one("#direction-label", Label)
        if ex.type_name == "Vocabulary":
            arrow = "French -> English" if ex.direction == "english" else "English -> French"
            direction_label.update(f"[dim]{arrow}[/]")
        else:
            direction_label.update("")

        inp = self.query_one("#answer-input", Input)
        inp.value = ""
        inp.display = True
        inp.disabled = False
        inp.focus()

        # Update progress
        total = len(self.exercises)
        self.query_one("#progress-label", Label).update(f"{self.current_idx + 1}/{total}")
        pbar = self.query_one("#exercise-progress", ProgressBar)
        pbar.total = total
        pbar.progress = self.current_idx

        self.waiting_for_next = False

    @on(Input.Submitted, "#answer-input")
    def on_answer_submitted(self, event: Input.Submitted) -> None:
        if self.waiting_for_next:
            self._advance()
            return

        if self.current_idx >= len(self.exercises):
            return

        raw = event.value.strip()

        # Handle hint request
        if raw.lower() == "h":
            ex = self.exercises[self.current_idx]
            hint = ex.get_hint()
            if hint:
                self.query_one("#hint-label", Label).update(f"[dim italic]Hint: {hint}[/]")
            inp = self.query_one("#answer-input", Input)
            inp.value = ""
            inp.focus()
            return

        if not raw:
            return

        user_input = normalize_input(raw)
        ex = self.exercises[self.current_idx]
        correct = ex.check(user_input)

        # Record result
        self.results.append({"exercise": ex, "correct": correct})

        # Update SRS
        quality = 2 if correct else 0
        stats_dict = self._all_stats.get(ex.stats_file, {})
        if ex.key not in stats_dict:
            stats_dict[ex.key] = SRSStats(ex.key)
        stats_dict[ex.key].update(quality)
        self._all_stats[ex.stats_file] = stats_dict
        save_stats(stats_dict, ex.stats_file)

        # Show feedback
        feedback = self.query_one("#feedback-label", Label)
        if correct:
            feedback.update(f"[bold green]Correct![/] {ex.get_correct()}")
        else:
            feedback.update(f"[bold red]Incorrect.[/] Correct: {ex.get_correct()}")

        # Update progress bar
        pbar = self.query_one("#exercise-progress", ProgressBar)
        pbar.progress = self.current_idx + 1

        # Disable input and wait for next submit
        inp = self.query_one("#answer-input", Input)
        inp.value = ""
        inp.placeholder = "Press Enter to continue..."
        inp.focus()
        self.waiting_for_next = True

    def _advance(self) -> None:
        self.current_idx += 1
        inp = self.query_one("#answer-input", Input)
        inp.placeholder = "Type your answer..."
        self._show_exercise()

    def _end_session(self) -> None:
        if self._session_timer:
            self._session_timer.stop()
        elapsed = time.monotonic() - self.session_start if self.session_start else 0
        self.app.push_screen(SummaryScreen(self.results, elapsed))

    def action_end_session(self) -> None:
        self._end_session()


# ======================================================================
# Summary Screen
# ======================================================================
class SummaryScreen(Screen):
    BINDINGS = [
        Binding("d", "dashboard", "Dashboard"),
        Binding("q", "quit_app", "Quit"),
    ]

    def __init__(self, results: list[dict], elapsed: float) -> None:
        super().__init__()
        self._results = results
        self._elapsed = elapsed

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Center(id="summary"):
            with Vertical(id="summary-box"):
                yield Label("Session Summary", id="summary-title")
                with VerticalScroll(id="summary-scroll"):
                    yield Static(id="summary-content")
                with Center(id="summary-buttons"):
                    yield Button("Dashboard (d)", id="btn-dashboard", variant="primary")
                    yield Button("Quit (q)", id="btn-summary-quit", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        total = len(self._results)
        correct = sum(1 for r in self._results if r["correct"])
        accuracy = (correct / total * 100) if total > 0 else 0

        minutes = int(self._elapsed) // 60
        seconds = int(self._elapsed) % 60

        # Breakdown by type
        type_stats: dict[str, dict] = {}
        for r in self._results:
            t = r["exercise"].type_name
            if t not in type_stats:
                type_stats[t] = {"total": 0, "correct": 0}
            type_stats[t]["total"] += 1
            if r["correct"]:
                type_stats[t]["correct"] += 1

        lines = []
        lines.append(f"  Time:      {minutes}:{seconds:02d}")
        lines.append(f"  Reviewed:  {total} items")
        lines.append(f"  Correct:   {correct}/{total} ({accuracy:.0f}%)")
        lines.append("")

        for type_name in ["Vocabulary", "Conjugation", "Grammar"]:
            if type_name in type_stats:
                ts = type_stats[type_name]
                color = TYPE_COLORS.get(type_name, "white")
                lines.append(f"  [{color}]{type_name}[/]: {ts['correct']}/{ts['total']}")

        # Update streak
        progress = load_daily_progress()
        if total > 0:
            progress = update_streak(progress)
            progress["sessions"].append({
                "date": date.today().isoformat(),
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 1),
            })
            save_daily_progress(progress)

        lines.append("")
        lines.append(f"  Streak:    {progress['streak']} day(s)")

        # Missed items
        missed = [r for r in self._results if not r["correct"]]
        if missed:
            lines.append("")
            lines.append("[bold red]  Missed items:[/]")
            for r in missed:
                ex = r["exercise"]
                color = TYPE_COLORS.get(ex.type_name, "white")
                lines.append(f"    [{color}]{ex.type_name}[/]: {ex.get_correct()}")

        self.query_one("#summary-content", Static).update("\n".join(lines))

    def action_dashboard(self) -> None:
        # Pop back to dashboard (remove exercise + summary screens)
        self.app.pop_screen()  # pop summary
        self.app.pop_screen()  # pop exercise
        # Refresh dashboard
        dashboard = self.app.screen
        if hasattr(dashboard, "_refresh_stats"):
            dashboard._refresh_stats()

    def action_quit_app(self) -> None:
        self.app.exit()

    @on(Button.Pressed, "#btn-dashboard")
    def on_dashboard(self) -> None:
        self.action_dashboard()

    @on(Button.Pressed, "#btn-summary-quit")
    def on_quit(self) -> None:
        self.action_quit_app()


# ======================================================================
# Main App
# ======================================================================
class DailyTrainerApp(App):
    CSS = APP_CSS
    TITLE = "Daily French Trainer"
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())


def main():
    app = DailyTrainerApp()
    app.run()


if __name__ == "__main__":
    main()
