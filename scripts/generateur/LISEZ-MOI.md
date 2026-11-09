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
