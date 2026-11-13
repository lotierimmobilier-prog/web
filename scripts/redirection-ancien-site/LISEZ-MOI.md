# Rediriger lotier-immobilier.com vers lotier.immo

Le fichier `htaccess-redirection.txt` contient un bloc à coller **tout en haut** du fichier `.htaccess` de l'ancien site
(à la racine du site sur le FTP, avant la ligne `# BEGIN WordPress`). Il ne remplace pas le `.htaccess` existant.

## Pose
1. Par FTP, télécharger le `.htaccess` actuel de l'ancien site et en garder une copie.
2. Ouvrir ce fichier, coller le contenu de `htaccess-redirection.txt` au tout début, enregistrer, renvoyer sur le FTP.
3. Vérifier : `https://www.lotier-immobilier.com/` doit mener à `https://lotier.immo/`, et `/wp-admin/` doit rester accessible.

Pour revenir en arrière : remettre la copie du `.htaccess`.

## Ce qui est redirigé (redirection permanente, 301)
- `/propriete/<annonce>/` vers `https://lotier.immo/annonces/<annonce>/` (même adresse) ; `/nos-biens/` vers `/nos-annonces/`.
- Gestion, syndic, mandataire, mentions légales, pages de présentation : vers la page équivalente.
- Espaces clients de l'ancien site (connexion, espace propriétaire) : vers `/mylotier/`.
- Tout le reste : vers l'accueil.

## Ce qui n'est PAS redirigé
- `/wp-admin/`, `/wp-login.php`, les photos (`/wp-content/`), la synchronisation ImmoWP : WordPress continue de fonctionner.
- Le robot du nouveau site (`LotierV2-sync`), qui lit les annonces de l'ancien site chaque nuit.
- Un administrateur connecté à WordPress voit toujours l'ancien site.
- `collab.lotier-immobilier.com` et les e-mails `@lotier-immobilier.com` ne sont pas concernés.

## À savoir
- L'ancien WordPress doit rester en ligne : c'est lui qui reçoit les annonces (ImmoWP / Hektor) que le nouveau site importe.
- Une annonce retirée de la vente affichera la page « introuvable » du nouveau site.
- Testé sur un Apache local avec un `.htaccess` WordPress standard à la suite du bloc.
