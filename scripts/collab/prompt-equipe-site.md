# Prompt pour Collab : publier toute l'équipe sur le site, avec validation de l'administrateur

À coller dans Collab (ou à donner à l'équipe qui le développe). Le site https://lotier.immo lit la liste publique `GET /api/public/v1/agents`
chaque nuit et à chaque clic sur « Publier ». Aujourd'hui cette liste ne contient que les agents commerciaux qui ont des annonces : il manque
les associés, les gestionnaires, les alternants, et des agents sans annonce (par exemple Marie Milla et Jonathan Gasser).

## Ce qu'il faut

1. **Tous les utilisateurs peuvent être publiés**, quel que soit leur rôle (agent commercial, associé, gérant, gestionnaire locatif, gestionnaire
   de copropriété, assistant, alternant…) et **même sans annonce ni mandat**.
2. **Rien n'est publié sans validation de l'administrateur.** Dans la fiche de chaque utilisateur, un bloc « Page du site » :
   - une case cochée par l'utilisateur : « J'accepte la publication de ma photo, de mon téléphone et de mon e-mail sur le site » ;
   - un interrupteur réservé à l'ADMIN : « Validé pour le site ». Tant qu'il n'est pas activé, l'utilisateur n'apparaît pas dans l'API publique.
   - L'administrateur voit la liste des profils en attente de validation, avec un aperçu.
3. **L'API publique `GET /api/public/v1/agents` renvoie tous les utilisateurs validés**, avec, en plus des champs actuels :

| Champ | Type | Rôle |
| --- | --- | --- |
| `statut` | texte | `independant` (agent commercial), `associe`, `salarie`, `alternant`. Déjà présent pour les agents. |
| `poste` | texte | Intitulé affiché sur le site pour les profils non commerciaux : « Gestionnaire locatif », « Associé », « Alternante en gestion »… |
| `validation_admin` | booléen | Toujours `true` dans la réponse (les autres ne sont pas renvoyés). Le site ignore un profil où il vaut `false`. |
| `afficher_sur_site` | booléen | `false` retire le profil du site sans le supprimer de Collab. |
| `accord_publication` | booléen | L'accord de l'utilisateur (voir point 2). |
| `mentions_legales` | objet | Pour les agents commerciaux seulement : `{ "rsac": "...", "rsac_ville": "..." }`. |
| `ordre` | nombre | Facultatif : ordre d'affichage sur la page de l'équipe. |

Les champs déjà demandés pour la fiche (présentation, spécialités, réseaux, lien Google, mots-clés, photo 600 × 600) restent valables :
voir `prompt-profil-agent.md`.

## Ce que fait le site (déjà en place)

- Un profil `independant` s'affiche comme « Agent commercial indépendant », avec ses annonces et sa mention RSAC.
- Les autres profils s'affichent avec leur `poste` (à défaut, le début du champ `fonction`), sans rubrique d'annonces ni mention RSAC.
- Un profil sans annonce est publié normalement.
- Un profil où `validation_admin` ou `afficher_sur_site` vaut `false` n'est pas publié.

## Règles

- Lecture publique, sans clé, comme le reste de l'API publique. Aucune donnée personnelle au-delà de ce que l'utilisateur a accepté de publier.
- Un utilisateur désactivé ou parti disparaît de la liste.
