# -*- coding: utf-8 -*-
import os, json, datetime
from common import *

def render_blocks(blocks):
    out = []
    for b in blocks:
        if isinstance(b, list): out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in b) + "</ul>")
        else: out.append(f"<p>{e(b)}</p>")
    return "\n          ".join(out)

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
        <p class="meta"><time datetime="{a["date"].isoformat()}">Publié le {fr_date(a["date"])}</time><span aria-hidden="true">·</span><span>{a["min"]} min de lecture</span><span aria-hidden="true">·</span><span>L'équipe LOTIER Immobilier</span></p>
      </div>
    </section>

    <article class="container article">
      <figure class="cover">{img(prefix, a["photo"], a["alt"], lazy=False)}</figure>
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
         "image": [f"{SITE}/assets/photos/{a['photo']}.jpg"], "datePublished": a["date"].isoformat(), "dateModified": a["date"].isoformat(),
         "inLanguage": "fr-FR", "articleSection": a["cat"], "wordCount": a["words"],
         "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Organization", "name": "LOTIER Immobilier", "url": SITE + "/"},
         "publisher": {"@type": "Organization", "name": "LOTIER Immobilier", "logo": {"@type": "ImageObject", "url": SITE + "/assets/lotier-logo.png"}}},
        breadcrumb_ld([("Accueil", SITE + "/"), ("Blog", SITE + "/blog/index.html"), (a["title"], url)]),
    ]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
                   "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": an}} for q, an in faqs]})
    title = f"{a.get('seo_title', a['title'])} | LOTIER"
    return shell(prefix, title, a["desc"], path, body, ld, f"assets/photos/{a['photo']}.jpg", og_type="article", banner=True, kind=KIND_BY_CAT[a["cat"]])

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
        {"@context": "https://schema.org", "@type": "Blog", "@id": SITE + "/blog/index.html#blog", "name": "Le blog de LOTIER Immobilier", "url": SITE + "/blog/index.html", "inLanguage": "fr-FR",
         "publisher": {"@id": SITE + "/#agence"},
         "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": f"{SITE}/blog/{a['slug']}.html", "datePublished": a["date"].isoformat()} for a in ARTICLES_BY_DATE]},
        breadcrumb_ld([("Accueil", SITE + "/"), ("Blog", SITE + "/blog/index.html")]),
    ]
    return shell(prefix, "Blog immobilier : conseils pour vendre, acheter, louer | LOTIER",
                 f"{len(ARTICLES)} guides pratiques sur la vente, l'achat, la location et la copropriété, et des présentations de Béziers, Montpellier, Nîmes et Carcassonne.",
                 "blog/index.html", body, ld, f"assets/photos/{first['photo']}.jpg", banner=True)

def city_page(c):
    prefix = ""
    url = f"{SITE}/{c['slug']}.html"
    art = BY_SLUG.get(c["article"]) or BY_SLUG["fixer-le-bon-prix-estimation"]
    others = [x for x in CITIES if x["key"] != c["key"]]
    svc = "".join(f'<article class="glass"><h3>{e(t)}</h3><p>{e(p)}</p><a class="text-link" href="index.html#contact">Nous contacter</a></article>' for t, p in c["services"])
    qs = "".join(f'<article class="glass quartier"><h3>{e(t)}</h3><p>{e(p)}</p></article>' for t, p in c["quartiers"])
    faq = "".join(f'<details><summary><span class="cat">Question</span><h3>{e(q)}</h3></summary><div class="answer"><p>{e(a)}</p></div></details>' for q, a in c["faq"])
    near = " · ".join(e(x) for x in c["nearby"])
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
        <a class="ph" href="blog/{art["slug"]}.html" tabindex="-1" aria-hidden="true">{img(prefix, art["photo"], art["alt"])}</a>
        <div class="read-body">
          <span class="label">À lire sur le blog</span>
          <h2 class="title"><a href="blog/{art["slug"]}.html">{e(art["title"])}</a></h2>
          <p class="muted">{e(art["desc"])}</p>
          <a class="btn btn-navy mag" href="blog/{art["slug"]}.html">Lire l'article {ARROW}</a>
        </div>
      </div>
    </section>

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
        <form class="estim-card" id="estimer" data-r aria-labelledby="est-t">
          <div class="ph">{img(prefix, "cles", "Photo d'illustration : remise de clés d'un logement")}</div>
          <h3 id="est-t">Demandez votre estimation</h3>
          <div class="field"><label for="est-adresse">Adresse du bien</label><input id="est-adresse" type="text" autocomplete="street-address" placeholder="Ex. 12 rue Française, {e(c["name"])}"></div>
          <div class="field"><label for="est-tel">Votre téléphone</label><input id="est-tel" type="tel" autocomplete="tel" placeholder="06 00 00 00 00"></div>
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
for a in ARTICLES:
    open(f"{ROOT}/blog/{a['slug']}.html", "w", encoding="utf-8").write(article_page(a))
