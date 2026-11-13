# -*- coding: utf-8 -*-
"""Prépare data/occitanie-carte.json : contour simplifié de la région Occitanie et de ses départements, pour le fond de la page « Nos agents ».
Source : https://github.com/gregoiredavid/france-geojson (licence Etalab 2.0), contours à jour de l'IGN.
Usage : python3 scripts/carte_occitanie.py <region.geojson> <departements.geojson>   (fichiers téléchargés au préalable)
Le fichier produit est versionné : le site ne dépend d'aucun service extérieur."""
import json, sys

def dp(pts, eps):
    """Simplification de Douglas-Peucker (itérative)."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True; pile = [(0, len(pts) - 1)]
    while pile:
        a, b = pile.pop(); (x1, y1), (x2, y2) = pts[a], pts[b]; dx, dy = x2 - x1, y2 - y1; n = (dx * dx + dy * dy) ** .5 or 1e-12; dm, im = 0, None
        for i in range(a + 1, b):
            d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / n
            if d > dm: dm, im = d, i
        if im is not None and dm > eps: keep[im] = True; pile += [(a, im), (im, b)]
    return [p for p, k in zip(pts, keep) if k]

def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [r for poly in polys for r in poly[:1]]          # contours extérieurs seulement

def simplifier(geom, eps):
    out = []
    for r in rings(geom):
        pts = [(round(p[0], 4), round(p[1], 4)) for p in r]; m = len(pts) // 2     # anneau fermé : deux moitiés simplifiées séparément
        s = dp(pts[:m + 1], eps)[:-1] + dp(pts[m:], eps)
        if len(s) >= 4: out.append([[round(x, 3), round(y, 3)] for x, y in s])
    return out

reg = json.load(open(sys.argv[1])); deps = json.load(open(sys.argv[2]))
res = {"region": simplifier(reg["geometry"], 0.012), "departements": {f["properties"]["code"]: simplifier(f["geometry"], 0.02) for f in deps["features"]}}
json.dump(res, open("data/occitanie-carte.json", "w"), separators=(",", ":"))
print(sum(len(r) for r in res["region"]), "points (région),", sum(len(r) for d in res["departements"].values() for r in d), "points (départements)")
