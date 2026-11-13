# -*- coding: utf-8 -*-
import os
from common import *
prefix = "../"
I_HOME2 = svg('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>')
I_KEY2 = svg('<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>')
I_BLD2 = svg('<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>')

def hero(crumb, h1, lead):
    return f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{e(crumb)}</span></nav>
        <h1 class="display page-title">{h1}</h1>
        <p class="lead">{e(lead)}</p>
      </div>
    </section>'''

def cards(items, compact=True):
    return '<div class="trio compact" data-stagger>' + "".join(f'<article class="glass"><h3>{e(t)}</h3><p>{e(p)}</p></article>' for t, p in items) + "</div>"

def steps(items):
    return '<ol class="stepper">' + "".join(f'<li><h3>{e(t)}</h3><p>{e(p)}</p></li>' for t, p in items) + "</ol>"

def section(label, title, inner, tid):
    return f'''    <section class="section container" aria-labelledby="{tid}">
      <div class="section-head"><div class="stack-3"><span class="label">{e(label)}</span><h2 class="title" id="{tid}">{title}</h2></div></div>
      {inner}
    </section>'''

def closing(title, text, kind_label, href):
    return f'''    <section class="section container">
      <div class="glass cta-box">
        <div><h2>{e(title)}</h2><p>{e(text)}</p></div>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="{href}">{e(kind_label)} {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </div>
    </section>'''

def write(folder, title, desc, body, kind, crumb=None, service=None):
    ld = [breadcrumb_ld([("Accueil", SITE + "/"), (crumb or title.split(" | ")[0], f"{SITE}/{folder}/")])]
    if service:
        ld.append({"@context": "https://schema.org", "@type": "Service", "@id": f"{SITE}/{folder}/#service", "name": service, "serviceType": service,
                   "provider": {"@id": SITE + "/#agence"}, "areaServed": [{"@type": "City", "name": n} for n in ("Béziers", "Montpellier", "Nîmes")],
                   "url": f"{SITE}/{folder}/", "inLanguage": "fr-FR"})
    os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
    open(f"{ROOT}/{folder}/index.html", "w", encoding="utf-8").write(
        shell(prefix, title, desc, f"{folder}/", body, ld, "assets/og-lotier.jpg", kind=kind, banner=False))

CONTACT = f"{prefix}index.html#contact"
ESTIM = f"{prefix}index.html#estimer"

# ---------- Notre service ----------
VALUES = [
    ("Le client d'abord", "Un interlocuteur identifié, qui connaît votre dossier et vous rappelle. Vous ne répétez pas votre histoire à chaque appel."),
    ("Transparence", "Nos honoraires sont publiés, en euros toutes taxes comprises, avant tout engagement. Pas de frais cachés, pas de surprise à la signature."),
    ("Professionnalisme", "Une agence immobilière titulaire de la carte professionnelle, avec garantie financière et assurance de responsabilité civile professionnelle."),
    ("Personnalisation", "Chaque projet est différent. Nous adaptons la méthode, le rythme et les outils à votre situation, que vous vendiez, louiez ou gériez une copropriété."),
    ("Un service moderne", "Estimation en ligne, suivi à distance, espace client MyLotier, signature électronique quand elle est possible : moins de papier, plus de temps."),
    ("Proche de vous", "Des agences et des conseillers à Béziers, Montpellier, Nîmes et Carcassonne, qui connaissent leur quartier, leurs prix et leurs copropriétés."),
]
HOW = [
    ("Vous nous contactez", "Par téléphone, par formulaire, par e-mail ou avec l'assistant LOTIER, quand vous le souhaitez."),
    ("Un conseiller vous répond", "Il comprend votre projet, vous explique la marche à suivre et le coût, avant tout engagement."),
    ("Nous agissons, vous restez informé", "Estimation, visites, dossier de location, assemblée de copropriété : vous savez où en est votre dossier."),
    ("Nous restons disponibles", "Après la vente, la location ou l'assemblée, votre conseiller reste votre interlocuteur."),
]
body = hero("Notre service", 'Un service client <em class="gold-text">avant tout.</em>', "Transparence, professionnalisme, personnalisation : voici comment LOTIER Immobilier travaille avec vous, du premier appel jusqu'à la clé.")
body += section("Nos engagements", "Ce que vous pouvez attendre de nous", cards(VALUES), "t-val")
body += section("Au quotidien", 'Comment cela se passe', steps(HOW), "t-how")
body += f'''    <section class="section container" aria-labelledby="t-ia">
      <div class="glass cta-box">
        <div><h2 id="t-ia">L'assistant LOTIER, un coup de pouce à toute heure</h2>
        <p>L'assistant en ligne répond à vos premières questions (nos services, nos honoraires, les pièces à fournir) et vous met en relation avec un conseiller. Il aide, il ne remplace pas votre interlocuteur : pour un conseil sur votre dossier, un conseiller prend le relais.</p></div>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="{CONTACT}">Contacter l'agence {ARROW}</a></div>
      </div>
    </section>'''
body += section("Nos métiers", "Vente, location, syndic", f'''<div class="trio" data-stagger>
        <article class="glass"><span class="ico">{I_HOME2}</span><h3>Vente</h3><p>De l'estimation à la signature de l'acte.</p><a class="text-link" href="{prefix}vente/">Découvrir la vente</a></article>
        <article class="glass"><span class="ico">{I_KEY2}</span><h3>Location</h3><p>Mise en location et gestion locative.</p><a class="text-link" href="{prefix}location/">Découvrir la location</a></article>
        <article class="glass"><span class="ico">{I_BLD2}</span><h3>Syndic</h3><p>La gestion claire de votre copropriété.</p><a class="text-link" href="{prefix}syndic/">Découvrir le syndic</a></article>
      </div>''', "t-met")
write("notre-service", "Notre service client : transparence et accompagnement | LOTIER", "Le service client LOTIER Immobilier : honoraires transparents, accompagnement personnalisé, assistant en ligne et proximité à Béziers, Montpellier, Nîmes et Carcassonne.", body, "agence", crumb="Notre service")

# ---------- Vente ----------
body = hero("Vente", 'Vendre votre bien, <em class="gold-text">sereinement.</em>', "Un conseiller vous accompagne de l'estimation à la signature de l'acte, avec un barème d'honoraires connu dès le premier échange.")
body += section("Les étapes", "Votre vente, pas à pas", steps([
    ("Estimation", "Nous estimons votre bien en nous appuyant sur les ventes récentes de votre quartier, et vous expliquons le raisonnement."),
    ("Mandat", "Nous convenons ensemble du prix, de la durée et de la façon de présenter votre bien. Les honoraires figurent au mandat."),
    ("Commercialisation et visites", "Diffusion de l'annonce, sélection des acquéreurs, organisation et compte rendu des visites."),
    ("Offre et compromis", "Nous vous aidons à analyser les offres, à vérifier le financement et à préparer le compromis."),
    ("Signature de l'acte", "Nous suivons le dossier avec le notaire jusqu'à la remise des clés."),
]), "t-etapes")
body += section("Transparence", "Nos honoraires, sans détour", f'''<p class="lead-sm">Nos honoraires de vente sont dégressifs, en euros toutes taxes comprises, à la charge du vendeur et inclus dans le prix affiché. Le barème complet est publié : <a class="text-link" href="{prefix}nos-honoraires/#vente">voir le barème de vente</a>.</p>''', "t-hon")
body += section("Votre projet", "Une vente sur mesure", cards([
    ("Un interlocuteur unique", "Le même conseiller du premier appel à la signature."),
    ("Un suivi régulier", "Compte rendu après les visites, point sur les offres, conseils pour ajuster le prix si nécessaire."),
    ("Des outils modernes", "Estimation en ligne, annonce diffusée sur les grands portails, échanges à distance quand vous le souhaitez."),
]), "t-sm")
body += closing("Un projet de vente ?", "Un conseiller vous répond sans engagement.", "Estimer mon bien", ESTIM)
write("vente", "Vendre son bien à Béziers, Montpellier, Nîmes | LOTIER", "Vendre votre bien avec LOTIER Immobilier : estimation, mandat, visites, offre et signature, avec des honoraires de vente publiés et un conseiller dédié.", body, "vendre", crumb="Vente", service="Vente immobilière")

# ---------- Location ----------
body = hero("Location", 'Louer et gérer, <em class="gold-text">l\'esprit tranquille.</em>', "Nous trouvons le locataire, rédigeons le bail et suivons votre bien. Vous savez ce que cela coûte avant de nous confier quoi que ce soit.")
body += section("Propriétaires bailleurs", "De la mise en location à la gestion", steps([
    ("Mise en location", "Visite du bien, annonce, sélection des dossiers et édition du bail."),
    ("État des lieux", "État des lieux d'entrée et de sortie, avec comparatif."),
    ("Gestion locative", "Quittances, encaissement des loyers, révision du loyer, suivi administratif et financier."),
    ("Travaux et contentieux", "Avec la formule complète : suivi des travaux et traitement des impayés."),
]), "t-bail")
body += section("Transparence", "Deux formules de gestion, des tarifs publiés", f'''<p class="lead-sm">Gestion complète à 7 % HT par mois (soit 8,40 % TTC), contentieux et travaux compris, ou gestion locative à 39,99 € TTC par mois. Une assurance loyers impayés est proposée en option. <a class="text-link" href="{prefix}nos-honoraires/#gestion">Voir tous les tarifs de gestion</a>.</p>''', "t-hon")
body += section("Locataires", "Vous cherchez un logement ?", cards([
    ("Un dossier clair", "Nous vous indiquons les pièces à fournir dès la première visite."),
    ("Des honoraires encadrés", "Les honoraires de mise en location et d'état des lieux sont plafonnés par la loi, publiés sur notre page tarifs."),
    ("Un interlocuteur", "Une question sur votre bail ou votre logement : vous savez qui appeler."),
]), "t-loc")
body += closing("Un bien à louer ou à gérer ?", "Parlons de votre projet, sans engagement.", "Confier mon bien", CONTACT)
write("location", "Gestion locative à Béziers, Montpellier, Nîmes | LOTIER", "Location et gestion locative avec LOTIER Immobilier : mise en location, état des lieux, gestion à partir de 39,99 € TTC par mois, tarifs publiés.", body, "bailleur", crumb="Location et gestion locative", service="Location et gestion locative")

# ---------- Syndic ----------
body = hero("Syndic", 'Votre copropriété, <em class="gold-text">en toute clarté.</em>', "Assemblées, charges, travaux : une gestion transparente et un interlocuteur qui répond, pour les copropriétaires comme pour le conseil syndical.")
body += section("Notre mission", "Ce que fait votre syndic", cards([
    ("Assemblées générales", "Convocations, ordre du jour, procès-verbal : nous préparons et suivons chaque assemblée."),
    ("Budget et charges", "Budget prévisionnel, appels de fonds, comptes présentés clairement."),
    ("Travaux et sinistres", "Mise en concurrence, suivi des chantiers, déclaration et suivi des sinistres."),
]), "t-mis")
body += section("Au quotidien", "Un suivi que vous pouvez consulter", f'''<p class="lead-sm">Les copropriétaires retrouvent leurs documents dans l'espace client : <a class="text-link" href="{prefix}mylotier/">accéder à MyLotier</a>. Pour toute question, un gestionnaire identifié vous répond.</p>''', "t-suivi")
body += section("Transparence", "Des honoraires connus d'avance", f'''<p class="lead-sm">Nos honoraires de syndic sont annuels, toutes taxes comprises (TVA à 20 %), dégressifs selon le nombre de lots et répartis selon les millièmes. <a class="text-link" href="{prefix}nos-honoraires/#syndic">Voir le barème de syndic</a>.</p>''', "t-hon")
body += closing("Une question sur votre copropriété ?", "L'équipe syndic de LOTIER Immobilier vous répond.", "Contacter le syndic", CONTACT)
write("syndic", "Syndic de copropriété à Béziers, Montpellier, Nîmes | LOTIER", "Syndic de copropriété LOTIER Immobilier : assemblées, charges, travaux, espace client MyLotier et honoraires annuels publiés.", body, "syndic", crumb="Syndic de copropriété", service="Syndic de copropriété")
print("services générés")
