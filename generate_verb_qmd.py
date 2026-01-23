#!/usr/bin/env python3
"""Generate the full verb conjugation Quarto document."""

import sys
sys.path.insert(0, '.')

from conjugation_engine import (
    load_verbs, get_verbs_by_tier, get_verb,
    conjugate, get_past_participle, get_translation,
)

STANDARD_PRONOUNS = ["je", "tu", "il", "nous", "vous", "ils"]
DISPLAY_PRONOUNS = ["je", "tu", "il/elle", "nous", "vous", "ils/elles"]

TENSES = ["present", "future", "imparfait", "conditional", "past", "near_future", "conditional_past"]
TENSE_HEADERS = ["Présent", "Futur", "Imparfait", "Cond.", "P. Composé", "F. Proche", "Cond. Passé"]


def elide_je(form):
    """Apply j' elision."""
    if form and form[0] in "aeéèêiîoôuûhyAEIOUH":
        return f"j'{form}"
    return f"je {form}"


def format_form(pronoun_idx, form):
    """Format a conjugated form with its pronoun."""
    p = DISPLAY_PRONOUNS[pronoun_idx]
    if pronoun_idx == 0:  # je
        return elide_je(form)
    return f"{p} {form}"


def generate_verb_entry(verb, verb_data, out):
    """Generate a single verb's conjugation table."""
    translation = verb_data.get("translation", "")
    verb_type = verb_data.get("type", "")
    auxiliary = verb_data.get("auxiliary", "avoir")
    pp = get_past_participle(verb, verb_data)

    type_short = {"regular_er": "-ER", "regular_ir": "-IR", "irregular": "irreg."}.get(verb_type, verb_type)

    # Header
    out.write(f"### {verb} *({translation})* {{.unnumbered}}\n\n")
    out.write(f"Type: {type_short} | Aux: {auxiliary} | P.P.: {pp}\n\n")

    # Get all conjugations
    all_forms = []
    for tense in TENSES:
        _, forms = conjugate(verb, tense, selected_pronouns=STANDARD_PRONOUNS)
        all_forms.append(forms)

    # Build table
    out.write(f"| | {' | '.join(TENSE_HEADERS)} |\n")
    out.write(f"|---|{'---|' * 7}\n")

    for i in range(6):
        row_cells = []
        for t_idx, forms in enumerate(all_forms):
            form = forms[i]
            row_cells.append(form)

        pronoun = DISPLAY_PRONOUNS[i]
        out.write(f"| **{pronoun}** | {' | '.join(row_cells)} |\n")

    out.write("\n")


def main():
    load_verbs()

    with open("cheatsheet_verbs.qmd", "w", encoding="utf-8") as out:
        # YAML header
        out.write("""---
title: "French Verb Conjugations"
format:
  pdf:
    documentclass: article
    papersize: a4
    classoption:
      - landscape
    geometry:
      - margin=1.2cm
    fontsize: 8pt
    include-in-header:
      text: |
        \\usepackage{booktabs}
        \\usepackage{array}
        \\usepackage{longtable}
        \\pagestyle{plain}
        \\setlength{\\parindent}{0pt}
        \\setlength{\\parskip}{3pt}
        \\setlength{\\tabcolsep}{2.5pt}
        \\renewcommand{\\arraystretch}{1.15}
---

""")

        for tier in ["core", "intermediate", "advanced"]:
            verbs = get_verbs_by_tier(tier)
            tier_title = tier.capitalize()

            out.write(f"## {tier_title} Tier ({len(verbs)} verbs)\n\n")

            for verb in verbs:
                verb_data = get_verb(verb)
                generate_verb_entry(verb, verb_data, out)

    print("Generated: cheatsheet_verbs.qmd")


if __name__ == "__main__":
    main()
