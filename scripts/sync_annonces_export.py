#!/usr/bin/env python3
"""Lit les annonces dans l'export Hektor de l'agence et écrit data/annonces.json.

L'export (lotier-immo.zip, format Poliris 4.12, renouvelé chaque nuit par Hektor) est la source des annonces : c'est
lui qui fait foi pour la liste des biens en ligne, les prix, les caractéristiques, les honoraires et les photos.
Ce script remplace la relecture des pages publiques de lotier-immobilier.com (ancien scripts/scrape_annonces.py).

Usage : python3 scripts/sync_annonces_export.py [chemin d'un zip déjà téléchargé]
Écrit data/annonces.json et copie les photos (réduites) dans assets/annonces/ ; il faut ensuite régénérer le site
(python3 scripts/generateur/build_all.py).

Règles :
  - l'adresse d'une fiche (son « id ») ne change jamais tant que la référence du bien reste dans l'export ;
  - aucun montant n'est calculé, sauf le montant des honoraires de vente à la charge de l'acquéreur, qui est la
    différence entre deux prix de l'export (prix honoraires inclus − prix hors honoraires) ;
  - seules les colonnes utiles à l'affichage sont lues : numéro et date de mandat, adresse du bien et coordonnées
    du mandant ne sont jamais recopiés ;
  - une photo n'est retéléchargée que si son adresse dans l'export a changé ;
  - si l'export est injoignable ou illisible, le script s'arrête en erreur sans rien modifier."""
import html, io, json, re, sys, time, unicodedata, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "annonces.json"
IMG_DIR = ROOT / "assets" / "annonces"
URL = "https://www.lotier-immobilier.com/lotier-immo.zip"
UA = "LotierV2-sync/1.0 (+https://www.lotier-immobilier.com)"
SCHEMA = 3
PHOTOS_MAX = 12
NB_COLONNES_MIN = 328

# Colonnes d'Annonces.csv (numérotées à partir de 1, comme dans la documentation Poliris).
C_REF, C_TRANSACTION, C_TYPE, C_VILLE, C_PAYS, C_SECTEUR, C_PRIX, C_CHARGES_COMPRISES, C_HONORAIRES = 2, 3, 4, 6, 7, 9, 11, 13, 15
C_SURFACE, C_TERRAIN, C_PIECES, C_CHAMBRES, C_TITRE, C_TEXTE, C_CHARGES, C_ETAGE, C_NB_ETAGES, C_MEUBLE, C_ANNEE = 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27
C_SDB, C_SDE, C_WC, C_CHAUFFAGE, C_CUISINE, C_SUD, C_EST, C_OUEST, C_NORD, C_BALCONS = 29, 30, 31, 33, 34, 35, 36, 37, 38, 39
C_ASCENSEUR, C_CAVE, C_PARKINGS, C_BOXES, C_GARDIEN, C_TERRASSE, C_CLIM, C_PISCINE, C_EXCLUSIVITE, C_COUP_DE_COEUR = 41, 42, 43, 44, 47, 48, 64, 65, 83, 84
C_TEL, C_CONTACT, C_EMAIL, C_DEPOT, C_DPE, C_DPE_CLASSE, C_GES, C_GES_CLASSE = 105, 106, 107, 161, 176, 177, 178, 179
C_COPRO, C_LOTS, C_CHARGES_COPRO, C_PROCEDURE, C_CHARGE_HONORAIRES, C_PRIX_HORS_HONORAIRES, C_MODALITES_CHARGES, C_ETAT_DES_LIEUX = 258, 259, 260, 261, 302, 303, 304, 306
C_DEPENSES_MIN, C_DEPENSES_MAX, C_PRIX_ENERGIES = 326, 327, 328
C_PHOTOS = list(range(85, 94)) + list(range(164, 175)) + list(range(264, 274))

