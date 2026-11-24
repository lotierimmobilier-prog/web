<?php
// Concours de Noël LOTIER Immobilier : page publique (présentation, dépôt, galerie, votes, partage).
declare(strict_types=1);
require __DIR__ . '/lib.php';
require __DIR__ . '/mails.php';
entetes_page();

$phase = phase();
$dessins = dessins_valides();
// Dessins d'exemple, hors concours : sans prénom, sans âge, sans vote. Ils disparaissent dès qu'il y a assez de vrais dessins, et dès l'ouverture des votes.
$exemples = [];
if (phase() === 'depot' && count($dessins) < JEU_EXEMPLES) foreach (glob(__DIR__ . '/exemples/exemple-*.jpg') ?: [] as $f) $exemples[] = 'exemples/' . basename($f);
sort($exemples, SORT_NATURAL);
$vedette = null;
$jd = (string) ($_GET['d'] ?? '');
if (preg_match('/^[a-f0-9]{16}$/', $jd)) { foreach ($dessins as $x) { if ($x['jeton'] === $jd) { $vedette = $x; break; } } }
$reste = function (string $fin): int { return max(0, (int) ceil(((new DateTimeImmutable($fin))->getTimestamp() - maintenant()->getTimestamp()) / 86400)); };
$j = $phase === 'depot' ? $reste(fin_depots()) : ($phase === 'vote' ? $reste(fin_votes()) : 0);
$compte = $phase === 'depot' ? ($j <= 1 ? 'Dernier jour pour déposer un dessin !' : "Plus que $j jours pour déposer un dessin")
        : ($phase === 'vote' ? ($j <= 1 ? 'Dernier jour pour voter !' : "Plus que $j jours pour voter") : '');
$nbVotes = (int) db()->query('SELECT COUNT(*) FROM votes')->fetchColumn();
$parCat = array_fill_keys(array_keys(JEU_CATEGORIES), []);
foreach ($dessins as $x) { $parCat[$x['categorie']][] = $x; }

function texte_partage(array $d, string $phase): string {
    $p = $d['prenom'];
    if ($phase === 'vote') return "Aidez $p à gagner le concours de Noël de LOTIER Immobilier ! Son dessin de la maison du Père Noël attend votre vote (un vote par jour, jusqu’au " . jour_mois(fin_votes()) . ") :";
    if ($phase === 'depot') return "$p participe au concours de Noël de LOTIER Immobilier ! Venez voir son dessin de la maison du Père Noël. Les votes ouvrent le " . jour_mois(debut_votes()) . " :";
    return "$p a participé au concours de Noël de LOTIER Immobilier. Voici son dessin de la maison du Père Noël :";
}
function carte(array $d, string $phase, int $rang = 0): string {
    $url = JEU_URL . '?d=' . $d['jeton'];
    $voix = (int) $d['voix'];
    $s = '<article class="carte" id="d-' . h($d['jeton']) . '" data-jeton="' . h($d['jeton']) . '" data-prenom="' . h($d['prenom']) . '" data-url="' . h($url) . '" data-texte="' . h(texte_partage($d, $phase)) . '">';
    $s .= '<a class="vue" href="image.php?d=' . h($d['jeton']) . '" target="_blank" rel="noopener"><img src="image.php?d=' . h($d['jeton']) . '&amp;v=1" alt="Dessin de ' . h($d['prenom']) . ', ' . (int) $d['age'] . ' ans : la maison du Père Noël" loading="lazy" width="640" height="480"></a>';
    $s .= '<div class="bas"><p class="qui"><b>' . h($d['prenom']) . '</b>, ' . (int) $d['age'] . ' ans</p>';
    if ($phase !== 'depot') $s .= '<p class="voix"><span data-voix>' . $voix . '</span> ' . ($voix > 1 ? 'votes' : 'vote') . ($phase === 'fini' && $rang === 1 ? ' · gagnant de la catégorie' : '') . ($phase === 'fini' && (int) reglage('jury') === (int) ($d['id'] ?? 0) ? ' · prix du jury' : '') . '</p>';
    $s .= '<div class="actions">';
    if ($phase === 'vote') $s .= '<button type="button" class="btn rouge" data-voter>Voter pour ' . h($d['prenom']) . '</button>';
    $s .= '<button type="button" class="btn clair" data-partager>Partager</button></div></div></article>';
    return $s;
}
$titre = $vedette ? 'Le dessin de ' . $vedette['prenom'] . ' | Concours de Noël LOTIER Immobilier' : 'Concours de Noël : dessine la maison du Père Noël | LOTIER Immobilier';
$desc = $vedette ? texte_partage($vedette, $phase) : 'Concours de dessin de Noël de LOTIER Immobilier : dessine la maison du Père Noël, dépose ton dessin avant le ' . jour_mois(fin_depots()) . ' et fais voter tes proches. Gratuit, de 3 à 103 ans.';
$image = $vedette ? JEU_URL . 'partage.php?d=' . $vedette['jeton'] . '&p=' . $phase . '&v=2' : JEU_URL . 'partage.jpg?v=2';
?><!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= h($titre) ?></title>
  <meta name="description" content="<?= h($desc) ?>">
  <link rel="canonical" href="<?= h(JEU_URL) ?>">
  <meta property="og:type" content="website">
  <meta property="og:title" content="<?= h($titre) ?>">
  <meta property="og:description" content="<?= h($desc) ?>">
  <meta property="og:url" content="<?= h(JEU_URL . ($vedette ? '?d=' . $vedette['jeton'] : '')) ?>">
  <meta property="og:image" content="<?= h($image) ?>">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Concours de Noël LOTIER Immobilier : dessine la maison du Père Noël">
  <meta property="og:locale" content="fr_FR">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  <link rel="stylesheet" href="style.css?v=21">
