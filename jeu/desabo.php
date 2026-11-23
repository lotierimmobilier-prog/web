<?php
// Concours de Noël : désinscription des e-mails de suivi, en un clic depuis le lien présent dans chaque message.
declare(strict_types=1);
require __DIR__ . '/lib.php';
require __DIR__ . '/mails.php';
entetes_page();

$jeton = (string) ($_GET['d'] ?? '');
$ok = preg_match('/^[a-f0-9]{16}$/', $jeton) && hash_equals(mails_signature($jeton), (string) ($_GET['s'] ?? ''));
if ($ok) {
    // Tous les dessins déposés avec la même adresse sont concernés.
    $q = db()->prepare('SELECT email FROM dessins WHERE jeton = ?'); $q->execute([$jeton]);
    $email = $q->fetchColumn();
    if ($email !== false) { db()->prepare('UPDATE dessins SET mails = 0 WHERE email = ?')->execute([$email]); journal('e-mails', 'désinscription'); }
}
?><!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
  <title>E-mails du concours | LOTIER Immobilier</title>
  <link rel="icon" type="image/png" href="../assets/favicon.png">
  <link rel="stylesheet" href="style.css?v=12">
</head>
<body>
  <header class="haut">
    <a class="logo" href="../" aria-label="LOTIER Immobilier, retour au site"><img src="../assets/lotier-logo-330.png" alt="LOTIER Immobilier" width="165" height="56"></a>
    <nav aria-label="Concours"><a href="./">Le concours</a><a href="reglement.php">Règlement</a></nav>
  </header>
  <main class="bloc reglement">
<?php if ($ok): ?>
    <h1>C’est noté</h1>
    <p class="avis" role="status">Vous ne recevrez plus les e-mails de suivi du concours. Votre dessin reste en ligne et continue de participer.</p>
    <p>Seul un éventuel message vous annonçant un lot pourra encore vous être adressé.</p>
<?php else: ?>
    <h1>Lien incomplet</h1>
    <p class="avis" role="alert">Ce lien de désinscription n’est pas valide. Écrivez-nous à contact@lotier-immobilier.com, nous nous en occupons.</p>
<?php endif; ?>
    <p><a class="btn rouge" href="./">Retour au concours</a></p>
  </main>
  <footer class="pied"><p>LOTIER Immobilier, 40 rue Française, 34500 Béziers · 04 67 11 28 31 · <a href="../lotier-rgpd/">Politique de protection des données</a></p></footer>
</body>
</html>
