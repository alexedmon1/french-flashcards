#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conjugation Engine - Generates French verb conjugations algorithmically

This module loads verb data from verbs.json and generates conjugations for
regular verbs using patterns, while using stored forms for irregular verbs.

Supports 8 tenses:
- présent (present)
- futur proche (futur_proche)
- futur simple (future)
- imparfait (imparfait)
- passé composé (past)
- conditionnel présent (conditional)
- conditionnel passé (conditional_past)
- subjonctif présent (subjunctive)
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
    "subjunctive": ["e", "es", "e", "ions", "iez", "ent"],
}

# Regular -IR verb endings (finir pattern)
IR_ENDINGS = {
    "present": ["is", "is", "it", "issons", "issez", "issent"],
    "future": ["ai", "as", "a", "ons", "ez", "ont"],
    "imparfait": ["issais", "issais", "issait", "issions", "issiez", "issaient"],
    "conditional": ["ais", "ais", "ait", "ions", "iez", "aient"],
    "subjunctive": ["isse", "isses", "isse", "issions", "issiez", "issent"],
}

# Avoir conjugations (for passé composé)
AVOIR_PRESENT = ["ai", "as", "a", "avons", "avez", "ont"]

# Être conjugations (for passé composé)
ETRE_PRESENT = ["suis", "es", "est", "sommes", "êtes", "sont"]

# Avoir conjugations (for conditionnel passé)
AVOIR_CONDITIONAL = ["aurais", "aurais", "aurait", "aurions", "auriez", "auraient"]

# Être conjugations (for conditionnel passé)
ETRE_CONDITIONAL = ["serais", "serais", "serait", "serions", "seriez", "seraient"]

# Aller conjugations (for futur proche: aller + infinitif)
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

# Reflexive pronoun prefixes (without elision)
REFLEXIVE_PRONOUNS = ["me ", "te ", "se ", "nous ", "vous ", "se "]

# Vowels and h for elision check
_ELISION_CHARS = set("aeéèêëiîïoôuùûüyh")


def reflexive_prefix(pronoun_idx: int, form: str) -> str:
    """Return the reflexive pronoun prefix with elision if needed."""
    base = REFLEXIVE_PRONOUNS[pronoun_idx]  # e.g. "me ", "se "
    if form and form[0].lower() in _ELISION_CHARS and base not in ("nous ", "vous "):
        # me -> m', te -> t', se -> s'
        return base[0] + "'"
    return base


def je_elides_before(form: str) -> bool:
    """True if the subject 'je' would elide to 'j'' before this form.

    The form may already carry a reflexive prefix (e.g. "me sens"), in which
    case the first letter is a consonant and no elision occurs.
    """
    return bool(form) and form[0].lower() in _ELISION_CHARS


def join_pronoun(pronoun: str, form: str) -> str:
    """Join a subject pronoun and conjugated form, eliding 'je' -> 'j''.

    Only 'je' elides in French, and only before a vowel or mute h
    (j'aime, j'ai, j'habite). All other pronouns are joined with a space.
    """
    if pronoun == "je" and je_elides_before(form):
        return f"j'{form}"
    return f"{pronoun} {form}"


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


# Pure-vowel suffix that mutates the present-tense stem when used as the
# subjunctive nous/vous stem (e.g. voyons -> voy + ions = voyions).
_SUBJ_PLURAL_ENDINGS = ("ions", "iez")
_SUBJ_SING_ENDINGS = ("e", "es", "e", "ent")


