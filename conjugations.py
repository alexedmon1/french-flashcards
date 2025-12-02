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
    "boire":     ["bois", "bois", "boit", "buvons", "buvez", "boivent"],
    "écrire":    ["écris", "écris", "écrit", "écrivons", "écrivez", "écrivent"],
    "lire":      ["lis", "lis", "lit", "lisons", "lisez", "lisent"],
    "partir":    ["pars", "pars", "part", "partons", "partez", "partent"],
    "dormir":    ["dors", "dors", "dort", "dormons", "dormez", "dorment"],
    "ouvrir":    ["ouvre", "ouvres", "ouvre", "ouvrons", "ouvrez", "ouvrent"],
    "recevoir":  ["reçois", "reçois", "reçoit", "recevons", "recevez", "reçoivent"],
    "montrer":   ["montre", "montres", "montre", "montrons", "montrez", "montrent"],
    "écouter":   ["écoute", "écoutes", "écoute", "écoutons", "écoutez", "écoutent"],
    "entendre":  ["entends", "entends", "entend", "entendons", "entendez", "entendent"],
    "attendre":  ["attends", "attends", "attend", "attendons", "attendez", "attendent"],
    "dépenser":  ["dépense", "dépenses", "dépense", "dépensons", "dépensez", "dépensent"],
    "s'asseoir": ["m'assieds", "t'assieds", "s'assied", "nous asseyons", "vous asseyez", "s'asseyent"],
    "monter":    ["monte", "montes", "monte", "montons", "montez", "montrent"],
    "dessiner":  ["dessine", "dessines", "dessine", "dessinons", "dessinez", "dessinent"],
    "voler":     ["vole", "voles", "vole", "volons", "volez", "volent"],
    "raconter":  ["raconte", "racontes", "raconte", "racontons", "racontez", "racontent"],
    "quitter":   ["quitte", "quittes", "quitte", "quittons", "quittez", "quittent"],
    "se sentir": ["me sens", "te sens", "se sent", "nous sentons", "vous sentez", "se sentent"],
    "garder":    ["garde", "gardes", "garde", "gardons", "gardez", "gardent"],
    "rencontrer":["rencontre", "rencontres", "rencontre", "rencontrons", "rencontrez", "rencontrent"],
    "obtenir":   ["obtiens", "obtiens", "obtient", "obtenons", "obtenez", "obtiennent"],
    "sembler":   ["semble", "sembles", "semble", "semblons", "semblez", "semblent"],
    "utiliser":  ["utilise", "utilises", "utilise", "utilisons", "utilisez", "utilisent"],
    "travailler":["travaille", "travailles", "travaille", "travaillons", "travaillez", "travaillent"],
    "couper":    ["coupe", "coupes", "coupe", "coupons", "coupez", "coupent"],
    "cuisiner":  ["cuisine", "cuisines", "cuisine", "cuisinons", "cuisinez", "cuisinent"],
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
    "boire":     ["boirai", "boiras", "boira", "boirons", "boirez", "boiront"],
    "écrire":    ["écrirai", "écriras", "écrira", "écrirons", "écrirez", "écriront"],
    "lire":      ["lirai", "liras", "lira", "lirons", "lirez", "liront"],
    "partir":    ["partirai", "partiras", "partira", "partirons", "partirez", "partiront"],
    "dormir":    ["dormirai", "dormiras", "dormira", "dormirons", "dormirez", "dormiront"],
    "ouvrir":    ["ouvrirai", "ouvriras", "ouvrira", "ouvrirons", "ouvrirez", "ouvriront"],
    "recevoir":  ["recevrai", "recevras", "recevra", "recevrons", "recevrez", "recevront"],
    "montrer":   ["montrerai", "montreras", "montrera", "montrerons", "montrerez", "montreront"],
    "écouter":   ["écouterai", "écouteras", "écoutera", "écouterons", "écouterez", "écouteront"],
    "entendre":  ["entendrai", "entendras", "entendra", "entendrons", "entendrez", "entendront"],
    "attendre":  ["attendrai", "attendras", "attendra", "attendrons", "attendrez", "attendront"],
    "dépenser":  ["dépenserai", "dépenseras", "dépensera", "dépenserons", "dépenserez", "dépenseront"],
    "s'asseoir": ["m'assiérai", "t'assiéras", "s'assiéra", "nous assiérons", "vous assiérez", "s'assiéront"],
    "monter":    ["monterai", "monteras", "montera", "monterons", "monterez", "monteront"],
    "dessiner":  ["dessinerai", "dessineras", "dessinera", "dessinerons", "dessinerez", "dessineront"],
    "voler":     ["volerai", "voleras", "volera", "volerons", "volerez", "voleront"],
    "raconter":  ["raconterai", "raconteras", "racontera", "raconterons", "raconterez", "raconteront"],
    "quitter":   ["quitterai", "quitteras", "quittera", "quitterons", "quitterez", "quitteront"],
    "se sentir": ["me sentirai", "te sentiras", "se sentira", "nous sentirons", "vous sentirez", "se sentiront"],
    "garder":    ["garderai", "garderas", "gardera", "garderons", "garderez", "garderont"],
    "rencontrer":["rencontrerai", "rencontreras", "rencontrera", "rencontrerons", "rencontrerez", "rencontreront"],
    "obtenir":   ["obtiendrai", "obtiendras", "obtiendra", "obtiendrons", "obtiendrez", "obtiendront"],
    "sembler":   ["semblerai", "sembleras", "semblera", "semblerons", "semblerez", "sembleront"],
    "utiliser":  ["utiliserai", "utiliseras", "utilisera", "utiliserons", "utiliserez", "utiliseront"],
    "travailler":["travaillerai", "travailleras", "travaillera", "travaillerons", "travaillerez", "travailleront"],
    "couper":    ["couperai", "couperas", "coupera", "couperons", "couperez", "couperont"],
    "cuisiner":  ["cuisinerai", "cuisineras", "cuisinera", "cuisinerons", "cuisinerez", "cuisineront"],
}