</head>
<body data-votes="<?= h(jour_mois(debut_votes())) ?>">
  <a class="evitement" href="#contenu">Aller au contenu</a>
  <header class="haut">
    <a class="logo" href="../" aria-label="LOTIER Immobilier, retour au site"><img src="../assets/lotier-logo-330.png" alt="LOTIER Immobilier" width="165" height="56"></a>
    <nav aria-label="Concours"><a href="#galerie">Les dessins</a><a href="reglement.php">Règlement</a><a href="../">lotier.immo</a><?php if ($phase === 'depot'): ?><a class="pastille" href="#participer"><svg class="pn" viewBox="0 0 40 40" width="32" height="32" aria-hidden="true"><circle cx="20" cy="23" r="9" fill="#f3c9a8"/><path d="M9 25c1 8 6 12 11 12s10-4 11-12c-2 3-6 5-11 5s-9-2-11-5z" fill="#fff"/><path d="M13 22c2 2 5 3 7 3s5-1 7-3c0 2-3 6-7 6s-7-4-7-6z" fill="#fff"/><path d="M8 20C8 9 14 3 23 4c3 .4 5 2 6 4-4-1-8 0-11 2 5 0 9 1 11 4z" fill="#c1272f"/><path d="M7 20c3-3 8-5 14-5s10 2 12 5c-1 2-4 3-7 2-4-1-9-1-13 0-3 1-5 0-6-2z" fill="#fff"/><circle cx="31" cy="6" r="3.4" fill="#fff"/><circle cx="16.5" cy="22.5" r="1.1" fill="#14100c"/><circle cx="23.5" cy="22.5" r="1.1" fill="#14100c"/><circle cx="20" cy="25" r="1.6" fill="#e0848a"/></svg><span>Participer</span></a><?php endif; ?></nav>
  </header>

  <main id="contenu">
    <section class="hero">
      <div class="traineau" aria-hidden="true"><img src="traineau.webp" alt="" width="900" height="222" decoding="async"></div>
      <p class="sur"><span class="point" aria-hidden="true"></span>Concours de dessin · gratuit · de 3 à 103 ans</p>
      <h1 aria-label="Dessine la maison du Père Noël"><span class="l1" aria-hidden="true">Dessine la mais<span class="boule" aria-hidden="true"><i></i></span>n</span><span class="l2" aria-hidden="true">du Père N<span class="boule" aria-hidden="true"><i></i></span>ël.</span></h1>
      <div class="hero-bas">
        <p class="chapo">Cheminée qui fume, atelier des lutins, garage à traîneau… À quoi ressemble la maison du Père Noël&nbsp;? Montre-le-nous, et fais voter toute la famille.</p>
        <p class="hero-cta">
