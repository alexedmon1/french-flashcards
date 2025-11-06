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
    "être":      ["suis", "es", "est", "sommes", "êtes", "sont"],
    "avoir":     ["ai", "as", "a", "avons", "avez", "ont"],
    "faire":     ["fais", "fais", "fait", "faisons", "faites", "font"],
    "dire":      ["dis", "dis", "dit", "disons", "dites", "disent"],
    "aller":     ["vais", "vas", "va", "allons", "allez", "vont"],
    "voir":      ["vois", "vois", "voit", "voyons", "voyez", "voient"],
    "savoir":    ["sais", "sais", "sait", "savons", "savez", "savent"],
    "pouvoir":   ["peux", "peux", "peut", "pouvons", "pouvez", "peuvent"],
    "vouloir":   ["veux", "veux", "veut", "voulons", "voulez", "veulent"],
    "venir":     ["viens", "viens", "vient", "venons", "venez", "viennent"],
    "devoir":    ["dois", "dois", "doit", "devons", "devez", "doivent"],
    "prendre":   ["prends", "prends", "prend", "prenons", "prenez", "prennent"],
    "donner":    ["donne", "donnes", "donne", "donnons", "donnez", "donnent"],
    "trouver":   ["trouve", "trouves", "trouve", "trouvons", "trouvez", "trouvent"],
    "penser":    ["pense", "penses", "pense", "pensons", "pensez", "pensent"],
    "parler":    ["parle", "parles", "parle", "parlons", "parlez", "parlent"],
    "mettre":    ["mets", "mets", "met", "mettons", "mettez", "mettent"],
    "aimer":     ["aime", "aimes", "aime", "aimons", "aimez", "aiment"],
    "passer":    ["passe", "passes", "passe", "passons", "passez", "passent"],
    "demander":  ["demande", "demandes", "demande", "demandons", "demandez", "demandent"],
    "croire":    ["crois", "crois", "croit", "croyons", "croyez", "croient"],
    "laisser":   ["laisse", "laisses", "laisse", "laissons", "laissez", "laissent"],
    "porter":    ["porte", "portes", "porte", "portons", "portez", "portent"],
    "tenir":     ["tiens", "tiens", "tient", "tenons", "tenez", "tiennent"],
    "appeler":   ["appelle", "appelles", "appelle", "appelons", "appelez", "appellent"],
    "rester":    ["reste", "restes", "reste", "restons", "restez", "restent"],
    "sortir":    ["sors", "sors", "sort", "sortons", "sortez", "sortent"],
    "vivre":     ["vis", "vis", "vit", "vivons", "vivez", "vivent"],
    "tomber":    ["tombe", "tombes", "tombe", "tombons", "tombez", "tombent"],
    "connaître": ["connais", "connais", "connait", "connaissons", "connaissez", "connaissent"],
    "finir":     ["finis", "finis", "finit", "finissons", "finissez", "finissent"],
    "choisir":   ["choisis", "choisis", "choisit", "choisissons", "choisissez", "choisissent"],
    "réussir":   ["réussis", "réussis", "réussit", "réussissons", "réussissez", "réussissent"],
    "remplir":   ["remplis", "remplis", "remplit", "remplissons", "remplissez", "remplissent"],
    "réfléchir": ["réfléchis", "réfléchis", "réfléchit", "réfléchissons", "réfléchissez", "réfléchissent"],
    "obéir":     ["obéis", "obéis", "obéit", "obéissons", "obéissez", "obéissent"],
    "grandir":   ["grandis", "grandis", "grandit", "grandissons", "grandissez", "grandissent"],
    "applaudir": ["applaudis", "applaudis", "applaudit", "applaudissons", "applaudissez", "applaudissent"],
    "établir":   ["établis", "établis", "établit", "établissons", "établissez", "établissent"],
    "bâtir":     ["bâtis", "bâtis", "bâtit", "bâtissons", "bâtissez", "bâtissent"],
    "agir":      ["agis", "agis", "agit", "agissons", "agissez", "agissent"],
}

