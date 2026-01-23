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


def latex_escape(text):
    """Escape special LaTeX characters."""
    replacements = [('&', r'\&'), ('#', r'\#'), ('%', r'\%'), ('_', r'\_')]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def generate_verb_entry(verb, verb_data, out):
    """Generate a single verb's conjugation table as raw LaTeX in a minipage."""
    translation = verb_data.get("translation", "")
    verb_type = verb_data.get("type", "")
    auxiliary = verb_data.get("auxiliary", "avoir")
    pp = get_past_participle(verb, verb_data)

    type_short = {"regular_er": "-ER", "regular_ir": "-IR", "irregular": "irreg."}.get(verb_type, verb_type)

    # Get all conjugations
    all_forms = []
    for tense in TENSES:
        _, forms = conjugate(verb, tense, selected_pronouns=STANDARD_PRONOUNS)
        all_forms.append(forms)

    # Wrap in minipage to prevent page breaks
    out.write("\\begin{minipage}{\\linewidth}\n")

    # Header
    out.write(f"\\vspace{{4pt}}\n")
    out.write(f"\\noindent\\textbf{{\\large {latex_escape(verb)}}} "
              f"\\textit{{({latex_escape(translation)})}}\n\n")
    out.write(f"\\noindent Type: {type_short} \\quad Aux: {auxiliary} \\quad P.P.: {latex_escape(pp)}\n\n")

    # Build LaTeX tabular
    out.write("\\begin{tabular}{l|lllllll}\n")
    out.write(f" & {' & '.join(TENSE_HEADERS)} \\\\\n")
    out.write("\\hline\n")

    for i in range(6):
        pronoun = DISPLAY_PRONOUNS[i].replace("/", "/\\hspace{0pt}")
        row_cells = [latex_escape(forms[i]) for forms in all_forms]
        out.write(f"\\textbf{{{pronoun}}} & {' & '.join(row_cells)} \\\\\n")

    out.write("\\end{tabular}\n")
    out.write("\\end{minipage}\n")
    out.write("\\vspace{6pt}\n\n")


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
        \\pagestyle{plain}
        \\setlength{\\parindent}{0pt}
        \\setlength{\\parskip}{3pt}
        \\setlength{\\tabcolsep}{2.5pt}
        \\renewcommand{\\arraystretch}{1.15}
---

""")

        out.write("```{=latex}\n")

        for tier in ["core", "intermediate", "advanced"]:
            verbs = get_verbs_by_tier(tier)
            tier_title = tier.capitalize()

            out.write(f"\\section*{{{tier_title} Tier ({len(verbs)} verbs)}}\n\n")

            for verb in verbs:
                verb_data = get_verb(verb)
                generate_verb_entry(verb, verb_data, out)

        out.write("```\n")

    print("Generated: cheatsheet_verbs.qmd")


if __name__ == "__main__":
    main()
