# -*- coding: utf-8 -*-
# Page de recrutement /rejoindre/ : contenu repris de https://rejoindre.lotier-immobilier.com/ et adapté au nouveau graphisme.
import os
from common import *

prefix = "../"
folder = "rejoindre"
url = f"{SITE}/{folder}/"
MAIL = "recrutement@lotier-immobilier.com"
CTA = ("Postuler maintenant", "#postuler")

FAQ_REJ = [
    ("Quelle commission touche un agent LOTIER ?", "La commission standard est de 75 % HT sur chaque facturation signée (vente, mise en location, état des lieux, avis de valeur, accompagnement…). Il n'y a ni redevance de marque ni quota imposé."),
    ("Combien coûte l'entrée dans le réseau ?", "Le coût d'entrée est de 160 € : 60 € pour la carte professionnelle (renouvelable tous les trois ans) et 100 € pour le kit de démarrage (panneaux, 100 cartes de visite, 100 flyers et une semaine de formation)."),
    ("Quel est l'abonnement mensuel ?", "L'abonnement est de 149 € TTC par mois, formation continue ALUR comprise, sans frais cachés."),
    ("Faut-il déjà avoir une carte professionnelle ?", "Non. LOTIER vous accompagne dans la constitution du dossier de carte professionnelle, qui est valable trois ans."),
    ("Peut-on vendre partout en France ?", "Oui. Les agents commerciaux n'ont aucune restriction géographique pour leur activité de vente, sur toute la France."),
    ("Comment fonctionne le parrainage ?", "Vous touchez 5 %, 3 %, 2 % et 1 % du chiffre d'affaires HT de vos filleuls, sur quatre niveaux."),
    ("Comment se déroule l'intégration ?", "En quatre étapes : candidature, dossier de carte professionnelle, kit et semaine de formation, puis premières ventes accompagnées avec un mentor dédié."),
]

def stat(counter, label):
    return f'<div class="glass stat">{counter}<span>{label}</span></div>'

stats = "".join([
    stat('<strong><span data-count="75">75</span><small>%</small></strong>', "de commission HT, sans redevance de marque"),
    stat('<strong>5·3·2·1<small>%</small></strong>', "de parrainage sur quatre niveaux"),
    stat('<strong><span data-count="149">149</span><small>€</small></strong>', "par mois TTC, tout inclus"),
    stat('<strong><span data-count="160">160</span><small>€</small></strong>', "pour démarrer : carte pro et kit"),
])

versus = '''<table class="legal-table versus">
          <thead><tr><th scope="col"></th><th scope="col">Agence classique</th><th scope="col">LOTIER</th></tr></thead>
          <tbody>
            <tr><th scope="row">Redevance de marque</th><td>3 à 8 % du chiffre d'affaires</td><td class="win">Aucune</td></tr>
            <tr><th scope="row">Quotas</th><td>Souvent imposés</td><td class="win">Aucun</td></tr>
            <tr><th scope="row">Commission</th><td>50 à 60 % en moyenne</td><td class="win">75 %</td></tr>
            <tr><th scope="row">Organisation</th><td>Liberté limitée</td><td class="win">Liberté totale</td></tr>
          </tbody>
        </table>'''

poles = "".join(f'<article class="glass"><span class="ico">{ic}</span><h3>{e(t)}</h3><p>{e(p)}</p></article>' for ic, t, p in [
    (svg('<path d="M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6"/>'), "Vente", "De l'estimation à la signature : vous accompagnez vos clients à chaque étape de leur projet."),
    (svg('<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>'), "Location et gestion locative", "Une équipe dédiée à Béziers prend en charge la gestion des biens confiés à l'agence."),
    (svg('<path d="M5 21V4h9v17M14 9h5v12M8 8h3M8 12h3M8 16h3M3 21h18"/>'), "Syndic de copropriété", "Plus de 40 copropriétés et 900 lots gérés par l'équipe syndic."),
])
cities = ["Béziers (siège)", "Montpellier", "Nîmes", "Alès", "Avignon", "Narbonne", "Carcassonne", "Brest", "Bordeaux", "Toulouse (bientôt)"]
city_chips = "".join(f'<span class="chip-link">{e(c)}</span>' for c in cities)

