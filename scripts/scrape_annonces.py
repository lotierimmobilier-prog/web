#!/usr/bin/env python3
"""Importe les annonces publiées sur lotier-immobilier.com/nos-biens/ vers le nouveau site.

Usage : python3 scripts/scrape_annonces.py
Écrit data/annonces.json et copie les photos (réduites) dans assets/annonces/, puis il faut régénérer le site
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
    return desc, blocs, photos

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
        if old and old.get("description_html") is not None:
            for k in ("description_html", "blocs", "photos"): item[k] = old[k]
        else:
            try:
                desc, blocs, urls = parse_fiche(sb.get(b["url"])); time.sleep(1)
                item["description_html"], item["blocs"] = desc, blocs
                item["photos"] = []
                for n, u in enumerate(urls[:6]):
                    dest = IMG_DIR / f"{sid}-{n + 1}.jpg"
                    if not dest.exists(): fetch_image(u, dest, (900, 675), 70); time.sleep(0.2)
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
