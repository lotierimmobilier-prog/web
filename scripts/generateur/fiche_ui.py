# -*- coding: utf-8 -*-
"""Blocs de présentation d'une fiche d'annonce (style « portail » : mosaïque, infos-clés, atouts, détail du prix, bilan énergie, partenaire).
Fonctions pures : elles reçoivent les données d'une annonce et rendent du HTML ; aucune écriture de fichier."""
import re as _re
from common import e, COLLAB_RAPPEL

NB = " "
PAPERNEST = ("https://app.papernest.com/onboarding?anonymous&x=a45d02d5-18bf-4b8b-a028-baf31f1cb7b7"
             "&y=1bd41d4a-598b-4237-a49f-03d0eaaaaaaa&destination=intro-call-or-app__generic&user.campaign=app_link")


def _ico(path): return f'<svg class="fi" viewBox="0 0 24 24" aria-hidden="true">{path}</svg>'

ICO = {
    "surface": _ico('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>'),
    "pieces": _ico('<path d="M4 20V5h10v15M14 9h6v11M2 20h20M8 10h2M8 14h2"/>'),
    "chambres": _ico('<path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6M3 15h18M6 10V7a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v3"/>'),
    "sdb": _ico('<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4zM6 12V6a2 2 0 0 1 4 0M7 19l-1 2M17 19l1 2"/>'),
    "annee": _ico('<path d="M3 11l9-7 9 7M5 10v10h14V10M10 20v-6h4v6"/>'),
    "etage": _ico('<path d="M4 20h16M6 20V9h12v11M9 9V4h6v5"/>'),
    "terrain": _ico('<path d="M3 17l5-9 4 6 3-4 6 7zM3 21h18"/>'),
    "chauffage": _ico('<path d="M12 3s5 4 5 9a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3 0-5 1-8z"/>'),
    "type": _ico('<path d="M3 21V8l9-5 9 5v13M9 21v-7h6v7"/>'),
    "ok": _ico('<path d="M5 12l4.5 4.5L19 7"/>'),
    "phone": _ico('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>'),
    "plug": _ico('<path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 0 1-10 0zM12 16v5"/>'),
    "photos": _ico('<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M21 16l-5-5-8 8"/>'),
}


def valeurs(blocs):
    """{libellé: valeur} à plat, tous blocs confondus (le premier gagne)."""
    out = {}
    for b in blocs or []:
        for k, v in b["lignes"]:
            out.setdefault(k, v)
    return out


def _num(s):
    m = _re.search(r"\d+(?:[.,]\d+)?", s or "")
    return m.group(0).replace(".", ",") if m else None


# ---------- Informations-clés ----------
def cles_bloc(a, v):
    """Tuiles à icône : surface, pièces, chambres, salles d'eau, terrain, année, étage, chauffage."""
    t = []
    if a.get("surface"): t.append(("surface", f"{a['surface']:g}".replace(".", ",") + f"{NB}m²", "Surface"))
    if v.get("Pièces"): t.append(("pieces", v["Pièces"], "Pièce" + ("s" if _num(v["Pièces"]) not in (None, "1") else "")))
    if a.get("chambres"): t.append(("chambres", str(a["chambres"]), "Chambre" + ("s" if a["chambres"] > 1 else "")))
    sdb = a.get("sdb") or _num(v.get("Salles d'eau")) or _num(v.get("Salles de bain"))
    if sdb: t.append(("sdb", str(sdb), "Salle" + ("s" if str(sdb) != "1" else "") + " d'eau/bain"))
    if v.get("Terrain"): t.append(("terrain", v["Terrain"].replace(" m²", f"{NB}m²"), "Terrain"))
    if v.get("Année de construction"): t.append(("annee", v["Année de construction"], "Construction"))
    if v.get("Étage"): t.append(("etage", v["Étage"], "Étage"))
    if v.get("Chauffage"): t.append(("chauffage", v["Chauffage"], "Chauffage"))
    if not t: return ""
    items = "".join(f'<li>{ICO[i]}<strong>{e(val)}</strong><span>{e(lab)}</span></li>' for i, val, lab in t)
    return f'<section class="ann-card ann-keys" aria-labelledby="ann-h-cles"><h2 id="ann-h-cles">Informations clés</h2><ul class="ann-keys-grid">{items}</ul></section>'


# ---------- Atouts ----------
_ATOUTS = ("Terrasse", "Balcon", "Garage", "Parking", "Boxe", "Cave", "Piscine", "Ascenseur", "Climatisation", "Gardien", "Meublé")

def atouts_bloc(v):
    """Pastilles pour les équipements présents (« Oui ») + cuisine et exposition quand elles sont renseignées."""
    chips = [k for k in _ATOUTS if str(v.get(k, "")).strip().lower() == "oui"]
    extra = []
    if v.get("Cuisine"): extra.append("Cuisine " + v["Cuisine"].lower())
    if v.get("Exposition"): extra.append("Exposition " + v["Exposition"].lower())
    if not chips and not extra: return ""
    items = "".join(f'<li>{ICO["ok"]}{e(c)}</li>' for c in chips + extra)
    return f'<section class="ann-card ann-atouts" aria-labelledby="ann-h-atouts"><h2 id="ann-h-atouts">Les atouts du bien</h2><ul class="ann-chips">{items}</ul></section>'


