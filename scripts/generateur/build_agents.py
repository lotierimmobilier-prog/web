# -*- coding: utf-8 -*-
import os, json
from common import *
prefix = "../"
NOINDEX = "noindex, follow"
DATA = json.load(open(f"{ROOT}/data/agents.json", encoding="utf-8"))
SECT = DATA["secteurs"]
AGENTS = DATA["agents"]
MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/></svg>'
SITE_ICO = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>'

def initials(n): return "".join(w[0] for w in n.split()[:2]).upper()

def card(a):
    tel = a.get("telephone", "")
    tel_raw = "".join(ch for ch in tel if ch.isdigit() or ch == "+")
    names = {s["id"]: s["nom"] for s in SECT}
    tags = "".join(f'<span class="tag">{e(names[s])}</span>' for s in a["secteurs"] if s in names)
    photo = f'<img class="agent-photo" src="{prefix}{e(a["photo"])}" alt="" width="72" height="72" loading="lazy">' if a.get("photo") else f'<span class="agent-photo agent-ini" aria-hidden="true">{e(initials(a["nom"]))}</span>'
    rows = ""
    if tel: rows += f'<a href="tel:{tel_raw}">{PH}{e(tel)}</a>'
    if a.get("email"): rows += f'<a href="mailto:{e(a["email"])}">{MAIL}{e(a["email"])}</a>'
    if a.get("site"): rows += f'<a href="{e(a["site"])}" target="_blank" rel="noopener">{SITE_ICO}Voir le mini-site</a>'
    comm = f'<p class="small muted">{e(a["communes"])}</p>' if a.get("communes") else ""
    role = f'<p class="small muted">{e(a["role"])}</p>' if a.get("role") else ""
    return f'''<article class="glass agent-card">
            <div class="agent-head">{photo}<div><h3>{e(a["nom"])}</h3>{role}</div></div>
            <div class="tags">{tags}</div>{comm}
            <div class="agent-links">{rows}</div>
          </article>'''

chips = '<button type="button" class="chip-link is-on" data-sect="all" aria-pressed="true">Tous les secteurs</button>' + "".join(
    f'<button type="button" class="chip-link" data-sect="{s["id"]}" aria-pressed="false">{e(s["nom"])}</button>' for s in SECT)

sections = ""
for s in SECT:
    ag = [a for a in AGENTS if s["id"] in a["secteurs"]]
    inner = "".join(card(a) for a in ag) if ag else f'<p class="muted agent-empty">Aucun agent référencé sur ce secteur pour le moment. <a class="text-link" href="{prefix}index.html#contact">Contacter l\'agence</a>.</p>'
    sections += f'''
      <section class="agent-sect" data-sect="{s["id"]}" aria-labelledby="s-{s["id"]}">
        <h2 class="heading" id="s-{s["id"]}">{e(s["nom"])} <span class="muted small">{e(s["dept"])}</span></h2>
        <div class="agent-grid">{inner}</div>
      </section>'''

body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Nos agents</span></nav>
        <h1 class="display page-title">Nos agents, <em class="gold-text">près de chez vous.</em></h1>
        <p class="lead">Chaque agent LOTIER connaît son secteur. Trouvez le vôtre, appelez-le ou écrivez-lui directement.</p>
      </div>
    </section>

    <section class="section container" id="agents-liste" aria-label="Liste des agents par secteur">
      <div class="chip-links agents-filter" role="group" aria-label="Filtrer par secteur">{chips}</div>
      <div class="agent-sects" data-src="{prefix}data/agents.json">{sections}</div>
      <p class="muted small" style="margin-top:32px">Vous ne trouvez pas votre secteur ? <a class="text-link" href="{prefix}index.html#contact">Contactez l'agence</a>, nous vous orienterons vers le bon conseiller.</p>
    </section>'''
ld = [breadcrumb_ld([("Accueil", SITE + "/"), ("Nos agents", SITE + "/nos-agents/")])]
robots = NOINDEX if not AGENTS else "index, follow, max-image-preview:large, max-snippet:-1"
os.makedirs(f"{ROOT}/nos-agents", exist_ok=True)
open(f"{ROOT}/nos-agents/index.html", "w", encoding="utf-8").write(
    shell(prefix, "Nos agents par secteur | LOTIER Immobilier", "Les agents LOTIER Immobilier par secteur : coordonnées, e-mail, téléphone et mini-site de chaque conseiller.", "nos-agents/", body, ld, "assets/og-lotier.jpg", robots=robots, kind="agence"))
print("agents généré", len(AGENTS), "agents")
