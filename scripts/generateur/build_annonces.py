# -*- coding: utf-8 -*-
"""Page « Nos annonces » : toutes les annonces de data/annonces.json, avec filtres (vente/location, ville)."""
import os, json
from common import *
import fiche_ui as F
from common import _nice_title, _price
prefix = "../"

ann = load_annonces()
os.makedirs(f"{ROOT}/nos-annonces", exist_ok=True)
nb_v = sum(1 for a in ann if a["type"] == "vente"); nb_l = len(ann) - nb_v
import collections as _co
villes = sorted({a["ville"] for a in ann if a["ville"]})
cards = "".join(annonce_card(a, prefix) for a in ann) if ann else '<p class="muted">Aucune annonce publiée pour le moment. <a class="text-link" href="../contact/">Contactez-nous</a> pour connaître nos biens à venir.</p>'
nb_biens = _co.Counter(categorie_bien(a) for a in ann)
nb_deps = _co.Counter(departement(a) for a in ann)
opts_ville = "".join(f'<option value="{e(v)}" data-dep="{e(departement(next(x for x in ann if x["ville"] == v)))}">{e(v)}</option>' for v in villes)
opts_bien = "".join(f'<option value="{k}">{e(lib)} ({nb_biens[k]})</option>' for k, lib in BIENS_LIBELLES.items() if nb_biens.get(k))
opts_dep = "".join(f'<option value="{c}">{e(nom)} ({c}) · {nb_deps[c]}</option>' for c, nom in DEPARTEMENTS.items() if nb_deps.get(c))
body = f'''    <section class="page-hero ann-list-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Nos annonces</span></nav>
        <h1 class="display page-title">Nos annonces, <em class="gold-text">ventes et locations.</em></h1>
        <p class="lead">{nb_v} biens à vendre et {nb_l} à louer autour de Béziers, Narbonne, Carcassonne, Montpellier et Nîmes. Un bien vous intéresse ? Un conseiller vous rappelle.</p>
      </div>
    </section>
    <section class="section container ann-list" aria-label="Annonces" data-annonces>
      <form class="ann-filtres" data-ann-form aria-label="Filtrer les annonces" onsubmit="return false">
        <div class="chip-links" role="group" aria-label="Vente ou location">
          <button type="button" class="chip-link is-on" data-ann-type-btn="" aria-pressed="true">Toutes ({len(ann)})</button>
          <button type="button" class="chip-link" data-ann-type-btn="vente" aria-pressed="false">À vendre ({nb_v})</button>
          <button type="button" class="chip-link" data-ann-type-btn="location" aria-pressed="false">À louer ({nb_l})</button>
        </div>
        <div class="ann-champs">
          <label><span>Type de bien</span><select data-ann-bien><option value="">Tous les biens</option>{opts_bien}</select></label>
          <label><span>Département</span><select data-ann-dep><option value="">Tous les départements</option>{opts_dep}</select></label>
          <label><span>Ville</span><select data-ann-city><option value="">Toutes les villes</option>{opts_ville}</select></label>
          <label><span>Budget min.</span><select data-ann-pmin disabled><option value="">Choisir vente ou location</option></select></label>
          <label><span>Budget max.</span><select data-ann-pmax disabled><option value="">Choisir vente ou location</option></select></label>
          <label><span>Trier par</span><select data-ann-sort><option value="">Sélection LOTIER</option><option value="prix-asc">Prix croissant</option><option value="prix-desc">Prix décroissant</option><option value="surf-desc">Surface décroissante</option></select></label>
        </div>
        <div class="ann-filtres-pied"><p class="muted small" data-ann-count aria-live="polite">{len(ann)} annonces</p><button type="button" class="text-link ann-reset" data-ann-reset hidden>Réinitialiser les filtres</button></div>
      </form>
      <div class="cards" data-ann-grid>{cards}
      </div>
      <p class="muted" data-ann-empty hidden>Aucune annonce ne correspond à ces critères. <button type="button" class="text-link ann-reset" data-ann-reset>Réinitialiser les filtres</button></p>
      <p class="muted small" style="margin-top:24px">Prix en euros. Les honoraires, le DPE et les informations légales figurent sur chaque fiche.</p>
    </section>
    <section class="section container">
      <div class="glass cta-box">
        <div><h2>Vous ne trouvez pas votre bien ?</h2><p>Dites-nous ce que vous cherchez : nous vous prévenons dès qu'un bien correspond.</p></div>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="../contact/">Nous contacter {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </div>
    </section>'''
ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "@id": f"{SITE}/nos-annonces/#page", "url": f"{SITE}/nos-annonces/", "name": "Nos annonces immobilières",
       "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#agence"},
       "mainEntity": {"@type": "ItemList", "numberOfItems": len(ann), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": a["titre"], "url": (f"{SITE}/annonces/{a['id']}/" if a.get("description_html") is not None else f"{SITE}/nos-annonces/")} for i, a in enumerate(ann)]}},
      breadcrumb_ld([("Accueil", SITE + "/"), ("Nos annonces", f"{SITE}/nos-annonces/")])]
