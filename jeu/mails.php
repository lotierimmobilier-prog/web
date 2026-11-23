<?php
// Concours de Noël : e-mails de suivi envoyés à l'adulte qui a déposé un dessin.
// Rien ne part tant que l'envoi n'est pas activé dans l'administration. Chaque e-mail porte un lien de désinscription.
declare(strict_types=1);

const MAILS_PAR_TOURNEE = 40;          // plafond par passage, pour ménager l'hébergement
const MAILS_HEURE = 9;                 // pas d'envoi programmé avant 9 h

function mails_actifs(): bool { return reglage('mails') === '1'; }
function mails_expediteur(): string { return reglage('mails_de') ?: 'concours@lotier.immo'; }
function mails_signature(string $jeton): string { return substr(hash_hmac('sha256', 'mails|' . $jeton, sel()), 0, 20); }

// Calendrier : clé => jour d'envoi (AAAA-MM-JJ). Un e-mail tous les deux jours pendant les votes.
function mails_calendrier(): array {
    $debut = new DateTimeImmutable(substr(debut_votes(), 0, 10));
    $fin = new DateTimeImmutable(substr(fin_votes(), 0, 10));
    $cal = ['avant-votes' => $debut->modify('-2 days')->format('Y-m-d'), 'ouverture' => $debut->format('Y-m-d')];
    $sprint = $fin->modify('-2 days');
    for ($i = 1, $j = $debut->modify('+2 days'); $j < $sprint->modify('-1 day'); $i++, $j = $j->modify('+2 days')) $cal['suivi-' . $i] = $j->format('Y-m-d');
    if ($sprint > $debut) $cal['sprint'] = $sprint->format('Y-m-d');
    $cal['dernier-jour'] = $fin->format('Y-m-d');
    $cal['resultats'] = $fin->modify('+1 day')->format('Y-m-d');
    return $cal;
}

// Liste de tous les modèles, pour l'aperçu dans l'administration.
function mails_modeles(): array {
    $m = ['recu' => 'À la réception du dessin', 'publie' => 'Quand le dessin est publié'];
    foreach (mails_calendrier() as $cle => $jour) $m[$cle] = 'Le ' . fr_date($jour);
    return $m;
}