CUISINES = {"2": "Américaine", "3": "Séparée", "4": "Industrielle", "5": "Coin cuisine", "6": "Américaine équipée", "7": "Séparée équipée",
            "8": "Coin cuisine équipée", "9": "Équipée"}
CHARGE_HONORAIRES = {"1": "Acquéreur", "2": "Vendeur", "3": "Honoraires partagés acquéreur / vendeur"}
MODALITES = {"1": ("Forfait de charges", "Forfaitaires mensuelles"), "2": ("Provisions sur charges", "Prévisionnelles mensuelles avec régularisation annuelle")}


def nombre(v):
    """« 1 080 » -> 1080 ; « 81.5 » -> 81.5 ; vide ou illisible -> None."""
    t = re.sub(r"[\s  ]", "", str(v or "")).replace(",", ".")
    try: n = float(t)
    except ValueError: return None
    return int(n) if n == int(n) else n


def positif(v):
    n = nombre(v)
    return n if n and n > 0 else None


def oui(v): return (v or "").strip().upper() == "OUI"


def euros(n, decimales=False):
    """1260 -> « 1 260 € » ; 98.25 -> « 98,25 € » si decimales, sinon arrondi à l'euro."""
    if decimales and n != int(n): t = f"{n:,.2f}".replace(",", " ").replace(".", ",")
    else: t = f"{round(n):,}".replace(",", " ")
    return t + " €"


def typo(s):
    """Apostrophes et tirets typographiques, espaces simples."""
    s = re.sub(r"\s+", " ", s or "").strip()
    return s.replace(" - ", " – ").replace("--", "—").replace("...", "…").replace("'", "’")


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:120].strip("-")


def chauffage(code):
    """Code Poliris (somme de trois réglages) -> « Individuel électrique radiateur ». Un réglage inconnu est passé sous silence."""
    n = nombre(code)
    if not isinstance(n, int) or n <= 0: return None
    mots = [{1: "Collectif", 2: "Individuel", 4: "Central"}.get(n >> 12 & 7), {1: "gaz", 2: "fioul", 4: "électrique"}.get(n >> 9 & 7),
            {1: "radiateur", 2: "sol", 3: "mixte"}.get(n >> 7 & 3)]
    t = " ".join(m for m in mots if m)
    return (t[0].upper() + t[1:]) if t else None


