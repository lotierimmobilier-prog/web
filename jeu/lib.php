<?php
// Concours de Noël LOTIER Immobilier : réglages, base de données et outils communs.
// Les données (base SQLite et dessins) sont rangées HORS du dossier public et hors du dépôt Git :
// elles ne sont ni versionnées, ni accessibles par une adresse web, ni touchées par les déploiements.
declare(strict_types=1);
date_default_timezone_set('Europe/Paris');
mb_internal_encoding('UTF-8');

const JEU_NOM = 'Concours de Noël';
const JEU_THEME = 'La maison du Père Noël';
const JEU_URL = 'https://lotier.immo/jeu/';
// Dates officielles. L'administration peut les remplacer (réglage « dates ») pour un essai, puis y revenir.
const JEU_FIN_DEPOTS = '2026-12-14';     // dernier jour des dépôts, jusqu'à 23 h 59
const JEU_FIN_VOTES = '2027-01-06';      // dernier jour des votes, jusqu'à 23 h 59 ; les votes ouvrent le lendemain de la fin des dépôts
const JEU_CATEGORIES = ['3-5' => 'De 3 à 5 ans', '6-8' => 'De 6 à 8 ans', '9-12' => 'De 9 à 12 ans', '13+' => '13 ans et plus'];
const JEU_PROJETS = ['' => 'Aucun projet pour le moment', 'vendre' => 'Vendre un bien', 'acheter' => 'Acheter un bien', 'louer' => 'Trouver une location',
                     'mettre-en-location' => 'Mettre un bien en location', 'estimer' => 'Faire estimer un bien'];
const JEU_VOTES_PAR_IP = 30;          // plafond de sécurité par adresse IP et par jour
const JEU_DEPOTS_PAR_IP = 10;         // dépôts par adresse IP et par jour
const JEU_DESSINS_PAR_EMAIL = 6;      // une famille nombreuse reste possible
const JEU_POIDS_MAX = 12 * 1024 * 1024;
// Valeur des bons cadeaux culturels (euros TTC) pour les 1er, 2e et 3e de chaque catégorie. null = pas encore fixée.
const JEU_LOTS = [1 => null, 'jury' => null];
const JEU_EXEMPLES = 8;              // dessins d'exemple (hors concours) affichés tant qu'il y a moins de N vrais dessins en ligne