pay = f'''<div class="pay-grid" data-stagger>
        <article class="glass pay pay-main"><span class="label">Commission standard</span><div class="pay-num gold-text">75 %</div><h3>de commission HT</h3><p>Sur chaque facturation signée : vente, mise en location, état des lieux, avis de valeur, accompagnement… Sans redevance de marque, sans quota.</p></article>
        <article class="glass pay"><span class="label">Parrainage multi-niveaux</span>
          <div class="levels" role="img" aria-label="Parrainage : 5 % au premier niveau, 3 % au deuxième, 2 % au troisième, 1 % au quatrième"><div><b>5 %</b><small>niveau 1</small></div><div><b>3 %</b><small>niveau 2</small></div><div><b>2 %</b><small>niveau 3</small></div><div><b>1 %</b><small>niveau 4</small></div></div>
          <p>Vous touchez un pourcentage du chiffre d'affaires HT de vos filleuls, sur quatre niveaux.</p></article>
        <article class="glass pay"><span class="label">Coût d'entrée</span><div class="pay-num">160 €</div>
          <ul class="tick"><li><b>60 €</b> : carte professionnelle, renouvelable tous les trois ans ;</li><li><b>100 €</b> : kit de démarrage (panneaux, 100 cartes de visite, 100 flyers) et une semaine de formation.</li></ul></article>
        <article class="glass pay"><span class="label">Abonnement</span><div class="pay-num">149 € <small>TTC / mois</small></div><p>Formation continue ALUR comprise, sans frais cachés.</p></article>
      </div>'''

sim = '''<div class="glass sim" id="simulateur-box">
        <div class="sim-head">
          <div><label for="sim-range" class="label">Honoraires HT d'une vente</label><div class="sim-value" id="sim-honoraires" aria-live="polite">10 000 €</div></div>
          <button type="button" class="btn btn-ghost btn-sm" id="sim-replay">Relancer le calcul</button>
        </div>
        <input type="range" id="sim-range" min="2000" max="30000" step="500" value="10000" aria-describedby="sim-note">
        <div class="sim-scale"><span>2 000 €</span><span>30 000 €</span></div>
        <div class="bars">
          <div class="bar-row"><span>Agence A · 55 %</span><div class="track-bar"><i class="bar" id="bar-a"></i></div><b id="sim-a">5 500 €</b></div>
          <div class="bar-row"><span>Agence B · 65 %</span><div class="track-bar"><i class="bar" id="bar-b"></i></div><b id="sim-b">6 500 €</b></div>
          <div class="bar-row lotier"><span>LOTIER · 75 %</span><div class="track-bar"><i class="bar" id="bar-l"></i></div><b id="sim-l">7 500 €</b></div>
        </div>
        <p class="sim-gap">Écart avec la meilleure des deux autres agences : <b id="sim-gap">+ 1 000 €</b></p>
        <p class="small muted" id="sim-note">Simulation indicative, hors revenus de parrainage. Les taux des agences A et B sont donnés à titre d'exemple.</p>
      </div>'''

steps = "".join(f'<li class="glass step"><span class="step-n" aria-hidden="true">{i}</span><h3>{e(t)}</h3><p>{e(p)}</p></li>' for i, (t, p) in enumerate([
    ("Candidature", "Vous présentez votre parcours et vos motivations, par téléphone ou avec le formulaire de candidature."),
    ("Carte professionnelle", "Nous montons le dossier avec vous. La carte est valable trois ans."),
    ("Kit et formation", "Vous recevez votre kit de démarrage et suivez une semaine de formation avec un formateur dédié."),
    ("Premières ventes accompagnées", "Vous démarrez avec l'équipe à vos côtés, à chaque étape."),
], 1))

partners = "".join(f'<span class="chip-link">{e(p)}</span>' for p in ["ANGC", "ESPI", "Banque Dupuy, de Parseval", "La Boîte Immo", "Assurances Chevalier", "Bien'ici", "Le Figaro", "Zelok", "Leboncoin", "Mila", "Allianz", "Urbanis", "FMA"])
faq_html = "".join(f'<details><summary><span class="cat">Question</span><h3>{e(q)}</h3></summary><div class="answer"><p>{e(a)}</p></div></details>' for q, a in FAQ_REJ)

