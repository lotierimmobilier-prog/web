# -*- coding: utf-8 -*-
"""Contenus venus de Collab (data/contenu.json) — lus par le générateur.

Le fichier est écrit par scripts/recuperer_contenu.py (publication depuis Collab). Il contient :
  { "empreinte": "...", "contenu": { "schema": 1, "gere": ["articles"], "articles": [...], "pages": [], "reglages": {}, "medias": [] } }

Règle de REPLI : pour chaque section, si Collab ne la « gère » pas (absente de `gere`), le générateur garde les textes
écrits dans le code (content_*.py). Quand Collab la gère, Collab fait foi : un contenu absent de Collab n'est PAS publié
(c'est ainsi qu'un article dépublié disparaît du site). Un contenu invalide ARRÊTE la génération (rien n'est publié).

LOTIER_CONTENU_STATIQUE=1 ignore data/contenu.json : sert à exporter les textes du code (scripts/exporter_articles.py)."""
import datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FICHIER = os.path.join(ROOT, "data", "contenu.json")

CATEGORIES = ("Vendre", "Acheter", "Bailleur", "Locataire", "Syndic", "Villes")
CTAS = ("estimation", "contact", "location", "syndic")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ContenuInvalide(ValueError):
    pass


def _charger():
    if os.environ.get("LOTIER_CONTENU_STATIQUE") == "1" or not os.path.exists(FICHIER):
        return {}
    try:
        with open(FICHIER, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as ex:  # noqa: BLE001
        raise ContenuInvalide(f"data/contenu.json illisible : {ex}")
    c = d.get("contenu") if isinstance(d, dict) else None
    if not isinstance(c, dict) or c.get("schema") != 1:
        raise ContenuInvalide("data/contenu.json : format inconnu (schema attendu : 1)")
    return c


_CONTENU = _charger()


def gere(section):
    """Collab gère-t-il cette section (articles, pages…) ? Sinon le générateur garde ses textes."""
    return section in (_CONTENU.get("gere") or [])


def _txt(a, cle, maxi, obligatoire=True):
    v = a.get(cle)
    if v is None or v == "":
        if obligatoire:
            raise ContenuInvalide(f"article « {a.get('slug', '?')} » : « {cle} » manquant")
        return None
    if not isinstance(v, str):
        raise ContenuInvalide(f"article « {a.get('slug', '?')} » : « {cle} » doit être un texte")
    v = v.strip()
    if len(v) > maxi:
        raise ContenuInvalide(f"article « {a.get('slug', '?')} » : « {cle} » dépasse {maxi} caractères")
    if obligatoire and not v:
        raise ContenuInvalide(f"article « {a.get('slug', '?')} » : « {cle} » vide")
    return v


def articles(photos_connues, villes_connues):
    """Les articles publiés par Collab, au format du générateur (voir content_articles.py). [] si Collab ne gère pas le blog."""
    if not gere("articles"):
        return None
    sortie, vus = [], set()
    for a in _CONTENU.get("articles") or []:
        if not isinstance(a, dict):
            raise ContenuInvalide("un article n'est pas un objet")
        slug = _txt(a, "slug", 90)
        if not SLUG.match(slug):
            raise ContenuInvalide(f"article « {slug} » : adresse invalide (lettres minuscules, chiffres et tirets)")
        if slug in vus:
            raise ContenuInvalide(f"article « {slug} » en double")
        vus.add(slug)
        cat = _txt(a, "categorie", 30)
        if cat not in CATEGORIES:
            raise ContenuInvalide(f"article « {slug} » : catégorie inconnue « {cat} »")
        cta = _txt(a, "cta", 20)
        if cta not in CTAS:
            raise ContenuInvalide(f"article « {slug} » : appel à l'action inconnu « {cta} »")
        photo = _txt(a, "photo", 40)
        if photo not in photos_connues:
            raise ContenuInvalide(f"article « {slug} » : photo inconnue « {photo} »")
        ville = _txt(a, "ville", 40, obligatoire=False)
        if ville and ville not in villes_connues:
            raise ContenuInvalide(f"article « {slug} » : ville inconnue « {ville} »")
        try:
            date = datetime.date.fromisoformat(_txt(a, "date", 10))
        except ValueError:
            raise ContenuInvalide(f"article « {slug} » : date invalide")
        sections = []
        if not isinstance(a.get("sections"), list) or not a["sections"]:
            raise ContenuInvalide(f"article « {slug} » : au moins une section est requise")
        for s in a["sections"]:
            titre = _txt(s, "titre", 200)
            blocs = []
            if not isinstance(s.get("blocs"), list) or not s["blocs"]:
                raise ContenuInvalide(f"article « {slug} » : la section « {titre} » est vide")
            for b in s["blocs"]:
                if b.get("type") == "texte":
                    blocs.append(_txt(b, "texte", 4000))
                elif b.get("type") == "liste":
                    items = b.get("items")
                    if not isinstance(items, list) or not items or not all(isinstance(x, str) and x.strip() for x in items):
                        raise ContenuInvalide(f"article « {slug} » : liste vide ou invalide dans « {titre} »")
                    blocs.append([x.strip() for x in items])
                else:
                    raise ContenuInvalide(f"article « {slug} » : bloc inconnu dans « {titre} »")
            sections.append((titre, blocs))
        retenir = a.get("retenir")
        if not isinstance(retenir, list) or not retenir or not all(isinstance(x, str) and x.strip() for x in retenir):
            raise ContenuInvalide(f"article « {slug} » : « À retenir » vide ou invalide")
        faq = []
        for q in a.get("faq") or []:
            faq.append((_txt(q, "question", 300), _txt(q, "reponse", 3000)))
        art = dict(slug=slug, cat=cat, photo=photo, alt=_txt(a, "photoAlt", 250), cta=cta,
                   title=_txt(a, "titre", 200), desc=_txt(a, "description", 400), intro=_txt(a, "intro", 3000),
                   sections=sections, retenir=[x.strip() for x in retenir], date=date, faq=faq)
        seo = _txt(a, "titreSeo", 200, obligatoire=False)
        if seo:
            art["seo_title"] = seo
        if ville:
            art["city"] = ville
        sortie.append(art)
    return sortie
