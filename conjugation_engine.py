#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conjugation Engine - Generates French verb conjugations algorithmically

This module loads verb data from verbs.json and generates conjugations for
regular verbs using patterns, while using stored forms for irregular verbs.

Supports 7 tenses:
- présent (present)
- futur simple (future)
- imparfait (imparfait)
- passé composé (past)
- futur proche (near_future)
- conditionnel présent (conditional)
- conditionnel passé (conditional_past)
"""

import json
import random
from pathlib import Path
from typing import Optional

# Path to verb data
VERB_DATA_PATH = Path(__file__).parent / "conjugation_data" / "verbs.json"

# Cache for loaded verb data
_VERB_DATA: Optional[dict] = None


# ----------------------------------------------------------------------
# Conjugation patterns
# ----------------------------------------------------------------------

# Regular -ER verb endings
ER_ENDINGS = {
    "present": ["e", "es", "e", "ons", "ez", "ent"],
    "future": ["ai", "as", "a", "ons", "ez", "ont"],
    "imparfait": ["ais", "ais", "ait", "ions", "iez", "aient"],
    "conditional": ["ais", "ais", "ait", "ions", "iez", "aient"],
}

# Regular -IR verb endings (finir pattern)
IR_ENDINGS = {
    "present": ["is", "is", "it", "issons", "issez", "issent"],
    "future": ["ai", "as", "a", "ons", "ez", "ont"],
    "imparfait": ["issais", "issais", "issait", "issions", "issiez", "issaient"],
    "conditional": ["ais", "ais", "ait", "ions", "iez", "aient"],
}

# Avoir conjugations (for passé composé and conditionnel passé)
AVOIR_PRESENT = ["ai", "as", "a", "avons", "avez", "ont"]
AVOIR_CONDITIONAL = ["aurais", "aurais", "aurait", "aurions", "auriez", "auraient"]

# Être conjugations (for passé composé and conditionnel passé)
ETRE_PRESENT = ["suis", "es", "est", "sommes", "êtes", "sont"]
ETRE_CONDITIONAL = ["serais", "serais", "serait", "serions", "seriez", "seraient"]

# Aller present (for futur proche)
ALLER_PRESENT = ["vais", "vas", "va", "allons", "allez", "vont"]

# Pronoun variations with gender
PRONOUN_VARIATIONS = [
    ["je"],                    # je
    ["tu"],                    # tu
    ["il", "elle", "on"],      # 3rd singular
    ["nous"],                  # nous
    ["vous"],                  # vous
    ["ils", "elles"],          # 3rd plural
]

# Standard pronouns for display
PRONOUNS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# Reflexive pronoun prefixes
REFLEXIVE_PRONOUNS = ["me ", "te ", "se ", "nous ", "vous ", "se "]


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------

def load_verbs() -> dict:
    """Load verb data from JSON file. Caches the result."""
    global _VERB_DATA
    if _VERB_DATA is None:
        with open(VERB_DATA_PATH, encoding='utf-8') as f:
            _VERB_DATA = json.load(f)
    return _VERB_DATA


def get_verb(infinitive: str) -> Optional[dict]:
    """Get data for a specific verb."""
    data = load_verbs()
    return data.get("verbs", {}).get(infinitive)


def get_all_verbs() -> list[str]:
    """Get list of all verb infinitives."""
    data = load_verbs()
    return list(data.get("verbs", {}).keys())


def get_verbs_by_type(verb_type: str) -> list[str]:
    """Get list of verbs of a specific type (regular_er, regular_ir, irregular)."""
    data = load_verbs()
    return [v for v, info in data.get("verbs", {}).items() if info.get("type") == verb_type]


def get_verbs_by_tier(tier: str) -> list[str]:
    """Get list of verbs of a specific tier (core, intermediate, advanced)."""
    data = load_verbs()
    return [v for v, info in data.get("verbs", {}).items() if info.get("tier") == tier]


def get_translation(infinitive: str) -> str:
    """Get English translation for a verb."""
    verb = get_verb(infinitive)
    return verb.get("translation", "") if verb else ""


# ----------------------------------------------------------------------
# Stem extraction
# ----------------------------------------------------------------------

def get_stem(infinitive: str) -> str:
    """Get the stem for regular conjugation (remove -er or -ir ending)."""
    if infinitive.endswith("er"):
        return infinitive[:-2]
    elif infinitive.endswith("ir"):
        return infinitive[:-2]
    elif infinitive.endswith("re"):
        return infinitive[:-2]
    return infinitive


def get_future_stem(infinitive: str, verb_data: dict) -> str:
    """
    Get the stem for future/conditional tense.

    For regular verbs: infinitive (drop final 'e' for -re verbs)
    For irregular verbs: use stored stem if available, otherwise infinitive
    """
    # Check for irregular stem
    stems = verb_data.get("stems", {})
    if "future" in stems:
        return stems["future"]

    # Regular -ER and -IR: use full infinitive
    if infinitive.endswith("er") or infinitive.endswith("ir"):
        return infinitive

    # -RE verbs: drop the final 'e'
    if infinitive.endswith("re"):
        return infinitive[:-1]

    return infinitive


def get_imparfait_stem(infinitive: str, verb_data: dict) -> str:
    """
    Get the stem for imparfait tense.

    Usually the nous-present stem, but some verbs have irregular stems.
    """
    # Check for irregular stem
    stems = verb_data.get("stems", {})
    if "imparfait" in stems:
        return stems["imparfait"]

    # For regular verbs, use the regular stem
    verb_type = verb_data.get("type", "")
    if verb_type == "regular_er":
        return get_stem(infinitive)
    elif verb_type == "regular_ir":
        return get_stem(infinitive) + "iss"

    # For irregular verbs without explicit stem, derive from nous-present
    # This fallback shouldn't be needed if data is complete
    return get_stem(infinitive)


# ----------------------------------------------------------------------
# Conjugation functions
# ----------------------------------------------------------------------

def conjugate_present(infinitive: str, verb_data: dict) -> list[str]:
    """Generate present tense conjugation."""
    verb_type = verb_data.get("type", "")

    # Check for explicit forms
    forms = verb_data.get("forms", {})
    if "present" in forms:
        return forms["present"]

    # Generate regular conjugation
    stem = get_stem(infinitive)

    if verb_type == "regular_er":
        return [stem + ending for ending in ER_ENDINGS["present"]]
    elif verb_type == "regular_ir":
        return [stem + ending for ending in IR_ENDINGS["present"]]

    # Should not reach here for well-defined data
    return [stem + ending for ending in ER_ENDINGS["present"]]


def conjugate_future(infinitive: str, verb_data: dict) -> list[str]:
    """Generate future simple tense conjugation."""
    # Check for explicit forms
    forms = verb_data.get("forms", {})
    if "future" in forms:
        return forms["future"]

    # Generate using stem + endings
    stem = get_future_stem(infinitive, verb_data)
    return [stem + ending for ending in ER_ENDINGS["future"]]


def conjugate_imparfait(infinitive: str, verb_data: dict) -> list[str]:
    """Generate imparfait tense conjugation."""
    # Check for explicit forms
    forms = verb_data.get("forms", {})
    if "imparfait" in forms:
        return forms["imparfait"]

    # Generate using stem + endings
    stem = get_imparfait_stem(infinitive, verb_data)
    return [stem + ending for ending in ER_ENDINGS["imparfait"]]


def conjugate_conditional(infinitive: str, verb_data: dict) -> list[str]:
    """
    Generate conditional present tense conjugation.
    Uses future stem + imparfait-style endings.
    """
    # Check for explicit forms
    forms = verb_data.get("forms", {})
    if "conditional" in forms:
        return forms["conditional"]

    # Generate using future stem + conditional endings
    stem = get_future_stem(infinitive, verb_data)
    return [stem + ending for ending in ER_ENDINGS["conditional"]]


def get_past_participle(infinitive: str, verb_data: dict) -> str:
    """Get past participle for a verb."""
    # Check for explicit past participle
    if "past_participle" in verb_data:
        return verb_data["past_participle"]

    # Generate regular past participle
    verb_type = verb_data.get("type", "")
    stem = get_stem(infinitive)

    if verb_type == "regular_er":
        return stem + "é"
    elif verb_type == "regular_ir":
        return stem + "i"

    # Default to -é
    return stem + "é"


def apply_participle_agreement(participle: str, pronoun: str, auxiliary: str) -> str:
    """
    Apply gender/number agreement to past participle for être verbs.

    Args:
        participle: Base past participle
        pronoun: The selected pronoun (e.g., "elle", "ils")
        auxiliary: "être" or "avoir"
    """
    if auxiliary != "être":
        return participle

    # Determine the root and base ending
    if participle.endswith("é"):
        root = participle[:-1]
        if pronoun == "elle":
            return root + "ée"
        elif pronoun == "elles":
            return root + "ées"
        elif pronoun in ["nous", "vous", "ils"]:
            return root + "és"
        return root + "é"

    elif participle.endswith("i"):
        root = participle[:-1]
        if pronoun == "elle":
            return root + "ie"
        elif pronoun == "elles":
            return root + "ies"
        elif pronoun in ["nous", "vous", "ils"]:
            return root + "is"
        return root + "i"

    elif participle.endswith("u"):
        root = participle[:-1]
        if pronoun == "elle":
            return root + "ue"
        elif pronoun == "elles":
            return root + "ues"
        elif pronoun in ["nous", "vous", "ils"]:
            return root + "us"
        return root + "u"

    # Irregular participles (mort, né, etc.) - no easy pattern
    # These need to be handled specially
    if participle == "mort":
        if pronoun == "elle":
            return "morte"
        elif pronoun == "elles":
            return "mortes"
        elif pronoun in ["nous", "vous", "ils"]:
            return "morts"
    elif participle == "né":
        if pronoun == "elle":
            return "née"
        elif pronoun == "elles":
            return "nées"
        elif pronoun in ["nous", "vous", "ils"]:
            return "nés"

    return participle


def conjugate_passe_compose(infinitive: str, verb_data: dict,
                            selected_pronouns: list[str]) -> list[str]:
    """
    Generate passé composé tense conjugation.

    Args:
        infinitive: The verb infinitive
        verb_data: Verb data dictionary
        selected_pronouns: List of 6 pronouns for this conjugation round
    """
    auxiliary = verb_data.get("auxiliary", "avoir")
    participle = get_past_participle(infinitive, verb_data)

    # Get auxiliary forms
    aux_forms = AVOIR_PRESENT if auxiliary == "avoir" else ETRE_PRESENT

    # Handle reflexive verbs
    is_reflexive = verb_data.get("reflexive", False)

    result = []
    for i, pronoun in enumerate(selected_pronouns):
        agreed_participle = apply_participle_agreement(participle, pronoun, auxiliary)

        if is_reflexive:
            # Reflexive: je me suis assis
            result.append(f"{REFLEXIVE_PRONOUNS[i]}{aux_forms[i]} {agreed_participle}")
        else:
            result.append(f"{aux_forms[i]} {agreed_participle}")

    return result


def conjugate_futur_proche(infinitive: str, verb_data: dict) -> list[str]:
    """
    Generate futur proche (near future) tense conjugation.
    Structure: aller (present) + infinitive
    """
    is_reflexive = verb_data.get("reflexive", False)

    if is_reflexive:
        # For reflexive verbs: je vais me lever
        base_inf = infinitive.replace("se ", "").replace("s'", "")
        reflexive_pronouns = ["me", "te", "se", "nous", "vous", "se"]
        return [f"{ALLER_PRESENT[i]} {reflexive_pronouns[i]} {base_inf}"
                for i in range(6)]
    else:
        return [f"{ALLER_PRESENT[i]} {infinitive}" for i in range(6)]


def conjugate_conditional_past(infinitive: str, verb_data: dict,
                                selected_pronouns: list[str]) -> list[str]:
    """
    Generate conditionnel passé tense conjugation.
    Structure: avoir/être (conditional) + past participle
    """
    auxiliary = verb_data.get("auxiliary", "avoir")
    participle = get_past_participle(infinitive, verb_data)

    # Get conditional forms of auxiliary
    aux_forms = AVOIR_CONDITIONAL if auxiliary == "avoir" else ETRE_CONDITIONAL

    # Handle reflexive verbs
    is_reflexive = verb_data.get("reflexive", False)

    result = []
    for i, pronoun in enumerate(selected_pronouns):
        agreed_participle = apply_participle_agreement(participle, pronoun, auxiliary)

        if is_reflexive:
            result.append(f"{REFLEXIVE_PRONOUNS[i]}{aux_forms[i]} {agreed_participle}")
        else:
            result.append(f"{aux_forms[i]} {agreed_participle}")

    return result


# ----------------------------------------------------------------------
# Main conjugation interface
# ----------------------------------------------------------------------

def get_random_pronouns() -> list[str]:
    """Get a set of randomly selected pronoun variations."""
    return [random.choice(variations) for variations in PRONOUN_VARIATIONS]


def conjugate(infinitive: str, tense: str,
              selected_pronouns: Optional[list[str]] = None) -> tuple[list[str], list[str]]:
    """
    Generate conjugation for a verb in a given tense.

    Args:
        infinitive: The verb infinitive (e.g., "parler")
        tense: One of "present", "future", "imparfait", "past",
               "near_future", "conditional", "conditional_past"
        selected_pronouns: Optional list of 6 pronouns to use.
                          If None, random pronouns are selected.

    Returns:
        Tuple of (pronouns, conjugations) where both are lists of 6 strings.
    """
    verb_data = get_verb(infinitive)
    if not verb_data:
        raise ValueError(f"Unknown verb: {infinitive}")

    if selected_pronouns is None:
        selected_pronouns = get_random_pronouns()

    # Generate conjugation based on tense
    if tense == "present":
        forms = conjugate_present(infinitive, verb_data)
    elif tense == "future":
        forms = conjugate_future(infinitive, verb_data)
    elif tense == "imparfait":
        forms = conjugate_imparfait(infinitive, verb_data)
    elif tense == "past":
        forms = conjugate_passe_compose(infinitive, verb_data, selected_pronouns)
    elif tense == "near_future":
        forms = conjugate_futur_proche(infinitive, verb_data)
    elif tense == "conditional":
        forms = conjugate_conditional(infinitive, verb_data)
    elif tense == "conditional_past":
        forms = conjugate_conditional_past(infinitive, verb_data, selected_pronouns)
    else:
        raise ValueError(f"Unknown tense: {tense}")

    return selected_pronouns, forms


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def get_tense_display_name(tense: str) -> str:
    """Get the French display name for a tense."""
    names = {
        "present": "présent",
        "future": "futur simple",
        "imparfait": "imparfait",
        "past": "passé composé",
        "near_future": "futur proche",
        "conditional": "conditionnel présent",
        "conditional_past": "conditionnel passé",
    }
    return names.get(tense, tense)


def get_all_tenses() -> list[str]:
    """Get list of all supported tense codes."""
    return ["present", "future", "imparfait", "past",
            "near_future", "conditional", "conditional_past"]


# ----------------------------------------------------------------------
# Validation / Testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Quick test of the engine
    print("Testing conjugation engine...\n")

    test_verbs = ["parler", "finir", "être", "avoir", "aller"]
    test_tenses = ["present", "future", "imparfait", "past", "near_future",
                   "conditional", "conditional_past"]

    for verb in test_verbs:
        print(f"\n=== {verb} ({get_translation(verb)}) ===")
        for tense in test_tenses:
            pronouns, forms = conjugate(verb, tense)
            print(f"\n{get_tense_display_name(tense)}:")
            for p, f in zip(pronouns, forms):
                print(f"  {p}: {f}")

    # Print verb counts by tier
    print("\n\n=== Verb counts by tier ===")
    for tier in ["core", "intermediate", "advanced"]:
        verbs = get_verbs_by_tier(tier)
        print(f"{tier}: {len(verbs)} verbs")

    print(f"\nTotal verbs: {len(get_all_verbs())}")
