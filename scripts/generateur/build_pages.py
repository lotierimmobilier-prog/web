# -*- coding: utf-8 -*-
import os, json, datetime
from common import *

def _taille_visuel(fichier):
    """(largeur, hauteur) d'un visuel de assets/blog/ : lue dans le viewBox d'un SVG, sinon dans l'image."""
    chemin = f"{ROOT}/assets/blog/{fichier}"
    if fichier.endswith(".svg"):
        m = re.search(r'viewBox="\s*[\d.]+[\s,]+[\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', open(chemin, encoding="utf-8").read(2000))
        return (round(float(m.group(1))), round(float(m.group(2)))) if m else (1200, 630)
    return Image.open(chemin).size

def render_blocks(blocks, prefix="../"):
    out = []
    for b in blocks:
        if isinstance(b, list): out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b) + "</ul>")
        elif isinstance(b, str): out.append(f"<p>{e(b)}</p>")
        elif b["type"] == "tableau":
            tete = "".join(f'<th scope="col">{e(x)}</th>' for x in b["entetes"])
            corps = "".join("<tr>" + "".join((f'<th scope="row">{e(c)}</th>' if i == 0 else f"<td>{e(c)}</td>") for i, c in enumerate(l)) + "</tr>" for l in b["lignes"])
            leg = f'<caption>{e(b["legende"])}</caption>' if b.get("legende") else ""
            out.append(f'<div class="art-table" tabindex="0" role="region" aria-label="{e(b.get("legende") or "Tableau")}"><table>{leg}<thead><tr>{tete}</tr></thead><tbody>{corps}</tbody></table></div>')
        elif b["type"] == "chiffres":
            out.append('<ul class="art-chiffres">' + "".join(f'<li><strong>{e(x["valeur"])}</strong><span>{e(x["libelle"])}</span></li>' for x in b["items"]) + "</ul>")
        elif b["type"] == "image":
            w, h = _taille_visuel(b["fichier"])
            leg = f'<figcaption>{e(b["legende"])}</figcaption>' if b.get("legende") else ""
            out.append(f'<figure class="art-visuel"><img src="{prefix}assets/blog/{e(b["fichier"])}" alt="{e(b["alt"])}" width="{w}" height="{h}" loading="lazy" decoding="async">{leg}</figure>')
        elif b["type"] == "sources":
            out.append('<ul class="art-sources">' + "".join(
                (f'<li><a href="{e(x["url"])}" rel="noopener nofollow" target="_blank">{e(x["titre"])}</a></li>' if x.get("url") else f'<li>{e(x["titre"])}</li>') for x in b["items"]) + "</ul>")
    return "\n          ".join(out)

def _blocs_de(a, type_):
    return [b for _, blocs in a["sections"] for b in blocs if isinstance(b, dict) and b["type"] == type_]

CTA_TEXT = {
    "estimation": ("Un projet de vente ?", "Un conseiller estime votre bien en s'appuyant sur les ventes récentes de votre quartier.", "Demander une estimation", "#estimer"),
    "contact": ("Un projet d'achat ?", "Nos conseillers vous présentent les biens qui correspondent à votre budget et à vos critères.", "Parler à un conseiller", "#contact"),
    "location": ("Un bien à louer ?", "Recherche du locataire, bail, état des lieux, suivi : une gestion locative à partir de 39,99 € par mois.", "Confier mon bien en gestion", "#contact"),
    "syndic": ("Une question sur votre copropriété ?", "L'équipe syndic de LOTIER Immobilier vous répond sur le budget, les charges et les travaux.", "Contacter le syndic", "#contact"),
}

KIND_BY_CAT = {"Acheter": "acheter", "Vendre": "vendre", "Bailleur": "bailleur", "Locataire": "locataire", "Syndic": "syndic", "Villes": "agence"}

