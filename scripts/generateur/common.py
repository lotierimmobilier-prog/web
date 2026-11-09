# -*- coding: utf-8 -*-
import html, json, random, datetime, math, re, sys, os
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from content_articles import ARTICLES
from content_cities import CITIES
from content_faq import FAQ as ART_FAQ
from extra1 import EXTRA1
from extra2 import EXTRA2
from extra3 import EXTRA3
from extra4 import EXTRA4
EXTRA = {**EXTRA1, **EXTRA2, **EXTRA3, **EXTRA4}
for _a in ARTICLES:
    _ex = EXTRA.get(_a["slug"])
    if _ex:
        _a["sections"] = list(_a["sections"]) + _ex["sections"]
        ART_FAQ[_a["slug"]] = list(ART_FAQ.get(_a["slug"], [])) + _ex["faq"]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _empreinte(rel):
    """Empreinte courte du contenu d'un fichier statique : change à chaque modification du fichier. Elle est ajoutée à l'adresse
    de la feuille de style et du script (?v=…) : le serveur les garde un mois en cache, sans elle un navigateur qui a déjà visité
    le site continue d'afficher l'ancienne mise en page avec les nouvelles pages (bug constaté le 2026-11-09 sur les fiches)."""
    import hashlib
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]
V_CSS = _empreinte("css/styles.css")
V_JS = _empreinte("js/main.js")

SITE = "https://lotier.immo"
# Adresses des réseaux sociaux : renseigner les URLs complètes (les liens n'apparaissent que si elles sont remplies)
# Adresse du portail client MyLotier (laisser vide tant qu'elle n'est pas connue : le bouton renvoie alors vers le contact)
MYLOTIER_URL = ""
# Réseaux sociaux : renseigner l'URL complète de chaque compte. Sans URL, l'entrée reste visible mais inactive
# (SOCIAL_SHOW_EMPTY = False pour la masquer tant que le lien n'est pas connu).
SOCIAL = {"Facebook": "https://www.facebook.com/lotierimmobilier", "X": "", "LinkedIn": "", "YouTube": "", "Instagram": "https://www.instagram.com/lotierimmobilier"}
SOCIAL_SHOW_EMPTY = True
# Assistant de chat : adresse d'un service qui répond en JSON {"reply": "..."} à un POST {"message": "...", "history": [...]}.
# Vide = l'assistant répond depuis les informations du site (mode local, sans serveur).
# Auguste, l'assistant de Collab (chatbot public : /session ouvre une conversation, /message répond). Vide = réponses locales seulement.
CHAT_ENDPOINT = "https://collab.lotier-immobilier.com/api/public/chatbot"
COLLAB_RAPPEL = "https://collab.lotier-immobilier.com/api/public/v1/demandes-rappel"   # « Être rappelé » : crée une tâche chez l'agent de l'annonce
COLLAB_ESTIMER = "https://collab.lotier-immobilier.com/estimer"   # estimation en ligne publique de Collab (ECM) ; reçoit ?adresse=&telephone=&mode=
COLLAB_LOGIN = "https://collab.lotier-immobilier.com/login"   # page de connexion (e-mail + mot de passe) de Collab, pour l'équipe
# Bureaux affichés dans la fenêtre « Nos agences » (adresse vide = « à compléter », comme sur la section Contact)
OFFICES = [
    {"city": "Béziers", "tag": "Siège", "addr": "40 rue Française, 1er étage", "zip": "34500"},
    {"city": "Montpellier", "tag": "Sur rendez-vous", "addr": "469 rue Favre de Saint-Castor", "zip": "34080", "place": "Montpellier"},
    {"city": "Nîmes", "tag": "Sur rendez-vous", "addr": "3 rue Bosquet", "zip": "30230", "place": "Rodilhan"},
]
PHONE_DISPLAY = "04 67 11 28 31"
PHONE_TEL = "+33467112831"
e = html.escape

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
def fr_date(d): return f"{d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]} {d.year}"

PIN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.6"/></svg>'
BELL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z"/><path d="M10 21a2 2 0 0 0 4 0"/></svg>'
CLOSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>'

def svg(path): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{path}</svg>'
PH = svg('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>')
ARROW = svg('<path d="M4 12h16M14 6l6 6-6 6"/>')
LEFT = svg('<path d="M20 12H4M10 6l-6 6 6 6"/>')
MENU = svg('<path d="M4 8h16M4 16h16"/>')

def img(prefix, name, alt, cls="", lazy=True):
    path = f"{ROOT}/assets/photos/{name}.jpg"
    w, h = Image.open(path).size
    extra = ' loading="lazy" decoding="async"' if lazy else ""
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{prefix}assets/photos/{name}.jpg" alt="{e(alt)}" width="{w}" height="{h}"{extra}{c}>'


