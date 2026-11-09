import json, html, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://lotier.immo"
PHONE_DISPLAY = "04 67 11 28 31"
PHONE_TEL = "+33467112831"
e = html.escape

FAQ = [
    ("Vendeur", "Quels documents préparer avant de vendre mon bien ?",
     "Rassemblez votre titre de propriété, votre dernière taxe foncière et les diagnostics techniques obligatoires, dont le DPE. Pour un appartement, ajoutez le règlement de copropriété, les derniers procès-verbaux d'assemblée générale et le relevé de charges. Un conseiller LOTIER vous remet la liste exacte selon votre bien."),
    ("Vendeur", "Comment est estimé le prix de mon bien ?",
     "Un conseiller compare votre bien aux ventes récentes de votre quartier, puis tient compte de la surface, de l'état, de l'étage, des extérieurs et des charges. La visite permet d'affiner : elle donne un prix réaliste, ni trop haut, ni trop bas."),
    ("Acquéreur", "Comment préparer mon achat avant les visites ?",
     "Faites chiffrer votre budget avec votre banque ou un courtier (apport, mensualité, frais de notaire), puis listez les critères indispensables et ceux qui peuvent attendre. Vous visiterez moins, mais mieux, et vous pourrez faire une offre rapidement."),
    ("Bailleur", "Que comprend la gestion locative ?",
     "Recherche et sélection du locataire, rédaction du bail, état des lieux, encaissement des loyers, quittances et suivi du logement au quotidien. Notre offre démarre à 39,99 € par mois."),
    ("Bailleur", "Le DPE a-t-il un impact sur la location de mon bien ?",
     "Oui. Le diagnostic de performance énergétique est obligatoire pour louer, et sa classe peut limiter la mise en location. Les règles évoluent : demandez à un conseiller de vérifier la situation de votre bien."),
    ("Locataire", "Comment réussir mon état des lieux d'entrée ?",
     "Notez par écrit tout ce que vous constatez (murs, sols, équipements, compteurs), prenez des photos datées et gardez un exemplaire signé. Cela évite les litiges à la sortie."),
    ("Copropriétaire", "À quoi sert le syndic de copropriété ?",
     "Le syndic applique les décisions de l'assemblée générale, gère le budget et les charges, fait entretenir l'immeuble et suit les contrats et les travaux. Il convoque aussi l'assemblée générale chaque année."),
]
CATS = ["Vendeur", "Acquéreur", "Bailleur", "Locataire", "Copropriétaire"]
CITIES = ["Béziers", "Montpellier", "Nîmes", "Avignon", "Narbonne", "Carcassonne", "Agde"]

def img(name, alt, cls="", lazy=True):
    path = f"{ROOT}/assets/photos/{name}.jpg"
    w, h = Image.open(path).size
    return f'<img src="assets/photos/{name}.jpg" alt="{e(alt)}" width="{w}" height="{h}"{" loading=\"lazy\" decoding=\"async\"" if lazy else ""}{" class=\"" + cls + "\"" if cls else ""}>'

def svg(path):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg>'

NEWS_ARTS = C.ARTICLES_BY_DATE[:4]
def _side(a):
    return f'''<article class="news-item"><div><span class="label">{e(a["cat"])} · {C.fr_date(a["date"])}</span><h3><a href="blog/{a["slug"]}.html">{e(a["title"])}</a></h3><a class="text-link" href="blog/{a["slug"]}.html">Lire l'article</a></div><div class="ph">{img(a["photo"], a["alt"])}</div></article>'''