def conjugate_subjunctive(infinitive: str, verb_data: dict) -> list[str]:
    """
    Generate présent du subjonctif conjugation.

    Pattern:
    - Singular and 3rd-plural forms derive from the ils-present stem
      (drop -ent, add e/es/e/ent).
    - 1st/2nd plural forms derive from the nous-present stem
      (drop -ons, add ions/iez).
    - Fully irregular verbs (être, avoir, aller, faire, pouvoir, savoir,
      vouloir, valoir) must supply explicit forms.subjunctive.
    """
    forms = verb_data.get("forms", {})
    if "subjunctive" in forms:
        return forms["subjunctive"]

    verb_type = verb_data.get("type", "")
    stem = get_stem(infinitive)

    if verb_type == "regular_er":
        return [stem + ending for ending in ER_ENDINGS["subjunctive"]]
    if verb_type == "regular_ir":
        return [stem + ending for ending in IR_ENDINGS["subjunctive"]]

    # Irregular: derive from present tense forms
    present_forms = conjugate_present(infinitive, verb_data)
    ils_present = present_forms[5]
    nous_present = present_forms[3]

    if not ils_present.endswith("ent"):
        raise ValueError(
            f"Cannot derive subjunctive for '{infinitive}': "
            f"3pl present '{ils_present}' does not end in -ent. "
            "Provide explicit forms.subjunctive in verbs.json."
        )
    if not nous_present.endswith("ons"):
        raise ValueError(
            f"Cannot derive subjunctive for '{infinitive}': "
            f"1pl present '{nous_present}' does not end in -ons. "
            "Provide explicit forms.subjunctive in verbs.json."
        )

    sing_stem = ils_present[:-3]
    plur_stem = nous_present[:-3]
    return [
        sing_stem + _SUBJ_SING_ENDINGS[0],   # je
        sing_stem + _SUBJ_SING_ENDINGS[1],   # tu
        sing_stem + _SUBJ_SING_ENDINGS[2],   # il/elle/on
        plur_stem + _SUBJ_PLURAL_ENDINGS[0], # nous
        plur_stem + _SUBJ_PLURAL_ENDINGS[1], # vous
        sing_stem + _SUBJ_SING_ENDINGS[3],   # ils/elles
    ]


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


def _conjugate_compound(infinitive: str, verb_data: dict,
                        selected_pronouns: list[str],
                        avoir_forms: list[str], etre_forms: list[str]) -> list[str]:
    """
    Generate a compound tense: auxiliary (in some tense) + past participle.

    Passé composé uses the present auxiliary; conditionnel passé uses the
    conditional auxiliary. The participle agreement and reflexive handling
    are identical, so both delegate here.

    Args:
        infinitive: The verb infinitive
        verb_data: Verb data dictionary
        selected_pronouns: List of 6 pronouns for this conjugation round
        avoir_forms: Auxiliary "avoir" forms in the target tense
        etre_forms: Auxiliary "être" forms in the target tense
    """
    auxiliary = verb_data.get("auxiliary", "avoir")
    participle = get_past_participle(infinitive, verb_data)

    # Get auxiliary forms
    aux_forms = avoir_forms if auxiliary == "avoir" else etre_forms

    # Handle reflexive verbs
    is_reflexive = verb_data.get("reflexive", False)

    result = []
    for i, pronoun in enumerate(selected_pronouns):
        agreed_participle = apply_participle_agreement(participle, pronoun, auxiliary)

        if is_reflexive:
            # Reflexive: je me suis assis(e) / je me serais assis(e)
            result.append(f"{reflexive_prefix(i, aux_forms[i])}{aux_forms[i]} {agreed_participle}")
        else:
            result.append(f"{aux_forms[i]} {agreed_participle}")

    return result


def conjugate_passe_compose(infinitive: str, verb_data: dict,
                            selected_pronouns: list[str]) -> list[str]:
    """Generate passé composé (present auxiliary + past participle)."""
    return _conjugate_compound(infinitive, verb_data, selected_pronouns,
                               AVOIR_PRESENT, ETRE_PRESENT)


def conjugate_conditionnel_passe(infinitive: str, verb_data: dict,
                                 selected_pronouns: list[str]) -> list[str]:
    """Generate conditionnel passé (conditional auxiliary + past participle)."""
    return _conjugate_compound(infinitive, verb_data, selected_pronouns,
                               AVOIR_CONDITIONAL, ETRE_CONDITIONAL)


def conjugate_futur_proche(infinitive: str, verb_data: dict,
                           selected_pronouns: list[str]) -> list[str]:
    """
    Generate futur proche: aller (présent) + infinitif.

    Non-reflexive: "je vais parler".
    Reflexive: the reflexive pronoun sits before the infinitive and agrees
    with the subject: "je vais me lever", "il va se lever", "nous allons
    nous lever". `infinitive` is the bare infinitive (reflexive prefix
    already stripped by conjugate()).
    """
    is_reflexive = verb_data.get("reflexive", False)

    result = []
    for i in range(6):
        aller = ALLER_PRESENT[i]
        if is_reflexive:
            result.append(f"{aller} {reflexive_prefix(i, infinitive)}{infinitive}")
        else:
            result.append(f"{aller} {infinitive}")

    return result


# ----------------------------------------------------------------------
# Main conjugation interface
# ----------------------------------------------------------------------

def get_random_pronouns() -> list[str]:
    """Get a set of randomly selected pronoun variations."""
    return [random.choice(variations) for variations in PRONOUN_VARIATIONS]


