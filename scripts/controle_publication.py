#!/usr/bin/env python3
"""Garde-fous de la PUBLICATION depuis Collab (.github/workflows/publier-site.yml).

Usage : python3 scripts/controle_publication.py [fichier du message de commit]

À lancer APRÈS la régénération du site, AVANT le commit. Compare le site régénéré au dernier commit (HEAD) :
  1. REFUSE (code 1, rien n'est publié) si une page essentielle manque, est vide ou n'a pas de <title> / <h1> ;
  2. REFUSE si le site perd plus de 10 % de ses pages d'un coup (une panne de contenu ressemble à ça) ;
  3. REFUSE si une page NOUVELLE ou MODIFIÉE n'a pas de <title>, pas de <h1>, ou renvoie vers une page interne inexistante ;
  4. REFUSE si data/contenu.json existe mais n'a pas le format attendu (voir scripts/recuperer_contenu.py).
Sinon écrit, dans le fichier de message, la liste lisible des pages ajoutées, modifiées et retirées.
Aucun secret, aucune écriture hors du fichier de message."""
import json, os, re, subprocess, sys
from pathlib import Path
from urllib.parse import unquote, urlparse

RACINE = Path(__file__).resolve().parent.parent
ESSENTIELLES = ["index.html", "vente/index.html", "location/index.html", "syndic/index.html", "a-propos/index.html",
                "contact/index.html", "blog/index.html", "mentions-legales/index.html", "sitemap.xml", "robots.txt", "llms.txt"]
BAISSE_PAGES_MAX = 0.10
IGNORES = ("v2/", "release/", "audit-lotier/", "mise-en-ligne/", "scripts/", ".github/", "node_modules/")


def git(*args):
    return subprocess.run(["git", *args], cwd=RACINE, capture_output=True, text=True, check=True).stdout


def pages_head():
    sortie = git("ls-tree", "-r", "--name-only", "HEAD")
    return {p for p in sortie.splitlines() if p.endswith(".html") and not p.startswith(IGNORES)}


def pages_maintenant():
    return {str(p.relative_to(RACINE)) for p in RACINE.rglob("*.html")
            if not str(p.relative_to(RACINE)).startswith(IGNORES) and "node_modules" not in p.parts}


def modifiees():
    """Pages HTML nouvelles ou modifiées par la régénération (d'après git)."""
    s = git("status", "--porcelain", "--untracked-files=all")
    out = set()
    for ligne in s.splitlines():
        chemin = ligne[3:].strip().strip('"')
        if chemin.endswith(".html") and not chemin.startswith(IGNORES):
            out.add(chemin)
    return out


LIEN_SANS_PAGE = re.compile(r'^(https?:|mailto:|tel:|#|data:|javascript:|sms:|whatsapp:|\+?[\d\s.]+$)')


def liens_casses(chemin):
    html = (RACINE / chemin).read_text(encoding="utf-8")
    base = (RACINE / chemin).parent
    cassés = []
    for m in re.findall(r'(?:href|src)="([^"]+)"', html):
        if LIEN_SANS_PAGE.match(m):
            continue
        p = unquote(urlparse(m).path)
        if not p:
            continue
        cible = (RACINE / p.lstrip("/")) if p.startswith("/") else (base / p)
        cible = Path(os.path.normpath(cible))
        if cible.is_dir():
            cible = cible / "index.html"
        if not cible.exists():
            cassés.append(m)
    return cassés


def controler_contenu():
    p = RACINE / "data" / "contenu.json"
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — on veut le message, pas la pile
        return [f"data/contenu.json illisible : {e}"]
    c = d.get("contenu") if isinstance(d, dict) else None
    if not isinstance(c, dict) or c.get("schema") != 1:
        return ["data/contenu.json : format inconnu (schema attendu : 1)"]
    mal = [k for k in ("articles", "pages", "medias") if not isinstance(c.get(k), list)]
    if not isinstance(c.get("reglages"), dict):
        mal.append("reglages")
    return [f"data/contenu.json : « {k} » absent ou de mauvais type" for k in mal]


def main():
    msg_p = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    erreurs = []
    avant, apres = pages_head(), pages_maintenant()

    for e in ESSENTIELLES:
        f = RACINE / e
        if not f.exists() or f.stat().st_size < 200:
            erreurs.append(f"page essentielle absente ou vide : {e}")
            continue
        if e.endswith(".html"):
            t = f.read_text(encoding="utf-8")
            if not re.search(r"<title>[^<]{3,}</title>", t) or "<h1" not in t:
                erreurs.append(f"page essentielle sans titre ou sans <h1> : {e}")

    if avant and len(apres) < len(avant) * (1 - BAISSE_PAGES_MAX):
        erreurs.append(f"{len(apres)} pages contre {len(avant)} avant : baisse de plus de {int(BAISSE_PAGES_MAX * 100)} %")

    touchees = modifiees() & apres
    for ch in sorted(touchees):
        t = (RACINE / ch).read_text(encoding="utf-8")
        if not re.search(r"<title>[^<]{3,}</title>", t):
            erreurs.append(f"{ch} : pas de <title>")
        if "<h1" not in t:
            erreurs.append(f"{ch} : pas de <h1>")
        for lien in liens_casses(ch)[:5]:
            erreurs.append(f"{ch} : lien interne cassé → {lien}")

    erreurs += controler_contenu()

    if erreurs:
        print("PUBLICATION REFUSÉE — rien n'est publié, le site en ligne ne change pas :", *erreurs, sep="\n  - ", file=sys.stderr)
        sys.exit(1)

    ajoutees = sorted(apres - avant)
    retirees = sorted(avant - apres)
    changees = sorted((touchees & avant & apres))
    print(f"Contrôles OK : {len(apres)} pages ; {len(ajoutees)} ajoutée(s), {len(changees)} modifiée(s), {len(retirees)} retirée(s).")
    if msg_p:
        lignes = ["Contenus : publication depuis Collab", ""]
        for titre, liste in (("Pages ajoutées", ajoutees), ("Pages retirées", retirees)):
            if liste:
                lignes.append(f"{titre} ({len(liste)}) :")
                lignes += [f"  - {p}" for p in liste[:30]] + ([f"  … et {len(liste) - 30} autres"] if len(liste) > 30 else [])
        lignes.append(f"Pages modifiées : {len(changees)}")
        msg_p.write_text("\n".join(lignes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
