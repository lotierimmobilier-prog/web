#!/usr/bin/env python3
"""Garde-fou de la mise à jour automatique des annonces (.github/workflows/maj-annonces.yml).

Usage : python3 scripts/controle_maj.py <data/annonces.json d'avant le scraper> [fichier du message de commit]

Lit l'ancien et le nouveau data/annonces.json et :
  1. REFUSE (code 1, rien n'est publié) si le résultat ressemble à une panne de WordPress, pas à une vraie évolution :
     - moins de 30 annonces, ou plus de 25 % d'annonces en moins qu'avant ;
     - plus de 10 % de fiches détaillées en moins qu'avant (fiche illisible = page de détail supprimée) ;
     - une annonce sur cinq (ou plus) sans photo.
  2. si SEULE la date « maj » change, remet l'ancien fichier (pas de commit quotidien pour rien) ;
  3. sinon écrit un message de commit lisible : annonces ajoutées, retirées, prix modifiés.
Aucun secret, aucune écriture hors de data/annonces.json et du fichier de message."""
import json, sys
from pathlib import Path

NOUVEAU = Path(__file__).resolve().parent.parent / "data" / "annonces.json"
MIN_ANNONCES = 30
BAISSE_MAX = 0.25          # part maximale d'annonces qui peuvent disparaître en une nuit
BAISSE_FICHES_MAX = 0.10   # idem pour les fiches détaillées (description lue)
SANS_PHOTO_MAX = 0.20


def charger(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage : controle_maj.py <ancien annonces.json> [fichier message]")
    ancien_p = Path(sys.argv[1]); msg_p = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    ancien, nouveau = charger(ancien_p), charger(NOUVEAU)
    a_old = {a["id"]: a for a in ancien.get("annonces", [])}
    a_new = {a["id"]: a for a in nouveau.get("annonces", [])}
    n_old, n_new = len(a_old), len(a_new)

    erreurs = []
    if n_new < MIN_ANNONCES:
        erreurs.append(f"seulement {n_new} annonces (minimum {MIN_ANNONCES})")
    if n_old and n_new < n_old * (1 - BAISSE_MAX):
        erreurs.append(f"{n_new} annonces contre {n_old} avant : baisse de plus de {int(BAISSE_MAX * 100)} %")
    d_old = sum(1 for a in a_old.values() if a.get("description_html") is not None)
    d_new = sum(1 for a in a_new.values() if a.get("description_html") is not None)
    if d_old and d_new < d_old * (1 - BAISSE_FICHES_MAX):
        erreurs.append(f"{d_new} fiches détaillées contre {d_old} avant : baisse de plus de {int(BAISSE_FICHES_MAX * 100)} %")
    sans_photo = sum(1 for a in a_new.values() if not a.get("photo"))
    if n_new and sans_photo / n_new >= SANS_PHOTO_MAX:
        erreurs.append(f"{sans_photo} annonces sur {n_new} sans photo")
    if erreurs:
        print("MISE À JOUR REFUSÉE — rien n'est publié :", *erreurs, sep="\n  - ", file=sys.stderr)
        sys.exit(1)

    # Rien d'autre que la date ne change : on garde l'ancien fichier (aucun commit).
    sans_date = lambda d: {k: v for k, v in d.items() if k != "maj"}
    if sans_date(ancien) == sans_date(nouveau):
        NOUVEAU.write_text(ancien_p.read_text(encoding="utf-8"), encoding="utf-8")
        print("Aucun changement dans les annonces.")
        return

    ajoutees = sorted(set(a_new) - set(a_old))
    retirees = sorted(set(a_old) - set(a_new))
    prix = sorted(i for i in set(a_new) & set(a_old) if a_new[i].get("prix") != a_old[i].get("prix"))
    lignes = [f"Annonces : mise à jour automatique du {nouveau.get('maj', '')}", "",
              f"{n_new} annonces ({n_new - n_old:+d}) : {len(ajoutees)} ajoutée(s), {len(retirees)} retirée(s), {len(prix)} prix modifié(s)."]
    for titre, ids, src in (("Ajoutées", ajoutees, a_new), ("Retirées", retirees, a_old)):
        if ids:
            lignes += ["", titre + " :"] + [f"- {src[i]['titre'][:80]} ({src[i]['ville']})" for i in ids[:20]]
    if prix:
        lignes += ["", "Prix modifiés :"] + [f"- {a_new[i]['titre'][:60]} : {a_old[i].get('prix')} → {a_new[i].get('prix')}" for i in prix[:20]]
    texte = "\n".join(lignes)
    print(texte)
    if msg_p:
        msg_p.write_text(texte + "\n", encoding="utf-8")


main()