# Concrete subject pronoun -> person index (0..5) into a conjugation.
_PRONOUN_INDEX = {
    "je": 0, "j'": 0,
    "tu": 1,
    "il": 2, "elle": 2, "on": 2,
    "nous": 3,
    "vous": 4,
    "ils": 5, "elles": 5,
}


def pronoun_index(pronoun: str) -> int:
    """Return the person index (0..5) for a concrete subject pronoun."""
    idx = _PRONOUN_INDEX.get(pronoun.strip().lower())
    if idx is None:
        raise ValueError(f"Unknown subject pronoun: {pronoun!r}")
    return idx


def conjugate_one(infinitive: str, tense: str, pronoun: str) -> str:
    """
    Return the single conjugated form for a concrete subject pronoun.

    The concrete pronoun (e.g. "elle", "ils") is placed at its person slot so
    that compound-tense participle agreement is computed correctly, and the
    matching form is returned (e.g. conjugate_one("aller", "past", "elle")
    -> "est allée"). Includes reflexive/auxiliary clitics where applicable.
    """
    idx = pronoun_index(pronoun)
    # Default concrete pronoun per slot, overriding the target slot.
    selected = [variations[0] for variations in PRONOUN_VARIATIONS]
    selected[idx] = pronoun.strip().lower()
    _, forms = conjugate(infinitive, tense, selected)
    return forms[idx]


