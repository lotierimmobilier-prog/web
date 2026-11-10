# Générateur du site

Les pages HTML, le sitemap, `llms.txt`, `.htaccess` et les versions Markdown (`.md`) sont **générés** par ces scripts Python. Ne modifiez pas directement les fichiers générés : modifiez le script, puis régénérez.

```bash
pip install pillow          # une seule fois
python3 scripts/generateur/build_all.py
```

- `common.py` : coquille commune (en-tête, pied de page, données de l'agence, JSON-LD, boutons d'appel à l'action).
- `build_site.py` : page d'accueil. `build_pages.py` : villes, blog, sitemap, `llms.txt`, `robots`. `build_misc.py` : plan du site, 404, `.htaccess`.
- `build_rejoindre.py`, `build_comparatif.py`, `build_mylotier.py`, `build_agents.py`, `build_services.py`, `build_about.py` : pages dédiées.
- `build_markdown.py` : jumeaux `.md` de chaque page (servis aux agents avec `Accept: text/markdown`). À lancer en dernier.
- `content_*.py`, `extra*.py` : textes des articles, villes et FAQ.

`../seo_audit.py` : audit SEO, lancé en dernier par `build_all.py`, écrit `data/seo-report.json` (lu par Collab).

`../ai_visibility_audit.py` : audit « visibilité dans les IA » (robots IA, llms.txt, Markdown, données structurées), écrit `data/ai-visibility-report.json` ; option `--live` pour contrôler le site en ligne.

Fichiers écrits à la main (non générés) : `robots.txt`, `.well-known/`, `mcp/`, `css/`, `js/`, `data/`, `assets/`.
Le dossier `scripts/` n'est pas servi au public (404 via `.htaccess`).
Après régénération, relire `git diff` : un lancement sans modification de contenu ne doit rien changer.

## Publication depuis Collab (étape S0, 09/11/2026)

Le bouton « Publier » de Collab fige les contenus du site et lance le workflow `.github/workflows/publier-site.yml` :
1. `scripts/recuperer_contenu.py` lit l'instantané (lecture publique de Collab) et l'écrit dans `data/contenu.json` (absent tant que Collab n'a rien publié : le générateur garde alors tous ses textes) ;
2. `scripts/generateur/build_all.py` régénère le site ;
3. `scripts/controle_publication.py` le contrôle (pages essentielles, titres, liens internes, perte de pages, format des contenus) — s'il refuse, **rien n'est publié** ;
4. s'il y a du nouveau, commit sur `main` (Hostinger redéploie) ; sinon aucun commit.

La mise à jour de nuit des annonces (`maj-annonces.yml`) reprend les mêmes étapes et partage le même verrou : jamais deux écritures sur `main` en même temps.
Le titre de l'exécution (« Publier le site — Collab n°N ») est un contrat avec Collab (`src/lib/site-publication.ts`) : ne pas le modifier sans modifier Collab.

## Le blog est géré depuis Collab (étape « Blog », 10/11/2026)

`contenu.py` lit `data/contenu.json` (écrit par `scripts/recuperer_contenu.py`). Quand Collab « gère » les articles (`gere: ["articles"]`),
**Collab fait foi** : les articles viennent de lui (titre, textes, FAQ, photo, date…), un article absent de Collab n'est pas publié et sa page
(`blog/<adresse>.html` et `.md`) est supprimée. Tant que Collab ne gère pas le blog, le générateur garde les textes de `content_articles.py`
et `extra*.py` (repli). Un article invalide (catégorie, photo ou ville inconnue, section vide…) **arrête la génération** : rien n'est publié.

Vérifier qu'un changement de générateur n'altère pas le site : `python3 scripts/exporter_articles.py /tmp/articles.json`, puis écrire
`data/contenu.json` avec ces articles (`{"contenu": {"schema": 1, "gere": ["articles"], "articles": [...], "pages": [], "reglages": {}, "medias": []}}`),
relancer `build_all.py` : `git status` ne doit montrer AUCUN fichier du site modifié. (`LOTIER_CONTENU_STATIQUE=1` ignore `data/contenu.json`.)