PAST_COMPOSE = {
    "être":      ("être",   ["été",     "été",     "été",     "été",     "été",     "été"]),
    "avoir":     ("avoir",  ["eu",      "eu",      "eu",      "eu",      "eu",      "eu"]),
    "faire":     ("avoir",  ["fait",    "fait",    "fait",    "fait",    "fait",    "fait"]),
    "dire":      ("avoir",  ["dit",     "dit",     "dit",     "dit",     "dit",     "dit"]),
    "aller":     ("être",   ["allé",    "allé",    "allé",    "allés",   "allés",   "allés"]),
    "voir":      ("avoir",  ["vu",      "vu",      "vu",      "vu",      "vu",      "vu"]),
    "savoir":    ("avoir",  ["su",      "su",      "su",      "su",      "su",      "su"]),
    "pouvoir":   ("avoir",  ["pu",      "pu",      "pu",      "pu",      "pu",      "pu"]),
    "vouloir":   ("avoir",  ["voulu",   "voulu",   "voulu",   "voulu",   "voulu",   "voulu"]),
    "venir":     ("être",   ["venu",    "venu",    "venu",    "venus",   "venus",   "venus"]),
    "devoir":    ("avoir",  ["dû",      "dû",      "dû",      "dû",      "dû",      "dû"]),
    "prendre":   ("avoir",  ["pris",    "pris",    "pris",    "pris",    "pris",    "pris"]),
    "donner":    ("avoir",  ["donné",   "donné",   "donné",   "donné",   "donné",   "donné"]),
    "trouver":   ("avoir",  ["trouvé",  "trouvé",  "trouvé",  "trouvé",  "trouvé",  "trouvé"]),
    "penser":    ("avoir",  ["pensé",   "pensé",   "pensé",   "pensé",   "pensé",   "pensé"]),
    "parler":    ("avoir",  ["parlé",   "parlé",   "parlé",   "parlé",   "parlé",   "parlé"]),
    "mettre":    ("avoir",  ["mis",     "mis",     "mis",     "mis",     "mis",     "mis"]),
    "aimer":     ("avoir",  ["aimé",    "aimé",    "aimé",    "aimé",    "aimé",    "aimé"]),
    "passer":    ("avoir",  ["passé",   "passé",   "passé",   "passé",   "passé",   "passé"]),
    "demander":  ("avoir",  ["demandé", "demandé", "demandé", "demandé", "demandé", "demandé"]),
    "croire":    ("avoir",  ["cru",     "cru",     "cru",     "cru",     "cru",     "cru"]),
    "laisser":   ("avoir",  ["laissé",  "laissé",  "laissé",  "laissé",  "laissé",  "laissé"]),
    "porter":    ("avoir",  ["porté",   "porté",   "porté",   "porté",   "porté",   "porté"]),
    "tenir":     ("avoir",  ["tenu",    "tenu",    "tenu",    "tenu",    "tenu",    "tenu"]),
    "appeler":   ("avoir",  ["appelé",  "appelé",  "appelé",  "appelé",  "appelé",  "appelé"]),
    "rester":    ("être",   ["resté",   "resté",   "resté",   "restés",  "restés",  "restés"]),
    "sortir":    ("être",   ["sorti",   "sorti",   "sorti",   "sortis",  "sortis",  "sortis"]),
    "vivre":     ("avoir",  ["vécu",    "vécu",    "vécu",    "vécu",    "vécu",    "vécu"]),
    "tomber":    ("être",   ["tombé",   "tombé",   "tombé",   "tombés",  "tombés",  "tombés"]),
    "connaître": ("avoir",  ["connu",   "connu",   "connu",   "connu",   "connu",   "connu"]),
    "finir":     ("avoir",  ["fini",    "fini",    "fini",    "fini",    "fini",    "fini"]),
    "choisir":   ("avoir",  ["choisi",  "choisi",  "choisi",  "choisi",  "choisi",  "choisi"]),
    "réussir":   ("avoir",  ["réussi",  "réussi",  "réussi",  "réussi",  "réussi",  "réussi"]),
    "remplir":   ("avoir",  ["rempli",  "rempli",  "rempli",  "rempli",  "rempli",  "rempli"]),
    "réfléchir": ("avoir",  ["réfléchi","réfléchi","réfléchi","réfléchi","réfléchi","réfléchi"]),
    "obéir":     ("avoir",  ["obéi",    "obéi",    "obéi",    "obéi",    "obéi",    "obéi"]),
    "grandir":   ("avoir",  ["grandi",  "grandi",  "grandi",  "grandi",  "grandi",  "grandi"]),
    "applaudir": ("avoir",  ["applaudi","applaudi","applaudi","applaudi","applaudi","applaudi"]),
    "établir":   ("avoir",  ["établi",  "établi",  "établi",  "établi",  "établi",  "établi"]),
    "bâtir":     ("avoir",  ["bâti",    "bâti",    "bâti",    "bâti",    "bâti",    "bâti"]),
    "agir":      ("avoir",  ["agi",     "agi",     "agi",     "agi",     "agi",     "agi"]),
    "boire":     ("avoir",  ["bu",      "bu",      "bu",      "bu",      "bu",      "bu"]),
    "écrire":    ("avoir",  ["écrit",   "écrit",   "écrit",   "écrit",   "écrit",   "écrit"]),
    "lire":      ("avoir",  ["lu",      "lu",      "lu",      "lu",      "lu",      "lu"]),
    "partir":    ("être",   ["parti",   "parti",   "parti",   "partis",  "partis",  "partis"]),
    "dormir":    ("avoir",  ["dormi",   "dormi",   "dormi",   "dormi",   "dormi",   "dormi"]),
    "ouvrir":    ("avoir",  ["ouvert",  "ouvert",  "ouvert",  "ouvert",  "ouvert",  "ouvert"]),
    "recevoir":  ("avoir",  ["reçu",    "reçu",    "reçu",    "reçu",    "reçu",    "reçu"]),
    "montrer":   ("avoir",  ["montré",  "montré",  "montré",  "montré",  "montré",  "montré"]),
    "écouter":   ("avoir",  ["écouté",  "écouté",  "écouté",  "écouté",  "écouté",  "écouté"]),
    "entendre":  ("avoir",  ["entendu", "entendu", "entendu", "entendu", "entendu", "entendu"]),
    "attendre":  ("avoir",  ["attendu", "attendu", "attendu", "attendu", "attendu", "attendu"]),
    "dépenser":  ("avoir",  ["dépensé", "dépensé", "dépensé", "dépensé", "dépensé", "dépensé"]),
    "s'asseoir": ("être",   ["assis",   "assis",   "assis",   "assis",   "assis",   "assis"]),
    "monter":    ("être",   ["monté",   "monté",   "monté",   "montés",  "montés",  "montés"]),
    "dessiner":  ("avoir",  ["dessiné", "dessiné", "dessiné", "dessiné", "dessiné", "dessiné"]),
    "voler":     ("avoir",  ["volé",    "volé",    "volé",    "volé",    "volé",    "volé"]),
    "raconter":  ("avoir",  ["raconté", "raconté", "raconté", "raconté", "raconté", "raconté"]),
    "quitter":   ("avoir",  ["quitté",  "quitté",  "quitté",  "quitté",  "quitté",  "quitté"]),
    "se sentir": ("être",   ["senti",   "senti",   "senti",   "sentis",  "sentis",  "sentis"]),
    "garder":    ("avoir",  ["gardé",   "gardé",   "gardé",   "gardé",   "gardé",   "gardé"]),
    "rencontrer":("avoir",  ["rencontré","rencontré","rencontré","rencontré","rencontré","rencontré"]),
    "obtenir":   ("avoir",  ["obtenu",  "obtenu",  "obtenu",  "obtenu",  "obtenu",  "obtenu"]),
    "sembler":   ("avoir",  ["semblé",  "semblé",  "semblé",  "semblé",  "semblé",  "semblé"]),
    "utiliser":  ("avoir",  ["utilisé", "utilisé", "utilisé", "utilisé", "utilisé", "utilisé"]),
    "travailler":("avoir",  ["travaillé","travaillé","travaillé","travaillé","travaillé","travaillé"]),
    "couper":    ("avoir",  ["coupé",   "coupé",   "coupé",   "coupé",   "coupé",   "coupé"]),
    "cuisiner":  ("avoir",  ["cuisiné", "cuisiné", "cuisiné", "cuisiné", "cuisiné", "cuisiné"]),
}

