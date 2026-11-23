<?php
// Concours de Noël : dépôt d'un dessin et vote. Réponses en JSON.
declare(strict_types=1);
require __DIR__ . '/lib.php';
require __DIR__ . '/mails.php';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') repondre(['erreur' => 'Méthode non autorisée.'], 405);
$origine = $_SERVER['HTTP_ORIGIN'] ?? '';
$hote = preg_replace('/:\d+$/', '', (string) ($_SERVER['HTTP_HOST'] ?? ''));
if ($origine !== '' && parse_url($origine, PHP_URL_HOST) !== $hote) repondre(['erreur' => 'Demande refusée.'], 403);
$action = (string) ($_POST['action'] ?? '');
$jour = maintenant()->format('Y-m-d');

if ($action === 'depot') {
    if (phase() !== 'depot') repondre(['erreur' => 'Les dépôts sont clos depuis le ' . fr_date(fin_depots()) . '.'], 403);
    if (($_POST['site'] ?? '') !== '' || !jeton_valide((string) ($_POST['jeton'] ?? ''))) repondre(['erreur' => 'Le formulaire a expiré. Rechargez la page, puis recommencez.'], 400);
    $prenom = trim(preg_replace('/\s+/u', ' ', (string) ($_POST['prenom'] ?? '')));
    if (!preg_match('/^[\p{L}][\p{L} \'’-]{1,29}$/u', $prenom)) repondre(['erreur' => 'Indiquez le prénom du dessinateur (lettres uniquement).'], 400);
    $age = filter_var($_POST['age'] ?? '', FILTER_VALIDATE_INT, ['options' => ['min_range' => 3, 'max_range' => 110]]);
    if ($age === false) repondre(['erreur' => 'Indiquez l’âge du dessinateur (à partir de 3 ans).'], 400);
    $email = email_propre((string) ($_POST['email'] ?? ''));
    if (!$email) repondre(['erreur' => 'L’adresse e-mail de l’adulte n’est pas valide.'], 400);
    if (($_POST['adulte'] ?? '') !== '1') repondre(['erreur' => 'Un adulte doit valider la participation.'], 400);
    if (($_POST['reglement'] ?? '') !== '1') repondre(['erreur' => 'Merci d’accepter le règlement du concours.'], 400);
    $lien = mb_substr(trim((string) ($_POST['lien'] ?? '')), 0, 30);
    $cp = trim((string) ($_POST['code_postal'] ?? ''));
    if ($cp !== '' && !preg_match('/^\d{5}$/', $cp)) repondre(['erreur' => 'Le code postal doit compter cinq chiffres.'], 400);
    $projet = (string) ($_POST['projet'] ?? '');
    if (!array_key_exists($projet, JEU_PROJETS)) $projet = '';
    $rappel = ($_POST['rappel'] ?? '') === '1' ? 1 : 0;
    $tel = preg_replace('/[^\d+]/', '', (string) ($_POST['telephone'] ?? ''));
    if ($rappel && !preg_match('/^(\+33|0)[1-9]\d{8}$/', $tel)) repondre(['erreur' => 'Pour être rappelé, indiquez un numéro de téléphone valide.'], 400);
    if (!$rappel) $tel = '';
    $infolettre = ($_POST['infolettre'] ?? '') === '1' ? 1 : 0;

    $q = db()->prepare("SELECT COUNT(*) FROM dessins WHERE ip = ? AND substr(cree_le, 1, 10) = ?"); $q->execute([ip(), $jour]);
    if ((int) $q->fetchColumn() >= JEU_DEPOTS_PAR_IP) repondre(['erreur' => 'Trop de dépôts aujourd’hui depuis cette connexion. Réessayez demain.'], 429);
    $q = db()->prepare("SELECT COUNT(*) FROM dessins WHERE email = ? AND statut != 'refuse'"); $q->execute([$email]);
    if ((int) $q->fetchColumn() >= JEU_DESSINS_PAR_EMAIL) repondre(['erreur' => 'Le nombre maximal de dessins pour cette adresse e-mail est atteint.'], 400);
    $q = db()->prepare("SELECT COUNT(*) FROM dessins WHERE email = ? AND lower(prenom) = lower(?) AND statut != 'refuse'"); $q->execute([$email, $prenom]);
    if ((int) $q->fetchColumn() > 0) repondre(['erreur' => 'Un dessin de ' . $prenom . ' est déjà enregistré : un seul dessin par participant.'], 400);

    $f = $_FILES['dessin'] ?? null;
    if (!$f || ($f['error'] ?? 1) !== UPLOAD_ERR_OK || !is_uploaded_file($f['tmp_name'])) repondre(['erreur' => 'La photo du dessin n’a pas été reçue. Réessayez avec une photo plus légère.'], 400);
    if ($f['size'] > JEU_POIDS_MAX) repondre(['erreur' => 'La photo est trop lourde (12 Mo au plus).'], 400);
    $jeton = bin2hex(random_bytes(8));
    if (!enregistrer_image($f['tmp_name'], $jeton)) repondre(['erreur' => 'Ce fichier n’est pas une photo lisible. Formats acceptés : JPEG, PNG ou WebP.'], 400);

    db()->prepare("INSERT INTO dessins (jeton, prenom, age, categorie, email, lien, code_postal, projet, rappel, telephone, infolettre, cree_le, ip)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        ->execute([$jeton, $prenom, $age, categorie_de((int) $age), $email, $lien, $cp, $projet, $rappel, $tel, $infolettre, maintenant()->format('Y-m-d H:i:s'), ip()]);
    journal('depot', $jeton);
    mails_envoyer('recu', (int) db()->lastInsertId());
    repondre(['ok' => true, 'jeton' => $jeton, 'prenom' => $prenom]);
}

if ($action === 'vote') {
    $ph = phase();
    if ($ph === 'depot') repondre(['erreur' => 'Les votes ouvrent le ' . fr_date(debut_votes()) . '.'], 403);
    if ($ph === 'fini') repondre(['erreur' => 'Les votes sont clos.'], 403);
    if (($_POST['site'] ?? '') !== '') repondre(['erreur' => 'Demande refusée.'], 400);
    $email = email_propre((string) ($_POST['email'] ?? ''));
    if (!$email) repondre(['erreur' => 'Indiquez une adresse e-mail valide pour voter.'], 400);
    $q = db()->prepare("SELECT id, email, prenom FROM dessins WHERE jeton = ? AND statut = 'valide'"); $q->execute([(string) ($_POST['dessin'] ?? '')]);
    $d = $q->fetch();
    if (!$d) repondre(['erreur' => 'Ce dessin est introuvable.'], 404);
    if ($d['email'] === $email) repondre(['erreur' => 'On ne vote pas pour son propre dessin : demandez plutôt à vos proches.'], 403);
    $q = db()->prepare('SELECT COUNT(*) FROM votes WHERE ip = ? AND jour = ?'); $q->execute([ip(), $jour]);
    if ((int) $q->fetchColumn() >= JEU_VOTES_PAR_IP) repondre(['erreur' => 'Trop de votes aujourd’hui depuis cette connexion. Revenez demain.'], 429);
    try {
        db()->prepare('INSERT INTO votes (dessin_id, email, jour, ip, cree_le) VALUES (?, ?, ?, ?, ?)')->execute([$d['id'], $email, $jour, ip(), maintenant()->format('Y-m-d H:i:s')]);
    } catch (PDOException $e) {
        repondre(['erreur' => 'Vous avez déjà voté aujourd’hui avec cette adresse. Revenez demain : un vote par jour.'], 409);
    }
    $q = db()->prepare('SELECT COUNT(*) FROM votes WHERE dessin_id = ?'); $q->execute([$d['id']]);
    repondre(['ok' => true, 'voix' => (int) $q->fetchColumn(), 'prenom' => $d['prenom']]);
}

repondre(['erreur' => 'Action inconnue.'], 400);
