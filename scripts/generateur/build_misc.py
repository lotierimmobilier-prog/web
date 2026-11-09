# -*- coding: utf-8 -*-
# Pages techniques et légales : plan du site, 404, mentions légales, confidentialité, honoraires, CGV,
# plus .htaccess, site.webmanifest et security.txt.
import os, json
from common import *

NOINDEX = "noindex, follow"
PH_TXT = "[À COMPLÉTER]"

def hero(title, lead, crumb):
    return f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{e(crumb)}</span></nav>
        <h1 class="display page-title">{e(title)}</h1>
        <p class="lead">{e(lead)}</p>
      </div>
    </section>'''

def legal_page(folder, title, lead, crumb, blocks, desc, note="Page à valider par l'agence avant publication : les champs entre crochets sont à compléter. Ce texte ne remplace pas l'avis d'un professionnel du droit."):
    """Page légale servie à l'adresse /<folder>/ (dossier avec index.html), comme sur l'ancien site."""
    prefix = "../"
    legal_note = f'<p class="legal-note glass">{e(note)}</p>' if note else ""
    body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{e(crumb)}</span></nav>
        <h1 class="display page-title">{e(title)}</h1>
        <p class="lead">{e(lead)}</p>
      </div>
    </section>

    <article class="container article legal">
      {legal_note}
      <div class="prose">
{blocks}
      </div>
    </article>'''
    os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
    open(f"{ROOT}/{folder}/index.html", "w", encoding="utf-8").write(
        shell(prefix, f"{title} | LOTIER Immobilier", desc, f"{folder}/", body,
              [breadcrumb_ld([("Accueil", SITE + "/"), (crumb, f"{SITE}/{folder}/")])], "assets/og-lotier.jpg", robots=NOINDEX))

