# Site LOTIER Immobilier

Site vitrine statique (HTML, CSS, JavaScript), sans étape de compilation. Direction graphique « Isométrique » : fond clair, verre dépoli, immeuble isométrique animé dont chaque étage est un service.

- `index.html` : page d'accueil (données structurées JSON-LD, balises Open Graph, lien canonique)
- `agence-immobiliere-beziers.html`, `...-montpellier.html`, `...-nimes.html`, `...-carcassonne.html`, `...-narbonne.html`, `...-avignon.html`, `...-agde.html` : une page de référencement par ville (contenu local, questions-réponses, FAQPage)
- `mentions-legales/` et `lotier-rgpd/` : pages obligatoires, aux adresses de l'ancien site (informations reprises de l'ancien site, en `noindex` tant qu'elles ne sont pas confirmées) ; `nos-honoraires/` : barème des honoraires
- `rejoindre/` : page de recrutement (agents commerciaux indépendants), reprise de rejoindre.lotier-immobilier.com ; le `.htaccess` redirige le sous-domaine vers cette page
- `blog/` : 20 articles (BlogPosting, FAQPage) et leur index ; les dates de publication sont des exemples
- `css/styles.css` : styles, avec les jetons de la charte en variables CSS
- `js/main.js` : immeuble isométrique, animations (respectent « réduire les animations »), carrousel, filtres des conseils, recherche, estimation
- `assets/lotier-logo.png` : le vrai logo (recadré, fond transparent) ; `assets/lotier-immobilier-logo.png` : fichier d'origine
- `assets/fonts/` : polices DM Sans et DM Serif Display hébergées sur le site (licence SIL OFL 1.1, voir `OFL.txt`) : aucune requête vers Google Fonts
- `assets/photos/` : photos d'illustration libres de droits (voir `CREDITS.md`)
- `robots.txt`, `sitemap.xml`, `llms.txt` : référencement et assistants IA

Les pages sont générées par les scripts de `scripts/generateur/` (voir `LISEZ-MOI.md` : `python3 scripts/generateur/build_all.py`). Modifier le script, puis régénérer, plutôt que les fichiers HTML.

Mise en ligne : copier le contenu du dossier à la racine de l'hébergement (Hostinger).

À compléter avant publication : photos et annonces réelles, avis, articles, adresses de Montpellier et de Nîmes, horaires, pages légales. Les champs concernés sont écrits entre crochets dans `index.html`. Le domaine `lotier-immobilier.com` (canonical, sitemap, JSON-LD, `llms.txt`) est à confirmer.
