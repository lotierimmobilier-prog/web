# -*- coding: utf-8 -*-
"""Page /nos-agents/ (bulles par secteur) et une fiche par agent : /nos-agents/<nom>/ avec ses annonces.
Données : data/agents.json (écrit par scripts/sync_agents.py depuis Collab) et data/agents-config.json (secteurs, réglages)."""
import os, json, re, shutil, unicodedata
from common import *
from common import annonce_card
prefix = "../"

DATA = json.load(open(f"{ROOT}/data/agents.json", encoding="utf-8"))
CFG = json.load(open(f"{ROOT}/data/agents-config.json", encoding="utf-8"))
AGENTS = DATA["agents"]
SECT = {s["id"]: s for s in CFG["secteurs"]}
CAT = CFG.get("specialites_catalogue", {})
def independant(a): return a.get("statut", "independant") == "independant" and a.get("role") != "Gérant"
# Le RSAC ne concerne que les agents commerciaux indépendants ; un salarié, un associé ou un alternant n'en a pas.
MANQUE_LEGAL = [f'{a["prenom"]} {a["nom"]}' for a in AGENTS if independant(a) and not a.get("rsac")]
# La page « Nos agents » est ouverte aux moteurs dès que le réglage « indexable » est activé. Une fiche sans RSAC reste, elle seule,
# masquée des moteurs (noindex) et hors du sitemap : un agent ajouté dans Collab sans son RSAC ne fait pas disparaître les autres de Google.
INDEXABLE = bool(CFG.get("indexable")) and bool(AGENTS)
if CFG.get("indexable") and MANQUE_LEGAL:
    print("ATTENTION : fiches laissées en noindex, RSAC manquant pour :", ", ".join(MANQUE_LEGAL))
ROBOTS_OK = "index, follow, max-image-preview:large, max-snippet:-1"
ROBOTS = ROBOTS_OK if INDEXABLE else "noindex, follow"

def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()
def tel_raw(t): return "".join(ch for ch in t if ch.isdigit() or ch == "+")
def tel_intl(t):
    d = tel_raw(t); return "+33" + d[1:] if d.startswith("0") else d
def initials(a): return (a["prenom"][:1] + a["nom"][:1]).upper()

