# -*- coding: utf-8 -*-
import os
from common import *
prefix = "../"

def hero(crumb, h1, lead):
    return f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{e(crumb)}</span></nav>
        <h1 class="display page-title">{h1}</h1>
        <p class="lead">{e(lead)}</p>
      </div>
    </section>'''

def section(label, title, inner, tid):
    return f'''    <section class="section container" aria-labelledby="{tid}">
      <div class="section-head"><div class="stack-3"><span class="label">{e(label)}</span><h2 class="title" id="{tid}">{title}</h2></div></div>
      {inner}
    </section>'''

def write(folder, title, desc, body, ld, crumb):
    os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
    open(f"{ROOT}/{folder}/index.html", "w", encoding="utf-8").write(
        shell(prefix, title, desc, f"{folder}/", body, ld + [breadcrumb_ld([("Accueil", SITE + "/"), (crumb, f"{SITE}/{folder}/")])], "assets/og-lotier.jpg", kind="agence"))

# ---------- À propos ----------
cities = ", ".join(c["name"] for c in CITIES)
legal = "".join(f'<li>{k}</li>' for k in [
    "SARL LOTIER, enseigne LOTIER Immobilier, au capital de 7 500 €",
    "Siège social : 40 rue Française, 1er étage, 34500 Béziers",
    "SIRET 452 117 294 00044, RCS Béziers 452 117 294",
    "Gérant : Nicolas Popovitch ; directeur de la publication : Jérôme Bouba",
    "Carte professionnelle CPI3401 2016 000 014 824, délivrée par la CCI de l'Hérault",
    "Garantie financière et assurance de responsabilité civile professionnelle : SO.CA.F."])
body = hero("À propos", 'LOTIER Immobilier, <em class="gold-text">une agence indépendante.</em>', "Vente, location, gestion locative et syndic de copropriété : qui nous sommes, comment nous travaillons et où nous trouver.")
body += section("Qui sommes-nous", "Une agence créée en 2018", f'''<div class="prose">
        <p>LOTIER Immobilier est une agence immobilière indépendante, créée en 2018 par trois associés. Son siège est à Béziers ; des bureaux sont ouverts à Montpellier et à Nîmes (sur rendez-vous), et un réseau d'agents accompagne les propriétaires, vendeurs, acquéreurs, bailleurs, locataires et copropriétaires autour de {e(cities)}.</p>
        <p>Nous réunissons l'expertise locale d'une agence et la souplesse d'un réseau d'agents : un interlocuteur identifié, des honoraires publiés et un accompagnement adapté à chaque projet.</p>
      </div>''', "t-qui")
body += section("Nos métiers", "Ce que nous faisons", f'''<div class="trio" data-stagger>
        <article class="glass"><h3>Vente</h3><p>De l'estimation à la signature de l'acte.</p><a class="text-link" href="{prefix}vente/">Découvrir la vente</a></article>
        <article class="glass"><h3>Location</h3><p>Mise en location et gestion locative.</p><a class="text-link" href="{prefix}location/">Découvrir la location</a></article>
        <article class="glass"><h3>Syndic</h3><p>La gestion claire de votre copropriété.</p><a class="text-link" href="{prefix}syndic/">Découvrir le syndic</a></article>
      </div>''', "t-metiers")
body += section("Notre approche", "Transparence et proximité", f'''<div class="prose">
        <p>Nos honoraires sont publiés en euros toutes taxes comprises : consultez le <a class="text-link" href="{prefix}nos-honoraires/">barème de nos honoraires</a>. Notre façon de travailler est détaillée sur la page <a class="text-link" href="{prefix}notre-service/">notre service</a>, et nos conseillers sont présentés sur la page <a class="text-link" href="{prefix}nos-agents/">nos agents</a>.</p>
        <p>Vous souhaitez rejoindre le réseau comme agent commercial indépendant ? Découvrez la page <a class="text-link" href="{prefix}rejoindre/">devenir agent</a>.</p>
      </div>''', "t-appr")
body += section("La société", "Informations légales", f'''<ul class="plain-list">{legal}</ul>
      <p class="muted small" style="margin-top:16px">Retrouvez le détail dans les <a class="text-link" href="{prefix}mentions-legales/">mentions légales</a>, la <a class="text-link" href="{prefix}lotier-rgpd/">politique de confidentialité</a> et la <a class="text-link" href="{prefix}cookies/">politique de cookies</a>.</p>''', "t-legal")
body += f'''    <section class="section container">
      <div class="glass cta-box">
        <div><h2>Une question ?</h2><p>Un conseiller vous répond par téléphone ou par e-mail.</p></div>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="{prefix}contact/">Nous contacter {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </div>
    </section>'''
ld = [{"@context": "https://schema.org", "@type": "AboutPage", "@id": f"{SITE}/a-propos/#page", "url": f"{SITE}/a-propos/", "name": "À propos de LOTIER Immobilier",
       "inLanguage": "fr-FR", "about": {"@id": SITE + "/#agence"}, "isPartOf": {"@id": SITE + "/#website"}}]
write("a-propos", "À propos de LOTIER Immobilier : agence indépendante depuis 2018", "LOTIER Immobilier, agence immobilière indépendante créée en 2018 à Béziers : vente, location, gestion locative et syndic. Société, métiers, informations légales.", body, ld, "À propos")

# ---------- Contact ----------
offices = ""
for o in OFFICES:
    place = o.get("place", o["city"])
    note = "Siège de l'agence" if o["tag"] == "Siège" else "Accueil sur rendez-vous"
    offices += f'''<article class="glass office-card"><h3>{e(o["city"])}</h3><p class="small muted">{note}</p>
          <address>LOTIER Immobilier<br>{e(o["addr"])}<br>{e(o["zip"])} {e(place)}</address>
          <p><a href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></p></article>
        '''
body = hero("Contact", 'Nous <em class="gold-text">contacter.</em>', "Par téléphone, par e-mail ou en agence : un conseiller vous répond.")
body += section("Nous joindre", "Téléphone et e-mail", f'''<div class="trio" data-stagger>
        <article class="glass"><h3>Téléphone</h3><p class="muted">Un conseiller vous répond.</p><a class="text-link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></article>
        <article class="glass"><h3>E-mail</h3><p class="muted">Pour toute question ou demande.</p><a class="text-link" href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a></article>
        <article class="glass"><h3>Devenir agent</h3><p class="muted">Candidature au réseau.</p><a class="text-link" href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a></article>
      </div>''', "t-joindre")
body += section("Nos agences", "Où nous trouver", f'<div class="trio" data-stagger>{offices}</div>', "t-agences")
body += section("Votre demande", "Choisir le bon interlocuteur", f'''<ul class="plain-list">
        <li><a class="text-link" href="{prefix}index.html#estimer">Estimer mon bien</a> : demande d'estimation gratuite.</li>
        <li><a class="text-link" href="{prefix}location/">Location et gestion locative</a> : confier ou louer un bien.</li>
        <li><a class="text-link" href="{prefix}syndic/">Syndic de copropriété</a> : une question sur votre immeuble.</li>
        <li><a class="text-link" href="{prefix}mylotier/">Espace client MyLotier</a> : accès à votre espace.</li>
        <li><a class="text-link" href="{prefix}nos-agents/">Nos agents</a> : trouver le conseiller de votre secteur.</li>{(chr(10) + '        <li><a class="text-link" href="' + prefix + 'equipe/">L’équipe</a> : direction, gestion locative, syndic et accueil.</li>') if EQUIPE else ""}
      </ul>
      <p class="muted small" style="margin-top:16px">Informations légales : <a class="text-link" href="{prefix}mentions-legales/">mentions légales</a>, <a class="text-link" href="{prefix}lotier-rgpd/">politique de confidentialité</a>, <a class="text-link" href="{prefix}nos-honoraires/">honoraires</a>.</p>''', "t-demande")
ld = [{"@context": "https://schema.org", "@type": "ContactPage", "@id": f"{SITE}/contact/#page", "url": f"{SITE}/contact/", "name": "Contacter LOTIER Immobilier",
       "inLanguage": "fr-FR", "about": {"@id": SITE + "/#agence"}, "isPartOf": {"@id": SITE + "/#website"}}]
write("contact", "Contacter LOTIER Immobilier : téléphone, e-mail et agences", "Contactez LOTIER Immobilier : téléphone, e-mail et adresses des agences de Béziers, Montpellier et Nîmes. Vente, location, gestion locative et syndic.", body, ld, "Contact")
print("à propos et contact générés")
