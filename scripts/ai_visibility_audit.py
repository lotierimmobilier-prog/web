#!/usr/bin/env python3
"""Audit « visibilité dans les IA » : le site est-il lisible, accessible et citable par les assistants IA ?
Usage : python3 scripts/ai_visibility_audit.py          (écrit data/ai-visibility-report.json)
        python3 scripts/ai_visibility_audit.py --live   (ajoute un contrôle du site en ligne, sans l'écrire dans le rapport)
Le rapport est lisible par Collab (https://lotier.immo/data/ai-visibility-report.json). Pas de date dans le
fichier : relancer sans changement du site ne le modifie pas."""
import glob, json, os, re, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://lotier.immo"
SKIP = ("v2/", "audit-lotier/", "mise-en-ligne/", "scripts/", ".claude/", "node_modules/", "release/", "mylotier/")

# Robots des assistants IA connus : (nom exact dans robots.txt, éditeur, rôle)
BOTS = [
    ("OAI-SearchBot", "OpenAI", "recherche"), ("ChatGPT-User", "OpenAI", "consultation à la demande"), ("GPTBot", "OpenAI", "entraînement"),
    ("Claude-SearchBot", "Anthropic", "recherche"), ("Claude-User", "Anthropic", "consultation à la demande"), ("ClaudeBot", "Anthropic", "entraînement"),
    ("PerplexityBot", "Perplexity", "recherche"), ("Perplexity-User", "Perplexity", "consultation à la demande"),
    ("Google-Extended", "Google", "entraînement Gemini (n'affecte pas la recherche Google)"), ("Applebot-Extended", "Apple", "entraînement"),
    ("CCBot", "Common Crawl", "entraînement"), ("Bytespider", "ByteDance", "entraînement"), ("Meta-ExternalAgent", "Meta", "entraînement"),
]

