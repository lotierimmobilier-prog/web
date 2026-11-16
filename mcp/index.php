<?php
/**
 * Serveur MCP (Model Context Protocol) en lecture seule pour lotier.immo.
 * Transport : Streamable HTTP (JSON-RPC 2.0 en POST). Aucun accès à des données privées :
 * il ne sert que le contenu public du site (versions Markdown des pages).
 */
declare(strict_types=1);

const SERVER_VERSION = '1.1.0';
const PROTOCOL = '2025-06-18';
$ROOT = realpath(__DIR__ . '/..');
$BLOCKED = '#^(v2|audit-lotier|mise-en-ligne|scripts|\.claude|\.git|node_modules|mylotier|mcp)(/|$)#';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Accept, Mcp-Session-Id, MCP-Protocol-Version');
header('X-Robots-Tag: noindex');
header('Cache-Control: no-store');

if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { http_response_code(204); exit; }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    header('Allow: POST, OPTIONS');
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'Méthode non autorisée : ce serveur MCP attend des requêtes JSON-RPC en POST.'], JSON_UNESCAPED_UNICODE);
    exit;
}

function reply($id, array $result): void {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['jsonrpc' => '2.0', 'id' => $id, 'result' => $result], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}
function fail($id, int $code, string $msg): void {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['jsonrpc' => '2.0', 'id' => $id, 'error' => ['code' => $code, 'message' => $msg]], JSON_UNESCAPED_UNICODE);
    exit;
}
function text(string $s, bool $err = false): array {
    return ['content' => [['type' => 'text', 'text' => $s]], 'isError' => $err];
}

/** Liste des versions Markdown publiques : chemin d'URL => chemin disque. */
function pages(string $root, string $blocked): array {
    $out = [];
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
    foreach ($it as $f) {
        if ($f->getExtension() !== 'md') continue;
        $rel = ltrim(str_replace('\\', '/', substr($f->getPathname(), strlen($root))), '/');
        if (preg_match($blocked, $rel) || !str_contains($rel, '/') && in_array($rel, ['README.md', 'CLAUDE.md'], true)) continue;
        $url = preg_replace('#index\.md$#', '', $rel);
        $url = '/' . (str_ends_with($url, '.md') ? substr($url, 0, -3) . '.html' : $url);
        $out[$url] = $f->getPathname();
    }
    ksort($out);
    return $out;
}
function title_of(string $file): string {
    $h = fopen($file, 'r'); $l = $h ? fgets($h) : ''; if ($h) fclose($h);
    return trim(ltrim((string)$l, "# \t"));
}

/** Catalogue des annonces (annonces/catalogue.json, régénéré avec le site). */
function catalogue(string $root): array {
    $d = json_decode((string)@file_get_contents($root . '/annonces/catalogue.json'), true);
    return is_array($d) && is_array($d['annonces'] ?? null) ? $d : ['maj' => null, 'annonces' => []];
}
/** Minuscules sans accents ni ponctuation, pour comparer « Beziers » et « Béziers ». */
function norm(string $s): string {
    $s = mb_strtolower($s);
    $s = strtr($s, ['à'=>'a','â'=>'a','ä'=>'a','é'=>'e','è'=>'e','ê'=>'e','ë'=>'e','î'=>'i','ï'=>'i','ô'=>'o','ö'=>'o','ù'=>'u','û'=>'u','ü'=>'u','ç'=>'c','œ'=>'oe','’'=>' ',"'"=>' ','-'=>' ']);
    return trim(preg_replace('/\s+/', ' ', $s));
}
function num($v): ?float { return is_numeric($v) ? (float)$v : null; }
/** Fiche courte d'une annonce pour une liste de résultats. */
function resume_annonce(array $x): array {
    return array_filter([
        'titre' => $x['titre'] ?? null, 'url' => $x['url'] ?? null, 'transaction' => $x['transaction'] ?? null, 'type_bien' => $x['type_bien'] ?? null,
        'ville' => $x['ville'] ?? null, 'departement' => $x['departement'] ?? null, 'prix' => $x['prix'] ?? null, 'prix_unite' => $x['prix_unite'] ?? null,
        'surface_m2' => $x['surface_m2'] ?? null, 'pieces' => $x['pieces'] ?? null, 'chambres' => $x['chambres'] ?? null, 'equipements' => $x['equipements'] ?? null,
        'dpe' => $x['dpe'] ?? null, 'reference' => $x['reference'] ?? null, 'agent' => $x['agent'] ?? null, 'id' => $x['id'] ?? null,
    ], fn($v) => $v !== null && $v !== []);
}