# ---------- Mentions légales (informations reprises de l'ancien site) ----------
NOTE_REPRISE = ""
def fact(title, rows):
    items = "".join(f"<div><dt>{e(k)}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f'<section class="glass fact"><h2>{e(title)}</h2><dl>{items}</dl></section>'

mentions_facts = "".join([
    fact("Éditeur du site", [
        ("Raison sociale", "SARL LOTIER, enseigne LOTIER Immobilier"),
        ("Forme et capital", "Société à responsabilité limitée au capital de 7 500 €"),
        ("Siège social", "40 rue Française, 1er étage, 34500 Béziers"),
        ("SIRET", "452 117 294 00044"),
        ("RCS", "Béziers, n° 452 117 294"),
        ("TVA intracommunautaire", "FR21 452 117 294"),
        ("Gérant", "Nicolas Popovitch"),
        ("Directeur de la publication", "Jérôme Bouba"),
        ("Adresse du site", "lotier.immo"),
        ("Contact", f'<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>')]),
    fact("Carte professionnelle", [
        ("Numéro", 'CPI3401 2016 000 014 824<br><a href="https://www.cci.fr/agent-immobilier/documents/LOTIER/cartes/CPI34012016000014824" target="_blank" rel="noopener">Vérifier sur le registre des agents immobiliers (CCI)</a>'),
        ("Titulaire", "Nicolas Popovitch"),
        ("Délivrée par", "La CCI de l'Hérault"),
        ("Valable jusqu'au", "6 octobre 2028"),
        ("Activités", "Transaction sur immeubles et fonds de commerce (sans détention de fonds), gestion immobilière et syndic de copropriété")]),
    fact("Assurance et garanties financières", [
        ("Assurance responsabilité civile professionnelle", "SO.CA.F., Paris 15e"),
        ("Caisse de garantie", "SO.CA.F., garantie n° 105 708 080, 26 rue de Suffren, 75015 Paris"),
        ("Transaction sur immeubles et fonds de commerce", "110 000 €"),
        ("Gestion immobilière", "240 000 €"),
        ("Syndic de copropriété", "840 000 €")]),
    fact("Médiation de la consommation", [
        ("Médiateur", "Médiation Vivons Mieux Ensemble"),
        ("Adresse", "2 impasse de Beauregard, 54000 Nancy"),
        ("Site internet", '<a href="https://www.mediation-vivons-mieux-ensemble.fr" rel="noopener">www.mediation-vivons-mieux-ensemble.fr</a>'),
        ("Coût", "Procédure gratuite pour le consommateur"),
        ("Cadre", "Règlement amiable des litiges entre le professionnel et le consommateur, selon les articles L611-1 à L641-1 et R612-1 à R616-2 du Code de la consommation, sous conditions de recevabilité de la saisine. Le médiateur est neutre, indépendant et impartial ; la procédure de saisine est expliquée sur son site.")]),
    fact("Hébergement du site", [
        ("Hébergeur", "OVH SAS"),
        ("Adresse", "2 rue Kellermann, 59100 Roubaix, France"),
        ("Site internet", '<a href="https://www.ovhcloud.com/fr/" rel="noopener">www.ovhcloud.com</a>')]),
])
legal_page("mentions-legales", "Mentions légales", "Qui édite ce site, quelles sont nos garanties et comment nous joindre.", "Mentions légales", f'''
        <div class="fact-grid">{mentions_facts}</div>
        <h2>Propriété intellectuelle et droits d'auteur</h2>
        <p>Les textes, la mise en page, les illustrations et le logo du site sont la propriété de la SARL LOTIER, sauf mention contraire. Les informations présentes sur ce site peuvent être téléchargées, reproduites ou imprimées à condition de les utiliser à des fins personnelles et non commerciales, de ne pas les modifier et de reproduire sur chaque copie la mention des droits d'auteur (contact@lotier-immobilier.com). Toute autre utilisation est interdite sans autorisation écrite préalable de LOTIER.</p>
        <h2>Photographies</h2>
        <p>Les photographies d'illustration proviennent de la bibliothèque Pexels et sont publiées sous la licence Pexels. Elles seront progressivement remplacées par les photos de l'agence.</p>
        <h2>Responsabilité</h2>
        <p>Les informations publiées sur ce site ont une valeur indicative et sont fournies en l'état. Les articles de blog donnent des repères généraux et ne remplacent pas un conseil personnalisé. Les annonces présentées peuvent évoluer ou être retirées sans préavis. LOTIER se réserve le droit de modifier ce site et les présentes mentions à tout moment. LOTIER Immobilier ne saurait être tenue responsable des dommages directs ou indirects résultant d'une information contenue sur ce site, ni du contenu des sites externes vers lesquels renvoient certains liens, qui ne sont pas sous son contrôle.</p>
        <h2>Données personnelles</h2>
        <p>La SARL LOTIER est responsable du traitement des données personnelles collectées sur ce site. Les finalités, les durées de conservation et vos droits (accès, rectification, effacement, opposition, limitation, portabilité) sont détaillés dans notre <a class="text-link" href="../lotier-rgpd/">politique de confidentialité (RGPD)</a>. Pour exercer vos droits, écrivez à <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>. Vous pouvez aussi saisir la CNIL (<a href="https://www.cnil.fr" rel="noopener">www.cnil.fr</a>) si vous estimez que vos droits ne sont pas respectés.</p>
        <h2>Cookies</h2>
        <p>Ce site ne dépose aucun cookie publicitaire. Sa fréquentation est mesurée avec Umami, un outil de statistiques sans cookie. Le détail de ce qui est enregistré dans votre navigateur et la façon de le gérer figurent sur la page <a class="text-link" href="../cookies/">Cookies et traceurs</a>.</p>
        <h2>Messagerie</h2>
        <p>Pour toute remarque sur le fonctionnement du site, écrivez à <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>. Les messages transmis par internet peuvent être interceptés : leur confidentialité ne peut être garantie jusqu'à leur réception.</p>''',
  "Mentions légales de LOTIER Immobilier : éditeur, carte professionnelle, assurance, garantie financière, médiateur de la consommation et hébergement.", note=NOTE_REPRISE)

# ---------- Politique de confidentialité (RGPD) ----------
rgpd_toc = [("responsable", "Responsable du traitement"), ("referent", "Référent à la protection des données"), ("perimetre", "Périmètre"), ("donnees", "Données collectées"), ("finalites", "Finalités et bases légales"),
            ("destinataires", "Destinataires"), ("durees", "Durées de conservation"), ("droits", "Vos droits"), ("exercer", "Exercer vos droits"), ("securite", "Sécurité"), ("transferts", "Transferts hors Union européenne"), ("reclamation", "Réclamation auprès de la CNIL"), ("cookies", "Cookies")]
toc_html = '<nav class="glass toc" aria-label="Sommaire"><span class="label">Sommaire</span><ul>' + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in rgpd_toc) + "</ul></nav>"
bref = '<div class="fact-grid fact-grid-3">' + "".join(f'<section class="glass fact"><h2>{e(t)}</h2><p>{e(p)}</p></section>' for t, p in [
    ("Vos données ne sont pas vendues", "Elles servent à traiter votre demande et à exécuter nos contrats. Nous ne les vendons, ne les louons ni ne les cédons à des fins commerciales."),
    ("Vous gardez la main", "Accès, rectification, effacement, opposition, limitation, portabilité : écrivez-nous, nous répondons sous un mois."),
    ("Un référent dédié", "Jérôme Bouba, référent à la protection des données, répond à vos questions. En cas de violation, la CNIL est informée sous 72 heures.")]) + "</div>"
rgpd_ident = fact("Responsable du traitement", [
    ("Raison sociale", "SARL LOTIER (LOTIER Immobilier)"),
    ("Siège", "40 rue Française, 1er étage, 34500 Béziers"),
    ("SIRET", "452 117 294 00044"),
    ("RCS", "Béziers, n° 452 117 294"),
    ("Représentant légal", "Nicolas Popovitch, gérant"),
    ("Téléphone", PHONE_DISPLAY),
    ("E-mail", '<a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>'),
    ("Site", "lotier.immo")])
