#!/usr/bin/env python3
"""Relit la liste des agents dans Collab et l'écrit dans data/agents.json (page /nos-agents/).

Usage : python3 scripts/sync_agents.py [--souple]

  --souple   (mise à jour de nuit) si Collab ne répond pas ou renvoie une liste vide, on garde le fichier actuel et on le dit.

Lecture publique de Collab (GET, sans clé) : /api/public/v1/agents et /api/public/v1/secteurs.
Les photos sont copiées dans assets/agents/ (le site ne dépend pas de Collab pour les afficher).
Réglages (secteurs affichés, personnes masquées, orthographe) : data/agents-config.json.
Le fichier écrit ne contient aucune date : une relecture sans changement ne modifie rien. Aucun secret."""
import io, json, re, sys, time, unicodedata, urllib.request
from pathlib import Path
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
BASE = "https://collab.lotier-immobilier.com/api/public/v1"
SORTIE = RACINE / "data" / "agents.json"
CONFIG = RACINE / "data" / "agents-config.json"
PHOTOS = RACINE / "assets" / "agents"
UA = "lotier-site-agents"


def lire(url, binaire=False, tentatives=3):
    derniere = None
    for i in range(tentatives):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json" if not binaire else "*/*"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = r.read()
                return d if binaire else json.loads(d.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            derniere = e; time.sleep(2 ** i)
    raise RuntimeError(f"Collab injoignable ({url}) : {derniere}")


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()


def tel(t):
    d = re.sub(r"\D", "", t or "")
    if d.startswith("33") and len(d) == 11: d = "0" + d[2:]
    return " ".join(d[i:i + 2] for i in range(0, len(d), 2)) if len(d) == 10 else (t or "").strip()


def titre(s):
    return s.title() if s and s.isupper() else s


def secteurs_de(a, cfg, noms_collab):
    sect = cfg["secteurs"]; ids = []
    f = norm(a.get("fonction"))
    gerant = "gerant" in f or "direct" in f
    for s in sect:                                            # 1. secteur annoncé dans la fonction
        if any(m in f for m in s["mots_fonction"]) and s["id"] not in ids: ids.append(s["id"])
    for sid in a.get("secteurs") or []:                       # 2. secteurs choisis dans Collab
        nom = norm(noms_collab.get(sid, ""))
        for s in sect:
            if nom and any(m in nom for m in s["mots_fonction"]) and s["id"] not in ids: ids.append(s["id"])
    communes = [norm(c.strip()) for c in (a.get("communes_couvertes") or "").split(",") if c.strip()]
    for s in sect:                                            # 3. communes couvertes
        if s["id"] not in ids and any(norm(c) in communes for c in s["communes"]): ids.append(s["id"])
    return ids, gerant


RESEAUX = ("facebook", "instagram", "linkedin", "tiktok", "youtube", "whatsapp")


def https(u):
    u = (u or "").strip()
    return u if re.match(r"^https://[^\s]+$", u) else ""


def mentions(a, p):
    """Mentions légales de l'agent (page Collab « Mes mentions légales »). Lues dans a["mentions_legales"] si Collab les expose
    (rsac, rsac_ville) ; l'accord de publication dans a["accord_publication"] (vrai/faux). Sinon dans data/agents-config.json."""
    m = a.get("mentions_legales") if isinstance(a.get("mentions_legales"), dict) else {}
    rsac = (p.get("rsac") or m.get("rsac") or a.get("rsac") or "").strip()
    ville = (p.get("rsac_ville") or m.get("rsac_ville") or m.get("greffe") or "").strip()
    acc = a.get("accord_publication", p.get("accord_publication"))
    return {"rsac": rsac or None, "rsac_ville": ville or None, "accord": acc if isinstance(acc, bool) else None}


def profil(a, cfg):
    """Champs de présentation : lus dans Collab s'il les fournit (presentation, reseaux, specialites, lien_google, mots_cles, rsac),
    sinon dans data/agents-config.json (profils). Rien n'est inventé : un champ absent reste vide."""
    p = (cfg.get("profils") or {}).get(a["id"], {})
    def pick(*cles):
        for k in cles:
            if a.get(k): return a[k]
        return None
    pres = (p.get("presentation") or pick("presentation") or "").strip()
    res_src = p.get("reseaux") or pick("reseaux") or {}
    res = {k: https(res_src.get(k)) for k in RESEAUX if https(res_src.get(k))}
    cat = cfg.get("specialites_catalogue", {})
    spe = [x for x in (p.get("specialites") or pick("specialites") or []) if x in cat]
    mots = [m.strip() for m in (p.get("mots_cles") or pick("mots_cles") or []) if str(m).strip()]
    return {"presentation": pres or None, "reseaux": res, "specialites": spe, "google": https(p.get("google") or pick("lien_google", "google")) or None,
            "mots_cles": mots, **mentions(a, p)}


def main():
    souple = "--souple" in sys.argv
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    ancien = json.loads(SORTIE.read_text(encoding="utf-8")) if SORTIE.exists() else None
    try:
        brut = lire(BASE + "/agents").get("agents", [])
        try: noms = {s["id"]: s.get("nom", "") for s in lire(BASE + "/secteurs").get("secteurs", [])}
        except Exception: noms = {}
        if not brut: raise RuntimeError("liste d'agents vide")
    except Exception as e:  # noqa: BLE001
        if souple and ancien:
            print(f"::warning::Agents de Collab non récupérés ({e}) : data/agents.json conservé tel quel."); return
        sys.exit(f"Échec : {e}")
    PHOTOS.mkdir(parents=True, exist_ok=True)
    out, gardees = [], set()
    for a in brut:
        if a["id"] in cfg.get("masquer", []): continue
        prenom = cfg["corrections_prenom"].get(a["prenom"], a["prenom"])
        ids, gerant = secteurs_de(a, cfg, noms)
        slug = re.sub(r"[^a-z0-9]+", "-", norm(f"{prenom} {a['nom']}")).strip("-")
        photo = None
        if a.get("photo_url"):
            dest = PHOTOS / f"{slug}.jpg"
            try:
                im = Image.open(io.BytesIO(lire(a["photo_url"], binaire=True))).convert("RGB"); im.thumbnail((800, 800))
                im.save(dest, "JPEG", quality=84, optimize=True, progressive=True); photo = f"assets/agents/{slug}.jpg"; gardees.add(dest.name)
            except Exception as e:  # noqa: BLE001
                print(f"::warning::Photo de {prenom} non récupérée ({e})")
                if dest.exists(): photo = f"assets/agents/{slug}.jpg"; gardees.add(dest.name)
        out.append({"id": a["id"], "slug": slug, "prenom": prenom, "nom": titre(a["nom"]), "fonction": (a.get("fonction") or "").strip(),
                    "role": "Gérant" if gerant else "Agent commercial indépendant", "secteurs": ids,
                    "communes": [c.strip() for c in (a.get("communes_couvertes") or "").split(",") if c.strip()],
                    "email": (a.get("email_pro") or "").strip(), "telephone": tel(a.get("telephone_pro")),
                    "mini_site": a.get("url_mini_site") or "", "photo": photo, "bio": (a.get("bio_courte") or "").strip() or None,
                    **profil(a, cfg)})
    # Agents absents de la liste publique de Collab (profil non publié) : saisis à la main dans data/agents-config.json, « ajouts ».
    deja = {x["email"].lower() for x in out}
    for x in cfg.get("ajouts") or []:
        if x.get("email", "").lower() in deja or x.get("id") in cfg.get("masquer", []): continue
        fake = {"fonction": x.get("fonction", ""), "secteurs": [], "communes_couvertes": ", ".join(x.get("communes", []))}
        ids, gerant = secteurs_de(fake, cfg, {})
        ph = x.get("photo") if x.get("photo") and (RACINE / x["photo"]).exists() else None
        if ph: gardees.add(Path(ph).name)
        slug = re.sub(r"[^a-z0-9]+", "-", norm(f"{x['prenom']} {x['nom']}")).strip("-")
        out.append({"id": x.get("id") or "ajout_" + slug, "slug": slug, "prenom": x["prenom"], "nom": x["nom"], "fonction": x.get("fonction", ""),
                    "role": "Gérant" if gerant else "Agent commercial indépendant", "secteurs": x.get("secteurs") or ids, "communes": x.get("communes", []),
                    "email": x.get("email", ""), "telephone": tel(x.get("telephone")), "mini_site": x.get("mini_site", ""), "photo": ph, "bio": x.get("bio"),
                    **profil({"id": x.get("id") or "ajout_" + slug, **x}, cfg)})
    ordre = cfg.get("ordre") or []
    out.sort(key=lambda x: (ordre.index(x["id"]) if x["id"] in ordre else 999, norm(x["prenom"])))
    for f in PHOTOS.glob("*.jpg"):
        if f.name not in gardees: f.unlink()
    nouveau = {"source": BASE + "/agents", "secteurs": [s["id"] for s in cfg["secteurs"]], "agents": out}
    SORTIE.write_text(json.dumps(nouveau, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out)} agent(s) écrits dans {SORTIE.name}")


main()
