# Prompt pour Collab : compléter la fiche « agent » pour la page publique du site

À coller dans Collab (ou à donner à l'équipe qui le développe). Le site https://lotier.immo lit déjà la liste publique des agents (`GET /api/public/v1/agents`). Pour la page individuelle de chaque agent (`/nos-agents/<prénom-nom>/`), il manque quelques champs. Le site les lit dès qu'ils existent dans la réponse ; en attendant, ils peuvent être saisis dans `data/agents-config.json` du dépôt du site.

## Champs à ajouter à chaque agent (réponse publique, tous facultatifs)

| Champ | Type | Contenu |
|---|---|---|
| `presentation` | texte | Présentation de l'agent, 2 à 6 phrases, plusieurs paragraphes possibles (séparés par un saut de ligne). Aujourd'hui `bio_courte` est tronquée avec « … » : fournir le texte complet. |
| `specialites` | liste de codes | Parmi : `vente`, `location`, `gestion`, `syndic`, `estimation`, `investissement`, `maison`, `appartement`, `commerce`, `terrain`, `neuf`, `prestige`. Le site affiche une icône par code. |
| `reseaux` | objet | Adresses complètes en `https://` : `facebook`, `instagram`, `linkedin`, `tiktok`, `youtube`, `whatsapp`. Seuls les réseaux renseignés s'affichent. |
| `lien_google` | adresse https | Page Google (fiche ou avis) de l'agent. |
| `mots_cles` | liste de textes | Expressions pour le référencement, par exemple « agent immobilier Béziers », « estimation gratuite Béziers », « gestion locative Narbonne » (3 à 8 par agent). |
| `rsac` | texte | Numéro d'immatriculation au registre des agents commerciaux (obligatoire pour afficher un agent commercial indépendant). |

Aussi : un champ `a_la_une` (booléen) et `ordre` (nombre) pour mettre un agent en avant et choisir l'ordre d'affichage ; `photo_url` en 600 × 600 px minimum, même cadrage pour tous (aujourd'hui 256 px maximum).

## Écran dans Collab
Dans la fiche d'un agent, un onglet « Page du site » avec ces champs, un aperçu de la page publique et un interrupteur « Afficher sur le site ». L'enregistrement se fait en brouillon ; la mise en ligne passe par le bouton « Publier » existant.

## Règles
- Lecture publique, sans donnée personnelle autre que celle que l'agent a acceptée de publier : prévoir une case « J'accepte la publication de ma photo, de mon téléphone et de mon e-mail sur le site ».
- Un agent sans accord ou sans RSAC n'est pas exposé par l'API publique.
- Le texte rendu vient des agents : le site l'affiche sans HTML.
