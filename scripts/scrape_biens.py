#!/usr/bin/env python3
"""Lit les annonces publiées sur lotier-immobilier.com/nos-biens/ et écrit v2/data/biens.json.

Usage : python3 scripts/scrape_biens.py
Les annonces restent gérées dans WordPress ; ce script ne fait que lire les pages publiques.
"""
import html, json, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.lotier-immobilier.com/nos-biens/"
OUT = Path(__file__).resolve().parent.parent / "v2" / "data" / "biens.json"
UA = "LotierV2-sync/1.0 (+https://www.lotier-immobilier.com)"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

def num(s):
    s = s.replace(" ", "").replace("\xa0", "").replace(" ", "").replace(",", ".")
    return float(s)

def parse_item(blk):
    url = re.search(r'<a href="([^"]+)"', blk)
    img = re.search(r'<img[^>]*src="([^"]+)"', blk)
    title = re.search(r"<h3>(.*?)</h3>", blk, re.S)
    city = re.search(r'class="localisation">(.*?)</div>', blk, re.S)
    price = re.search(r'class="iwp__price">(.*?)</span>', blk, re.S)
    postfix = re.search(r'class="iwp__postfix">(.*?)</span>', blk, re.S)
    over = text(re.sub(r"<svg.*?</svg>", "", blk, flags=re.S))
    meta = re.search(r'iwp__item-meta">(.*?)</div>', blk, re.S)
    badges = [text(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", meta.group(1), re.S)] if meta else []
    badges = [b for b in badges if b]
    if not badges:
        badges = [b for b in ("Exclusivité", "Coup de coeur") if b in over]
    ch = re.search(r"(\d+)\s*ch\.", over)
    m2 = re.search(r"([\d.,]+)\s*m²", over)
    sb = re.search(r"(\d+)\s*(?:sdb|sde)", over)
    p = text(price.group(1)) if price else ""
    pv = re.sub(r"[^\d.,]", "", p.replace("\xa0", ""))
    return {
        "url": url.group(1) if url else None,
        "titre": text(title.group(1)) if title else "",
        "ville": text(city.group(1)) if city else "",
        "type": "location" if postfix and "mois" in postfix.group(1) else "vente",
        "prix": num(pv) if pv else None,
        "surface": num(m2.group(1)) if m2 else None,
        "chambres": int(ch.group(1)) if ch else None,
        "sdb": int(sb.group(1)) if sb else None,
        "image": img.group(1) if img else None,
        "badges": badges,
    }

def main():
    biens, page = [], 1
    while True:
        url = BASE if page == 1 else f"{BASE}page/{page}/"
        try:
            h = get(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            raise
        parts = h.split('<div class="iwp__item">')[1:]
        if not parts:
            break
        for blk in parts:
            blk = blk.split('<div class="iwp__item">')[0]
            b = parse_item(blk)
            if b["url"] and b["titre"]:
                biens.append(b)
        print(f"page {page}: {len(parts)} annonces", file=sys.stderr)
        page += 1
        time.sleep(1)
    if not biens:
        sys.exit("Aucune annonce trouvée : la structure de la page a peut-être changé, fichier non modifié.")
    seen, uniq = set(), []
    for b in biens:
        if b["url"] not in seen:
            seen.add(b["url"]); uniq.append(b)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(timespec="seconds"), "biens": uniq},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(uniq)} annonces écrites dans {OUT}", file=sys.stderr)

if __name__ == "__main__":
    main()
