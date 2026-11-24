/* Administration du concours : tourner et recadrer une photo. Le cadre est exprimé en fractions de la photo tournée ; le serveur applique la retouche. */
(function () {
  'use strict';
  var d = document, fen = d.getElementById('retouche'); if (!fen || !fen.showModal) return;
  var form = d.getElementById('retouche-form'), toile = d.getElementById('retouche-toile'), cadre = d.getElementById('retouche-cadre'), ctx = toile.getContext('2d');
  var img = null, angle = 0, c = { x: 0, y: 0, w: 1, h: 1 }, MIN = 0.08;
  function champ(n) { return form.elements[n]; }
  function dessine() {
    if (!img) return;
    var q = angle % 180 !== 0, lo = q ? img.naturalHeight : img.naturalWidth, ha = q ? img.naturalWidth : img.naturalHeight;
    var k = Math.min(1, 560 / Math.max(lo, ha)); toile.width = Math.round(lo * k); toile.height = Math.round(ha * k);
    ctx.save(); ctx.translate(toile.width / 2, toile.height / 2); ctx.rotate(angle * Math.PI / 180);
    ctx.drawImage(img, -img.naturalWidth * k / 2, -img.naturalHeight * k / 2, img.naturalWidth * k, img.naturalHeight * k); ctx.restore();
    place();
  }
  function place() {
    cadre.style.left = c.x * 100 + '%'; cadre.style.top = c.y * 100 + '%'; cadre.style.width = c.w * 100 + '%'; cadre.style.height = c.h * 100 + '%';
    champ('angle').value = angle; champ('x').value = c.x.toFixed(4); champ('y').value = c.y.toFixed(4); champ('w').value = c.w.toFixed(4); champ('h').value = c.h.toFixed(4);
  }
  d.querySelectorAll('.js-retoucher').forEach(function (b) {
    b.addEventListener('click', function () {
      champ('id').value = b.dataset.id; d.getElementById('retouche-titre').textContent = 'Retoucher la photo de ' + b.dataset.prenom;
      d.getElementById('retouche-original').hidden = b.dataset.original !== '1';
      angle = 0; c = { x: 0, y: 0, w: 1, h: 1 }; img = new Image();
      img.onload = dessine; img.src = 'image.php?d=' + encodeURIComponent(b.dataset.jeton) + '&t=' + Date.now();
      fen.showModal();
    });
  });
  form.querySelectorAll('[data-tourner]').forEach(function (b) {
    b.addEventListener('click', function () { angle = (angle + parseInt(b.dataset.tourner, 10) + 360) % 360; c = { x: 0, y: 0, w: 1, h: 1 }; dessine(); });
  });
  d.getElementById('retouche-tout').addEventListener('click', function () { c = { x: 0, y: 0, w: 1, h: 1 }; place(); });
  d.getElementById('retouche-annuler').addEventListener('click', function () { fen.close(); });
  // Déplacer le cadre ou tirer l'un de ses coins.
  var geste = null;
  cadre.addEventListener('pointerdown', function (e) {
    var coin = e.target.dataset && e.target.dataset.c; var r = toile.getBoundingClientRect();
    geste = { coin: coin || null, x: e.clientX, y: e.clientY, c: { x: c.x, y: c.y, w: c.w, h: c.h }, l: r.width, h: r.height };
    cadre.setPointerCapture(e.pointerId); e.preventDefault();
  });
  cadre.addEventListener('pointermove', function (e) {
    if (!geste) return; var dx = (e.clientX - geste.x) / geste.l, dy = (e.clientY - geste.y) / geste.h, o = geste.c, n = { x: o.x, y: o.y, w: o.w, h: o.h };
    if (!geste.coin) { n.x = Math.min(1 - o.w, Math.max(0, o.x + dx)); n.y = Math.min(1 - o.h, Math.max(0, o.y + dy)); }
    else {
      var g = geste.coin.indexOf('w') >= 0, ha = geste.coin.indexOf('n') >= 0;
      if (g) { n.x = Math.min(o.x + o.w - MIN, Math.max(0, o.x + dx)); n.w = o.x + o.w - n.x; } else { n.w = Math.min(1 - o.x, Math.max(MIN, o.w + dx)); }
      if (ha) { n.y = Math.min(o.y + o.h - MIN, Math.max(0, o.y + dy)); n.h = o.y + o.h - n.y; } else { n.h = Math.min(1 - o.y, Math.max(MIN, o.h + dy)); }
    }
    c = n; place();
  });
  function fin() { geste = null; } cadre.addEventListener('pointerup', fin); cadre.addEventListener('pointercancel', fin);
})();