<?php if ($phase === 'depot'): ?>
          <a class="btn rouge grand" href="#participer">Déposer un dessin <span aria-hidden="true">→</span></a><a class="lien" href="#galerie">Voir les dessins</a>
<?php elseif ($phase === 'vote'): ?>
          <a class="btn rouge grand" href="#galerie">Voter pour un dessin <span aria-hidden="true">→</span></a><a class="lien" href="reglement.php">Lire le règlement</a>
<?php else: ?>
          <a class="btn rouge grand" href="#galerie">Voir les résultats <span aria-hidden="true">→</span></a><a class="lien" href="reglement.php">Lire le règlement</a>
<?php endif; ?>
        </p>
        <dl class="fiche">
          <div class="tete"><dt>Concours de Noël 2026</dt><dd><?= h(['depot' => 'Dépôts ouverts', 'vote' => 'Votes ouverts', 'fini' => 'Terminé'][$phase]) ?></dd></div>
          <div<?= $phase === 'depot' ? ' class="ici"' : '' ?>><dt>Dépôt des dessins</dt><dd>jusqu’au <?= h(jour_court(fin_depots())) ?></dd></div>
          <div<?= $phase === 'vote' ? ' class="ici"' : '' ?>><dt>Votes, un par jour</dt><dd><?= h(jour_court(debut_votes())) ?> → <?= h(jour_court(fin_votes())) ?></dd></div>
          <div><dt>Catégories d’âge</dt><dd>4</dd></div>
          <div><dt>À gagner</dt><dd>5 bons cadeaux</dd></div>
<?php if ($compte): ?>          <div class="fort"><dt><?= $phase === 'depot' ? 'Il reste' : 'Il reste pour voter' ?></dt><dd><?= $j <= 1 ? 'dernier jour' : $j . ' jours' ?></dd></div>
<?php endif; ?>
        </dl>
      </div>
    </section>

    <div class="defile" aria-hidden="true"><div class="piste"><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>5 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>5 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>5 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>5 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i></div></div>

    <section class="chiffres" aria-label="Le concours en chiffres">
      <div><b data-compte="<?= count($dessins) ?>"><?= count($dessins) ?></b><span><?= count($dessins) > 1 ? 'dessins en ligne' : 'dessin en ligne' ?></span></div>
<?php if ($phase === 'depot'): ?>
      <div><b data-compte="<?= $j ?>"><?= $j ?></b><span><?= $j > 1 ? 'jours pour participer' : 'jour pour participer' ?></span></div>
<?php else: ?>
      <div><b data-compte="<?= $nbVotes ?>"><?= $nbVotes ?></b><span><?= $nbVotes > 1 ? 'votes enregistrés' : 'vote enregistré' ?></span></div>
<?php endif; ?>
      <div><b data-compte="4">4</b><span>catégories d’âge</span></div>
      <div><b data-compte="12">12</b><span>bons cadeaux à gagner</span></div>
    </section>

<?php if ($vedette): ?>
    <section class="bloc vedette" aria-labelledby="t-vedette">
      <h2 id="t-vedette">Le dessin de <?= h($vedette['prenom']) ?></h2>
      <div class="grille une"><?= carte($vedette, $phase) ?></div>
    </section>
