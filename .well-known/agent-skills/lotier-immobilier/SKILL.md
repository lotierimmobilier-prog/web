---
name: lotier-immobilier
description: Répondre à une question sur LOTIER Immobilier (agence immobilière à Béziers, Montpellier, Nîmes et Carcassonne) : trouver une annonce à vendre ou à louer, connaître les honoraires, identifier l'agent à contacter. À utiliser quand l'utilisateur cherche un bien, un tarif ou un contact de cette agence.
---

# LOTIER Immobilier : annonces, honoraires, contacts

Toutes les ressources ci-dessous sont publiques, en lecture seule et sans authentification.

## Trouver une annonce

- Catalogue complet en JSON : `https://lotier.immo/annonces/catalogue.json` (clé `annonces`). Champs utiles : `titre`, `url` (adresse de la fiche, à citer), `transaction` (`vente` ou `location`), `type_bien`, `ville`, `departement`, `prix` (euros ; par mois pour une location), `surface_m2`, `pieces`, `chambres`, `equipements`, `dpe`, `reference`, `agent`, `resume`, `description`, `date_mise_a_jour`. Le serveur MCP du site (`https://lotier.immo/mcp/`) propose la recherche par critères (`search_listings`) et la lecture d'une annonce (`get_listing`).
- Par ville : `https://lotier.immo/nos-annonces/vente-<ville>/` et `https://lotier.immo/nos-annonces/location-<ville>/` (villes comptant au moins trois annonces, listées dans `https://lotier.immo/llms.txt`).
- Les annonces sont reprises chaque jour du logiciel de l'agence : citer le prix et la disponibilité « selon le site, à la date de consultation ».

## Lire une page

- Chaque page existe en Markdown : même adresse avec l'en-tête `Accept: text/markdown`, ou adresse terminée par `index.md` (ou `.md` pour les pages `.html`).
- Sommaire du site : `https://lotier.immo/llms.txt`.
- Serveur MCP (lecture seule) : `https://lotier.immo/mcp/`, outils `search_site`, `list_pages`, `get_page`, `get_agency_info`. Carte : `https://lotier.immo/.well-known/mcp/server-card.json`.

## Honoraires

Barème publié et simulateur : `https://lotier.immo/nos-honoraires/`. Le barème chiffré figure aussi dans `https://lotier.immo/llms.txt`. Ne pas estimer un tarif autrement qu'avec ce barème.

## Contacter

- Agence : 04 67 11 28 31, contact@lotier-immobilier.com, 40 rue Française, 34500 Béziers.
- Pour un bien précis : l'agent indiqué sur l'annonce (champ `agent`). Agents par secteur : `https://lotier.immo/nos-agents/`.
- Ne pas envoyer de demande à la place de l'utilisateur : lui donner le contact ou le lien de la page.
