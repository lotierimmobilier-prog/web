// Affiche les annonces lues dans data/biens.json (généré par scripts/scrape_biens.py).
(function () {
  var root = document.querySelector('[data-biens]');
  if (!root) return;
  var limit = parseInt(root.getAttribute('data-limit') || '0', 10);
  var withFilters = root.hasAttribute('data-filtres');
  var cityOnly = root.getAttribute('data-ville');
  var onlyFavs = root.hasAttribute('data-favoris');
  var dataUrl = root.getAttribute('data-src');
  var list = root.querySelector('.biens-liste');
  var count = root.querySelector('.biens-count');
  var all = [];
  var eur = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });

  function safe(u) { return /^https:\/\/(www\.)?lotier-immobilier\.com\//.test(u || '') ? u : '#'; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }

  function titre(t) {
    t = t.replace(/^\s*(à|a)\s+(louer|vendre)\s*[-–:]?\s*/i, '');
    var letters = t.replace(/[^A-Za-zÀ-ÿ]/g, '');
    if (letters.length > 6 && letters === letters.toUpperCase()) t = t.toLowerCase();
    return t.charAt(0).toUpperCase() + t.slice(1);
  }

  var KEY = 'lotier_favoris';
  function favs() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function saveFavs(l) { try { localStorage.setItem(KEY, JSON.stringify(l)); } catch (e) {} }
  function isFav(u) { return favs().indexOf(u) > -1; }
  function toggleFav(u) { var l = favs(), i = l.indexOf(u); if (i > -1) l.splice(i, 1); else l.push(u); saveFavs(l); return i === -1; }
  function favButton(b, onChange) {
    var btn = el('button', 'fav'); btn.type = 'button';
    function paint() { var on = isFav(b.url); btn.setAttribute('aria-pressed', on); btn.textContent = on ? '♥' : '♡'; btn.setAttribute('aria-label', (on ? 'Retirer des favoris : ' : 'Ajouter aux favoris : ') + titre(b.titre)); }
    btn.addEventListener('click', function () { toggleFav(b.url); paint(); if (onChange) onChange(); });
    paint(); return btn;
  }

  function card(b) {
    var wrap = el('div', 'bien-carte');
    wrap.appendChild(cardLink(b));
    wrap.appendChild(favButton(b, onFavChange));
    return wrap;
  }

  function cardLink(b) {
    var a = el('a', 'bien'); a.href = safe(b.url);
    var fig = el('div', 'bien-img');
    if (b.image) { var im = el('img'); im.src = safe(b.image); im.alt = titre(b.titre); im.loading = 'lazy'; im.width = 400; im.height = 300; fig.appendChild(im); }
    if (b.badges && b.badges.length) fig.appendChild(el('span', 'bien-badge', b.badges[0]));
    a.appendChild(fig);
    var body = el('div', 'bien-body');
    body.appendChild(el('p', 'bien-prix', eur.format(b.prix) + ' €' + (b.type === 'location' ? ' / mois' : '')));
    body.appendChild(el('h3', null, titre(b.titre)));
    body.appendChild(el('p', 'bien-ville', b.ville));
    var m = [];
    if (b.surface) m.push(String(b.surface).replace('.', ',') + ' m²');
    if (b.chambres) m.push(b.chambres + ' ch.');
    if (b.sdb) m.push(b.sdb + ' sdb');
    body.appendChild(el('p', 'bien-meta', m.join(' · ')));
    a.appendChild(body);
    return a;
  }

  function onFavChange() { if (onlyFavs) filterAndRender(); }

  function render(items) {
    list.textContent = '';
    var shown = limit ? items.slice(0, limit) : items;
    shown.forEach(function (b) { list.appendChild(card(b)); });
    if (count) count.textContent = items.length + (items.length > 1 ? ' biens' : ' bien');
    if (!items.length) list.appendChild(el('p', null, cityOnly ? 'Pas d\'annonce en ligne à ' + cityOnly + ' pour le moment : contactez-nous, nous avons peut-être des biens avant publication.' : 'Aucun bien ne correspond à ces critères.'));
  }

  function filterAndRender() {
    var l = favs(); var items = all.filter(function (b) { return l.indexOf(b.url) > -1; });
    render(items);
    if (!items.length) { list.textContent = ''; var p = el('p', null, 'Aucun favori pour le moment. Touchez le cœur sur une annonce pour la retrouver ici.'); list.appendChild(p); }
  }

  function filter() {
    var f = {};
    root.querySelectorAll('[data-f]').forEach(function (i) { f[i.getAttribute('data-f')] = i.value; });
    var out = all.filter(function (b) {
      if (f.type && b.type !== f.type) return false;
      if (f.ville && b.ville !== f.ville) return false;
      if (f.max && b.prix > parseFloat(f.max)) return false;
      return true;
    });
    var s = f.tri;
    if (s === 'prix') out.sort(function (a, b) { return a.prix - b.prix; });
    if (s === '-prix') out.sort(function (a, b) { return b.prix - a.prix; });
    render(out);
  }

  fetch(dataUrl).then(function (r) { return r.json(); }).then(function (d) {
    all = d.biens || [];
    if (cityOnly) all = all.filter(function (b) { return b.ville === cityOnly; });
    if (onlyFavs) { filterAndRender(); return; }
    if (withFilters) {
      var sel = root.querySelector('[data-f="ville"]');
      var counts = {};
      all.forEach(function (b) { counts[b.ville] = (counts[b.ville] || 0) + 1; });
      Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a] || a.localeCompare(b, 'fr'); }).forEach(function (v) {
        var o = el('option', null, v + ' (' + counts[v] + ')'); o.value = v; sel.appendChild(o);
      });
      root.querySelectorAll('[data-f]').forEach(function (i) { i.addEventListener('change', filter); });
      var q = new URLSearchParams(location.search);
      ['type', 'ville', 'max'].forEach(function (k) {
        var v = q.get(k), s = root.querySelector('[data-f="' + k + '"]');
        if (v && s) s.value = v;
      });
      filter();
    } else { render(all); }
  }).catch(function () {
    list.textContent = '';
    var p = el('p', null, 'Les annonces sont momentanément indisponibles. '); var l = el('a', null, 'Voir toutes nos annonces');
    l.href = 'https://www.lotier-immobilier.com/nos-biens/'; p.appendChild(l); list.appendChild(p);
  });
})();
