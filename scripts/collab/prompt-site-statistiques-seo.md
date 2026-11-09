# Prompt pour Collab : module « Site web > Statistiques et référencement »

À coller dans Collab (ou à donner à l'équipe qui le développe). Le site https://lotier.immo est statique ; Collab ne le modifie pas ici, il **lit** des données et les présente.

## Objectif
Un écran réservé aux administrateurs, en français, qui répond à trois questions : le site est-il techniquement sain ? Comment est-il vu sur Google ? Combien de personnes viennent et combien demandent une estimation ?

## Sources de données

1. **Audit technique du site (disponible maintenant)**
   - `GET https://lotier.immo/data/seo-report.json`, public, sans clé, mis à jour à chaque régénération du site.
   - Contenu : `resume` (pages auditées, erreurs, avertissements, problèmes par type), `fichiers` (robots.txt, sitemap, llms.txt, Content-Signal, carte MCP, pages Markdown), `pages[]` (url, titre, description, nombre de mots, H1, images, liens, `problemes[]` avec `niveau` erreur/avertissement, `code`, `message`).
   - À faire : relire le fichier chaque jour, **conserver un historique** (date, nb d'erreurs, nb d'avertissements) pour tracer l'évolution.

2. **Google Search Console (à brancher : en attente de la vérification du domaine)**
   - API Search Analytics, lecture seule (`webmasters.readonly`), propriété `sc-domain:lotier.immo`.
   - À afficher : clics, impressions, CTR, position moyenne, par page, par requête, par pays/appareil, sur 7/28/90 jours ; comparaison avec la période précédente.
   - Sitemaps : état de `https://lotier.immo/sitemap.xml`, pages indexées / non indexées et motifs.

3. **Performance (Core Web Vitals)**
   - API PageSpeed Insights (clé API Google gratuite) sur une liste de pages (accueil, villes, blog), mobile et ordinateur : LCP, CLS, INP, score. Relevé hebdomadaire avec historique.

4. **Fréquentation et demandes**
   - Aucun outil de mesure n'est installé sur le site à ce jour. Décision à prendre (voir plus bas). Dès qu'un outil existe : visiteurs, pages vues, sources, pages d'entrée.
   - Demandes d'estimation et appels : à relier au flux de demandes déjà décrit dans le prompt « estimation / agents » (webhook du site vers Collab) pour calculer un taux de transformation.

## Écrans attendus
- **Tableau de bord** : note de santé du site (erreurs, avertissements, tendance), clics et impressions Google sur 28 jours, 3 pages à corriger en priorité, état du sitemap.
- **Audit technique** : liste filtrable par gravité et par type de problème, ouverture de la page concernée, message en clair, bouton « Marquer comme traité ».
- **Pages** : tableau (page, titre, description, mots, clics, impressions, position), tri et recherche.
- **Requêtes** : requêtes Google, avec celles qui gagnent ou perdent des positions.
- **Alertes** (courriel ou notification Collab) : nouvelle erreur d'audit, page qui sort de l'index, chute de clics de plus de 30 % sur 7 jours, Core Web Vitals dégradés.

## Règles
- Lecture seule sur le site et sur Google ; aucune clé ni jeton stocké côté navigateur.
- Accès réservé au rôle administrateur ; chaque consultation et chaque réglage journalisés.
- Données personnelles : uniquement des statistiques agrégées. Pas d'adresse IP ni d'identifiant de visiteur.
- Si une source est indisponible, l'écran l'indique clairement et affiche les autres.

## Décisions à prendre avant de brancher la fréquentation
- Outil de mesure **sans cookie** (Plausible, Matomo configuré sans cookie ou statistiques serveur) : recommandé, car il évite le bandeau de consentement. Lequel, hébergé où ?
- Qui crée le compte Google (Search Console, clé PageSpeed) et donne l'accès en lecture à Collab ?