// Contenu d'un e-mail : [objet, titre, paragraphes (HTML sûr), libellé du bouton, lien du bouton].
function mails_contenu(string $cle, array $d): array {
    $p = h($d['prenom']); $pn = $d['prenom'];
    $lien = JEU_URL . '?d=' . $d['jeton'];
    $ouv = jour_mois(debut_votes()); $fin = jour_mois(fin_votes());
    $voix = (int) ($d['voix'] ?? 0); $rang = (int) ($d['rang'] ?? 0); $nb = (int) ($d['nb'] ?? 0);
    $cat = mb_strtolower(JEU_CATEGORIES[$d['categorie']] ?? '');
    $etape = $voix === 0
        ? "Le dessin de $p n’a pas encore reçu de vote : le premier partage fera la différence."
        : "Le dessin de $p compte <b>$voix " . ($voix > 1 ? 'votes' : 'vote') . "</b>" . ($rang && $nb > 1 ? " : il est <b>" . ($rang === 1 ? '1er' : $rang . 'e') . " sur $nb</b> dans la catégorie « $cat »." : '.');
    $message = "Aidez $pn à gagner le concours de Noël de LOTIER Immobilier ! Son dessin de la maison du Père Noël attend votre vote, un vote par jour jusqu’au $fin : $lien";

    switch ($cle) {
        case 'recu': return ["Le dessin de $pn est bien arrivé", "Merci, le dessin de $p est bien arrivé !", [
            "Bravo à l’artiste ! Nous avons bien reçu son dessin de la maison du Père Noël.",
            "L’équipe LOTIER le regarde et le met en ligne sous 12 heures. Vous recevrez un message dès qu’il sera visible.",
            "Les votes ouvrent le <b>$ouv</b>. D’ici là, vous pouvez déjà prévenir la famille et les amis."], 'Voir le concours', JEU_URL];
        case 'publie': return ["Le dessin de $pn est en ligne", "Le dessin de $p est en ligne !", [
            "Ça y est : le dessin de $p est visible par tous sur la page du concours.",
            "Les votes ouvrent le <b>$ouv</b>. Partagez dès maintenant le lien du dessin : ceux qui l’auront vu penseront à voter le jour venu.",
            "Le bouton « Partager », sous le dessin, prépare le message pour WhatsApp, Facebook, l’e-mail ou le SMS."], "Voir le dessin de $pn", $lien];
        case 'avant-votes': return ["Dans deux jours, on vote pour $pn", "Les votes ouvrent dans deux jours", [
            "Le <b>$ouv</b>, chacun pourra voter pour le dessin de $p : un vote par jour et par adresse e-mail, jusqu’au $fin.",
            "Trois gestes simples pour bien démarrer :",
            "<b>1.</b> Prévenez dès aujourd’hui la famille proche : parents, grands-parents, oncles et tantes.<br><b>2.</b> Gardez le lien du dessin sous la main, par exemple en vous l’envoyant à vous-même.<br><b>3.</b> Notez la date : les premiers jours donnent l’élan."], "Voir le dessin de $pn", $lien];
        case 'ouverture': return ["C’est parti : votez pour $pn !", "Les votes sont ouverts !", [
            "À partir d’aujourd’hui et jusqu’au <b>$fin</b>, tout le monde peut voter pour le dessin de $p.",
            "Un vote par jour et par adresse e-mail : on peut donc revenir voter chaque jour. Pensez à voter vous aussi, avec une autre adresse que celle du dépôt.",
            "Le plus efficace aujourd’hui : envoyer le lien du dessin à vos proches, avec un petit mot."], "Voter pour $pn", $lien];
        case 'sprint': return ["Plus que trois jours pour $pn", "Plus que trois jours de votes", [
            $etape,
            "Les votes ferment le <b>$fin</b> à 23 h 59. C’est le moment de relancer tous ceux qui ont déjà voté : ils peuvent voter à nouveau chaque jour.",
            "Un simple « tu peux revoter aujourd’hui ? » dans vos groupes suffit souvent."], "Voter pour $pn", $lien];
        case 'dernier-jour': return ["Dernier jour : chaque vote compte pour $pn", "Dernier jour de votes", [
            $etape,
            "Les votes ferment <b>ce soir à 23 h 59</b>. Un dernier partage, un dernier vote : tout peut encore bouger.",
            "Merci pour votre énergie depuis le début du concours."], "Voter pour $pn", $lien];
        case 'resultats': return ["Merci ! Le concours de Noël est terminé", "Bravo à $p, et merci à vous", [
            "Les votes sont clos. " . ($voix > 0 ? "Le dessin de $p a reçu <b>$voix " . ($voix > 1 ? 'votes' : 'vote') . "</b>" . ($rang && $nb > 1 ? " et termine <b>" . ($rang === 1 ? '1er' : $rang . 'e') . " sur $nb</b> dans sa catégorie." : '.') : "Merci à $p d’avoir participé."),
            "Les gagnants sont prévenus par e-mail dans les quinze jours. Les résultats sont visibles sur la page du concours.",
            "Toute l’équipe LOTIER Immobilier vous souhaite de très belles fêtes."], 'Voir les résultats', JEU_URL . '#galerie'];
    }
    // E-mails de suivi, tous les deux jours : un conseil, puis un point d'étape, en alternance.
    $n = (int) substr($cle, 6);
    $conseils = [
        ["Le bon réflexe : un vote par jour", "Le bon réflexe : un vote par jour", [
            "Beaucoup de personnes votent une fois, puis oublient qu’elles peuvent recommencer le lendemain.",
            "Un petit rappel régulier fait toute la différence : « Tu as pensé à voter pour $p aujourd’hui ? »",
            $etape]],
        ["Trois endroits où partager le dessin de $pn", "Trois endroits où partager le dessin", [
            "<b>Les groupes de famille</b> sur WhatsApp ou par SMS : c’est là que l’on vote le plus volontiers.<br><b>Les collègues</b> : un message sur la messagerie du travail, à la pause.<br><b>Facebook</b> : une publication avec le lien du dessin, l’image s’affiche toute seule.",
            $etape]],
        ["Un message tout prêt à envoyer", "Un message tout prêt, à copier", [
            "Pas le temps de rédiger ? Copiez ce message et envoyez-le à vos proches :",
            '<span style="display:block;background:#f4eee2;border-radius:10px;padding:12px 14px">' . h($message) . '</span>',
            $etape]],
        ["Les grands-parents votent aussi", "Pensez à ceux qui sont moins à l’aise avec Internet", [
            "Grands-parents, voisins, amis : beaucoup aimeraient voter mais ne savent pas comment faire. Un appel de deux minutes suffit pour les guider.",
            "Il faut seulement ouvrir le lien, cliquer sur « Voter » et indiquer une adresse e-mail. Chaque adulte du foyer peut voter avec sa propre adresse.",
            $etape]],
        ["Et si $pn remerciait ses soutiens ?", "Un merci qui relance les votes", [
            "Un petit message de remerciement, écrit ou dessiné par $p, est la meilleure des relances : il fait plaisir, et il rappelle que l’on peut voter chaque jour.",
            $etape]],
    ];
    if ($n % 2 === 0) return ["Où en est le dessin de $pn ?", "Le point sur les votes", [
        $etape,
        "Rien n’est joué avant le $fin : les classements bougent tous les jours. Un nouveau partage aujourd’hui peut faire gagner plusieurs places.",
        "Rappel : chaque personne peut voter une fois par jour."], "Voter pour $pn", $lien];
    $c = $conseils[intdiv($n - 1, 2) % count($conseils)];
    return [$c[0], $c[1], $c[2], "Voter pour $pn", $lien];
}