def description(brut):
    """Texte de l'export (retours à la ligne en <br>) -> paragraphes et listes à puces en HTML simple."""
    raw = re.sub(r"<br[^>]*>", "\n", brut or ""); raw = re.sub(r"</p>", "\n\n", raw)
    out, ul = [], []
    def flush():
        nonlocal ul
        if ul: out.append("<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in ul) + "</ul>"); ul = []
    for ln in raw.split("\n"):
        ln = typo(html.unescape(re.sub(r"<[^>]+>", "", ln)))
        if not ln: flush(); continue
        if re.match(r"^(o|•|-|–|·)\s+\S", ln): ul.append(re.sub(r"^(o|•|-|–|·)\s+", "", ln))
        else: flush(); out.append(f"<p>{html.escape(ln)}</p>")
    flush()
    return "".join(out)


def lire_export(octets):
    with zipfile.ZipFile(io.BytesIO(octets)) as z:
        nom = next((n for n in z.namelist() if n.lower().endswith("annonces.csv")), None)
        if not nom: raise ValueError("Annonces.csv absent de l'export")
        texte = z.read(nom).decode("cp1252", errors="replace")
    lignes = []
    for ligne in texte.split("\n"):
        ligne = ligne.strip("\r")
        if not ligne.strip(): continue
        c = [x[1:-1] if len(x) >= 2 and x[0] == '"' and x[-1] == '"' else x for x in ligne.split("!#")]
        if len(c) >= NB_COLONNES_MIN and c[C_REF - 1].strip(): lignes.append(c)
    return lignes


def fiche(c):
    """Une ligne de l'export -> les champs d'une annonce (sans id ni photos)."""
    g = lambda n: (c[n - 1] if n <= len(c) else "").strip()
    transaction = g(C_TRANSACTION).lower()
    location = transaction.startswith("location")
    type_brut = g(C_TYPE).lower()
    prix, surface = positif(g(C_PRIX)), positif(g(C_SURFACE))
    sdb, sde = positif(g(C_SDB)), positif(g(C_SDE))
    badges = (["Exclusivité"] if oui(g(C_EXCLUSIVITE)) else []) + (["Coup de coeur"] if oui(g(C_COUP_DE_COEUR)) else [])
    if "prestige" in transaction: badges.append("Vente de prestige")
    if "fonds" in transaction: badges.append("Vente-fonds-de-commerce")

    carac = []
    if type_brut and type_brut != "inconnu": carac.append(["Type de bien", type_brut[0].upper() + type_brut[1:]])
    if surface: carac.append(["Surface habitable", f"{g(C_SURFACE)} m²"])
    for lab, col in (("Pièces", C_PIECES), ("Chambres", C_CHAMBRES), ("Salles de bain", C_SDB), ("Salles d'eau", C_SDE), ("WC", C_WC)):
        if positif(g(col)): carac.append([lab, str(positif(g(col)))])
    if g(C_ETAGE) != "":
        carac.append(["Étage", g(C_ETAGE) + (f" / {g(C_NB_ETAGES)}" if positif(g(C_NB_ETAGES)) else "")])
    elif positif(g(C_NB_ETAGES)): carac.append(["Nombre d'étages", g(C_NB_ETAGES)])
    if positif(g(C_TERRAIN)): carac.append(["Terrain", f"{g(C_TERRAIN)} m²"])
    if positif(g(C_ANNEE)): carac.append(["Année de construction", g(C_ANNEE)])

    equip = []
    if chauffage(g(C_CHAUFFAGE)): equip.append(["Chauffage", chauffage(g(C_CHAUFFAGE))])
    if g(C_CUISINE) in CUISINES: equip.append(["Cuisine", CUISINES[g(C_CUISINE)]])
    expo = [nom for nom, col in (("Nord", C_NORD), ("Sud", C_SUD), ("Est", C_EST), ("Ouest", C_OUEST)) if oui(g(col))]
    if expo: equip.append(["Exposition", " ".join(expo)])
    if g(C_ASCENSEUR).upper() in ("OUI", "NON"): equip.append(["Ascenseur", "Oui" if oui(g(C_ASCENSEUR)) else "Non"])
    for lab, ok in (("Balcon", positif(g(C_BALCONS))), ("Terrasse", oui(g(C_TERRASSE))), ("Cave", oui(g(C_CAVE))), ("Parking", positif(g(C_PARKINGS))),
                    ("Garage", positif(g(C_BOXES))), ("Climatisation", oui(g(C_CLIM))), ("Piscine", oui(g(C_PISCINE))), ("Gardien", oui(g(C_GARDIEN))),
                    ("Meublé", oui(g(C_MEUBLE)) and not location)):
        if ok: equip.append([lab, "Oui"])

    fin, mentions, honoraires = [], [], None
    if location and prix:
        cc, charges = oui(g(C_CHARGES_COMPRISES)), positif(g(C_CHARGES))
        lab_charges, modalite = MODALITES.get(g(C_MODALITES_CHARGES), ("Charges récupérables", None))
        fin.append(["Loyer charges comprises" if cc else "Loyer", f"{euros(prix)} / mois"])
        if charges: fin.append([lab_charges, f"{euros(charges)} / mois"])
        if cc and charges: mentions.append(f"Charges comprises, dont {euros(charges)} de {lab_charges[0].lower() + lab_charges[1:]}")
        elif cc: mentions.append("Charges comprises")
        elif charges: mentions.append(f"Hors charges, plus {euros(charges)} de {lab_charges[0].lower() + lab_charges[1:]}")
        else: mentions.append("Hors charges, montant des charges non communiqué")
        total, edl = positif(g(C_HONORAIRES)), positif(g(C_ETAT_DES_LIEUX))
        if total:
            honoraires = {"locataire": total}
            if edl and edl <= total: honoraires["etat_des_lieux"] = edl
        if edl: fin.append(["Honoraires état des lieux (TTC, charge locataire)", euros(edl, True)])
        if modalite and charges: fin.append(["Modalités de règlement des charges", modalite])
        if positif(g(C_DEPOT)): fin.append(["Dépôt de garantie", euros(positif(g(C_DEPOT)))])
        if g(C_MEUBLE).upper() in ("OUI", "NON"):
            meuble = "Location meublée" if oui(g(C_MEUBLE)) else "Location non meublée"
            fin.append(["Caractère meublé", meuble]); mentions.append(meuble)
    elif prix:
        fin.append(["Prix FAI", euros(prix)])
        charge = CHARGE_HONORAIRES.get(g(C_CHARGE_HONORAIRES))
        if charge: fin.append(["Charge honoraires", charge])
        hors = positif(g(C_PRIX_HORS_HONORAIRES))
        if g(C_CHARGE_HONORAIRES) in ("1", "3") and hors and hors < prix:
            if positif(g(C_HONORAIRES)): fin.append(["Honoraires", f"{g(C_HONORAIRES)}% TTC"])
            fin.append(["Montant honoraires", euros(prix - hors)]); fin.append(["Prix hors honoraires", euros(hors)])

    copro = []
    if oui(g(C_COPRO)): copro.append(["Copropriété", "Oui"])
    if positif(g(C_LOTS)): copro.append(["Nombre de lots", g(C_LOTS)])
    if positif(g(C_CHARGES_COPRO)): copro.append(["Charges annuelles", f"{euros(positif(g(C_CHARGES_COPRO)))}/an"])
    if oui(g(C_COPRO)) and g(C_PROCEDURE).upper() in ("OUI", "NON"): copro.append(["Procédures en cours", "Oui" if oui(g(C_PROCEDURE)) else "Non"])

    situation = ([["Secteur", typo(g(C_SECTEUR))]] if g(C_SECTEUR) else []) + ([["Ville", g(C_VILLE)]] if g(C_VILLE) else []) + ([["Pays", g(C_PAYS)]] if g(C_PAYS) else [])
    blocs = [{"titre": t, "lignes": l} for t, l in (("Caractéristiques", carac), ("Équipements et confort", equip), ("Informations financières", fin),
                                                     ("Copropriété (loi ALUR)", copro), ("Situation", situation)) if l]

    energie = None
    if positif(g(C_DPE)) and g(C_DPE_CLASSE) in list("ABCDEFG"):
        energie = {"dpe": {"valeur": positif(g(C_DPE)), "classe": g(C_DPE_CLASSE)}}
        if nombre(g(C_GES)) is not None and g(C_GES_CLASSE) in list("ABCDEFG"): energie["ges"] = {"valeur": nombre(g(C_GES)), "classe": g(C_GES_CLASSE)}
        if positif(g(C_DEPENSES_MIN)) and positif(g(C_DEPENSES_MAX)):
            energie["depenses_min"], energie["depenses_max"] = positif(g(C_DEPENSES_MIN)), positif(g(C_DEPENSES_MAX))
            if re.fullmatch(r"\d{2}/\d{2}/\d{4}", g(C_PRIX_ENERGIES)) and not g(C_PRIX_ENERGIES).startswith("00"): energie["prix_energies"] = g(C_PRIX_ENERGIES)

    agent = None
    if g(C_CONTACT):
        agent = {"nom": re.sub(r"\s+", " ", g(C_CONTACT)), "email": g(C_EMAIL).lower() or None, "telephone": re.sub(r"[^\d+]", "", g(C_TEL)) or None, "photo": None}

    return {"titre": typo(g(C_TITRE)).rstrip(" -–"), "ville": g(C_VILLE), "type": "location" if location else "vente", "prix": float(prix) if prix else None,
            "surface": float(surface) if surface else None, "chambres": positif(g(C_CHAMBRES)), "sdb": sdb or sde, "badges": badges,
            "description_html": description(g(C_TEXTE)), "blocs": blocs, "reference": g(C_REF), "agent": agent, "energie": energie,
            "mentions_prix": mentions, "honoraires": honoraires,
            "_photos": [u for u in (g(n) for n in C_PHOTOS) if re.match(r"^https://[^\s\"<>]+\.(?:jpe?g|png|webp)$", u, re.I)][:PHOTOS_MAX]}


def copier_image(url, dest, taille, qualite):
    from PIL import Image
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    im.thumbnail(taille); dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=qualite, optimize=True, progressive=True)


