// Carte des biens : un repère par commune (position approximative), filtres type / budget.
(function () {
  var box = document.getElementById('carte');
  if (!box || !window.L) return;
  var map = L.map(box, { scrollWheelZoom: false }).setView([43.55, 3.6], 8);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '© <a href="https://www.openstreetmap.org/copyright">contributeurs OpenStreetMap</a>'
  }).addTo(map);
  var layer = L.layerGroup().addTo(map);
  var eur = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
  var biens = [], communes = {};
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function safe(u) { return /^https:\/\/(www\.)?lotier-immobilier\.com\//.test(u || '') ? u : '#'; }

  function draw() {
    layer.clearLayers();
    var type = document.querySelector('[data-c="type"]').value;
    var max = parseFloat(document.querySelector('[data-c="max"]').value) || Infinity;
    var groups = {}, total = 0, sans = 0, pts = [];
    biens.forEach(function (b) {
      if (type && b.type !== type) return;
      if (b.prix > max) return;
      if (!communes[b.ville]) { sans++; return; }
      (groups[b.ville] = groups[b.ville] || []).push(b); total++;
    });
    Object.keys(groups).forEach(function (v) {
      var g = groups[v], pos = communes[v]; pts.push(pos);
      var icon = L.divIcon({ className: 'pin', html: '<span>' + g.length + '</span>', iconSize: [36, 36], iconAnchor: [18, 18] });
      var m = L.marker(pos, { icon: icon, title: v + ' : ' + g.length + ' bien(s)', alt: v });
      var pop = el('div', 'pop');
      pop.appendChild(el('strong', null, v + ' · ' + g.length + (g.length > 1 ? ' biens' : ' bien')));
      var ul = el('ul');
      g.slice(0, 5).forEach(function (b) {
        var li = el('li'), a = el('a', null, (b.prix ? eur.format(b.prix) + ' €' + (b.type === 'location' ? '/mois' : '') : '') + ' · ' + b.titre);
        a.href = safe(b.url); li.appendChild(a); ul.appendChild(li);
      });
      pop.appendChild(ul);
      var more = el('a', 'btn', 'Voir les biens à ' + v); more.href = '../biens/?ville=' + encodeURIComponent(v) + (type ? '&type=' + type : '');
      pop.appendChild(more);
      m.bindPopup(pop); m.addTo(layer);
    });
    if (pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 11 });
    document.getElementById('carte-count').textContent = total + (total > 1 ? ' biens affichés' : ' bien affiché') + (sans ? ' · ' + sans + ' sans position sur la carte' : '');
  }

  Promise.all([fetch('../data/biens.json').then(function (r) { return r.json(); }), fetch('../data/communes.json').then(function (r) { return r.json(); })])
    .then(function (r) { biens = r[0].biens || []; communes = r[1]; delete communes._note; draw();
      document.querySelectorAll('[data-c]').forEach(function (i) { i.addEventListener('change', draw); }); })
    .catch(function () { document.getElementById('carte-count').textContent = 'La carte est momentanément indisponible.'; });
})();