PRONOUNS = ["je", "tu", "il/elle/on", "nous", "vous", "ils/elles"]

# Pronoun variations with gender - each can be randomly selected
PRONOUN_VARIATIONS = [
    ["je"],                           # je (no gender variation for 1st person singular)
    ["tu"],                           # tu (no gender variation for 2nd person singular)
    ["il", "elle", "on"],             # 3rd singular: masculine, feminine, or neutral
    ["nous"],                         # nous (no variation for 1st person plural)
    ["vous"],                         # vous (no variation for 2nd person plural)
    ["ils", "elles"],                 # 3rd plural: masculine or feminine
]

# Agreement endings for être verbs based on pronoun choice
# Format: {pronoun: (ending_singular, ending_plural_nous_vous, ending_plural_ils)}
ETRE_AGREEMENTS = {
    "je":    ("é",   "és",  "és"),   # default masculine
    "tu":    ("é",   "és",  "és"),   # default masculine
    "il":    ("é",   "és",  "és"),   # masculine
    "elle":  ("ée",  "ées", "ées"),  # feminine
    "on":    ("é",   "és",  "és"),   # default masculine (on = nous)
    "nous":  ("és",  "és",  "és"),   # masculine plural
    "vous":  ("és",  "és",  "és"),   # masculine plural
    "ils":   ("és",  "és",  "és"),   # masculine plural
    "elles": ("ées", "ées", "ées"),  # feminine plural
}

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
    "boire":     "to drink",
    "écrire":    "to write",
    "lire":      "to read",
    "partir":    "to leave / to depart",
    "dormir":    "to sleep",
    "ouvrir":    "to open",
    "recevoir":  "to receive",
    "montrer":   "to show",
    "écouter":   "to listen (to)",
    "entendre":  "to hear",
    "attendre":  "to wait (for)",
    "dépenser":  "to spend (money)",
    "s'asseoir": "to sit (down)",
    "monter":    "to go up / to climb",
    "dessiner":  "to draw",
    "voler":     "to fly / to steal",
    "raconter":  "to tell (a story)",
    "quitter":   "to leave / to quit",
    "se sentir": "to feel",
    "garder":    "to keep / to guard",
    "rencontrer":"to meet",
    "obtenir":   "to obtain / to get",
    "sembler":   "to seem",
    "utiliser":  "to use",
    "travailler":"to work",
    "couper":    "to cut",
    "cuisiner":  "to cook",
}