def main():
    fichiers = [a for a in sys.argv[1:] if not a.startswith("--")]
    try:
        if fichiers: octets = Path(fichiers[0]).read_bytes()
        else:
            with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=60) as rep: octets = rep.read()
        lignes = lire_export(octets)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"Export Hektor non lu : {e}. Fichiers non modifiés.")
    if not lignes: sys.exit("Aucune annonce dans l'export : format inattendu ? Fichiers non modifiés.")

    try: ancien = json.loads(OUT.read_text(encoding="utf-8")).get("annonces", [])
    except Exception: ancien = []  # noqa: BLE001
    par_ref = {a.get("reference"): a for a in ancien if a.get("reference")}
    rang = {a.get("reference"): i for i, a in enumerate(ancien)}
    pris = {a["id"] for a in ancien}

    sortie, vues = [], set()
    for c in lignes:
        f = fiche(c)
        ref = f["reference"]
        if ref in vues or not f["titre"]: continue
        vues.add(ref)
        old = par_ref.get(ref)
        if old: sid = old["id"]
        else:
            sid = base = slug(f["titre"]) or slug(ref); n = 2
            while sid in pris: sid = f"{base}-{n}"; n += 1
            pris.add(sid)
        sources = f.pop("_photos")
        # Sans trace des adresses d'origine (fiches reprises de l'ancien import), les photos déjà copiées sont gardées.
        connues = (old or {}).get("photos_source")
        item = {"id": sid, **f, "photo": None, "photos": [], "photos_source": sources, "schema": SCHEMA}
        for n, u in enumerate(sources):
            dest = IMG_DIR / f"{sid}-{n + 1}.jpg"
            change = connues is not None and (n >= len(connues) or connues[n] != u)
            try:
                if change or not dest.exists(): copier_image(u, dest, (1000, 750), 70); time.sleep(0.2)
                item["photos"].append(f"assets/annonces/{sid}-{n + 1}.jpg")
            except Exception as e:  # noqa: BLE001
                print("photo ignorée", sid, n + 1, e, file=sys.stderr)
        if sources:
            dest = IMG_DIR / f"{sid}.jpg"
            try:
                if not dest.exists() or (connues is not None and connues[:1] != sources[:1]): copier_image(sources[0], dest, (720, 540), 76)
                item["photo"] = f"assets/annonces/{sid}.jpg"
            except Exception as e:  # noqa: BLE001
                print("photo ignorée", sid, e, file=sys.stderr)
        sortie.append(item)

    # Ordre d'affichage : les nouveautés en tête, puis l'ordre déjà en place.
    sortie.sort(key=lambda a: rang.get(a["reference"], -1))
    garder = {Path(i["photo"]).name for i in sortie if i["photo"]} | {Path(p).name for i in sortie for p in i["photos"]}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in garder: f.unlink()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"maj": datetime.now(timezone.utc).date().isoformat(), "source": "Export Hektor de l'agence (lotier-immo.zip)",
                               "annonces": sortie}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(sortie)} annonces, {sum(1 for i in sortie if i['photo'])} avec photo", file=sys.stderr)


if __name__ == "__main__":
    main()