def read(rel):
    p = os.path.join(ROOT, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None

def parse_robots(txt):
    groups, cur, last_was_agent = [], None, False
    for raw in (txt or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line: continue
        k, v = [s.strip() for s in line.split(":", 1)]; k = k.lower()
        if k == "user-agent":
            if not last_was_agent: cur = {"agents": [], "rules": []}; groups.append(cur)
            cur["agents"].append(v.lower()); last_was_agent = True
        else:
            last_was_agent = False
            if cur is not None and k in ("allow", "disallow"): cur["rules"].append((k, v))
    return groups

def _matches(pattern, path):
    """Motif robots.txt (RFC 9309) : « * » = suite de caractères, « $ » = fin de l'adresse."""
    rx = re.escape(pattern).replace(r"\*", ".*")
    if rx.endswith(r"\$"): rx = rx[:-2] + "$"
    return re.match(rx, path) is not None

def allowed(groups, bot, paths=("/", "/blog/index.html")):
    """Le robot peut-il lire le site ? (groupe précis, sinon groupe « * » ; règle la plus longue gagne, « Allow » en cas d'égalité)."""
    g = next((x for x in groups if bot.lower() in x["agents"]), None) or next((x for x in groups if "*" in x["agents"]), None)
    if g is None: return True, "aucune règle (autorisé par défaut)"
    verdict = True
    for path in paths:
        best, ok = -1, True  # sans règle applicable : autorisé
        for k, v in g["rules"]:
            if v and _matches(v, path):
                n = len(v)
                if n > best or (n == best and k == "allow"): best, ok = n, (k == "allow")
        verdict = verdict and ok
    explicit = any(bot.lower() in x["agents"] for x in groups)
    return verdict, ("règle explicite" if explicit else "règle générale (*)")

def jsonld_types(html):
    out = set()
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try: data = json.loads(blob)
        except Exception: continue
        stack = [data]
        while stack:
            d = stack.pop()
            if isinstance(d, dict):
                t = d.get("@type"); out.update([t] if isinstance(t, str) else (t or []))
                stack.extend(d.values())
            elif isinstance(d, list): stack.extend(d)
    return out

def main():
    robots = read("robots.txt"); groups = parse_robots(robots)
    bots = []
    for name, vendor, role in BOTS:
        ok, why = allowed(groups, name); bots.append({"robot": name, "editeur": vendor, "role": role, "autorise": ok, "regle": why})
    search_bots = [b for b in bots if b["role"] in ("recherche", "consultation à la demande")]

    llms = read("llms.txt") or ""
    llms_links = re.findall(r"\]\((https://lotier\.immo[^)#\s]*)", llms)
    def local(u):
        path = urlparse(u).path
        f = os.path.join(ROOT, path.lstrip("/")); return os.path.exists(f) or os.path.exists(os.path.join(f, "index.html")) or u.rstrip("/") == SITE or path.endswith("/") and os.path.isdir(f)
    broken_llms = [u for u in llms_links if not local(u) and not u.endswith("/mcp/")]

    pages = []
    for f in sorted(glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True)):
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        if rel.startswith(SKIP) or rel == "404.html": continue
        html = open(f, encoding="utf-8").read()
        if "noindex" in (re.search(r'<meta name="robots" content="([^"]*)"', html) or [0, ""])[1]: continue
        types = jsonld_types(html)
        kind = "accueil" if rel == "index.html" else "article" if rel.startswith("blog/") and rel != "blog/index.html" else "ville" if rel.startswith("agence-immobiliere-") else "service" if rel.split("/")[0] in ("vente", "location", "syndic", "notre-service", "nos-honoraires") else "autre"
        issues = []
        if not os.path.exists(f[:-5] + ".md"): issues.append("pas de version Markdown")
        if not types: issues.append("aucune donnée structurée")
        if kind == "article":
            if not types & {"Article", "BlogPosting"}: issues.append("article sans balisage Article")
            if '"dateModified"' not in html and '"datePublished"' not in html: issues.append("date de publication absente du balisage")
            if "author" not in html.lower(): issues.append("auteur absent")
        if kind == "accueil" and "RealEstateAgent" not in types: issues.append("fiche d'entreprise absente")
        if kind in ("accueil", "ville", "service") and "FAQPage" not in types: issues.append("pas de FAQ balisée (FAQPage)")
        pages.append({"url": SITE + "/" + (rel[:-10] if rel.endswith("index.html") else rel), "type": kind, "balisage": sorted(t for t in types if isinstance(t, str)),
                      "markdown": os.path.exists(f[:-5] + ".md"), "problemes": issues})

    n = max(1, len(pages))
    md_cov = sum(p["markdown"] for p in pages) / n
    ld_cov = sum(1 for p in pages if p["balisage"]) / n
    checks = [
        ("Les robots de recherche et de consultation IA sont autorisés", all(b["autorise"] for b in search_bots), 20),
        ("Content-Signal déclaré dans robots.txt", bool(robots and "Content-Signal:" in robots), 8),
        ("llms.txt présent, avec titre et résumé", llms.startswith("# ") and "\n> " in llms, 12),
        ("Liens de llms.txt valides", not broken_llms, 5),
        ("Version Markdown de toutes les pages indexables", md_cov == 1, 15),
        ("Données structurées sur toutes les pages", ld_cov == 1, 15),
        ("Fiche d'entreprise (RealEstateAgent) sur l'accueil", any(p["type"] == "accueil" and "RealEstateAgent" in p["balisage"] for p in pages), 8),
        ("Carte de serveur MCP publiée", os.path.exists(os.path.join(ROOT, ".well-known/mcp/server-card.json")), 5),
        ("Outils WebMCP déclarés", "registerTool" in (read("js/main.js") or ""), 4),
        ("Sitemap déclaré dans robots.txt", bool(robots and "Sitemap:" in robots), 4),
        ("Pages importantes avec FAQ balisée", all("pas de FAQ balisée (FAQPage)" not in p["problemes"] for p in pages if p["type"] in ("accueil", "ville")), 4),
    ]
    score = sum(w for _, ok, w in checks if ok)
    training = [b["robot"] for b in bots if b["role"].startswith("entra") and b["autorise"]]
    report = {"version": 1, "site": SITE, "score": score, "score_max": sum(w for *_, w in checks),
              "controles": [{"libelle": l, "reussi": bool(ok), "points": w} for l, ok, w in checks],
              "robots_ia": bots, "entrainement_autorise_pour": training,
              "note_entrainement": "Content-Signal ai-train=no demande aux robots de ne pas entraîner de modèle, mais robots.txt autorise encore ces robots d'entraînement : décision éditoriale à confirmer.",
              "llms_txt": {"present": bool(llms), "liens": len(llms_links), "liens_invalides": broken_llms},
              "couverture": {"pages_indexables": len(pages), "markdown": round(md_cov, 3), "donnees_structurees": round(ld_cov, 3)},
              "pages": pages}
    out = os.path.join(ROOT, "data", "ai-visibility-report.json")
    with open(out, "w", encoding="utf-8") as fh: json.dump(report, fh, ensure_ascii=False, indent=1); fh.write("\n")
    print(f"Visibilité IA : {score}/{report['score_max']}")
    for l, ok, w in checks: print(("  OK   " if ok else "  À VOIR ") + l)
    if training: print("  Robots d'entraînement autorisés :", ", ".join(training))
    if "--live" in sys.argv: live()

def live():
    import urllib.request
    def get(path, headers=None):
        req = urllib.request.Request(SITE + path, headers=headers or {})
        with urllib.request.urlopen(req, timeout=20) as r: return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read(2000).decode("utf-8", "replace")
    print("Contrôle en ligne :")
    for label, fn in (("Markdown à la demande", lambda: get("/", {"Accept": "text/markdown"})[1].get("content-type", "").startswith("text/markdown")),
                      ("En-tête Link sur l'accueil", lambda: "llms.txt" in get("/")[1].get("link", "")),
                      ("Carte de serveur MCP", lambda: get("/.well-known/mcp/server-card.json")[0] == 200),
                      ("llms.txt", lambda: get("/llms.txt")[0] == 200)):
        try: print(("  OK   " if fn() else "  ÉCHEC ") + label)
        except Exception as e: print(f"  ÉCHEC {label} ({e})")

main()