<?php endif; ?>

    <section class="bloc apparait message-pn" aria-labelledby="t-message">
      <h2 id="t-message">Le message du Père Noël</h2>
      <div class="video-pn" id="video-pere-noel">
        <video controls playsinline preload="none" poster="pere-noel.jpg" width="960" height="540">
          <source src="pere-noel.mp4?v=3" type="video/mp4">
          <a href="pere-noel.mp4?v=3">Voir la vidéo du Père Noël</a>
        </video>
      </div>
      <p class="petit">«&nbsp;Cette année, j’ai une mission pour vous&nbsp;: dessinez-moi ma maison&nbsp;!&nbsp;» Vidéo de 22 secondes, avec le son. Personnage et voix créés par ordinateur.</p>

      <h3 class="sous-titre-pn">Et le lutin t’explique comment faire</h3>
      <div class="video-pn" id="video-lutin">
        <video controls playsinline preload="none" poster="lutin.jpg" width="960" height="540">
          <source src="lutin.mp4?v=6" type="video/mp4">
          <a href="lutin.mp4?v=6">Voir la vidéo du lutin</a>
        </video>
      </div>
      <p class="petit">Vidéo de 24 secondes, avec le son. Les dates indiquées sont celles du concours. Personnage et voix créés par ordinateur.</p>
    </section>

    <section class="bloc apparait" aria-labelledby="t-comment">
      <p class="kick">Comment ça marche</p>
      <h2 id="t-comment" class="grand-titre">En trois temps.</h2>
      <ol class="etapes">
        <li><span class="n" aria-hidden="true">1</span><div><h3>On dessine</h3><p>Crayons, feutres, peinture, collage&nbsp;: tout est permis, sur une feuille, autour du thème «&nbsp;<?= h(JEU_THEME) ?>&nbsp;».</p></div></li>
        <li><span class="n" aria-hidden="true">2</span><div><h3>Un adulte envoie la photo</h3><p>Papa, maman, tatie, papy ou mamie prend le dessin en photo et le dépose ici. L’équipe LOTIER le publie sous 12&nbsp;heures.</p></div></li>
        <li><span class="n" aria-hidden="true">3</span><div><h3>On fait voter</h3><p>À partir du 15 décembre, chacun peut voter une fois par jour. Le dessin le plus soutenu de chaque catégorie gagne un bon cadeau culturel, et le jury choisit son préféré parmi tous.</p></div></li>
      </ol>
      <p class="cats"><?php foreach (JEU_CATEGORIES as $c): ?><span><?= h($c) ?></span><?php endforeach; ?></p>
    </section>

    <section class="bloc apparait" aria-labelledby="t-lots">
      <p class="kick">À gagner</p>
      <div class="gain">
        <div>
          <h2 id="t-lots" class="cinq-titre"><b aria-hidden="true">5</b><span><span class="sr">5 </span>bons cadeaux<br>culturels</span></h2>
          <p class="intro">Livres, musique, spectacles, loisirs créatifs… Cinq gagnants en tout.</p>
        </div>
        <dl class="gains">
          <div><dt>Dans chaque catégorie</dt><dd>Le dessin le plus voté<b>4 × 1 bon cadeau</b></dd></div>
          <div><dt>Prix du jury</dt><dd>Un dessin choisi par l’équipe LOTIER, toutes catégories<b>1 bon cadeau</b></dd></div>
        </dl>
      </div>
    </section>