open(f"{ROOT}/nos-annonces/index.html", "w", encoding="utf-8").write(shell(prefix, "Nos annonces immobilières : vente et location | LOTIER",
     "Annonces de vente et de location de LOTIER Immobilier à Béziers, Narbonne, Carcassonne, Montpellier, Nîmes et alentours : appartements, maisons, locaux, terrains.",
     "nos-annonces/", body, ld, "assets/og-lotier.jpg", kind="agence"))
print(f"page annonces générée ({len(ann)} annonces)")


# ---------- Fiches détaillées : /annonces/<id>/ ----------
import html as _h, re as _re
def _clip(s, n):
    s = _re.sub(r"\s+", " ", s).strip()
    if len(s) <= n: return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(" ,;:.-")
    return cut + "\u2026"

def _plain(htmlstr): return _re.sub(r"\s+", " ", _h.unescape(_re.sub(r"<[^>]+>", " ", htmlstr or ""))).strip()

# ---- Outils d'affichage d'une fiche ----
NB = " "  # espace insécable

def _eur(t):
    """« 650EUR » -> « 650 € » (les descriptions Hektor écrivent EUR)."""
    return _re.sub(r"(\d)\s?EUR\b", lambda m: m.group(1) + NB + "€", t or "")

def _tel(t):
    """« 0651450663 » -> (« 06 51 45 06 63 », « +33651450663 »), ou None."""
    d = _re.sub(r"\D", "", t or "")
    if d.startswith("33") and len(d) == 11: d = "0" + d[2:]
    if len(d) != 10 or not d.startswith("0"): return None
    return " ".join(d[i:i + 2] for i in range(0, 10, 2)), "+33" + d[1:]

def _nom(n):
    """« BARBARA BOUBA » -> « Barbara Bouba » (prénoms composés compris)."""
    return " ".join("-".join(w.capitalize() for w in part.split("-")) for part in (n or "").strip().split())

def _initiales(n):
    return "".join(w[0] for w in (n or "").split()[:2]).upper() or "L"

_LIEN = _re.compile(r"((?:https?://|www\.)[^\s<>()]*[^\s<>().,;:!?])")
def _liens(txt):
    """Texte brut -> HTML échappé, adresses web cliquables."""
    out, last = "", 0
    for m in _LIEN.finditer(txt):
        out += e(txt[last:m.start()]); u = m.group(1)
        href = u if u.startswith("http") else "https://" + u
        out += f'<a class="text-link" href="{e(href)}" target="_blank" rel="noopener noreferrer">{e(u)}</a>'
        last = m.end()
    return out + e(txt[last:])

# Paragraphes de la description qui sont des MENTIONS LÉGALES (honoraires, mandataire, risques) : ils vont dans leur propre bloc.
_LEGAL = _re.compile(r"^(honoraires|les honoraires|frais d['’]agence|dont honoraires|cette annonce vous est propos|les informations sur les risques|annonce rédigée|barème)|\bR\.?S\.?A\.?C\b|\bRCS\b|carte professionnelle|garantie financi", _re.I)

