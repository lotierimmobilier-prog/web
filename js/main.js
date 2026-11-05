// LOTIER Immobilier : interactions et animations de la page d'accueil (direction « Isométrique »).
// Aucune dépendance. Les animations respectent « réduire les animations » du système.

(function () {
  var MAIL = 'contact@lotier-immobilier.com';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;
  root.classList.add('js');

  // ----- Menu mobile -----
  var navToggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Ouvrir le menu');
      }
    });
  }

  // ----- Titre mot à mot -----
  document.querySelectorAll('[data-split]').forEach(function (el) {
    var i = 0;
    (function walk(n) {
      [].slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var f = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { f.appendChild(document.createTextNode(' ')); return; }
            var sp = document.createElement('span');
            sp.className = 'w';
            sp.style.setProperty('--i', i++);
            sp.textContent = w;
            f.appendChild(sp);
          });
          n.replaceChild(f, c);
        } else if (c.nodeType === 1) { walk(c); }
      });
    })(el);
  });

  // ----- Apparition au défilement + compteurs -----
  document.querySelectorAll('[data-stagger]').forEach(function (p) {
    [].forEach.call(p.children, function (c, i) { c.setAttribute('data-r', ''); c.style.setProperty('--d', (i * 90) + 'ms'); });
  });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll('[data-r]').forEach(function (e) { io.observe(e); });

  function fmt(v) { return String(Math.round(v)); }
  var cio = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      var el = e.target, to = +el.dataset.count, from = +(el.dataset.from || 0), suf = el.dataset.suf || '', t0 = null;
      if (reduce) { el.textContent = fmt(to) + suf; return; }
      (function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / 1800), ez = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt(from + (to - from) * ez) + suf;
        if (p < 1) requestAnimationFrame(step);
      })(performance.now());
    });
  }, { threshold: 0.4 });
  document.querySelectorAll('[data-count]').forEach(function (e) { cio.observe(e); });

  // ----- Boutons magnétiques, cartes inclinables -----
  if (!reduce) {
    document.querySelectorAll('.mag').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.setProperty('--tx', ((e.clientX - r.left - r.width / 2) * 0.2) + 'px');
        b.style.setProperty('--ty', ((e.clientY - r.top - r.height / 2) * 0.3) + 'px');
      });
      b.addEventListener('pointerleave', function () { b.style.setProperty('--tx', '0px'); b.style.setProperty('--ty', '0px'); });
    });
    document.querySelectorAll('[data-tilt]').forEach(function (c) {
      c.addEventListener('pointermove', function (e) {
        var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        c.style.transform = 'perspective(900px) rotateY(' + ((x - 0.5) * 7) + 'deg) rotateX(' + ((0.5 - y) * 7) + 'deg)';
      });
      c.addEventListener('pointerleave', function () { c.style.transform = ''; });
    });
  }

  // ----- Parallaxe douce de la photo des agences -----
  var par = document.querySelector('.agencies .photo img');
  if (par && !reduce) {
    var tick = false;
    window.addEventListener('scroll', function () {
      if (tick) return; tick = true;
      requestAnimationFrame(function () {
        var r = par.parentNode.getBoundingClientRect();
        var py = (r.top + r.height / 2 - window.innerHeight / 2) * -0.06;
        par.style.setProperty('--py', Math.max(-38, Math.min(38, py)) + 'px');
        tick = false;
      });
    }, { passive: true });
  }

  // ----- Immeuble isométrique -----
  var FLOORS = [
    { n: 'Conseil', t: 'Un conseiller à votre écoute', p: 'On commence toujours par vous écouter, avant de parler prix ou calendrier.', a: 'Prendre rendez-vous', h: '#contact' },
    { n: 'Location', t: 'Louer l\'esprit tranquille', p: 'Nous trouvons le locataire, rédigeons le bail et suivons votre bien. À partir de 39,99 € par mois.', a: 'Mettre mon bien en location', h: 'mailto:gestion@lotier-immobilier.com' },
    { n: 'Vente', t: 'Vendre au bon prix', p: 'Estimation, mandat, visites, signature : un conseiller vous accompagne jusqu\'à l\'acte.', a: 'Estimer mon bien', h: '#estimer' },
    { n: 'Syndic', t: 'Une copropriété claire', p: 'Assemblées, charges, travaux : une gestion transparente pour votre immeuble.', a: 'Écrire au syndic', h: 'mailto:syndic@lotier-immobilier.com' },
    { n: 'Estimation', t: 'Combien vaut votre bien ?', p: 'Une estimation appuyée sur les ventes récentes de votre quartier.', a: 'Estimer mon bien', h: '#estimer' }
  ];

  function isoSvg() {
    var S = 46, W = 3.1, D = 2.5, H = 1.0, ox = 300, oy = 330, c30 = Math.cos(Math.PI / 6), s30 = Math.sin(Math.PI / 6);
    function P(x, y, z) { return [(ox + (x - y) * c30 * S).toFixed(1), (oy + (x + y) * s30 * S - z * S).toFixed(1)].join(','); }
    function poly(pts, cls, style) { return '<polygon class="' + cls + '"' + (style ? ' style="' + style + '"' : '') + ' points="' + pts.map(function (q) { return P(q[0], q[1], q[2]); }).join(' ') + '"/>'; }
    var s = '<svg viewBox="0 0 600 470" role="group" aria-label="Immeuble en trois dimensions : chaque étage est un service de l\'agence"><defs><filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter></defs>';
    s += '<polygon points="' + [P(-0.8, -0.8, 0), P(W + 0.8, -0.8, 0), P(W + 0.8, D + 0.8, 0), P(-0.8, D + 0.8, 0)].join(' ') + '" fill="#cfd9e6" opacity=".7"/>';
    s += '<polygon points="' + [P(0.2, 0.2, 0), P(W + 1.2, 0.2, 0), P(W + 1.2, D + 1.2, 0), P(0.2, D + 1.2, 0)].join(' ') + '" fill="#0f2744" opacity=".28" filter="url(#sh)"/>';
    FLOORS.forEach(function (f, k) {
      var z0 = k * H, z1 = z0 + H;
      var g = '<g class="fl" data-k="' + k + '" style="--k:' + k + ';--ft:#f3f7fc;--fl:' + (k % 2 ? '#dfe8f3' : '#e8eff8') + ';--fr:' + (k % 2 ? '#bccbdd' : '#c6d4e5') + '" tabindex="0" role="button" aria-pressed="false" aria-label="Étage ' + (k + 1) + ' : ' + f.n + '">';
      g += poly([[0, D, z0], [W, D, z0], [W, D, z1], [0, D, z1]], 'lf');
      g += poly([[W, 0, z0], [W, D, z0], [W, D, z1], [W, 0, z1]], 'rt');
      g += poly([[0, 0, z1], [W, 0, z1], [W, D, z1], [0, D, z1]], 'top');
      for (var c = 0; c < 4; c++) { var xa = 0.3 + c * 0.7, xb = xa + 0.45; g += '<polygon class="win lit" style="animation-delay:' + (((c * 3 + k * 5) % 7) * 0.4) + 's" points="' + [P(xa, D, z0 + 0.25), P(xb, D, z0 + 0.25), P(xb, D, z1 - 0.2), P(xa, D, z1 - 0.2)].join(' ') + '"/>'; }
      for (var d = 0; d < 3; d++) { var ya = 0.3 + d * 0.72, yb = ya + 0.46; g += '<polygon class="win lit" style="animation-delay:' + (((d * 4 + k * 3) % 7) * 0.4) + 's" points="' + [P(W, ya, z0 + 0.25), P(W, yb, z0 + 0.25), P(W, yb, z1 - 0.2), P(W, ya, z1 - 0.2)].join(' ') + '"/>'; }
      if (k === 0) g += poly([[1.2, D, 0], [1.9, D, 0], [1.9, D, 0.62], [1.2, D, 0.62]], 'door', 'fill:#0f2744');
      if (k === FLOORS.length - 1) {
        g += poly([[0.2, 0.2, z1], [1.1, 0.2, z1], [1.1, 1.0, z1], [0.2, 1.0, z1]], 'roof', 'fill:#cfe0f3');
        g += '<polygon style="fill:#0f2744;opacity:.85" points="' + [P(W - 1.1, D - 0.9, z1), P(W - 0.2, D - 0.9, z1), P(W - 0.2, D - 0.1, z1), P(W - 1.1, D - 0.1, z1)].join(' ') + '"/>';
      }
      s += g + '</g>';
    });
    return s + '</svg>';
  }

  var isoBox = document.getElementById('iso-svg');
  if (isoBox) {
    isoBox.innerHTML = isoSvg();
    var fls = isoBox.querySelectorAll('.fl');
    var btns = document.querySelectorAll('.elev button');
    var t = document.getElementById('floor-t'), p = document.getElementById('floor-p'), a = document.getElementById('floor-a');
    var set = function (k) {
      var f = FLOORS[k];
      t.textContent = 'Étage ' + (k + 1) + ' · ' + f.t;
      p.textContent = f.p;
      a.textContent = f.a;
      a.setAttribute('href', f.h);
      fls.forEach(function (el, i) {
        el.classList.add('set');
        el.classList.toggle('act', i === k);
        el.setAttribute('aria-pressed', String(i === k));
        el.style.setProperty('--ty', (i > k ? -26 : i === k ? -10 : 0) + 'px');
      });
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(+b.dataset.k === k)); });
    };
    fls.forEach(function (el) {
      var k = +el.dataset.k;
      el.addEventListener('pointerenter', function () { set(k); });
      el.addEventListener('focus', function () { set(k); });
      el.addEventListener('click', function () { set(k); });
      el.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); set(k); } });
    });
    btns.forEach(function (b) {
      b.addEventListener('pointerenter', function () { set(+b.dataset.k); });
      b.addEventListener('click', function () { set(+b.dataset.k); });
    });
    set(2);
  }

  // Lance les animations d'ouverture (titre, étages) une fois la page peinte.
  requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.add('go'); }); });

  // ----- Estimation : prépare un e-mail à l'agence -----
  var est = document.getElementById('estimer');
  if (est) {
    est.addEventListener('submit', function (e) {
      e.preventDefault();
      var adresse = document.getElementById('est-adresse').value.trim();
      var tel = document.getElementById('est-tel').value.trim();
      var body = 'Bonjour,\n\nJe souhaite faire estimer mon bien.\n\nAdresse : ' + adresse + '\nTéléphone : ' + tel + '\n\nMerci de me rappeler.';
      window.location.href = 'mailto:' + MAIL + '?subject=' + encodeURIComponent('Demande d\'estimation') + '&body=' + encodeURIComponent(body);
    });
  }

  // ----- Recherche : onglets Acheter / Louer -----
  var modes = { vente: { label: 'Budget maximum', hint: 'Ex. 250 000 €' }, location: { label: 'Loyer maximum', hint: 'Ex. 750 € par mois' } };
  var tabs = document.querySelectorAll('[data-mode]');
  var budgetLabel = document.querySelector('label[for="budget"]');
  var budgetInput = document.getElementById('budget');
  function setMode(key) {
    if (!budgetLabel || !budgetInput) return;
    tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.getAttribute('data-mode') === key)); });
    budgetLabel.textContent = modes[key].label;
    budgetInput.placeholder = modes[key].hint;
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { setMode(t.getAttribute('data-mode')); }); });
  var sub = document.getElementById('search-submit');
  if (sub) sub.addEventListener('click', function () { var an = document.getElementById('annonces'); if (an) an.scrollIntoView(); });
  setMode('vente');

  // ----- Carrousel d'annonces -----
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.track'), prev = car.querySelector('[data-dir="-1"]'), next = car.querySelector('[data-dir="1"]');
    function update() {
      prev.disabled = track.scrollLeft < 4;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
    }
    prev.addEventListener('click', function () { track.scrollBy({ left: -track.clientWidth * 0.8 }); });
    next.addEventListener('click', function () { track.scrollBy({ left: track.clientWidth * 0.8 }); });
    track.addEventListener('scroll', update);
    window.addEventListener('resize', update);
    update();
  });

  // ----- Conseils : filtre par profil -----
  var chips = document.querySelectorAll('[data-filter]');
  var items = document.querySelectorAll('.faq details');
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.getAttribute('data-filter');
      chips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
      items.forEach(function (d) { d.hidden = !(f === 'all' || d.getAttribute('data-cat') === f); });
    });
  });

  // ----- Blog : filtre par thème -----
  var bchips = document.querySelectorAll('[data-bf]');
  var cards = document.querySelectorAll('#blog-list .blog-card');
  bchips.forEach(function (c) {
    c.addEventListener('click', function () {
      var f = c.getAttribute('data-bf');
      bchips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
      cards.forEach(function (d) { d.hidden = !(f === 'all' || d.getAttribute('data-cat') === f); });
    });
  });
})();