legal_page("lotier-rgpd", "Politique de confidentialité (RGPD)", "Comment LOTIER Immobilier protège vos données personnelles, et comment exercer vos droits.", "Données personnelles (RGPD)", f'''
        {bref}
        {toc_html}
        <p>En qualité de responsable du traitement, LOTIER Immobilier respecte le règlement (UE) 2016/679 du 27 avril 2016 (RGPD) et la loi n° 78-17 du 6 janvier 1978 modifiée relative à l'informatique, aux fichiers et aux libertés.</p>
        <h2 id="responsable">Responsable du traitement</h2>
        <p>Les données personnelles sont collectées et traitées par la SARL LOTIER, qui exerce ses activités de transaction, de gestion locative et de syndic de copropriété à Béziers, Montpellier, Nîmes et Carcassonne.</p>
        {rgpd_ident}
        <h2 id="referent">Référent à la protection des données</h2>
        <p>LOTIER Immobilier a désigné un référent chargé de veiller au respect de la réglementation, pour les traitements réalisés en agence comme sur le site.</p>
        <ul>
          <li><b>Référent :</b> Jérôme Bouba ;</li>
          <li><b>E-mail :</b> <a href="mailto:jerome.bouba@lotier-immobilier.com">jerome.bouba@lotier-immobilier.com</a> ;</li>
          <li><b>Courrier :</b> LOTIER Immobilier, Référent protection des données, 40 rue Française, 1er étage, 34500 Béziers.</li>
        </ul>
        <h2 id="perimetre">Périmètre</h2>
        <p>Cette politique couvre les données recueillies <b>en agence</b> (projets de vente, d'achat ou de location, mandats, baux, états des lieux, assemblées générales de copropriété) et celles issues <b>du site</b> lotier.immo (formulaires, messages, données de navigation).</p>
        <h2 id="donnees">Données collectées</h2>
        <h3>En agence</h3>
        <ul>
          <li><b>Identification :</b> nom, prénom, date et lieu de naissance, adresse postale, téléphone, e-mail, pièce d'identité ;</li>
          <li><b>Situation financière :</b> revenus, avis d'imposition, relevés bancaires, garanties locatives, dans le cadre de la gestion locative et du syndic ;</li>
          <li><b>Bien immobilier :</b> adresse, surface, diagnostics, état des lieux, règlement de copropriété ;</li>
          <li><b>Contrats :</b> mandats, baux, procès-verbaux d'assemblée générale, correspondances, quittances.</li>
        </ul>
        <h3>Sur le site</h3>
        <ul>
          <li><b>Contact :</b> nom, prénom, e-mail, téléphone saisis dans les formulaires ;</li>
          <li><b>Projet :</b> type de bien recherché, localisation, budget, informations saisies librement dans vos messages ;</li>
          <li><b>Navigation :</b> données techniques de connexion (adresse IP, type de navigateur) traitées par l'hébergeur pour assurer le fonctionnement et la sécurité du site.</li>
        </ul>
        <p>Les champs signalés comme obligatoires sont nécessaires au traitement de votre demande : sans eux, nous ne pouvons pas y donner suite. Le formulaire d'estimation prépare un e-mail adressé à l'agence : les informations partent depuis votre messagerie.</p>
        <h2 id="finalites">Finalités et bases légales</h2>
        <table class="legal-table">
          <thead><tr><th scope="col">Finalité</th><th scope="col">Base légale</th></tr></thead>
          <tbody>
            <tr><td>Gestion des projets de vente, d'achat ou de location</td><td>Exécution d'un contrat ou de mesures précontractuelles</td></tr>
            <tr><td>Gestion locative : baux, quittances, états des lieux, charges</td><td>Exécution du mandat de gestion</td></tr>
            <tr><td>Syndic : convocations, procès-verbaux, appels de fonds, sinistres</td><td>Exécution du contrat de syndic</td></tr>
            <tr><td>Comptabilité, obligations fiscales, lutte contre le blanchiment et le financement du terrorisme</td><td>Obligation légale</td></tr>
            <tr><td>Communications commerciales, newsletters, propositions de biens</td><td>Votre consentement, retirable à tout moment</td></tr>
            <tr><td>Sécurité du site, amélioration du service, statistiques de fréquentation (sans cookie)</td><td>Intérêt légitime</td></tr>
            <tr><td>Gestion des litiges et recouvrement</td><td>Intérêt légitime (défense de nos droits)</td></tr>
          </tbody>
        </table>
        <h2 id="destinataires">Destinataires</h2>
        <p>Vos données sont traitées par les collaborateurs habilités de l'agence, dans le strict cadre de leurs missions. Elles peuvent être transmises, dans la limite du nécessaire, à :</p>
        <ul>
          <li>nos prestataires de logiciels de gestion immobilière (ICS, logiciel Spirit) et de comptabilité de syndic (CEGIMM) ;</li>
          <li>les notaires, diagnostiqueurs, géomètres et autres professionnels intervenant dans votre dossier ;</li>
          <li>les assureurs (garantie des loyers impayés, assurance de l'immeuble, sinistres) et les établissements bancaires concernés par votre dossier ;</li>
          <li>notre hébergeur (OVH) et nos prestataires de maintenance informatique ;</li>
          <li>notre outil de mesure d'audience (Umami), qui reçoit des statistiques de fréquentation du site ;</li>
          <li>un prestataire d'envoi d'e-mails, si vous avez consenti à recevoir nos communications commerciales ;</li>
          <li>les autorités administratives ou judiciaires, sur demande légale.</li>
        </ul>
        <p>Vos données ne sont ni vendues, ni louées, ni cédées à des tiers à leurs propres fins commerciales.</p>
        <h2 id="durees">Durées de conservation</h2>
        <table class="legal-table">
          <thead><tr><th scope="col">Type de données</th><th scope="col">Durée</th></tr></thead>
          <tbody>
            <tr><td>Contacts sans projet précis</td><td>3 mois</td></tr>
            <tr><td>Prospects (coordonnées et projet communiqués)</td><td>3 ans à compter du dernier contact</td></tr>
            <tr><td>Clients : locataires, propriétaires mandants, copropriétaires</td><td>Durée de la relation contractuelle, puis 5 ans</td></tr>
            <tr><td>Dossiers de lutte contre le blanchiment</td><td>5 ans après la fin de la relation d'affaires</td></tr>
            <tr><td>Documents comptables et pièces justificatives</td><td>10 ans</td></tr>
            <tr><td>Cookies et traceurs soumis à consentement</td><td>13 mois maximum</td></tr>
          </tbody>
        </table>
        <p>À l'issue de ces durées, les données sont supprimées ou anonymisées.</p>
        <h2 id="droits">Vos droits</h2>
        <ul>
          <li><b>Accès :</b> obtenir une copie de vos données et des informations sur leur traitement ;</li>
          <li><b>Rectification :</b> faire corriger des données inexactes ou incomplètes ;</li>
          <li><b>Effacement :</b> demander la suppression de vos données dans les cas prévus par la loi ;</li>
          <li><b>Limitation :</b> suspendre temporairement le traitement dans certains cas ;</li>
          <li><b>Portabilité :</b> recevoir vos données dans un format structuré et lisible par machine ;</li>
          <li><b>Opposition :</b> vous opposer à tout moment au traitement, notamment à la prospection commerciale, sans avoir à vous justifier ;</li>
          <li><b>Retrait du consentement :</b> à tout moment, sans effet sur les traitements antérieurs ;</li>
          <li><b>Directives après décès :</b> définir le sort de vos données après votre décès (loi n° 2016-1321 du 7 octobre 2016).</li>
        </ul>
        <p>Pour ne plus recevoir nos communications commerciales, écrivez-nous ou utilisez le lien de désinscription présent dans chaque e-mail.</p>
        <h2 id="exercer">Exercer vos droits</h2>
        <p>Adressez votre demande à notre référent : par e-mail à <a href="mailto:jerome.bouba@lotier-immobilier.com">jerome.bouba@lotier-immobilier.com</a>, par courrier au 40 rue Française, 1er étage, 34500 Béziers, ou par téléphone au {PHONE_DISPLAY}. Indiquez vos nom, prénom, adresse postale et e-mail. En cas de doute raisonnable, nous pouvons vous demander un justificatif d'identité.</p>
        <p>Nous répondons dans un délai d'un mois à compter de la réception de votre demande. Ce délai peut être prolongé de deux mois en raison de la complexité ou du nombre de demandes : vous en serez alors informé.</p>
        <h2 id="securite">Sécurité</h2>
        <p>Nous mettons en œuvre des mesures techniques et organisationnelles adaptées :</p>
        <ul>
          <li>accès limités aux collaborateurs concernés, selon leurs missions ;</li>
          <li>communications sécurisées (HTTPS) ;</li>
          <li>sauvegardes régulières ;</li>
          <li>sensibilisation des collaborateurs à la protection des données ;</li>
          <li>obligations de confidentialité et de protection des données imposées à nos prestataires.</li>
        </ul>
        <p>En cas de violation de données présentant un risque pour vos droits et libertés, nous la notifions à la CNIL dans les 72 heures et, si le risque est élevé, nous vous en informons dans les meilleurs délais.</p>
        <h2 id="transferts">Transferts hors Union européenne</h2>
        <p>Nous traitons vos données principalement dans l'Union européenne. Si un prestataire impliquait un transfert hors de l'Union (par exemple certains outils de messagerie ou d'envoi d'e-mails), ce transfert serait encadré par des garanties reconnues par la Commission européenne : décision d'adéquation, clauses contractuelles types ou règles d'entreprise contraignantes.</p>
        <h2 id="reclamation">Réclamation auprès de la CNIL</h2>
        <p>Nous vous invitons à nous contacter en premier lieu. En l'absence de réponse ou si elle ne vous satisfait pas, vous pouvez saisir la Commission nationale de l'informatique et des libertés (CNIL), autorité de contrôle française : 3 place de Fontenoy, TSA 80715, 75334 Paris Cedex 07, téléphone 01 53 73 22 22, <a class="text-link" href="https://www.cnil.fr/fr/plaintes" rel="noopener">cnil.fr/fr/plaintes</a>.</p>
        <h2 id="cookies">Cookies</h2>
        <p>Un cookie est un petit fichier enregistré sur votre appareil lors de la visite d'un site. À ce jour, ce site ne dépose ni cookie publicitaire, ni cookie de réseau social. La mesure d'audience (Umami) fonctionne sans cookie. La police de caractères est hébergée sur le site : aucune donnée n'est transmise à un service tiers pour l'afficher.</p>
        <p>Si de tels cookies étaient ajoutés, vous en seriez informé et votre consentement serait demandé avant tout dépôt, avec un refus aussi simple que l'acceptation et une durée de validité de 13 mois au maximum. Vous pouvez aussi configurer votre navigateur pour refuser ou supprimer les cookies. Le détail figure sur la page <a class="text-link" href="../cookies/">Cookies et traceurs</a> ; voir aussi les conseils de la <a class="text-link" href="https://www.cnil.fr/fr/cookies-et-traceurs-comment-les-maitriser" rel="noopener">CNIL</a>.</p>
        <p>Dernière mise à jour : novembre 2026. Cette politique peut évoluer ; la version en ligne fait foi.</p>''',
  "Politique de confidentialité de LOTIER Immobilier : données traitées, finalités, durées de conservation, droits RGPD, cookies et réclamation.", note="")