body = f'''    <section class="hero hero-tight">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <span class="cloud" style="top:12%;width:120px" aria-hidden="true"></span>
      <span class="cloud" style="top:34%;width:90px;animation-duration:62s;animation-delay:-22s" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane" style="padding-top:20px"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">Devenir agent</span></nav>
        <div class="hero-grid" style="padding-top:clamp(12px,2vw,28px)">
          <div class="hero-copy">
            <span class="label">Agence immobilière indépendante · Recrutement</span>
            <h1 class="display" data-split>Gagnez <em class="gold-text">75 %.</em> Ne perdez pas de temps&nbsp;!</h1>
            <p class="lead">LOTIER vous laisse l'essentiel de ce que vous gagnez : aucune redevance de marque, aucun quota imposé. Touchez ou survolez l'immeuble pour découvrir votre parcours.</p>
            <div class="glass floor-panel" aria-live="polite">
              <h2 id="floor-t"></h2>
              <p id="floor-p"></p>
              <a class="text-link" id="floor-a" href="#postuler">Postuler</a>
            </div>
            <div class="acts">
              <a class="btn btn-gold btn-lg mag" href="#postuler">Devenir agent LOTIER {ARROW}</a>
              <a class="btn btn-ghost btn-lg mag" href="#conditions">Voir les conditions</a>
            </div>
            <p class="hero-call">Une question ? Appelez-nous <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
          </div>
          <div class="iso">
            <div id="iso-svg" data-floors="parcours"></div>
            <div class="elev" role="group" aria-label="Choisir une étape">
              <button type="button" data-k="4" aria-pressed="false"><b>5</b>Indépendance</button>
              <button type="button" data-k="3" aria-pressed="false"><b>4</b>Premières ventes</button>
              <button type="button" data-k="2" aria-pressed="true"><b>3</b>Kit et formation</button>
              <button type="button" data-k="1" aria-pressed="false"><b>2</b>Carte pro</button>
              <button type="button" data-k="0" aria-pressed="false"><b>1</b>Candidature</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section container" aria-label="Chiffres clés">
      <div class="stats stats-join" data-stagger>{stats}</div>
    </section>

    <section class="section container" id="histoire" aria-labelledby="t-histoire">
      <div class="agencies">
        <div data-r>
          <span class="label">D'où l'on vient</span>
          <h2 class="title" id="t-histoire" style="margin-top:14px">Une agence indépendante, <em class="gold-text">à taille humaine.</em></h2>
          <p class="muted" style="margin-top:16px;max-width:52ch">LOTIER a été fondée par Jérôme Bouba et Nicolas Popovitch, deux amis issus du sport de haut niveau. L'agence s'est développée par pôles (vente, location et gestion locative, syndic) et par villes, de Béziers à Avignon.</p>
          <p class="muted" style="margin-top:12px;max-width:52ch">Beaucoup de professionnels, en activité ou en reconversion, veulent reprendre le contrôle de leur carrière sans renoncer à une structure et à un accompagnement. C'est exactement ce que propose LOTIER : l'indépendance professionnelle et financière, avec une équipe derrière vous.</p>
        </div>
        <div data-r><div class="table-wrap">{versus}</div><p style="margin-top:16px"><a class="text-link" href="comparatif/">Comparatif complet et FAQ : réseaux, agence classique et LOTIER</a></p></div>
      </div>
    </section>

    <section class="section container" id="lotier" aria-labelledby="t-lotier">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Qui est LOTIER</span><h2 class="title" id="t-lotier">Trois pôles, <em class="gold-text">trois cartes professionnelles.</em></h2><p class="muted">Nous détenons les cartes professionnelles T (transaction), G (gestion) et S (syndic). Vous vous appuyez sur une agence complète.</p></div></div>
      <div class="trio" data-stagger>{poles}</div>
      <div class="glass near" style="margin-top:20px" data-r>
        <div><span class="label">Nos implantations</span><div class="chip-links">{city_chips}</div></div>
        <div><span class="label">Sans frontière</span><p class="muted" style="margin-top:12px">Les agents commerciaux n'ont aucune restriction géographique pour leur activité de vente : vous pouvez travailler sur toute la France.</p></div>
      </div>
    </section>

    <section class="section container" id="conditions" aria-labelledby="t-pay">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Rémunération</span><h2 class="title" id="t-pay">Ce que vous gagnez, <em class="gold-text">ce que cela coûte.</em></h2></div></div>
      {pay}
    </section>

    <section class="section container" id="simulateur" aria-labelledby="t-sim">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Simulateur</span><h2 class="title" id="t-sim">Combien gagnez-vous <em class="gold-text">sur une vente ?</em></h2><p class="muted">Déplacez le curseur : comparez votre commission chez LOTIER et dans deux agences aux taux plus bas.</p></div></div>
      <div data-r>{sim}</div>
    </section>

    <section class="section container" id="parcours" aria-labelledby="t-parcours">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Parcours d'intégration</span><h2 class="title" id="t-parcours">De la candidature <em class="gold-text">aux premières ventes.</em></h2></div></div>
      <ol class="steps" data-stagger>{steps}</ol>
      <div class="cards" style="margin-top:20px" data-stagger>
        <article class="glass quote"><h3 class="heading">Un rendez-vous communautaire chaque mois</h3><p class="muted">Un intervenant expert partage son savoir-faire avec tous les agents du réseau.</p></article>
        <article class="glass quote"><h3 class="heading">Un mentor dédié dès votre arrivée</h3><p class="muted">Vous n'êtes jamais seul face à votre premier dossier.</p></article>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-faq-rej">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Questions fréquentes</span><h2 class="title" id="t-faq-rej">Avant de vous lancer</h2></div></div>
      <div class="faq" data-r>{faq_html}</div>
    </section>

    <section class="contact" id="postuler" aria-labelledby="t-post">
      <div class="container">
        <div class="apply-grid">
          <div class="contact-intro" data-r>
            <h2 id="t-post">Signez votre <em class="gold-text">indépendance.</em></h2>
            <p class="lead">Parlez-nous de votre parcours : un membre de l'équipe vous rappelle pour présenter l'agence et répondre à vos questions.</p>
            <div class="acts">
              <a class="btn btn-gold btn-lg mag" href="mailto:{MAIL}?subject=Candidature%20agent%20commercial%20ind%C3%A9pendant">Postuler par e-mail</a>
              <a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a>
            </div>
            <p class="small muted">{MAIL}<br>40 rue Française, 1er étage, 34500 Béziers</p>
            <div><span class="label">Nos partenaires</span><div class="chip-links">{partners}</div></div>
            <p class="small muted">Un groupe Facebook consacré à l'immobilier réunit plus de 10 000 membres.</p>
          </div>
          <form class="glass apply-form" id="postuler-form" data-r aria-labelledby="ap-t">
            <h3 id="ap-t">Formulaire de candidature</h3>
            <div class="field"><label for="ap-nom">Nom et prénom</label><input id="ap-nom" type="text" autocomplete="name" required></div>
            <div class="field"><label for="ap-tel">Téléphone</label><input id="ap-tel" type="tel" autocomplete="tel" required placeholder="06 00 00 00 00"></div>
            <div class="field"><label for="ap-mail">E-mail</label><input id="ap-mail" type="email" autocomplete="email" required></div>
            <div class="field"><label for="ap-ville">Ville</label><input id="ap-ville" type="text" autocomplete="address-level2" placeholder="Ex. Béziers"></div>
            <div class="field"><label for="ap-situation">Votre situation</label><select id="ap-situation"><option>Agent immobilier en activité</option><option>En reconversion</option><option>Débutant dans l'immobilier</option><option>Autre</option></select></div>
            <div class="field"><label for="ap-msg">Votre message</label><textarea id="ap-msg" rows="4" placeholder="Parlez-nous de votre parcours et de vos motivations"></textarea></div>
            <button type="submit" class="btn btn-navy btn-lg btn-block">Envoyer ma candidature</button>
            <p class="small muted">Le bouton prépare un e-mail adressé à l'équipe recrutement.</p>
          </form>
        </div>
      </div>
    </section>'''

ld = [
    {"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url, "name": "Devenir agent immobilier indépendant chez LOTIER", "inLanguage": "fr-FR",
     "description": "Rejoignez LOTIER Immobilier comme agent commercial indépendant : 75 % de commission HT, aucune redevance de marque, aucun quota, formation et mentor dédié.",
     "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#agence"}},
    {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_REJ]},
    breadcrumb_ld([("Accueil", SITE + "/"), ("Devenir agent", url)]),
]
os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
page = shell(prefix, "Agent immobilier indépendant : 75 % de commission | LOTIER",
             "Rejoignez LOTIER Immobilier comme agent commercial indépendant : 75 % de commission HT, aucune redevance de marque, aucun quota, formation ALUR et mentor dédié.",
             f"{folder}/", body, ld, "assets/photos/agent.jpg", cta=CTA)
page = page.replace("<title>", "<title>", 1)
open(f"{ROOT}/{folder}/index.html", "w", encoding="utf-8").write(page)
print("page de recrutement générée")