VERB_TYPES = {
    "regular_er": ["donner", "trouver", "penser", "parler", "aimer",
                   "passer", "demander", "laisser", "porter", "rester", "tomber",
                   "montrer", "écouter", "dépenser", "monter", "dessiner", "voler",
                   "raconter", "quitter", "garder", "rencontrer", "sembler", "utiliser",
                   "travailler", "couper", "cuisiner"],
    "regular_ir": ["finir", "choisir", "réussir", "remplir", "réfléchir",
                   "obéir", "grandir", "applaudir", "établir", "bâtir", "agir"],
    "irregular": ["être", "avoir", "faire", "dire", "aller", "voir", "savoir",
                  "pouvoir", "vouloir", "venir", "devoir", "prendre", "mettre",
                  "croire", "tenir", "appeler", "sortir", "vivre", "connaître",
                  "boire", "écrire", "lire", "partir", "dormir", "ouvrir", "recevoir",
                  "entendre", "attendre", "s'asseoir", "se sentir", "obtenir"],
}

# ----------------------------------------------------------------------
# 2️⃣  Helpers
# ----------------------------------------------------------------------
def get_participle_with_agreement(base_participle: str, pronoun: str) -> str:
    """Apply agreement to past participle based on pronoun (for être verbs only)."""
    # Get the root of the participle (remove existing ending)
    # Check longer endings first
    if base_participle.endswith("és"):
        root = base_participle[:-2]
        base_ending = "é"
    elif base_participle.endswith("is"):
        root = base_participle[:-2]
        base_ending = "i"
    elif base_participle.endswith("é"):
        root = base_participle[:-1]
        base_ending = "é"
    elif base_participle.endswith("i"):
        root = base_participle[:-1]
        base_ending = "i"
    else:
        return base_participle  # Irregular, keep as is

    # Apply correct ending based on pronoun
    if base_ending == "é":
        # Participles ending in -é (allé, resté, tombé, etc.)
        if pronoun == "elle":
            return root + "ée"
        elif pronoun == "elles":
            return root + "ées"
        elif pronoun in ["nous", "vous", "ils"]:
            return root + "és"
        else:  # je, tu, il, on (masculine singular)
            return root + "é"
    else:  # base_ending == "i"
        # Participles ending in -i (sorti, parti)
        if pronoun == "elle":
            return root + "ie"
        elif pronoun == "elles":
            return root + "ies"
        elif pronoun in ["nous", "vous", "ils"]:
            return root + "is"
        else:  # je, tu, il, on (masculine singular)
            return root + "i"