def _separe_mentions(desc_html):
    """(description sans les mentions légales, [mentions en texte brut])."""
    garde, mentions = [], []
    for blk in _re.findall(r"<p>.*?</p>|<ul>.*?</ul>", desc_html or "", _re.S):
        if blk.startswith("<p>") and _LEGAL.search(_plain(blk)): mentions.append(_eur(_plain(blk)))
        else: garde.append(_eur(blk))
    return "".join(garde), mentions

def _montant(n):
    return f"{n:,.0f}".replace(",", NB) if n is not None else ""

def _echelle(kind, lettre, valeur, unite):
    """Une échelle DPE (A à G) ou GES : la classe du bien est mise en avant, avec sa valeur."""
    lignes = ""
    for L in "ABCDEFG":
        on = L == lettre
        val = f'<span class="dpe-val"><b>{e(str(valeur))}</b> {unite}</span>' if on and valeur is not None else ""
        lignes += f'<li class="dpe-row l-{L.lower()}{" is-on" if on else ""}"><span class="dpe-pt">{val}</span><span class="dpe-bar">{L}</span></li>'
    return f'<ol class="dpe-scale {kind}" aria-hidden="true">{lignes}</ol>'

def energie_bloc(a, titre=True):
    en = a.get("energie") or {}
    dpe, ges = en.get("dpe"), en.get("ges")
    if not dpe and not ges: return ""
    parts, resume = "", []
    if dpe:
        v = dpe.get("valeur")
        resume.append(f"DPE classe {dpe['classe']}" + (f", {v} kWh/m².an" if v is not None else ""))
        parts += ('<figure class="dpe"><figcaption>Diagnostic de performance énergétique</figcaption><div class="dpe-legend"><span>Logement économe</span></div>'
                  + _echelle("dpe-e", dpe["classe"], v, "kWh/m².an") + '<div class="dpe-legend"><span>Logement énergivore</span></div></figure>')
    if ges:
        v = ges.get("valeur")
        resume.append(f"GES classe {ges['classe']}" + (f", {v} kg CO₂/m².an" if v is not None else ""))
        parts += ('<figure class="dpe"><figcaption>Émissions de gaz à effet de serre</figcaption><div class="dpe-legend"><span>Faible émission</span></div>'
                  + _echelle("dpe-g", ges["classe"], v, "kg CO₂/m².an") + '<div class="dpe-legend"><span>Forte émission</span></div></figure>')
    note = ""
    if en.get("depenses_min") is not None and en.get("depenses_max") is not None:
        note += f"<p>Montant estimé des dépenses annuelles d’énergie pour un usage standard : entre {_montant(en['depenses_min'])}{NB}€ et {_montant(en['depenses_max'])}{NB}€ par an.</p>"
    if en.get("prix_energies"):
        note += f"<p>Prix moyens des énergies indexés au {e(en['prix_energies'])} (abonnement compris).</p>"
    note += '<p>Les informations sur les risques auxquels ce bien est exposé sont disponibles sur le site Géorisques : <a class="text-link" href="https://www.georisques.gouv.fr" target="_blank" rel="noopener noreferrer">www.georisques.gouv.fr</a>.</p>'
    tt = '<h2>Diagnostic énergétique du bien</h2>' if titre else ''
    return (f'<div class="ann-diag-in">{tt}<p class="sr-only">{e(" ; ".join(resume))}.</p>'
            f'<div class="dpe-grid">{parts}</div><div class="ann-note">{note}</div></div>')

def mentions_bloc(mentions, p2):
    items = "".join(f"<li>{_liens(m)}</li>" for m in mentions)
    bareme = f'<li>Barème des honoraires de LOTIER Immobilier : <a class="text-link" href="{p2}nos-honoraires/">voir la page Honoraires</a>.</li>'
    return f'<div class="glass ann-bloc ann-legal"><h2>Mentions légales</h2><ul>{items}{bareme}</ul></div>'

