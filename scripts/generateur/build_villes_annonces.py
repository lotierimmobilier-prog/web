# -*- coding: utf-8 -*-
"""Pages « Biens à vendre à <ville> » et « Biens à louer à <ville> » : /nos-annonces/vente-<ville>/ et /nos-annonces/location-<ville>/.
Une page par ville et par type de transaction comptant au moins 3 annonces (pages_ville_annonces, common.py). Tout le texte est
déduit des annonces (nombre, types, prix, surfaces) : rien n'est inventé. Les pages suivent la mise à jour quotidienne des annonces."""
import os, json, shutil, collections
from common import *
from common import annonce_card
from content_cities import CITIES

p2 = "../../"
PAGES = pages_ville_annonces()
VILLE_AGENCE = {c["name"]: c for c in CITIES}
NOMS = {"maison": ("maison", "maisons"), "appartement": ("appartement", "appartements"), "immeuble": ("immeuble", "immeubles"), "terrain": ("terrain", "terrains"),
        "commerce": ("local commercial", "locaux commerciaux"), "parking": ("parking", "parkings")}
_TYPE = {"Appartement": "appartement", "Maison/villa": "maison", "Immeuble": "immeuble", "Terrain": "terrain", "Local": "commerce", "Boutique": "commerce", "Bureaux": "commerce", "Parking/box": "parking"}

def cat(x):
    brut = next((l[1] for b in x.get("blocs") or [] for l in b["lignes"] if l[0] == "Type de bien"), "")
    return _TYPE.get(brut) or categorie_bien(x)
def eur(n): return f"{int(round(n)):,}".replace(",", " ") + " €"
def liste(xs): return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " et " + xs[-1]
def a_ville(v): return ("au " + v[3:]) if v.startswith("Le ") else ("aux " + v[4:]) if v.startswith("Les ") else "à " + v