def article_page(a):
    prefix = "../"
    path = f"blog/{a['slug']}.html"
    url = f"{SITE}/{path}"
    ct = CTA_TEXT[a["cta"]]
    related = [x for x in ARTICLES_BY_DATE if x["slug"] != a["slug"] and x["cat"] == a["cat"]][:3]
    for x in ARTICLES_BY_DATE:
        if len(related) >= 3: break
        if x["slug"] != a["slug"] and x not in related: related.append(x)
    city_link = ""
    if a.get("city"):
        c = CITY_BY_KEY[a["city"]]
        city_link = f'<p class="city-link"><a class="text-link" href="{city_url(prefix, c)}">Voir notre page : agence immobilière à {e(c["name"])} →</a></p>'
    sections = "\n".join(f'          <h2>{e(h)}</h2>\n          {render_blocks(b)}' for h, b in a["sections"])
    retenir = "".join(f"<li>{e(x)}</li>" for x in a["retenir"])
    faqs = ART_FAQ.get(a["slug"], [])
    faq_html = ""
    if faqs:
        faq_html = '<section class="art-faq" aria-labelledby="faq-t"><h2 id="faq-t">Questions fréquentes</h2><div class="faq faq-simple">' + "".join(f'<details><summary><h3>{e(q)}</h3></summary><div class="answer"><p>{e(an)}</p></div></details>' for q, an in faqs) + '</div></section>'
    cta_href = f"{prefix}index.html{ct[3]}"
    body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><a href="{blog_index(prefix)}">Blog</a><span aria-hidden="true">/</span><span aria-current="page">{e(a["cat"])}</span></nav>
        <span class="label">{e(a["cat"])}</span>
        <h1 class="display page-title">{e(a["title"])}</h1>
        <p class="meta"><time datetime="{a["date"].isoformat()}">Publié le {fr_date(a["date"])}</time>{(f'<span aria-hidden="true">·</span><time datetime="{a["maj"].isoformat()}">Mis à jour le {fr_date(a["maj"])}</time>') if a.get("maj") and a["maj"] != a["date"] else ""}<span aria-hidden="true">·</span><span>{a["min"]} min de lecture</span><span aria-hidden="true">·</span><span>L'équipe LOTIER Immobilier</span></p>
      </div>
    </section>

    <article class="container article">
      <figure class="cover">{img(prefix, a["photo"], a["alt"], lazy=False, larg=860)}</figure>
      <p class="article-intro">{e(a["intro"])}</p>
      <div class="prose">
{sections}
      </div>
      {faq_html}
      <aside class="glass callout" aria-labelledby="retenir-t">
        <h2 id="retenir-t">À retenir</h2>
        <ul>{retenir}</ul>
      </aside>
      {city_link}
      <p class="disclaimer">Cet article donne des repères généraux et ne remplace pas un conseil personnalisé. Les règles évoluent : demandez à un conseiller de vérifier votre situation.</p>
      <section class="glass cta-box" aria-labelledby="cta-t">
        <div><h2 id="cta-t">{e(ct[0])}</h2><p>{e(ct[1])}</p></div>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="{cta_href}">{e(ct[2])} {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </section>
    </article>

    <section class="section container" aria-labelledby="t-related">
      <div class="section-head"><div class="stack-3"><span class="label">À lire aussi</span><h2 class="title" id="t-related">Dans le même esprit</h2></div><a class="text-link" href="{blog_index(prefix)}">Tous les articles</a></div>
      <div class="blog-grid">
        {"".join(card_article(prefix, x) for x in related)}
      </div>
    </section>'''
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "@id": url + "#article", "headline": a["title"], "description": a["desc"],
         "image": [f"{SITE}/assets/photos/{a['photo']}.jpg"] + [f"{SITE}/assets/blog/{b['fichier']}" for b in _blocs_de(a, "image")],
         "datePublished": a["date"].isoformat(), "dateModified": (a.get("maj") or a["date"]).isoformat(),
         "inLanguage": "fr-FR", "articleSection": a["cat"], "wordCount": a["words"],
         "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Organization", "name": "LOTIER Immobilier", "url": SITE + "/"},
         "publisher": {"@type": "Organization", "name": "LOTIER Immobilier", "logo": {"@type": "ImageObject", "url": SITE + "/assets/lotier-logo.png"}}},
        breadcrumb_ld([("Accueil", SITE + "/"), ("Blog", SITE + "/blog/"), (a["title"], url)]),
    ]
    _cit = [({"@type": "CreativeWork", "name": x["titre"], "url": x["url"]} if x.get("url") else {"@type": "CreativeWork", "name": x["titre"]}) for b in _blocs_de(a, "sources") for x in b["items"]]
    if _cit: ld[0]["citation"] = _cit
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
                   "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": an}} for q, an in faqs]})
    title = f"{a.get('seo_title', a['title'])} | LOTIER"
    _d = a["desc"] if len(a["desc"]) <= 165 else a["desc"][:162].rsplit(" ", 1)[0].rstrip(" ,;:.") + "…"      # description venue de Collab : ramenée à la longueur affichée par Google
    return shell(prefix, title, _d, path, body, ld, f"assets/photos/{a['photo']}.jpg", og_type="article", banner=True, kind=KIND_BY_CAT[a["cat"]])

def blog_index_page():
    prefix = "../"
    cats = []
    for a in ARTICLES_BY_DATE:
        if a["cat"] not in cats: cats.append(a["cat"])
    chips = '<button type="button" data-bf="all" aria-pressed="true">Tous les articles</button>' + "".join(f'<button type="button" data-bf="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)
    first = ARTICLES_BY_DATE[0]
    body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Blog</span></nav>
        <span class="label">Le blog de l'agence</span>
        <h1 class="display page-title">Conseils et actualités <em class="gold-text">de l'immobilier.</em></h1>
        <p class="lead">Vendre, acheter, louer, gérer une copropriété, mieux connaître nos villes : {len(ARTICLES)} guides écrits par les conseillers de LOTIER Immobilier.</p>
      </div>
    </section>

    <section class="section container" aria-label="Articles">
      <div class="chips" role="group" aria-label="Filtrer par thème">{chips}</div>
      <div class="blog-grid blog-grid-lg" id="blog-list">
        {"".join(card_article(prefix, a) for a in ARTICLES_BY_DATE)}
      </div>
    </section>'''
    ld = [
        {"@context": "https://schema.org", "@type": "Blog", "@id": SITE + "/blog/#blog", "name": "Le blog de LOTIER Immobilier", "url": SITE + "/blog/", "inLanguage": "fr-FR",
         "publisher": {"@id": SITE + "/#agence"},
         "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": f"{SITE}/blog/{a['slug']}.html", "datePublished": a["date"].isoformat()} for a in ARTICLES_BY_DATE]},
        breadcrumb_ld([("Accueil", SITE + "/"), ("Blog", SITE + "/blog/")]),
    ]
    return shell(prefix, "Blog immobilier : conseils pour vendre, acheter, louer | LOTIER",
                 f"{len(ARTICLES)} guides pratiques sur la vente, l'achat, la location et la copropriété, et des présentations de Béziers, Montpellier, Nîmes et Carcassonne.",
                 "blog/", body, ld, f"assets/photos/{first['photo']}.jpg", banner=True)

