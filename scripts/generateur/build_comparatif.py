# -*- coding: utf-8 -*-
# Page /rejoindre/comparatif/ : réseaux de mandataires, agence classique et modèle hybride LOTIER + FAQ.
# Les chiffres de LOTIER et ceux de l'« agence classique » (3 à 8 %, 50 à 60 %) viennent de rejoindre.lotier-immobilier.com.
# Les réseaux sont décrits de façon générale et sans marque : leurs offres varient.
import os
from common import *

prefix = "../../"
folder = "rejoindre/comparatif"
url = f"{SITE}/{folder}/"
CTA = ("Postuler maintenant", "../#postuler")

FAQ_COMP = [
    ("Quelle est la différence entre un réseau de mandataires et une agence classique ?",
     "Dans un réseau de mandataires, l'agent travaille le plus souvent à domicile, en indépendant, avec une commission élevée et un abonnement ou des frais mensuels, sans agence physique. Dans une agence classique, l'agent s'appuie sur des locaux, une équipe et une marque, mais sa part de commission est en général plus faible, et il peut être soumis à des quotas ou à une redevance de marque."),
    ("Qu'est-ce que le modèle hybride de LOTIER ?",
     "LOTIER associe l'indépendance d'un agent commercial à l'appui d'une vraie agence. Vous gardez 75 % de commission HT, sans redevance de marque ni quota, et vous vous appuyez sur des agences, des cartes professionnelles de transaction, de gestion et de syndic, une équipe de gestion locative et un mentor dédié."),
    ("Combien gagne un agent LOTIER par rapport à un réseau ?",
     "LOTIER verse 75 % HT de commission sur chaque facturation signée, avec un abonnement de 149 € TTC par mois. Les réseaux affichent des taux variables, souvent progressifs selon le chiffre d'affaires. Pour comparer, regardez ce qu'il vous reste après l'abonnement, les frais et les éventuelles redevances, et pas seulement le taux affiché."),
    ("Y a-t-il une redevance de marque chez LOTIER ?",
     "Non. LOTIER ne prélève aucune redevance de marque. Selon le site de recrutement de l'agence, les agences à enseigne en franchise en prélèvent souvent entre 3 et 8 % du chiffre d'affaires."),
    ("Faut-il atteindre des quotas ?",
     "Non, LOTIER n'impose aucun quota. Vous organisez votre activité en toute liberté."),
    ("Quels sont les frais fixes pour démarrer ?",
     "Le coût d'entrée est de 160 € : 60 € pour la carte professionnelle (valable trois ans) et 100 € pour le kit de démarrage (panneaux, 100 cartes de visite, 100 flyers) avec une semaine de formation. L'abonnement est ensuite de 149 € TTC par mois, formation continue ALUR comprise."),
    ("Puis-je organiser mon activité comme je le souhaite ?",
     "Oui. L'organisation est libre : vous choisissez vos horaires et votre façon de travailler, et vous pouvez vous appuyer sur l'agence et son équipe quand vous en avez besoin. Vous n'avez aucune restriction géographique pour votre activité de vente, sur toute la France."),
    ("Un débutant ou une personne en reconversion peut-elle rejoindre LOTIER ?",
     "Oui. Le parcours d'intégration comprend le dossier de carte professionnelle, un kit de démarrage, une semaine de formation avec un formateur dédié, puis des premières ventes accompagnées et un mentor dédié dès votre arrivée."),
    ("Comment fonctionne le parrainage ?",
     "Vous touchez 5 %, 3 %, 2 % et 1 % du chiffre d'affaires HT de vos filleuls, sur quatre niveaux. Il s'ajoute à votre commission de 75 %."),
    ("Que comparer avant de choisir un réseau ou une agence ?",
     "Le taux de commission net après tous les frais, l'abonnement ou la redevance, les quotas éventuels, la durée d'engagement et les conditions de sortie, la formation initiale et continue, l'accompagnement au quotidien, la présence d'une agence et d'une équipe (gestion locative, syndic), et la liberté d'organisation. Demandez tout par écrit avant de vous engager."),
    ("Pourquoi choisir une agence indépendante plutôt qu'une franchise ?",
     "Une agence indépendante n'a pas de redevance de marque à reverser à un franchiseur ni de cahier des charges imposé : ce que vous gagnez vous revient davantage, et vous gardez la liberté de vous organiser. L'agence reste une structure à taille humaine, avec des interlocuteurs que vous connaissez."),
    ("Comment postuler ?",
     "Utilisez le formulaire de candidature de la page « Devenir agent », écrivez à recrutement@lotier-immobilier.com ou appelez le 04 67 11 28 31. Un membre de l'équipe vous rappelle pour présenter l'agence et répondre à vos questions."),
]

