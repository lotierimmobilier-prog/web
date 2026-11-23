<?php
// Concours de Noël LOTIER Immobilier : page publique (présentation, dépôt, galerie, votes, partage).
declare(strict_types=1);
require __DIR__ . '/lib.php';
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
    if ($phase !== 'depot') $s .= '<p class="voix"><span data-voix>' . $voix . '</span> ' . ($voix > 1 ? 'votes' : 'vote') . ($phase === 'fini' && $rang >= 1 && $rang <= 3 ? ' · ' . ($rang === 1 ? '1er' : $rang . 'e') . ' prix' : '') . '</p>';
    $s .= '<div class="actions">';
    if ($phase === 'vote') $s .= '<button type="button" class="btn rouge" data-voter>Voter pour ' . h($d['prenom']) . '</button>';
    $s .= '<button type="button" class="btn clair" data-partager>Partager</button></div></div></article>';
    return $s;
}
$titre = $vedette ? 'Le dessin de ' . $vedette['prenom'] . ' | Concours de Noël LOTIER Immobilier' : 'Concours de Noël : dessine la maison du Père Noël | LOTIER Immobilier';
$desc = $vedette ? texte_partage($vedette, $phase) : 'Concours de dessin de Noël de LOTIER Immobilier : dessine la maison du Père Noël, dépose ton dessin avant le ' . jour_mois(fin_depots()) . ' et fais voter tes proches. Gratuit, de 3 à 103 ans.';
$image = $vedette ? JEU_URL . 'partage.php?d=' . $vedette['jeton'] . '&p=' . $phase : JEU_URL . 'partage.jpg?v=1';
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
  <link rel="stylesheet" href="style.css?v=8">
</head>
<body data-votes="<?= h(jour_mois(debut_votes())) ?>">
  <a class="evitement" href="#contenu">Aller au contenu</a>
  <header class="haut">
    <a class="logo" href="../" aria-label="LOTIER Immobilier, retour au site"><img src="../assets/lotier-logo-330.png" alt="LOTIER Immobilier" width="165" height="56"></a>
    <nav aria-label="Concours"><a href="#galerie">Les dessins</a><a href="reglement.php">Règlement</a><a href="../">lotier.immo</a><?php if ($phase === 'depot'): ?><a class="pastille" href="#participer">Participer</a><?php endif; ?></nav>
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
          <div><dt>À gagner</dt><dd>12 bons cadeaux</dd></div>
