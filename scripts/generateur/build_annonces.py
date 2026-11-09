# -*- coding: utf-8 -*-
"""Page « Nos annonces » : toutes les annonces de data/annonces.json, avec filtres (vente/location, ville)."""
import os, json
from common import *
prefix = "../"

ann = load_annonces()
os.makedirs(f"{ROOT}/nos-annonces", exist_ok=True)
nb_v = sum(1 for a in ann if a["type"] == "vente"); nb_l = len(ann) - nb_v
villes = sorted({a["ville"] for a in ann if a["ville"]})
cards = "".join(annonce_card(a, prefix) for a in ann) if ann else '<p class="muted">Aucune annonce publiée pour le moment. <a class="text-link" href="../contact/">Contactez-nous</a> pour connaître nos biens à venir.</p>'
opts = '<option value="">Toutes les villes</option>' + "".join(f'<option value="{e(v)}">{e(v)}</option>' for v in villes)
body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Nos annonces</span></nav>
        <h1 class="display page-title">Nos annonces, <em class="gold-text">ventes et locations.</em></h1>
        <p class="lead">{nb_v} biens à vendre et {nb_l} à louer autour de Béziers, Narbonne, Carcassonne, Montpellier et Nîmes. Un bien vous intéresse ? Un conseiller vous rappelle.</p>
      </div>
    </section>
    <section class="section container" aria-label="Annonces" data-annonces>
      <div class="ann-filters">
        <div class="chip-links" role="group" aria-label="Type d'annonce">
          <button type="button" class="chip-link is-on" data-ann-type-btn="" aria-pressed="true">Toutes ({len(ann)})</button>
          <button type="button" class="chip-link" data-ann-type-btn="vente" aria-pressed="false">À vendre ({nb_v})</button>
          <button type="button" class="chip-link" data-ann-type-btn="location" aria-pressed="false">À louer ({nb_l})</button>
        </div>
        <label class="ann-city"><span class="small muted">Ville</span><select data-ann-city>{opts}</select></label>
      </div>
      <p class="muted small" data-ann-count aria-live="polite">{len(ann)} annonces</p>
      <div class="cards" data-ann-grid>{cards}
      </div>
      <p class="muted small" data-ann-empty hidden>Aucune annonce ne correspond à ce filtre.</p>
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
       "mainEntity": {"@type": "ItemList", "numberOfItems": len(ann), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": a["titre"], "url": a["url"]} for i, a in enumerate(ann)]}},
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

def detail_page(a):
    p2 = "../../"
    title = _nice_title(a); price = _price(a)
    photos = a.get("photos") or ([a["photo"]] if a.get("photo") else [])
    loc = a["type"] == "location"
    gallery = ""
    if photos:
        thumbs = "".join(f'<button type="button" class="ann-thumb{" is-on" if i == 0 else ""}" data-ann-photo="{p2}{ph}" aria-label="Photo {i + 1} sur {len(photos)}"><img src="{p2}{ph}" alt="" width="120" height="90" loading="lazy"></button>' for i, ph in enumerate(photos)) if len(photos) > 1 else ""
        gallery = f'''<div class="ann-gallery" data-ann-gallery>
          <div class="ann-main"><img src="{p2}{photos[0]}" alt="{e(title)}" width="900" height="675" data-ann-main fetchpriority="high"><span class="badge{' loc' if loc else ''}">{'LOCATION' if loc else 'VENTE'}</span></div>
          <div class="ann-thumbs">{thumbs}</div>
        </div>'''
    facts = []
    if a.get("surface"): facts.append(f"{a['surface']:g}".replace(".", ",") + " m\u00b2")
    if a.get("chambres"): facts.append(f"{a['chambres']} chambre" + ("s" if a["chambres"] > 1 else ""))
    if a.get("sdb"): facts.append(f"{a['sdb']} salle" + ("s" if a["sdb"] > 1 else "") + " d'eau/bain")
    facts_html = "".join(f"<li>{e(f)}</li>" for f in facts)
    blocs = "".join(f'''<div class="glass ann-bloc"><h2>{e(b['titre'])}</h2><dl>{''.join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in b['lignes'])}</dl></div>''' for b in a.get("blocs", []))
    desc = a.get("description_html") or ""
    body = f'''    <section class="page-hero ann-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{p2}index.html">Accueil</a><span aria-hidden="true">/</span><a href="{p2}nos-annonces/">Nos annonces</a><span aria-hidden="true">/</span><span aria-current="page">{e(a['ville'])}</span></nav>
        <h1 class="display page-title ann-title">{e(title)}</h1>
        <p class="lead">{e(a['ville'])}{(' \u00b7 ' + ' \u00b7 '.join(facts)) if facts else ''}</p>
      </div>
    </section>
    <section class="section container ann-detail">
      <div class="ann-layout">
        <div class="ann-left">
          {gallery}
          <div class="glass ann-desc"><h2>Description</h2>{desc if desc else '<p class="muted">Contactez-nous pour recevoir la description complète de ce bien.</p>'}</div>
          {blocs}
        </div>
        <aside class="ann-side">
          <div class="glass ann-box">
            <span class="price">{price}</span>
            <ul class="ann-facts">{facts_html}</ul>
            <a class="btn btn-gold btn-lg btn-block mag" href="{p2}contact/">Être rappelé {ARROW}</a>
            <a class="btn btn-ghost btn-lg btn-block mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a>
            <p class="muted small">Référence : {e(a['id'][:40])}. Annonce proposée par LOTIER Immobilier.</p>
          </div>
        </aside>
      </div>
      <p style="margin-top:28px"><a class="text-link" href="{p2}nos-annonces/">\u2190 Toutes les annonces</a></p>
    </section>'''
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
for a in _detail: detail_page(a)
print(f"{len(_detail)} fiches d\u00e9taill\u00e9es g\u00e9n\u00e9r\u00e9es")
