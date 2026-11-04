# Mise en ligne de la v2 sur lotier-immobilier.com

Principe : la v2 se **superpose** à WordPress, elle ne le remplace pas. WordPress continue de servir les fiches
des biens (`/propriete/…`), les mentions légales, la FAQ, les pages mandataires, la connexion ICS et l'import des annonces.
Seules la page d'accueil et les nouvelles pages (liste dans `release/`) sont servies par les fichiers statiques.

## 0. Avant de commencer
- [ ] Faire une **sauvegarde complète** (fichiers + base de données) depuis l'hébergeur.
- [ ] Télécharger l'ancien `.htaccess` et le garder en lieu sûr.
- [ ] Choisir un moment calme (soir ou week-end).

## 1. À compléter / décider (bloquant)
- [x] **Mentions légales** : reprises du site actuel dans `mentions-legales/` (SIRET, carte pro, garanties, médiateur). À corriger : la phrase CNIL « via la société , » (nom vide à la source), l'hébergeur (absent), le RCS.
- [ ] **Page Estimer** : coller le code de l'outil d'estimation dans `estimer/index.html` (repère « COLLER ICI »).
- [ ] **Devenir agent** : compléter statut / rémunération / formation dans `devenir-agent/index.html`. La page renvoie vers `rejoindre.lotier-immobilier.com` : vérifier que le lien fonctionne (https).
- [ ] **Relire les 3 articles** de `actualites/` et la page `gestion-locative-occitanie/`.
- [ ] **Adresses des autres agences** (Montpellier, Nîmes, Carcassonne…) si elles existent.
- [x] Logo, favicon et image de partage : en place (`v2/img/`). Les photos d'ambiance sont générées par IA : voir `v2/img/CREDITS.md` ; les remplacer par de vraies photos de la région/de l'agence dès que possible.
- [ ] Vérifier les positions de `data/communes.json` (petites communes approximatives).
- [ ] Politique de confidentialité (`/politique-de-confidentialite/` renvoie 404 aujourd'hui) : à créer (Complianz peut la générer).

## 2. Fabriquer le dossier à déposer
```bash
python3 scripts/scrape_biens.py      # rafraîchit les annonces (data/biens.json)
python3 scripts/build_release.py     # crée release/ (noindex retiré, URLs à la racine)
python3 scripts/check_links.py release
```

## 3. Déposer sur l'hébergement
- [ ] Comparer les dossiers de `release/` avec ceux déjà présents à la racine du serveur
      (`actualites, biens, carte, contact, data, devenir-agent, espace-client, estimer, favoris, fonts, gestion-locative-occitanie, img, mentions-legales, syndic, vendor, villes`).
      **Ne jamais écraser un dossier existant** sans l'avoir regardé (ex. `/recrutement/` existe déjà et n'est volontairement pas touché).
- [ ] Téléverser le **contenu** de `release/` à la racine (FTP / gestionnaire de fichiers), dont `index.html`, `biens.js`, `carte.js`, `style.css`, `contact/envoyer.php`.
- [ ] Ajouter `htaccess-final.txt` en tête du `.htaccess` (+ en-têtes de sécurité de `audit-lotier/3-htaccess.txt`).
- [ ] Ajouter `audit-lotier/4-securite-wordpress.php` dans `wp-content/mu-plugins/` (ferme l'API des utilisateurs, XML-RPC).

## 4. Tests juste après la mise en ligne (5 minutes)
- [ ] `/` affiche la nouvelle page ; `/biens/`, `/carte/`, `/favoris/`, `/villes/nimes/` chargent leurs annonces.
- [ ] Clic sur une annonce : la fiche WordPress `/propriete/…` s'ouvre.
- [ ] `/nos-biens/` → redirige vers `/biens/` (301) ; `/syndic-de-copropriete/` → `/syndic/`.
- [ ] **Formulaire de contact** : envoi réel, le mail arrive bien à `contact@lotier-immobilier.com` (vérifier les spams).
- [ ] Mobile : menu, recherche, carte, favoris.
- [ ] `view-source:` de l'accueil : plus de `noindex`.
- [ ] Mentions légales, connexion ICS, `/wp-admin/` : toujours accessibles.

## 5. Référencement
- [ ] Search Console : envoyer `https://www.lotier-immobilier.com/sitemap-v2.xml` (en plus de `wp-sitemap.xml`).
- [ ] Demander l'indexation de l'accueil et des 6 pages de villes.
- [ ] Google Business Profile : lien du site mis à jour, vérifier nom/adresse/téléphone.
- [ ] Suivre 4 semaines : pages indexées, erreurs 404, positions « agence immobilière Béziers / Nîmes… ».

## 6. Retour arrière (si problème)
1. Remettre l'ancien `.htaccess`.
2. Supprimer `index.html` de la racine (WordPress reprend l'accueil) et les dossiers ajoutés.
3. Restaurer la sauvegarde si besoin.

## 7. Entretien
- **Annonces, mise à jour automatique** : téléverser `sync-biens.php` à la racine, puis créer une tâche planifiée (cron) chez l'hébergeur, par exemple toutes les heures :
  `php /chemin/du/site/sync-biens.php` (le fichier refuse de s'exécuter depuis un navigateur, et garde l'ancien `data/biens.json` si le résultat est vide ou suspect).
- Le dossier `data/` doit être inscriptible par PHP.
- Limite connue : les fiches détail et les pages WordPress gardent l'ancien habillage tant qu'elles ne sont pas refaites.
