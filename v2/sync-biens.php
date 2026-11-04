<?php
// Met à jour data/biens.json à partir des annonces publiées sur /nos-biens/ (WordPress).
// À lancer par une tâche planifiée (cron) de l'hébergeur, jamais depuis le navigateur :
//   php /chemin/vers/le/site/sync-biens.php
// Option : un second argument = chemin du fichier de sortie (pour les tests).
declare(strict_types=1);

if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }

const BASE = 'https://www.lotier-immobilier.com/nos-biens/';
const UA   = 'LotierV2-sync/1.0 (+https://www.lotier-immobilier.com)';
$sortie = $argv[1] ?? __DIR__ . '/data/biens.json';

function get(string $url): ?string {
    if (function_exists('curl_init')) {
        $c = curl_init($url);
        curl_setopt_array($c, [CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true, CURLOPT_TIMEOUT => 30, CURLOPT_USERAGENT => UA]);
        $h = curl_exec($c); $code = (int)curl_getinfo($c, CURLINFO_RESPONSE_CODE); curl_close($c);
        return ($h !== false && $code === 200) ? (string)$h : null;
    }
    $ctx = stream_context_create(['http' => ['header' => 'User-Agent: ' . UA, 'timeout' => 30, 'ignore_errors' => true]]);
    $h = @file_get_contents($url, false, $ctx);
    $code = 0;
    if (isset($http_response_header[0]) && preg_match('#\s(\d{3})\s#', $http_response_header[0], $m)) $code = (int)$m[1];
    return ($h !== false && $code === 200) ? $h : null;
}
function txt(string $s): string {
    return trim(preg_replace('/\s+/u', ' ', html_entity_decode(strip_tags(str_replace('<', ' <', $s)), ENT_QUOTES | ENT_HTML5, 'UTF-8')) ?? '');
}
function nombre(string $s): float {
    return (float)str_replace(',', '.', preg_replace('/[^\d.,]/u', '', $s) ?? '');
}

$biens = [];
for ($page = 1; $page <= 50; $page++) {
    $h = get($page === 1 ? BASE : BASE . "page/$page/");
    if ($h === null) break;
    $parts = array_slice(explode('<div class="iwp__item">', $h), 1);
    if (!$parts) break;
    foreach ($parts as $blk) {
        if (preg_match('#<a href="([^"]+)"#', $blk, $u) === 0 || preg_match('#<h3>(.*?)</h3>#s', $blk, $t) === 0) continue;
        preg_match('#<img[^>]*src="([^"]+)"#', $blk, $img);
        preg_match('#class="localisation">(.*?)</div>#s', $blk, $ville);
        preg_match('#class="iwp__price">(.*?)</span>#s', $blk, $prix);
        preg_match('#class="iwp__postfix">(.*?)</span>#s', $blk, $post);
        $apercu = txt(preg_replace('#<svg.*?</svg>#s', '', $blk) ?? '');
        $badges = [];
        if (preg_match('#iwp__item-meta">(.*?)</div>#s', $blk, $meta)) {
            preg_match_all('#<li[^>]*>(.*?)</li>#s', $meta[1], $li);
            foreach ($li[1] as $b) { if (($b = txt($b)) !== '') $badges[] = $b; }
        }
        if (!$badges) foreach (['Exclusivité', 'Coup de coeur'] as $b) if (str_contains($apercu, $b)) $badges[] = $b;
        preg_match('#(\d+)\s*ch\.#u', $apercu, $ch);
        preg_match('#([\d.,]+)\s*m²#u', $apercu, $m2);
        preg_match('#(\d+)\s*(?:sdb|sde)#u', $apercu, $sb);
        $pv = isset($prix[1]) ? nombre(txt($prix[1])) : 0.0;
        $biens[$u[1]] = [
            'url' => $u[1], 'titre' => txt($t[1]), 'ville' => isset($ville[1]) ? txt($ville[1]) : '',
            'type' => (isset($post[1]) && str_contains(txt($post[1]), 'mois')) ? 'location' : 'vente',
            'prix' => $pv > 0 ? $pv : null,
            'surface' => isset($m2[1]) ? nombre($m2[1]) : null,
            'chambres' => isset($ch[1]) ? (int)$ch[1] : null,
            'sdb' => isset($sb[1]) ? (int)$sb[1] : null,
            'image' => $img[1] ?? null, 'badges' => $badges,
        ];
    }
    fwrite(STDERR, "page $page : " . count($parts) . " annonces\n");
    sleep(1);
}
$biens = array_values($biens);

// Garde-fous : on ne remplace jamais le fichier existant par un résultat vide ou très réduit
$ancien = is_file($sortie) ? (json_decode((string)file_get_contents($sortie), true)['biens'] ?? []) : [];
if (!$biens || (count($ancien) >= 10 && count($biens) < count($ancien) * 0.5)) {
    fwrite(STDERR, "Résultat suspect (" . count($biens) . " annonces contre " . count($ancien) . "), fichier conservé.\n");
    exit(1);
}
$json = json_encode(['maj' => gmdate('c'), 'biens' => $biens], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
$tmp = $sortie . '.tmp';
if (file_put_contents($tmp, $json, LOCK_EX) === false || !rename($tmp, $sortie)) { fwrite(STDERR, "Écriture impossible.\n"); exit(1); }
fwrite(STDERR, count($biens) . " annonces écrites dans $sortie\n");