<?php if ($phase === 'depot'): ?>
    <section class="bloc apparait" id="participer" aria-labelledby="t-participer">
      <h2 id="t-participer">Déposer un dessin</h2>
      <p class="intro">Avis aux artistes de moins de 18 ans&nbsp;: c’est un adulte qui remplit ce formulaire. Papa, maman, tatie, papy, mamie… peu importe, tant qu’il ou elle est majeur. Le Père Noël vérifie, et il a l’œil.</p>
      <form id="depot" class="formulaire" novalidate>
        <input type="hidden" name="action" value="depot">
        <input type="hidden" name="jeton" value="<?= h(jeton_formulaire()) ?>">
        <p class="piege" aria-hidden="true"><label>Ne pas remplir <input type="text" name="site" tabindex="-1" autocomplete="off"></label></p>
        <fieldset><legend>L’artiste</legend>
          <div class="duo">
            <p><label for="prenom">Prénom de l’artiste</label><input id="prenom" name="prenom" type="text" required maxlength="30" autocomplete="off"></p>
            <p><label for="age">Âge</label><input id="age" name="age" type="number" required min="3" max="110" inputmode="numeric"><small id="cat-auto" aria-live="polite"></small></p>
          </div>
          <p><label for="dessin">Photo du dessin</label><input id="dessin" name="dessin" type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif" required><small>Bien éclairé, cadré sur la feuille, sans visage ni nom de famille visible.</small></p>
          <p id="apercu" hidden><img alt="Aperçu du dessin"></p>
        </fieldset>
        <fieldset><legend>L’adulte qui valide</legend>
          <div class="duo">
            <p><label for="email">Adresse e-mail de l’adulte</label><input id="email" name="email" type="email" required maxlength="120" autocomplete="email"><small>Jamais affichée. Elle sert à vous prévenir en cas de gain.</small></p>
            <p><label for="lien">Vous êtes… <span class="facultatif">(facultatif)</span></label><select id="lien" name="lien"><option value="">Choisir</option><option>Le parent</option><option>Le grand-parent</option><option>La tante ou l’oncle</option><option>Un autre adulte de la famille</option><option>L’artiste (j’ai 18 ans ou plus)</option></select></p>
          </div>
          <p class="case"><input id="adulte" name="adulte" type="checkbox" value="1" required><label for="adulte">Je suis majeur. Si l’artiste a moins de 18 ans, je suis son parent ou son représentant légal, ou je dépose ce dessin avec leur accord. J’autorise LOTIER Immobilier à publier le dessin, le prénom et l’âge de l’artiste sur cette page.</label></p>
          <p class="case"><input id="reglement" name="reglement" type="checkbox" value="1" required><label for="reglement">J’ai lu et j’accepte le <a href="reglement.php" target="_blank" rel="noopener">règlement du concours</a>.</label></p>
          <p class="petit">Vous recevrez par e-mail le suivi du concours (dessin en ligne, ouverture des votes, conseils pour être soutenu). Désinscription en un clic dans chaque message.</p>
        </fieldset>
        <fieldset><legend>Et si on parlait immobilier&nbsp;? <span class="facultatif">(facultatif)</span></legend>
          <div class="duo">
            <p><label for="code_postal">Code postal</label><input id="code_postal" name="code_postal" type="text" inputmode="numeric" maxlength="5" autocomplete="postal-code"></p>
            <p><label for="projet">Un projet immobilier&nbsp;?</label><select id="projet" name="projet"><?php foreach (JEU_PROJETS as $k => $v): ?><option value="<?= h($k) ?>"><?= h($v) ?></option><?php endforeach; ?></select></p>
          </div>
          <p class="case"><input id="rappel" name="rappel" type="checkbox" value="1"><label for="rappel">Je souhaite être rappelé par un conseiller LOTIER.</label></p>
          <p id="bloc-tel" hidden><label for="telephone">Téléphone</label><input id="telephone" name="telephone" type="tel" maxlength="20" autocomplete="tel"></p>
          <p class="case"><input id="infolettre" name="infolettre" type="checkbox" value="1"><label for="infolettre">Je souhaite recevoir la lettre d’information de LOTIER Immobilier (désinscription possible à tout moment).</label></p>
        </fieldset>
        <p class="rgpd">Vos données servent uniquement à gérer le concours, et à vous recontacter si vous l’avez demandé. Elles ne sont ni vendues ni cédées. <a href="reglement.php#donnees">Tout savoir sur vos données</a> · <a href="../lotier-rgpd/">Politique de protection des données</a></p>
        <p class="message" id="msg-depot" role="alert" aria-live="assertive"></p>
        <p><button type="submit" class="btn rouge grand">Envoyer le dessin</button></p>
      </form>
      <div id="merci" class="merci" hidden tabindex="-1">
        <canvas class="confettis" data-confettis aria-hidden="true"></canvas>
        <p class="merci-sur">Dessin bien arrivé</p>
        <h3>Bravo <span data-merci-prenom></span>&nbsp;!<br><em>Le Père Noël a reçu ton dessin.</em></h3>
        <p class="merci-chance">Bonne chance pour le concours&nbsp;: on croise les doigts (et les bois des rennes) pour toi&nbsp;!</p>
        <ol class="merci-etapes">
          <li><b>Sous 12&nbsp;heures</b><span>Les lutins de LOTIER regardent le dessin et le mettent en ligne.</span></li>
          <li><b>Le <?= h(jour_mois(debut_votes())) ?></b><span>Les votes ouvrent&nbsp;: un vote par jour et par adresse e-mail.</span></li>
          <li><b>Dès maintenant</b><span>Préviens la famille et les amis, pour qu’ils soient prêts à voter.</span></li>
        </ol>
        <p class="boutons"><button type="button" class="btn rouge grand" data-partager-merci>Prévenir mes proches</button><a class="btn clair" href="./">Déposer un autre dessin</a></p>
        <p class="avis-google">Vous connaissez LOTIER Immobilier&nbsp;? <a href="https://g.page/r/CRMEk2Rx1mm0EBE/review" target="_blank" rel="noopener">Donnez votre avis sur Google</a>. C’est libre et sans lien avec le concours.</p>
      </div>
    </section>
