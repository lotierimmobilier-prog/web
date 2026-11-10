#!/usr/bin/env python3
"""Exporte les articles du blog TELS QUE LE CODE LES PUBLIE (content_articles.py + extra*.py + photos + dates) au format de Collab.

Usage : python3 scripts/exporter_articles.py [sortie.json]      (défaut : sortie standard)

Sert à (1) reprendre les 20 articles actuels dans Collab (étape « Blog » de l'administration du site), (2) vérifier que le site
régénéré depuis Collab est IDENTIQUE au site actuel. Ignore volontairement data/contenu.json (LOTIER_CONTENU_STATIQUE=1).
Aucun secret, aucune écriture hors du fichier de sortie."""
import json, os, sys
os.environ["LOTIER_CONTENU_STATIQUE"] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "generateur"))
import common as C  # noqa: E402


def exporter():
    sortie = []
    for a in sorted(C.ARTICLES, key=lambda x: x["slug"]):
        sections = []
        for titre, blocs in a["sections"]:
            sections.append({"titre": titre, "blocs": [{"type": "liste", "items": list(b)} if isinstance(b, list) else {"type": "texte", "texte": b} for b in blocs]})
        sortie.append({
            "slug": a["slug"], "titre": a["title"], "titreSeo": a.get("seo_title"), "description": a["desc"], "categorie": a["cat"],
            "cta": a["cta"], "photo": a["photo"], "photoAlt": a["alt"], "ville": a.get("city"), "intro": a["intro"],
            "sections": sections, "faq": [{"question": q, "reponse": r} for q, r in C.ART_FAQ.get(a["slug"], [])],
            "retenir": list(a["retenir"]), "date": a["date"].isoformat(),
        })
    return sortie


if __name__ == "__main__":
    texte = json.dumps(exporter(), ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if len(sys.argv) > 1:
        open(sys.argv[1], "w", encoding="utf-8").write(texte)
        print(f"{len(json.loads(texte))} articles exportés → {sys.argv[1]}", file=sys.stderr)
    else:
        sys.stdout.write(texte)
