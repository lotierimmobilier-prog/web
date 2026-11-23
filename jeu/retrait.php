<?php
// Concours de Noël : demande de retrait d'un dessin. La demande arrive dans l'administration, qui la traite.
declare(strict_types=1);
require __DIR__ . '/lib.php';
entetes_page();

$erreur = ''; $envoye = false;
$prenom = ''; $email = ''; $message = '';
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $prenom = mb_substr(trim(preg_replace('/\s+/u', ' ', (string) ($_POST['prenom'] ?? ''))), 0, 30);
    $message = mb_substr(trim((string) ($_POST['message'] ?? '')), 0, 600);
    $e = email_propre((string) ($_POST['email'] ?? ''));
    $email = $e ?? mb_substr(trim((string) ($_POST['email'] ?? '')), 0, 120);
    $jour = maintenant()->format('Y-m-d');
    $q = db()->prepare('SELECT COUNT(*) FROM demandes WHERE ip = ? AND substr(cree_le, 1, 10) = ?'); $q->execute([ip(), $jour]);
    if (($_POST['site'] ?? '') !== '' || !jeton_valide((string) ($_POST['jeton'] ?? ''))) $erreur = 'Le formulaire a expiré. Rechargez la page, puis recommencez.';
    elseif ($prenom === '') $erreur = 'Indiquez le prénom de l’artiste.';
    elseif (!$e) $erreur = 'Indiquez l’adresse e-mail utilisée pour déposer le dessin.';
    elseif ((int) $q->fetchColumn() >= 5) $erreur = 'Trop de demandes aujourd’hui depuis cette connexion. Écrivez-nous à contact@lotier-immobilier.com.';
    else {
        // Le dessin correspondant est recherché, mais la réponse est la même qu'il existe ou non.
        $q = db()->prepare('SELECT id FROM dessins WHERE email = ? AND lower(prenom) = lower(?) ORDER BY id DESC LIMIT 1'); $q->execute([$e, $prenom]);
        $id = $q->fetchColumn();
        db()->prepare('INSERT INTO demandes (dessin_id, prenom, email, message, cree_le, ip) VALUES (?, ?, ?, ?, ?, ?)')
            ->execute([$id === false ? null : (int) $id, $prenom, $e, $message, maintenant()->format('Y-m-d H:i:s'), ip()]);
        journal('demande de retrait', $id === false ? 'sans dessin correspondant' : (string) $id);
        $envoye = true;
    }
}
?><!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
  <title>Retirer un dessin | Concours de Noël LOTIER Immobilier</title>
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  <link rel="stylesheet" href="style.css?v=13">
</head>
<body>
  <header class="haut">
    <a class="logo" href="../" aria-label="LOTIER Immobilier, retour au site"><img src="../assets/lotier-logo-330.png" alt="LOTIER Immobilier" width="165" height="56"></a>
    <nav aria-label="Concours"><a href="./">Le concours</a><a href="reglement.php">Règlement</a></nav>
  </header>
  <main class="bloc reglement">
    <h1>Retirer un dessin du concours</h1>
<?php if ($envoye): ?>
    <p class="avis" role="status">Votre demande est bien arrivée. L’équipe LOTIER la traite sous 72 heures et vous répond à l’adresse indiquée.</p>
    <p><a class="btn rouge" href="./">Retour au concours</a></p>
<?php else: ?>
    <p>Vous avez déposé un dessin et vous souhaitez qu’il ne soit plus affiché&nbsp;? Remplissez ce formulaire&nbsp;: le dessin, les données associées et ses votes sont retirés sous 72 heures, à tout moment du concours.</p>
<?php if ($erreur): ?>    <p class="avis" role="alert"><?= h($erreur) ?></p>
<?php endif; ?>
    <form method="post" action="retrait.php" style="max-width:520px">
      <input type="hidden" name="jeton" value="<?= h(jeton_formulaire()) ?>">
      <p hidden><label for="r-site">Ne pas remplir</label><input id="r-site" name="site" type="text" tabindex="-1" autocomplete="off"></p>
      <p><label for="r-prenom">Prénom de l’artiste</label><input id="r-prenom" name="prenom" type="text" required maxlength="30" value="<?= h($prenom) ?>"></p>
      <p><label for="r-email">Adresse e-mail utilisée pour le dépôt</label><input id="r-email" name="email" type="email" required maxlength="120" autocomplete="email" value="<?= h($email) ?>"></p>
      <p><label for="r-message">Précision (facultatif)</label><textarea id="r-message" name="message" maxlength="600"><?= h($message) ?></textarea></p>
      <p><button class="btn rouge" type="submit">Envoyer la demande</button></p>
    </form>
    <p>Votre adresse sert uniquement à vérifier la demande et à vous répondre. Voir le <a href="reglement.php#donnees">règlement, article 9</a>.</p>
<?php endif; ?>
  </main>
  <footer class="pied"><p>LOTIER Immobilier, 40 rue Française, 34500 Béziers · 04 67 11 28 31 · <a href="../lotier-rgpd/">Politique de protection des données</a></p></footer>
</body>
</html>
