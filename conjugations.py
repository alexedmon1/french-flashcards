#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 19:17:20 2025

@author: alexdevyn
"""

#!/usr/bin/env python3
import random
import sys

# ----------------------------------------------------------------------
# 1️⃣  Data tables
# ----------------------------------------------------------------------
PRESENT = {
    "être":   ["suis", "es", "est", "sommes", "êtes", "sont"],
    "avoir":  ["ai", "as", "a", "avons", "avez", "ont"],
    "aller":  ["vais", "vas", "va", "allons", "allez", "vont"],
    "faire":  ["fais", "fais", "fait", "faisons", "faites", "font"],
    "parler": ["parle", "parles", "parle", "parlons", "parlez", "parlent"],
    "finir":  ["finis", "finis", "finit", "finissons", "finissez", "finissent"],
    "savoir": ["sais", "sais", "sait", "savons", "savez", "savent"],
    "connaître": ["connais", "connais", "connait", "connaissons", "connaissez",
                  "connaissent"],
    "venir": ["viens", "viens", "vient", "venons", "venez", "viennent"],
    "vouloir": ["veux", "veux", "veut", "voulons", "voulez", "veulent"],
    "pouvoir": ["peux", "peux", "peut", "pouvons", "pouvez", "peuvent"],
    "devoir": ["dois", "dois", "doit", "devons", "devez", "doivent"]
    
}

FUTURE = {
    "être":   ["serai", "seras", "sera", "serons", "serez", "seront"],
    "avoir":  ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
    "aller":  ["irai", "iras", "ira", "irons", "irez", "iront"],
    "faire":  ["ferai", "feras", "fera", "ferons", "ferez", "feront"],
    "parler": ["parlerai", "parleras", "parlera", "parlerons",
               "parlerez", "parleront"],
    "finir":  ["finirai", "finiras", "finira", "finirons",
               "finirez", "finiront"],
}

PAST_COMPOSE = {
    "être":   ("être",   ["été",   "été",   "été",   "été",   "été",   "été"]),
    "avoir":  ("avoir",  ["eu",    "eu",    "eu",    "eu",    "eu",    "eu"]),
    "aller":  ("être",   ["allé",  "allé",  "allé",  "allés", "allés", "allés"]),
    "faire":  ("avoir",  ["fait",  "fait",  "fait",  "faits", "faits", "faits"]),
    "parler": ("avoir",  ["parlé", "parlé", "parlé", "parlés","parlés","parlés"]),
    "finir":  ("avoir",  ["fini",  "fini",  "fini",  "finis", "finis", "finis"]),
}

PRONOUNS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# ----------------------------------------------------------------------
# 2️⃣  Helpers
# ----------------------------------------------------------------------
def get_table(infinitive: str, tense: str):
    if tense == "present":
        return PRONOUNS, PRESENT[infinitive]
    if tense == "future":
        return PRONOUNS, FUTURE[infinitive]

    # passé composé
    aux, part = PAST_COMPOSE[infinitive]
    aux_forms = PRESENT[aux]                     # auxiliary conjugated in présent
    full = [f"{aux_forms[i]} {part[i]}" for i in range(6)]
    return PRONOUNS, full


def choose_tense() -> str:
    print("\nQuel temps voulez‑vous réviser ?")
    print("  1 – Présent")
    print("  2 – Futur simple")
    print("  3 – Passé composé")
    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        if c in {"1", "2", "3"}:
            return {"1": "present", "2": "future", "3": "past"}[c]
        print("Choisissez 1, 2 ou 3.")


def ask_one_verb(infinitive: str, tense: str):
    pronouns, correct = get_table(infinitive, tense)
    print(f"\nConjuguez le verbe « {infinitive} » au {tense}:")
    answers = []
    for p in pronouns:
        ans = input(f"{p} ... ").strip()
        answers.append(ans)

    score = 0
    for i, (u, c) in enumerate(zip(answers, correct)):
        if u.lower() == c.lower():
            print(f"✔ {pronouns[i]} {u}")
            score += 1
        else:
            print(f"✘ {pronouns[i]} {u} → correct: {c}")

    print(f"Score pour ce verbe ({tense}) : {score}/6")
    return score, 6


# ----------------------------------------------------------------------
# 3️⃣  Main loop
# ----------------------------------------------------------------------
def main():
    total_ok = 0
    total_q  = 0

    print("=== Test de conjugaison française (présent, futur, passé) ===")
    print("Tapez 'q' à tout moment pour quitter.\n")

    while True:
        tense = choose_tense()
        infinitive = random.choice(list(PRESENT.keys()))   # same keys across tables

        try:
            ok, qty = ask_one_verb(infinitive, tense)
        except (KeyboardInterrupt, EOFError):
            print("\nInterruption détectée – au revoir !")
            break

        total_ok += ok
        total_q  += qty

        nxt = input("\nUn autre verbe ? (Entrée=oui, q=quitter) ").strip().lower()
        if nxt == "q":
            break

    if total_q:
        pct = (total_ok / total_q) * 100
        print("\n--- Résultat final ---")
        print(f"Points obtenus : {total_ok}/{total_q}")
        print(f"Taux de réussite : {pct:.1f}%")
    else:
        print("\nAucun point enregistré.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Erreur inattendue : {exc}", file=sys.stderr)
        sys.exit(1)