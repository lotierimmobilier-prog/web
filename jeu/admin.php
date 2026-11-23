<?php
// Concours de Noël : administration (validation des dessins, résultats, exports). Accès par mot de passe.
declare(strict_types=1);
require __DIR__ . '/lib.php';
require __DIR__ . '/mails.php';
entetes_page();
header('X-Robots-Tag: noindex, nofollow');

$https = (($_SERVER['HTTPS'] ?? '') === 'on') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('concours_admin');
session_start(['cookie_path' => '/jeu/', 'cookie_httponly' => true, 'cookie_samesite' => 'Strict', 'cookie_secure' => $https, 'use_strict_mode' => true]);
if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
$csrf = $_SESSION['csrf'];
$post = ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST';
$csrf_ok = $post && hash_equals($csrf, (string) ($_POST['csrf'] ?? ''));
$empreinte = reglage('admin');
$erreur = ''; $info = ($_GET['ok'] ?? '') === 'dates' ? 'Dates enregistrées. Le site public les applique dès maintenant.' : '';

function trop_de_tentatives(): bool {
    db()->prepare('DELETE FROM tentatives WHERE quand < ?')->execute([time() - 900]);
    $q = db()->prepare('SELECT COUNT(*) FROM tentatives WHERE ip = ?'); $q->execute([ip()]);
    return (int) $q->fetchColumn() >= 6;
}

// Première ouverture : choix du mot de passe (il n'est écrit nulle part dans le code, seule son empreinte est gardée).
if ($empreinte === null) {
    if ($csrf_ok && ($_POST['action'] ?? '') === 'creer') {
        $m = (string) ($_POST['mdp'] ?? '');
        if (mb_strlen($m) < 12) $erreur = 'Le mot de passe doit compter au moins 12 caractères.';
        else { reglage('admin', password_hash($m, PASSWORD_DEFAULT)); journal('admin', 'mot de passe créé'); session_regenerate_id(true); $_SESSION['admin'] = true; header('Location: admin.php'); exit; }
    }
} elseif (empty($_SESSION['admin'])) {
    if ($csrf_ok && ($_POST['action'] ?? '') === 'connexion') {
        if (trop_de_tentatives()) $erreur = 'Trop de tentatives. Réessayez dans un quart d’heure.';
        elseif (password_verify((string) ($_POST['mdp'] ?? ''), $empreinte)) { session_regenerate_id(true); $_SESSION['admin'] = true; header('Location: admin.php'); exit; }
        else { db()->prepare('INSERT INTO tentatives (ip, quand) VALUES (?, ?)')->execute([ip(), time()]); usleep(400000); $erreur = 'Mot de passe incorrect.'; }
    }
}
$admin = !empty($_SESSION['admin']) && $empreinte !== null;