# ---------- Honoraires ----------
def hon_table(head, rows, num=False, extra=""):
    """Tableau d'honoraires. num : colonnes de valeurs centrées. Une cellule (texte, n) s'étend sur n colonnes."""
    nc = ' class="num"' if num else ""
    th = "".join(f'<th scope="col"{nc if i else ""}>{e(h)}</th>' for i, h in enumerate(head))
    def cell(i, c):
        txt, span = c if isinstance(c, tuple) else (c, 1)
        attrs = (f' colspan="{span}"' if span > 1 else "") + (nc if i else "")
        return f"<td{attrs}>{txt}</td>"
    body = "".join("<tr>" + "".join(cell(i, c) for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table class="legal-table hon-table {extra}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

hon_vente = hon_table(["Prix de vente", "Honoraires (TTC)"], num=True, rows=[
    ("De 0 à 10 000 €", "3 000 €"), ("De 10 001 à 70 000 €", "10 % (minimum 3 000 €)"), ("De 70 001 à 100 000 €", "8 %"),
    ("De 100 001 à 150 000 €", "7 %"), ("De 150 001 à 200 000 €", "6 %"), ("À partir de 200 001 €", "5 %")])
hon_loc = hon_table(["Prestation (€ TTC par m²)", "Autre zone", "Zone tendue", "Zone très tendue"], num=True, extra="hon-zones", rows=[
    ("Mise en location : visite, constitution du dossier, édition du bail", "8,07 €", "10,09 €", "12,10 €"),
    ("État des lieux d'entrée et de sortie", ("3,03 € quelle que soit la zone", 3))])
hon_gest = hon_table(["Formule", "Tarif"], [
    ("Gestion complète : gestion administrative, quotidienne et financière, révision du loyer, contentieux et travaux", "7 % HT par mois, soit 8,40 % TTC (TVA 20 %)"),
    ("Gestion locative : gestion administrative, quotidienne et financière, révision du loyer", "39,99 € TTC par mois")])
hon_gli = hon_table(["Assurance loyers impayés", "Tarif"], [("Assurances Chevalier", "4 % du loyer charges comprises"), ("Mila / Zelok", "3,5 % TTC du loyer charges comprises")])
hon_syn = hon_table(["Taille de la copropriété", "Honoraires annuels (TTC)"], num=True, rows=[
    ("De 1 à 10 lots", "2 000 €"), ("De 11 à 50 lots", "160 € par lot"), ("De 51 à 100 lots", "150 € par lot"),
    ("De 101 à 200 lots", "144 € par lot"), ("Plus de 200 lots", "Sur devis")])
legal_page("nos-honoraires", "Nos honoraires", "Le barème des honoraires de l'agence, tel qu'il est affiché en agence.", "Nos honoraires", f'''
        <p>Ni forfait au rabais, ni tarifs excessifs qui compliquent parfois l'obtention d'un prêt : nous avons établi un barème lisible, applicable à tous.</p>
        <h2 id="vente">Vente</h2>
        <p>Honoraires de négociation, toutes taxes comprises, à la charge du vendeur et inclus dans le prix affiché.</p>
        {hon_vente}
        <h2 id="location">Location</h2>
        <p>Honoraires de mise en location et d'état des lieux, selon la zone où se situe le logement. Les montants, en euros TTC, sont exprimés par mètre carré de surface habitable et valables pour les baux signés à partir du 1er janvier 2026.</p>
        {hon_loc}
        <h2 id="gestion">Gestion locative</h2>
        {hon_gest}
        <h3>Assurance loyers impayés (facultative)</h3>
        {hon_gli}
        <h2 id="syndic">Syndic de copropriété</h2>
        <p>Honoraires annuels, toutes taxes comprises (TVA à 20 %).</p>
        {hon_syn}
        <p>Ces honoraires sont répartis entre les copropriétaires selon leurs millièmes. Ils s'appliquent par lot principal (un appartement, par exemple) et non aux lots accessoires (garage, parking, cave…), sauf si ces lots sont indépendants, par exemple lorsque leur propriétaire ne possède pas d'appartement.</p>
        <p>Pour toute précision sur ce barème : <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a> ou {PHONE_DISPLAY}.</p>''',
  "Barème des honoraires de LOTIER Immobilier : vente, location, gestion locative, assurance loyers impayés et syndic.", note="")

# ---------- Cookies et traceurs ----------
legal_page("cookies", "Cookies et traceurs", "Ce que ce site enregistre sur votre appareil, et comment le gérer.", "Cookies et traceurs", f'''
        <h2>Ce que le site enregistre</h2>
        <p>Ce site ne dépose aucun cookie publicitaire ni de mesure d'audience. La mesure d'audience est faite sans cookie (voir ci-dessous). Il utilise uniquement le stockage local de votre navigateur pour retenir, sur votre appareil, quelles nouveautés vous avez déjà consultées (cloche « Nouveautés »). Cette donnée ne quitte pas votre navigateur.</p>
        <h2>Mesure d'audience</h2>
        <p>Nous mesurons la fréquentation du site (pages consultées, provenance, type d'appareil) avec Umami, un service de statistiques conçu pour fonctionner sans cookie. Ces statistiques servent uniquement à améliorer le site ; elles ne sont pas utilisées à des fins publicitaires ni croisées avec d'autres sites. Vous pouvez refuser cette mesure à tout moment avec le bouton « Modifier mon choix » ci-dessous. Lieu d'hébergement des statistiques : {PH_TXT}.</p>
        <h2>Si d'autres outils de contenu externe sont ajoutés</h2>
        <p>Cartes, vidéos ou réseaux sociaux ne sont pas utilisés à ce jour. S'ils l'étaient, votre consentement serait demandé avant tout dépôt.</p>
        <h2>Gérer vos choix</h2>
        <p>Votre choix du bandeau cookies est mémorisé sur votre appareil. <button type="button" class="btn btn-ghost" data-cookie-open>Modifier mon choix</button></p>
        <p>Vous pouvez à tout moment supprimer les données enregistrées par ce site depuis les réglages de votre navigateur (rubrique « Confidentialité » ou « Cookies et données de sites »).</p>
        <h2>Contact</h2>
        <p>Pour toute question : <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>.</p>''',
  "Cookies et traceurs sur le site de LOTIER Immobilier : ce qui est enregistré et comment le gérer.")

# ---------- Déclaration d'accessibilité ----------
legal_page("accessibilite", "Déclaration d'accessibilité", "Notre engagement pour un site utilisable par tous.", "Accessibilité", f'''
        <h2>Notre engagement</h2>
        <p>LOTIER Immobilier s'efforce de rendre ce site accessible : navigation au clavier, contrastes de couleurs, textes alternatifs sur les images, respect du réglage « réduire les animations » de votre appareil.</p>
        <h2>État de conformité</h2>
        <p>{PH_TXT} : le niveau de conformité au référentiel RGAA n'a pas encore été évalué par un audit. Aucune conformité n'est déclarée à ce jour.</p>
        <h2>Signaler un défaut d'accessibilité</h2>
        <p>Si vous ne parvenez pas à accéder à un contenu ou à un service, écrivez-nous à <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a> ou appelez le <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> : nous vous fournirons l'information sous une autre forme.</p>
        <h2>Voies de recours</h2>
        <p>{PH_TXT} : coordonnées du Défenseur des droits, à indiquer si votre demande reste sans réponse satisfaisante.</p>''',
  "Déclaration d'accessibilité du site de LOTIER Immobilier.")

# ---------- Plan du site (HTML) ----------
def plan_page():
    cats = []
    for a in ARTICLES_BY_DATE:
        if a["cat"] not in cats: cats.append(a["cat"])
    def li(href, label): return f'<li><a href="{href}">{e(label)}</a></li>'
    villes = "".join(li(f"{c['slug']}.html", f"Agence immobilière à {c['name']}") for c in CITIES)
    blog = ""
    for cat in cats:
        items = "".join(li(f"blog/{a['slug']}.html", a["title"]) for a in ARTICLES_BY_DATE if a["cat"] == cat)
        blog += f'<div><h3>{e(cat)}</h3><ul>{items}</ul></div>'
    body = hero("Plan du site", "Toutes les pages du site de LOTIER Immobilier, par thème.", "Plan du site") + f'''

    <section class="section container" aria-label="Plan du site">
      <div class="plan-grid" data-stagger>
        <div class="glass plan-box"><h2>Accueil</h2><ul>
          {li("index.html", "Page d'accueil")}
          {li("nos-annonces/", "Annonces")}
          {li("index.html#metiers", "Vente, location, syndic")}
          {li("index.html#conseils", "Conseils immo (questions fréquentes)")}
          {li("a-propos/", "À propos")}
          {li("contact/", "Contact")}
          {li("notre-service/", "Notre service")}
          {li("vente/", "Vendre avec LOTIER")}
          {li("location/", "Location et gestion locative")}
          {li("syndic/", "Syndic de copropriété")}
          {li("nos-agents/", "Nos agents par secteur")}
          {li("index.html#estimer", "Estimer mon bien")}
          {li("index.html#contact", "Contact et agences")}
          {li("mylotier/", "MyLotier, espace client")}
          {li("rejoindre/", "Devenir agent immobilier indépendant")}
          {li("rejoindre/comparatif/", "Comparatif : réseaux, agence classique, LOTIER")}
        </ul></div>
        <div class="glass plan-box"><h2>Nos villes</h2><ul>{villes}</ul></div>
        <div class="glass plan-box"><h2>Informations</h2><ul>
          {li("nos-honoraires/", "Nos honoraires")}
          {li("cookies/", "Cookies et traceurs")}
          {li("accessibilite/", "Déclaration d'accessibilité")}
          {li("mentions-legales/", "Mentions légales")}
          {li("lotier-rgpd/", "Données personnelles (RGPD)")}
        </ul></div>
        <div class="glass plan-box"><h2>Pour les robots</h2><ul>
          {li("sitemap.xml", "sitemap.xml (plan du site pour les moteurs de recherche)")}
          {li("robots.txt", "robots.txt")}
          {li("llms.txt", "llms.txt (résumé pour les assistants IA)")}
        </ul></div>
      </div>
    </section>

    <section class="section container" aria-labelledby="t-blog-plan">
      <div class="section-head" data-r><div class="stack-3"><span class="label">Blog</span><h2 class="title" id="t-blog-plan">Les {len(ARTICLES)} articles par thème</h2></div><a class="text-link" href="blog/index.html">Voir l'index du blog</a></div>
      <div class="plan-grid plan-blog" data-stagger>{blog}</div>
    </section>'''
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "@id": SITE + "/plan-du-site.html", "name": "Plan du site LOTIER Immobilier", "url": SITE + "/plan-du-site.html", "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}},
          breadcrumb_ld([("Accueil", SITE + "/"), ("Plan du site", SITE + "/plan-du-site.html")])]
    open(f"{ROOT}/plan-du-site.html", "w", encoding="utf-8").write(
        shell("", "Plan du site | LOTIER Immobilier", "Plan du site de LOTIER Immobilier : pages de villes, articles de blog, informations légales et fichiers pour les moteurs de recherche.", "plan-du-site.html", body, ld, "assets/og-lotier.jpg"))
plan_page()

# ---------- Page 404 ----------
cities_links = "".join(f'<a class="chip-link" href="{c["slug"]}.html">Immobilier à {e(c["name"])}</a>' for c in CITIES)
body404 = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <span class="label">Erreur 404</span>
        <h1 class="display page-title">Cette page est introuvable.</h1>
        <p class="lead">Le lien est peut-être ancien ou mal saisi. Voici de quoi retrouver votre chemin.</p>
        <div class="acts"><a class="btn btn-gold btn-lg mag" href="/index.html">Retour à l'accueil {ARROW}</a><a class="btn btn-ghost btn-lg mag" href="tel:{PHONE_TEL}">{PH}{PHONE_DISPLAY}</a></div>
      </div>
    </section>
    <section class="section container" aria-label="Pages utiles">
      <div class="glass near">
        <div><span class="label">Nos villes</span><div class="chip-links">{cities_links}</div></div>
        <div><span class="label">À lire</span><div class="chip-links"><a class="chip-link" href="/blog/index.html">Le blog</a><a class="chip-link" href="/plan-du-site.html">Plan du site</a><a class="chip-link" href="/index.html#estimer">Estimer mon bien</a></div></div>
      </div>
    </section>'''
# La page 404 est servie depuis n'importe quelle adresse : tous les liens sont absolus (depuis la racine).
html404 = shell("/", "Page introuvable | LOTIER Immobilier", "Cette page est introuvable. Retrouvez nos pages de villes, notre blog et notre plan du site.", "404.html", body404, [], "assets/og-lotier.jpg", robots="noindex, nofollow")
html404 = html404.replace('href="/index.html#estimer"', 'href="/index.html#estimer"')
open(f"{ROOT}/404.html", "w", encoding="utf-8").write(html404)

# ---------- Fichiers techniques ----------
open(f"{ROOT}/.htaccess", "w", encoding="utf-8").write('''# LOTIER Immobilier : configuration Apache (hébergement mutualisé OVH).
# Chaque bloc est protégé : s'il n'est pas disponible sur l'offre d'hébergement, il est ignoré.

ErrorDocument 404 /404.html
Options -Indexes
DirectoryIndex index.html index.php

<IfModule mod_rewrite.c>
  RewriteEngine On
  # Toujours en HTTPS
  RewriteCond %{HTTPS} !=on
  RewriteCond %{HTTP:X-Forwarded-Proto} !https
  RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
  # Ancien site de recrutement : le sous-domaine renvoie vers la page /rejoindre/ (si le sous-domaine pointe vers ce dossier)
  RewriteCond %{HTTP_HOST} ^rejoindre\\.lotier-immobilier\\.com$ [NC]
  RewriteRule ^ https://lotier.immo/rejoindre/ [L,R=301]
  # Adresse sans « www » (à adapter si le domaine canonique est avec www)
  RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
  RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]
  # /index.html -> /
  RewriteCond %{THE_REQUEST} \\s/index\\.html[\\s?] [NC]
  RewriteRule ^index\\.html$ / [L,R=301]

  # Dossiers et fichiers de travail du dépôt : jamais servis au public (le site est déployé depuis GitHub)
  RewriteRule ^(v2|audit-lotier|mise-en-ligne|scripts|\\.claude|\\.git|node_modules)(/|$) - [R=404,L]
  RewriteRule ^(README\\.md|CLAUDE\\.md|\\.gitignore)$ - [R=404,L]

  # Négociation de contenu : un agent qui demande « Accept: text/markdown » reçoit la version Markdown de la page
  RewriteCond %{HTTP:Accept} text/markdown [NC]
  RewriteCond %{REQUEST_URI} ^(.*/)$
  RewriteCond %{DOCUMENT_ROOT}%1index.md -f
  RewriteRule ^(.*/)?$ $1index.md [L,T=text/markdown]
  RewriteCond %{HTTP:Accept} text/markdown [NC]
  RewriteCond %{REQUEST_URI} ^(.+)\\.html$
  RewriteCond %{DOCUMENT_ROOT}%1.md -f
  RewriteRule ^(.+)\\.html$ $1.md [L,T=text/markdown]

  # Anciennes adresses du site WordPress : redirections permanentes vers les nouvelles pages
  # (liste établie à partir du plan du site de l'ancien site ; à tester après la mise en ligne)
  RewriteRule ^gestion-2/?$ /nos-honoraires/ [NE,L,R=301]
  RewriteRule ^(gestion|gestion-locative|gestion-locative-lotier)/?$ /location/ [NE,L,R=301]
  RewriteRule ^syndic-de-copropriete/?$ /syndic/ [NE,L,R=301]
  RewriteRule ^mentions-legales-2/?$ /mentions-legales/ [NE,L,R=301]
  RewriteRule ^faq/?$ /#conseils [NE,L,R=301]
  RewriteRule ^avis/?$ /#avis [NE,L,R=301]
  RewriteRule ^nos-biens/?$ /nos-annonces/ [NE,L,R=301]
  RewriteRule ^(mandataire|transaction-mandataire|faq-mandataire|gestion-mandataire)/?$ /rejoindre/ [NE,L,R=301]
  RewriteRule ^(jerome-bouba-entrepreneur-immobilier-et-fondateur-de-lotier-immobilier|nicolas-popovitch-parcours-et-experience-dans-limmobilier)/?$ /notre-service/ [NE,L,R=301]
  RewriteRule ^(espace-proprietaire|espace-membre|connections|login|logout|user|members|account|password-reset|lotier-immobilier-accueil/page-de-connexion-ics-lotier)/?$ /mylotier/ [NE,L,R=301]
  RewriteRule ^limportance-dune-gestion-de-copropriete-efficace/?$ /blog/charges-copropriete-appel-de-fonds.html [NE,L,R=301]
  RewriteRule ^vendre-votre-bien-immobilier-pourquoi-lentretien-fait-toute-la-difference/?$ /blog/home-staging-mieux-vendre.html [NE,L,R=301]
  RewriteRule ^(il-achete-letage-entier|2-immeubles-tres-rentable|pourquoi-recevez-vous-cet-email-en-tant-que-locataire|category/blog|category/non-classe)/?$ /blog/ [NE,L,R=301]
  # Anciennes fiches de biens et filtres de recherche : retour vers la section Annonces
  RewriteCond %{DOCUMENT_ROOT}/annonces/$1/index.html -f
  RewriteRule ^propriete/([a-z0-9-]+)/?$ /annonces/$1/ [NE,L,R=301]
  RewriteRule ^(propriete|iwp_[a-z_]+)/ /nos-annonces/ [NE,L,R=301]
  # Anciens comptes auteurs, brouillons : retour vers l'accueil
  RewriteRule ^(author/.*|brouillon-auto(-2)?/?)$ / [L,R=301]