<?php if ($compte): ?>          <div class="fort"><dt><?= $phase === 'depot' ? 'Il reste' : 'Il reste pour voter' ?></dt><dd><?= $j <= 1 ? 'dernier jour' : $j . ' jours' ?></dd></div>
<?php endif; ?>
        </dl>
      </div>
    </section>

    <div class="defile" aria-hidden="true"><div class="piste"><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>12 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>12 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>12 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i><span>La maison du Père Noël</span><i>✦</i><span>Concours de dessin</span><i>✦</i><span>De 3 à 103 ans</span><i>✦</i><span>Gratuit</span><i>✦</i><span>12 bons cadeaux à gagner</span><i>✦</i><span>Un vote par jour</span><i>✦</i></div></div>

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

    <section class="bloc apparait" aria-labelledby="t-comment">
      <h2 id="t-comment">Comment ça marche&nbsp;?</h2>
      <div class="trois">
        <div><span class="num">1</span><svg class="ico" viewBox="0 0 48 48" aria-hidden="true"><path d="M8 40l4-12L32 8l8 8-20 20z" fill="#f6dfb8" stroke="#8f2530" stroke-width="2.5" stroke-linejoin="round"/><path d="M27 13l8 8M8 40l12-4-8-8z" fill="#8f2530" stroke="#8f2530" stroke-width="2.5" stroke-linejoin="round"/></svg><h3>On dessine</h3><p>Crayons, feutres, peinture, collage&nbsp;: tout est permis, sur une feuille, autour du thème «&nbsp;<?= h(JEU_THEME) ?>&nbsp;».</p></div>
        <div><span class="num">2</span><svg class="ico" viewBox="0 0 48 48" aria-hidden="true"><rect x="6" y="14" width="36" height="26" rx="5" fill="#f6dfb8" stroke="#8f2530" stroke-width="2.5"/><path d="M17 14l3-5h8l3 5" fill="none" stroke="#8f2530" stroke-width="2.5" stroke-linejoin="round"/><circle cx="24" cy="27" r="7" fill="#fff" stroke="#8f2530" stroke-width="2.5"/></svg><h3>Un adulte envoie la photo</h3><p>Papa, maman, tatie, papy ou mamie prend le dessin en photo et le dépose ici. L’équipe LOTIER le publie sous 12&nbsp;heures.</p></div>
        <div><span class="num">3</span><svg class="ico" viewBox="0 0 48 48" aria-hidden="true"><path d="M24 41S7 31 7 19a9 9 0 0 1 17-4 9 9 0 0 1 17 4c0 12-17 22-17 22z" fill="#f6dfb8" stroke="#8f2530" stroke-width="2.5" stroke-linejoin="round"/></svg><h3>On fait voter</h3><p>À partir du 15 décembre, chacun peut voter une fois par jour. Les trois dessins les plus soutenus de chaque catégorie gagnent un bon cadeau culturel.</p></div>
      </div>
      <p class="cats"><?php foreach (JEU_CATEGORIES as $c): ?><span><?= h($c) ?></span><?php endforeach; ?></p>
    </section>

    <section class="bloc apparait" aria-labelledby="t-lots">
      <h2 id="t-lots">À gagner</h2>
      <p class="intro">Dans chacune des quatre catégories, les trois dessins les plus soutenus remportent un bon cadeau culturel : livres, musique, spectacles, loisirs créatifs… Douze gagnants en tout.</p>
      <div class="gagner"><div>
      <div class="lots">
        <div class="lot or"><span class="medaille">1</span><h3>1er prix</h3><p>Bon cadeau culturel</p></div>
        <div class="lot argent"><span class="medaille">2</span><h3>2e prix</h3><p>Bon cadeau culturel</p></div>
        <div class="lot bronze"><span class="medaille">3</span><h3>3e prix</h3><p>Bon cadeau culturel</p></div>
      </div>
      </div>
      <svg class="scene" viewBox="0 0 520 440" role="img" aria-label="Illustration : la maison du Père Noël sous la neige">
        <circle cx="420" cy="78" r="38" fill="#fbe9b7"/><circle cx="436" cy="68" r="34" fill="#7d1f2a" opacity=".55"/>
        <g fill="#fff" opacity=".9"><circle cx="70" cy="60" r="2.5"/><circle cx="150" cy="30" r="2"/><circle cx="250" cy="70" r="2.5"/><circle cx="330" cy="26" r="2"/><circle cx="480" cy="170" r="2"/><circle cx="40" cy="170" r="2"/><circle cx="200" cy="120" r="1.8"/></g>
        <path d="M0 360 Q130 300 260 340 T520 320 V440 H0Z" fill="#f4ece0"/><path d="M0 392 Q160 350 300 384 T520 372 V440 H0Z" fill="#fff"/>
        <g><path d="M70 372 l28-64 28 64z" fill="#1f5c43"/><path d="M78 338 l20-48 20 48z" fill="#27704f"/><path d="M84 306 l14-34 14 34z" fill="#2f8a5f"/><rect x="93" y="372" width="10" height="14" fill="#5b3a22"/><path d="M84 306 l14-34 14 34 q-14-10-28 0z" fill="#fff" opacity=".9"/></g>
        <g><path d="M418 366 l24-56 24 56z" fill="#1f5c43"/><path d="M425 336 l17-42 17 42z" fill="#27704f"/><rect x="437" y="366" width="9" height="13" fill="#5b3a22"/><path d="M425 336 l17-42 17 42 q-17-12-34 0z" fill="#fff" opacity=".9"/></g>
        <rect x="300" y="150" width="34" height="74" fill="#8f2530"/><rect x="294" y="142" width="46" height="14" rx="5" fill="#fff"/>
        <g fill="#fff" opacity=".8" class="fumee"><circle cx="318" cy="118" r="11"/><circle cx="334" cy="92" r="14"/><circle cx="356" cy="62" r="18"/></g>
        <rect x="160" y="226" width="210" height="150" rx="6" fill="#f6dfb8"/>
        <path d="M134 236 L265 132 L396 236Z" fill="#b3323a"/><path d="M134 236 L265 132 L396 236 l-16 0 L265 152 L150 236Z" fill="#fff"/>
        <path d="M150 236 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 20 0 q10 14 10 0z" fill="#fff"/>
        <circle cx="265" cy="196" r="17" fill="#fbe9b7" stroke="#8f2530" stroke-width="4"/><path d="M265 180v32M249 196h32" stroke="#8f2530" stroke-width="3"/>
        <rect x="184" y="262" width="52" height="52" rx="5" fill="#fbe08a" stroke="#8f2530" stroke-width="5"/><path d="M210 262v52M184 288h52" stroke="#8f2530" stroke-width="4"/>
        <rect x="294" y="262" width="52" height="52" rx="5" fill="#fbe08a" stroke="#8f2530" stroke-width="5"/><path d="M320 262v52M294 288h52" stroke="#8f2530" stroke-width="4"/>
        <path d="M242 376 v-58 a23 23 0 0 1 46 0 v58z" fill="#1f5c43"/><circle cx="279" cy="346" r="3.5" fill="#e3c98a"/>
        <circle cx="265" cy="304" r="13" fill="none" stroke="#2f8a5f" stroke-width="6"/><circle cx="265" cy="316" r="4" fill="#b3323a"/>
        <path d="M160 376 h210 v8 H160z" fill="#fff"/>
        <g><rect x="384" y="336" width="6" height="42" fill="#5b3a22"/><rect x="368" y="322" width="64" height="26" rx="4" fill="#fff" stroke="#8f2530" stroke-width="3"/><text x="400" y="340" text-anchor="middle" font-size="12" font-weight="700" fill="#8f2530" font-family="Arial, sans-serif">Père Noël</text></g>
      </svg>
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
        <h3>Merci, le dessin de <span data-merci-prenom></span> est bien arrivé&nbsp;!</h3>
        <p>L’équipe LOTIER le regarde et le publie sous 12&nbsp;heures. En attendant, prévenez la famille&nbsp;: les votes ouvrent le <?= h(jour_mois(debut_votes())) ?>.</p>
        <p class="boutons"><button type="button" class="btn rouge" data-partager-merci>Prévenir mes proches</button><a class="btn clair" href="./">Déposer un autre dessin</a></p>
      </div>
    </section>