def page(g):
    ville, loc, ann = g["ville"], g["type"] != "vente", g["annonces"]
    n = len(ann); action = "à louer" if loc else "à vendre"; ou = a_ville(ville)
    cats = collections.Counter(cat(x) for x in ann)
    types = [f"{k} {NOMS[c][1 if k > 1 else 0]}" for c, k in cats.most_common() if c in NOMS]
    prix = sorted(x["prix"] for x in ann if x.get("prix") and (loc or x["prix"] >= 1000))
    surf = sorted(x["surface"] for x in ann if x.get("surface"))
    unite = " par mois" if loc else ""
    # --- texte déduit des annonces ---
    intro = f"LOTIER Immobilier propose actuellement {n} biens {action} {ou}" + (f" : {liste(types)}." if types else ".")
    if len(prix) > 1: intro += f" Les {'loyers' if loc else 'prix'} vont de {eur(prix[0])} à {eur(prix[-1])}{unite}."
    if len(surf) > 1: intro += f" Les surfaces vont de {round(surf[0])} à {round(surf[-1])} m²."
    faq = [(f"Combien de biens sont {action} {ou} chez LOTIER Immobilier ?", f"{n} biens sont {action} {ou} aujourd'hui" + (f" : {liste(types)}." if types else ".") + " Cette liste est reprise chaque jour du logiciel de l'agence.")]
    if len(prix) > 1:
        med = prix[len(prix) // 2]
        faq.append((f"Quel budget prévoir pour {'louer' if loc else 'acheter'} {ou} ?", f"Parmi nos annonces, les {'loyers' if loc else 'prix'} vont de {eur(prix[0])} à {eur(prix[-1])}{unite}, avec un {'loyer' if loc else 'prix'} médian de {eur(med)}{unite}. Ces montants reflètent nos annonces du moment, pas l'ensemble du marché."))
    ags = collections.OrderedDict()
    for x in ann:
        nom = (x.get("agent") or {}).get("nom")
        if nom: ags[" ".join(w.capitalize() for w in nom.split())] = 1
    if ags: faq.append((f"Qui contacter pour visiter un bien {ou} ?", f"Chaque annonce indique l'agent qui présente le bien et son téléphone direct. {ou[0].upper() + ou[1:]}, nos annonces sont présentées par {liste(list(ags)[:4])}. Vous pouvez aussi demander à être rappelé depuis l'annonce."))
    if loc: faq.append(("Quels sont les honoraires de location ?", "Les honoraires de mise en location sont plafonnés par la loi et calculés au mètre carré : 8,07 €, 10,09 € ou 12,10 € TTC par m² selon la zone, plus 3,03 € TTC par m² pour l'état des lieux. Le détail figure sur la page Nos honoraires."))
    else: faq.append(("Les honoraires sont-ils inclus dans les prix affichés ?", "Oui. Les prix de vente affichés comprennent les honoraires de l'agence, qui sont à la charge du vendeur. Le barème est publié sur la page Nos honoraires."))
    faq_html = '<div class="faq">' + "".join(f'<details><summary><span class="cat">Question</span><h3>{e(q)}</h3></summary><div class="answer"><p>{e(r)}</p></div></details>' for q, r in faq) + "</div>"
    # --- liens ---
    autre = next((x for x in PAGES if x["ville"] == ville and x["type"] != g["type"]), None)
    voisines = [x for x in PAGES if x["type"] == g["type"] and x["ville"] != ville][:6]
    liens = ""
    if autre: liens += f'<a class="chip-link" href="../{autre["slug"]}/">Biens {"à vendre" if loc else "à louer"} {e(ou)} ({len(autre["annonces"])})</a>'
    liens += "".join(f'<a class="chip-link" href="../{x["slug"]}/">{"Location" if loc else "Vente"} {e(a_ville(x["ville"]))} ({len(x["annonces"])})</a>' for x in voisines)
    ag = VILLE_AGENCE.get(ville)
    if ag: liens += f'<a class="chip-link" href="{p2}{ag["slug"]}.html">Notre agence {e(ou)}</a>'
    liens += f'<a class="chip-link" href="{p2}nos-honoraires/">Nos honoraires</a><a class="chip-link" href="{p2}nos-agents/">Nos agents</a>'
    h1 = f'Biens {action} <em class="gold-text">{e(ou)}.</em>'
    body = f'''    <section class="page-hero ann-list-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{p2}index.html">Accueil</a><span aria-hidden="true">/</span><a href="../">Nos annonces</a><span aria-hidden="true">/</span><span aria-current="page">{"Location" if loc else "Vente"} {e(ou)}</span></nav>
        <h1 class="display page-title">{h1}</h1>
        <p class="lead">{e(intro)}</p>
      </div>
    </section>
    <section class="section container" aria-label="Annonces">
      <h2 class="sr-only">Liste des annonces</h2>
      <div class="cards ag-cards">{"".join(annonce_card(x, p2) for x in ann)}
      </div>
      <p style="margin-top:28px"><a class="text-link" href="../?offre={g["type"]}&amp;ville={e(ville)}">Filtrer et trier ces annonces</a> · <a class="text-link" href="../">Toutes nos annonces</a></p>
    </section>
    <section class="section container" aria-labelledby="t-faq">
      <div class="section-head"><div class="stack-3"><span class="label">Questions fréquentes</span><h2 class="title" id="t-faq">{"Louer" if loc else "Acheter"} {e(ou)}</h2></div></div>
      {faq_html}
    </section>
    <section class="section container" aria-label="À voir aussi"><div class="chip-links">{liens}</div></section>'''
    url = f"{SITE}/nos-annonces/{g['slug']}/"
    titre = f"{'Location' if loc else 'Immobilier à vendre'} {ou} : {n} biens | LOTIER"
    if len(titre) > 65: titre = f"{'Location' if loc else 'Vente'} {ou} : {n} biens | LOTIER"
    desc = clip_desc(f"{n} biens {action} {ou} avec LOTIER Immobilier" + (f" : {liste(types)}" if types else "") + (f", de {eur(prix[0])} à {eur(prix[-1])}{unite}" if len(prix) > 1 else "") + ". Photos, prix, agent à contacter.")
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "@id": url + "#page", "url": url, "name": f"Biens {action} {ou}", "description": desc, "inLanguage": "fr-FR",
           "isPartOf": {"@id": SITE + "/#website"}, "about": {"@type": "City", "name": ville},
           "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["titre"], "url": f"{SITE}/annonces/{x['id']}/"} for i, x in enumerate(ann)]}},
          {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]},
          breadcrumb_ld([("Accueil", SITE + "/"), ("Nos annonces", SITE + "/nos-annonces/"), (f"{'Location' if loc else 'Vente'} {ou}", url)])]
    os.makedirs(f"{ROOT}/nos-annonces/{g['slug']}", exist_ok=True)
    photo = next((x["photo"] for x in ann if x.get("photo")), "assets/og-lotier.jpg")
    open(f"{ROOT}/nos-annonces/{g['slug']}/index.html", "w", encoding="utf-8").write(shell(p2, titre, desc, f"nos-annonces/{g['slug']}/", body, ld, photo, kind="agence"))

def clip_desc(s, n=160):
    if len(s) <= n: return s
    return s[:n].rsplit(" ", 1)[0].rstrip(" ,;:.") + "…"

garder = {g["slug"] for g in PAGES}
base = f"{ROOT}/nos-annonces"
for d in os.listdir(base):                      # pages dont la ville est passée sous le seuil : retirées
    if os.path.isdir(f"{base}/{d}") and d not in garder: shutil.rmtree(f"{base}/{d}")
for g in PAGES: page(g)
print(f"{len(PAGES)} pages d'annonces par ville :", ", ".join(f'{g["slug"]} ({len(g["annonces"])})' for g in PAGES))