# Photos d'illustration : variété et textes alternatifs
ALT_PHOTO = {
 "immeuble": "Photo d'illustration : immeuble moderne avec balcons", "salon": "Photo d'illustration : salon lumineux avec canapé gris",
 "salon2": "Photo d'illustration : séjour moderne avec grande baie vitrée", "cuisine": "Photo d'illustration : cuisine blanche avec îlot en marbre",
 "cles": "Photo d'illustration : remise de clés d'un logement", "agent": "Photo d'illustration : un conseiller remet les clés à un couple",
 "villa": "Photo d'illustration : villa contemporaine avec piscine", "village": "Photo d'illustration : village de pierre aux toits de tuiles",
 "toits": "Photo d'illustration : toits de tuiles d'une vieille ville du Sud", "ruelle2": "Photo d'illustration : rue calme bordée de façades claires",
 "terrasse": "Photo d'illustration : terrasse avec piscine au crépuscule", "syndic": "Photo d'illustration : façade d'immeuble en noir et blanc",
 "gordes": "Photo d'illustration : village perché de Gordes",
}
PHOTO_BY_SLUG = {
 "diagnostics-immobiliers-obligatoires-vente": "immeuble", "home-staging-mieux-vendre": "salon", "mandat-exclusif-ou-simple": "agent",
 "fixer-le-bon-prix-estimation": "villa", "compromis-de-vente-points-de-vigilance": "cles", "frais-de-notaire-comprendre": "ruelle2",
 "premier-achat-erreurs-a-eviter": "village", "visiter-un-appartement-checklist": "immeuble", "meuble-ou-vide-choisir-location": "cuisine",
 "depot-de-garantie-location": "terrasse", "loyers-impayes-reflexes-proprietaire": "syndic", "dpe-classes-a-g-comprendre": "gordes",
 "dossier-de-location-solide": "salon2", "assemblee-generale-copropriete-preparer": "syndic", "charges-copropriete-appel-de-fonds": "immeuble",
 "travaux-en-copropriete-qui-decide": "toits",
}
for _a in ARTICLES:
    if _a["slug"] in PHOTO_BY_SLUG:
        _a["photo"] = PHOTO_BY_SLUG[_a["slug"]]
        _a["alt"] = ALT_PHOTO[_a["photo"]]

# ---------- Articles : dates aléatoires de publication ----------
random.seed(20261105)
_start, _end = datetime.date(2025, 11, 12), datetime.date(2026, 11, 2)
_days = random.sample(range((_end - _start).days + 1), len(ARTICLES))
for a, off in zip(ARTICLES, _days):
    a["date"] = _start + datetime.timedelta(days=off)

def _text_of(a):
    parts = [a["intro"]]
    for h, blocks in a["sections"]:
        parts.append(h)
        for b in blocks:
            parts.extend(b if isinstance(b, list) else [b])
    parts.extend(a["retenir"])
    for q, ans in ART_FAQ.get(a["slug"], []): parts.extend([q, ans])
    return " ".join(parts)
for a in ARTICLES:
    a["words"] = len(_text_of(a).split())
    a["min"] = max(3, math.ceil(a["words"] / 200))
ARTICLES_BY_DATE = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)
BY_SLUG = {a["slug"]: a for a in ARTICLES}
CITY_BY_KEY = {c["key"]: c for c in CITIES}

def art_url(prefix, a): return f"{prefix}blog/{a['slug']}.html"
def city_url(prefix, c): return f"{prefix}{c['slug']}.html"
def blog_index(prefix): return f"{prefix}blog/index.html"

# ---------- En-tête, pied de page, coque de page ----------
LOGO_FN = lambda prefix: f'<img src="{prefix}assets/lotier-logo.png" alt="LOTIER Immobilier" width="165" height="56">'

CONTACT_CONSENTEMENT = ("J’accepte que LOTIER Immobilier utilise ces informations pour me recontacter au sujet de ma demande. "
                        "Elles sont conservées 3 ans au plus et réservées à nos conseillers (voir ")