<?php endif; ?>

<?php
$faces = [];
foreach ($dessins as $f) $faces[] = ['lien' => '#d-' . $f['jeton'], 'image' => 'image.php?d=' . $f['jeton'] . '&v=1', 'nom' => $f['prenom'] . ', ' . (int) $f['age'] . ' ans' . ($phase !== 'depot' ? ' · ' . (int) $f['voix'] . ((int) $f['voix'] > 1 ? ' votes' : ' vote') : '')];
foreach ($exemples as $f) $faces[] = ['lien' => '#inspiration', 'image' => $f, 'nom' => 'Exemple, hors concours'];
if ($faces): $base = $faces; while (count($faces) < 4) $faces = array_merge($faces, $base);   // on ne répète les dessins que s’il y en a moins de quatre $faces = array_slice($faces, 0, 16); ?>
    <section class="ronde" aria-labelledby="t-ronde">
      <p class="sur"><span class="point" aria-hidden="true"></span>La galerie</p>
      <h2 id="t-ronde">La ronde <em>des dessins.</em></h2>
      <div class="manege" data-manege aria-label="Carrousel des dessins : faites glisser pour le faire tourner">
        <div class="incline"><div class="anneau">
<?php foreach ($faces as $f): ?>
          <a class="face" href="<?= h($f['lien']) ?>" draggable="false"><span class="recto" style="background-image:url(<?= h($f['image']) ?>)"></span><span class="verso" style="background-image:url(<?= h($f['image']) ?>)" aria-hidden="true"></span><span class="nom"><?= h($f['nom']) ?></span></a>
<?php endforeach; ?>
        </div></div>
      </div>
      <p class="aide">Faites glisser pour faire tourner · touchez un dessin pour le voir</p>
    </section>
<?php endif; ?>

    <section class="bloc apparait" id="galerie" aria-labelledby="t-galerie">
      <h2 id="t-galerie"><?= $phase === 'fini' ? 'Les résultats' : 'Les dessins' ?></h2>
