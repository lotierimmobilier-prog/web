#!/usr/bin/env python3
"""Importe les annonces publiées sur lotier-immobilier.com/nos-biens/ vers le nouveau site.

Usage : python3 scripts/scrape_annonces.py
Écrit data/annonces.json (description, caractéristiques, photos, agent, diagnostic énergétique, mentions) et copie les
photos (réduites) dans assets/annonces/, puis il faut régénérer le site
(python3 scripts/generateur/build_all.py). Les annonces restent gérées dans WordPress ; le script ne fait que lire
les pages publiques. À remplacer par un flux Collab lorsqu'il existera."""
import io, json, re, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scrape_biens as sb

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "annonces.json"
IMG_DIR = ROOT / "assets" / "annonces"
SCHEMA = 2        # version du format des fiches : une fiche d'une version plus ancienne est relue en entier
CHAMPS_FICHE = ("description_html", "blocs", "photos", "reference", "agent", "energie", "mentions_prix")
PHOTOS_MAX = 12   # photos copiées par annonce (WPImmo en propose souvent une vingtaine)

def slug_of(url):
    return re.sub(r"[^a-z0-9-]", "", urlparse(url).path.strip("/").split("/")[-1].lower())

def fetch_image(url, dest, size=(720, 540), quality=76):
    req = urllib.request.Request(url, headers={"User-Agent": sb.UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    im.thumbnail(size); dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
    return im.size

import html as _html

def _txt(s):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def _nombre(v):
    """« 1 080 » -> 1080 ; « 81.5 » -> 81.5 ; autre chose -> None."""
    t = re.sub(r"[\s \xa0]", "", v or "").replace(",", ".")
    try: n = float(t)
    except ValueError: return None
    return int(n) if n == int(n) else n

def parse_agent(h):
    """Le conseiller affiché dans la colonne de droite de WPImmo : nom, e-mail, téléphone (publics sur l'ancien site)."""
    i = h.find('iwp__sidebar-agent"')
    if i < 0: return None
    blk = h[i:i + 3000]
    j = blk.find("iwp__price-card")           # fin du bloc agent
    if j > 0: blk = blk[:j]
    nom = re.search(r"<h3>(.*?)</h3>", blk, re.S)
    mail = re.search(r'href="mailto:([^"]+)"', blk)
    tel = re.search(r'href="tel:([^"]+)"', blk)
    img = re.search(r'<img[^>]*src="([^"]+)"', blk)
    a = {"nom": _txt(nom.group(1)) if nom else "", "email": _html.unescape(mail.group(1)).strip().lower() if mail else None,
         "telephone": re.sub(r"[^\d+]", "", _html.unescape(tel.group(1))) if tel else None, "photo": img.group(1) if img else None}
    return a if a["nom"] else None

def parse_energie(h):
    """Diagnostic énergétique : valeurs et classes DPE / GES, dépenses annuelles, date de référence des prix, Géorisques."""
    i = h.find("iwp__block-energie")
    if i < 0: return None
    j = h.find("iwp__sidebar-region", i)
    blk = h[i:j if j > 0 else i + 30000]
    txt = _txt(blk)
    e = {}
    v = re.search(r'class="diagnostic-number"[^>]*>\s*([\d.,\s]+)<', blk); c = re.search(r"diagnostic-(?:scale|diagram) number([A-G])\b", blk)
    if v and c: e["dpe"] = {"valeur": _nombre(v.group(1)), "classe": c.group(1)}
    v = re.search(r'class="emission-number"[^>]*>\s*([\d.,\s]+)\*?\s*<', blk); c = re.search(r"emission-(?:scale|diagram) number([A-G])\b", blk)
    if v and c: e["ges"] = {"valeur": _nombre(v.group(1)), "classe": c.group(1)}
    d = re.search(r"entre\s+([\d\s \xa0.,]+?)\s*€\s+et\s+([\d\s \xa0.,]+?)\s*€", txt)
    if d: e["depenses_min"], e["depenses_max"] = _nombre(d.group(1)), _nombre(d.group(2))
    r = re.search(r"index[ée]s au (\d{2}/\d{2}/\d{4})", txt)
    if r: e["prix_energies"] = r.group(1)
    return e or None

def parse_mentions_prix(h):
    """Les lignes sous le prix (« Charges comprises, dont 20 € de provisions », « Location meublée », frais d'agence…) et la référence."""
    i = h.find('iwp__price-card"')
    if i < 0: return [], None
    blk = h[i:i + 4000]
    ms = [_txt(x) for x in re.findall(r'class="iwp__price-card-mention"[^>]*>(.*?)</p>', blk, re.S)]
    ref = re.search(r"Réf\.\s*([^<\s]+)", _html.unescape(blk))
    return [m for m in ms if m], (ref.group(1) if ref else None)

def parse_fiche(h):
    """Description (HTML simple), blocs de caractéristiques et adresses des photos d'une fiche."""
    desc = ""
    m = re.search(r'iwp__block-description[^>]*>.*?<div class="iwp__card-body">(.*?)</div>\s*</div>', h, re.S)
    if m:
        raw = re.sub(r"<br[^>]*>", "\n", m.group(1)); raw = re.sub(r"</p>", "\n\n", raw)
        lines = [_txt(x) for x in re.sub(r"<(?!/?(?:strong|b)\b)[^>]+>", "", raw).split("\n")]
        out, ul = [], []
        def flush():
            nonlocal ul
            if ul: out.append("<ul>" + "".join(f"<li>{_html.escape(x)}</li>" for x in ul) + "</ul>"); ul = []
        for ln in lines:
            ln = _html.unescape(re.sub(r"</?(?:strong|b)>", "", ln)).strip()
            if not ln: flush(); continue
            if re.match(r"^(o|•|-|·)\s+\S", ln): ul.append(re.sub(r"^(o|•|-|·)\s+", "", ln))
            else: flush(); out.append(f"<p>{_html.escape(ln)}</p>")
        flush(); desc = "".join(out)
    blocs = []
    for b in re.finditer(r'<div class="iwp__block iwp__block-kv[^"]*"><div class="iwp__card-header"><h2>(.*?)</h2></div><div class="iwp__card-body">(.*?)</div></div>', h, re.S):
        rows = [[_txt(a), _txt(v)] for a, v in re.findall(r'iwp__kv-label">(.*?)</span><span class="iwp__kv-value">(.*?)</span>', b.group(2), re.S)]
        rows = [r for r in rows if r[0] and r[1] and r[1].lower() not in ("inconnu", "non renseigné")]
        if rows: blocs.append({"titre": _txt(b.group(1)), "lignes": rows})
    photos = []
    for u in re.findall(r'data-pswp-src="([^"]+)"', h):
        if u not in photos: photos.append(u)
    mentions_prix, reference = parse_mentions_prix(h)
    return {"description_html": desc, "blocs": blocs, "photos": photos, "reference": reference, "agent": parse_agent(h),
            "energie": parse_energie(h), "mentions_prix": mentions_prix}

def main():
    biens, page = [], 1
    while True:
        url = sb.BASE if page == 1 else f"{sb.BASE}page/{page}/"
        try: h = sb.get(url)
        except Exception as e:
            if getattr(e, "code", None) == 404: break
            raise
        parts = h.split('<div class="iwp__item">')[1:]
        if not parts: break
        for blk in parts:
            b = sb.parse_item(blk.split('<div class="iwp__item">')[0])
            if b["url"] and b["titre"]: biens.append(b)
        page += 1; time.sleep(1)
    if not biens: sys.exit("Aucune annonce trouvée : structure de la page modifiée ? Fichiers non modifiés.")
    prev = {}
    if OUT.exists():
        try: prev = {a["id"]: a for a in json.loads(OUT.read_text(encoding="utf-8")).get("annonces", [])}
        except Exception: prev = {}
    seen, out = set(), []
    for b in biens:
        if b["url"] in seen: continue
        seen.add(b["url"]); sid = slug_of(b["url"])
        item = {"id": sid, "url": b["url"], "titre": b["titre"], "ville": b["ville"], "type": b["type"], "prix": b["prix"],
                "surface": b["surface"], "chambres": b["chambres"], "sdb": b["sdb"], "badges": b["badges"], "photo": None}
        if b["image"]:
            dest = IMG_DIR / f"{sid}.jpg"
            try:
                if not dest.exists(): fetch_image(b["image"], dest); time.sleep(0.3)
                item["photo"] = f"assets/annonces/{sid}.jpg"
            except Exception as e: print("photo ignorée", sid, e, file=sys.stderr)
        old = prev.get(sid)
        if old and old.get("schema") == SCHEMA and old.get("description_html") is not None:
            for k in CHAMPS_FICHE: item[k] = old.get(k)
            item["schema"] = SCHEMA
        else:
            try:
                f = parse_fiche(sb.get(b["url"])); time.sleep(1)
                for k in CHAMPS_FICHE:
                    if k != "photos": item[k] = f[k]
                item["schema"] = SCHEMA
                item["photos"] = []
                for n, u in enumerate(f["photos"][:PHOTOS_MAX]):
                    dest = IMG_DIR / f"{sid}-{n + 1}.jpg"
                    if not dest.exists(): fetch_image(u, dest, (1000, 750), 70); time.sleep(0.2)
                    item["photos"].append(f"assets/annonces/{sid}-{n + 1}.jpg")
            except Exception as e:
                print("fiche ignorée", sid, e, file=sys.stderr); item["description_html"] = None
        out.append(item)
    # photos d'annonces retirées : on les supprime
    keep = {Path(i["photo"]).name for i in out if i["photo"]} | {Path(p).name for i in out for p in i.get("photos", [])}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep: f.unlink()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"maj": datetime.now(timezone.utc).date().isoformat(), "source": sb.BASE, "annonces": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out)} annonces, {sum(1 for i in out if i['photo'])} photos", file=sys.stderr)

main()
