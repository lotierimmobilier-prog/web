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
      <p class="muted small" style="margin-top:24px">Les fiches détaillées (photos, diagnostics, honoraires) s'ouvrent sur notre ancien site. Prix en euros ; les honoraires et le DPE figurent sur chaque fiche.</p>
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
