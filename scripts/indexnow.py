#!/usr/bin/env python3
"""Prévient les moteurs de recherche (protocole IndexNow : Bing, Yandex, Seznam, Naver…) des pages qui viennent de changer.

Usage : python3 scripts/indexnow.py <commit d'avant> [<commit d'après>]     (par défaut : HEAD)
        python3 scripts/indexnow.py --tout                                  (toutes les adresses du sitemap)
        ajouter --essai pour afficher la liste sans rien envoyer.

Les pages modifiées, créées ou supprimées entre les deux commits sont converties en adresses publiques et envoyées en une
requête. La clé n'est pas un secret : le protocole demande qu'elle soit lisible à la racine du site (fichier <clé>.txt).
Aucune donnée personnelle n'est envoyée. Un échec n'est jamais bloquant : le script se termine toujours avec le code 0."""
import json, re, subprocess, sys, urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
HOTE = "lotier.immo"
SITE = f"https://{HOTE}"
EXCLUS = ("v2/", "audit-lotier/", "mise-en-ligne/", "scripts/", "mylotier/", "node_modules/", ".claude/", ".github/")
MAX = 10000


def cle():
    """La clé est le nom du fichier <clé>.txt posé à la racine (32 caractères hexadécimaux), dont le contenu est la clé elle-même."""
    for f in sorted(RACINE.glob("*.txt")):
        if re.fullmatch(r"[0-9a-f]{32}", f.stem) and f.read_text(encoding="utf-8").strip() == f.stem:
            return f.stem
    return None


def adresse(chemin):
    """Chemin d'un fichier du dépôt -> adresse publique, ou None si ce n'est pas une page."""
    if not chemin.endswith(".html") or chemin.startswith(EXCLUS) or chemin == "404.html":
        return None
    if chemin == "index.html":
        return SITE + "/"
    if chemin.endswith("/index.html"):
        return f"{SITE}/{chemin[:-10]}"
    return f"{SITE}/{chemin}"


def pages_changees(avant, apres):
    r = subprocess.run(["git", "diff", "--name-only", avant, apres], cwd=RACINE, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"IndexNow : comparaison impossible ({r.stderr.strip()[:200]}).")
        return []
    return [u for u in (adresse(l.strip()) for l in r.stdout.splitlines()) if u]


def pages_du_sitemap():
    try:
        return re.findall(r"<loc>([^<]+)</loc>", (RACINE / "sitemap.xml").read_text(encoding="utf-8"))
    except OSError:
        return []


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    essai = "--essai" in sys.argv
    if "--tout" in sys.argv:
        urls = pages_du_sitemap()
    elif args:
        urls = pages_changees(args[0], args[1] if len(args) > 1 else "HEAD")
    else:
        print(__doc__)
        return
    urls = sorted(set(urls))[:MAX]
    k = cle()
    if not urls:
        print("IndexNow : aucune page à signaler.")
        return
    if not k:
        print("IndexNow : fichier de clé introuvable à la racine, rien n'est envoyé.")
        return
    print(f"IndexNow : {len(urls)} adresse(s) à signaler.")
    for u in urls[:15]:
        print("  ", u)
    if essai:
        print("Essai : rien n'est envoyé.")
        return
    corps = json.dumps({"host": HOTE, "key": k, "keyLocation": f"{SITE}/{k}.txt", "urlList": urls}).encode("utf-8")
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=corps, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "lotier-immo-indexnow"})
    try:
        with urllib.request.urlopen(req, timeout=30) as rep:
            print(f"IndexNow : réponse {rep.status} (200 ou 202 = bien reçu).")
    except Exception as e:  # noqa: BLE001 : un échec ne doit jamais bloquer une publication
        print(f"::warning::IndexNow : envoi non abouti ({e}). Les moteurs passeront par le sitemap.")


if __name__ == "__main__":
    main()