<?php endif; ?>

<?php
$faces = [];
foreach ($dessins as $f) $faces[] = ['lien' => '#d-' . $f['jeton'], 'image' => 'image.php?d=' . $f['jeton'] . '&v=1', 'nom' => $f['prenom'] . ', ' . (int) $f['age'] . ' ans' . ($phase !== 'depot' ? ' · ' . (int) $f['voix'] . ((int) $f['voix'] > 1 ? ' votes' : ' vote') : '')];
foreach ($exemples as $f) $faces[] = ['lien' => '#inspiration', 'image' => $f, 'nom' => 'Exemple, hors concours'];
if ($faces): $base = $faces; while (count($faces) < 8) $faces = array_merge($faces, $base); $faces = array_slice($faces, 0, 16); ?>
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
        <tbody><?php foreach ($parCat[$cle] as $i => $d): ?><tr<?= $i < 3 ? ' class="podium"' : '' ?>><td><?= $i + 1 ?></td><td><a href="#d-<?= h($d['jeton']) ?>"><?= h($d['prenom']) ?></a></td><td><?= (int) $d['age'] ?> ans</td><td><b><?= (int) $d['voix'] ?></b></td></tr><?php endforeach; ?></tbody>
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
    <p><a class="cadenas" href="admin.php" rel="nofollow" aria-label="Administration du concours (accès réservé)" title="Administration"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2.2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 11V8a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="16" r="1.4" fill="currentColor"/></svg></a></p>
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
    <p><button type="button" class="btn clair" data-fermer>Fermer</button></p>
  </dialog>

  <script src="app.js?v=5" defer></script>
</body>
</html>