</IfModule>

<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json application/ld+json text/plain text/xml application/xml image/svg+xml
</IfModule>

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType text/html "access plus 0 seconds"
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set Permissions-Policy "camera=(), microphone=(), geolocation=()"
  # Ressources annoncées aux agents (RFC 8288)
  Header always set Link '</llms.txt>; rel="describedby"; type="text/plain", </sitemap.xml>; rel="sitemap"; type="application/xml", </.well-known/mcp/server-card.json>; rel="mcp-server-card"; type="application/json"' "expr=%{REQUEST_URI} == '/' || %{REQUEST_URI} == '/index.html'"
  # Les versions Markdown ne doivent pas concurrencer les pages HTML dans les moteurs
  <FilesMatch "\\.md$">
    Header set X-Robots-Tag "noindex"
    Header set Content-Type "text/markdown; charset=utf-8"
  </FilesMatch>
  Header merge Vary Accept "expr=%{CONTENT_TYPE} =~ m#^text/(html|markdown)#"
  <FilesMatch "server-card\\.json$">
    Header set Access-Control-Allow-Origin "*"
  </FilesMatch>
</IfModule>

AddDefaultCharset UTF-8
AddType application/manifest+json .webmanifest
AddType font/woff2 .woff2
AddType text/markdown .md
''')
open(f"{ROOT}/site.webmanifest", "w", encoding="utf-8").write(json.dumps({
    "name": "LOTIER Immobilier", "short_name": "LOTIER", "lang": "fr-FR", "start_url": "/", "display": "browser",
    "background_color": "#eef3f9", "theme_color": "#eef3f9",
    "icons": [{"src": "/assets/favicon.png", "sizes": "192x192", "type": "image/png"}]}, ensure_ascii=False, indent=2) + "\n")
os.makedirs(f"{ROOT}/.well-known", exist_ok=True)
open(f"{ROOT}/.well-known/security.txt", "w", encoding="utf-8").write(f'''Contact: mailto:contact@lotier-immobilier.com
Expires: 2027-11-05T00:00:00.000Z
Preferred-Languages: fr
Canonical: {SITE}/.well-known/security.txt
''')
print("pages techniques générées")