def contact_dialog(prefix):
    """Fenêtre unique de contact (« Être rappelé » sur une fiche, « Écrire à l'agence » partout) : le JavaScript l'adapte au bouton qui l'ouvre.
    Sans JavaScript, chaque bouton reste un lien ordinaire vers la page Contact."""
    return (f'''  <dialog class="rappel" id="contact-dlg" aria-labelledby="rappel-t" data-endpoint="{e(COLLAB_RAPPEL)}" data-phone="{PHONE_TEL}" data-phone-label="{PHONE_DISPLAY}">
    <form class="rappel-form" novalidate>
      <button type="button" class="rappel-x" data-rappel-close aria-label="Fermer">{CLOSE}</button>
      <h2 id="rappel-t" data-rappel-titre>Être rappelé</h2>
      <p class="muted" data-rappel-intro></p>
      <div class="rappel-grid">
        <label>Prénom<input name="prenom" autocomplete="given-name" required maxlength="60"></label>
        <label>Nom<input name="nom" autocomplete="family-name" required maxlength="80"></label>
        <label><span>Téléphone <span class="muted" data-opt-tel></span></span><input name="telephone" type="tel" inputmode="tel" autocomplete="tel" maxlength="30" placeholder="06 12 34 56 78"></label>
        <label><span>E-mail <span class="muted" data-opt-mail>(facultatif)</span></span><input name="email" type="email" autocomplete="email" maxlength="160"></label>
      </div>
      <label class="rappel-msg"><span>Message <span class="muted" data-opt-msg>(facultatif)</span></span><textarea name="message" rows="4" maxlength="1500"></textarea></label>
      <div class="rappel-piege" aria-hidden="true"><label>Ne pas remplir<input name="site" tabindex="-1" autocomplete="off"></label></div>
      <label class="rappel-ok"><input type="checkbox" name="consentement"><span>{CONTACT_CONSENTEMENT}<a class="text-link" href="{prefix}lotier-rgpd/">notre politique de protection des données</a>).</span></label>
      <p class="rappel-err" role="alert" hidden></p>
      <div class="rappel-act"><button type="submit" class="btn btn-gold btn-lg" data-rappel-envoi>Envoyer</button>
        <a class="btn btn-ghost btn-lg" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
    </form>
    <div class="rappel-fait" hidden><h2>Merci, votre demande est bien reçue.</h2><p data-rappel-merci></p>
      <button type="button" class="btn btn-navy btn-lg" data-rappel-close>Fermer</button></div>
  </dialog>
''')

def chat_widget(prefix):
    return f'''  <div class="chat" id="chat" data-prefix="{prefix}" data-endpoint="{CHAT_ENDPOINT}" data-phone="{PHONE_TEL}" data-phone-label="{PHONE_DISPLAY}">
    <button type="button" class="chat-fab" data-chat-open aria-haspopup="dialog" aria-controls="chat-panel" aria-expanded="false">
      <span class="chat-fab-ico"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg><i class="chat-dot" aria-hidden="true"></i></span>
      <span class="chat-fab-txt"><strong>Auguste</strong><small>Assistant LOTIER, 7j/7</small></span>
    </button>
    <section class="chat-panel" id="chat-panel" role="dialog" aria-label="Auguste, assistant LOTIER" hidden>
      <header class="chat-head">
        <span class="chat-ava" data-chat-avatar aria-hidden="true" hidden></span>
        <div><strong>Auguste</strong><span><i class="chat-dot" aria-hidden="true"></i>Assistant LOTIER, disponible 7j/7</span></div>
        <button type="button" class="chat-x" data-chat-close aria-label="Fermer le chat">{CLOSE}</button>
      </header>
      <div class="chat-log" id="chat-log" role="log" aria-live="polite"></div>
      <div class="chat-chips" id="chat-chips"></div>
      <form class="chat-form" id="chat-form" autocomplete="off">
        <label class="sr-only" for="chat-input">Votre message</label>
        <input id="chat-input" type="text" placeholder="Posez votre question" maxlength="400">
        <button type="submit" aria-label="Envoyer">{ARROW}</button>
      </form>
      <p class="chat-foot">Auguste est un assistant automatique ; vos messages sont transmis à LOTIER Immobilier pour vous répondre (<a href="{prefix}lotier-rgpd/">données personnelles</a>). Un conseil personnalisé : <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
    </section>
  </div>
'''

# Partenaires affichés dans le bandeau défilant (texte seul : remplacer par les logos officiels fournis par chaque partenaire)
# Partenaires affichés dans le bandeau défilant (logos dans assets/partners/, gris au repos, en couleur au survol)
PARTNERS = [
    ("ANGC, Association nationale des gestionnaires de copropriété", "angc", 224, 96),
    ("ESPI, Former à l'immobilier de demain", "espi", 484, 96),
    ("Banque Dupuy, de Parseval", "banque-dupuy-de-parseval", 296, 96),
    ("La Boîte Immo, webmarketing immobilier", "la-boite-immo", 619, 96),
    ("Assurances Chevalier", "assurances-chevalier", 121, 96),
    ("Bien'ici", "bienici", 457, 96),
    ("Le Figaro", "le-figaro", 701, 96),
    ("Zelok", "zelok", 405, 96),
    ("Leboncoin", "leboncoin", 547, 96),
    ("Mila", "mila", 170, 96),
    ("Allianz", "allianz", 386, 96),
    ("Urbanis", "urbanis", 406, 96),
    ("FMA, Fermetures Menuiseries Audoises", "fma", 227, 96),
]

