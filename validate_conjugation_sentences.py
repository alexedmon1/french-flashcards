#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validator for conjugation-in-context sentences.

For every sentence in conjugation_sentence_data/*.json this checks that:
- id is present and unique across all files
- verb / tense / pronoun are known to the conjugation engine
- english and french text are present
- the engine-generated conjugated form actually appears in the french
  sentence (whole-token match)

The conjugation engine is the single source of truth: if an authored French
sentence uses a verb form that the engine would not produce, that item is
rejected here — before it can ever reach a practice session. Re-run this
whenever sentences are added or the verb data changes.

Usage:
    uv run python validate_conjugation_sentences.py

Exit code is 0 when every sentence is valid, 1 otherwise.
"""

import json
import sys
from pathlib import Path

from conjugation_engine import conjugate_one, get_all_tenses, get_verb
from exercise_types import CONJ_SENTENCE_DATA_DIR, verb_form_present

REQUIRED_FIELDS = ("id", "verb", "tense", "pronoun", "english", "french")
VALID_PRONOUNS = {"je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"}
VALID_TENSES = set(get_all_tenses())


def validate() -> int:
    if not CONJ_SENTENCE_DATA_DIR.exists():
        print(f"No data directory: {CONJ_SENTENCE_DATA_DIR}")
        return 1

    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    total = 0

    for json_path in sorted(CONJ_SENTENCE_DATA_DIR.glob("*.json")):
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)

        for sent in data.get("sentences", []):
            total += 1
            sid = sent.get("id", "<no-id>")
            loc = f"{json_path.name}:{sid}"

            missing = [field for field in REQUIRED_FIELDS if not sent.get(field)]
            if missing:
                errors.append(f"{loc}: missing field(s): {', '.join(missing)}")
                continue

            if sid in seen_ids:
                errors.append(f"{loc}: duplicate id (also in {seen_ids[sid]})")
            seen_ids[sid] = json_path.name

            verb, tense, pronoun = sent["verb"], sent["tense"], sent["pronoun"]

            if get_verb(verb) is None:
                errors.append(f"{loc}: unknown verb {verb!r}")
                continue
            if tense not in VALID_TENSES:
                errors.append(f"{loc}: unknown tense {tense!r}")
                continue
            if pronoun.lower() not in VALID_PRONOUNS:
                errors.append(f"{loc}: unknown pronoun {pronoun!r}")
                continue
            if sent.get("register") not in (None, "formal", "informal"):
                errors.append(f"{loc}: register must be 'formal'/'informal', "
                              f"got {sent['register']!r}")

            expected = conjugate_one(verb, tense, pronoun)
            if not verb_form_present(expected, sent["french"]):
                errors.append(
                    f"{loc}: engine form «{expected}» "
                    f"({verb}/{tense}/{pronoun}) not found in french "
                    f"«{sent['french']}»"
                )

    if errors:
        print(f"✗ {len(errors)} problem(s) across {total} sentence(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✓ All {total} sentence(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