FUTURE = {
    "être":      ["serai", "seras", "sera", "serons", "serez", "seront"],
    "avoir":     ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
    "faire":     ["ferai", "feras", "fera", "ferons", "ferez", "feront"],
    "dire":      ["dirai", "diras", "dira", "dirons", "direz", "diront"],
    "aller":     ["irai", "iras", "ira", "irons", "irez", "iront"],
    "voir":      ["verrai", "verras", "verra", "verrons", "verrez", "verront"],
    "savoir":    ["saurai", "sauras", "saura", "saurons", "saurez", "sauront"],
    "pouvoir":   ["pourrai", "pourras", "pourra", "pourrons", "pourrez", "pourront"],
    "vouloir":   ["voudrai", "voudras", "voudra", "voudrons", "voudrez", "voudront"],
    "venir":     ["viendrai", "viendras", "viendra", "viendrons", "viendrez", "viendront"],
    "devoir":    ["devrai", "devras", "devra", "devrons", "devrez", "devront"],
    "prendre":   ["prendrai", "prendras", "prendra", "prendrons", "prendrez", "prendront"],
    "donner":    ["donnerai", "donneras", "donnera", "donnerons", "donnerez", "donneront"],
    "trouver":   ["trouverai", "trouveras", "trouvera", "trouverons", "trouverez", "trouveront"],
    "penser":    ["penserai", "penseras", "pensera", "penserons", "penserez", "penseront"],
    "parler":    ["parlerai", "parleras", "parlera", "parlerons", "parlerez", "parleront"],
    "mettre":    ["mettrai", "mettras", "mettra", "mettrons", "mettrez", "mettront"],
    "aimer":     ["aimerai", "aimeras", "aimera", "aimerons", "aimerez", "aimeront"],
    "passer":    ["passerai", "passeras", "passera", "passerons", "passerez", "passeront"],
    "demander":  ["demanderai", "demanderas", "demandera", "demanderons", "demanderez", "demanderont"],
    "croire":    ["croirai", "croiras", "croira", "croirons", "croirez", "croiront"],
    "laisser":   ["laisserai", "laisseras", "laissera", "laisserons", "laisserez", "laisseront"],
    "porter":    ["porterai", "porteras", "portera", "porterons", "porterez", "porteront"],
    "tenir":     ["tiendrai", "tiendras", "tiendra", "tiendrons", "tiendrez", "tiendront"],
    "appeler":   ["appellerai", "appelleras", "appellera", "appellerons", "appellerez", "appelleront"],
    "rester":    ["resterai", "resteras", "restera", "resterons", "resterez", "resteront"],
    "sortir":    ["sortirai", "sortiras", "sortira", "sortirons", "sortirez", "sortiront"],
    "vivre":     ["vivrai", "vivras", "vivra", "vivrons", "vivrez", "vivront"],
    "tomber":    ["tomberai", "tomberas", "tombera", "tomberons", "tomberez", "tomberont"],
    "connaître": ["connaîtrai", "connaîtras", "connaîtra", "connaîtrons", "connaîtrez", "connaîtront"],
    "finir":     ["finirai", "finiras", "finira", "finirons", "finirez", "finiront"],
    "choisir":   ["choisirai", "choisiras", "choisira", "choisirons", "choisirez", "choisiront"],
    "réussir":   ["réussirai", "réussiras", "réussira", "réussirons", "réussirez", "réussiront"],
    "remplir":   ["remplirai", "rempliras", "remplira", "remplirons", "remplirez", "rempliront"],
    "réfléchir": ["réfléchirai", "réfléchiras", "réfléchira", "réfléchirons", "réfléchirez", "réfléchiront"],
    "obéir":     ["obéirai", "obéiras", "obéira", "obéirons", "obéirez", "obéiront"],
    "grandir":   ["grandirai", "grandiras", "grandira", "grandirons", "grandirez", "grandiront"],
    "applaudir": ["applaudirai", "applaudiras", "applaudira", "applaudirons", "applaudirez", "applaudiront"],
    "établir":   ["établirai", "établiras", "établira", "établirons", "établirez", "établiront"],
    "bâtir":     ["bâtirai", "bâtiras", "bâtira", "bâtirons", "bâtirez", "bâtiront"],
    "agir":      ["agirai", "agiras", "agira", "agirons", "agirez", "agiront"],
}