def conjugate(infinitive: str, tense: str,
              selected_pronouns: Optional[list[str]] = None) -> tuple[list[str], list[str]]:
    """
    Generate conjugation for a verb in a given tense.

    Args:
        infinitive: The verb infinitive (e.g., "parler")
        tense: One of "present", "futur_proche", "future", "imparfait",
               "past", "conditional", "conditional_past", "subjunctive"
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

    is_reflexive = verb_data.get("reflexive", False)

    # Strip reflexive prefix for conjugation (se sentir -> sentir)
    bare_infinitive = infinitive
    if is_reflexive:
        if infinitive.startswith("se "):
            bare_infinitive = infinitive[3:]
        elif infinitive.startswith("s'"):
            bare_infinitive = infinitive[2:]

    # Generate conjugation based on tense
    # Note: compound tenses and futur proche handle reflexive pronouns internally
    if tense == "present":
        forms = conjugate_present(bare_infinitive, verb_data)
    elif tense == "futur_proche":
        forms = conjugate_futur_proche(bare_infinitive, verb_data, selected_pronouns)
    elif tense == "future":
        forms = conjugate_future(bare_infinitive, verb_data)
    elif tense == "imparfait":
        forms = conjugate_imparfait(bare_infinitive, verb_data)
    elif tense == "past":
        forms = conjugate_passe_compose(bare_infinitive, verb_data, selected_pronouns)
    elif tense == "conditional":
        forms = conjugate_conditional(bare_infinitive, verb_data)
    elif tense == "conditional_past":
        forms = conjugate_conditionnel_passe(bare_infinitive, verb_data, selected_pronouns)
    elif tense == "subjunctive":
        forms = conjugate_subjunctive(bare_infinitive, verb_data)
    else:
        raise ValueError(f"Unknown tense: {tense}")

    # Add reflexive pronouns for simple tenses. Compound tenses (passé
    # composé, conditionnel passé) and futur proche place the reflexive
    # pronoun internally, so skip them here.
    if is_reflexive and tense not in ("past", "conditional_past", "futur_proche"):
        forms = [reflexive_prefix(i, form) + form for i, form in enumerate(forms)]

    return selected_pronouns, forms


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def get_verb_regularity(infinitive: str, tense: str) -> str:
    """Describe whether a verb is regular or irregular in a given tense.

    Returns a short string like "Regular -ER verb", "Irregular",
    or "Irregular stem" for the hint system.
    """
    verb_data = get_verb(infinitive)
    if not verb_data:
        return ""

    verb_type = verb_data.get("type", "")

    if verb_type == "regular_er":
        return "Regular -ER verb"
    elif verb_type == "regular_ir":
        return "Regular -IR verb"

    # Irregular verb — check if this specific tense uses explicit forms or stems
    forms = verb_data.get("forms", {})
    stems = verb_data.get("stems", {})

    tense_key = tense
    if tense in ("past", "conditional_past"):
        # Compound tenses: irregular if has explicit past_participle
        if "past_participle" in verb_data:
            return "Irregular (past participle)"
        return "Irregular"

    if tense == "futur_proche":
        # Always aller (présent) + infinitif — uniform construction
        return "aller (présent) + infinitif"

    if tense_key in forms:
        return "Irregular (unique forms)"

    stem_map = {"future": "future", "imparfait": "imparfait", "conditional": "future"}
    if stem_map.get(tense_key) in stems:
        return "Irregular (irregular stem)"

    if tense == "present":
        return "Irregular"

    return "Irregular"


def get_pattern_hint(infinitive: str, tense: str) -> Optional[str]:
    """Return an ending-pattern hint as two lines (header + formula).

    Regular -ER / -IR verbs get their canonical pattern. Irregular verbs
    also get a useful hint for future, conditional, imparfait, and past
    composé — only the stem (or past participle) is verb-specific in
    those tenses; the endings are universal.

    Returns None when there is no clean formula (irregular present /
    subjunctive, or any tense where the verb defines explicit forms).
    """
    verb_data = get_verb(infinitive)
    if not verb_data:
        return None

    verb_type = verb_data.get("type", "")
    forms = verb_data.get("forms", {})
    stems = verb_data.get("stems", {})
    tense_label = get_tense_display_name(tense)

    if verb_type == "regular_er":
        type_label = "Régulier -ER"
    elif verb_type == "regular_ir":
        type_label = "Régulier -IR"
    else:
        type_label = "Irrégulier"
    header = f"{type_label}, {tense_label}"

    # Futur proche — aller (présent) + infinitif, universal structure
    if tense == "futur_proche":
        return f"{header}\n  aller (présent) + «{infinitive}» (infinitif)"

    # Compound tenses — auxiliary + past participle, universal structure.
    # Passé composé uses the present auxiliary; conditionnel passé the
    # conditional auxiliary.
    if tense in ("past", "conditional_past"):
        aux_tense = "présent" if tense == "past" else "conditionnel"
        if verb_type == "regular_er":
            return f"{header}\n  avoir/être ({aux_tense}) + participe passé en -é"
        if verb_type == "regular_ir":
            return f"{header}\n  avoir/être ({aux_tense}) + participe passé en -i"
        aux = verb_data.get("auxiliary", "avoir")
        pp = verb_data.get("past_participle")
        if pp:
            return f"{header}\n  {aux} ({aux_tense}) + «{pp}» (participe passé)"
        return None

    # If the verb defines explicit forms for this tense, no formula applies.
    if tense in forms:
        return None

    # Regular -ER / -IR: stem (or infinitive) + canonical endings.
    if verb_type in ("regular_er", "regular_ir"):
        endings = (ER_ENDINGS if verb_type == "regular_er" else IR_ENDINGS).get(tense)
        if not endings:
            return None
        stem_label = "infinitif" if tense in ("future", "conditional") else "stem"
        return f"{header}\n  {stem_label} + {'/'.join(endings)}"

    # Irregular verb: endings are still universal for future / conditional
    # / imparfait. Only the stem is verb-specific.
    if tense in ("future", "conditional"):
        stem = stems.get("future")
        if not stem:
            if infinitive.endswith(("er", "ir")):
                stem = infinitive
            elif infinitive.endswith("re"):
                stem = infinitive[:-1]
            else:
                return None
        endings = ER_ENDINGS[tense]
        return f"{header}\n  radical «{stem}-» + {'/'.join(endings)}"

    if tense == "imparfait":
        stem = get_imparfait_stem(infinitive, verb_data)
        endings = ["ais", "ais", "ait", "ions", "iez", "aient"]
        return f"{header}\n  radical «{stem}-» + {'/'.join(endings)}"

    # Irregular present / subjunctive: no single-line formula.
    return None


def get_tense_display_name(tense: str) -> str:
    """Get the French display name for a tense."""
    names = {
        "present": "présent",
        "futur_proche": "futur proche",
        "future": "futur simple",
        "imparfait": "imparfait",
        "past": "passé composé",
        "conditional": "conditionnel présent",
        "conditional_past": "conditionnel passé",
        "subjunctive": "subjonctif présent",
    }
    return names.get(tense, tense)


def get_all_tenses() -> list[str]:
    """Get list of all supported tense codes."""
    return ["present", "futur_proche", "future", "imparfait", "past",
            "conditional", "conditional_past", "subjunctive"]


# ----------------------------------------------------------------------
# Validation / Testing
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Quick test of the engine
    print("Testing conjugation engine...\n")

    test_verbs = ["parler", "finir", "être", "avoir", "aller"]
    test_tenses = get_all_tenses()

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