# ---------- Caractéristiques détaillées (hors prix, hors situation) ----------
def caracteristiques_bloc(blocs):
    sections = ""
    for b in blocs or []:
        if b["titre"] in ("Informations financières", "Situation"): continue
        lignes = [(k, val) for k, val in b["lignes"] if k != "Détails procédures"]
        if not lignes: continue
        dl = "".join(f"<div><dt>{e(k)}</dt><dd>{e(val)}</dd></div>" for k, val in lignes)
        sections += f'<div class="ann-carac-grp"><h3>{e(b["titre"])}</h3><dl>{dl}</dl></div>'
    return f'<section class="ann-card ann-carac" aria-labelledby="ann-h-carac"><h2 id="ann-h-carac">Caractéristiques</h2><div class="ann-carac-grid">{sections}</div></section>' if sections else ""


# ---------- Détail du prix ----------
def prix_bloc(a, v, price, notes):
    loc = a["type"] == "location"
    cartes = [("Loyer" if loc else "Prix", price, "Charges comprises" if loc and any("comprises" in n.lower() for n in notes) else "Frais d'agence inclus" if not loc else "")]
    ordre = ("Loyer charges comprises", "Provisions sur charges", "Forfait de charges", "Dépôt de garantie", "Charge honoraires", "Honoraires", "Montant honoraires",
             "Honoraires état des lieux (TTC, charge locataire)", "Charges annuelles", "Prix hors honoraires", "Charges récupérables", "Modalités de règlement des charges", "Caractère meublé")
    vus = set()
    for k in ordre:
        if v.get(k) and k not in vus:
            vus.add(k)
            val = v[k]
            lab = {"Charge honoraires": "Honoraires à la charge de", "Charges annuelles": "Charges de copropriété", "Honoraires état des lieux (TTC, charge locataire)": "État des lieux (locataire, TTC)"}.get(k, k)
            cartes.append((lab, val, ""))
    items = "".join(f'<li><span>{e(l)}</span><strong{" class=\"long\"" if len(val) > 22 else ""}>{e(val)}</strong>{f"<em>{e(sub)}</em>" if sub else ""}</li>' for l, val, sub in cartes)
    return f'<section class="ann-card ann-prix" aria-labelledby="ann-h-prix"><h2 id="ann-h-prix">Détail du prix</h2><ul class="ann-prix-grid">{items}</ul></section>'


# ---------- Bilan énergie compact ----------
_COULEURS = {"A": "#319834", "B": "#33cc31", "C": "#cbfc34", "D": "#fbfe06", "E": "#fbcc05", "F": "#fc9935", "G": "#fc0205"}

def _frise(titre, classe, valeur, unite):
    cases = "".join(f'<li class="{"is-on" if L == classe else ""}" style="--c:{_COULEURS[L]}">{L}</li>' for L in "ABCDEFG")
    val = f'<span class="ann-nrj-val"><b>{e(str(valeur))}</b> {unite}</span>' if valeur is not None else ""
    return f'<div class="ann-nrj-ligne"><div class="ann-nrj-tt"><span>{titre}</span>{val}</div><ol class="ann-nrj-bar" role="img" aria-label="{e(titre)} : classe {classe}">{cases}</ol></div>'

def bilan_energie(a, detail_html):
    en = a.get("energie") or {}
    dpe, ges = en.get("dpe"), en.get("ges")
    if not dpe and not ges: return ""
    lignes = ""
    if dpe: lignes += _frise("DPE · Consommation d'énergie", dpe["classe"], dpe.get("valeur"), "kWh/m².an")
    if ges: lignes += _frise("GES · Émissions de gaz à effet de serre", ges["classe"], ges.get("valeur"), "kg CO₂/m².an")
    note = ""
    if en.get("depenses_min") is not None and en.get("depenses_max") is not None:
        note = f'<p class="ann-nrj-note">Dépenses annuelles d’énergie estimées : <strong>entre {_fmt(en["depenses_min"])}{NB}€ et {_fmt(en["depenses_max"])}{NB}€</strong> par an.</p>'
    return (f'<section class="ann-card ann-nrj" aria-labelledby="ann-h-nrj"><h2 id="ann-h-nrj">Bilan énergétique</h2>{lignes}{note}'
            f'<details class="ann-det"><summary>Voir le diagnostic complet</summary>{detail_html}</details></section>')

def _fmt(n): return f"{n:,.0f}".replace(",", NB)