_m = NEWS_ARTS[0]
NEWS = f'''<section class="section container" id="actualites" aria-labelledby="t-actu">
      <div class="section-head" data-r>
        <div class="stack-3"><span class="label">Actualités</span><h2 class="title" id="t-actu">L'actu immo de la semaine</h2></div>
        <a class="text-link" href="blog/index.html">Tous les articles ({len(C.ARTICLES)})</a>
      </div>
      <div class="news">
        <article class="news-main" data-r>
          {img(_m["photo"], _m["alt"])}
          <div class="body">
            <span class="label">{e(_m["cat"])} · {C.fr_date(_m["date"])}</span>
            <h3><a href="blog/{_m["slug"]}.html" style="text-decoration:none">{e(_m["title"])}</a></h3>
            <p>{e(_m["desc"])}</p>
            <a class="text-link" href="blog/{_m["slug"]}.html">Lire l'article</a>
          </div>
        </article>
        <div class="news-side" data-stagger>
          {"".join(_side(a) for a in NEWS_ARTS[1:])}
        </div>
      </div>
    </section>'''
_VT = {"beziers": ("bez-pont", "Siège de l'agence, rue Française. Cathédrale, canal du Midi et proximité de la mer."),
       "montpellier": ("montpellier", "Écusson, Antigone, Port Marianne : une ville jeune, universitaire et en mouvement."),
       "nimes": ("nimes", "Arènes, Maison Carrée, jardins de la Fontaine. Une agence LOTIER à Nîmes."),
       "carcassonne": ("carcassonne", "Cité médiévale, Bastide Saint-Louis et canal du Midi, sur le couloir de l'Aude."),
       "narbonne": ("narbonne", "Cathédrale, canal de la Robine, halles et littoral à quelques minutes."),
       "avignon": ("avignon", "Palais des Papes, remparts et pont Saint-Bénézet, aux portes de la Provence."),
       "agde": ("agde", "La Perle noire de la Méditerranée : port, Grau d'Agde et Cap d'Agde.")}
def _vcard(c):
    ph, tx = _VT[c["key"]]
    return f'''<a class="glass city-card" href="{c["slug"]}.html"><div class="ph">{img(ph, "Photo d'illustration : " + c["name"])}</div><div class="city-card-body"><h3>Immobilier à {e(c["name"])}</h3><p>{e(tx)}</p><span class="text-link">Voir la page {e(c["name"])}</span></div></a>'''
VILLES = f'''<section class="section container" id="villes" aria-labelledby="t-villes">
      <div class="section-head" data-r>
        <div class="stack-3"><span class="label">Nos villes</span><h2 class="title" id="t-villes">Une agence <em class="gold-text">de Nîmes à Carcassonne.</em></h2></div>
      </div>
      <div class="city-cards" data-stagger>
        {"".join(_vcard(c) for c in C.CITIES)}
      </div>
    </section>'''
HEADER = C.header("", True)
FOOTER = C.footer("", True) + "\n" + C.chat_widget("")

PH = svg('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>')
ARROW = svg('<path d="M4 12h16M14 6l6 6-6 6"/>')
LEFT = svg('<path d="M20 12H4M10 6l-6 6 6 6"/>')
MENU = svg('<path d="M4 8h16M4 16h16"/>')
I_HOME = svg('<path d="M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6"/>')
I_KEY = svg('<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>')
I_BLD = svg('<path d="M5 21V4h9v17M14 9h5v12M8 8h3M8 12h3M8 16h3M3 21h18"/>')

faq_html = "".join(f'''
        <details data-cat="{e(c)}">
          <summary><span class="cat">{e(c)}</span><h3>{e(q)}</h3></summary>
          <div class="answer"><p>{e(a)}</p><a class="text-link" href="#contact">En parler à un conseiller</a></div>
        </details>''' for c, q, a in FAQ)
chips_html = '<button type="button" data-filter="all" aria-pressed="true">Tous les conseils</button>' + "".join(
    f'<button type="button" data-filter="{c}" aria-pressed="false">{c}</button>' for c in CATS)

def card(photo, alt, loc):
    badge = '<span class="badge loc">LOCATION</span>' if loc else '<span class="badge">VENTE</span>'
    price = "[LOYER] € par mois" if loc else "[PRIX] €"
    return f'''
          <article class="card" data-tilt>
            <div class="ph">{img(photo, alt)}{badge}</div>
            <div class="card-body">
              <span class="price">{price}</span>
              <h3 class="heading">[TYPE DE BIEN] · [VILLE]</h3>
              <span class="muted small">[SURFACE] m² · [PIÈCES] pièces</span>
            </div>
            <div class="card-actions"><a class="btn btn-navy btn-sm" href="#contact">Voir le bien</a><a class="text-link" href="#contact">Être rappelé</a></div>
          </article>'''

