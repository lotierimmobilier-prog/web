<?php
// Reçoit le formulaire de contact et l'envoie par e-mail à l'agence.
// Hébergement PHP avec mail() requis. Réponse : redirection vers la page de contact.
declare(strict_types=1);

const DESTINATAIRE = 'contact@lotier-immobilier.com';
const EXPEDITEUR   = 'no-reply@lotier-immobilier.com'; // doit appartenir au domaine (SPF)
const OBJETS = ['Acheter','Louer','Vendre / estimer mon bien','Gestion locative','Syndic de copropriété','Recrutement : devenir agent','Autre demande'];

function fin(bool $ok): never {
    header('Location: index.html?' . ($ok ? 'envoye=1' : 'erreur=1'), true, 303);
    exit;
}
function nettoie(string $s, int $max): string {
    $s = preg_replace('/[\r\n\t]+/', ' ', $s) ?? '';   // pas de saut de ligne : évite l'injection d'en-têtes
    return mb_substr(trim($s), 0, $max);
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit; }

// Anti-spam : champ piège, délai minimal, limite par adresse IP
if (!empty($_POST['site'])) { fin(true); }                          // robot : on fait semblant
$t = (int)($_POST['t'] ?? 0);
if ($t > 0) { $age = time() - intdiv($t, 1000); if ($age < 3 || $age > 86400) fin(false); }
$cle = sys_get_temp_dir() . '/lotier_contact_' . hash('sha256', $_SERVER['REMOTE_ADDR'] ?? '');
$essais = array_filter(is_file($cle) ? (array)json_decode((string)file_get_contents($cle), true) : [], fn($x) => $x > time() - 3600);
if (count($essais) >= 5) fin(false);

$objet   = (string)($_POST['objet'] ?? '');
$nom     = nettoie((string)($_POST['nom'] ?? ''), 100);
$email   = nettoie((string)($_POST['email'] ?? ''), 150);
$tel     = nettoie((string)($_POST['tel'] ?? ''), 20);
$message = trim(mb_substr((string)($_POST['message'] ?? ''), 0, 3000));

if (!in_array($objet, OBJETS, true) || $nom === '' || mb_strlen($message) < 10
    || !filter_var($email, FILTER_VALIDATE_EMAIL) || empty($_POST['rgpd'])
    || ($tel !== '' && !preg_match('/^[0-9 +().-]{6,20}$/', $tel))) {
    fin(false);
}

$essais[] = time();
@file_put_contents($cle, json_encode(array_values($essais)), LOCK_EX);

$corps = "Nouvelle demande via le site\n\nProjet : $objet\nNom : $nom\nE-mail : $email\nTéléphone : " . ($tel ?: 'non renseigné') . "\n\nMessage :\n$message\n";
$entetes = [
    'From' => 'Site Lotier <' . EXPEDITEUR . '>',
    'Reply-To' => $nom !== '' ? '"' . str_replace('"', '', $nom) . '" <' . $email . '>' : $email,
    'MIME-Version' => '1.0',
    'Content-Type' => 'text/plain; charset=UTF-8',
];
$ok = mail(DESTINATAIRE, '=?UTF-8?B?' . base64_encode("Contact site : $objet") . '?=', $corps, $entetes);
fin($ok);