function maintenant(): DateTimeImmutable {
    $essai = getenv('JEU_DATE');            // essais en local uniquement (variable d'environnement absente du serveur)
    return new DateTimeImmutable($essai ?: 'now');
}
function phase(): string {
    $n = maintenant()->format('Y-m-d H:i:s');
    if ($n <= fin_depots()) return 'depot';
    if ($n <= fin_votes()) return 'vote';
    return 'fini';
}
function categorie_de(int $age): string {
    if ($age <= 5) return '3-5';
    if ($age <= 8) return '6-8';
    if ($age <= 12) return '9-12';
    return '13+';
}
function h(?string $s): string { return htmlspecialchars((string) $s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

function dossier(): string {
    static $d = null;
    if ($d !== null) return $d;
    $candidats = [];
    if (getenv('JEU_DATA')) $candidats[] = getenv('JEU_DATA');
    $racine = $_SERVER['DOCUMENT_ROOT'] ?? '';
    if ($racine !== '') $candidats[] = dirname(rtrim($racine, '/')) . '/concours-noel-data';
    $candidats[] = __DIR__ . '/data';                     // dernier recours, protégé par .htaccess
    foreach ($candidats as $c) {
        if ((is_dir($c) || @mkdir($c, 0700, true)) && is_writable($c)) {
            if (!is_dir("$c/dessins")) @mkdir("$c/dessins", 0700, true);
            if (!is_file("$c/.htaccess")) @file_put_contents("$c/.htaccess", "Require all denied\nDeny from all\n");
            return $d = $c;
        }
    }
    http_response_code(500);
    exit('Le concours est momentanément indisponible.');
}

function db(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    $pdo = new PDO('sqlite:' . dossier() . '/concours.sqlite', null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);
    @chmod(dossier() . '/concours.sqlite', 0600);
    $pdo->exec('PRAGMA busy_timeout = 5000');
    $pdo->exec('PRAGMA foreign_keys = ON');
    $pdo->exec("CREATE TABLE IF NOT EXISTS dessins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, jeton TEXT NOT NULL UNIQUE, prenom TEXT NOT NULL, age INTEGER NOT NULL, categorie TEXT NOT NULL,
        email TEXT NOT NULL, lien TEXT NOT NULL DEFAULT '', code_postal TEXT NOT NULL DEFAULT '', projet TEXT NOT NULL DEFAULT '',
        rappel INTEGER NOT NULL DEFAULT 0, telephone TEXT NOT NULL DEFAULT '', infolettre INTEGER NOT NULL DEFAULT 0,
        statut TEXT NOT NULL DEFAULT 'attente', cree_le TEXT NOT NULL, traite_le TEXT, ip TEXT NOT NULL DEFAULT '')");
    $pdo->exec("CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, dessin_id INTEGER NOT NULL REFERENCES dessins(id) ON DELETE CASCADE, email TEXT NOT NULL,
        jour TEXT NOT NULL, ip TEXT NOT NULL DEFAULT '', cree_le TEXT NOT NULL, UNIQUE (email, jour))");
    $pdo->exec("CREATE INDEX IF NOT EXISTS votes_dessin ON votes (dessin_id)");
    $pdo->exec("CREATE TABLE IF NOT EXISTS reglages (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL)");
    $pdo->exec("CREATE TABLE IF NOT EXISTS demandes (id INTEGER PRIMARY KEY AUTOINCREMENT, dessin_id INTEGER, prenom TEXT NOT NULL, email TEXT NOT NULL,
        message TEXT NOT NULL DEFAULT '', cree_le TEXT NOT NULL, traite_le TEXT, ip TEXT NOT NULL DEFAULT '')");
    $pdo->exec("CREATE TABLE IF NOT EXISTS envois (dessin_id INTEGER NOT NULL REFERENCES dessins(id) ON DELETE CASCADE, cle TEXT NOT NULL, quand TEXT NOT NULL, ok INTEGER NOT NULL DEFAULT 1, UNIQUE (dessin_id, cle))");
    if (!in_array('mails', array_column($pdo->query('PRAGMA table_info(dessins)')->fetchAll(), 'name'), true)) $pdo->exec('ALTER TABLE dessins ADD COLUMN mails INTEGER NOT NULL DEFAULT 1');
    $pdo->exec("CREATE TABLE IF NOT EXISTS tentatives (ip TEXT NOT NULL, quand INTEGER NOT NULL)");
    $pdo->exec("CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY AUTOINCREMENT, quand TEXT NOT NULL, action TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '')");
    return $pdo;
}
function reglage(string $cle, ?string $valeur = null): ?string {
    if ($valeur !== null) {
        db()->prepare('INSERT INTO reglages (cle, valeur) VALUES (?, ?) ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur')->execute([$cle, $valeur]);
        return $valeur;
    }
    $q = db()->prepare('SELECT valeur FROM reglages WHERE cle = ?'); $q->execute([$cle]);
    $v = $q->fetchColumn();
    return $v === false ? null : (string) $v;
}
// Dates du concours : celles choisies dans l'administration si elles existent et sont cohérentes, sinon les dates officielles.
function dates(): array {
    static $d = null;
    if ($d !== null) return $d;
    $d = ['depots' => JEU_FIN_DEPOTS, 'votes' => JEU_FIN_VOTES, 'essai' => false];
    $r = json_decode((string) reglage('dates'), true);
    $ok = fn($v) => is_string($v) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $v) && checkdate((int) substr($v, 5, 2), (int) substr($v, 8, 2), (int) substr($v, 0, 4));
    if (is_array($r) && $ok($r['depots'] ?? null) && $ok($r['votes'] ?? null) && $r['votes'] > $r['depots']) $d = ['depots' => $r['depots'], 'votes' => $r['votes'], 'essai' => true];
    return $d;
}
function fin_depots(): string { return dates()['depots'] . ' 23:59:59'; }
function debut_votes(): string { return (new DateTimeImmutable(dates()['depots']))->modify('+1 day')->format('Y-m-d') . ' 00:00:00'; }
function fin_votes(): string { return dates()['votes'] . ' 23:59:59'; }
function jour_mois(string $d): string { return preg_replace('/ \d{4}$/', '', fr_date($d)); }      // « 15 décembre »
function jour_court(string $d): string {                                                            // « 15 déc. »
    static $m = [1 => 'janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
    $t = new DateTimeImmutable($d);
    return ($t->format('j') === '1' ? '1er' : $t->format('j')) . ' ' . $m[(int) $t->format('n')];
}
function journal(string $action, string $detail = ''): void {
    db()->prepare('INSERT INTO journal (quand, action, detail) VALUES (?, ?, ?)')->execute([date('Y-m-d H:i:s'), $action, $detail]);
}
function sel(): string {
    $s = reglage('sel');
    return $s ?? reglage('sel', bin2hex(random_bytes(24)));
}
function ip_brute(): string {
    foreach (['HTTP_CF_CONNECTING_IP', 'HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR'] as $k) {
        if (!empty($_SERVER[$k])) {
            $ip = trim(explode(',', (string) $_SERVER[$k])[0]);
            if (filter_var($ip, FILTER_VALIDATE_IP)) return $ip;
        }
    }
    return (string) ($_SERVER['REMOTE_ADDR'] ?? '');
}
// L'adresse IP n'est jamais gardée en clair : seule son empreinte sert aux plafonds de sécurité.
function ip(): string { return substr(hash('sha256', ip_brute() . '|' . sel()), 0, 24); }

function email_propre(string $e): ?string {
    $e = mb_strtolower(trim($e));
    return (mb_strlen($e) <= 120 && filter_var($e, FILTER_VALIDATE_EMAIL)) ? $e : null;
}
function repondre(array $donnees, int $code = 200): never {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($donnees, JSON_UNESCAPED_UNICODE);
    exit;
}
function entetes_page(): void {
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: DENY');
    header('Referrer-Policy: strict-origin-when-cross-origin');
}
// Jeton du formulaire : horodatage signé, pour écarter les envois automatiques (ni cookie, ni traceur).
function jeton_formulaire(): string { $t = (string) time(); return $t . '.' . substr(hash_hmac('sha256', $t, sel()), 0, 20); }
function jeton_valide(string $j): bool {
    [$t, $s] = array_pad(explode('.', $j, 2), 2, '');
    if (!ctype_digit($t) || !hash_equals(substr(hash_hmac('sha256', $t, sel()), 0, 20), $s)) return false;
    $age = time() - (int) $t;
    return $age >= 3 && $age <= 6 * 3600;
}
function chemin_dessin(string $jeton, bool $vignette = false): string { return dossier() . '/dessins/' . $jeton . ($vignette ? '-v' : '') . '.jpg'; }

// Réenregistre la photo reçue : format vérifié, orientation corrigée, métadonnées (dont la position GPS) supprimées.
function enregistrer_image(string $source, string $jeton): bool {
    $info = @getimagesize($source);
    if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true)) return false;
    if ($info[0] < 200 || $info[1] < 200 || $info[0] * $info[1] > 60_000_000) return false;
    $im = match ($info[2]) { IMAGETYPE_JPEG => @imagecreatefromjpeg($source), IMAGETYPE_PNG => @imagecreatefrompng($source), default => @imagecreatefromwebp($source) };
    if (!$im) return false;
    if ($info[2] === IMAGETYPE_JPEG && function_exists('exif_read_data')) {
        $o = (int) ((@exif_read_data($source)['Orientation'] ?? 1));
        $angle = [3 => 180, 6 => -90, 8 => 90][$o] ?? 0;
        if ($angle) { $r = imagerotate($im, $angle, 0); if ($r) { $im = $r; } }
    }
    foreach ([[1600, false, 84], [640, true, 80]] as [$max, $vignette, $qualite]) {
        $l = imagesx($im); $ht = imagesy($im);
        $k = min(1, $max / max($l, $ht));
        $nl = max(1, (int) round($l * $k)); $nh = max(1, (int) round($ht * $k));
        $sortie = imagecreatetruecolor($nl, $nh);
        imagefill($sortie, 0, 0, imagecolorallocate($sortie, 255, 255, 255));
        imagecopyresampled($sortie, $im, 0, 0, 0, 0, $nl, $nh, $l, $ht);
        if (!imagejpeg($sortie, chemin_dessin($jeton, $vignette), $qualite)) return false;
    }
    return true;
}
function dessins_valides(): array {
    return db()->query("SELECT d.id, d.jeton, d.prenom, d.age, d.categorie, d.cree_le, (SELECT COUNT(*) FROM votes v WHERE v.dessin_id = d.id) AS voix
                        FROM dessins d WHERE d.statut = 'valide' ORDER BY voix DESC, d.cree_le ASC")->fetchAll();
}
function fr_date(string $d): string {
    static $mois = [1 => 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
    $t = new DateTimeImmutable($d);
    return ($t->format('j') === '1' ? '1er' : $t->format('j')) . ' ' . $mois[(int) $t->format('n')] . ' ' . $t->format('Y');
}