def galerie(photos, title, loc, p2):
    """Galerie : flèches, compteur, clavier, balayage au doigt, miniatures, agrandissement plein écran (js/main.js)."""
    if not photos: return ""
    n = len(photos)
    thumbs = "".join(f'<button type="button" class="ann-thumb{" is-on" if i == 0 else ""}" data-gal-i="{i}" data-ann-photo="{p2}{ph}" aria-label="Photo {i + 1} sur {n}"><img src="{p2}{ph}" alt="" width="120" height="90" loading="lazy" decoding="async"></button>' for i, ph in enumerate(photos)) if n > 1 else ""
    fleches = (f'<button type="button" class="ann-nav prev" data-gal-prev aria-label="Photo précédente">{LEFT}</button>'
               f'<button type="button" class="ann-nav next" data-gal-next aria-label="Photo suivante">{ARROW}</button>') if n > 1 else ""
    compteur = f'<span class="ann-count" data-gal-count aria-live="polite">1 / {n}</span>' if n > 1 else ""
    zoom = (f'<button type="button" class="ann-zoom" data-gal-open aria-label="Agrandir la photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg><span class="ann-zoom-txt">Voir les {n} photos</span></button>' if n > 1 else
            '<button type="button" class="ann-zoom" data-gal-open aria-label="Agrandir la photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button>')
    tuiles = F.vignettes(photos, title, p2)
    boite = (f'<dialog class="ann-lightbox" data-gal-box aria-label="Photos du bien"><button type="button" class="ann-close" data-gal-close aria-label="Fermer">{CLOSE}</button>'
             f'<img alt="" data-gal-big>{fleches}{compteur.replace("data-gal-count", "data-gal-count2")}</dialog>')
    return (f'<div class="ann-gallery{" has-tiles" if tuiles else ""}" data-gal data-ann-gallery="">\n'
            f'          <div class="ann-mosaic">\n'
            f'          <div class="ann-main" data-gal-stage tabindex="0" aria-roledescription="carrousel" aria-label="Photos du bien ({n})"><img src="{p2}{photos[0]}" alt="{e(title)}" width="1000" height="750" data-ann-main fetchpriority="high"><span class="badge{" loc" if loc else ""}">{"LOCATION" if loc else "VENTE"}</span>{fleches}{compteur}{zoom}</div>\n'
            f'          {tuiles}\n          </div>\n'
            f'          <div class="ann-thumbs">{thumbs}</div>\n          {boite}\n        </div>')


# ---------- Biens de l'agent et biens proches (bas de fiche) ----------
import unicodedata as _ud
_PROX = json.load(open(f"{ROOT}/data/proximite.json", encoding="utf-8"))["zones"]
def _cle_ville(v): return _re.sub(r"[^a-z0-9]+", "-", _ud.normalize("NFD", (v or "").lower()).encode("ascii", "ignore").decode()).strip("-")
_ZONE_DE = {_cle_ville(c): z for z in _PROX for c in z["communes"]}
_ZONES = {z["id"]: z for z in _PROX}
def _agent_cle(a):
    ag = a.get("agent") or {}
    return (ag.get("email") or "").strip().lower() or _nom(ag.get("nom") or "").strip().lower()
def _eloignement(a, b):
    """0 = même commune, 1 = même secteur, 2+ = secteurs voisins (plus petit = plus proche) ; None = trop loin."""
    ka, kb = _cle_ville(a["ville"]), _cle_ville(b["ville"])
    if ka == kb: return 0
    za, zb = _ZONE_DE.get(ka), _ZONE_DE.get(kb)
    if not za or not zb: return None
    if za["id"] == zb["id"]: return 1
    return 2 + za["proches"].index(zb["id"]) if zb["id"] in za["proches"] else None
def suggestions(a, tous, n_agent=4, n_proches=3):
    """(autres biens de l'agent, biens proches) : uniquement des fiches qui existent, sans doublon ni la fiche elle-même."""
    ok = [b for b in tous if b["id"] != a["id"] and b.get("description_html") is not None]
    cle = _agent_cle(a)
    agent = [b for b in ok if cle and _agent_cle(b) == cle]
    agent.sort(key=lambda b: (_eloignement(a, b) if _eloignement(a, b) is not None else 99, b["type"] != a["type"], b["id"]))
    agent = agent[:n_agent]
    vus = {b["id"] for b in agent}
    proches = [(d, b) for b in ok if b["id"] not in vus for d in [_eloignement(a, b)] if d is not None]
    proches.sort(key=lambda t: (t[0], t[1]["type"] != a["type"], t[1]["id"]))
    return agent, [b for _, b in proches[:n_proches]]