# ---------- icônes ----------
MAIL = svg('<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>')
SITE_ICO = svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>')
GOOGLE = svg('<path d="M20.5 12.2c0-.6-.1-1.2-.2-1.7H12v3.3h4.8a4.1 4.1 0 0 1-1.8 2.7v2.2h2.9c1.7-1.6 2.6-3.9 2.6-6.5z"/><path d="M12 21c2.4 0 4.5-.8 5.9-2.2L15 16.6c-.8.5-1.8.9-3 .9-2.3 0-4.3-1.6-5-3.7H4v2.3A9 9 0 0 0 12 21z"/><path d="M7 13.8a5.4 5.4 0 0 1 0-3.6V8H4a9 9 0 0 0 0 8z"/><path d="M12 6.6c1.3 0 2.5.5 3.4 1.3l2.6-2.6A9 9 0 0 0 4 8l3 2.3c.7-2.1 2.7-3.7 5-3.7z"/>')
SPE_ICO = {
    "vente": svg('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
    "location": svg('<circle cx="8" cy="12" r="3.5"/><path d="M11.5 12H21M18 12v3M15 12v2"/>'),
    "gestion": svg('<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>'),
    "syndic": svg('<path d="M4 21V8l8-5 8 5v13"/><path d="M8 21v-5h3v5M13 21v-5h3v5M8 11h3M13 11h3"/>'),
    "estimation": svg('<circle cx="11" cy="11" r="6"/><path d="m20 20-4.5-4.5M11 8v6M9 10h4"/>'),
    "investissement": svg('<path d="M4 19V5M4 19h16"/><path d="m7 15 4-4 3 3 5-6"/>'),
    "maison": svg('<path d="M3 12l9-8 9 8"/><path d="M6 10.5V20h12v-9.5"/><rect x="10" y="14" width="4" height="6"/>'),
    "appartement": svg('<rect x="6" y="3" width="12" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>'),
    "commerce": svg('<path d="M4 9l1.5-5h13L20 9"/><path d="M4 9v11h16V9"/><path d="M4 9a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0A2.7 2.7 0 0 0 20 9"/>'),
    "terrain": svg('<path d="M3 18l5-8 4 5 3-4 6 7z"/><path d="M3 21h18"/>'),
    "neuf": svg('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>'),
    "prestige": svg('<path d="M3 9l4 3 5-7 5 7 4-3-2 10H5z"/>'),
}
RES_ICO = {
    "facebook": ("Facebook", svg('<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8.5A.5.5 0 0 1 14 8z"/>')),
    "instagram": ("Instagram", svg('<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.6"/><path d="M16.8 7.2h.01"/>')),
    "linkedin": ("LinkedIn", svg('<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 10v6M8 7.5v.01M12 16v-6M12 12.5a2.5 2.5 0 0 1 5 0V16"/>')),
    "tiktok": ("TikTok", svg('<path d="M14 4v10.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 4c.4 2.4 2 3.9 4.5 4.1"/>')),
    "youtube": ("YouTube", svg('<rect x="3" y="6" width="18" height="12" rx="4"/><path d="m10.5 9.5 4 2.5-4 2.5z"/>')),
    "whatsapp": ("WhatsApp", svg('<path d="M4 20l1.2-4A8 8 0 1 1 8 18.8z"/><path d="M9 9c0 3 3 6 6 6l1-1.5-2-1-1 .8a4 4 0 0 1-2-2l.8-1-1-2z"/>')),
}

def clean_bio(a):
    t = (a.get("presentation") or a.get("bio") or "").strip()
    if t.endswith("…"):                          # texte tronqué par Collab : on coupe à la dernière phrase complète
        t = t[:-1].rstrip()
        k = max(t.rfind(". "), t.rfind("! "))
        t = t[:k + 1] if k > 60 else t.rstrip(",;: ") + "…"
    return t

def sect_names(a): return [SECT[s]["nom"] for s in a["secteurs"] if s in SECT]
def principal(a): return SECT.get(a["secteurs"][0]) if a["secteurs"] else None
def couleur(a): return (principal(a) or {}).get("couleur", "#867244")

def annonces_de(a):
    """Annonces dont l'agent est celui-ci (adresse e-mail, sinon prénom et nom)."""
    cle = norm(f"{a['prenom']} {a['nom']}")
    res = []
    for x in load_annonces():
        ag = x.get("agent") or {}
        if (ag.get("email") or "").lower() == a["email"].lower() or norm(ag.get("nom") or "") == cle:
            res.append(x)
    return res

def portrait(a, cls="ag-ph", size=96):
    if a.get("photo"):
        return f'<span class="{cls}"><img src="{{p}}{e(a["photo"])}" alt="Portrait de {e(a["prenom"])} {e(a["nom"])}" width="{size}" height="{size}" loading="lazy"></span>'
    return f'<span class="{cls} ag-ini" aria-hidden="true">{e(initials(a))}</span>'

# ---------- page liste ----------
def static_card(a):
    """Carte d'un agent dans la liste du bas : portrait, secteur, coordonnées, lien vers sa page (et son mini-site Collab s'il répond)."""
    sn = " · ".join(sect_names(a)); nb = len(annonces_de(a)); url = f'{prefix}nos-agents/{a["slug"]}/'
    page = "Voir sa page" + (f" et ses {nb} annonces" if nb > 1 else " et son annonce" if nb == 1 else "")
    liens = f'<a class="btn btn-gold" href="{url}">{page}</a>'
    if a.get("telephone"): liens += f'<a class="btn btn-ghost" href="tel:{tel_intl(a["telephone"])}">{e(a["telephone"])}</a>'
    mail = f'<a class="ag-scard-mail" href="mailto:{e(a["email"])}">{e(a["email"])}</a>' if a.get("email") else ""
    mini = ""   # le mini-site de l'agent est sa page sur ce site (celui de Collab répond de façon instable)
    return (f'''<li class="glass ag-scard" data-s="{" ".join(a["secteurs"])}" style="--rc:{couleur(a)}">{portrait(a).replace("{p}", prefix)}<div><h3><a href="{url}">{e(a["prenom"])} {e(a["nom"])}</a></h3>'''
            f'''<p class="small muted">{e(a["role"])}{(" · " + e(sn)) if sn else ""}</p><p class="small">{e(", ".join(a["communes"][:5]))}</p></div>'''
            f'''<div class="ag-scard-act">{liens}</div><p class="small ag-scard-liens">{mail}{mini}</p></li>''')

def bubble_data(a):
    return {"id": a["id"], "slug": a["slug"], "prenom": a["prenom"], "nom": a["nom"], "role": a["role"], "secteurs": a["secteurs"], "communes": a["communes"],
            "tel": a["telephone"], "email": a["email"], "photo": (prefix + a["photo"]) if a.get("photo") else None, "nb": len(annonces_de(a)),
            "url": f'{prefix}nos-agents/{a["slug"]}/'}

secteurs_utiles = [s for s in CFG["secteurs"] if any(s["id"] in a["secteurs"] for a in AGENTS)]
# Fond de la zone des bulles : lumière beige très transparente + carte de l'Occitanie et ses villes phares (contours dans data/occitanie-carte.json)
import math
_VILLES = [("Béziers", 3.2158, 43.3440, "beziers", (14, -10, "start")), ("Montpellier", 3.8767, 43.6108, "montpellier", (16, 6, "start")),
           ("Nîmes", 4.3601, 43.8367, "nimes", (16, 6, "start")), ("Carcassonne", 2.3491, 43.2130, "carcassonne", (-14, 6, "end")),
           ("Narbonne", 3.0050, 43.1839, "carcassonne", (-14, 20, "end"))]
def _carte():
    try: g = json.load(open(f"{ROOT}/data/occitanie-carte.json", encoding="utf-8"))
    except (OSError, ValueError): return ""
    lon0, lon1, lat0, lat1 = -0.35, 4.87, 42.30, 45.07
    k = 1000 / ((lon1 - lon0) * math.cos(math.radians(43.7)))
    X = lambda lo: (lo - lon0) * math.cos(math.radians(43.7)) * k
    Y = lambda la: (lat1 - la) * k
    H = round(Y(lat0))
    path = lambda rings: "".join("M" + "L".join(f"{X(a):.0f} {Y(b):.0f}" for a, b in r) + "Z" for r in rings)
    deps = "".join(f'<path class="cp-dep" d="{path(r)}"/>' for r in g["departements"].values())
    villes = ""
    for nom, lo, la, sid, (dx, dy, anc) in _VILLES:
        col = SECT.get(sid, {}).get("couleur", "#867244"); x, y = X(lo), Y(la)
        villes += (f'<g class="cp-v" data-s="{sid}" style="--vc:{col}"><circle class="cp-halo" cx="{x:.0f}" cy="{y:.0f}" r="9"/><circle class="cp-dot" cx="{x:.0f}" cy="{y:.0f}" r="6"/>'
                   f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="{anc}">{nom}</text></g>')
    return (f'<svg class="ag-carte" viewBox="0 0 1000 {H}" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><path class="cp-reg" d="{path(g["region"])}"/>{deps}{villes}</svg>')
aurore = '<div class="ag-aurore" aria-hidden="true"><i class="au au-0"></i><i class="au au-1"></i><i class="au au-2"></i></div>' + _carte()
chips = '<button type="button" class="chip-link is-on" data-sect="all" aria-pressed="true">Tous</button>' + "".join(
    f'<button type="button" class="chip-link" data-sect="{s["id"]}" aria-pressed="false"><i style="background:{s["couleur"]}"></i>{e(s["nom"])}</button>' for s in secteurs_utiles) + \
    '<button type="button" class="chip-link ag-mix" data-mix>&#8635; Mélanger</button>'
payload = {"secteurs": {s["id"]: {"nom": s["nom"], "couleur": s["couleur"]} for s in CFG["secteurs"]}, "agents": [bubble_data(a) for a in AGENTS]}
data_js = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Nos agents</span></nav>
        <h1 class="display page-title">Nos agents, <em class="gold-text">près de chez vous.</em></h1>
        <p class="lead">Chaque agent LOTIER connaît son secteur. Touchez un portrait pour le découvrir, voir ses annonces ou l'appeler directement.</p>
      </div>
    </section>

    <section class="section container" id="agents-liste" aria-label="Les agents LOTIER" data-agents>
      <div class="chip-links ag-chips" role="group" aria-label="Filtrer par secteur">{chips}</div>
      <div class="ag-stage">{aurore}<div class="ag-field" id="ag-field"></div></div>
      <div class="glass ag-info" id="ag-info" aria-live="polite"></div>
      <h2 class="title ag-list-t" id="t-tous">Tous nos agents</h2>
      <ul class="ag-list" aria-labelledby="t-tous">{"".join(static_card(a) for a in AGENTS)}</ul>
      <p class="muted small" style="margin-top:28px">Vous ne trouvez pas votre secteur ? <a class="text-link" href="{prefix}contact/">Contactez l'agence</a>, nous vous orienterons vers le bon conseiller. Les agents LOTIER sont des agents commerciaux indépendants.</p>
      <div class="glass ag-join"><div><strong>Envie de rejoindre l'équipe ?</strong><span class="muted"> Devenez agent immobilier indépendant avec LOTIER.</span></div><a class="btn btn-gold" href="{prefix}rejoindre/">Voir le parcours {ARROW}</a></div>
      <script type="application/json" id="ag-data">{data_js}</script>
    </section>'''
ld = [breadcrumb_ld([("Accueil", SITE + "/"), ("Nos agents", SITE + "/nos-agents/")]),
      {"@context": "https://schema.org", "@type": "ItemList", "name": "Les agents LOTIER Immobilier", "numberOfItems": len(AGENTS),
       "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f'{a["prenom"]} {a["nom"]}', "url": f'{SITE}/nos-agents/{a["slug"]}/'} for i, a in enumerate(AGENTS)]}] if AGENTS else [breadcrumb_ld([("Accueil", SITE + "/"), ("Nos agents", SITE + "/nos-agents/")])]

def ecrire(chemin, html):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    open(chemin, "w", encoding="utf-8").write(html)

def avec_script(html, src):
    return html.replace("</body>", f'  <script src="{src}" defer></script>\n</body>', 1)

shutil.rmtree(f"{ROOT}/nos-agents", ignore_errors=True)
page = shell(prefix, "Agents immobiliers à Béziers, Nîmes, Carcassonne | LOTIER", "Les agents LOTIER Immobilier par secteur : Béziers, Carcassonne, Narbonne, Montpellier, Nîmes. Coordonnées, annonces et présentation de chaque conseiller.",
             "nos-agents/", body, ld, "assets/og-lotier.jpg", robots=ROBOTS, kind="agence")
ecrire(f"{ROOT}/nos-agents/index.html", avec_script(page, f'{prefix}js/agents.js?v={V_AGENTS_JS}'))

# ---------- mini-site d'un agent : ce que ses annonces disent de son activité (rien n'est inventé, tout vient de data/annonces.json) ----------
_BIEN_NOM = {"maison": ("maison", "maisons"), "appartement": ("appartement", "appartements"), "immeuble": ("immeuble", "immeubles"), "terrain": ("terrain", "terrains"),
             "commerce": ("local commercial", "locaux commerciaux"), "parking": ("parking", "parkings")}
_BIEN_SPE = {"maison": "maison", "appartement": "appartement", "commerce": "commerce", "terrain": "terrain", "immeuble": "investissement"}

_TYPE_FICHE = {"Appartement": "appartement", "Maison/villa": "maison", "Immeuble": "immeuble", "Terrain": "terrain", "Local": "commerce", "Boutique": "commerce",
               "Bureaux": "commerce", "Parking/box": "parking"}
_UN = {"maison": "d'une maison", "appartement": "d'un appartement", "immeuble": "d'un immeuble", "terrain": "d'un terrain", "commerce": "d'un local commercial", "parking": "d'un parking"}

def _cat(x):
    """Catégorie du bien : le « Type de bien » de la fiche d'abord (un titre « maison avec garage » n'est pas un parking)."""
    brut = next((l[1] for b in x.get("blocs") or [] for l in b["lignes"] if l[0] == "Type de bien"), "")
    return _TYPE_FICHE.get(brut) or categorie_bien(x)

def _eur(n): return f"{int(round(n)):,}".replace(",", " ") + " €"
def _liste(xs): return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " et " + xs[-1]
def _a_ville(v): return ("au " + v[3:]) if v.startswith("Le ") else ("aux " + v[4:]) if v.startswith("Les ") else "à " + v

def activite(a, ann):
    """(paragraphes, codes de spécialités, mots-clés) déduits des annonces en ligne de l'agent."""
    if not ann: return [], [], [], {}
    from collections import Counter
    nv = [x for x in ann if x["type"] == "vente"]; nl = [x for x in ann if x["type"] != "vente"]
    villes = [v for v, _ in Counter(x["ville"] for x in ann).most_common()]
    cats = Counter(_cat(x) for x in ann)
    types = [f"{n} {_BIEN_NOM[c][1 if n > 1 else 0]}" for c, n in cats.most_common() if c in _BIEN_NOM]
    parts = ([f"{len(nv)} à vendre"] if nv else []) + ([f"{len(nl)} à louer"] if nl else [])
    p1 = ((f"{a['prenom']} présente actuellement {len(ann)} biens ({' et '.join(parts)})" if nv and nl else f"{a['prenom']} présente actuellement {len(ann)} biens {'à vendre' if nv else 'à louer'}") if len(ann) > 1 else f"{a['prenom']} présente actuellement un bien {'à vendre' if nv else 'à louer'}")
    p1 += f" {_a_ville(villes[0])}" if len(villes) == 1 else (f", notamment à {', '.join(villes[:6])}" if len(villes) > 6 else f", à {_liste(villes)}")
    p1 += "."
    p2 = []
    if types: p2.append(f"Parmi ces biens : {_liste(types)}." if len(ann) > 1 else f"Il s'agit {_UN[cats.most_common(1)[0][0]]}.")
    pv = sorted(x["prix"] for x in nv if x.get("prix") and x["prix"] >= 1000); pl = sorted(x["prix"] for x in nl if x.get("prix"))
    if len(pv) > 1: p2.append(f"Les biens à vendre vont de {_eur(pv[0])} à {_eur(pv[-1])}.")
    elif pv: p2.append(f"Le bien à vendre est proposé à {_eur(pv[0])}.")
    if len(pl) > 1: p2.append(f"Les loyers vont de {_eur(pl[0])} à {_eur(pl[-1])} par mois.")
    elif pl: p2.append(f"Le bien à louer est proposé à {_eur(pl[0])} par mois.")
    spe = (["vente"] if nv else []) + (["location"] if nl else []) + [_BIEN_SPE[c] for c, _ in cats.most_common() if c in _BIEN_SPE]
    combos = Counter((_cat(x), x["type"], x["ville"]) for x in ann if _cat(x) in _BIEN_NOM)
    mots = [f"{_BIEN_NOM[c][0].capitalize()} {'à vendre' if t == 'vente' else 'à louer'} {_a_ville(v)}" for (c, t, v), _ in combos.most_common(8)]
    prix = (([f"Ventes de {_eur(pv[0])} à {_eur(pv[-1])}"] if len(pv) > 1 else [f"Vente à {_eur(pv[0])}"] if pv else [])
            + ([f"loyers de {_eur(pl[0])} à {_eur(pl[-1])} par mois"] if len(pl) > 1 else [f"loyer de {_eur(pl[0])} par mois"] if pl else []))
    chiffres = {"biens": len(ann), "vente": len(nv), "location": len(nl), "communes": len(villes), "types": types, "prix": " · ".join(prix)}
    return [p1] + ([" ".join(p2)] if p2 else []), list(dict.fromkeys(spe)), mots, chiffres

def filtres_annonces(ann):
    """Mêmes filtres et tri que la page « Nos annonces » (même script js/main.js), limités aux biens de l'agent."""
    from collections import Counter
    nv = sum(1 for x in ann if x["type"] == "vente"); nl = len(ann) - nv
    biens = Counter(categorie_bien(x) for x in ann); deps = Counter(departement(x) for x in ann)
    villes = sorted({x["ville"] for x in ann if x["ville"]})
    o_ville = "".join(f'<option value="{e(v)}" data-dep="{e(departement(next(x for x in ann if x["ville"] == v)))}">{e(v)}</option>' for v in villes)
    o_bien = "".join(f'<option value="{k}">{e(lib)} ({biens[k]})</option>' for k, lib in BIENS_LIBELLES.items() if biens.get(k))
    o_dep = "".join(f'<option value="{c}">{e(n)} ({c}) · {deps[c]}</option>' for c, n in DEPARTEMENTS.items() if deps.get(c))
    cache = lambda n: " hidden" if n < 2 else ""      # un seul département ou une seule ville : le choix n'a pas de sens
    mixte = "" if nv and nl else " hidden"
    return f'''<form class="ann-filtres ann-filtres-mini" data-ann-form aria-label="Filtrer les annonces" onsubmit="return false">
        <div class="chip-links" role="group" aria-label="Vente ou location"{mixte}>
          <button type="button" class="chip-link is-on" data-ann-type-btn="" aria-pressed="true">Toutes ({len(ann)})</button>
          <button type="button" class="chip-link" data-ann-type-btn="vente" aria-pressed="false">À vendre ({nv})</button>
          <button type="button" class="chip-link" data-ann-type-btn="location" aria-pressed="false">À louer ({nl})</button>
        </div>
        <div class="ann-champs">
          <label{cache(len(biens))}><span>Type de bien</span><select data-ann-bien><option value="">Tous les biens</option>{o_bien}</select></label>
          <label{cache(len(deps))}><span>Département</span><select data-ann-dep><option value="">Tous les départements</option>{o_dep}</select></label>
          <label{cache(len(villes))}><span>Ville</span><select data-ann-city><option value="">Toutes les villes</option>{o_ville}</select></label>
          <label hidden><span>Budget min.</span><select data-ann-pmin disabled><option value="">Choisir vente ou location</option></select></label>
          <label hidden><span>Budget max.</span><select data-ann-pmax disabled><option value="">Choisir vente ou location</option></select></label>
          <label><span>Trier par</span><select data-ann-sort><option value="">Trier</option><option value="prix-asc">Prix croissant</option><option value="prix-desc">Prix décroissant</option><option value="surf-desc">Surface décroissante</option></select></label>
        </div>
        <div class="ann-filtres-pied"><p class="muted small" data-ann-count aria-live="polite">{len(ann)} annonces</p><button type="button" class="text-link ann-reset" data-ann-reset hidden>Réinitialiser les filtres</button></div>
      </form>'''

# ---------- fiche d'un agent ----------
def fiche(a):
    p2 = "../../"
    nom = f'{a["prenom"]} {a["nom"]}'
    sects = sect_names(a); pr = principal(a)
    ann = annonces_de(a); nv = sum(1 for x in ann if x["type"] == "vente"); nl = len(ann) - nv
    bio = clean_bio(a)
    base = f'{nom} est {a["role"].lower()} LOTIER Immobilier' + (f', secteur {" et ".join(sects)}' if sects else "") + "."
    act_txt, act_spe, act_mots, ch = activite(a, ann)
    texte_fiche = bio or base        # les chiffres, les communes et les types de biens sont dans les tuiles et les encadrés
    tuiles = ""
    if ch and ch["biens"] >= 3:      # avec un ou deux biens, des tuiles « 1 · 1 · 1 » n'apportent rien
        t = [(ch["biens"], "bien" + ("s" if ch["biens"] > 1 else "") + " en ligne"), (ch["vente"], "à vendre"), (ch["location"], "à louer"), (ch["communes"], "commune" + ("s" if ch["communes"] > 1 else ""))]
        tuiles = '<ul class="ag-stats">' + "".join(f'<li class="glass"><strong>{n}</strong><span>{e(l)}</span></li>' for n, l in t if n) + "</ul>"
    if not tuiles: texte_fiche = "\n".join([texte_fiche] + ([" Communes couvertes : " + ", ".join(a["communes"]) + "."] if a["communes"] and not bio else []) + act_txt)
    prix_l = f'<p class="ag-prix">{e(ch["prix"])}.</p>' if ch.get("prix") and tuiles else ""
    types_l = "".join(f"<li>{e(x)}</li>" for x in ch.get("types", []))
    specialites = [x for x in (a.get("specialites") or act_spe) if x in CAT]      # saisies dans Collab, sinon déduites des annonces
    mots_cles = a.get("mots_cles") or act_mots
    liens = ""
    if a.get("telephone"): liens += f'<a class="btn btn-gold" href="tel:{tel_intl(a["telephone"])}">{PH}{e(a["telephone"])}</a>'
    if a.get("email"): liens += f'<a class="btn btn-ghost" href="mailto:{e(a["email"])}">{MAIL}Écrire</a>'
    liens += f'<a class="btn btn-navy ag-estim" href="{p2}index.html#estimer"><span>Estimer mon bien</span>{ARROW}</a>'
    if a.get("google"): liens += f'<a class="btn btn-ghost" href="{e(a["google"])}" target="_blank" rel="noopener">{GOOGLE}Avis Google</a>'
    reseaux = "".join(f'<a class="ag-res" href="{e(u)}" target="_blank" rel="noopener me" aria-label="{RES_ICO[k][0]} de {e(nom)}" title="{RES_ICO[k][0]}">{RES_ICO[k][1]}</a>' for k, u in (a.get("reseaux") or {}).items() if k in RES_ICO)
    spe = "".join(f'<li class="ag-spe">{SPE_ICO.get(s, "")}<span>{e(CAT[s])}</span></li>' for s in specialites)
    comm = "".join(f'<li>{e(c)}</li>' for c in a["communes"])
    mots = "".join(f'<li>{e(m)}</li>' for m in mots_cles)
    cartes = "".join(annonce_card(x, p2) for x in ann)
    mini = f'<a class="text-link" href="{e(a["mini_site"])}" target="_blank" rel="noopener">{SITE_ICO}Son mini-site</a>' if a.get("mini_site") else ""
    legal = ""
    if a.get("rsac"):
        legal = (f'{a["role"]} de la SARL LOTIER Immobilier, immatriculé' + ((" au RSAC d’" if a["rsac_ville"][:1].lower() in "aeiouyhéèî" else " au RSAC de ") + a["rsac_ville"] if a.get("rsac_ville") else " au RSAC") + f' sous le n° {a["rsac"]}. '
                 'Carte professionnelle de LOTIER : CPI3401 2016 000 014 824, délivrée par la CCI de l\'Hérault. Garantie financière : SOCAF.')
    puces = " ".join(f'<span class="ag-pill" style="--rc:{SECT[s]["couleur"]}">{e(SECT[s]["nom"])}</span>' for s in a["secteurs"] if s in SECT)
    body = f'''    <section class="page-hero ag-hero" style="--rc:{couleur(a)}">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container ag-hero-grid">
        {portrait(a, "ag-ph ag-ph-xl", 220).replace("{p}", p2)}
        <div>
          <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{p2}index.html">Accueil</a><span aria-hidden="true">/</span><a href="{p2}nos-agents/">Nos agents</a><span aria-hidden="true">/</span><span aria-current="page">{e(nom)}</span></nav>
          <h1 class="display page-title">{e(nom)}</h1>
          <p class="lead">{e(a["role"])}{(" · secteur " + e(" et ".join(sects))) if sects else ""}</p>
          <p>{puces}</p>
          <div class="acts">{liens}</div>
          {('<div class="ag-resx" aria-label="Réseaux sociaux">' + reseaux + '</div>') if reseaux else ""}
        </div>
      </div>
    </section>
''' + f'''    <section class="section container{" ann-list" if len(ann) >= 4 else ""}" aria-labelledby="ag-ann"{" data-annonces" if len(ann) >= 4 else ""}>
      <div class="section-head"><div class="stack-3"><span class="label">Annonces</span><h2 class="title" id="ag-ann">Les biens de {e(a["prenom"])}</h2></div><a class="text-link" href="{p2}nos-annonces/">Toutes les annonces</a></div>
      {((filtres_annonces(ann) + '<div class="cards" data-ann-grid>' + cartes + '</div><p class="muted" data-ann-empty hidden>Aucune annonce ne correspond à ces critères. <button type="button" class="text-link ann-reset" data-ann-reset>Réinitialiser les filtres</button></p>') if len(ann) >= 4 else ('<p class="muted small">' + " · ".join(x for x in ((f"{nv} à vendre" if nv else ""), (f"{nl} à louer" if nl else "")) if x) + '</p><div class="cards ag-cards">' + cartes + '</div>')) if ann else f'<p class="muted">{e(a["prenom"])} n\'a pas d\'annonce en ligne pour le moment. <a class="text-link" href="{p2}nos-annonces/">Voir toutes nos annonces</a> ou <a class="text-link" href="{p2}contact/">contactez l\'agence</a>.</p>'}
    </section>
''' + (f'''    <section class="section container" aria-labelledby="ag-pres"><div class="section-head"><div class="stack-3"><span class="label">Présentation</span><h2 class="title" id="ag-pres">Faire connaissance avec {e(a["prenom"])}</h2></div></div>
      {tuiles}
      <div class="prose ag-prose">{"".join(f"<p>{e(x)}</p>" for x in texte_fiche.split(chr(10)) if x.strip())}{prix_l}</div>
      <div class="ag-trio">{('<div class="glass ag-side"><h3>Spécialités</h3><ul class="ag-spes">' + spe + '</ul></div>') if spe else ""}{('<div class="glass ag-side"><h3>Communes couvertes</h3><ul class="ag-comm">' + comm + '</ul></div>') if comm else ""}{('<div class="glass ag-side"><h3>Biens proposés</h3><ul class="ag-types">' + types_l + '</ul>' + (('<ul class="ag-comm ag-kw">' + mots + '</ul>') if a.get("mots_cles") else "") + '</div>') if types_l or a.get("mots_cles") else ""}</div>
    </section>
''' if (texte_fiche or spe or comm) else "") + f'''    {('<section class="section container"><p class="muted small ag-legal">' + e(legal) + '</p></section>') if legal else ""}
    <section class="section container"><div class="glass cta-box"><div><h2>Un projet de vente, de location ou d'estimation ?</h2><p>{e(a["prenom"])} vous répond directement.</p></div><div class="acts"><a class="btn btn-gold btn-lg mag" href="{p2}index.html#estimer">Estimer mon bien {ARROW}</a>{('<a class="btn btn-ghost btn-lg mag" href="tel:' + tel_intl(a["telephone"]) + '">' + PH + e(a["telephone"]) + '</a>') if a.get("telephone") else ""}</div></div></section>'''
    if not ann and not independant(a):     # un gestionnaire, un associé ou un alternant n'a pas d'annonces : pas de rubrique vide
        import re as _re2
        body = _re2.sub(r'    <section class="section container[^"]*" aria-labelledby="ag-ann"[^>]*>.*?</section>\n', "", body, count=1, flags=_re2.S)
    secteurs_txt = ", ".join(a["communes"][:4])
    titre = (f'{nom}, agent immobilier {("à " + secteurs_txt.split(",")[0]) if a["communes"] else ""} | LOTIER' if independant(a) else f'{nom}, {a["role"][:1].lower() + a["role"][1:]} | LOTIER').replace("  ", " ")
    desc = (bio[:150].rsplit(" ", 1)[0] + "…") if len(bio) > 160 else (bio or f'{nom}, {a["role"].lower()} LOTIER Immobilier.' + (f' Secteur : {secteurs_txt}.' if secteurs_txt else '') + ' Coordonnées' + (' et annonces.' if ann else ' et présentation.'))
    if len(desc) < 70: desc = f'{nom}, {a["role"].lower()} LOTIER Immobilier : {desc}' + (f' Secteur : {secteurs_txt}.' if secteurs_txt else ' Agence immobilière à Béziers, Montpellier, Nîmes et Carcassonne.')
    sameas = [u for u in (a.get("reseaux") or {}).values()] + ([a["google"]] if a.get("google") else [])
    person = {"@context": "https://schema.org", "@type": "RealEstateAgent" if independant(a) or a.get("role") == "Gérant" else "Person", "@id": f'{SITE}/nos-agents/{a["slug"]}/#agent', "name": nom, "jobTitle": a["role"], "url": f'{SITE}/nos-agents/{a["slug"]}/',
              "worksFor": {"@id": SITE + "/#agence"}, "parentOrganization": {"@id": SITE + "/#agence"}, "areaServed": [{"@type": "City", "name": c} for c in a["communes"]],
              "knowsAbout": [CAT[s] for s in specialites] + mots_cles, "inLanguage": "fr-FR"}
    if a.get("telephone"): person["telephone"] = tel_intl(a["telephone"])
    if a.get("email"): person["email"] = a["email"]
    if a.get("photo"): person["image"] = f'{SITE}/{a["photo"]}'
    if bio: person["description"] = bio
    if sameas: person["sameAs"] = sameas
    node_page = {"@context": "https://schema.org", "@type": "ProfilePage", "@id": f'{SITE}/nos-agents/{a["slug"]}/#page', "url": f'{SITE}/nos-agents/{a["slug"]}/', "name": titre, "mainEntity": {"@id": person["@id"]}, "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "fr-FR"}
    html = shell(p2, titre, desc, f'nos-agents/{a["slug"]}/', body, [person, node_page, breadcrumb_ld([("Accueil", SITE + "/"), ("Nos agents", SITE + "/nos-agents/"), (nom, f'{SITE}/nos-agents/{a["slug"]}/')])],
                 a["photo"] if a.get("photo") else "assets/og-lotier.jpg", robots=ROBOTS if a.get("rsac") or not independant(a) else "noindex, follow", kind="agence")
    if a.get("mots_cles"):
        html = html.replace('<meta name="robots"', f'<meta name="keywords" content="{e(", ".join(a["mots_cles"]))}">\n  <meta name="robots"', 1)
    ecrire(f'{ROOT}/nos-agents/{a["slug"]}/index.html', avec_script(html, f'{p2}js/agents.js?v={V_AGENTS_JS}') if False else html)

for a in AGENTS: fiche(a)
print(f"agents : page liste + {len(AGENTS)} fiches ({'indexables' if INDEXABLE else 'noindex'})")

# ---------- page « L'équipe » : direction, gestion, syndic, accueil (hors agents commerciaux, qui ont leur page) ----------
_SERVICES = [("direction", "Direction"), ("gestion", "Gestion locative"), ("syndic", "Syndic de copropriété"), ("administratif", "Accueil et administratif")]

def carte_equipe(m):
    contact = ""
    if m.get("telephone"): contact += f'<a href="tel:{tel_intl(m["telephone"])}">{e(m["telephone"])}</a>'
    if m.get("email"): contact += f'<a href="mailto:{e(m["email"])}">{e(m["email"])}</a>'
    bio = clean_bio(m)
    return (f'''<li class="glass eq-card">{portrait(m).replace("{p}", "../")}<div><h3>{e(m["prenom"])} {e(m["nom"])}</h3><p class="small muted">{e(m["role"])}</p>'''
            + (f'<p class="small">{e(bio)}</p>' if bio else "") + (f'<p class="small eq-contact">{contact}</p>' if contact else "") + "</div></li>")

shutil.rmtree(f"{ROOT}/equipe", ignore_errors=True)
if EQUIPE:
    blocs = ""
    for cle, titre_s in _SERVICES:
        membres = [m for m in EQUIPE if m.get("service") == cle]
        if membres:
            blocs += (f'''    <section class="section container" aria-labelledby="eq-{cle}"><div class="section-head"><div class="stack-3"><h2 class="title" id="eq-{cle}">{e(titre_s)}</h2></div></div>
      <ul class="eq-list">{"".join(carte_equipe(m) for m in membres)}</ul>
    </section>
''')
    corps = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="../index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">L’équipe</span></nav>
        <h1 class="display page-title">L’équipe <em class="gold-text">de l’agence.</em></h1>
        <p class="lead">Direction, gestion locative, syndic de copropriété, accueil : celles et ceux qui suivent vos dossiers au quotidien chez LOTIER Immobilier.</p>
      </div>
    </section>
{blocs}    <section class="section container"><div class="glass ag-join"><div><strong>Vous cherchez un conseiller pour vendre ou acheter ?</strong><span class="muted"> Nos agents commerciaux sont présentés par secteur.</span></div><a class="btn btn-gold" href="../nos-agents/">Voir nos agents {ARROW}</a></div></section>'''
    ld_eq = [breadcrumb_ld([("Accueil", SITE + "/"), ("L’équipe", SITE + "/equipe/")]),
             {"@context": "https://schema.org", "@type": "AboutPage", "@id": SITE + "/equipe/#page", "url": SITE + "/equipe/", "name": "L’équipe de LOTIER Immobilier", "inLanguage": "fr-FR",
              "about": {"@id": SITE + "/#agence"},
              "mentions": [{"@type": "Person", "name": f'{m["prenom"]} {m["nom"]}', "jobTitle": m["role"], "worksFor": {"@id": SITE + "/#agence"}} for m in EQUIPE]}]
    ecrire(f"{ROOT}/equipe/index.html", shell("../", "L’équipe de l’agence : direction, gestion, syndic | LOTIER",
           "L’équipe de LOTIER Immobilier : direction, gestion locative, syndic de copropriété et accueil. Les personnes qui suivent vos dossiers au quotidien.",
           "equipe/", corps, ld_eq, "assets/og-lotier.jpg", kind="agence"))
    print(f"page équipe générée ({len(EQUIPE)} membres)")