def city_page(c):
    prefix = ""
    url = f"{SITE}/{c['slug']}.html"
    art = BY_SLUG.get(c["article"]) or BY_SLUG["fixer-le-bon-prix-estimation"]
    others = [x for x in CITIES if x["key"] != c["key"]]
    svc = "".join(f'<article class="glass"><h3>{e(t)}</h3><p>{e(p)}</p><a class="text-link" href="index.html#contact">Nous contacter</a></article>' for t, p in c["services"])
    qs = "".join(f'<article class="glass quartier"><h3>{e(t)}</h3><p>{e(p)}</p></article>' for t, p in c["quartiers"])
    faq = "".join(f'<details><summary><span class="cat">Question</span><h3>{e(q)}</h3></summary><div class="answer"><p>{e(a)}</p></div></details>' for q, a in c["faq"])
    near = " · ".join(e(x) for x in c["nearby"])
    # Annonces de la ville (puis des communes voisines citées sur la page) : contenu frais et liens vers les fiches
    _fiches = [x for x in load_annonces() if x.get("description_html") is not None]
    _ici = [x for x in _fiches if x["ville"] == c["name"]]
    _pres = [x for x in _fiches if x["ville"] != c["name"] and x["ville"] in c["nearby"]]
    _sel = (_ici + _pres)[:6]
    biens = ""
    _liens_pv = "".join(f'<a class="text-link" href="nos-annonces/{g["slug"]}/">Biens {"à louer" if g["type"] != "vente" else "à vendre"} à {e(g["ville"])} ({len(g["annonces"])})</a> · ' for g in pages_ville_annonces() if g["ville"] == c["name"])
    if _sel:
        _tete = "Biens à vendre et à louer" if _ici else "Nos biens les plus proches,"
        _ou = (f"à {e(c['name'])}" if len(_ici) >= len(_sel) else f"à {e(c['name'])} et alentours") if _ici else ("autour d’" if c["name"][:1] in "AEIOUYH" else "autour de ") + e(c["name"])
        biens = f'''    <section class="section container" aria-labelledby="t-biens">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Nos annonces</span><h2 class="title" id="t-biens">{_tete} <em class="gold-text">{_ou}.</em></h2></div></div>
      <div class="cards ann-more-grid">{"".join(annonce_card(x, prefix) for x in _sel)}
      </div>
      <p style="margin-top:28px">{_liens_pv}<a class="text-link" href="nos-annonces/">Voir toutes nos annonces</a></p>
    </section>'''
    other_links = "".join(f'<a class="chip-link" href="{o["slug"]}.html">Immobilier à {e(o["name"])}</a>' for o in others)
    body = f'''    <section class="page-hero city-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <span class="croix-photo" style="background-image:url({prefix}assets/photos/{c["photo"]}.jpg)" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="index.html">Accueil</a><span aria-hidden="true">/</span><span>Nos villes</span><span aria-hidden="true">/</span><span aria-current="page">{e(c["name"])}</span></nav>
        <div class="city-grid">
          <div class="hero-copy">
            <span class="label">{e(c["dept"])} · {e(c["cp"])}</span>
            <h1 class="display page-title">{e(c["h1"])}</h1>
            <p class="lead">{e(c["lead"])}</p>
            <div class="acts">
              <a class="btn btn-gold btn-lg mag" href="index.html#contact">Recevoir des offres {ARROW}</a>
              <a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a>
            </div>
            <p class="small muted">{e(c["agency"])}</p>
          </div>
          <div class="city-photo">{img(prefix, c["photo"], c["alt"], lazy=False)}<span class="glass">{e(c["name"])}</span></div>
        </div>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-intro">
      <div class="city-intro">
        <div data-r>
          <span class="label">Votre agence à {e(c["name"])}</span>
          <h2 class="title" id="t-intro">Un conseiller qui connaît <em class="gold-text">{e(c["name"])}.</em></h2>
          {"".join(f"<p class='muted' style='margin-top:16px'>{e(p)}</p>" for p in c["intro"])}
        </div>
        <div class="photo" data-r>{img(prefix, c["photo2"], c["alt2"])}</div>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-svc">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Nos services</span><h2 class="title" id="t-svc">Vendre, louer, gérer à {e(c["name"])}</h2></div></div>
      <div class="trio" data-stagger>{svc}</div>
    </section>

    <section class="section container" aria-labelledby="t-quartiers">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Secteurs à connaître</span><h2 class="title" id="t-quartiers">Les secteurs de <em class="gold-text">{e(c["name"])}.</em></h2></div></div>
      <div class="cards" data-stagger>{qs}</div>
    </section>

    <section class="section container" aria-label="À lire">
      <div class="glass read-card" data-r>
        <a class="ph" href="blog/{art["slug"]}.html" tabindex="-1" aria-hidden="true">{img(prefix, art["photo"], art["alt"], larg=400)}</a>
        <div class="read-body">
          <span class="label">À lire sur le blog</span>
          <h2 class="title"><a href="blog/{art["slug"]}.html">{e(art["title"])}</a></h2>
          <p class="muted">{e(art["desc"])}</p>
          <a class="btn btn-navy mag" href="blog/{art["slug"]}.html">Lire l'article {ARROW}</a>
        </div>
      </div>
    </section>

{biens}

    <section class="section container" aria-labelledby="t-faq">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Questions fréquentes</span><h2 class="title" id="t-faq">Vos questions sur <em class="gold-text">{e(c["name"])}.</em></h2></div></div>
      <div class="faq" data-r>{faq}</div>
    </section>

    <section class="estim" aria-labelledby="t-estim">
      <div class="container">
        <div data-r>
          <h2 id="t-estim">Combien vaut votre bien à {e(c["name"])}&nbsp;?</h2>
          <p>Un conseiller compare votre bien aux ventes récentes de son secteur et vous explique le prix du marché.</p>
          <p class="alt-call">Ou appelez-nous : <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
        </div>
        <form class="estim-card" id="estimer" data-r aria-labelledby="est-t" action="{COLLAB_ESTIMER}" method="get">
          <div class="ph">{img(prefix, "cles", "Photo d'illustration : remise de clés d'un logement")}</div>
          <h3 id="est-t">Demandez votre estimation</h3>
          <input type="hidden" name="mode" value="vente">
          <div class="field"><label for="est-adresse">Adresse du bien</label><input id="est-adresse" name="adresse" type="text" autocomplete="street-address" placeholder="Ex. 12 rue Française, {e(c["name"])}"></div>
          <div class="field"><label for="est-tel">Votre téléphone</label><input id="est-tel" name="telephone" type="tel" autocomplete="tel" placeholder="06 00 00 00 00"></div>
          <button type="submit" class="btn btn-navy btn-lg btn-block">Demander mon estimation</button>
        </form>
      </div>
    </section>

    <section class="section container" id="contact" aria-labelledby="t-near">
      <div class="glass near" data-r>
        <div>
          <span class="label">Autour de {e(c["name"])}</span>
          <h2 class="title" id="t-near">Nous intervenons aussi à…</h2>
          <p class="muted" style="margin-top:12px">{near}</p>
        </div>
        <div>
          <span class="label">Nos autres villes</span>
          <div class="chip-links">{other_links}</div>
          <p class="small muted" style="margin-top:16px">Contact : <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> · <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a><br>Siège : 40 rue Française, 1er étage, 34500 Béziers</p>
        </div>
      </div>
    </section>'''
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]}
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url, "name": c["title"], "description": c["desc"], "inLanguage": "fr-FR",
               "about": {"@type": "City", "name": c["name"], "containedInPlace": {"@type": "AdministrativeArea", "name": c["dept"]}},
               "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#agence"}}
    agent = dict(AGENCE_LD); agent["@context"] = "https://schema.org"
    agent["areaServed"] = [{"@type": "City", "name": c["name"]}] + [{"@type": "City", "name": n} for n in c["nearby"][:4]]
    agent["description"] = c["desc"]
    ld = [page_ld, agent, faq_ld, breadcrumb_ld([("Accueil", SITE + "/"), ("Nos villes", SITE + "/#villes"), (c["name"], url)])]
    return shell(prefix, c["title"], c["desc"], f"{c['slug']}.html", body, ld, f"assets/photos/{c['photo']}.jpg", banner=True, kind="ville", city=c["name"])

