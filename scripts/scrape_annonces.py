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

def fetch_image(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": sb.UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    im.thumbnail((720, 540)); dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=76, optimize=True, progressive=True)
    return im.size

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
        out.append(item)
    # photos d'annonces retirées : on les supprime
    keep = {Path(i["photo"]).name for i in out if i["photo"]}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep: f.unlink()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"maj": datetime.now(timezone.utc).date().isoformat(), "source": sb.BASE, "annonces": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out)} annonces, {sum(1 for i in out if i['photo'])} photos", file=sys.stderr)

main()