def partners_strip(prefix=""):
    def one(hidden=False):
        alt = "" if hidden else None
        return "".join(
            f'<li class="pt"><img src="{prefix}assets/partners/{f}.png" alt="{"" if hidden else e(n)}" width="{w}" height="{h}" decoding="async"></li>'
            for n, f, w, h in PARTNERS)
    return f'''    <section class="partners" aria-labelledby="t-partners">
      <p class="partners-label" id="t-partners">Nos partenaires</p>
      <div class="marquee">
        <ul class="marquee-track">{one()}</ul>
        <ul class="marquee-track" aria-hidden="true">{one(True)}</ul>
      </div>
    </section>'''

def recruit_banner(prefix):
    return f'''    <section class="rband" aria-labelledby="t-rband">
      <div class="container">
        <div class="rband-box">
          <div class="rband-photo">
            <img src="{prefix}assets/photos/agent.jpg" alt="Photo d'illustration : un agent immobilier remet les clés à un couple" width="1100" height="733" loading="lazy">
            <span class="rband-sticker" aria-hidden="true"><b>75&nbsp;%</b><i>de vos commissions</i></span>
          </div>
          <div class="rband-copy">
            <p class="rband-kicker">Recrutement</p>
            <h2 id="t-rband">Votre patron actuel ne lit pas ce site. <em>Profitez-en.</em></h2>
            <p class="rband-sub">Devenez agent LOTIER et gardez 75&nbsp;% de vos commissions HT. Lui, il garde la machine à café.</p>
            <div class="rband-act">
              <a class="btn btn-white" href="{prefix}rejoindre/">Je change de vie {ARROW}</a>
              <a class="rband-link" href="{prefix}rejoindre/comparatif/">Comparer avant de sauter</a>
            </div>
          </div>
        </div>
      </div>
    </section>'''

def news_items(prefix):
    latest = sorted(ARTICLES, key=lambda x: x["date"], reverse=True)[:3]
    items = [("mylotier", f"{prefix}mylotier/", "Nouveau", "MyLotier, votre espace client", "")]
    items += [(a["slug"], f"{prefix}blog/{a['slug']}.html", a["cat"], a["title"], fr_date(a["date"])) for a in latest]
    return "".join(f'<li><a href="{u}" data-news-id="{i}"><span class="news-tag">{e(t)}</span><span class="news-title">{e(ti)}</span>' + (f'<span class="news-date">{d}</span>' if d else "") + "</a></li>" for i, u, t, ti, d in items)

def agences_dialog():
    cards = ""
    for o in OFFICES:
        place = o.get("place", o["city"])
        addr = f'{e(o["addr"])}, {o["zip"]} {e(place)}' if o["addr"] else f'[ADRESSE À COMPLÉTER], {o["zip"]} {e(place)}'
        tag = f'<span class="of-tag">{e(o["tag"])}</span>' if o["tag"] else ""
        route = ""
        if o["addr"]:
            q = (o["addr"] + " " + o["zip"] + " " + place).replace(" ", "+")
            route = f'<a class="of-link" href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener">Itinéraire</a>'
        cards += f'<li class="office"><div><strong>{e(o["city"])}</strong>{tag}</div><address>LOTIER Immobilier<br>{addr}</address><div class="of-acts"><a class="of-link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>{route}</div></li>'
    return f'''  <dialog class="agences" id="agences-dialog" aria-labelledby="agences-title">
    <div class="agences-box">
      <button type="button" class="dlg-close" data-close-agences aria-label="Fermer">{CLOSE}</button>
      <h2 id="agences-title">Nos agences</h2>
      <p class="muted">Trois espaces géographiques, des équipes réactives en Languedoc.</p>
      <ul class="offices">{cards}</ul>
    </div>
  </dialog>'''

# Boutons d'action adaptés à la page : (libellé, ancre de l'accueil, titre du bandeau du pied de page)
CTA_KINDS = {
    "vendre": ("Estimer mon bien", "#estimer", "Un projet de vente&nbsp;?"),
    "acheter": ("Recevoir des offres", "#contact", "Un projet d'achat&nbsp;?"),
    "bailleur": ("Confier mon bien", "#contact", "Un bien à louer&nbsp;?"),
    "locataire": ("Trouver un logement", "#contact", "Vous cherchez un logement&nbsp;?"),
    "syndic": ("Contacter le syndic", "#contact", "Une question sur votre copropriété&nbsp;?"),
    "agence": ("Contacter l'agence", "#contact", "Une question&nbsp;? Parlons-en."),
}

def cta_for(prefix, kind, city=None):
    """Bouton principal (en-tête, bas de page, barre mobile) selon le thème de la page."""
    if kind == "ville":
        return ("Contacter l'agence", f"{prefix}index.html#contact", f"Un projet à {city}&nbsp;?")
    label, frag, title = CTA_KINDS[kind]
    return (label, f"{prefix}index.html{frag}", title)

