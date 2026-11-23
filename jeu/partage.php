<?php
// Image d'aperçu pour le partage d'un dessin (Facebook, WhatsApp…) : le dessin encadré, le prénom, l'âge et l'appel au vote.
declare(strict_types=1);
require __DIR__ . '/lib.php';

$jeton = (string) ($_GET['d'] ?? '');
if (!preg_match('/^[a-f0-9]{16}$/', $jeton)) { http_response_code(404); exit; }
$q = db()->prepare("SELECT prenom, age FROM dessins WHERE jeton = ? AND statut = 'valide'"); $q->execute([$jeton]);
$d = $q->fetch();
$fichier = chemin_dessin($jeton);
if (!$d || !is_file($fichier)) { http_response_code(404); exit; }
$police = __DIR__ . '/police-700.ttf';
$fond = @imagecreatefromjpeg(__DIR__ . '/partage-fond.jpg');
$dessin = @imagecreatefromjpeg($fichier);
if (!$fond || !$dessin || !function_exists('imagettftext') || !is_file($police)) { header('Location: image.php?d=' . $jeton, true, 302); exit; }   // à défaut, le dessin seul

// Le dessin, entier, dans un cadre blanc centré sur la zone de gauche (680 × 470 à partir de 44, 40).
$l = imagesx($dessin); $h = imagesy($dessin);
$k = min(628 / $l, 418 / $h); $nl = (int) round($l * $k); $nh = (int) round($h * $k);
$x = 44 + (int) ((680 - $nl) / 2); $y = 40 + (int) ((470 - $nh) / 2);
imagealphablending($fond, true);
for ($i = 9; $i >= 1; $i--) imagefilledrectangle($fond, $x - 10 - $i, $y - 10 - $i + 6, $x + $nl + 9 + $i, $y + $nh + 9 + $i + 6, imagecolorallocatealpha($fond, 20, 16, 12, 123));
imagefilledrectangle($fond, $x - 10, $y - 10, $x + $nl + 9, $y + $nh + 9, imagecolorallocate($fond, 255, 255, 255));
imagecopyresampled($fond, $dessin, $x, $y, 0, 0, $nl, $nh, $l, $h);

// Le texte, à droite.
$phase = phase();
$gris = imagecolorallocate($fond, 74, 66, 56); $noir = imagecolorallocate($fond, 20, 16, 12); $rouge = imagecolorallocate($fond, 143, 37, 48);
$haut = $phase === 'vote' ? 'Votez pour' : ($phase === 'depot' ? 'Le dessin de' : 'Bravo à');
$bas = $phase === 'vote' ? 'Un vote par jour, jusqu’au ' . jour_mois(fin_votes()) : ($phase === 'depot' ? 'Votes à partir du ' . jour_mois(debut_votes()) : 'Merci pour vos votes !');
$ajuste = function (string $t, int $max, int $min, int $large = 400) use ($police): int {          // plus grande taille qui tient dans la largeur
    for ($c = $max; $c > $min; $c -= 2) { $b = imagettfbbox($c, 0, $police, $t); if (abs($b[2] - $b[0]) <= $large) return $c; }
    return $min;
};
$prenom = mb_strimwidth((string) $d['prenom'], 0, 20, '…');
$taille = $ajuste($prenom, 74, 22);
imagettftext($fond, 26, 0, 764, 178, $gris, $police, $haut);
imagettftext($fond, $taille, 0, 761, 178 + 24 + $taille, $noir, $police, $prenom);
imagettftext($fond, 30, 0, 764, 178 + 24 + $taille + 52, $rouge, $police, (int) $d['age'] . ' ans');
imagettftext($fond, $ajuste($bas, 17, 11), 0, 764, 178 + 24 + $taille + 90, $gris, $police, $bas);

// Le bandeau du bas : l'appel à voter, à partager, et à participer tant que les dépôts sont ouverts.
$p = mb_strimwidth((string) $d['prenom'], 0, 16, '…');
[$l1, $l2] = $phase === 'vote' ? ["Votez et partagez pour aider $p !", 'Un vote par jour, gratuit, en deux clics']
           : ($phase === 'depot' ? ["Partagez ce dessin pour aider $p !", 'Envie de jouer aussi ? Déposez votre dessin avant le ' . jour_mois(fin_depots())]
           : ['Merci pour vos votes et vos partages !', 'Rendez-vous l’année prochaine']);
imagefilledrectangle($fond, 0, 545, 850, 629, imagecolorat($fond, 20, 600));
imagettftext($fond, $ajuste($l1, 22, 14, 780), 0, 48, 582, imagecolorallocate($fond, 255, 255, 255), $police, $l1);
imagettftext($fond, $ajuste($l2, 15, 10, 780), 0, 48, 611, imagecolorallocate($fond, 243, 223, 174), $police, $l2);

header('Content-Type: image/jpeg');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: public, max-age=3600');
imagejpeg($fond, null, 86);
