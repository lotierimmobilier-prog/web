# Collab : blocs enrichis pour les articles du blog (tableau, chiffres clés, visuel, sources)

À transmettre à l'équipe (ou à l'assistant) qui développe Collab. Le site lotier.immo sait déjà afficher ces blocs ;
il reste à permettre leur saisie dans Collab, écran « Blog » de l'administration du site.

## Contexte

Un article publié par Collab est une liste de sections ; chaque section porte un titre et des blocs. Collab connaît
aujourd'hui deux types de blocs : `texte` et `liste`. Le générateur du site (`scripts/generateur/contenu.py`) en accepte
désormais quatre de plus. Un bloc inconnu ou invalide arrête la génération : rien n'est publié.

## Les quatre nouveaux blocs

```json
{ "type": "tableau", "entetes": ["Durée du prêt", "CAFPI", "Meilleurtaux"],
  "lignes": [["15 ans", "3,40 %", "3,50 %"], ["20 ans", "3,61 %", "3,70 %"]],
  "legende": "Taux moyens hors assurance, relevés le 17 novembre 2026." }
```
- 2 à 6 colonnes ; chaque ligne a exactement autant de cellules que d'en-têtes ; cellules en texte simple.
- `legende` facultative (300 caractères). La première colonne sert d'intitulé de ligne.

```json
{ "type": "chiffres", "items": [ { "valeur": "5,40 %", "libelle": "Taux d'usure des prêts de 20 ans et plus" } ] }
```
- 2 à 4 chiffres ; `valeur` 24 caractères au plus, `libelle` 120 au plus.

```json
{ "type": "image", "fichier": "dpe-calendrier-location.svg",
  "alt": "Description complète de ce que montre le visuel.", "legende": "Les échéances du DPE." }
```
- `fichier` : nom d'un fichier présent dans `assets/blog/` du site (minuscules, chiffres, tirets ; svg, png, jpg ou webp).
- `alt` obligatoire (500 caractères) : il décrit le contenu du visuel pour les lecteurs d'écran et les assistants IA.
- Tant que Collab ne téléverse pas de fichiers vers le site, proposer la liste des visuels déjà présents dans `assets/blog/`.

```json
{ "type": "sources", "items": [ { "titre": "CAFPI, baromètre des taux, novembre 2026", "url": "https://…" },
                                { "titre": "Arrêté du 13 août 2025", "url": null } ] }
```
- `titre` obligatoire (300 caractères) ; `url` facultative, en `https://` uniquement.

## Champ d'article ajouté

- `dateMaj` (facultatif, `AAAA-MM-JJ`, postérieure ou égale à `date`) : date de dernière mise à jour. Le site affiche
  « Mis à jour le … » et la transmet aux moteurs. À renseigner quand un article d'actualité est corrigé.

## À faire dans Collab

1. Accepter ces quatre blocs et `dateMaj` dans le modèle, la validation et l'export vers le site, avec les mêmes limites que ci-dessus.
2. Les rendre saisissables dans l'éditeur d'article (ajout, déplacement, suppression d'un bloc).
3. Les afficher dans l'aperçu de l'article.
4. Proposer un import d'articles au format JSON (celui que produit `scripts/exporter_articles.py`), pour reprendre les
   articles tenus dans `data/articles-site.json` du site.

## Reprise des articles tenus dans le site

Le fichier `data/articles-site.json` du dépôt du site contient les articles que Collab ne sait pas encore saisir. Ils
s'ajoutent à ceux de Collab ; à adresse (`slug`) égale, celui de Collab l'emporte. Une fois un article repris dans
Collab avec la même adresse, le retirer de ce fichier.
