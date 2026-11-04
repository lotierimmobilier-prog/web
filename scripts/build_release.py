#!/usr/bin/env python3
"""Prépare le dossier release/ à déposer à la RACINE de l'hébergement.

- retire la balise noindex,
- remplace les URLs /v2/ par la racine (canonical, sitemap),
- écrit sitemap-v2.xml (le sitemap WordPress wp-sitemap.xml reste en place).
Usage : python3 scripts/build_release.py
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "v2", ROOT / "release"
if DST.exists():
    shutil.rmtree(DST)
shutil.copytree(SRC, DST)

n_html = 0
for p in DST.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    t = re.sub(r'<meta name="robots" content="noindex, nofollow">(<!--.*?-->)?\n?', "", t)
    t = t.replace("https://www.lotier-immobilier.com/v2/", "https://www.lotier-immobilier.com/")
    p.write_text(t, encoding="utf-8")
    n_html += 1

sm = (DST / "sitemap.xml").read_text(encoding="utf-8").replace("/v2/", "/")
(DST / "sitemap-v2.xml").write_text(sm, encoding="utf-8")
(DST / "sitemap.xml").unlink()   # ne pas masquer le sitemap WordPress

bad = [str(p) for p in DST.rglob("*.html") if "noindex" in p.read_text(encoding="utf-8") or "/v2/" in p.read_text(encoding="utf-8")]
if bad:
    sys.exit("Erreur : noindex ou /v2/ restant dans : " + ", ".join(bad))
print(f"release/ prêt : {n_html} pages HTML, noindex retiré, URLs à la racine.")
print("Dossiers à vérifier contre ceux de l'hébergement :", ", ".join(sorted(d.name for d in DST.iterdir() if d.is_dir())))
