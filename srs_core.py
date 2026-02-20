#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared SRS (Spaced Repetition System) core module.

Provides the SM-2 algorithm, stats tracking, normalize_input utility,
and file I/O helpers used by all trainers.
"""

import json
import unicodedata
from datetime import date, timedelta
from pathlib import Path

# SRS intervals (in days) - simplified SM-2 algorithm
INTERVALS = {
    0: 0,      # Wrong - review same session
    1: 1,      # Hard - 1 day
    2: 3,      # Good - 3 days
    3: 7,      # Easy - 1 week
}


class SRSStats:
    """Track SRS data for a single item (card, verb-tense combo, exercise, etc.)."""

    def __init__(self, key: str):
        self.key = key
        self.times_seen = 0
        self.times_correct = 0
        self.last_reviewed = None
        self.interval = 0  # days until next review
        self.ease_factor = 2.5
        self.due_date = date.today().isoformat()

    def to_dict(self) -> dict:
        return {
            "times_seen": self.times_seen,
            "times_correct": self.times_correct,
            "last_reviewed": self.last_reviewed,
            "interval": self.interval,
            "ease_factor": self.ease_factor,
            "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, key: str, data: dict) -> "SRSStats":
        stats = cls(key)
        stats.times_seen = data.get("times_seen", 0)
        stats.times_correct = data.get("times_correct", 0)
        stats.last_reviewed = data.get("last_reviewed")
        stats.interval = data.get("interval", 0)
        stats.ease_factor = data.get("ease_factor", 2.5)
        stats.due_date = data.get("due_date", date.today().isoformat())
        return stats

    def update(self, quality: int):
        """Update stats based on performance (0=wrong, 1=hard, 2=good, 3=easy)."""
        self.times_seen += 1
        if quality > 0:
            self.times_correct += 1

        self.last_reviewed = date.today().isoformat()

        # Update ease factor (simplified SM-2)
        self.ease_factor = max(
            1.3,
            self.ease_factor + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02)),
        )

        # Calculate next interval
        if quality == 0:
            self.interval = 0
        else:
            if self.times_correct == 1:
                self.interval = INTERVALS[quality]
            else:
                self.interval = int(self.interval * self.ease_factor)

        # Calculate due date
        next_date = date.today() + timedelta(days=self.interval)
        self.due_date = next_date.isoformat()


def load_stats(file_path: Path, stats_cls: type[SRSStats] = SRSStats) -> dict[str, SRSStats]:
    """Load SRS statistics from a JSON file."""
    if not file_path.exists():
        return {}
    with file_path.open() as f:
        data = json.load(f)
    return {key: stats_cls.from_dict(key, val) for key, val in data.items()}


def save_stats(stats: dict[str, SRSStats], file_path: Path):
    """Save SRS statistics to a JSON file."""
    file_path.parent.mkdir(exist_ok=True)
    data = {key: val.to_dict() for key, val in stats.items()}
    with file_path.open("w") as f:
        json.dump(data, f, indent=2)


def normalize_input(text: str) -> str:
    """
    Clean up input text by removing surrogate characters and normalizing Unicode.

    Handles issues from typing accented characters and using backspace,
    which can leave behind invisible combining characters or malformed
    Unicode sequences.
    """
    # Handle backspace characters
    while "\x08" in text or "\x7f" in text:
        if "\x08" in text:
            idx = text.index("\x08")
            if idx > 0:
                text = text[: idx - 1] + text[idx + 1 :]
            else:
                text = text[1:]
        if "\x7f" in text:
            idx = text.index("\x7f")
            if idx > 0:
                text = text[: idx - 1] + text[idx + 1 :]
            else:
                text = text[1:]

    # Normalize to NFC
    normalized = unicodedata.normalize("NFC", text)

    # Remove surrogate characters
    cleaned = normalized.encode("utf-8", errors="ignore").decode(
        "utf-8", errors="ignore"
    )

    # Invisible characters to remove
    invisible_chars = {
        "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad",
        "\u034f", "\u061c", "\u115f", "\u1160", "\u17b4", "\u17b5",
        "\u180e", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",
        "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200a",
        "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
        "\u2066", "\u2067", "\u2068", "\u2069",
    }

    cleaned = "".join(
        char
        for char in cleaned
        if char not in invisible_chars
        and (
            unicodedata.category(char) not in ("Cc", "Cf")
            or char in ("\n", "\r", "\t")
        )
    )

    return cleaned.strip()
