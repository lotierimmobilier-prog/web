/* Intro d'accueil : le logo rond se dessine, son cercle s'ouvre en iris sur Béziers, puis Montpellier, Carcassonne
   et Nîmes, et la croix occitane ouvre la page. Jouée une seule fois par visite ; « Passer l'intro » toujours disponible.
   Utilise GSAP (js/gsap.min.js, hébergé sur le site). */
(function () {
  var root = document.documentElement;
  if (!root.classList.contains('has-intro')) return;
  window.__lotierIntro = true;
  function done() { try { sessionStorage.setItem('lotier-intro', '1'); } catch (e) {} root.classList.remove('has-intro'); root.classList.add('intro-done'); }
  var hero = document.getElementById('accueil-hero');
  if (!hero) { root.classList.remove('has-intro'); return; }
  if (!window.gsap) { done(); return; }
  var CITIES = [['bez-pont', 'BÉZIERS', 'Cathédrale · Pont-Vieux'], ['montpellier', 'MONTPELLIER', 'Place de la Comédie'], ['carcassonne', 'CARCASSONNE', 'La Cité'], ['nimes', 'NÎMES', 'Les Arènes']];
  var BASE = 'assets/intro/';
  var el = document.createElement('div');
  el.id = 'intro'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-label', 'Animation d\'introduction de LOTIER Immobilier');
  el.innerHTML =
    '<div class="li-phs"></div><div class="li-edge"></div>' +
    '<div class="li-badge"><svg viewBox="0 0 800 800" aria-hidden="true">' +
    '<circle class="li-ring" cx="400" cy="400" r="294" fill="none" stroke="#AE986A" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" transform="rotate(-90 400 400)"/>' +
    '<g transform="translate(115.2 285.4) scale(0.3336)"><defs><clipPath id="li-gc"><rect x="176" y="96" width="301" height="481"/></clipPath>' +
    '<linearGradient id="li-sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".8"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>' +
    '<g class="li-blk"><path fill="#AE986A" fill-rule="evenodd" d="M176 96H477V577H176Z M223 149H274V484H450V533H223Z"/><g clip-path="url(#li-gc)"><rect class="li-shine" x="-200" y="0" width="150" height="689" fill="url(#li-sh)" transform="skewX(-18)"/></g></g>' +
    '<image class="li-otier" href="' + BASE + 'otier.png" x="488" y="183" width="1134" height="290"/><image class="li-immo" href="' + BASE + 'immo.png" x="520" y="482" width="842" height="93"/></g></svg></div>' +
    '<div class="li-city" aria-hidden="true"><em></em><b></b></div><div class="li-count" aria-hidden="true"></div>' +
    '<div class="li-cross"></div><div class="li-flash"></div>' +
    '<button type="button" class="li-skip">Passer l\'intro ›</button><div class="li-bar"><i></i></div>';
  hero.appendChild(el);
  var $ = function (s) { return el.querySelector(s); };
  var phsBox = $('.li-phs'), edge = $('.li-edge'), badge = $('.li-badge'), cross = $('.li-cross'), skipBtn = $('.li-skip');
  var photos = CITIES.map(function (c, i) {
    var d = document.createElement('div'); d.className = 'li-ph'; d.style.zIndex = i + 1;
    var im = new Image(); im.alt = ''; im.decoding = 'async'; im.src = BASE + c[0] + '.jpg'; d.appendChild(im); phsBox.appendChild(d); return d;
  });
  cross.style.backgroundImage = 'url(' + BASE + 'bez-pont.jpg)';
  skipBtn.focus();
  var R = 0, tl = null, mo = { v: 6 }, finished = false;
  function metrics() {
    var W = el.clientWidth, H = el.clientHeight, D = Math.min(W * 0.86, H * 0.82);
    R = Math.hypot(W, H) / 2 * 1.04;
    badge.style.cssText = 'width:' + D + 'px;height:' + D + 'px;margin-left:' + (-D / 2) + 'px;margin-top:' + (-D / 2) + 'px';
    return D * (300 / 800);
  }
  function setClip(i, r) { photos[i].style.clipPath = 'circle(' + r + 'px at 50% 50%)'; }
  function setEdge(r, o) { var s = Math.max(r, 1); edge.style.width = edge.style.height = (2 * s) + 'px'; edge.style.marginLeft = edge.style.marginTop = (-s) + 'px'; edge.style.opacity = o; }
  function setMask() { var v = mo.v + '%'; cross.style.webkitMaskSize = v; cross.style.maskSize = v; }
  function flash(o, d) { gsap.fromTo($('.li-flash'), { opacity: o }, { opacity: 0, duration: d, ease: 'power2.out', overwrite: 'auto' }); }
  function shake(a) { gsap.fromTo(el, { x: a, y: -a / 2 }, { x: 0, y: 0, duration: .35, ease: 'elastic.out(1,.25)', overwrite: 'auto' }); }
  function finish(fast) {
    if (finished) return; finished = true;
    if (tl) tl.pause();
    gsap.to(el, { opacity: 0, duration: fast ? .35 : .7, ease: 'power1.inOut', onComplete: function () { el.remove(); done(); window.dispatchEvent(new Event('lotier-intro-end')); } });
    done();
  }
  skipBtn.addEventListener('click', function () { finish(true); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') finish(true); });

  var r0 = metrics();
  gsap.set('.li-blk', { svgOrigin: '326 336', scale: 0, opacity: 0 });
  gsap.set('.li-otier,.li-immo', { opacity: 0, x: -40 });
  tl = gsap.timeline({ defaults: { ease: 'expo.out' }, onComplete: function () { finish(false); } });
  /* 1 · le logo rond */
  tl.to('.li-ring', { strokeDashoffset: 0, duration: 1.2, ease: 'power2.inOut' }, 0.1)
    .to('.li-blk', { scale: 1, opacity: 1, duration: .9, ease: 'elastic.out(1,.55)' }, 0.9)
    .to('.li-otier', { opacity: 1, x: 0, duration: .8 }, 1.2)
    .to('.li-immo', { opacity: 1, x: 0, duration: .8 }, 1.45)
    .to('.li-shine', { x: 2400, duration: 1.0, ease: 'power2.inOut' }, 1.8)
    .to(badge, { rotation: 360, duration: 1.4, ease: 'power3.inOut' }, 0.1);
  /* 2 · iris sur Béziers */
  var o = { r: r0 }, at = 2.9;
  tl.add(function () { gsap.set('.li-ring', { opacity: 0 }); setEdge(r0, 1); setClip(0, r0); flash(.35, .3); }, at)
    .to('.li-otier,.li-immo,.li-blk', { opacity: 0, duration: .25, ease: 'power2.in' }, at)
    .to(o, { r: R, duration: .95, ease: 'expo.in', onUpdate: function () { setClip(0, o.r); setEdge(o.r, 1); } }, at)
    .to(photos[0].firstChild, { scale: 1.08, duration: 1.6, ease: 'power1.out' }, at)
    .add(function () { setEdge(0, 0); flash(.8, .45); shake(10); }, at + .95);
  var cut = at + .95, cityN = $('.li-city b'), cityK = $('.li-city em'), count = $('.li-count');
  function name(i, t) {
    tl.add(function () { cityN.textContent = CITIES[i][1]; cityK.textContent = CITIES[i][2]; count.textContent = '0' + (i + 1) + ' / 04'; }, t)
      .fromTo('.li-city', { opacity: 0 }, { opacity: 1, duration: .01, immediateRender: false }, t)
      .fromTo(cityN, { yPercent: 100 }, { yPercent: 0, duration: .55, immediateRender: false }, t + .02)
      .fromTo(cityK, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: .5, immediateRender: false }, t + .15)
      .to(count, { opacity: 1, duration: .2 }, t + .1);
  }
  name(0, cut + .05);
  /* 3 · les trois autres villes */
  for (var i = 1; i < CITIES.length; i++) (function (i) {
    var t = cut + i * 1.0, p = { r: 0 };
    tl.set('.li-city', { opacity: 0 }, t - .02)
      .add(function () { setClip(i, 0); setEdge(0, 1); }, t)
      .to(p, { r: R, duration: .55, ease: 'expo.inOut', onUpdate: function () { setClip(i, p.r); setEdge(p.r, p.r >= R * .97 ? 0 : 1); } }, t)
      .to(photos[i].firstChild, { scale: 1.08, duration: 1.5, ease: 'power1.out' }, t)
      .add(function () { flash(.45, .3); shake(6); }, t + .2)
      .add(function () { setEdge(0, 0); }, t + .6);
    name(i, t + .4);
  })(i);
  var t3 = cut + CITIES.length * 1.0;
  /* 4 · la croix occitane ouvre la page */
  tl.to('.li-city,.li-count', { opacity: 0, duration: .2 }, t3 - .1)
    .set(cross, { opacity: 1 }, t3)
    .to(mo, { v: 560, duration: 1.5, ease: 'expo.in', onUpdate: setMask }, t3)
    .add(function () { flash(.7, .45); shake(10); }, t3 + 1.45);
  tl.to('.li-bar i', { scaleX: 1, duration: tl.duration(), ease: 'none' }, 0);
  var rt, lw = el.clientWidth;
  window.addEventListener('resize', function () { if (el.clientWidth === lw) return; lw = el.clientWidth; clearTimeout(rt); rt = setTimeout(function () { r0 = metrics(); }, 200); });
})();
