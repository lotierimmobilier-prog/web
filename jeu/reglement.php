<?php
// Concours de Noël : règlement du jeu et information sur les données personnelles.
declare(strict_types=1);
require __DIR__ . '/lib.php';
entetes_page();
$lot = function ($rang): string {
    $v = JEU_LOTS[$rang] ?? null;
    return $v ? 'un bon cadeau culturel d’une valeur de ' . $v . ' € TTC' : 'un bon cadeau culturel';
};
?><!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Règlement du concours de Noël | LOTIER Immobilier</title>
  <meta name="description" content="Règlement du concours de dessin de Noël de LOTIER Immobilier : participation, votes, lots et protection des données personnelles.">
  <link rel="canonical" href="<?= h(JEU_URL) ?>reglement.php">
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  <link rel="stylesheet" href="style.css?v=22">
</head>
<body>
  <header class="haut">
    <a class="logo" href="../" aria-label="LOTIER Immobilier, retour au site"><img src="../assets/lotier-logo-330.png" alt="LOTIER Immobilier" width="165" height="56"></a>
    <nav aria-label="Concours"><a href="./">Le concours</a><a href="./#galerie">Les dessins</a></nav>
  </header>
  <main class="bloc reglement">
    <h1>Règlement du concours de Noël</h1>

    <h2>Article 1. Organisateur</h2>
    <p>Le concours est organisé par la SARL LOTIER, enseigne LOTIER Immobilier, société à responsabilité limitée au capital de 7 500 €, dont le siège est situé 40 rue Française, 1er étage, 34500 Béziers, immatriculée au RCS de Béziers sous le numéro 452 117 294, titulaire de la carte professionnelle CPI3401 2016 000 014 824 (ci-après « l’organisateur »).</p>
    <p>Le concours est gratuit et sans obligation d’achat. Il se déroule sur la page <?= h(JEU_URL) ?>.</p>

    <h2>Article 2. Thème et calendrier</h2>
    <p>Les participants réalisent un dessin sur le thème « <?= h(JEU_THEME) ?> ».</p>
    <ul>
      <li>Dépôt des dessins : de l’ouverture du concours au <?= fr_date(fin_depots()) ?> à 23 h 59 (heure de Paris).</li>
      <li>Votes du public : du <?= fr_date(debut_votes()) ?> au <?= fr_date(fin_votes()) ?> à 23 h 59.</li>
      <li>Annonce des résultats : dans les quinze jours qui suivent la clôture des votes.</li>
    </ul>

    <h2>Article 3. Qui peut participer</h2>
    <p>Le concours est ouvert à toute personne âgée de 3 ans ou plus, résidant en France métropolitaine. Les dirigeants et salariés de l’organisateur, ainsi que les membres de leur famille, peuvent participer dans les mêmes conditions que les autres participants.</p>
    <p><b>Participants mineurs.</b> Le dessin d’un mineur est déposé par un adulte : son parent ou son représentant légal, ou un autre adulte de la famille agissant avec l’accord de ceux-ci. Cet adulte garantit disposer de cet accord, et autorise la publication du dessin, du prénom et de l’âge de l’enfant.</p>
    <p>Chaque participant ne peut déposer qu’un seul dessin. Une même adresse e-mail peut déposer les dessins de plusieurs enfants, dans la limite de <?= JEU_DESSINS_PAR_EMAIL ?>.</p>

    <h2>Article 4. Catégories</h2>
    <p>Les dessins sont classés en quatre catégories, selon l’âge du participant au jour du dépôt : <?= h(implode(' ; ', array_map('mb_strtolower', JEU_CATEGORIES))) ?> (adultes compris).</p>

    <h2>Article 5. Dépôt et publication des dessins</h2>
    <p>Le dessin est une création personnelle et originale du participant, réalisée à la main ou sur écran, sans recours à un générateur d’images. Il est transmis sous la forme d’une photographie, par le formulaire du concours.</p>
    <p>Chaque dessin est examiné par l’organisateur avant sa mise en ligne, en principe sous 12 heures. L’organisateur peut refuser, sans avoir à se justifier, un dessin hors sujet, qui ne serait manifestement pas l’œuvre du participant, qui montrerait un visage, un nom de famille ou une adresse, ou dont le contenu serait injurieux, violent, discriminatoire ou contraire à la loi.</p>
    <p>Seuls le dessin, le prénom et l’âge du participant sont affichés. L’adresse e-mail et le numéro de téléphone ne sont jamais rendus publics.</p>

    <h2>Article 6. Votes</h2>
    <p>Du <?= fr_date(debut_votes()) ?> au <?= fr_date(fin_votes()) ?>, toute personne peut voter pour le dessin de son choix, à raison d’un vote par jour et par adresse e-mail. Il n’est pas possible de voter pour un dessin déposé avec sa propre adresse e-mail.</p>
    <p>Le partage d’un dessin par messagerie ou sur les réseaux sociaux est libre et n’apporte aucun avantage. L’organisateur peut annuler les votes obtenus de façon manifestement frauduleuse (adresses créées en série, automates), et exclure le dessin concerné.</p>

    <h2>Article 7. Lots</h2>
    <p>Deux sortes de lots sont attribuées :</p>
    <ul>
      <li>un lot par catégorie : dans chacune des quatre catégories, le dessin ayant reçu le plus de voix gagne <?= $lot(1) ?> ;</li>
      <li>le prix du jury : l’équipe LOTIER Immobilier choisit un dessin, toutes catégories confondues, qui gagne <?= $lot('jury') ?>. Ce choix est libre et ne dépend pas du nombre de voix. Le dessin choisi peut aussi être celui qui a gagné dans sa catégorie ; dans ce cas, le jury choisit un autre dessin.</li>
    </ul>
    <p>Soit cinq lots au total. En cas d’égalité de voix dans une catégorie, le dessin déposé le premier l’emporte. Les lots ne peuvent être ni échangés, ni remboursés, ni cédés.</p>
    <p>Les gagnants sont prévenus par e-mail, à l’adresse de l’adulte indiquée lors du dépôt. Le lot est envoyé par e-mail ou par courrier postal, au choix de l’organisateur ; dans le second cas, l’adresse postale est demandée au gagnant à cette seule fin. Un lot non réclamé dans les trois mois qui suivent l’annonce des résultats est perdu.</p>

    <h2>Article 8. Droits sur les dessins</h2>
    <p>Le participant, ou l’adulte qui le représente, autorise gratuitement l’organisateur à reproduire et à publier le dessin, accompagné du prénom et de l’âge de son auteur, sur la page du concours, sur le site lotier.immo, dans ses agences, sur ses réseaux sociaux et dans son magazine, pendant la durée du concours et les trois mois qui suivent la clôture des votes. Le participant reste propriétaire de son dessin et peut en demander le retrait à tout moment, y compris pendant le concours, par le <a href="retrait.php">formulaire de retrait</a>.</p>

    <h2 id="donnees">Article 9. Données personnelles</h2>
    <p><b>Responsable du traitement :</b> SARL LOTIER, 40 rue Française, 34500 Béziers, contact@lotier-immobilier.com.</p>
    <ul>
      <li><b>Données collectées pour participer :</b> prénom et âge de l’artiste, photographie du dessin, adresse e-mail de l’adulte. Facultatif : lien avec l’artiste, code postal, projet immobilier, numéro de téléphone si un rappel est demandé.</li>
      <li><b>Données collectées pour voter :</b> adresse e-mail du votant, utilisée uniquement pour limiter les votes à un par jour.</li>
      <li><b>Finalités :</b> organisation du concours, publication des dessins, désignation et information des gagnants, lutte contre la fraude. Envoi à l’adulte déposant d’e-mails de suivi du concours (réception et publication du dessin, ouverture des votes, conseils, résultats), avec un lien de désinscription dans chaque message. Si vous l’avez demandé : rappel par un conseiller, envoi de la lettre d’information.</li>
      <li><b>Destinataires :</b> les seules équipes de LOTIER Immobilier. Les données ne sont ni vendues, ni cédées. Le site est hébergé par Hostinger, dans l’Union européenne.</li>
      <li><b>Durées de conservation :</b> les dessins, les données des participants et les adresses des votants sont supprimés trois mois après la clôture des votes. Les coordonnées des gagnants sont conservées jusqu’à la remise de leur lot, et au plus tard jusqu’à l’expiration du délai de réclamation prévu à l’article 7. Un dessin est supprimé en cours de concours sur simple demande, par le <a href="retrait.php">formulaire de retrait</a>. Les dessins refusés sont supprimés sous trente jours. Les coordonnées des personnes ayant demandé un rappel ou la lettre d’information sont conservées trois ans au plus après le dernier contact.</li>
      <li><b>Sécurité :</b> les photographies sont réenregistrées sans leurs informations cachées (lieu de prise de vue, appareil). L’adresse de connexion n’est conservée que sous une forme chiffrée irréversible, pour limiter les abus.</li>
      <li><b>Vos droits :</b> accès, rectification, effacement, opposition, limitation, retrait du consentement, en écrivant à contact@lotier-immobilier.com. Le retrait d’un dessin se demande par le <a href="retrait.php">formulaire de retrait</a> ; il est effectué sous 72 heures. Vous pouvez adresser une réclamation à la CNIL (cnil.fr).</li>
    </ul>
    <p>Pour le reste, la <a href="../lotier-rgpd/">politique de protection des données</a> de LOTIER Immobilier s’applique.</p>

    <h2>Article 10. Responsabilité</h2>
    <p>L’organisateur peut écourter, prolonger, modifier ou annuler le concours si les circonstances l’exigent ; il en informe les participants sur la page du concours. Il ne peut être tenu responsable d’une interruption du service, d’un défaut de connexion ou de l’impossibilité de joindre un gagnant à l’adresse indiquée.</p>

    <h2>Article 11. Acceptation et litiges</h2>
    <p>La participation vaut acceptation du présent règlement, consultable gratuitement sur cette page pendant toute la durée du concours. Toute réclamation est adressée par écrit à l’organisateur, au plus tard un mois après la clôture des votes. Le règlement est soumis au droit français. Il n’est pas déposé chez un commissaire de justice.</p>
    <p><a class="btn rouge" href="./">Retour au concours</a></p>
  </main>
  <footer class="pied"><p>LOTIER Immobilier, 40 rue Française, 34500 Béziers · 04 67 11 28 31 · <a href="../lotier-rgpd/">Politique de protection des données</a></p></footer>
</body>
</html>