_ann = C.load_annonces()
_vente = [a for a in _ann if a["type"] == "vente"][:5]; _loc = [a for a in _ann if a["type"] == "location"][:3]
cards = "".join(C.annonce_card(a, "") for a in (_vente + _loc)) if _ann else (card("immeuble", "Photo d'illustration : immeuble moderne avec balcons", False)
         + card("salon2", "Photo d'illustration : séjour lumineux", True))

jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "LOTIER Immobilier", "inLanguage": "fr-FR", "publisher": {"@id": SITE + "/#agence"}},
                {**C.AGENCE_LD,
            "description": "Agence immobilière indépendante à Béziers, Montpellier et Nîmes : vente, location, gestion locative et syndic de copropriété, de Nîmes à Carcassonne en passant par Montpellier et Béziers.",
            "areaServed": [{"@type": "City", "name": c} for c in CITIES],
            "knowsAbout": ["Vente immobilière", "Location", "Gestion locative", "Syndic de copropriété", "Estimation immobilière"],
        },
        *C.office_nodes(),
        {"@type": "FAQPage", "@id": SITE + "/#faq", "inLanguage": "fr-FR",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for _, q, a in FAQ]},
    ],
}
jsonld_s = json.dumps(jsonld, ensure_ascii=False, indent=2)

TITLE = "Agence immobilière Béziers, Montpellier, Nîmes | LOTIER"
DESC = "Agence immobilière indépendante : vente, location, gestion locative et syndic de copropriété, de Nîmes à Carcassonne en passant par Montpellier et Béziers. Estimez votre bien et parlez à un conseiller."
LOGO = '<img src="assets/lotier-logo.png" alt="LOTIER Immobilier" width="165" height="56">'

TRUST = "".join(f"<li>{t}</li>" for t in ["Depuis 2018", "900+ lots gérés", "40+ copropriétés"])

page = f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(TITLE)}</title>
  <meta name="description" content="{e(DESC)}">
  <meta name="theme-color" content="#eef3f9">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{SITE}/">
  <link rel="alternate" type="text/markdown" href="{SITE}/index.md">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="LOTIER Immobilier">
  <meta property="og:title" content="{e(TITLE)}">
  <meta property="og:description" content="{e(DESC)}">
  <meta property="og:url" content="{SITE}/">
  <meta property="og:image" content="{SITE}/assets/og-lotier.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="assets/favicon.png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="apple-touch-icon" href="assets/favicon.png">
  <link rel="preload" href="assets/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="css/styles.css">
  <script type="application/ld+json">
{jsonld_s}
  </script>
</head>
<body id="top">
  <a class="skip-link" href="#contenu">Aller au contenu</a>