# ---------- Partenaire : abonnements du logement ----------
def partenaire_bloc():
    return (f'<aside class="ann-card ann-part" aria-labelledby="ann-h-part">'
            f'<span class="ann-part-ico">{ICO["plug"]}</span>'
            f'<div class="ann-part-txt"><span class="ann-part-tag">Lien partenaire</span><h2 id="ann-h-part">Un nouveau logement, de nouveaux abonnements ?</h2>'
            f'<p>Comparez et souscrivez en quelques minutes les meilleurs prix pour l’énergie, internet ou l’assurance habitation, avec notre partenaire Papernest. Service gratuit, sans engagement de votre part envers LOTIER Immobilier.</p></div>'
            f'<a class="btn btn-navy btn-lg ann-part-btn" href="{e(PAPERNEST)}" target="_blank" rel="sponsored noopener noreferrer">Comparer les offres <span class="sr-only"> (nouvelle fenêtre, site partenaire Papernest)</span></a>'
            f'</aside>')


# ---------- Mosaïque : vignettes latérales ----------
def vignettes(photos, title, p2, max_n=2):
    """Deux vignettes à droite de la photo principale (photos 2 et 3) ; la dernière porte « Voir les N photos »."""
    n = len(photos)
    if n < 3: return ""
    out = ""
    for k in range(1, 1 + max_n):
        dernier = k == max_n
        plus = f'<span class="ann-tile-more">{ICO["photos"]}Voir les {n} photos</span>' if dernier and n > 3 else ""
        out += (f'<button type="button" class="ann-tile" data-gal-goto="{k}" aria-label="Voir la photo {k + 1} sur {n}">'
                f'<img src="{p2}{photos[k]}" alt="" width="480" height="360" loading="lazy" decoding="async">{plus}</button>')
    return f'<div class="ann-tiles">{out}</div>'


# ---------- « Être rappelé » : fenêtre de demande, envoyée à Collab (tâche chez l'agent de l'annonce) ----------
RAPPEL_CONSENTEMENT = ("J’accepte que LOTIER Immobilier utilise ces informations pour me rappeler au sujet de ce bien. "
                       "Elles sont conservées 3 ans au plus ; vous pouvez y accéder, les corriger ou les faire supprimer (voir")

def rappel_bloc(a, agent_prenom, p2, url):
    """La fenêtre (dialog) du formulaire. Sans JavaScript, le bouton qui l'ouvre mène à la page Contact."""
    ag = a.get("agent") or {}
    cible = f" {e(agent_prenom)}" if agent_prenom else " un conseiller"
    donnees = (f'data-endpoint="{e(COLLAB_RAPPEL)}" data-ref="{e(a.get("reference") or "")}" data-titre="{e(a.get("titre") or "")}" '
               f'data-url="{e(url)}" data-agent="{e(ag.get("email") or "")}" data-agent-prenom="{e(agent_prenom or "")}"')
    return (f'<dialog class="rappel" id="rappel" aria-labelledby="rappel-t" {donnees}>'
            f'<form class="rappel-form" method="dialog" novalidate>'
            f'<button type="button" class="rappel-x" data-rappel-close aria-label="Fermer">{_ico(chr(77)+"6 6l12 12M18 6 6 18")}</button>'
            f'<h2 id="rappel-t">Être rappelé{(" par " + e(agent_prenom)) if agent_prenom else ""}</h2>'
            f'<p class="muted">Laissez vos coordonnées : {cible.strip()} vous rappelle rapidement au sujet de ce bien.</p>'
            f'<div class="rappel-grid">'
            f'<label>Prénom<input name="prenom" autocomplete="given-name" required maxlength="60"></label>'
            f'<label>Nom<input name="nom" autocomplete="family-name" required maxlength="80"></label>'
            f'<label>Téléphone<input name="telephone" type="tel" inputmode="tel" autocomplete="tel" required maxlength="30" placeholder="06 12 34 56 78"></label>'
            f'<label>E-mail <span class="muted">(facultatif)</span><input name="email" type="email" autocomplete="email" maxlength="160"></label>'
            f'</div>'
            f'<label class="rappel-msg">Message <span class="muted">(facultatif)</span><textarea name="message" rows="3" maxlength="1500" placeholder="Vos disponibilités, une question sur le bien…"></textarea></label>'
            f'<div class="rappel-piege" aria-hidden="true"><label>Ne pas remplir<input name="site" tabindex="-1" autocomplete="off"></label></div>'
            f'<label class="rappel-ok"><input type="checkbox" name="consentement" required><span>{RAPPEL_CONSENTEMENT} <a class="text-link" href="{p2}lotier-rgpd/">notre politique de protection des données</a>).</span></label>'
            f'<p class="rappel-err" role="alert" hidden></p>'
            f'<div class="rappel-act"><button type="submit" class="btn btn-gold btn-lg">Je souhaite être rappelé</button>'
            f'<a class="btn btn-ghost btn-lg" href="tel:{{PHONE}}">Ou appelez-nous</a></div>'
            f'</form>'
            f'<div class="rappel-fait" hidden><h2>Merci, votre demande est bien reçue.</h2><p>{cible.strip().capitalize() if False else "Votre conseiller"} vous rappelle rapidement.</p>'
            f'<button type="button" class="btn btn-navy btn-lg" data-rappel-close>Fermer</button></div>'
            f'</dialog>')