def header(prefix, home=False, cta=None):
    def a(frag): return frag if home else f"{prefix}index.html{frag}"
    cta_label, cta_href = cta[:2] if cta else ("Estimer mon bien", a("#estimer"))
    return f'''  <div class="topbar">
    <div class="container">
      <span class="tb-l"><span class="tb-txt">Agence indépendante en Occitanie</span><span class="tb-rate" role="img" aria-label="Note Google : 4,7 sur 5"><span class="stars" aria-hidden="true">★★★★★</span> <b>4,7/5</b> sur Google</span></span>
      <div class="tb-r">
        <a class="tb-tel" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a>
        <button type="button" class="tb-btn" data-open-agences aria-haspopup="dialog" aria-controls="agences-dialog">{PIN}Nos agences</button>
        <a class="tb-my" href="{prefix}mylotier/">Espace client MyLotier</a>
      </div>
    </div>
  </div>

  <header class="site-header">
    <div class="container">
      <a class="logo" href="{a("#top") if home else prefix + "index.html"}" aria-label="LOTIER Immobilier, accueil">{LOGO_FN(prefix)}</a>
      <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Ouvrir le menu">{MENU}</button>
      <nav class="site-nav" id="nav" aria-label="Navigation principale">
        <a href="{prefix}vente/">Vente</a>
        <a href="{prefix}location/">Location</a>
        <a href="{prefix}syndic/">Syndic</a>
        <a href="{prefix}nos-annonces/">Annonces</a>
        <a href="{a("#villes")}">Villes</a>
        <a href="{a("#conseils")}">Conseils</a>
        <a href="{blog_index(prefix)}">Blog</a>
        <a class="nav-my" href="{prefix}mylotier/">Espace client MyLotier</a>
        <div class="bell-wrap">
          <button type="button" class="bell" data-bell aria-haspopup="true" aria-expanded="false" aria-controls="news-panel" aria-label="Nouveautés"><span class="bell-ico">{BELL}</span><span class="bell-badge" data-bell-badge hidden></span><span class="bell-txt">Nouveautés</span></button>
          <div class="news-panel" id="news-panel" role="region" aria-label="Nouveautés" hidden>
            <p class="news-head">Nouveautés</p>
            <ul>{news_items(prefix)}</ul>
            <a class="news-all" href="{blog_index(prefix)}">Tous les articles du blog</a>
          </div>
        </div>
        <a class="btn btn-gold btn-header mag" href="{cta_href}">{cta_label} {ARROW}</a>
      </nav>
    </div>
  </header>
{agences_dialog()}
'''