PAST_COMPOSE = {
    "être":      ("être",   ["été",     "été",     "été",     "été",     "été",     "été"]),
    "avoir":     ("avoir",  ["eu",      "eu",      "eu",      "eu",      "eu",      "eu"]),
    "faire":     ("avoir",  ["fait",    "fait",    "fait",    "faits",   "faits",   "faits"]),
    "dire":      ("avoir",  ["dit",     "dit",     "dit",     "dits",    "dits",    "dits"]),
    "aller":     ("être",   ["allé",    "allé",    "allé",    "allés",   "allés",   "allés"]),
    "voir":      ("avoir",  ["vu",      "vu",      "vu",      "vus",     "vus",     "vus"]),
    "savoir":    ("avoir",  ["su",      "su",      "su",      "sus",     "sus",     "sus"]),
    "pouvoir":   ("avoir",  ["pu",      "pu",      "pu",      "pus",     "pus",     "pus"]),
    "vouloir":   ("avoir",  ["voulu",   "voulu",   "voulu",   "voulus",  "voulus",  "voulus"]),
    "venir":     ("être",   ["venu",    "venu",    "venu",    "venus",   "venus",   "venus"]),
    "devoir":    ("avoir",  ["dû",      "dû",      "dû",      "dûs",     "dûs",     "dûs"]),
    "prendre":   ("avoir",  ["pris",    "pris",    "pris",    "pris",    "pris",    "pris"]),
    "donner":    ("avoir",  ["donné",   "donné",   "donné",   "donnés",  "donnés",  "donnés"]),
    "trouver":   ("avoir",  ["trouvé",  "trouvé",  "trouvé",  "trouvés", "trouvés", "trouvés"]),
    "penser":    ("avoir",  ["pensé",   "pensé",   "pensé",   "pensés",  "pensés",  "pensés"]),
    "parler":    ("avoir",  ["parlé",   "parlé",   "parlé",   "parlés",  "parlés",  "parlés"]),
    "mettre":    ("avoir",  ["mis",     "mis",     "mis",     "mis",     "mis",     "mis"]),
    "aimer":     ("avoir",  ["aimé",    "aimé",    "aimé",    "aimés",   "aimés",   "aimés"]),
    "passer":    ("avoir",  ["passé",   "passé",   "passé",   "passés",  "passés",  "passés"]),
    "demander":  ("avoir",  ["demandé", "demandé", "demandé", "demandés","demandés","demandés"]),
    "croire":    ("avoir",  ["cru",     "cru",     "cru",     "crus",    "crus",    "crus"]),
    "laisser":   ("avoir",  ["laissé",  "laissé",  "laissé",  "laissés", "laissés", "laissés"]),
    "porter":    ("avoir",  ["porté",   "porté",   "porté",   "portés",  "portés",  "portés"]),
    "tenir":     ("avoir",  ["tenu",    "tenu",    "tenu",    "tenus",   "tenus",   "tenus"]),
    "appeler":   ("avoir",  ["appelé",  "appelé",  "appelé",  "appelés", "appelés", "appelés"]),
    "rester":    ("être",   ["resté",   "resté",   "resté",   "restés",  "restés",  "restés"]),
    "sortir":    ("être",   ["sorti",   "sorti",   "sorti",   "sortis",  "sortis",  "sortis"]),
    "vivre":     ("avoir",  ["vécu",    "vécu",    "vécu",    "vécus",   "vécus",   "vécus"]),
    "tomber":    ("être",   ["tombé",   "tombé",   "tombé",   "tombés",  "tombés",  "tombés"]),
    "connaître": ("avoir",  ["connu",   "connu",   "connu",   "connus",  "connus",  "connus"]),
    "finir":     ("avoir",  ["fini",    "fini",    "fini",    "finis",   "finis",   "finis"]),
    "choisir":   ("avoir",  ["choisi",  "choisi",  "choisi",  "choisis", "choisis", "choisis"]),
    "réussir":   ("avoir",  ["réussi",  "réussi",  "réussi",  "réussis", "réussis", "réussis"]),
    "remplir":   ("avoir",  ["rempli",  "rempli",  "rempli",  "remplis", "remplis", "remplis"]),
    "réfléchir": ("avoir",  ["réfléchi","réfléchi","réfléchi","réfléchis","réfléchis","réfléchis"]),
    "obéir":     ("avoir",  ["obéi",    "obéi",    "obéi",    "obéis",   "obéis",   "obéis"]),
    "grandir":   ("avoir",  ["grandi",  "grandi",  "grandi",  "grandis", "grandis", "grandis"]),
    "applaudir": ("avoir",  ["applaudi","applaudi","applaudi","applaudis","applaudis","applaudis"]),
    "établir":   ("avoir",  ["établi",  "établi",  "établi",  "établis", "établis", "établis"]),
    "bâtir":     ("avoir",  ["bâti",    "bâti",    "bâti",    "bâtis",   "bâtis",   "bâtis"]),
    "agir":      ("avoir",  ["agi",     "agi",     "agi",     "agis",    "agis",    "agis"]),
}

