#!/usr/bin/env python3
"""Relève les honoraires de location dans l'export Hektor de l'agence et écrit data/honoraires-location.json.

L'export (lotier-immo.zip, format Poliris 4.12, renouvelé chaque nuit par Hektor) est le fichier qui alimente les
annonces de lotier-immobilier.com. Les fiches publiques de ce site n'affichent que la part « état des lieux » des
honoraires de location ; l'export porte aussi le total à la charge du locataire. Ce script ne lit que deux colonnes
d'Annonces.csv, pour les seules locations :
  - colonne 15  : honoraires à la charge du locataire (total, en euros) ;
  - colonne 306 : part de ces honoraires qui correspond à l'état des lieux.
Aucun montant n'est calculé : les valeurs sont recopiées. Le fichier d'export n'est ni conservé ni versionné.

Usage : python3 scripts/sync_export_hektor.py [--souple] [chemin d'un zip déjà téléchargé]
  --souple : en cas d'échec (export injoignable ou illisible), garde le fichier existant et se termine sans erreur."""
import datetime, io, json, sys, urllib.request, zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "data" / "honoraires-location.json"
URL = "https://www.lotier-immobilier.com/lotier-immo.zip"
UA = "LotierV2-sync/1.0 (+https://www.lotier-immobilier.com)"
COL_REF, COL_TYPE, COL_HONORAIRES, COL_ETAT_DES_LIEUX, NB_COLONNES_MIN = 1, 2, 14, 305, 306      # index à partir de 0


def nombre(v):
    try:
        x = float(str(v).replace(",", ".").replace(" ", ""))
    except ValueError:
        return None
    return x if x > 0 else None


def lire(octets):
    with zipfile.ZipFile(io.BytesIO(octets)) as z:
        nom = next((n for n in z.namelist() if n.lower().endswith("annonces.csv")), None)
        if not nom:
            raise ValueError("Annonces.csv absent de l'export")
        texte = z.read(nom).decode("cp1252", errors="replace")
    sortie, locations = {}, 0
    for ligne in texte.split("\n"):
        ligne = ligne.strip("\r")
        if not ligne.strip():
            continue
        c = [x[1:-1] if len(x) >= 2 and x[0] == '"' and x[-1] == '"' else x for x in ligne.split("!#")]
        if len(c) < NB_COLONNES_MIN or c[COL_TYPE].strip().lower() != "location":
            continue
        locations += 1
        total = nombre(c[COL_HONORAIRES])
        if total is None or not c[COL_REF].strip():
            continue
        entree = {"locataire": total}
        edl = nombre(c[COL_ETAT_DES_LIEUX])
        if edl is not None and edl <= total:
            entree["etat_des_lieux"] = edl
        sortie[c[COL_REF].strip()] = entree
    if not locations:
        raise ValueError("aucune location dans l'export : format inattendu")
    return sortie, locations


def main():
    souple = "--souple" in sys.argv
    fichiers = [a for a in sys.argv[1:] if not a.startswith("--")]
    try:
        if fichiers:
            octets = Path(fichiers[0]).read_bytes()
        else:
            req = urllib.request.Request(URL, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as rep:
                octets = rep.read()
        honoraires, locations = lire(octets)
    except Exception as e:  # noqa: BLE001
        if souple:
            print(f"::warning::Export Hektor non lu ({e}) : les honoraires déjà relevés sont conservés.")
            return
        sys.exit(f"Export Hektor non lu : {e}")
    try:
        ancien = json.loads(SORTIE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        ancien = {}
    if ancien.get("honoraires") == honoraires:
        print(f"Honoraires de location : {len(honoraires)} relevés sur {locations} locations, inchangés.")
        return
    SORTIE.write_text(json.dumps({
        "_note": "Honoraires de location relevés chaque nuit dans l'export Hektor de l'agence (scripts/sync_export_hektor.py). "
                 "Clé : référence de l'annonce. « locataire » : total à la charge du locataire ; « etat_des_lieux » : part de ce total. "
                 "Montants recopiés de l'export, jamais calculés. Ne pas modifier à la main.",
        "maj": datetime.date.today().isoformat(), "source": URL, "honoraires": dict(sorted(honoraires.items())),
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Honoraires de location : {len(honoraires)} relevés sur {locations} locations.")


if __name__ == "__main__":
    main()
