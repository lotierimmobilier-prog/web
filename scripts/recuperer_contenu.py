#!/usr/bin/env python3
"""Récupère dans Collab l'instantané des contenus du site (dernier clic sur « Publier ») et l'écrit dans data/contenu.json.

Usage : python3 scripts/recuperer_contenu.py [--numero N] [--empreinte HEX] [--souple]

  --numero N      la publication n° N exactement (le workflow « Publier le site » la reçoit de Collab) ; sinon la plus récente
  --empreinte HEX refuse (code 1) un instantané dont l'empreinte diffère de celle annoncée par Collab
  --souple        (mise à jour de nuit) si Collab ne répond pas ou renvoie n'importe quoi : on garde le data/contenu.json
                  actuel, on le dit, et le travail continue (les annonces ne doivent pas dépendre de Collab)

Lecture publique de Collab (GET, sans clé, lecture seule) : https://collab.lotier-immobilier.com/api/public/v1/site/contenu.
Le fichier écrit ne contient QUE l'empreinte et les contenus (pas le numéro, pas la date) : deux publications identiques
donnent le même fichier, donc aucun commit inutile. Aucune publication encore (numéro 0) : le fichier n'est pas créé et
le générateur garde tous ses textes actuels. Aucun secret ici."""
import argparse, json, sys, time, urllib.error, urllib.request
from pathlib import Path

URL = "https://collab.lotier-immobilier.com/api/public/v1/site/contenu"
SORTIE = Path(__file__).resolve().parent.parent / "data" / "contenu.json"
TENTATIVES = 4


def lire(url):
    derniere = None
    for i in range(TENTATIVES):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "lotier-site-publication"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):      # inutile de réessayer : la demande elle-même est fausse
                raise
            derniere = e
        except Exception as e:  # noqa: BLE001
            derniere = e
        time.sleep(2 ** i)
    raise RuntimeError(f"Collab injoignable après {TENTATIVES} essais : {derniere}")


def valider(d):
    if not isinstance(d, dict) or not isinstance(d.get("contenu"), dict):
        raise ValueError("réponse sans « contenu »")
    c = d["contenu"]
    if c.get("schema") != 1:
        raise ValueError(f"format de contenu inconnu (schema {c.get('schema')!r}, attendu 1)")
    for k in ("articles", "pages", "medias"):
        if not isinstance(c.get(k), list):
            raise ValueError(f"« {k} » absent ou de mauvais type")
    if not isinstance(c.get("reglages"), dict):
        raise ValueError("« reglages » absent ou de mauvais type")
    if not isinstance(d.get("empreinte"), str) or not d["empreinte"]:
        raise ValueError("empreinte absente")
    if not isinstance(d.get("numero"), int):
        raise ValueError("numéro absent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--numero", type=int)
    ap.add_argument("--empreinte")
    ap.add_argument("--souple", action="store_true")
    a = ap.parse_args()
    url = URL + (f"?numero={a.numero}" if a.numero else "")
    try:
        d = lire(url)
        valider(d)
        if a.empreinte and d["empreinte"] != a.empreinte:
            raise ValueError("l'empreinte reçue ne correspond pas à celle annoncée par Collab (publication remplacée entre-temps ?)")
    except Exception as e:  # noqa: BLE001
        if a.souple:
            print(f"::warning::Contenus de Collab non récupérés ({e}) : data/contenu.json conservé tel quel.")
            return
        print(f"RÉCUPÉRATION REFUSÉE — rien n'est publié : {e}", file=sys.stderr)
        sys.exit(1)

    if d["numero"] == 0:
        print("Aucune publication dans Collab : le site garde tous ses textes actuels.")
        return
    texte = json.dumps({"empreinte": d["empreinte"], "contenu": d["contenu"]}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if SORTIE.exists() and SORTIE.read_text(encoding="utf-8") == texte:
        print(f"Publication n° {d['numero']} : contenus identiques, data/contenu.json inchangé.")
        return
    SORTIE.write_text(texte, encoding="utf-8")
    print(f"Publication n° {d['numero']} : data/contenu.json écrit.")


if __name__ == "__main__":
    main()