// Compose l'e-mail complet : [objet, HTML, texte brut].
function mails_composer(string $cle, array $d): array {
    [$objet, $titre, $paras, $bouton, $lien] = mails_contenu($cle, $d);
    $desabo = JEU_URL . 'desabo.php?d=' . $d['jeton'] . '&s=' . mails_signature($d['jeton']);
    $html = '<!doctype html><html lang="fr"><body style="margin:0;background:#ece6da;font-family:Arial,Helvetica,sans-serif;color:#2b2620">'
          . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ece6da"><tr><td align="center" style="padding:24px 12px">'
          . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden">'
          . '<tr><td style="background:#8f2530;padding:18px 28px;color:#f3dfae;font-size:13px;letter-spacing:2px;text-transform:uppercase">Concours de Noël · LOTIER Immobilier</td></tr>'
          . '<tr><td style="padding:28px 28px 8px"><h1 style="margin:0 0 16px;font-size:24px;line-height:1.25;color:#14100c">' . $titre . '</h1>';
    foreach ($paras as $t) $html .= '<p style="margin:0 0 14px;font-size:16px;line-height:1.55">' . $t . '</p>';
    $html .= '<p style="margin:22px 0 26px"><a href="' . h($lien) . '" style="display:inline-block;background:#c1272f;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:13px 24px;border-radius:999px">' . h($bouton) . '</a></p>'
          . '</td></tr><tr><td style="padding:16px 28px 24px;border-top:1px solid #eee4d2;font-size:12.5px;line-height:1.5;color:#6b6257">'
          . 'Vous recevez ce message parce que vous avez déposé un dessin au concours de Noël de LOTIER Immobilier, 40 rue Française, 34500 Béziers. '
          . '<a href="' . h($desabo) . '" style="color:#6b6257">Ne plus recevoir ces e-mails</a> · <a href="' . h(JEU_URL . 'reglement.php') . '" style="color:#6b6257">Règlement</a>'
          . '</td></tr></table></td></tr></table></body></html>';
    $texte = html_entity_decode(strip_tags(str_replace(['<br>', '</p>'], ["\n", "\n\n"], $titre . "</p>" . implode('</p>', $paras) . '</p>')), ENT_QUOTES | ENT_HTML5, 'UTF-8')
           . "$bouton : $lien\n\n--\nLOTIER Immobilier, 40 rue Française, 34500 Béziers\nNe plus recevoir ces e-mails : $desabo\n";
    return [$objet, $html, $texte];
}

function mails_envoyer_a(string $a, string $objet, string $html, string $texte, string $desabo = ''): bool {
    $de = mails_expediteur();
    $b = 'lotier-' . bin2hex(random_bytes(8));
    $entetes = ['MIME-Version: 1.0', 'From: =?UTF-8?B?' . base64_encode('LOTIER Immobilier') . '?= <' . $de . '>', 'Reply-To: contact@lotier-immobilier.com',
                'Content-Type: multipart/alternative; boundary="' . $b . '"', 'X-Auto-Response-Suppress: All'];
    if ($desabo !== '') { $entetes[] = 'List-Unsubscribe: <' . $desabo . '>'; }
    $corps = "--$b\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($texte))
           . "--$b\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html)) . "--$b--\r\n";
    if (getenv('JEU_MAILS_VERS')) {      // essais en local : l'e-mail est écrit dans un dossier au lieu d'être envoyé
        return (bool) file_put_contents(rtrim(getenv('JEU_MAILS_VERS'), '/') . '/' . date('His') . '-' . bin2hex(random_bytes(3)) . '.eml', "To: $a\nSubject: $objet\n\n$texte\n\n$html");
    }
    return @mail($a, '=?UTF-8?B?' . base64_encode($objet) . '?=', $corps, implode("\r\n", $entetes), '-f' . $de);
}