def get_table(infinitive: str, tense: str):
    # Randomly select pronoun variations for this round
    selected_pronouns = [random.choice(variations) for variations in PRONOUN_VARIATIONS]

    if tense == "present":
        return selected_pronouns, PRESENT[infinitive]
    if tense == "future":
        return selected_pronouns, FUTURE[infinitive]

    # passé composé
    aux, part_list = PAST_COMPOSE[infinitive]
    aux_forms = PRESENT[aux]  # auxiliary conjugated in présent

    # If using avoir, no agreement needed
    if aux == "avoir":
        full = [f"{aux_forms[i]} {part_list[i]}" for i in range(6)]
    else:  # être - apply gender agreement
        full = []
        for i, pronoun in enumerate(selected_pronouns):
            # Get base participle and apply agreement
            participle = get_participle_with_agreement(part_list[i], pronoun)
            full.append(f"{aux_forms[i]} {participle}")

    return selected_pronouns, full


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
    print("  1 – Regular -ER verbs (26 verbs)")
    print("  2 – Regular -IR verbs (11 verbs)")
    print("  3 – Irregular verbs (30 verbs)")
    print("  4 – All verbs (67 verbs)")
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


def normalize_input(text: str) -> str:
    """Clean up input text by removing surrogate characters and normalizing."""
    # Remove surrogate characters that can appear from backspacing
    cleaned = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    return cleaned.strip()


def ask_one_verb(infinitive: str, tense: str):
    pronouns, correct = get_table(infinitive, tense)
    translation = VERB_TRANSLATIONS.get(infinitive, "")
    print(f"\nConjuguez le verbe « {infinitive} » ({translation}) au {tense}:")
    answers = []
    for p in pronouns:
        ans = input(f"{p} ... ").strip()
        ans = normalize_input(ans)
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