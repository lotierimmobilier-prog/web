#!/usr/bin/env python3
"""Audit SEO du site statique : contrôle chaque page indexable et écrit data/seo-report.json.
Usage : python3 scripts/seo_audit.py            (écrit le rapport et affiche un résumé)
        python3 scripts/seo_audit.py --strict   (code de sortie 1 s'il reste des erreurs)
Le rapport est lisible par Collab (https://lotier.immo/data/seo-report.json). Aucune date n'y figure :
relancer l'audit sans modifier le site ne change pas le fichier."""
import glob, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote, urljoin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://lotier.immo"
SKIP_DIRS = ("v2/", "audit-lotier/", "mise-en-ligne/", "scripts/", ".claude/", "node_modules/", "release/")

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.title = ""; s.in_title = False; s.meta = {}; s.canon = None; s.h = []; s.cur = None
        s.imgs_no_alt = 0; s.imgs = 0; s.ld = []; s.in_ld = False; s.links = []; s.text = []
        s.lang = None; s.skip = 0; s.alt_md = False; s.in_main = False
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "html": s.lang = a.get("lang")
        elif tag == "title": s.in_title = True
        elif tag == "meta" and a.get("name"): s.meta[a["name"].lower()] = a.get("content", "")
        elif tag == "meta" and a.get("property"): s.meta[a["property"].lower()] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical": s.canon = a.get("href")
        elif tag == "link" and a.get("rel") == "alternate" and a.get("type") == "text/markdown": s.alt_md = True
        elif tag in ("h1", "h2", "h3"): s.cur = [tag, ""]
        elif tag == "img":
            s.imgs += 1
            if "alt" not in a: s.imgs_no_alt += 1
        elif tag == "a" and a.get("href"): s.links.append(a["href"])
        elif tag == "script" and a.get("type") == "application/ld+json": s.in_ld = True; s.ld.append("")
        elif tag in ("script", "style", "svg"): s.skip += 1
        elif tag == "main": s.in_main = True
    def handle_endtag(s, tag):
        if tag == "title": s.in_title = False
        elif tag in ("h1", "h2", "h3") and s.cur: s.h.append(s.cur); s.cur = None
        elif tag == "script":
            if s.in_ld: s.in_ld = False
            else: s.skip = max(0, s.skip - 1)
        elif tag in ("style", "svg"): s.skip = max(0, s.skip - 1)
    def handle_data(s, d):
        if s.in_title: s.title += d
        if s.in_ld and s.ld: s.ld[-1] += d; return
        if s.cur is not None: s.cur[1] += d
        if s.in_main and not s.skip: s.text.append(d)

def url_for(rel):
    if rel == "index.html": return SITE + "/"
    if rel.endswith("/index.html"): return SITE + "/" + rel[:-10]
    return SITE + "/" + rel

def target_exists(base_rel, href):
    u = urlparse(href); path = unquote(u.path)
    if not path: return True
    full = os.path.normpath(os.path.join(ROOT, path.lstrip("/"))) if path.startswith("/") else os.path.normpath(os.path.join(ROOT, os.path.dirname(base_rel), path))
    if os.path.isdir(full): full = os.path.join(full, "index.html")
    return os.path.exists(full)