// Dessin enrichi de son nombre de voix, de son rang et de la taille de sa catégorie.
function mails_dessin(int $id): ?array {
    $q = db()->prepare('SELECT d.*, (SELECT COUNT(*) FROM votes v WHERE v.dessin_id = d.id) AS voix FROM dessins d WHERE d.id = ?'); $q->execute([$id]);
    $d = $q->fetch();
    if (!$d) return null;
    $d['rang'] = 0; $d['nb'] = 0;
    foreach (dessins_valides() as $x) {
        if ($x['categorie'] !== $d['categorie']) continue;
        $d['nb']++;
        if ($x['jeton'] === $d['jeton']) $d['rang'] = $d['nb'];
    }
    return $d;
}

// Envoie un e-mail du tunnel à un dessin, une seule fois. Retourne vrai s'il est parti.
function mails_envoyer(string $cle, int $id): bool {
    if (!mails_actifs()) return false;
    $d = mails_dessin($id);
    if (!$d || !(int) $d['mails']) return false;
    $q = db()->prepare('SELECT 1 FROM envois WHERE dessin_id = ? AND cle = ?'); $q->execute([$id, $cle]);
    if ($q->fetchColumn()) return false;
    [$objet, $html, $texte] = mails_composer($cle, $d);
    $desabo = JEU_URL . 'desabo.php?d=' . $d['jeton'] . '&s=' . mails_signature($d['jeton']);
    $ok = mails_envoyer_a($d['email'], $objet, $html, $texte, $desabo);
    db()->prepare('INSERT OR IGNORE INTO envois (dessin_id, cle, quand, ok) VALUES (?, ?, ?, ?)')->execute([$id, $cle, date('Y-m-d H:i:s'), $ok ? 1 : 0]);
    return $ok;
}

// Tournée du jour : envoie à chaque dessin publié l'e-mail prévu aujourd'hui (ou hier s'il a été manqué).
function mails_tournee(bool $forcer = false): int {
    if (!mails_actifs()) return 0;
    $n = maintenant();
    if (!$forcer && ((int) $n->format('G') < MAILS_HEURE || reglage('mails_tournee') === $n->format('Y-m-d'))) return 0;
    $jours = [$n->format('Y-m-d'), $n->modify('-1 day')->format('Y-m-d')];
    $cles = array_keys(array_filter(mails_calendrier(), fn($j) => in_array($j, $jours, true)));
    $envoyes = 0; $reste = false;
    if ($cles) {
        foreach (db()->query("SELECT id FROM dessins WHERE statut = 'valide' AND mails = 1 ORDER BY id")->fetchAll(PDO::FETCH_COLUMN) as $id) {
            $q = db()->prepare('SELECT COUNT(*) FROM envois WHERE dessin_id = ? AND substr(quand, 1, 10) = ?'); $q->execute([(int) $id, date('Y-m-d')]);
            if ((int) $q->fetchColumn() > 0) continue;                                   // un seul e-mail par jour et par dessin
            foreach (array_reverse($cles) as $cle) {                                     // le plus récent d'abord
                $q = db()->prepare('SELECT 1 FROM envois WHERE dessin_id = ? AND cle = ?'); $q->execute([(int) $id, $cle]);
                if ($q->fetchColumn()) continue;
                if ($envoyes >= MAILS_PAR_TOURNEE) { $reste = true; break 2; }
                if (mails_envoyer($cle, (int) $id)) $envoyes++;
                break;
            }
        }
    }
    if (!$reste) reglage('mails_tournee', $n->format('Y-m-d'));                          // sinon la suite part au prochain passage
    if ($envoyes) journal('e-mails', "tournée : $envoyes");
    return $envoyes;
}

// Dessin d'exemple pour les aperçus et les messages d'essai de l'administration.
function mails_exemple(): array {
    return ['jeton' => '0000000000000000', 'prenom' => 'Léa', 'age' => 7, 'categorie' => '6-8', 'voix' => 12, 'rang' => 2, 'nb' => 9, 'email' => '', 'mails' => 1];
}