models = "".join(f'''<article class="glass model{' model-lotier' if lot else ''}">
          <span class="label">{e(lab)}</span><h3>{e(title)}</h3><p>{e(text)}</p>
          <ul class="tick">{"".join(f"<li>{e(x)}</li>" for x in pts)}</ul></article>''' for lab, title, text, pts, lot in [
    ("Modèle 1", "Réseau de mandataires", "Un agent indépendant, souvent à domicile, rattaché à un réseau en ligne.",
     ["Commission élevée, souvent progressive", "Abonnement ou frais mensuels, selon les réseaux", "Pas d'agence physique", "Accompagnement variable selon le réseau"], False),
    ("Modèle 2", "Agence classique", "Un agent qui s'appuie sur des locaux, une équipe et une marque.",
     ["Locaux et clientèle de passage", "Commission en moyenne de 50 à 60 %", "Redevance de marque en franchise : 3 à 8 % du chiffre d'affaires", "Quotas souvent imposés, liberté limitée"], False),
    ("Modèle 3", "Hybride LOTIER", "L'indépendance d'un réseau, avec l'appui d'une vraie agence.",
     ["75 % de commission HT", "Aucune redevance de marque, aucun quota", "Agences, cartes pro T, G et S, équipe gestion et syndic", "Mentor dédié, formation, parrainage 5·3·2·1 %"], True),
])

rows = [
    ("Statut", "Agent indépendant", "Salarié ou agent commercial", "Agent commercial indépendant"),
    ("Commission", "Élevée, souvent progressive", "50 à 60 % en moyenne", "75 % HT"),
    ("Redevance de marque", "Variable : abonnement ou forfait", "3 à 8 % du CA en franchise", "Aucune"),
    ("Quotas", "Rares à variables", "Souvent imposés", "Aucun"),
    ("Frais d'entrée et mensuels", "Variables selon le réseau", "Variables (dépôt, loyer de bureau, etc.)", "160 € à l'entrée, puis 149 € TTC par mois"),
    ("Agence physique", "Non", "Oui", "Oui (Béziers, Montpellier, Nîmes…)"),
    ("Équipe et services", "Plateforme et parrainage", "Équipe de l'agence", "Équipes vente, location, gestion et syndic"),
    ("Liberté d'organisation", "Grande", "Limitée", "Totale"),
    ("Zone d'exercice", "Variable", "Souvent locale", "Toute la France pour la vente"),
    ("Formation et accompagnement", "Variable", "Variable", "Semaine de formation, formation ALUR, mentor, rendez-vous mensuel"),
]
table = '<div class="table-wrap"><table class="legal-table versus compare">\n          <thead><tr><th scope="col">Critère</th><th scope="col">Réseau de mandataires</th><th scope="col">Agence classique</th><th scope="col">Hybride LOTIER</th></tr></thead>\n          <tbody>' + "".join(
    f'\n            <tr><th scope="row">{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td><td class="win">{e(d)}</td></tr>' for a, b, c, d in rows) + "\n          </tbody>\n        </table></div>"


BRANDS_NET = [
 ("SAFTI", "Réseau de mandataires", "Commission reversée au mandataire par paliers, de 70 % à 100 % selon le chiffre d'affaires cumulé. Abonnement mensuel d'environ 159 € HT (offre de lancement à 99 € les premiers mois).", "Sources publiques, consulter le site officiel"),
 ("iad", "Réseau de mandataires", "Rétrocession annoncée « jusqu'à » environ 85 à 88 % selon le palier, sous conditions (ancienneté, volume). Pas d'abonnement fixe communiqué de façon uniforme.", "Sources publiques, consulter le site officiel"),
 ("Propriétés Privées", "Réseau de mandataires", "Rétrocession annoncée entre 60 % et 90 % selon le niveau, d'après les offres de recrutement publiées.", "Offres de recrutement publiques"),
 ("BSK Immobilier", "Réseau de mandataires", "Conditions de rémunération non communiquées publiquement : à demander directement au réseau.", "Non communiqué"),
]
BRANDS_AG = [
 ("Century 21", "Franchise d'agences", "Agences indépendantes sous enseigne : redevance de franchise et droit d'entrée à la charge de l'agence, honoraires fixés par chaque agence.", "Informations générales de franchise"),
 ("Guy Hoquet", "Franchise d'agences", "Modèle de franchise comparable : droit d'entrée, redevance, honoraires libres par agence.", "Informations générales de franchise"),
 ("Laforêt", "Franchise d'agences", "Modèle de franchise comparable : droit d'entrée, redevance, honoraires libres par agence.", "Informations générales de franchise"),
 ("Foncia", "Agence intégrée / réseau", "Offres de recrutement publiques évoquant une rémunération de l'ordre de 50 à 70 % pour les négociateurs.", "Offres de recrutement publiques"),
 ("Citya", "Agence intégrée / réseau", "Aucune offre de rémunération publiée n'a été trouvée.", "Non communiqué"),
]
def brand_cards(cap, rows):
    cards="".join(f'<article class="glass quote"><h4 class="heading">{e(a)}</h4><p class="small"><strong>{e(b)}</strong></p><p class="muted">{e(c)}</p><p class="small muted">Source : {e(d)}</p></article>' for a,b,c,d in rows)
    return f'<h3 class="heading" style="margin:8px 0 14px">{e(cap)}</h3><div class="cards cards-2" data-stagger>{cards}</div>'