open(f"{ROOT}/blog/index.html", "w", encoding="utf-8").write(blog_index_page())
for c in CITIES:
    open(f"{ROOT}/{c['slug']}.html", "w", encoding="utf-8").write(city_page(c))

# plan du site
today = "2026-11-05"
urls = [(f"{SITE}/", today, "1.0", "weekly")]
urls += [(f"{SITE}/{c['slug']}.html", today, "0.9", "monthly") for c in CITIES]
urls += [(f"{SITE}/blog/index.html", max(a["date"] for a in ARTICLES).isoformat(), "0.8", "weekly")]
urls += [(f"{SITE}/rejoindre/", today, "0.8", "monthly")]
urls += [(f"{SITE}/rejoindre/comparatif/", today, "0.8", "monthly")]
urls += [(f"{SITE}/{x}/", today, "0.8", "monthly") for x in ("a-propos", "contact", "notre-service", "vente", "location", "syndic")]
urls += [(f"{SITE}/plan-du-site.html", today, "0.3", "monthly")]
urls += [(f"{SITE}/blog/{a['slug']}.html", a["date"].isoformat(), "0.7", "monthly") for a in ARTICLES_BY_DATE]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- À compléter à chaque nouvelle page : annonces, articles, villes. -->\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, d, p, f in urls:
    sm += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{f}</changefreq>\n    <priority>{p}</priority>\n  </url>\n"
sm += "</urlset>\n"
open(f"{ROOT}/sitemap.xml", "w", encoding="utf-8").write(sm)

# llms.txt
ll = open(f"{ROOT}/llms.txt", encoding="utf-8").read()
cut = ll.split("## Pages principales")[0]
ll = cut + "## Pages principales\n\n- [Accueil](https://lotier.immo/): présentation, annonces, estimation en ligne.\n- [Conseils immo](https://lotier.immo/#conseils): réponses courtes aux questions des vendeurs, acquéreurs, bailleurs, locataires et copropriétaires.\n- [Blog](https://lotier.immo/blog/index.html): " + str(len(ARTICLES)) + " guides pratiques.\n- [À propos](https://lotier.immo/a-propos/): qui nous sommes, métiers, informations légales.\n- [Contact](https://lotier.immo/contact/): téléphone, e-mail et adresses des agences.\n- [Honoraires](https://lotier.immo/nos-honoraires/): barème de vente, de location, de gestion et de syndic.\n- [Notre service](https://lotier.immo/notre-service/): transparence, personnalisation, proximité.\n- [Devenir agent immobilier indépendant](https://lotier.immo/rejoindre/): conditions, simulateur de commission et candidature.\n- [Comparatif réseaux, agence classique et modèle hybride LOTIER](https://lotier.immo/rejoindre/comparatif/): comparatif et FAQ.\n\n## Pour les agents\n\n- Chaque page existe en Markdown : même adresse avec l'en-tête `Accept: text/markdown`, ou adresse terminée par `index.md` (ou `.md` pour les pages `.html`).\n- [Serveur MCP en lecture seule](https://lotier.immo/mcp/) décrit par la [carte de serveur](https://lotier.immo/.well-known/mcp/server-card.json).\n\n## Pages par ville\n\n"
for c in CITIES:
    ll += f"- [Agence immobilière à {c['name']}]({SITE}/{c['slug']}.html): vente, location, gestion locative et syndic à {c['name']}.\n"
ll += "\n## Articles du blog\n\n"
for a in ARTICLES_BY_DATE:
    ll += f"- [{a['title']}]({SITE}/blog/{a['slug']}.html) ({a['cat']}, {a['date'].isoformat()}): {a['desc']}\n"
ll += "\n## Contact\n\n- Téléphone : 04 67 11 28 31\n- E-mail : contact@lotier-immobilier.com\n- Siège : 40 rue Française, 1er étage, 34500 Béziers\n- Carte professionnelle CPI3401 2016 000 014 824, garantie financière SOCAF n° 105 708 080\n"
open(f"{ROOT}/llms.txt", "w", encoding="utf-8").write(ll)
print(len(ARTICLES), "articles,", len(CITIES), "villes")
for a in ARTICLES_BY_DATE: print(a["date"], a["min"], "min", a["words"], "mots", a["slug"])