def main():
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    in_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    pages = []; seen_titles = {}; seen_desc = {}
    files = sorted(glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True))
    for f in files:
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        if rel.startswith(SKIP_DIRS) or rel == "404.html": continue
        t = open(f, encoding="utf-8").read(); p = P(); p.feed(t)
        robots = p.meta.get("robots", "")
        indexable = "noindex" not in robots.lower()
        url = url_for(rel); issues = []
        def add(level, code, msg): issues.append({"niveau": level, "code": code, "message": msg})
        title = p.title.strip(); desc = p.meta.get("description", "").strip()
        if not title: add("erreur", "title-absent", "Balise title absente.")
        elif len(title) > 65: add("avertissement", "title-long", f"Titre de {len(title)} caractères (65 conseillés au maximum).")
        elif len(title) < 25: add("avertissement", "title-court", f"Titre de {len(title)} caractères (25 conseillés au minimum).")
        if not desc: add("erreur", "description-absente", "Meta description absente.")
        elif len(desc) > 170: add("avertissement", "description-longue", f"Description de {len(desc)} caractères (170 au maximum).")
        elif len(desc) < 70: add("avertissement", "description-courte", f"Description de {len(desc)} caractères (70 au minimum).")
        h1 = [h for h in p.h if h[0] == "h1"]
        if len(h1) != 1: add("erreur", "h1", f"{len(h1)} titres H1 (un seul attendu).")
        if p.canon not in (url, url + "index.html"): add("erreur", "canonical", f"Canonical « {p.canon} » différent de l'adresse attendue « {url} ».")
        if p.lang != "fr": add("avertissement", "lang", "Attribut lang=fr absent.")
        if p.imgs_no_alt: add("erreur", "alt", f"{p.imgs_no_alt} image(s) sans attribut alt.")
        for blob in p.ld:
            try: json.loads(blob)
            except Exception: add("erreur", "jsonld", "Données structurées JSON-LD invalides.")
        if indexable and not p.ld: add("avertissement", "jsonld-absent", "Aucune donnée structurée.")
        if indexable and not ({url, url + "index.html"} & in_sitemap): add("erreur", "hors-sitemap", "Page indexable absente du sitemap.")
        if not indexable and {url, url + "index.html"} & in_sitemap: add("erreur", "sitemap-noindex", "Page noindex présente dans le sitemap.")
        if "og:image" not in p.meta and indexable: add("avertissement", "og-image", "Image de partage (og:image) absente.")
        broken = sorted({h for h in p.links if not re.match(r"(https?:|mailto:|tel:|#|data:|javascript:)", h) and not target_exists(rel, h)})
        for h in broken: add("erreur", "lien-casse", f"Lien interne cassé : {h}")
        words = len(re.findall(r"\w+", " ".join(p.text)))
        if indexable and words < 150: add("avertissement", "contenu-court", f"Contenu court ({words} mots).")
        if indexable: seen_titles.setdefault(title, []).append(url); seen_desc.setdefault(desc, []).append(url)
        pages.append({"url": url, "fichier": rel, "indexable": indexable, "titre": title, "description": desc, "mots": words,
                      "h1": h1[0][1].strip() if h1 else "", "nb_h2": sum(1 for h in p.h if h[0] == "h2"), "images": p.imgs, "liens": len(p.links),
                      "markdown": os.path.exists(f[:-5] + ".md"), "problemes": issues})
    for table, code, label in ((seen_titles, "title-doublon", "Titre"), (seen_desc, "description-doublon", "Description")):
        for k, urls in table.items():
            if k and len(urls) > 1:
                for pg in pages:
                    if pg["url"] in urls: pg["problemes"].append({"niveau": "avertissement", "code": code, "message": f"{label} identique sur {len(urls)} pages."})
    idx = [p for p in pages if p["indexable"]]
    err = sum(1 for p in pages for i in p["problemes"] if i["niveau"] == "erreur")
    warn = sum(1 for p in pages for i in p["problemes"] if i["niveau"] == "avertissement")
    codes = {}
    for p in pages:
        for i in p["problemes"]: codes[i["code"]] = codes.get(i["code"], 0) + 1
    # Fichiers de référencement
    def has(path): return os.path.exists(os.path.join(ROOT, path))
    robots_txt = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read() if has("robots.txt") else ""
    sitewide = {"robots.txt": has("robots.txt"), "sitemap.xml": has("sitemap.xml"), "llms.txt": has("llms.txt"),
                "robots_declare_sitemap": "Sitemap:" in robots_txt, "content_signal": "Content-Signal:" in robots_txt,
                "carte_serveur_mcp": has(".well-known/mcp/server-card.json"), "pages_markdown": sum(1 for p in pages if p["markdown"])}
    report = {"version": 1, "site": SITE,
              "resume": {"pages_auditees": len(pages), "pages_indexables": len(idx), "erreurs": err, "avertissements": warn,
                         "pages_sans_probleme": sum(1 for p in pages if not p["problemes"]), "problemes_par_type": dict(sorted(codes.items()))},
              "fichiers": sitewide, "pages": pages}
    out = os.path.join(ROOT, "data", "seo-report.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1); fh.write("\n")
    r = report["resume"]
    print(f"{r['pages_auditees']} pages ({r['pages_indexables']} indexables) : {r['erreurs']} erreur(s), {r['avertissements']} avertissement(s).")
    for k, v in r["problemes_par_type"].items(): print(f"  {k}: {v}")
    sys.exit(1 if "--strict" in sys.argv and err else 0)

main()