def footer(prefix, home=False, cta=None):
    def a(frag): return frag if home else f"{prefix}index.html{frag}"
    cta_label, cta_href = cta[:2] if cta else ("Estimer mon bien", a("#estimer"))
    cities = "".join(f'<a href="{city_url(prefix, c)}">Immobilier à {c["name"]}</a>' for c in CITIES)
    ico = {"Facebook": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v7h4v-7h3l1-4h-4V8z"/>', "Instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/>'}
    SOC_ICONS = {
        "Facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="5" fill="#1877F2"/><path fill="#fff" d="M16.6 24v-8.8h2.9l.5-3.5h-3.4V9.5c0-1 .3-1.7 1.7-1.7H20V4.7c-.3 0-1.4-.2-2.6-.2-2.6 0-4.3 1.6-4.3 4.4v2.8h-3v3.5h3V24z"/></svg>',
        "X": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.2 2.5h3.3l-7.2 8.2 8.5 11.3h-6.7l-5.2-6.8-6 6.8H1.6l7.7-8.8L1.2 2.5H8l4.7 6.2zm-1.2 17.5h1.8L7 4.4H5.1z"/></svg>',
        "LinkedIn": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="4" fill="#0A66C2"/><path fill="#fff" d="M4.6 9.3h3v9.6h-3zM6.1 4.6a1.7 1.7 0 1 1 0 3.4 1.7 1.7 0 0 1 0-3.4M9.6 9.3h2.9v1.3c.4-.8 1.4-1.5 2.9-1.5 3 0 3.6 2 3.6 4.5v5.3h-3V14c0-1.1 0-2.5-1.5-2.5s-1.8 1.2-1.8 2.4v5h-3z"/></svg>',
        "YouTube": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect y="3.5" width="24" height="17" rx="5" fill="#FF0000"/><path fill="#fff" d="M9.8 8.6v6.8l5.9-3.4z"/></svg>',
        "Instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="ig-g" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#FEDA75"/><stop offset=".35" stop-color="#FA7E1E"/><stop offset=".6" stop-color="#D62976"/><stop offset=".85" stop-color="#962FBF"/><stop offset="1" stop-color="#4F5BD5"/></linearGradient></defs><rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="url(#ig-g)" stroke-width="2.2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="url(#ig-g)" stroke-width="2.2"/><circle cx="17.3" cy="6.7" r="1.3" fill="#D62976"/></svg>',
    }
    soc_items = ""
    for n, u in SOCIAL.items():
        if u:
            soc_items += f'<a class="soc-link" href="{u}" target="_blank" rel="noopener me">{SOC_ICONS[n]}<span>{n}</span></a>'
        elif SOCIAL_SHOW_EMPTY:
            soc_items += f'<span class="soc-link soc-off" title="Lien bientôt disponible">{SOC_ICONS[n]}<span>{n}</span></span>'
    soc_nav = f'<nav aria-label="Réseaux sociaux"><h2>Nous suivre</h2>{soc_items}</nav>' if soc_items else ""
    cta_title = cta[2] if cta and len(cta) > 2 else ("Prêt à nous rejoindre&nbsp;?" if cta else "Un projet immobilier&nbsp;?")
    home_href = a("#top") if home else prefix + "index.html"
    return f'''  <footer class="footer">
    <div class="container">
      <div class="glass footer-cta">
        <div><strong>{cta_title}</strong><span>Un conseiller vous répond sous 24&nbsp;h, sans engagement.</span></div>
        <div class="footer-cta-btns"><a class="btn btn-primary" href="{cta_href}">{cta_label}</a><a class="btn btn-ghost" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </div>
      <div class="footer-grid">
        <div class="f-brand">
          <a class="logo" href="{home_href}" aria-label="LOTIER Immobilier, accueil">{LOGO_FN(prefix)}</a>
          <p>Agence immobilière hybride : l'expertise locale d'une agence, la souplesse d'un réseau d'agents.</p>
          <address>40 rue Française, 1er étage<br>34500 Béziers<br><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></address>
        </div>
        <nav aria-label="Nos villes"><h2>Nos villes</h2>{cities}</nav>
        <nav aria-label="Notre site"><h2>Notre site</h2>
          <a href="{prefix}a-propos/">À propos</a>
          <a href="{prefix}notre-service/">Notre service</a>
          <a href="{prefix}plan-du-site.html">Plan du site</a>
          <a href="{prefix}mentions-legales/">Mentions légales</a>
          <a href="{prefix}lotier-rgpd/">Politique de protection des données</a>
          <a href="{prefix}cookies/">Cookies et traceurs</a>
          <a href="{prefix}nos-honoraires/">Nos honoraires</a>
          <a href="{prefix}accessibilite/">Déclaration d'accessibilité</a>
        </nav>
        <nav aria-label="Infos utiles"><h2>Infos utiles</h2>
          <a href="{prefix}contact/">Nous contacter</a>
          <a href="{prefix}nos-agents/">Nos agents</a>
          <button type="button" class="foot-link" data-open-agences aria-haspopup="dialog" aria-controls="agences-dialog">Trouver une agence</button>
          <a href="{a("#estimer")}">Estimer mon bien</a>
          <a href="{prefix}nos-annonces/">Nos annonces</a>
          <a href="{blog_index(prefix)}">Actualités et conseils</a>
          <a href="{a("#conseils")}">Questions fréquentes</a>
          <a href="{prefix}rejoindre/">Devenir agent</a>
          <a href="{prefix}rejoindre/comparatif/">Réseau, agence ou LOTIER&nbsp;?</a>
          <a href="{prefix}mylotier/">Espace client MyLotier</a>
        </nav>
        {soc_nav}
      </div>
      <div class="footer-bottom">
        <p class="footer-line">SARL LOTIER, SIRET 452 117 294 00044. Carte professionnelle CPI3401 2016 000 014 824. Garantie financière : SOCAF, n° 105 708 080.</p>
        <p class="footer-line">© 2026 LOTIER Immobilier. Photos d'illustration : <a href="https://www.pexels.com/">Pexels</a>.
        <a class="f-lock" href="{COLLAB_LOGIN}" target="_blank" rel="noopener noreferrer nofollow" title="Accès équipe LOTIER" aria-label="Accès équipe LOTIER : connexion à Collab avec e-mail et mot de passe (nouvel onglet)"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg></a>
        <a class="to-top" href="#top" aria-label="Retour en haut"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg></a></p>
      </div>
    </div>
  </footer>

  <div class="mbar">
    <a class="a1" href="tel:{PHONE_TEL}">{PH}Appeler</a>
    <a class="a2" href="{cta_href}">{cta_label}</a>
  </div>
'''

def shell(prefix, title, desc, path, body, jsonld, og_image, og_type="website", home=False, robots="index, follow, max-image-preview:large, max-snippet:-1", cta=None, banner=False, kind=None, city=None):
    if cta is None and not home:
        cta = cta_for(prefix, kind or "agence", city)
    canonical = f"{SITE}/{path}" if path else f"{SITE}/"
    md_alt = ""
    if "noindex" not in robots and not path.startswith(("mylotier", "404")):
        md_path = "index.md" if not path else (path + "index.md" if path.endswith("/") else (path[:-5] + ".md" if path.endswith(".html") else ""))
        if md_path:
            md_alt = f'  <link rel="alternate" type="text/markdown" href="{SITE}/{md_path}">\n'
    ld = "".join(f'  <script type="application/ld+json">\n{json.dumps(j, ensure_ascii=False, indent=2)}\n  </script>\n' for j in jsonld)
    page = f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#ffffff">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{canonical}">
{md_alt}  <meta property="og:type" content="{og_type}">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="LOTIER Immobilier">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="{prefix}assets/favicon.png">
  <link rel="manifest" href="{prefix}site.webmanifest">
  <link rel="apple-touch-icon" href="{prefix}assets/favicon.png">
  <link rel="preload" href="{prefix}assets/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{prefix}css/styles.css?v={V_CSS}">
{ld}</head>
<body id="top">
  <a class="skip-link" href="#contenu">Aller au contenu</a>

{header(prefix, home, cta)}
  <main id="contenu">
{body}
{recruit_banner(prefix) if banner else ''}
  </main>

{footer(prefix, home, cta)}
{chat_widget(prefix)}
{contact_dialog(prefix)}  <script src="{prefix}js/main.js?v={V_JS}"></script>
</body>
</html>
'''
    head, sep, rest = page.partition("</head>")
    rest = rest.replace(" ?", "&nbsp;?")
    return head + sep + rest

AGENCE_LD = {
    "@type": ["RealEstateAgent", "LocalBusiness"], "sameAs": [u for u in SOCIAL.values() if u], "@id": SITE + "/#agence", "name": "LOTIER Immobilier", "legalName": "SARL LOTIER",
    "alternateName": "LOTIER", "url": SITE + "/", "logo": SITE + "/assets/lotier-logo.png", "image": SITE + "/assets/og-lotier.jpg",
    "telephone": PHONE_TEL, "email": "contact@lotier-immobilier.com", "foundingDate": "2018", "slogan": "Votre bien, notre métier.",
    "vatID": "FR21452117294",
    "identifier": [{"@type": "PropertyValue", "propertyID": "SIRET", "value": "45211729400044"}, {"@type": "PropertyValue", "propertyID": "RCS", "value": "Béziers 452 117 294"}],
    "address": {"@type": "PostalAddress", "streetAddress": "40 rue Française, 1er étage", "postalCode": "34500", "addressLocality": "Béziers", "addressRegion": "Occitanie", "addressCountry": "FR"},
    "contactPoint": [{"@type": "ContactPoint", "contactType": "customer service", "telephone": PHONE_TEL, "email": "contact@lotier-immobilier.com", "availableLanguage": ["fr"], "areaServed": "FR"}],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services de LOTIER Immobilier", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Vente immobilière", "url": SITE + "/vente/"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Location et gestion locative", "url": SITE + "/location/"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Syndic de copropriété", "url": SITE + "/syndic/"}}]},
}


def office_nodes():
    """Une fiche par agence (Béziers, Montpellier, Nîmes), rattachée à l'agence principale."""
    out = []
    for o in OFFICES:
        slug = o["city"].lower().replace("î", "i").replace("é", "e")
        node = {"@type": "RealEstateAgent", "@id": f"{SITE}/#agence-{slug}", "name": f"LOTIER Immobilier {o['city']}",
                "parentOrganization": {"@id": SITE + "/#agence"}, "url": SITE + "/", "telephone": PHONE_TEL,
                "address": {"@type": "PostalAddress", "streetAddress": o["addr"], "postalCode": o["zip"], "addressLocality": o.get("place", o["city"]), "addressCountry": "FR"}}
        if o["tag"] != "Siège": node["description"] = f"Agence de {o['city']}, ouverte sur rendez-vous."
        out.append(node)
    return out

def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def card_article(prefix, a, cls="blog-card"):
    return f'''<article class="{cls}" data-cat="{e(a["cat"])}">
            <a class="ph" href="{art_url(prefix, a)}" tabindex="-1" aria-hidden="true">{img(prefix, a["photo"], a["alt"])}</a>
            <div class="blog-card-body">
              <div class="pm"><b>{e(a["cat"])}</b><time datetime="{a["date"].isoformat()}">{fr_date(a["date"])}</time><span>{a["min"]} min</span></div>
              <h3><a href="{art_url(prefix, a)}">{e(a["title"])}</a></h3>
              <p>{e(a["desc"])}</p>
            </div>
          </article>'''


# ---------- Annonces (importées par scripts/scrape_annonces.py) ----------
def load_annonces():
    p = f"{ROOT}/data/annonces.json"
    if not os.path.exists(p): return []
    return json.load(open(p, encoding="utf-8")).get("annonces", [])

def _nice_title(a):
    t = a["titre"].strip()
    letters = [c for c in t if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:  # titres en capitales : on adoucit
        t = t.lower().capitalize()
        for w in sorted({a["ville"], "Béziers", "Narbonne", "Nîmes", "Montpellier", "Carcassonne", "Capendu", "Limoux", "Agde"}, key=len, reverse=True):
            if w: t = re.sub(re.escape(w.lower()), w, t, flags=re.I)
        t = re.sub(r"\b(boulevard|rue|avenue|place|chemin|route|impasse|all\u00e9e|quai|cours)( (?:de la |de l'|du |des |de |d')?)([a-z\u00e0-\u00ff])", lambda m: m.group(1) + m.group(2) + m.group(3).upper(), t)
        t = re.sub(r"(\bde |\bdu |\bd')(gen\u00e8ve|libert\u00e9)", lambda m: m.group(1) + m.group(2).capitalize(), t)
        t = re.sub(r"\bt(\d)\b", lambda m: "T" + m.group(1), t)
    return t

def _price(a):
    if a.get("prix") is None or (a["type"] == "vente" and a["prix"] < 1000): return "Prix sur demande"  # prix de vente invraisemblable : on n'affiche pas
    n = f"{a['prix']:,.0f}".replace(",", "\u202f")
    return f"{n}\u00a0\u20ac" + ("\u00a0par mois" if a["type"] == "location" else "")

# ---- Filtres de « Nos annonces » : catégorie de bien et département ----
_DEPS = json.load(open(f"{ROOT}/data/departements.json", encoding="utf-8"))
DEPARTEMENTS = _DEPS["departements"]
def departement(a):
    """Code du département (« 34 ») de la commune de l'annonce, ou \"\" si la commune n'est pas dans data/departements.json."""
    return _DEPS["communes"].get(a.get("ville") or "", "")
_BIENS = (("appartement", "Appartement"), ("maison", "Maison"), ("terrain", "Terrain"), ("immeuble", "Immeuble"), ("commerce", "Local, bureaux, commerce"), ("parking", "Parking, box"), ("autre", "Autre"))
BIENS_LIBELLES = dict(_BIENS)
def categorie_bien(a):
    """Catégorie de bien (clé de _BIENS) : lue dans la fiche (« Type de bien »), à défaut déduite du titre."""
    brut = next((l[1] for b in a.get("blocs", []) for l in b["lignes"] if l[0] == "Type de bien"), "") or ""
    t = (brut + " " + (a.get("titre") or "")).lower()
    for cle, mots in (("parking", ("parking", "box", "garage")), ("terrain", ("terrain",)), ("immeuble", ("immeuble",)),
                      ("commerce", ("local", "boutique", "bureau", "commerc", "fonds")), ("maison", ("maison", "villa")), ("appartement", ("appartement", "studio", "t1", "t2", "t3", "t4", "t5"))):
        if any(m in t for m in mots): return cle
    return "autre"

def annonce_card(a, prefix):
    loc = a["type"] == "location"
    badge = '<span class="badge loc">LOCATION</span>' if loc else '<span class="badge">VENTE</span>'
    extra = " ".join(f'<span class="badge xtra">{e(b)}</span>' for b in a.get("badges", []) if b)
    title = _nice_title(a)
    bits = []
    if a.get("surface"): bits.append(f"{a['surface']:g}".replace(".", ",") + " m\u00b2")
    if a.get("chambres"): bits.append(f"{a['chambres']} ch.")
    photo = (f'<img src="{prefix}{a["photo"]}" alt="{e(title)}" width="720" height="540" loading="lazy" decoding="async">' if a.get("photo") else "")
    return f'''
          <article class="card" data-tilt data-ann-type="{a['type']}" data-ann-ville="{e(a['ville'])}" data-ann-dep="{departement(a)}" data-ann-bien="{categorie_bien(a)}" data-ann-prix="{int(a['prix']) if a.get('prix') else ''}" data-ann-surf="{int(a['surface']) if a.get('surface') else ''}">
            <div class="ph">{photo}{badge}</div>
            <div class="card-body">
              <span class="price">{_price(a)}</span>
              <h3 class="heading">{e(title)}</h3>
              <span class="muted small">{e(a['ville'])}{(' · ' + ' · '.join(bits)) if bits else ''}</span>
            </div>
            <div class="card-actions"><a class="btn btn-navy btn-sm" href="{(prefix + 'annonces/' + a['id'] + '/') if a.get('description_html') is not None else prefix + 'contact/'}">{"Voir l'annonce" if a.get('description_html') is not None else "Nous contacter"}</a><a class="text-link" href="{prefix}contact/">Être rappelé</a></div>
          </article>'''
