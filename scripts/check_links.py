#!/usr/bin/env python3
"""Vérifie que les liens et ressources relatifs d'un dossier de site statique existent.
Usage : python3 scripts/check_links.py v2   (ou release)"""
import os, re, sys
from urllib.parse import urlparse, unquote
root = sys.argv[1] if len(sys.argv) > 1 else "v2"
bad = 0
for d, _, fs in os.walk(root):
    if "vendor" in d: continue
    for f in fs:
        if not f.endswith(".html"): continue
        p = os.path.join(d, f); t = open(p, encoding="utf-8").read()
        for m in re.findall(r'(?:href|src)="([^"]+)"', t):
            if re.match(r'(https?:|mailto:|tel:|#|data:|javascript:)', m): continue
            path = unquote(urlparse(m).path)
            if not path: continue
            target = os.path.normpath(os.path.join(d, path))
            if os.path.isdir(target): target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                print(f"CASSÉ  {p} -> {m}"); bad += 1
print("liens relatifs : OK" if not bad else f"{bad} lien(s) cassé(s)")
sys.exit(1 if bad else 0)
