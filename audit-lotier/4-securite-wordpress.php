<?php
/**
 * Plugin Name: Lotier – correctifs audit
 * Description: SEO local (données structurées), sécurité REST, viewport.
 * À déposer dans wp-content/mu-plugins/lotier-audit.php (chargé automatiquement).
 * Compléter les valeurs [À COMPLÉTER] avant de mettre en ligne.
 */

// 1) Ne plus exposer la liste des utilisateurs aux visiteurs non connectés
add_filter('rest_endpoints', function ($endpoints) {
    if (!is_user_logged_in()) {
        unset($endpoints['/wp/v2/users'], $endpoints['/wp/v2/users/(?P<id>[\d]+)']);
    }
    return $endpoints;
});
// Bloque aussi /?author=1 (énumération des identifiants)
add_action('template_redirect', function () {
    if (is_author() || isset($_GET['author'])) { wp_redirect(home_url('/'), 301); exit; }
});

// 2) Désactiver XML-RPC et masquer la version WordPress
add_filter('xmlrpc_enabled', '__return_false');
remove_action('wp_head', 'wp_generator');

// 3) Viewport accessible (autorise le zoom)
add_action('template_redirect', function () {
    ob_start(function ($html) {
        return preg_replace(
            '/<meta name="viewport"[^>]*>/i',
            '<meta name="viewport" content="width=device-width, initial-scale=1" />',
            $html
        );
    });
});

// 4) Données structurées + Open Graph sur la page d'accueil
add_action('wp_head', function () {
    if (!is_front_page()) return;
    $data = [
        '@context' => 'https://schema.org',
        '@type'    => 'RealEstateAgent',
        'name'     => 'Lotier Immobilier',
        'url'      => 'https://www.lotier-immobilier.com/',
        'telephone'=> '+33467112831',
        'email'    => 'contact@lotier-immobilier.com',
        'image'    => 'https://www.lotier-immobilier.com/wp-content/uploads/2026/06/cropped-logo-rond-192x192.jpg',
        'address'  => [
            '@type' => 'PostalAddress',
            'streetAddress'   => '38/40 rue Française',
            'postalCode'      => '34500',
            'addressLocality' => 'Béziers',
            'addressCountry'  => 'FR',
        ],
        'openingHoursSpecification' => [[
            '@type'     => 'OpeningHoursSpecification',
            'dayOfWeek' => ['Monday', 'Tuesday', 'Wednesday', 'Friday'],
            'opens' => '09:00', 'closes' => '18:00', // pause 12h-14h : à affiner en 2 plages si souhaité
        ]],
        'areaServed' => 'Béziers',
        'sameAs' => ['[URL Facebook À COMPLÉTER]', '[URL Instagram À COMPLÉTER]'],
    ];
    echo '<script type="application/ld+json">' . wp_json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "</script>\n";
    echo '<meta property="og:type" content="website" />' . "\n";
    echo '<meta property="og:title" content="Lotier Immobilier – Agence à Béziers" />' . "\n";
    echo '<meta property="og:description" content="Vente, gestion locative et syndic de copropriété à Béziers." />' . "\n";
    echo '<meta property="og:url" content="https://www.lotier-immobilier.com/" />' . "\n";
    echo '<meta property="og:image" content="[URL IMAGE 1200x630 À COMPLÉTER]" />' . "\n";
}, 5);