# ---------- Écriture des fichiers ----------
os.makedirs(f"{ROOT}/blog", exist_ok=True)
# Un article qui n'est plus dans la liste (dépublié dans Collab) disparaît du site : sa page et sa version Markdown sont supprimées,
# pas seulement retirées de l'index, du plan du site et de llms.txt.
_slugs = {a["slug"] for a in ARTICLES}
for _f in os.listdir(f"{ROOT}/blog"):
    _nom, _ext = os.path.splitext(_f)
    if _ext in (".html", ".md") and _nom != "index" and _nom not in _slugs:
        os.remove(f"{ROOT}/blog/{_f}")
        print("article retiré :", _f)
for a in ARTICLES:
    open(f"{ROOT}/blog/{a['slug']}.html", "w", encoding="utf-8").write(article_page(a))
open(f"{ROOT}/blog/index.html", "w", encoding="utf-8").write(blog_index_page())
for c in CITIES:
    open(f"{ROOT}/{c['slug']}.html", "w", encoding="utf-8").write(city_page(c))

# plan du site
today = "2026-11-14"      # dernière révision des pages fixes (à avancer quand leur contenu change)
try: maj_ann = json.load(open(f"{ROOT}/data/annonces.json", encoding="utf-8")).get("maj") or today      # pages nourries par les annonces
except (OSError, ValueError): maj_ann = today
urls = [(f"{SITE}/", today, "1.0", "weekly")]
urls += [(f"{SITE}/{c['slug']}.html", maj_ann, "0.9", "weekly") for c in CITIES]
urls += [(f"{SITE}/blog/", max(a["date"] for a in ARTICLES).isoformat(), "0.8", "weekly")]
urls += [(f"{SITE}/rejoindre/", today, "0.8", "monthly")]
urls += [(f"{SITE}/rejoindre/comparatif/", today, "0.8", "monthly")]
_ag = json.load(open(f"{ROOT}/data/agents.json", encoding="utf-8")).get("agents", []) if os.path.exists(f"{ROOT}/data/agents.json") else []
_cfg_ag = json.load(open(f"{ROOT}/data/agents-config.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/data/agents-config.json") else {}
if _cfg_ag.get("indexable") and _ag:     # la page des agents n'entre dans le sitemap qu'une fois ouverte aux moteurs
    urls += [(f"{SITE}/nos-agents/", maj_ann, "0.7", "weekly")] + [(f"{SITE}/nos-agents/{a['slug']}/", maj_ann, "0.6", "weekly") for a in _ag if a.get("rsac")]
if EQUIPE: urls += [(f"{SITE}/equipe/", today, "0.5", "monthly")]
urls += [(f"{SITE}/nos-annonces/{g['slug']}/", maj_ann, "0.7", "daily") for g in pages_ville_annonces()]
_da = dates_annonces()
urls += [(f"{SITE}/annonces/{a['id']}/", _da.get(a["id"], {}).get("maj") or maj_ann, "0.6", "weekly") for a in load_annonces() if a.get("description_html") is not None]
urls += [(f"{SITE}/{x}/", today, "0.8", "monthly") for x in ("a-propos", "contact", "nos-annonces", "notre-service", "vente", "location", "syndic", "nos-honoraires")]
if os.path.exists(f"{ROOT}/data/partenaires.json"): urls += [(f"{SITE}/sites-partenaires/", today, "0.4", "monthly")]
urls += [(f"{SITE}/plan-du-site.html", today, "0.3", "monthly")]
urls += [(f"{SITE}/blog/{a['slug']}.html", (a.get("maj") or a["date"]).isoformat(), "0.7", "monthly") for a in ARTICLES_BY_DATE]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- À compléter à chaque nouvelle page : annonces, articles, villes. -->\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, d, p, f in urls:
    sm += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{f}</changefreq>\n    <priority>{p}</priority>\n  </url>\n"
sm += "</urlset>\n"
open(f"{ROOT}/sitemap.xml", "w", encoding="utf-8").write(sm)

# llms.txt
ll = open(f"{ROOT}/llms.txt", encoding="utf-8").read()
cut = ll.split("## Pages principales")[0]
ll = cut + "## Pages principales\n\n- [Accueil](https://lotier.immo/): présentation, annonces, estimation en ligne.\n- [Conseils immo](https://lotier.immo/#conseils): réponses courtes aux questions des vendeurs, acquéreurs, bailleurs, locataires et copropriétaires.\n- [Blog](https://lotier.immo/blog/): " + str(len(ARTICLES)) + " guides pratiques.\n- [À propos](https://lotier.immo/a-propos/): qui nous sommes, métiers, informations légales.\n- [Nos annonces](https://lotier.immo/nos-annonces/): biens à vendre et à louer.\n- [Contact](https://lotier.immo/contact/): téléphone, e-mail et adresses des agences.\n- [Honoraires](https://lotier.immo/nos-honoraires/): barème de vente, de location, de gestion et de syndic.\n- [Notre service](https://lotier.immo/notre-service/): transparence, personnalisation, proximité.\n- [Devenir agent immobilier indépendant](https://lotier.immo/rejoindre/): conditions, simulateur de commission et candidature.\n- [Comparatif réseaux, agence classique et modèle hybride LOTIER](https://lotier.immo/rejoindre/comparatif/): comparatif et FAQ.\n\n## Pour les agents\n\n- Chaque page existe en Markdown : même adresse avec l'en-tête `Accept: text/markdown`, ou adresse terminée par `index.md` (ou `.md` pour les pages `.html`).\n- [Serveur MCP en lecture seule](https://lotier.immo/mcp/) décrit par la [carte de serveur](https://lotier.immo/.well-known/mcp/server-card.json).\n\n## Pages par ville\n\n"
for c in CITIES:
    ll += f"- [Agence immobilière à {c['name']}]({SITE}/{c['slug']}.html): vente, location, gestion locative et syndic à {c['name']}.\n"
if _cfg_ag.get("indexable") and _ag:
    ll += f"\n## Nos agents\n\n- [Nos agents par secteur]({SITE}/nos-agents/): les conseillers LOTIER Immobilier, leur secteur et leurs annonces.\n"
    for a in [x for x in _ag if x.get("rsac")]:
        ll += f"- [{a['prenom']} {a['nom']}]({SITE}/nos-agents/{a['slug']}/): {a.get('role') or 'agent commercial'}" + (f", secteur {', '.join(a['communes'][:4])}" if a.get("communes") else "") + ".\n"
try: _part = json.load(open(f"{ROOT}/data/partenaires.json", encoding="utf-8")).get("sites", [])
except (OSError, ValueError): _part = []
if _part:
    ll += f"\n## Sites partenaires\n\n- [Sites partenaires]({SITE}/sites-partenaires/): " + " ; ".join(f"{p['nom']} ({p['url']}), {p.get('accroche', '').rstrip('.').lower()}" for p in _part) + ".\n"
_la = [a for a in load_annonces() if a.get("description_html") is not None]
if _la:
    ll += (f"\n## Annonces en cours ({len(_la)})\n\n"
           f"- [Catalogue complet en JSON]({SITE}/annonces/catalogue.json): toutes les annonces avec type de bien, commune, département, prix, surface, pièces, équipements, classe énergie, référence, agent, texte et date de mise à jour. Régénéré chaque jour.\n")
    for a in sorted(_la, key=lambda x: (x["type"] != "vente", x.get("ville") or "", x.get("prix") or 0)):
        c = entree_catalogue(a)
        prix = (f"{c['prix']:,.0f}".replace(",", " ") + (" € par mois" if c["transaction"] == "location" else " €")) if c["prix"] else "prix sur demande"
        ll += f"- [{c['titre']}]({c['url']}): {prix}" + (f", {c['departement_nom']} ({c['departement']})" if c["departement"] else "") + (f", classe énergie {c['dpe']}" if c["dpe"] else "") + (f", réf. {c['reference']}" if c["reference"] else "") + ".\n"
_pv = pages_ville_annonces()
if _pv:
    ll += "\n## Annonces par ville\n\n"
    for g in _pv:
        ll += f"- [Biens {'à louer' if g['type'] != 'vente' else 'à vendre'} à {g['ville']}]({SITE}/nos-annonces/{g['slug']}/): {len(g['annonces'])} annonces, mises à jour chaque jour.\n"
ll += ("\n## Honoraires (barème publié)\n\n"
       "- Vente : honoraires TTC à la charge du vendeur, inclus dans le prix affiché. 5 % à partir de 200 001 €, 6 % de 150 001 à 200 000 €, 7 % de 100 001 à 150 000 €, 8 % de 70 001 à 100 000 €, 10 % (minimum 3 000 €) de 10 001 à 70 000 €, 3 000 € jusqu'à 10 000 €.\n"
       "- Mise en location : 8,07 €, 10,09 € ou 12,10 € TTC par m² selon la zone (autre, tendue, très tendue), plus 3,03 € TTC par m² pour l'état des lieux.\n"
       "- Gestion locative : gestion complète à 7 % HT par mois (8,40 % TTC), ou gestion locative à 39,99 € TTC par mois. Assurance loyers impayés facultative : 4 % ou 3,5 % TTC du loyer charges comprises.\n"
       "- Syndic : 2 000 € par an de 1 à 10 lots, puis 160 € par lot (11 à 50), 150 € (51 à 100), 144 € (101 à 200), sur devis au-delà.\n"
       f"- [Barème complet et simulateur]({SITE}/nos-honoraires/).\n")
if EQUIPE:
    ll += f"\n## L'équipe\n\n- [L'équipe de l'agence]({SITE}/equipe/): direction, gestion locative, syndic de copropriété et accueil.\n"
ll += "\n## Articles du blog\n\n"
for a in ARTICLES_BY_DATE:
    ll += f"- [{a['title']}]({SITE}/blog/{a['slug']}.html) ({a['cat']}, {a['date'].isoformat()}): {a['desc']}\n"
ll += "\n## Contact\n\n- Téléphone : 04 67 11 28 31\n- E-mail : contact@lotier-immobilier.com\n- Siège : 40 rue Française, 1er étage, 34500 Béziers\n- Carte professionnelle CPI3401 2016 000 014 824, garantie financière SOCAF n° 105 708 080\n"
open(f"{ROOT}/llms.txt", "w", encoding="utf-8").write(ll)
print(len(ARTICLES), "articles,", len(CITIES), "villes")
for a in ARTICLES_BY_DATE: print(a["date"], a["min"], "min", a["words"], "mots", a["slug"])