def suggestions_bloc(a, tous, p2):
    agent, proches = suggestions(a, tous)
    def liste(titre, items, id_):
        if not items: return ""
        return (f'<div class="ann-more-grp"><h2 class="heading" id="{id_}">{titre}</h2>'
                f'<div class="cards ann-more-grid" aria-labelledby="{id_}">{"".join(annonce_card(b, p2) for b in items)}\n      </div></div>')
    ag = a.get("agent") or {}
    prenom = _nom(ag["nom"]).split(" ")[0] if ag.get("nom") else ""
    html = liste(f"Les autres biens de {e(prenom)}" if prenom else "Les autres biens de votre conseiller", agent, "ann-agent-biens") + liste("Biens à proximité", proches, "ann-proches")
    return f'<section class="section container ann-more" aria-label="Autres biens">{html}</section>' if html else ""

def detail_page(a, tous=()):
    p2 = "../../"
    title = _nice_title(a); price = _price(a)
    photos = a.get("photos") or ([a["photo"]] if a.get("photo") else [])
    loc = a["type"] == "location"
    gallery = galerie(photos, title, loc, p2)
    facts = []
    if a.get("surface"): facts.append(f"{a['surface']:g}".replace(".", ",") + " m²")
    if a.get("chambres"): facts.append(f"{a['chambres']} chambre" + ("s" if a["chambres"] > 1 else ""))
    if a.get("sdb"): facts.append(f"{a['sdb']} salle" + ("s" if a["sdb"] > 1 else "") + " d'eau/bain")
    facts_html = "".join(f"<li>{e(f)}</li>" for f in facts)
    vals = F.valeurs(a.get("blocs"))
    desc, mentions = _separe_mentions(a.get("description_html") or "")
    diag = F.bilan_energie(a, energie_bloc(a, titre=False))
    legal = mentions_bloc(mentions, p2)
    ag = a.get("agent") or {}
    tel = _tel(ag.get("telephone"))
    notes_l = [_eur(m) for m in (a.get("mentions_prix") or [])]
    notes = "".join(f"<li>{e(m)}</li>" for m in notes_l)
    cles = F.cles_bloc(a, vals); atouts = F.atouts_bloc(vals); carac = F.caracteristiques_bloc(a.get("blocs")); prix_det = F.prix_bloc(a, vals, price, notes_l)
    ref = f'<p class="ann-ref muted small">Réf. {e(a["reference"])}</p>' if a.get("reference") else ""
    rappel_attrs = (f'data-contact-open="rappel" data-ref="{e(a.get("reference") or "")}" data-titre="{e(title)}" '
                    f'data-url="{SITE}/annonces/{a["id"]}/" data-agent="{e(ag.get("email") or "")}" '
                    f'data-agent-prenom="{e(_nom(ag["nom"]).split(" ")[0]) if ag.get("nom") else ""}"{attr_tel_agent(ag)}')
    if ag.get("nom"):
        prenom = _nom(ag["nom"]).split(" ")[0]
        appel = f'<a class="btn btn-gold btn-lg btn-block mag ann-call" href="tel:{tel[1]}">{PH}<span class="ann-call-txt"><span>Appeler {e(prenom)}</span><strong>{tel[0]}</strong></span></a>' if tel else ""
        mail = f'<a class="ann-mail" href="mailto:{e(ag["email"])}">{e(ag["email"])}</a>' if ag.get("email") else ""
        agent = (f'<div class="ann-agent"><span class="ann-ava" aria-hidden="true">{e(_initiales(ag["nom"]))}</span><div><strong>{e(_nom(ag["nom"]))}</strong><span class="muted small">Votre contact LOTIER Immobilier</span></div></div>\n'
                 f'            {appel}\n            {mail}\n'
                 f'            <a class="btn btn-ghost btn-lg btn-block mag" href="{p2}contact/" {rappel_attrs}>Être rappelé {ARROW}</a>\n'
                 f'            <p class="muted small">Standard de l’agence : <a class="text-link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>')
    else:
        agent = (f'<a class="btn btn-gold btn-lg btn-block mag" href="{p2}contact/" {rappel_attrs}>Être rappelé {ARROW}</a>\n'
                 f'            <a class="btn btn-ghost btn-lg btn-block mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a>')
    body = f'''    <section class="page-hero ann-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{p2}index.html">Accueil</a><span aria-hidden="true">/</span><a href="{p2}nos-annonces/">Nos annonces</a><span aria-hidden="true">/</span><span aria-current="page">{e(a['ville'])}</span></nav>
        <h1 class="display page-title ann-title">{e(title)}</h1>
        <p class="lead"><strong>{price}</strong> · {e(a['ville'])}{(' · ' + ' · '.join(facts)) if facts else ''}</p>
      </div>
    </section>
    <section class="section container ann-detail">
      <div class="ann-layout">
        <div class="ann-left">
          {gallery}
          {cles}
          <section class="ann-card ann-desc" aria-labelledby="ann-h-desc"><h2 id="ann-h-desc">Description</h2>{desc if desc else '<p class="muted">Contactez-nous pour recevoir la description complète de ce bien.</p>'}</section>
          {atouts}
          {carac}
          {prix_det}
          {diag}
          {F.simulation_bloc(a)}
          {F.partenaire_bloc()}
          {legal}
        </div>
        <aside class="ann-side">
          <div class="glass ann-box">
            <span class="ann-label">{'LOYER' if loc else 'PRIX'}</span>
            <span class="price">{price}</span>
            {f'<ul class="ann-notes">{notes}</ul>' if notes else ''}
            {ref}
            <ul class="ann-facts">{facts_html}</ul>
            {agent}
            <p class="muted small">Annonce proposée par LOTIER Immobilier.</p>
          </div>
        </aside>
      </div>
      <p style="margin-top:28px"><a class="text-link" href="{p2}nos-annonces/">← Toutes les annonces</a></p>
    </section>
    {suggestions_bloc(a, tous, p2)}'''

    url = f"{SITE}/annonces/{a['id']}/"
    d = _clip(_plain(desc), 165) if desc else f"{title} \u00e0 {a['ville']} : annonce LOTIER Immobilier. Photos, caract\u00e9ristiques et contact."
    if len(d) < 80: d = _clip(f"{title} \u00e0 {a['ville']}. {d} Annonce LOTIER Immobilier : photos, caract\u00e9ristiques et contact.", 165)
    t = _clip(title, 52) + " | LOTIER"
    offer = {"@type": "Offer", "priceCurrency": "EUR", "price": a["prix"], "availability": "https://schema.org/InStock", "seller": {"@id": SITE + "/#agence"}} if a.get("prix") and not (a["type"] == "vente" and a["prix"] < 1000) else None
    node = {"@context": "https://schema.org", "@type": ["RealEstateListing", "WebPage"], "@id": url + "#annonce", "url": url, "name": title, "description": d, "inLanguage": "fr-FR",
            "datePosted": None, "image": [f"{SITE}/{ph}" for ph in photos], "about": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": a["ville"], "addressCountry": "FR"}},
            "isPartOf": {"@id": SITE + "/#website"}}
    if offer: node["offers"] = offer
    node = {k: v for k, v in node.items() if v is not None}
    os.makedirs(f"{ROOT}/annonces/{a['id']}", exist_ok=True)
    open(f"{ROOT}/annonces/{a['id']}/index.html", "w", encoding="utf-8").write(shell(p2, t, d, f"annonces/{a['id']}/", body, [node, breadcrumb_ld([("Accueil", SITE + "/"), ("Nos annonces", f"{SITE}/nos-annonces/"), (title, url)])],
        photos[0] if photos else "assets/og-lotier.jpg", kind="agence"))

import shutil
_detail = [a for a in ann if a.get("description_html") is not None]
shutil.rmtree(f"{ROOT}/annonces", ignore_errors=True)
for a in _detail: detail_page(a, ann)
print(f"{len(_detail)} fiches d\u00e9taill\u00e9es g\u00e9n\u00e9r\u00e9es")
