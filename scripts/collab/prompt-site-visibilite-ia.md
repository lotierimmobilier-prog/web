# Prompt pour Collab : module « Site web > Visibilité dans les IA »

À coller dans Collab (ou à donner à l'équipe qui le développe). Le site https://lotier.immo est statique ; Collab **lit** des données et les présente, il ne modifie pas le site ici.

## Objectif
Un écran d'administration, en français, qui répond à quatre questions : les assistants IA peuvent-ils lire le site ? Est-il bien structuré pour être cité ? Des visiteurs arrivent-ils depuis des assistants IA ? LOTIER est-elle citée quand on pose les questions de ses clients ?

## Sources de données

1. **Rapport de préparation IA (disponible maintenant)**
   - `GET https://lotier.immo/data/ai-visibility-report.json`, public, sans clé, mis à jour à chaque régénération du site.
   - Contenu : `score` sur `score_max` et `controles[]` (réussi ou non, points) ; `robots_ia[]` (robot, éditeur, rôle : recherche, consultation à la demande, entraînement ; autorisé ou non) ; `entrainement_autorise_pour` ; `llms_txt` ; `couverture` (Markdown, données structurées) ; `pages[]` avec leurs `problemes`.
   - À faire : relire chaque jour et **garder un historique** (date, score, nombre de problèmes).
   - Sur l'écran, afficher un **point d'attention** tant que `entrainement_autorise_pour` n'est pas vide : le site déclare `ai-train=no` mais `robots.txt` autorise encore ces robots d'entraînement. C'est une décision éditoriale à confirmer.

2. **Trafic venant des IA (à brancher : Umami)**
   - API Umami (clé à fournir) : visites par origine (referrer). Regrouper les origines des assistants : chatgpt.com, chat.openai.com, perplexity.ai, claude.ai, gemini.google.com, copilot.microsoft.com, et les suivantes que l'on observera.
   - À afficher : visites par assistant, pages d'arrivée, évolution sur 28 jours, part dans le trafic total. Mention : certaines IA n'envoient pas d'origine, le chiffre est un minimum.

3. **Suivi des citations (à décider)**
   - Liste de **questions types** gérée dans Collab (par exemple « Quelle agence immobilière à Béziers pour vendre ? », « Combien coûte un syndic de copropriété à Montpellier ? », « Honoraires de gestion locative à Nîmes »).
   - Chaque semaine, poser ces questions à un ou plusieurs assistants et relever : LOTIER est-elle citée, avec quel lien, quels concurrents, quelle formulation.
   - Deux façons de le faire : manuellement par un collaborateur (gratuit, saisie dans Collab), ou automatiquement via les API des assistants (payant, clés à fournir). **À valider avant de développer.**

## Écrans attendus
- **Tableau de bord** : score de préparation IA, tendance, visites venant des IA sur 28 jours, 3 actions prioritaires.
- **Accès des robots** : tableau des robots IA (autorisé, rôle), avec le point d'attention sur l'entraînement.
- **Pages** : pages à corriger (sans version Markdown, sans données structurées, sans FAQ balisée), tri par gravité.
- **Trafic IA** : visites par assistant et par page.
- **Citations** : questions types, résultats par date, évolution du taux de citation.
- **Alertes** : score en baisse, robot de recherche IA bloqué, chute des visites venant des IA.

## Règles
- Lecture seule sur le site ; aucune clé ni jeton côté navigateur.
- Accès réservé au rôle administrateur ; consultations et réglages journalisés.
- Données agrégées uniquement, sans donnée personnelle de visiteur.
- Si une source est indisponible, l'écran l'indique et affiche les autres.

## Décisions à prendre
- Autoriser ou non l'entraînement des modèles sur le contenu du site (aujourd'hui : déclaré refusé, mais non bloqué dans `robots.txt`).
- Suivi des citations : manuel ou automatique, avec quels assistants et quel budget.
- Qui fournit la clé API Umami à Collab.