<?php if ($phase === 'depot'): ?>
      <p class="intro">Les votes ouvrent le <?= h(jour_mois(debut_votes())) ?>. D’ici là, admirez, et partagez vos préférés.</p>
<?php elseif ($phase === 'vote'): ?>
      <p class="intro">Un vote par jour et par adresse e-mail, jusqu’au <?= h(jour_mois(fin_votes())) ?>. Revenez demain pour voter à nouveau.</p>
<?php else: ?>
      <p class="intro">Les votes sont clos. Bravo à tous les artistes&nbsp;! Les gagnants sont prévenus par e-mail.</p>
<?php endif; ?>
<?php if (!$dessins): ?>
      <p class="vide">Les premiers dessins arrivent… Le vôtre sera peut-être le premier&nbsp;!</p>
<?php else: foreach (JEU_CATEGORIES as $cle => $nom): if (!$parCat[$cle]) continue; ?>
      <h3 class="cat"><?= h($nom) ?> <span>(<?= count($parCat[$cle]) ?>)</span></h3>
<?php if ($phase !== 'depot'): ?>
      <table class="classement"><caption>Classement, <?= h(mb_strtolower($nom)) ?></caption>
        <thead><tr><th scope="col">Rang</th><th scope="col">Prénom</th><th scope="col">Âge</th><th scope="col">Votes</th></tr></thead>
        <tbody><?php foreach ($parCat[$cle] as $i => $d): ?><tr<?= $i < 1 ? ' class="podium"' : '' ?>><td><?= $i + 1 ?></td><td><a href="#d-<?= h($d['jeton']) ?>"><?= h($d['prenom']) ?></a></td><td><?= (int) $d['age'] ?> ans</td><td><b><?= (int) $d['voix'] ?></b></td></tr><?php endforeach; ?></tbody>
      </table>
<?php endif; ?>
      <div class="grille"><?php foreach ($parCat[$cle] as $i => $d) echo carte($d, $phase, $i + 1); ?></div>
<?php endforeach; endif; ?>
<?php if ($exemples): ?>
      <div class="inspiration" id="inspiration">
        <h3 class="cat">Pour s’inspirer <span>(exemples, hors concours)</span></h3>
        <p class="intro">En panne d’idée&nbsp;? Voici quelques illustrations d’exemple préparées par LOTIER Immobilier. Elles ne participent pas au concours et ne reçoivent aucun vote&nbsp;: elles laisseront la place aux vrais dessins au fil des dépôts.</p>
        <div class="grille"><?php foreach ($exemples as $f): ?><figure class="carte exemple"><span class="vue"><img src="<?= h($f) ?>" alt="Illustration d’exemple, hors concours : la maison du Père Noël" loading="lazy" width="960" height="540"></span><figcaption class="bas"><p class="etiquette">Exemple, hors concours</p></figcaption></figure><?php endforeach; ?></div>
      </div>
