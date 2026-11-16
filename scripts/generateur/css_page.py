# -*- coding: utf-8 -*-
"""Feuille de style réduite à ce qu'une page peut utiliser (employée pour l'accueil, la page la plus vue).

Une règle est gardée quand toutes les classes, tous les identifiants et tous les attributs de l'un de ses sélecteurs
apparaissent, en mot entier, dans la page ou dans les scripts qu'elle charge (les scripts ajoutent des classes et du
contenu après coup). Le contenu d'un « :not(...) » ne compte pas : « .a:not(.b) » s'applique même si .b n'existe pas.
L'ordre des règles est conservé ; les @font-face sont tous gardés (une police n'est téléchargée que si elle sert) ;
les @keyframes ne sont gardés que s'ils sont cités par une règle gardée."""
import re

_JETON = re.compile(r"([.#])(-?[A-Za-z_][\w-]*)|\[\s*([A-Za-z_][\w-]*)")


def _blocs(css):
    """Découpe une feuille compactée en blocs de premier niveau : (en-tête, corps)."""
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0: break
        prof, k = 1, j + 1
        while k < n and prof:
            c = css[k]
            if c == "{": prof += 1
            elif c == "}": prof -= 1
            k += 1
        out.append((css[i:j].strip(), css[j + 1:k - 1]))
        i = k
    return out


def _selecteurs(s):
    """Sépare une liste de sélecteurs sur les virgules de premier niveau (pas celles de :is(), :not()…)."""
    out, prof, deb = [], 0, 0
    for i, c in enumerate(s):
        if c in "([": prof += 1
        elif c in ")]": prof -= 1
        elif c == "," and prof == 0:
            out.append(s[deb:i]); deb = i + 1
    out.append(s[deb:])
    return [x.strip() for x in out if x.strip()]


def _sans_not(sel):
    """Retire le contenu des :not(...) (parenthèses imbriquées comprises)."""
    while True:
        i = sel.find(":not(")
        if i < 0: return sel
        prof, k = 1, i + 5
        while k < len(sel) and prof:
            if sel[k] == "(": prof += 1
            elif sel[k] == ")": prof -= 1
            k += 1
        sel = sel[:i] + sel[k:]


def _peut_servir(sel, mots, prefixes):
    for m in _JETON.finditer(_sans_not(sel)):
        nom = m.group(2) or m.group(3)
        if nom not in mots and not nom.startswith(prefixes): return False
    return True


def _filtre(css, mots, prefixes):
    out = []
    for tete, corps in _blocs(css):
        if tete.startswith("@media") or tete.startswith("@supports"):
            dedans = _filtre(corps, mots, prefixes)
            if dedans: out.append(f"{tete}{{{dedans}}}")
        elif tete.startswith("@"):
            out.append(f"{tete}{{{corps}}}")            # @font-face, @keyframes (triés ensuite)
        else:
            gardes = [s for s in _selecteurs(tete) if _peut_servir(s, mots, prefixes)]
            if gardes: out.append(f"{','.join(gardes)}{{{corps}}}")
    return "".join(out)


def css_pour_page(css, page_html, scripts=""):
    """`css` : feuille compactée complète ; `page_html` : la page ; `scripts` : texte des scripts qu'elle charge."""
    foin = page_html + "\n" + scripts
    mots = set(re.findall(r"-?[A-Za-z_][\w-]*", foin))                    # noms entiers présents dans la page ou les scripts
    # classes fabriquées par un script (« 'cm cm-' + qui ») : tout nom qui commence par ce préfixe est gardé
    prefixes = tuple(sorted({m.group(1) for m in re.finditer(r"([A-Za-z_][\w-]*-)['\"`]\s*\+", scripts)})) or ("\0",)
    reduit = _filtre(css, mots, prefixes)
    # @keyframes non cités par ce qui reste : retirés
    blocs = _blocs(reduit)
    autres = "".join(f"{t}{{{c}}}" for t, c in blocs if not t.startswith("@keyframes"))
    morceaux = []
    for tete, corps in blocs:
        if tete.startswith("@keyframes"):
            nom = tete.split()[1]
            if not re.search(r"(?<![\w-])" + re.escape(nom) + r"(?![\w-])", autres): continue
        morceaux.append(f"{tete}{{{corps}}}")
    return "".join(morceaux) + "\n"
