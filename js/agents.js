/* Page « Nos agents » : les agents en bulles de même taille, placées au hasard à chaque ouverture.
   Les données viennent du HTML (script#ag-data, écrit par le générateur depuis Collab). Sans JavaScript, la liste des
   agents (ul.ag-list) reste affichée. Survol ou toucher : la bulle grossit ; un clic affiche la fiche ; « Voir sa page » ouvre la fiche. */
(function () {
  var sec = document.querySelector('[data-agents]'), node = document.getElementById('ag-data');
  if (!sec || !node) return;
  var D; try { D = JSON.parse(node.textContent); } catch (e) { return; }
  var field = document.getElementById('ag-field'), info = document.getElementById('ag-info'), chips = sec.querySelector('.ag-chips');
  var L = D.agents || [], filt = 'all', sel = null, GEO = null;
  if (!L.length) return;
  sec.classList.add('ag-js');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function el(t, c, h) { var n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function col(a) { var s = D.secteurs[a.secteurs[0]]; return s ? s.couleur : '#867244'; }
  function nom(a) { var s = D.secteurs[a.secteurs[0]]; return s ? s.nom : ''; }
  function ph(a) { return a.photo ? '<img src="' + esc(a.photo) + '" alt="Portrait de ' + esc(a.prenom + ' ' + a.nom) + '" width="256" height="256">' : '<b>' + esc(a.prenom.charAt(0) + a.nom.charAt(0)) + '</b>'; }
  function shuffle(x) { for (var i = x.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = x[i]; x[i] = x[j]; x[j] = t; } return x; }
  function show(a) {
    if (!a) { info.innerHTML = '<p class="muted" style="margin:0">Touchez un portrait pour découvrir l\'agent, ses annonces et ses coordonnées.</p>'; return; }
    var t = a.tel ? a.tel.replace(/ /g, '') : '';
    info.style.setProperty('--rc', col(a));
    info.innerHTML = '<span class="ag-big">' + ph(a) + '</span><div><h2 class="ag-iname">' + esc(a.prenom + ' ' + a.nom) + '</h2><p class="small muted">' + esc(a.role) + (nom(a) ? ' · ' + esc(nom(a)) : '') + '<br>' + esc(a.communes.slice(0, 5).join(', ')) + '</p><div class="acts">' +
      '<a class="btn btn-gold btn-sm" href="' + esc(a.url) + '">Voir sa page' + (a.nb ? ' et ses ' + a.nb + ' annonce' + (a.nb > 1 ? 's' : '') : '') + '</a>' + (t ? '<a class="btn btn-ghost btn-sm" href="tel:' + esc(t) + '">' + esc(a.tel) + '</a>' : '') + '</div></div>';
  }
  function layout() {
    var W = field.clientWidth, H = field.clientHeight, n = L.length, narrow = W < 700;
    var d = Math.min(W * (narrow ? 0.36 : 0.19), H * (narrow ? 0.2 : 0.3)); d = Math.max(d, 96);
    var lab = d * 0.5, padX = d * 0.62, top = 20 + d * 0.52, bot = lab + d * 0.52 + 8, minD = d * 1.0, best = null, tries = 0;
    function hit(a, c) { var cx = Math.max(a.x - d * 0.7, Math.min(c.x, a.x + d * 0.7)), cy = Math.max(a.y + d * 0.5, Math.min(c.y, a.y + d * 0.5 + lab)); return Math.hypot(cx - c.x, cy - c.y) < d * 0.5 - 2; }
    function ok(p, x, y) { return Math.hypot(p.x - x, p.y - y) >= minD && !hit(p, { x: x, y: y }) && !hit({ x: x, y: y }, p); }
    while (!best && tries < 60) {
      tries++; var pts = [], k = 0;
      while (pts.length < n && k < 3000) { k++; var x = padX + Math.random() * Math.max(1, W - 2 * padX), y = top + Math.random() * Math.max(1, H - top - bot); if (pts.every(function (p) { return ok(p, x, y); })) pts.push({ x: x, y: y }); }
      if (pts.length === n) best = pts;
    }
    if (!best) { best = []; var cols = narrow ? 2 : 3; for (var i = 0; i < n; i++) best.push({ x: padX + (i % cols) * (W - 2 * padX) / Math.max(1, cols - 1), y: top + Math.floor(i / cols) * (d + lab) }); }
    return { d: d, pts: best };
  }
  function fit() { var n = L.length, narrow = field.clientWidth < 700; field.style.height = (narrow ? Math.max(440, Math.ceil(n / 2) * 250 + 60) : Math.max(460, Math.ceil(n / 3) * 270 + 120)) + 'px'; }
  function render() {
    fit(); field.innerHTML = ''; var G = layout(), order = shuffle(L.slice()); GEO = { d: G.d, pos: {} };
    order.forEach(function (a, i) {
      var p = G.pts[i], b = el('button', 'bb'); GEO.pos[a.id] = p;
      b.type = 'button'; b.dataset.id = a.id; b.dataset.s = a.secteurs.join(' ');
      b.style.cssText = 'left:' + (p.x - G.d / 2) + 'px;top:' + (p.y - G.d / 2) + 'px;--d:' + G.d + 'px;--rc:' + col(a) + ';--z:' + (1 + i) + ';--dl:' + (reduce ? 0 : i * 0.09) + 's';
      b.setAttribute('aria-label', a.prenom + ' ' + a.nom + (nom(a) ? ', ' + nom(a) : ''));
      b.innerHTML = '<span class="disc">' + ph(a) + '</span>' + (nom(a) ? '<span class="role">' + esc(nom(a).split(' ')[0]) + '</span>' : '') + '<span class="nm"><b>' + esc(a.prenom + ' ' + a.nom) + '</b><i>' + esc(a.communes.slice(0, 3).join(', ')) + '</i></span>';
      field.appendChild(b);
    });
    apply();
  }
  function by(id) { return L.filter(function (a) { return a.id === id; })[0]; }
  /* Secteur choisi : ses agents viennent se placer au centre du cadre, agrandis ; les autres s'effacent en arrière-plan. */
  function zoom() {
    var W = field.clientWidth, H = field.clientHeight, d = GEO.d, narrow = W < 700;
    var on = filt === 'all' ? [] : L.filter(function (a) { return a.secteurs.indexOf(filt) > -1; });
    var k = on.length, cols = k ? Math.min(k, narrow ? 2 : 4) : 1, rows = k ? Math.ceil(k / cols) : 1;
    var lab = d * 0.5, gap = 1.12;
    var s = Math.min(1.9, (W * 0.88) / (cols * d * gap), (H * 0.9) / (rows * (d + lab) * gap)); s = Math.max(1, s);
    var cell = d * s * gap, cellH = (d + lab) * s * gap, x0 = W / 2 - (cols * cell) / 2 + cell / 2, y0 = H / 2 - (rows * cellH) / 2 + (d * s) / 2;
    var idx = {}; on.forEach(function (a, i) { idx[a.id] = i; });
    field.querySelectorAll('.bb').forEach(function (b) {
      var id = b.dataset.id, o = GEO.pos[id];
      if (filt !== 'all' && id in idx) {
        var i = idx[id], inRow = (i / cols | 0) === rows - 1 ? k - (rows - 1) * cols : cols;      /* dernière ligne centrée */
        var cx = W / 2 - (inRow * cell) / 2 + cell / 2 + (i % cols) * cell, cy = y0 + (i / cols | 0) * cellH;
        b.style.setProperty('--tx', (cx - o.x) + 'px'); b.style.setProperty('--ty', (cy - o.y) + 'px'); b.style.setProperty('--sc', s);
        b.style.setProperty('--zz', 40 + i);
      } else { b.style.setProperty('--tx', '0px'); b.style.setProperty('--ty', '0px'); b.style.setProperty('--sc', 1); b.style.removeProperty('--zz'); }
    });
    return on;
  }
  function apply() {
    field.classList.toggle('f', filt !== 'all');
    var on = GEO ? zoom() : [];
    field.querySelectorAll('.bb').forEach(function (b) { b.classList.toggle('on', filt === 'all' || b.dataset.s.split(' ').indexOf(filt) > -1); b.classList.toggle('sel', b.dataset.id === sel); });
    chips.querySelectorAll('[data-sect]').forEach(function (c) { var on2 = c.dataset.sect === filt; c.classList.toggle('is-on', on2); c.setAttribute('aria-pressed', on2 ? 'true' : 'false'); });
    if (filt !== 'all' && on.length === 1) { sel = on[0].id; show(on[0]); field.querySelectorAll('.bb').forEach(function (b) { b.classList.toggle('sel', b.dataset.id === sel); }); }
  }
  chips.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-mix]')) { render(); return; }
    var c = ev.target.closest('[data-sect]'); if (!c) return; filt = c.dataset.sect; apply();
  });
  var touch = 'ontouchstart' in window;
  field.addEventListener('click', function (ev) {
    var b = ev.target.closest('.bb'); if (!b) return; var a = by(b.dataset.id);
    if (sel === a.id) { window.location.href = a.url; return; }      /* deuxième clic : on ouvre la fiche */
    sel = a.id; show(a); apply();
  });
  field.addEventListener('mouseover', function (ev) { if (touch) return; var b = ev.target.closest('.bb'); if (b && sel !== b.dataset.id) { sel = b.dataset.id; show(by(sel)); apply(); } });
  var lw = field.clientWidth, rt;
  window.addEventListener('resize', function () { if (field.clientWidth === lw) return; lw = field.clientWidth; clearTimeout(rt); rt = setTimeout(render, 200); });
  show(null); render();
})();