<?php endif; ?>
    </section>
  </main>

  <section class="final">
    <svg class="ruban" viewBox="0 0 1440 320" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="or" x1="0" x2="1"><stop offset="0" stop-color="#8a6a14"/><stop offset=".3" stop-color="#f3dfae"/><stop offset=".55" stop-color="#c79a3a"/><stop offset=".8" stop-color="#f7e9c3"/><stop offset="1" stop-color="#8a6a14"/></linearGradient></defs>
      <path class="r1" d="M0 210 C180 120 300 300 480 220 S760 110 940 210 1240 300 1440 180 V320 H0Z" fill="url(#or)" opacity=".95"/>
      <path class="r2" d="M0 250 C200 190 320 320 520 260 S800 180 980 250 1260 320 1440 230 V320 H0Z" fill="#fbf6ee"/>
    </svg>
    <div class="final-in">
      <p class="sur"><span class="point" aria-hidden="true"></span><?= $phase === 'depot' ? 'À vos crayons' : ($phase === 'vote' ? 'À vos votes' : 'Merci à tous') ?></p>
      <h2><?= $phase === 'depot' ? 'À toi de jouer.<br><em>Le Père Noël attend.</em>' : ($phase === 'vote' ? 'Un vote par jour.<br><em>Chaque voix compte.</em>' : 'Bravo aux artistes.<br><em>À l’année prochaine.</em>') ?></h2>
      <p class="boutons"><a class="btn or grand" href="<?= $phase === 'depot' ? '#participer' : '#galerie' ?>"><?= $phase === 'depot' ? 'Déposer un dessin' : ($phase === 'vote' ? 'Voter maintenant' : 'Voir les résultats') ?> <span aria-hidden="true">→</span></a></p>
    </div>
  </section>

  <footer class="pied">
    <p><a href="reglement.php">Règlement du concours</a> · <a href="reglement.php#donnees">Vos données personnelles</a> · <a href="../lotier-rgpd/">Politique de protection des données</a> · <a href="../">lotier.immo</a></p>
    <p>Jeu gratuit et sans obligation d’achat, organisé par LOTIER Immobilier, 40 rue Française, 34500 Béziers. 04 67 11 28 31.</p>
    <p><a href="retrait.php">Retirer un dessin</a> · <a class="cadenas" href="admin.php" rel="nofollow" aria-label="Administration du concours (accès réservé)" title="Administration"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2.2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 11V8a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="16" r="1.4" fill="currentColor"/></svg></a></p>
  </footer>

  <dialog id="dlg-vote" aria-labelledby="t-vote">
    <form id="vote" method="dialog" novalidate>
      <h2 id="t-vote">Voter pour <span data-vote-prenom></span></h2>
      <p>Un vote par jour et par adresse e-mail. Votre adresse sert uniquement à compter votre vote&nbsp;: elle n’est ni affichée, ni utilisée pour vous écrire.</p>
      <p class="piege" aria-hidden="true"><label>Ne pas remplir <input type="text" name="site" tabindex="-1" autocomplete="off"></label></p>
      <p><label for="vote-email">Votre adresse e-mail</label><input id="vote-email" name="email" type="email" required maxlength="120" autocomplete="email"></p>
      <p class="message" id="msg-vote" role="alert" aria-live="assertive"></p>
      <p class="boutons"><button type="submit" class="btn rouge">Valider mon vote</button><button type="button" class="btn clair" data-fermer>Annuler</button></p>
    </form>
  </dialog>

  <dialog id="dlg-partage" aria-labelledby="t-partage">
    <h2 id="t-partage">Partager le dessin de <span data-partage-prenom></span></h2>
    <p><label for="partage-texte">Votre message (modifiable)</label><textarea id="partage-texte" rows="4"></textarea></p>
    <p class="reseaux"><a class="btn rouge" data-r="whatsapp" target="_blank" rel="noopener">WhatsApp</a><a class="btn rouge" data-r="facebook" target="_blank" rel="noopener">Facebook</a><a class="btn rouge" data-r="email">E-mail</a><a class="btn rouge" data-r="sms">SMS</a><button type="button" class="btn clair" data-r="copier">Copier le message</button><button type="button" class="btn clair" data-r="natif" hidden>Autre application</button></p>
    <p class="message" id="msg-partage" aria-live="polite"></p>
    <p class="avis-google">Vous connaissez LOTIER Immobilier&nbsp;? <a href="https://g.page/r/CRMEk2Rx1mm0EBE/review" target="_blank" rel="noopener">Donnez votre avis sur Google</a>. C’est libre et sans lien avec le concours.</p>
    <p><button type="button" class="btn clair" data-fermer>Fermer</button></p>
  </dialog>

  <script src="app.js?v=10" defer></script>
</body>
</html>
<?php
if (mails_actifs()) { if (function_exists('fastcgi_finish_request')) fastcgi_finish_request(); try { mails_tournee(); } catch (Throwable $e) { journal('e-mails', 'erreur : ' . mb_substr($e->getMessage(), 0, 120)); } }