brands = brand_cards("Réseaux de mandataires", BRANDS_NET) + '<div style="height:28px"></div>' + brand_cards("Agences à enseigne", BRANDS_AG)

why = "".join(f'<article class="glass quote"><h3 class="heading">{e(t)}</h3><p class="muted">{e(p)}</p></article>' for t, p in [
    ("Une rémunération d'indépendant", "75 % de commission HT, sans redevance de marque ni quota : l'essentiel de ce que vous gagnez vous revient."),
    ("Une vraie agence derrière vous", "Des agences, des cartes professionnelles de transaction, de gestion et de syndic, et des équipes dédiées à la gestion locative et au syndic."),
    ("Une liberté totale d'organisation", "Vous décidez de votre façon de travailler, sans restriction géographique pour la vente, sur toute la France."),
    ("Un réseau humain", "Un mentor dédié, un rendez-vous communautaire chaque mois et un parrainage sur quatre niveaux (5·3·2·1 %)."),
])
faq_html = "".join(f'<details><summary><span class="cat">Question</span><h3>{e(q)}</h3></summary><div class="answer"><p>{e(a)}</p></div></details>' for q, a in FAQ_COMP)

body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><a href="../">Devenir agent</a><span aria-hidden="true">/</span><span aria-current="page">Comparatif</span></nav>
        <span class="label">Comparatif et FAQ</span>
        <h1 class="display page-title">Réseau, agence classique ou LOTIER : <em class="gold-text">quel modèle choisir ?</em></h1>
        <p class="lead">Trois façons d'exercer le métier d'agent immobilier. Ce que chacune apporte, ce qu'elle coûte, et pourquoi LOTIER propose un modèle hybride.</p>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="../#postuler">Devenir agent LOTIER {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="../#simulateur">Simuler ma commission</a></div>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-models">
      <div class="section-head" data-r><div class="stack-3"><span class="label">En un coup d'œil</span><h2 class="title" id="t-models">Trois modèles, <em class="gold-text">trois philosophies.</em></h2></div></div>
      <div class="models" data-stagger>{models}</div>
    </section>

    <section class="section container" id="tableau" aria-labelledby="t-table">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Le détail</span><h2 class="title" id="t-table">Le comparatif, critère par critère</h2><p class="muted">Repères généraux : les offres varient d'un réseau et d'une agence à l'autre. Vérifiez toujours les conditions écrites avant de vous engager.</p></div></div>
      <div data-r>{table}</div>
    </section>

    <section class="section container" id="offres" aria-labelledby="t-offres">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Repères par enseigne</span><h2 class="title" id="t-offres">Ce que disent les réseaux <em class="gold-text">et les enseignes.</em></h2><p class="muted">Informations indicatives issues de sources publiques consultées le 5 novembre 2026 (sites, offres de recrutement). Elles évoluent régulièrement et peuvent comporter des conditions : référez-vous toujours aux documents officiels de chaque enseigne. « Non communiqué » signifie qu'aucune donnée fiable n'a pu être vérifiée.</p></div></div>
      <div data-r>{brands}</div>
    </section>

    <section class="section container" aria-labelledby="t-why">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Le modèle hybride</span><h2 class="title" id="t-why">Le meilleur des deux, <em class="gold-text">sans les contraintes.</em></h2></div></div>
      <div class="cards cards-2" data-stagger>{why}</div>
    </section>

    <section class="section container" id="faq" aria-labelledby="t-faq-comp">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Questions fréquentes</span><h2 class="title" id="t-faq-comp">Vos questions sur <em class="gold-text">les modèles d'exercice.</em></h2></div></div>
      <div class="faq" data-r>{faq_html}</div>
      <div class="glass faq-cta">
        <p>Une question sur votre situation ? Un membre de l'équipe vous rappelle.</p>
        <a class="btn btn-navy btn-lg mag" href="../#postuler">Postuler maintenant</a>
      </div>
    </section>'''

ld = [
    {"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url, "name": "Réseau, agence classique ou LOTIER : comparatif et FAQ", "inLanguage": "fr-FR",
     "description": "Comparatif entre les réseaux de mandataires, l'agence classique et le modèle hybride de LOTIER Immobilier : commission, redevance, quotas, accompagnement.",
     "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#agence"}},
    {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq", "inLanguage": "fr-FR",
     "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_COMP]},
    breadcrumb_ld([("Accueil", SITE + "/"), ("Devenir agent", SITE + "/rejoindre/"), ("Comparatif", url)]),
]
os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
page = shell(prefix, "Réseau, agence classique ou LOTIER : le comparatif | LOTIER",
             "Comparatif entre réseaux de mandataires, agence classique et modèle hybride LOTIER : commission de 75 %, redevance, quotas, accompagnement, avec FAQ.",
             f"{folder}/", body, ld, "assets/photos/agent.jpg", cta=CTA)
open(f"{ROOT}/{folder}/index.html", "w", encoding="utf-8").write(page)
print("comparatif généré")