{HEADER}

  <main id="contenu">

    <section class="hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <span class="cloud" style="top:12%;width:120px" aria-hidden="true"></span>
      <span class="cloud" style="top:34%;width:90px;animation-duration:62s;animation-delay:-22s" aria-hidden="true"></span>
      <div class="container">
        <div class="hero-grid">
          <div class="hero-copy">
            <span class="label">Agence indépendante · Béziers · Montpellier · Nîmes · Carcassonne</span>
            <h1 class="display" data-split>Votre bien, <em class="gold-text">notre métier.</em></h1>
            <p class="lead">Vente, location et syndic de copropriété, de Nîmes à Carcassonne en passant par Montpellier et Béziers. Touchez ou survolez l'immeuble : chaque étage est un service de l'agence.</p>
            <div class="glass floor-panel" aria-live="polite">
              <h2 id="floor-t"></h2>
              <p id="floor-p"></p>
              <a class="text-link" id="floor-a" href="#estimer">Estimer mon bien</a>
            </div>
            <div class="acts">
              <a class="btn btn-gold btn-lg mag" href="#estimer">Estimer mon bien {ARROW}</a>
              <a class="btn btn-ghost btn-lg mag" href="#annonces">Voir nos annonces</a>
            </div>
            <p class="hero-call">Une question ? Appelez-nous <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
          </div>
          <div class="iso">
            <div id="iso-svg"></div>
            <div class="elev" role="group" aria-label="Choisir un étage">
              <button type="button" data-k="4" aria-pressed="false"><b>5</b>Estimation</button>
              <button type="button" data-k="3" aria-pressed="false"><b>4</b>Syndic</button>
              <button type="button" data-k="2" aria-pressed="true"><b>3</b>Vente</button>
              <button type="button" data-k="1" aria-pressed="false"><b>2</b>Location</button>
              <button type="button" data-k="0" aria-pressed="false"><b>1</b>Conseil</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="container">
      <form class="glass search" id="recherche" aria-label="Rechercher un bien" onsubmit="return false">
        <div class="search-tabs">
          <button type="button" data-mode="vente" aria-pressed="true">Acheter</button>
          <button type="button" data-mode="location" aria-pressed="false">Louer</button>
        </div>
        <div class="search-fields">
          <div class="field">
            <label for="ville">Ville</label>
            <select id="ville"><option>Toutes les villes</option>{"".join(f"<option>{c}</option>" for c in CITIES)}</select>
          </div>
          <div class="field">
            <label for="type">Type de bien</label>
            <select id="type"><option>Tous les biens</option><option>Appartement</option><option>Maison</option><option>Immeuble</option></select>
          </div>
          <div class="field">
            <label for="budget">Budget maximum</label>
            <input id="budget" type="text" placeholder="Ex. 250 000 €">
          </div>
          <button type="submit" class="btn btn-navy" id="search-submit">Rechercher</button>
        </div>
      </form>
    </div>

    <section class="section container" aria-label="Chiffres clés">
      <div class="stats" data-stagger>
        <div class="glass stat"><strong data-count="2018" data-from="1990">2018</strong><span>Création de l'agence par trois associés</span></div>
        <div class="glass stat"><strong data-count="40" data-suf="+">40+</strong><span>Copropriétés en syndic</span></div>
        <div class="glass stat"><strong data-count="900" data-suf="+">900+</strong><span>Lots gérés</span></div>
        <div class="glass stat"><strong data-count="10">10</strong><span>Collaborateurs, de la vente au syndic</span></div>
      </div>
    </section>

    <section class="section container" id="metiers" aria-labelledby="t-metiers">
      <div class="section-head" data-r>
        <div class="stack-3"><span class="label">Vente · Location · Syndic</span><h2 class="title" id="t-metiers">Un seul interlocuteur, <em class="gold-text">trois métiers.</em></h2></div>
        <a class="text-link" href="notre-service/">Notre façon de travailler</a>
      </div>
      <div class="trio" data-stagger>
        <article class="glass"><span class="ico">{I_HOME}</span><h3>Vente</h3><p>Estimation, mandat, visites, signature : un conseiller vous accompagne jusqu'à l'acte.</p><a class="text-link" href="vente/">Vendre mon bien</a></article>
        <article class="glass"><span class="ico">{I_KEY}</span><h3>Location</h3><p>Nous trouvons le locataire, rédigeons le bail et suivons votre bien. À partir de 39,99 € par mois.</p><a class="text-link" href="location/">Mettre en location</a></article>
        <article class="glass"><span class="ico">{I_BLD}</span><h3>Syndic</h3><p>Assemblées, charges, travaux : une gestion claire et transparente pour votre copropriété.</p><a class="text-link" href="syndic/">Confier mon immeuble</a></article>
      </div>
    </section>

    <section class="section container" id="annonces" aria-labelledby="t-annonces">
      <div data-carousel>
        <div class="section-head" data-r>
          <div class="stack-3"><span class="label">Nos annonces</span><h2 class="title" id="t-annonces">Les biens du moment</h2></div>
          <div class="carousel-btns">
            <button type="button" data-dir="-1" aria-label="Annonces précédentes">{LEFT}</button>
            <button type="button" data-dir="1" aria-label="Annonces suivantes">{ARROW}</button>
          </div>
        </div>
        <div class="track" tabindex="0" aria-label="Liste des annonces">{cards}
        </div>
      </div>
      <div class="section-cta"><a class="btn btn-navy btn-lg mag" href="nos-annonces/">Voir toutes les annonces {ARROW}</a></div>
    </section>

    <section class="estim" aria-labelledby="t-estim">
      <div class="container">
        <div data-r>
          <h2 id="t-estim">Combien vaut votre bien ?</h2>
          <p>Un conseiller compare votre bien aux ventes récentes de votre quartier et vous explique le prix du marché.</p>
          <p class="alt-call">Ou appelez-nous : <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
        </div>
        <form class="estim-card" id="estimer" data-r aria-labelledby="est-t" toolname="demander_estimation" tooldescription="Demander une estimation gratuite de son bien à LOTIER Immobilier : un conseiller rappelle pour affiner avec une visite.">
          <div class="ph">{img("cles", "Photo d'illustration : remise de clés d'un logement")}</div>
          <h3 id="est-t">Demandez votre estimation</h3>
          <div class="field"><label for="est-adresse">Adresse du bien</label><input id="est-adresse" name="adresse" toolparamdescription="Adresse du bien à estimer" type="text" autocomplete="street-address" placeholder="Ex. 12 rue Française, Béziers"></div>
          <div class="field"><label for="est-tel">Votre téléphone</label><input id="est-tel" name="telephone" toolparamdescription="Téléphone pour être rappelé" type="tel" autocomplete="tel" placeholder="06 00 00 00 00"></div>
          <button type="submit" class="btn btn-navy btn-lg btn-block">Demander mon estimation</button>
        </form>
      </div>
    </section>

    <section class="section container" id="conseils" aria-labelledby="t-conseils">
      <div class="section-head" data-r>
        <div class="stack-3">
          <span class="label">Conseils immo</span>
          <h2 class="title" id="t-conseils">Nos réponses à <em class="gold-text">vos questions.</em></h2>
          <p class="muted">Acheter, vendre, louer ou gérer une copropriété : des réponses courtes, écrites par les conseillers de l'agence.</p>
        </div>
      </div>
      <div class="chips" role="group" aria-label="Filtrer par profil">{chips_html}</div>
      <div class="faq" data-r>{faq_html}
      </div>
      <div class="glass faq-cta">
        <p>Votre situation est particulière ? Un conseiller vous répond.</p>
        <a class="btn btn-navy btn-lg mag" href="#contact">Poser ma question</a>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-agences">
      <div class="agencies">
        <div class="photo" data-r>{img("bez-pont", "Photo d'illustration : le Pont Vieux et la cathédrale Saint-Nazaire de Béziers")}<span class="glass">Béziers · siège de l'agence</span></div>
        <div data-r>
          <span class="label">Nos agences</span>
          <h2 class="title" id="t-agences" style="margin-top:14px">Une agence locale, de <em class="gold-text">Nîmes à Carcassonne.</em></h2>
          <p class="muted" style="margin-top:14px;max-width:46ch">Trois espaces géographiques, des équipes réactives en Languedoc.</p>
          <ul class="agency-list">
            <li><span class="city">Béziers</span><span class="small muted">40 rue Française, 1er étage, 34500</span></li>
            <li><span class="city">Montpellier</span><span class="small muted">469 rue Favre de Saint-Castor, 34080 · sur rendez-vous</span></li>
            <li><span class="city">Nîmes</span><span class="small muted">3 rue Bosquet, 30230 Rodilhan · sur rendez-vous</span></li>
          </ul>
          <div class="acts" style="margin-top:24px"><a class="btn btn-navy mag" href="#contact">Contacter l'agence</a></div>
        </div>
      </div>
    </section>

    {VILLES}

    <section class="section container" id="avis" aria-labelledby="t-avis">
      <div class="section-head" data-r>
        <div class="stack-3"><span class="label">Avis clients</span><h2 class="title" id="t-avis">Ils nous ont fait confiance</h2></div>
        <a class="text-link" href="#avis">Voir tous les avis</a>
      </div>
      <div class="cards" data-stagger>
        <figure class="glass quote"><blockquote>[AVIS CLIENT RÉEL À INSÉRER]</blockquote><figcaption class="small muted">[PRÉNOM] · [MÉTIER : VENTE, LOCATION OU SYNDIC] · [DATE]</figcaption></figure>
        <figure class="glass quote"><blockquote>[AVIS CLIENT RÉEL À INSÉRER]</blockquote><figcaption class="small muted">[PRÉNOM] · [MÉTIER : VENTE, LOCATION OU SYNDIC] · [DATE]</figcaption></figure>
        <figure class="glass quote"><blockquote>[AVIS CLIENT RÉEL À INSÉRER]</blockquote><figcaption class="small muted">[PRÉNOM] · [MÉTIER : VENTE, LOCATION OU SYNDIC] · [DATE]</figcaption></figure>
      </div>
    </section>

    {C.partners_strip("")}

    {C.recruit_banner('')}

    {NEWS}

    <section class="section container" id="agents" aria-label="Devenir agent">
      <div class="glass recruit" data-r>
        <div class="photo">{img("agent", "Photo d'illustration : un conseiller remet les clés à un couple")}</div>
        <div class="recruit-text">
          <span class="label">Devenir agent</span>
          <h2 class="title">Devenez agent immobilier indépendant</h2>
          <p class="muted">Une offre clé en main pour exercer à votre compte, avec les outils, la formation et le réseau d'une agence indépendante.</p>
          <a class="btn btn-navy btn-lg mag" href="rejoindre/">Découvrir l'offre {ARROW}</a>
        </div>
      </div>
    </section>

    <section class="contact" id="contact" aria-labelledby="t-contact">
      <div class="container">
        <div class="contact-intro" data-r>
          <h2 id="t-contact">Parlons de <em class="gold-text">votre projet.</em></h2>
          <p class="lead">Vente, location ou syndic : appelez-nous ou écrivez-nous, un conseiller vous répond.</p>
          <a class="big-phone gold-text" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
          <div class="acts">
            <a class="btn btn-gold btn-lg mag" href="mailto:contact@lotier-immobilier.com">Écrire à l'agence</a>
            <a class="btn btn-ghost btn-lg mag" href="#estimer">Estimer mon bien</a>
          </div>
        </div>
        <dl class="contact-details" data-stagger>
          <div class="glass"><dt>BÉZIERS · SIÈGE</dt><dd>LOTIER Immobilier<br>40 rue Française, 1er étage<br>34500 Béziers</dd></div>
          <div class="glass"><dt>MONTPELLIER · SUR RENDEZ-VOUS</dt><dd>LOTIER Immobilier<br>469 rue Favre de Saint-Castor<br>34080 Montpellier</dd></div>
          <div class="glass"><dt>NÎMES · SUR RENDEZ-VOUS</dt><dd>LOTIER Immobilier<br>3 rue Bosquet<br>30230 Rodilhan</dd></div>
          <div class="glass"><dt>CONTACT</dt><dd><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a></dd></div>
          <div class="glass"><dt>HORAIRES</dt><dd>[HORAIRES À CONFIRMER]<br>Fermé le samedi, le dimanche et les jours fériés</dd></div>
        </dl>
      </div>
    </section>

  </main>

{FOOTER}
  <script src="js/main.js"></script>
</body>
</html>
'''
head, sep, rest = page.partition('</script>')
rest = rest.replace(' ?', '&nbsp;?')
page = head + sep + rest
open(f'{ROOT}/index.html', 'w', encoding='utf-8').write(page)
print(len(page))
