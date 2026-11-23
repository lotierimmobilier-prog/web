<?php
// Sert un dessin validé (ou tout dessin pour l'administrateur connecté). Les fichiers ne sont jamais accessibles directement.
declare(strict_types=1);
require __DIR__ . '/lib.php';

$jeton = (string) ($_GET['d'] ?? '');
if (!preg_match('/^[a-f0-9]{16}$/', $jeton)) { http_response_code(404); exit; }
$q = db()->prepare('SELECT statut FROM dessins WHERE jeton = ?'); $q->execute([$jeton]);
$statut = $q->fetchColumn();
$admin = false;
if ($statut !== 'valide' && isset($_COOKIE['concours_admin'])) {
    session_name('concours_admin'); session_start(['cookie_path' => '/jeu/', 'cookie_httponly' => true, 'cookie_samesite' => 'Strict', 'read_and_close' => true]);
    $admin = !empty($_SESSION['admin']);
}
$fichier = chemin_dessin($jeton, isset($_GET['v']));
if (($statut !== 'valide' && !$admin) || $statut === false || !is_file($fichier)) { http_response_code(404); exit; }
header('Content-Type: image/jpeg');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: ' . ($statut === 'valide' ? 'public, max-age=86400' : 'private, no-store'));
header('Content-Length: ' . filesize($fichier));
readfile($fichier);
