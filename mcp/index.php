<?php
/**
 * Serveur MCP (Model Context Protocol) en lecture seule pour lotier.immo.
 * Transport : Streamable HTTP (JSON-RPC 2.0 en POST). Aucun accès à des données privées :
 * il ne sert que le contenu public du site (versions Markdown des pages).
 */
declare(strict_types=1);

const SERVER_VERSION = '1.0.0';
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

$tools = [
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
            'instructions' => "Serveur en lecture seule : contenu public du site lotier.immo (agence immobilière à Béziers, Montpellier, Nîmes, Carcassonne). Pour estimer un bien ou être rappelé, renvoyer l'utilisateur vers https://lotier.immo/#estimer ou le 04 67 11 28 31.",
        ]);
    case 'ping': reply($id, []);
    case 'tools/list': reply($id, ['tools' => $tools]);
    case 'tools/call':
        $name = (string)($p['name'] ?? ''); $a = is_array($p['arguments'] ?? null) ? $p['arguments'] : [];
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
