/* Décor de Noël de lotier.immo.
   - Actif du 1er décembre au 5 janvier (essai hors saison : ajouter ?noel=1 à l'adresse, ?noel=0 pour l'arrêter).
   - Le visiteur peut revenir au thème normal avec le bouton de la barre du haut ; son choix est gardé dans le navigateur.
   - Tout est ajouté par ce script (styles, guirlande, neige) : hors saison, la page n'est pas modifiée.
   - Mouvement réduit demandé par le visiteur : pas de neige ni de clignotement, décor fixe seulement. */
(function () {
  'use strict';
  var d = document, racine = d.documentElement, CLE = 'lotier-noel';
  var lire = function (s, k) { try { return s.getItem(k); } catch (e) { return null; } };
  var ecrire = function (s, k, v) { try { s.setItem(k, v); } catch (e) { /* stockage indisponible */ } };

  var q = /[?&]noel=([01])\b/.exec(location.search);
  if (q) ecrire(sessionStorage, CLE + '-essai', q[1]);
  var essai = lire(sessionStorage, CLE + '-essai');
  var j = new Date(), mois = j.getMonth(), jour = j.getDate();
  var saison = mois === 11 || (mois === 0 && jour <= 5);
  if (essai === '1') saison = true;
  if (essai === '0') saison = false;
  if (!saison) return;

  var barre = d.querySelector('.topbar .tb-r'), entete = d.querySelector('.site-header');
  if (!barre || !entete) return;
  var calme = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var actif = lire(localStorage, CLE) !== 'off';

  var svg = function (corps) { return "url(\"data:image/svg+xml," + encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' width='240' height='34' viewBox='0 0 240 34'>" + corps + "</svg>") + "\")"; };
  var FIL = svg("<path d='M0 3 Q30 23 60 3 T120 3 T180 3 T240 3' fill='none' stroke='#1d3a2f' stroke-width='1.6'/>");
  var ampoule = function (x, c) { return "<rect x='" + (x - 2) + "' y='11' width='4' height='4' rx='1' fill='#1d3a2f'/><ellipse cx='" + x + "' cy='21.5' rx='5.6' ry='7.6' fill='" + c + "'/><ellipse cx='" + (x - 1.7) + "' cy='19' rx='1.5' ry='2.4' fill='#fff' opacity='.55'/>"; };
  var LOT_A = svg(ampoule(30, '#d8423f') + ampoule(150, '#e9b949'));
  var LOT_B = svg(ampoule(90, '#2f9a68') + ampoule(210, '#5aa9e6'));

  var css = d.createElement('style');
  css.textContent =
    '.tb-noel{cursor:pointer;gap:8px}' +
    '.tb-noel svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}' +
    '.tb-noel .n-court{display:none}' +
    '.noel .tb-noel{background:rgba(255,255,255,.12);border-radius:999px;padding-inline:12px}' +
    '.noel .topbar{background:linear-gradient(90deg,#0f2744 0%,#123b33 55%,#5b1d24 100%)}' +
    '.noel .site-header{border-bottom-color:rgba(174,152,106,.55)}' +
    '.noel-guirlande{position:absolute;left:0;right:0;top:100%;height:34px;pointer-events:none;background:' + FIL + ' repeat-x 0 0;display:none}' +
    '.noel .noel-guirlande{display:block}' +
    '.noel-guirlande::before,.noel-guirlande::after{content:"";position:absolute;inset:0;background-repeat:repeat-x}' +
    '.noel-guirlande::before{background-image:' + LOT_A + ';filter:drop-shadow(0 0 5px rgba(233,185,73,.75))}' +
    '.noel-guirlande::after{background-image:' + LOT_B + ';filter:drop-shadow(0 0 5px rgba(90,169,230,.7))}' +
    '.noel-neige{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:55;display:none}' +
    '.noel .noel-neige{display:block}' +
    '@keyframes noel-clin{0%,100%{opacity:1}50%{opacity:.45}}' +
    '@media (prefers-reduced-motion: no-preference){.noel-guirlande::before{animation:noel-clin 1.8s ease-in-out infinite}.noel-guirlande::after{animation:noel-clin 1.8s ease-in-out .9s infinite}}' +
    '@media (max-width:760px){.tb-noel .n-long{display:none}.tb-noel .n-court{display:inline}.tb-noel{gap:5px}.tb-noel svg{display:inline-block;width:14px;height:14px}.noel .tb-noel{padding-inline:9px}.noel-guirlande{height:25px;background-size:176px 25px}.noel-guirlande::before,.noel-guirlande::after{background-size:176px 25px}}' +
    '@media print{.noel-guirlande,.noel-neige,.tb-noel{display:none!important}}';
  d.head.appendChild(css);

  var bouton = d.createElement('button');
  bouton.type = 'button';
  bouton.className = 'tb-btn tb-noel';
  bouton.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v20M3.3 7l17.4 10M20.7 7 3.3 17M12 6 9.5 3.5M12 6l2.5-2.5M12 18l-2.5 2.5M12 18l2.5 2.5"/></svg><span class="n-long"></span><span class="n-court" aria-hidden="true"></span>';
  barre.insertBefore(bouton, barre.firstChild);

  var guirlande = d.createElement('div');
  guirlande.className = 'noel-guirlande';
  guirlande.setAttribute('aria-hidden', 'true');
  entete.appendChild(guirlande);

  /* ---- Neige ---- */
  var toile = null, ctx = null, flocons = [], image = 0, L = 0, H = 0;
  function taille() {
    var r = Math.min(window.devicePixelRatio || 1, 2);
    L = window.innerWidth; H = window.innerHeight;
    toile.width = L * r; toile.height = H * r;
    ctx.setTransform(r, 0, 0, r, 0, 0);
    var n = Math.round(Math.min(90, Math.max(28, L / 16)));
    while (flocons.length < n) flocons.push(flocon(true));
    flocons.length = n;
  }
  function flocon(partout) {
    var r = 1.2 + Math.random() * 3.2;
    return { x: Math.random() * L, y: partout ? Math.random() * H : -8, r: r, v: 0.35 + r * 0.22 + Math.random() * 0.4, d: Math.random() * 6.28, a: 0.45 + Math.random() * 0.45 };
  }
  function dessine() {
    ctx.clearRect(0, 0, L, H);
    for (var i = 0; i < flocons.length; i++) {
      var f = flocons[i];
      f.y += f.v; f.d += 0.012; f.x += Math.sin(f.d) * 0.5;
      if (f.y > H + 8) { flocons[i] = f = flocon(false); }
      ctx.beginPath();
      ctx.fillStyle = 'rgba(228,238,250,' + Math.min(1, f.a + 0.25) + ')';
      ctx.strokeStyle = 'rgba(110,145,190,' + (f.a * 0.7) + ')';
      ctx.lineWidth = 0.8;
      ctx.arc(f.x, f.y, f.r, 0, 6.2832);
      ctx.fill(); ctx.stroke();
    }
    image = requestAnimationFrame(dessine);
  }
  function neige(oui) {
    if (calme) return;
    if (oui && !toile) {
      toile = d.createElement('canvas');
      toile.className = 'noel-neige';
      toile.setAttribute('aria-hidden', 'true');
      d.body.appendChild(toile);
      ctx = toile.getContext('2d');
      window.addEventListener('resize', taille);
      d.addEventListener('visibilitychange', function () { cancelAnimationFrame(image); if (!d.hidden && racine.classList.contains('noel')) image = requestAnimationFrame(dessine); });
    }
    if (!toile) return;
    cancelAnimationFrame(image);
    if (oui) { taille(); image = requestAnimationFrame(dessine); }
  }

  function applique() {
    racine.classList.toggle('noel', actif);
    bouton.setAttribute('aria-pressed', actif ? 'true' : 'false');
    bouton.setAttribute('aria-label', actif ? 'Décor de Noël activé. Revenir au thème normal' : 'Activer le décor de Noël');
    bouton.querySelector('.n-long').textContent = actif ? 'Revenir au thème normal' : 'Thème de Noël';
    bouton.querySelector('.n-court').textContent = actif ? 'Normal' : 'Noël';
    neige(actif);
  }
  bouton.addEventListener('click', function () {
    actif = !actif;
    ecrire(localStorage, CLE, actif ? 'on' : 'off');
    applique();
  });
  applique();
})();