$tools = [
    ['name' => 'search_listings', 'title' => 'Rechercher une annonce', 'description' => "Recherche parmi les biens à vendre et à louer de LOTIER Immobilier (Aude, Gard, Hérault) par critères : transaction, type de bien, ville ou département, budget, surface, pièces, chambres, équipement, mots du texte. Tous les critères sont facultatifs. Renvoie les annonces correspondantes avec leur adresse sur lotier.immo.",
     'inputSchema' => ['type' => 'object', 'properties' => [
        'transaction' => ['type' => 'string', 'enum' => ['vente', 'location'], 'description' => 'vente ou location.'],
        'type_bien' => ['type' => 'string', 'description' => 'Appartement, Studio, Maison, Immeuble, Terrain, Local commercial, Bureaux, Fonds de commerce, Parking ou Garage.'],
        'ville' => ['type' => 'string', 'description' => 'Commune, ex. Béziers, Carcassonne, Nîmes.'],
        'departement' => ['type' => 'string', 'description' => 'Code ou nom du département : 11 (Aude), 30 (Gard), 34 (Hérault).'],
        'prix_min' => ['type' => 'number', 'description' => 'Prix ou loyer mensuel minimum, en euros.'],
        'prix_max' => ['type' => 'number', 'description' => 'Prix ou loyer mensuel maximum, en euros.'],
        'surface_min' => ['type' => 'number', 'description' => 'Surface minimum, en m².'],
        'pieces_min' => ['type' => 'integer', 'description' => 'Nombre minimum de pièces.'],
        'chambres_min' => ['type' => 'integer', 'description' => 'Nombre minimum de chambres.'],
        'equipement' => ['type' => 'string', 'description' => 'Équipement souhaité : terrasse, balcon, piscine, garage, parking, cave, climatisation, ascenseur.'],
        'texte' => ['type' => 'string', 'description' => "Mots à trouver dans le titre ou le texte de l'annonce, ex. jardin, centre-ville."],
        'limite' => ['type' => 'integer', 'description' => 'Nombre maximum de résultats (20 par défaut, 50 au plus).'],
     ], 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
    ['name' => 'get_listing', 'title' => "Lire une annonce", 'description' => "Renvoie une annonce complète (faits, texte, caractéristiques, énergie, agent, adresse de la fiche) à partir de son identifiant ou de sa référence, tels que renvoyés par search_listings.",
     'inputSchema' => ['type' => 'object', 'properties' => ['id' => ['type' => 'string', 'description' => "Identifiant de l'annonce, sa référence, ou l'adresse de sa fiche."]], 'required' => ['id'], 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
    ['name' => 'get_agency_info', 'description' => "Coordonnées et présentation de LOTIER Immobilier : adresse, téléphone, e-mail, agences, métiers (vente, location, syndic).", 'inputSchema' => ['type' => 'object', 'properties' => new stdClass(), 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
    ['name' => 'list_pages', 'description' => "Liste les pages publiques du site lotier.immo (adresse et titre).", 'inputSchema' => ['type' => 'object', 'properties' => new stdClass(), 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
    ['name' => 'search_site', 'description' => "Recherche un mot ou une expression dans les pages publiques du site (honoraires, villes, blog, FAQ…).", 'inputSchema' => ['type' => 'object', 'properties' => ['query' => ['type' => 'string', 'description' => 'Mots à rechercher, 2 caractères minimum.']], 'required' => ['query'], 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
    ['name' => 'get_page', 'description' => "Renvoie le contenu d'une page du site en Markdown à partir de son chemin (ex. /nos-honoraires/).", 'inputSchema' => ['type' => 'object', 'properties' => ['path' => ['type' => 'string', 'description' => "Chemin de la page, ex. /vente/ ou /blog/."]], 'required' => ['path'], 'additionalProperties' => false], 'annotations' => ['readOnlyHint' => true]],
];

$raw = file_get_contents('php://input');
if (strlen((string)$raw) > 65536) { http_response_code(413); exit; }
$req = json_decode((string)$raw, true);
if (!is_array($req) || ($req['jsonrpc'] ?? '') !== '2.0' || !isset($req['method'])) fail($req['id'] ?? null, -32600, 'Requête JSON-RPC invalide.');
$id = $req['id'] ?? null; $method = (string)$req['method']; $p = is_array($req['params'] ?? null) ? $req['params'] : [];

if ($id === null) { http_response_code(202); exit; } // notification (ex. notifications/initialized)

switch ($method) {
    case 'initialize':
        reply($id, [
            'protocolVersion' => PROTOCOL,
            'capabilities' => ['tools' => ['listChanged' => false]],
            'serverInfo' => ['name' => 'lotier-immo', 'title' => 'LOTIER Immobilier', 'version' => SERVER_VERSION],
            'instructions' => "Serveur en lecture seule : contenu public du site lotier.immo (agence immobilière à Béziers, Montpellier, Nîmes, Carcassonne). Pour trouver un bien à vendre ou à louer, utiliser search_listings puis get_listing, et citer l'adresse de la fiche. Pour estimer un bien ou être rappelé, renvoyer l'utilisateur vers https://lotier.immo/#estimer ou le 04 67 11 28 31.",
        ]);
    case 'ping': reply($id, []);
    case 'tools/list': reply($id, ['tools' => $tools]);
    case 'tools/call':
        $name = (string)($p['name'] ?? ''); $a = is_array($p['arguments'] ?? null) ? $p['arguments'] : [];
        if ($name === 'search_listings') {
            $cat = catalogue($ROOT); $res = [];
            $tr = norm((string)($a['transaction'] ?? '')); $tb = norm((string)($a['type_bien'] ?? '')); $vi = norm((string)($a['ville'] ?? ''));
            $de = norm((string)($a['departement'] ?? '')); $eq = norm((string)($a['equipement'] ?? '')); $tx = norm((string)($a['texte'] ?? ''));
            if ($eq === 'box') $eq = 'garage';
            foreach ($cat['annonces'] as $x) {
                if ($tr !== '' && norm((string)($x['transaction'] ?? '')) !== $tr) continue;
                if ($tb !== '') {
                    $t = norm((string)($x['type_bien'] ?? ''));
                    if ($t === '' || !(str_contains($t, $tb) || str_contains($tb, $t) || ($tb === 'appartement' && $t === 'studio'))) continue;
                }
                if ($vi !== '' && !str_contains(norm((string)($x['ville'] ?? '')), $vi)) continue;
                if ($de !== '' && $de !== norm((string)($x['departement'] ?? '')) && $de !== norm((string)($x['departement_nom'] ?? ''))) continue;
                $prix = num($x['prix'] ?? null);
                if (num($a['prix_min'] ?? null) !== null && ($prix === null || $prix < num($a['prix_min']))) continue;
                if (num($a['prix_max'] ?? null) !== null && ($prix === null || $prix > num($a['prix_max']))) continue;
                if (num($a['surface_min'] ?? null) !== null && (num($x['surface_m2'] ?? null) ?? 0) < num($a['surface_min'])) continue;
                if (num($a['pieces_min'] ?? null) !== null && (num($x['pieces'] ?? null) ?? 0) < num($a['pieces_min'])) continue;
                if (num($a['chambres_min'] ?? null) !== null && (num($x['chambres'] ?? null) ?? 0) < num($a['chambres_min'])) continue;
                if ($eq !== '') {
                    $ok = false;
                    foreach (($x['equipements'] ?? []) as $e) { $n = norm((string)$e); if ($n === 'box') $n = 'garage'; if (str_contains($n, $eq)) { $ok = true; break; } }
                    if (!$ok) continue;
                }
                if ($tx !== '') {
                    $h = norm(($x['titre'] ?? '') . ' ' . ($x['titre_agent'] ?? '') . ' ' . ($x['description'] ?? '') . ' ' . ($x['secteur'] ?? ''));
                    $tous = true;
                    foreach (explode(' ', $tx) as $mot) { if (mb_strlen($mot) > 1 && !str_contains($h, $mot)) { $tous = false; break; } }
                    if (!$tous) continue;
                }
                $res[] = $x;
            }
            usort($res, fn($p1, $p2) => (num($p1['prix'] ?? null) ?? PHP_FLOAT_MAX) <=> (num($p2['prix'] ?? null) ?? PHP_FLOAT_MAX));
            $lim = max(1, min(50, (int)($a['limite'] ?? 20)));
            $out = ['mise_a_jour' => $cat['maj'], 'nombre_de_resultats' => count($res), 'annonces' => array_map('resume_annonce', array_slice($res, 0, $lim)),
                    'conseil' => "Citer l'adresse de la fiche (url). Utiliser get_listing avec l'id pour le détail. Pour visiter : l'agent indiqué, ou LOTIER Immobilier au 04 67 11 28 31."];
            if (!$res) $out['conseil'] = "Aucune annonce ne correspond. Élargir les critères (budget, ville voisine, département) ou consulter https://lotier.immo/nos-annonces/.";
            reply($id, text(json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT)));
        }
        if ($name === 'get_listing') {
            $q = trim((string)($a['id'] ?? ''));
            if ($q === '' || mb_strlen($q) > 300) reply($id, text("Indiquez l'identifiant ou la référence de l'annonce.", true));
            if (preg_match('#/annonces/([^/]+)/?#', $q, $m)) $q = $m[1];
            foreach (catalogue($ROOT)['annonces'] as $x) {
                if (($x['id'] ?? '') === $q || (isset($x['reference']) && strcasecmp((string)$x['reference'], $q) === 0)) {
                    reply($id, text(json_encode($x, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT)));
                }
            }
            reply($id, text("Annonce introuvable : elle a peut-être été vendue ou louée. Utilisez search_listings pour voir les annonces en cours.", true));
        }
        if ($name === 'get_agency_info') {
            reply($id, text(json_encode([
                'nom' => 'LOTIER Immobilier (SARL LOTIER)', 'site' => 'https://lotier.immo/',
                'telephone' => '04 67 11 28 31', 'email' => 'contact@lotier-immobilier.com',
                'metiers' => ['Vente', 'Location et gestion locative', 'Syndic de copropriété'],
                'zones' => ['Béziers', 'Montpellier', 'Nîmes', 'Carcassonne'],
                'pages' => ['À propos' => 'https://lotier.immo/a-propos/', 'Contact' => 'https://lotier.immo/contact/', 'Honoraires' => 'https://lotier.immo/nos-honoraires/', 'Estimation gratuite' => 'https://lotier.immo/#estimer'],
            ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT)));
        }
        if ($name === 'list_pages') {
            $lines = [];
            foreach (pages($ROOT, $BLOCKED) as $url => $f) $lines[] = "- {$url} : " . title_of($f);
            reply($id, text(implode("\n", $lines)));
        }
        if ($name === 'search_site') {
            $q = trim((string)($a['query'] ?? ''));
            if (mb_strlen($q) < 2 || mb_strlen($q) > 100) reply($id, text('Indiquez une recherche de 2 à 100 caractères.', true));
            $res = [];
            foreach (pages($ROOT, $BLOCKED) as $url => $f) {
                $c = (string)file_get_contents($f);
                $pos = mb_stripos($c, $q);
                if ($pos === false) continue;
                $snip = trim(preg_replace('/\s+/', ' ', mb_substr($c, max(0, $pos - 80), 220)));
                $res[] = "- {$url} : " . title_of($f) . "\n  …{$snip}…";
                if (count($res) >= 10) break;
            }
            reply($id, text($res ? implode("\n", $res) : 'Aucun résultat.'));
        }
        if ($name === 'get_page') {
            $path = (string)($a['path'] ?? '');
            $path = parse_url($path, PHP_URL_PATH) ?: $path;
            $all = pages($ROOT, $BLOCKED);
            $key = '/' . ltrim($path, '/');
            if (isset($all[$key]) || isset($all[$key . '/']) ) { $f = $all[$key] ?? $all[$key . '/']; }
            elseif (isset($all[rtrim($key, '/') . '.html'])) { $f = $all[rtrim($key, '/') . '.html']; }
            else reply($id, text("Page introuvable. Utilisez list_pages pour connaître les chemins disponibles.", true));
            reply($id, text((string)file_get_contents($f)));
        }
        fail($id, -32602, 'Outil inconnu : ' . $name);
    default:
        fail($id, -32601, 'Méthode non prise en charge : ' . $method);
}