if ($admin && $csrf_ok) {
    $a = (string) ($_POST['action'] ?? ''); $id = (int) ($_POST['id'] ?? 0);
    if ($a === 'deconnexion') { $_SESSION = []; session_destroy(); header('Location: admin.php'); exit; }
    if (in_array($a, ['valider', 'refuser', 'suspendre'], true) && $id) {
        db()->prepare('UPDATE dessins SET statut = ?, traite_le = ? WHERE id = ?')->execute([['valider' => 'valide', 'refuser' => 'refuse', 'suspendre' => 'suspendu'][$a], date('Y-m-d H:i:s'), $id]);
        journal($a, (string) $id); if ($a === 'valider') mails_envoyer('publie', $id); $info = ['valider' => 'Dessin publié.', 'refuser' => 'Dessin refusé (il n’est pas affiché).', 'suspendre' => 'Dessin suspendu : il n’est plus affiché et ne peut plus recevoir de vote. Ses données et ses votes sont conservés ; « Remettre en ligne » le republie.'][$a];
    }
    if ($a === 'supprimer' && $id) {
        $q = db()->prepare('SELECT jeton FROM dessins WHERE id = ?'); $q->execute([$id]); $j = $q->fetchColumn();
        if ($j) { @unlink(chemin_dessin($j)); @unlink(chemin_dessin($j, true)); db()->prepare('DELETE FROM dessins WHERE id = ?')->execute([$id]); journal('supprimer', (string) $id); $info = 'Dessin, données et votes associés supprimés.'; }
    }
    if ($a === 'demande-traitee' && $id) { db()->prepare('UPDATE demandes SET traite_le = ? WHERE id = ?')->execute([date('Y-m-d H:i:s'), $id]); journal('demande traitée', (string) $id); $info = 'Demande classée.'; }
    if ($a === 'demande-suspendre' && $id) {
        $q = db()->prepare('SELECT dessin_id FROM demandes WHERE id = ?'); $q->execute([$id]); $did = $q->fetchColumn();
        if ($did) {
            db()->prepare("UPDATE dessins SET statut = 'suspendu', traite_le = ? WHERE id = ?")->execute([date('Y-m-d H:i:s'), (int) $did]);
            db()->prepare('UPDATE demandes SET traite_le = ? WHERE id = ?')->execute([date('Y-m-d H:i:s'), $id]);
            journal('demande : dessin suspendu', (string) $did); $info = 'Dessin suspendu et demande classée. Pour effacer aussi ses données, utilisez « Supprimer » sur le dessin.';
        }
    }
    if ($a === 'mails-reglages') {
        $de = email_propre((string) ($_POST['de'] ?? ''));
        if (!$de) $erreur = 'Indiquez une adresse d’expédition valide.';
        else { reglage('mails_de', $de); reglage('mails', ($_POST['actif'] ?? '') === '1' ? '1' : '0'); journal('e-mails', mails_actifs() ? 'activés' : 'désactivés'); $info = mails_actifs() ? 'E-mails activés : les prochains messages partiront automatiquement.' : 'E-mails désactivés : plus rien ne part.'; }
    }
    if ($a === 'mails-essai') {
        $vers = email_propre((string) ($_POST['vers'] ?? '')); $cle = (string) ($_POST['cle'] ?? '');
        if (!$vers || !isset(mails_modeles()[$cle])) $erreur = 'Indiquez une adresse valide et choisissez un message.';
        else { [$o, $hh, $t] = mails_composer($cle, mails_exemple()); $ok = mails_envoyer_a($vers, '[Essai] ' . $o, $hh, $t); if ($ok) $info = 'Message d’essai envoyé à ' . $vers . '. Vérifiez aussi le dossier des indésirables.'; else $erreur = 'Le serveur a refusé l’envoi.'; }
    }
    if ($a === 'mails-tournee') { $n = mails_tournee(true); $info = $n . ' e-mail(s) envoyé(s).'; }
    if ($a === 'dates') {
        $dd = (string) ($_POST['depots'] ?? ''); $dv = (string) ($_POST['votes'] ?? '');
        $ok = fn($v) => preg_match('/^\d{4}-\d{2}-\d{2}$/', $v) && checkdate((int) substr($v, 5, 2), (int) substr($v, 8, 2), (int) substr($v, 0, 4));
        if (!$ok($dd) || !$ok($dv)) $erreur = 'Indiquez deux dates valides.';
        elseif ($dv <= $dd) $erreur = 'Le dernier jour des votes doit être postérieur au dernier jour des dépôts.';
        elseif ($dd === JEU_FIN_DEPOTS && $dv === JEU_FIN_VOTES) { db()->exec("DELETE FROM reglages WHERE cle = 'dates'"); journal('dates', 'officielles'); header('Location: admin.php?ok=dates'); exit; }
        else { reglage('dates', json_encode(['depots' => $dd, 'votes' => $dv])); journal('dates', "$dd / $dv"); header('Location: admin.php?ok=dates'); exit; }
    }
    if ($a === 'dates-officielles') { db()->exec("DELETE FROM reglages WHERE cle = 'dates'"); journal('dates', 'officielles'); header('Location: admin.php?ok=dates'); exit; }
    if ($a === 'vider-votes' && ($_POST['confirmation'] ?? '') === 'EFFACER') {
        $n = (int) db()->query('SELECT COUNT(*) FROM votes')->fetchColumn(); db()->exec('DELETE FROM votes'); journal('votes', "effacés : $n"); $info = "$n vote(s) effacé(s).";
    } elseif ($a === 'vider-votes') $erreur = 'Pour effacer les votes, écrivez EFFACER dans la case.';
    if ($a === 'mdp') {
        $m = (string) ($_POST['mdp'] ?? '');
        if (mb_strlen($m) < 12) $erreur = 'Le nouveau mot de passe doit compter au moins 12 caractères.';
        else { reglage('admin', password_hash($m, PASSWORD_DEFAULT)); journal('admin', 'mot de passe changé'); $info = 'Mot de passe changé.'; }
    }
}
if ($admin && isset($_GET['apercu']) && isset(mails_modeles()[(string) $_GET['apercu']])) {
    header('Content-Type: text/html; charset=utf-8'); header('Cache-Control: no-store');
    echo mails_composer((string) $_GET['apercu'], mails_exemple())[1]; exit;
}
if ($admin && isset($_GET['export'])) {
    $quoi = $_GET['export'] === 'infolettre' ? 'infolettre' : 'participants';
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="concours-noel-' . $quoi . '-' . date('Y-m-d') . '.csv"');
    $s = fopen('php://output', 'w'); fwrite($s, "\xEF\xBB\xBF");
    $sur = fn($v) => preg_match('/^[=+\-@\t\r]/', (string) $v) ? "'" . $v : (string) $v;      // pas de formule dans un tableur
    if ($quoi === 'infolettre') {
        fputcsv($s, ['E-mail', 'Code postal', 'Projet', 'Date du consentement'], ';');
        foreach (db()->query("SELECT DISTINCT email, code_postal, projet, cree_le FROM dessins WHERE infolettre = 1 ORDER BY cree_le") as $r) fputcsv($s, array_map($sur, array_values($r)), ';');
    } else {
        fputcsv($s, ['Prénom', 'Âge', 'Catégorie', 'Statut', 'Voix', 'E-mail de l’adulte', 'Lien', 'Code postal', 'Projet', 'Rappel demandé', 'Téléphone', 'Lettre d’information', 'Déposé le'], ';');
        foreach (db()->query("SELECT prenom, age, categorie, statut, (SELECT COUNT(*) FROM votes v WHERE v.dessin_id = d.id), email, lien, code_postal, projet, rappel, telephone, infolettre, cree_le FROM dessins d ORDER BY categorie, cree_le") as $r) fputcsv($s, array_map($sur, array_values($r)), ';');
    }
    journal('export', $quoi);
    exit;
}
$liste = $admin ? db()->query("SELECT d.*, (SELECT COUNT(*) FROM votes v WHERE v.dessin_id = d.id) AS voix FROM dessins d ORDER BY CASE statut WHEN 'attente' THEN 0 WHEN 'valide' THEN 1 WHEN 'suspendu' THEN 2 ELSE 3 END, categorie, voix DESC, cree_le")->fetchAll() : [];
$demandes = $admin ? db()->query("SELECT q.*, d.prenom AS d_prenom, d.age AS d_age, d.statut AS d_statut, d.jeton AS d_jeton FROM demandes q LEFT JOIN dessins d ON d.id = q.dessin_id WHERE q.traite_le IS NULL ORDER BY q.id")->fetchAll() : [];
$compte = ['attente' => 0, 'valide' => 0, 'suspendu' => 0, 'refuse' => 0];
foreach ($liste as $d) $compte[$d['statut']]++;
$champ_csrf = '<input type="hidden" name="csrf" value="' . h($csrf) . '">';
$suivi = null;
if ($admin) {
    $jour = maintenant()->format('Y-m-d');
    $un = fn(string $sql, array $p = []) => (function () use ($sql, $p) { $q = db()->prepare($sql); $q->execute($p); return (int) $q->fetchColumn(); })();
    $suivi = ['total' => $un('SELECT COUNT(*) FROM votes'), 'jour' => $un('SELECT COUNT(*) FROM votes WHERE jour = ?', [$jour]), 'votants' => $un('SELECT COUNT(DISTINCT email) FROM votes'),
              'par_jour' => db()->query('SELECT jour, COUNT(*) AS n FROM votes GROUP BY jour ORDER BY jour DESC LIMIT 30')->fetchAll(),
              'alertes' => db()->query("SELECT v.jour, d.prenom, COUNT(*) AS n FROM votes v JOIN dessins d ON d.id = v.dessin_id GROUP BY v.jour, v.ip, v.dessin_id HAVING n >= 8 ORDER BY v.jour DESC, n DESC LIMIT 20")->fetchAll()];
    $classement = array_fill_keys(array_keys(JEU_CATEGORIES), []);
    foreach (dessins_valides() as $x) $classement[$x['categorie']][] = $x;
}
?><!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
  <title>Administration du concours de Noël</title>
  <link rel="stylesheet" href="style.css?v=10">
  <style>
    .adm { max-width: 1180px; margin: 0 auto; padding: 24px clamp(14px, 3vw, 32px) 60px; }
    .adm h1 { font-size: 30px; margin-bottom: 6px; } .adm h2 { font-size: 22px; margin: 28px 0 10px; }
    .boite { background: #fff; border: 1px solid var(--trait); border-radius: 18px; padding: 20px; max-width: 460px; }
    .ligne { display: grid; grid-template-columns: 150px 1fr auto; gap: 16px; align-items: start; background: #fff; border: 1px solid var(--trait); border-radius: 16px; padding: 12px; margin-bottom: 10px; }
    .ligne img { border-radius: 10px; width: 150px; } .ligne p { margin: 0 0 3px; font-size: 15px; } .ligne form { display: inline; }
    .ligne .btn { min-height: 38px; padding: 6px 14px; font-size: 14.5px; margin: 0 0 6px 6px; }
    .etat { display: inline-block; border-radius: 999px; padding: 2px 10px; font-size: 13px; font-weight: 600; }
    .attente { background: #fff3cd; color: #5c4a10; } .valide { background: #dff3e4; color: #17502c; } .refuse { background: #f6dddd; color: #7a1f27; } .suspendu { background: #e6e9ee; color: #33415a; }
    .alerte { background: #fff3cd; color: #5c4a10; padding: 10px 14px; border-radius: 12px; max-width: 640px; } .adm .aide { font-size: 14px; color: #4d5c70; margin: 6px 0; } .adm .boite + form, .adm form + .boite { margin-top: 12px; }
    .ok { background: #dff3e4; color: #17502c; padding: 10px 14px; border-radius: 12px; font-weight: 600; }
    .diag { font-size: 14px; color: #4d5c70; } .diag code { background: #eef1f5; padding: 1px 5px; border-radius: 4px; }
    .suivi { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 0 22px; } .adm .classement { max-width: none; } .adm .classement td, .adm .classement th { white-space: nowrap; } .adm .jours { max-width: 420px; }
    @media (max-width: 720px) { .ligne { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<main class="adm">
  <h1>Concours de Noël · administration</h1>
<?php if ($erreur): ?><p class="message"><?= h($erreur) ?></p><?php endif; ?>
<?php if ($info): ?><p class="ok"><?= h($info) ?></p><?php endif; ?>

<?php if ($empreinte === null): ?>
  <form method="post" class="boite" autocomplete="off"><?= $champ_csrf ?><input type="hidden" name="action" value="creer">
    <p><b>Première ouverture.</b> Choisissez le mot de passe de l’administration (12 caractères au moins).</p>
    <p><label for="mdp">Mot de passe</label><input id="mdp" name="mdp" type="password" required minlength="12" autocomplete="new-password"></p>
    <p><button class="btn rouge" type="submit">Enregistrer</button></p>
  </form>
<?php elseif (!$admin): ?>
  <form method="post" class="boite"><?= $champ_csrf ?><input type="hidden" name="action" value="connexion">
    <p><label for="mdp">Mot de passe</label><input id="mdp" name="mdp" type="password" required autocomplete="current-password"></p>
    <p><button class="btn rouge" type="submit">Se connecter</button></p>
  </form>
<?php else: ?>
  <p>Phase en cours : <b><?= ['depot' => 'dépôt des dessins', 'vote' => 'votes', 'fini' => 'concours terminé'][phase()] ?></b> · <?= $compte['attente'] ?> en attente · <?= $compte['valide'] ?> publié(s) · <?= $compte['suspendu'] ?> suspendu(s) · <?= $compte['refuse'] ?> refusé(s)<?php if ($demandes): ?> · <a href="#demandes"><b><?= count($demandes) ?> demande(s) de retrait à traiter</b></a><?php endif; ?></p>
  <p class="boutons"><a class="btn clair" href="admin.php">Actualiser</a><a class="btn clair" href="admin.php?export=participants">Exporter les participants (CSV)</a><a class="btn clair" href="admin.php?export=infolettre">Exporter les inscrits à la lettre d’information (CSV)</a><a class="btn clair" href="./" target="_blank" rel="noopener">Voir le concours</a></p>
<?php if ($demandes): ?>
  <h2 id="demandes">Demandes de retrait (<?= count($demandes) ?>)</h2>
<?php foreach ($demandes as $q): ?>
  <div class="ligne demande">
<?php if ($q['d_jeton']): ?>    <img src="image.php?d=<?= h($q['d_jeton']) ?>&amp;v=1" alt="Dessin concerné" width="150" height="112" loading="lazy">
<?php else: ?>    <span></span>
<?php endif; ?>
    <div>
      <p><b><?= h($q['prenom']) ?></b> · <?= h($q['email']) ?> · reçue le <?= h(fr_date($q['cree_le'])) ?> à <?= h(substr($q['cree_le'], 11, 5)) ?></p>
<?php if ($q['d_jeton']): ?>      <p><span class="etat valide">Prénom et e-mail identiques à ceux du dépôt</span> · dessin de <?= h($q['d_prenom']) ?>, <?= (int) $q['d_age'] ?> ans, actuellement <?= h(['attente' => 'en attente', 'valide' => 'publié', 'suspendu' => 'suspendu', 'refuse' => 'refusé'][$q['d_statut']] ?? $q['d_statut']) ?></p>
<?php else: ?>      <p><span class="etat refuse">Aucun dessin déposé avec ce prénom et cette adresse</span> · vérifiez avant d’agir, et répondez au demandeur.</p>
<?php endif; ?>
<?php if ($q['message'] !== ''): ?>      <p>« <?= nl2br(h($q['message'])) ?> »</p>
<?php endif; ?>
    </div>
    <div>
<?php if ($q['d_jeton'] && $q['d_statut'] !== 'suspendu'): ?>      <form method="post"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $q['id'] ?>"><button class="btn rouge" name="action" value="demande-suspendre">Suspendre le dessin</button></form>
<?php endif; ?>
      <form method="post"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $q['id'] ?>"><button class="btn clair" name="action" value="demande-traitee">Classer la demande</button></form>
    </div>
  </div>
<?php endforeach; ?>
<?php endif; ?>
  <h2>Suivi des votes</h2>
  <p><b><?= $suivi['total'] ?></b> vote(s) au total · <b><?= $suivi['jour'] ?></b> aujourd’hui · <b><?= $suivi['votants'] ?></b> votant(s) différent(s)</p>
  <div class="suivi">
<?php foreach (JEU_CATEGORIES as $cle => $nom): ?>
    <table class="classement"><caption><?= h($nom) ?></caption><thead><tr><th>Rang</th><th>Prénom</th><th>Âge</th><th>Votes</th></tr></thead><tbody>
<?php if (!$classement[$cle]): ?><tr><td colspan="4">Aucun dessin publié.</td></tr><?php endif; ?>
<?php foreach ($classement[$cle] as $i => $x): ?><tr<?= $i < 3 ? ' class="podium"' : '' ?>><td><?= $i + 1 ?></td><td><?= h($x['prenom']) ?></td><td><?= (int) $x['age'] ?> ans</td><td><b><?= (int) $x['voix'] ?></b></td></tr><?php endforeach; ?>
    </tbody></table>
<?php endforeach; ?>
  </div>
<?php if ($suivi['par_jour']): ?>
  <table class="classement jours"><caption>Votes par jour</caption><thead><tr><th>Jour</th><th>Votes</th></tr></thead><tbody>
<?php foreach ($suivi['par_jour'] as $r): ?><tr><td style="width:auto"><?= h(fr_date($r['jour'])) ?></td><td><b><?= (int) $r['n'] ?></b></td></tr><?php endforeach; ?>
  </tbody></table>
<?php endif; ?>
<?php if ($suivi['alertes']): ?>
  <p class="message">À surveiller : beaucoup de votes pour un même dessin depuis une même connexion, le même jour.</p>
  <ul><?php foreach ($suivi['alertes'] as $r): ?><li><?= h(fr_date($r['jour'])) ?> : <?= (int) $r['n'] ?> votes pour <?= h($r['prenom']) ?></li><?php endforeach; ?></ul>
<?php endif; ?>
  <h2>Dessins</h2>
<?php if (!$liste): ?><p>Aucun dessin pour le moment.</p><?php endif; ?>
<?php foreach ($liste as $d): ?>
  <div class="ligne">
    <a href="image.php?d=<?= h($d['jeton']) ?>" target="_blank" rel="noopener"><img src="image.php?d=<?= h($d['jeton']) ?>&amp;v=1" alt="Dessin de <?= h($d['prenom']) ?>" loading="lazy"></a>
    <div>
      <p><b><?= h($d['prenom']) ?></b>, <?= (int) $d['age'] ?> ans · <?= h(JEU_CATEGORIES[$d['categorie']] ?? $d['categorie']) ?> · <span class="etat <?= h($d['statut']) ?>"><?= ['attente' => 'En attente', 'valide' => 'Publié', 'suspendu' => 'Suspendu', 'refuse' => 'Refusé'][$d['statut']] ?? $d['statut'] ?></span> · <?= (int) $d['voix'] ?> vote(s)</p>
      <p>Adulte : <?= h($d['email']) ?><?= $d['lien'] !== '' ? ' (' . h($d['lien']) . ')' : '' ?></p>
      <p><?= $d['code_postal'] !== '' ? 'Code postal : ' . h($d['code_postal']) . ' · ' : '' ?><?= $d['projet'] !== '' ? 'Projet : ' . h(JEU_PROJETS[$d['projet']] ?? $d['projet']) . ' · ' : '' ?><?= $d['rappel'] ? '<b>À rappeler : ' . h($d['telephone']) . '</b> · ' : '' ?><?= $d['infolettre'] ? 'Lettre d’information : oui' : 'Lettre d’information : non' ?></p>
      <p class="diag">Déposé le <?= h($d['cree_le']) ?> · lien public : <code><?= h(JEU_URL . '?d=' . $d['jeton']) ?></code></p>
    </div>
    <div>
<?php if ($d['statut'] !== 'valide'): ?><form method="post"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $d['id'] ?>"><button class="btn rouge" name="action" value="valider"><?= $d['statut'] === 'suspendu' ? 'Remettre en ligne' : 'Publier' ?></button></form><?php endif; ?>
<?php if ($d['statut'] === 'valide'): ?><form method="post"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $d['id'] ?>"><button class="btn clair" name="action" value="suspendre">Suspendre</button></form><?php endif; ?>
<?php if ($d['statut'] !== 'refuse'): ?><form method="post"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $d['id'] ?>"><button class="btn clair" name="action" value="refuser">Refuser</button></form><?php endif; ?>
      <form method="post" onsubmit="return confirm('Supprimer définitivement ce dessin, ses données et ses votes ?')"><?= $champ_csrf ?><input type="hidden" name="id" value="<?= (int) $d['id'] ?>"><button class="btn clair" name="action" value="supprimer">Supprimer</button></form>
    </div>
  </div>
<?php endforeach; ?>

  <h2 id="mails">E-mails aux participants</h2>
<?php $nbEnvois = (int) db()->query('SELECT COUNT(*) FROM envois WHERE ok = 1')->fetchColumn(); $nbEchecs = (int) db()->query('SELECT COUNT(*) FROM envois WHERE ok = 0')->fetchColumn(); $nbDesabo = (int) db()->query('SELECT COUNT(DISTINCT email) FROM dessins WHERE mails = 0')->fetchColumn(); ?>
  <p>État : <b><?= mails_actifs() ? 'activés' : 'désactivés (rien ne part)' ?></b> · <?= $nbEnvois ?> envoyé(s) · <?= $nbEchecs ?> échec(s) · <?= $nbDesabo ?> désinscrit(s)</p>
  <p class="aide">Chaque adulte reçoit un message à la réception du dessin, un autre à sa publication, puis un message tous les deux jours pendant les votes (conseils et point sur le classement), jusqu’aux résultats. Les envois programmés partent le matin, à partir de <?= MAILS_HEURE ?> h. Un lien de désinscription figure dans chaque message.</p>
  <table class="classement" style="max-width:760px"><thead><tr><th>Quand</th><th>Objet</th><th></th></tr></thead><tbody>
<?php foreach (mails_modeles() as $cle => $quand): ?><tr><td style="width:auto"><?= h($quand) ?></td><td><?= h(mails_contenu($cle, mails_exemple())[0]) ?></td><td><a href="admin.php?apercu=<?= h($cle) ?>" target="_blank" rel="noopener">Aperçu</a></td></tr>
<?php endforeach; ?>
  </tbody></table>
  <form method="post" class="boite"><?= $champ_csrf ?><input type="hidden" name="action" value="mails-essai">
    <p><label for="m-cle">Recevoir un message d’essai</label><select id="m-cle" name="cle"><?php foreach (mails_modeles() as $cle => $quand): ?><option value="<?= h($cle) ?>"><?= h(mails_contenu($cle, mails_exemple())[0]) ?></option><?php endforeach; ?></select></p>
    <p><label for="m-vers">Votre adresse e-mail</label><input id="m-vers" name="vers" type="email" required></p>
    <p><button class="btn clair" type="submit">M’envoyer l’essai</button></p>
  </form>
  <form method="post" class="boite"><?= $champ_csrf ?><input type="hidden" name="action" value="mails-reglages">
    <p><label for="m-de">Adresse d’expédition</label><input id="m-de" name="de" type="email" required value="<?= h(mails_expediteur()) ?>"></p>
    <p class="case"><input id="m-actif" name="actif" type="checkbox" value="1"<?= mails_actifs() ? ' checked' : '' ?>><label for="m-actif">Activer l’envoi automatique des e-mails</label></p>
    <p class="aide">Avant d’activer : envoyez-vous un essai et vérifiez qu’il arrive bien dans la boîte de réception. Si vous modifiez les dates du concours pour un essai, désactivez d’abord les e-mails, sinon les participants recevront les messages correspondants.</p>
    <p><button class="btn rouge" type="submit">Enregistrer</button></p>
  </form>
<?php if (mails_actifs()): ?>  <form method="post"><?= $champ_csrf ?><button class="btn clair" name="action" value="mails-tournee">Envoyer maintenant les messages du jour</button></form>
<?php endif; ?>

  <h2 id="dates">Dates du concours</h2>
<?php $dt = dates(); if ($dt['essai']): ?>
  <p class="alerte"><b>Dates modifiées.</b> Le site public suit ces dates, pour tous les visiteurs. Dates officielles&nbsp;: dépôts jusqu’au <?= fr_date(JEU_FIN_DEPOTS) ?>, votes jusqu’au <?= fr_date(JEU_FIN_VOTES) ?>.</p>
<?php endif; ?>
  <form method="post" class="boite"><?= $champ_csrf ?><input type="hidden" name="action" value="dates">
    <p><label for="d-depots">Dernier jour pour déposer un dessin</label><input id="d-depots" name="depots" type="date" required value="<?= h($dt['depots']) ?>"></p>
    <p><label for="d-votes">Dernier jour pour voter</label><input id="d-votes" name="votes" type="date" required value="<?= h($dt['votes']) ?>"></p>
    <p class="aide">Les votes ouvrent le lendemain du dernier jour des dépôts, à minuit. Pour essayer les votes dès maintenant, choisissez hier comme dernier jour des dépôts. Attention&nbsp;: le changement s’applique aussitôt au site public, et les dépôts sont fermés pendant la phase de votes.</p>
    <p><button class="btn rouge" type="submit">Enregistrer les dates</button></p>
  </form>
<?php if ($dt['essai']): ?>
  <form method="post"><?= $champ_csrf ?><button class="btn clair" name="action" value="dates-officielles">Revenir aux dates officielles</button></form>
<?php endif; ?>
  <form method="post" class="boite" autocomplete="off" onsubmit="return confirm('Effacer définitivement tous les votes ?')"><?= $champ_csrf ?><input type="hidden" name="action" value="vider-votes">
    <p><label for="conf">Effacer tous les votes (après un essai)</label><input id="conf" name="confirmation" type="text" placeholder="Écrivez EFFACER" autocomplete="off"></p>
    <p class="aide">Remet tous les compteurs à zéro. Les dessins et les participants ne sont pas touchés. Action définitive.</p>
    <p><button class="btn clair" type="submit">Effacer les votes</button></p>
  </form>

  <h2>Réglages</h2>
  <form method="post" class="boite" autocomplete="off"><?= $champ_csrf ?><input type="hidden" name="action" value="mdp">
    <p><label for="nmdp">Changer le mot de passe</label><input id="nmdp" name="mdp" type="password" required minlength="12" autocomplete="new-password"></p>
    <p><button class="btn clair" type="submit">Changer</button></p>
  </form>
  <p class="diag">Données rangées dans <code><?= h(dossier()) ?></code> (<?= str_starts_with(dossier(), __DIR__) ? '<b>dans le dossier public : à signaler</b>' : 'hors du dossier public' ?>) · PHP <?= h(PHP_VERSION) ?> · traitement d’image : <?= function_exists('imagecreatefromjpeg') ? 'oui' : '<b>absent</b>' ?> · texte sur les images de partage : <?= function_exists('imagettftext') ? 'oui' : '<b>absent</b> (le dessin seul est partagé)' ?> · adresse vue par le serveur : <code><?= h($_SERVER['REMOTE_ADDR'] ?? '') ?></code>, retenue : <code><?= h(ip_brute()) ?></code></p>
  <form method="post"><?= $champ_csrf ?><button class="btn clair" name="action" value="deconnexion">Se déconnecter</button></form>
<?php endif; ?>
</main>
</body>
</html>