PRONOUNS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

VERB_TRANSLATIONS = {
    "être":      "to be",
    "avoir":     "to have",
    "faire":     "to do / to make",
    "dire":      "to say / to tell",
    "aller":     "to go",
    "voir":      "to see",
    "savoir":    "to know (facts)",
    "pouvoir":   "to be able to / can",
    "vouloir":   "to want",
    "venir":     "to come",
    "devoir":    "to have to / must",
    "prendre":   "to take",
    "donner":    "to give",
    "trouver":   "to find",
    "penser":    "to think",
    "parler":    "to speak / to talk",
    "mettre":    "to put / to place",
    "aimer":     "to like / to love",
    "passer":    "to pass / to spend (time)",
    "demander":  "to ask",
    "croire":    "to believe",
    "laisser":   "to leave / to let",
    "porter":    "to wear / to carry",
    "tenir":     "to hold",
    "appeler":   "to call",
    "rester":    "to stay / to remain",
    "sortir":    "to go out / to leave",
    "vivre":     "to live",
    "tomber":    "to fall",
    "connaître": "to know (people/places)",
    "finir":     "to finish",
    "choisir":   "to choose",
    "réussir":   "to succeed",
    "remplir":   "to fill",
    "réfléchir": "to reflect / to think",
    "obéir":     "to obey",
    "grandir":   "to grow",
    "applaudir": "to applaud / to clap",
    "établir":   "to establish",
    "bâtir":     "to build",
    "agir":      "to act",
}

VERB_TYPES = {
    "regular_er": ["donner", "trouver", "penser", "parler", "aimer",
                   "passer", "demander", "laisser", "porter", "rester", "tomber"],
    "regular_ir": ["finir", "choisir", "réussir", "remplir", "réfléchir",
                   "obéir", "grandir", "applaudir", "établir", "bâtir", "agir"],
    "irregular": ["être", "avoir", "faire", "dire", "aller", "voir", "savoir",
                  "pouvoir", "vouloir", "venir", "devoir", "prendre", "mettre",
                  "croire", "tenir", "appeler", "sortir", "vivre", "connaître"],
}

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


def choose_verb_type() -> list:
    """Choose which type of verbs to practice. Returns a list of verbs."""
    print("\nQuel type de verbes voulez-vous réviser ?")
    print("  1 – Regular -ER verbs (11 verbs)")
    print("  2 – Regular -IR verbs (11 verbs)")
    print("  3 – Irregular verbs (18 verbs)")
    print("  4 – All verbs (40 verbs)")
    while True:
        c = input("Entrez le numéro (ou q pour quitter) : ").strip().lower()
        if c == "q":
            sys.exit(0)
        if c == "1":
            return VERB_TYPES["regular_er"]
        elif c == "2":
            return VERB_TYPES["regular_ir"]
        elif c == "3":
            return VERB_TYPES["irregular"]
        elif c == "4":
            return list(PRESENT.keys())
        print("Choisissez 1, 2, 3 ou 4.")


def ask_one_verb(infinitive: str, tense: str):
    pronouns, correct = get_table(infinitive, tense)
    translation = VERB_TRANSLATIONS.get(infinitive, "")
    print(f"\nConjuguez le verbe « {infinitive} » ({translation}) au {tense}:")
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

    # Choose verb type once at the start
    verb_list = choose_verb_type()

    while True:
        tense = choose_tense()
        infinitive = random.choice(verb_list)

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