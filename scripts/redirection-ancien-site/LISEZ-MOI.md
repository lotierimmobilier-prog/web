# Rediriger lotier-immobilier.com vers lotier.immo

`htaccess-complet.txt` est le fichier `.htaccess` COMPLET de l'ancien site : le bloc de redirection, puis les blocs
« Really Simple Security » et « WordPress » qui s'y trouvaient déjà.

## Pose
1. Par FTP, à la racine de l'ancien site, garder une copie du `.htaccess` actuel s'il existe encore.
2. Envoyer le fichier, puis le renommer SUR LE SERVEUR (clic droit, Renommer dans le logiciel FTP) en `.htaccess`, avec le point au début et sans `.txt`.
3. Vérifier : `https://www.lotier-immobilier.com/nos-biens/` doit mener à `https://lotier.immo/nos-annonces/`, et `/wp-admin/` doit rester accessible.

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
- Testé sur un Apache local. Cette version n'utilise ni le drapeau `S=` ni `REDIRECT_STATUS`, pour fonctionner aussi sur LiteSpeed.
