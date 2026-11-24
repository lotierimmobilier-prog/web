/* Concours de Noël LOTIER Immobilier : dépôt, vote et partage. */
(function () {
  'use strict';
  var d = document;
  var q = function (s, r) { return (r || d).querySelector(s); };
  var tous = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var garde = { lire: function (k) { try { return localStorage.getItem(k) || ''; } catch (e) { return ''; } }, ecrire: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* indisponible */ } } };

  function envoyer(donnees) {
    return fetch('api.php', { method: 'POST', body: donnees, credentials: 'same-origin' })
      .then(function (r) { return r.json().catch(function () { return { erreur: 'Réponse inattendue du serveur. Réessayez dans un instant.' }; }); })
      .catch(function () { return { erreur: 'Connexion impossible. Vérifiez votre réseau, puis réessayez.' }; });
  }

  /* ---- Dépôt ---- */
  var depot = q('#depot');
  if (depot) {
    var age = q('#age'), cat = q('#cat-auto'), fichier = q('#dessin'), apercu = q('#apercu'), msg = q('#msg-depot');
    var reduite = null;
    age.addEventListener('input', function () {
      var a = parseInt(age.value, 10);
      cat.textContent = !a || a < 3 ? '' : 'Catégorie : ' + (a <= 5 ? 'de 3 à 5 ans' : a <= 8 ? 'de 6 à 8 ans' : a <= 12 ? 'de 9 à 12 ans' : '13 ans et plus');
    });
    q('#rappel').addEventListener('change', function (e) { q('#bloc-tel').hidden = !e.target.checked; });
    /* La photo est réduite dans le navigateur avant l'envoi : plus rapide sur téléphone, et les informations cachées (lieu, appareil) disparaissent. */
    fichier.addEventListener('change', function () {
      reduite = null; apercu.hidden = true;
      var f = fichier.files && fichier.files[0];
      if (!f) return;
      var url = URL.createObjectURL(f), im = new Image();
      im.onload = function () {
        var k = Math.min(1, 1800 / Math.max(im.naturalWidth, im.naturalHeight));
        var c = d.createElement('canvas');
        c.width = Math.round(im.naturalWidth * k); c.height = Math.round(im.naturalHeight * k);
        var x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height); x.drawImage(im, 0, 0, c.width, c.height);
        c.toBlob(function (b) { reduite = b; q('img', apercu).src = URL.createObjectURL(b); apercu.hidden = false; URL.revokeObjectURL(url); }, 'image/jpeg', 0.88);
      };
      im.onerror = function () { URL.revokeObjectURL(url); };
      im.src = url;
    });
    depot.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.textContent = '';
      if (!depot.checkValidity()) {
        var faux = q('input:invalid, select:invalid', depot);
        msg.textContent = faux && faux.type === 'checkbox' ? 'Merci de cocher les deux cases obligatoires.' : 'Il manque une information : vérifiez les champs du formulaire.';
        if (faux) faux.focus();
        return;
      }
      var donnees = new FormData(depot);
      if (reduite) donnees.set('dessin', reduite, 'dessin.jpg');
      var bouton = q('button[type=submit]', depot);
      bouton.disabled = true; bouton.textContent = 'Envoi en cours…';
      envoyer(donnees).then(function (r) {
        bouton.disabled = false; bouton.textContent = 'Envoyer le dessin';
        if (!r.ok) { msg.textContent = r.erreur || 'Le dessin n’a pas pu être envoyé.'; return; }
        var merci = q('#merci');
        q('[data-merci-prenom]', merci).textContent = r.prenom;
        merci.dataset.prenom = r.prenom; merci.dataset.url = location.origin + location.pathname + '?d=' + r.jeton;
        depot.hidden = true; merci.hidden = false; merci.focus();
        merci.scrollIntoView({ block: 'center' });
        confettis(q('[data-confettis]', merci));
      });
    });
    var pm = q('[data-partager-merci]');
    if (pm) pm.addEventListener('click', function () {
      var m = q('#merci');
      ouvrirPartage(m.dataset.prenom, m.dataset.prenom + ' participe au concours de Noël de LOTIER Immobilier ! Son dessin de la maison du Père Noël sera en ligne sous 12 heures. Les votes ouvrent le ' + (document.body.dataset.votes || '15 décembre') + ', un vote par jour :', m.dataset.url);
    });
  }

  /* ---- Vote ---- */
  var dlgVote = q('#dlg-vote'), carteVotee = null;
  tous('[data-voter]').forEach(function (b) {
    b.addEventListener('click', function () {
      carteVotee = b.closest('.carte');
      q('[data-vote-prenom]', dlgVote).textContent = carteVotee.dataset.prenom;
      q('#msg-vote').textContent = '';
      q('#vote-email').value = garde.lire('concours-email');
      dlgVote.showModal();
    });
  });
  var vote = q('#vote');
  if (vote) vote.addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = q('#msg-vote'), email = q('#vote-email');
    if (!email.checkValidity()) { msg.textContent = 'Indiquez une adresse e-mail valide.'; email.focus(); return; }
    var donnees = new FormData(vote);
    donnees.set('action', 'vote'); donnees.set('dessin', carteVotee.dataset.jeton);
    envoyer(donnees).then(function (r) {
      if (!r.ok) { msg.textContent = r.erreur || 'Le vote n’a pas pu être enregistré.'; return; }
      garde.ecrire('concours-email', email.value.trim());
      var v = q('[data-voix]', carteVotee); if (v) v.textContent = r.voix;
      dlgVote.close();
      ouvrirPartage(carteVotee.dataset.prenom, carteVotee.dataset.texte, carteVotee.dataset.url, 'Merci, votre vote pour ' + r.prenom + ' est compté ! Revenez demain, et faites passer le mot.');
    });
  });

  /* ---- Partage ---- */
  var dlgPartage = q('#dlg-partage'), zone = q('#partage-texte'), urlPartage = '';
  function liens() {
    var texte = zone.value.trim(), complet = texte + ' ' + urlPartage, e = encodeURIComponent;
    q('[data-r=whatsapp]', dlgPartage).href = 'https://wa.me/?text=' + e(complet);
    q('[data-r=facebook]', dlgPartage).href = 'https://www.facebook.com/sharer/sharer.php?u=' + e(urlPartage);
    q('[data-r=email]', dlgPartage).href = 'mailto:?subject=' + e('Concours de Noël : un petit vote ?') + '&body=' + e(complet);
    q('[data-r=sms]', dlgPartage).href = 'sms:?&body=' + e(complet);
  }
  function ouvrirPartage(prenom, texte, url, annonce) {
    urlPartage = url;
    q('[data-partage-prenom]', dlgPartage).textContent = prenom;
    zone.value = texte;
    q('#msg-partage').textContent = annonce || '';
    q('[data-r=natif]', dlgPartage).hidden = !navigator.share;
    liens();
    dlgPartage.showModal();
  }
  zone.addEventListener('input', liens);
  tous('[data-partager]').forEach(function (b) {
    b.addEventListener('click', function () { var c = b.closest('.carte'); ouvrirPartage(c.dataset.prenom, c.dataset.texte, c.dataset.url); });
  });
  q('[data-r=copier]', dlgPartage).addEventListener('click', function () {
    var complet = zone.value.trim() + ' ' + urlPartage, m = q('#msg-partage');
    var fait = function () { m.textContent = 'Message copié : collez-le où vous voulez.'; };
    if (navigator.clipboard) navigator.clipboard.writeText(complet).then(fait, function () { zone.select(); m.textContent = 'Sélectionnez le texte, puis copiez-le.'; });
    else { zone.value = complet; zone.select(); d.execCommand('copy'); fait(); }
  });
  q('[data-r=natif]', dlgPartage).addEventListener('click', function () {
    navigator.share({ text: zone.value.trim(), url: urlPartage }).catch(function () { /* partage annulé */ });
  });
  /* ---- Dessin agrandi : selon la date, on propose de voter ou de partager le concours ---- */
  var dlgPhoto = q('#dlg-photo'), cartePhoto = null;
  if (dlgPhoto) {
    var imgPhoto = q('img', dlgPhoto);
    tous('a[data-agrandir]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;      // ouverture dans un nouvel onglet : comportement habituel
        e.preventDefault();
        cartePhoto = a.closest('.carte');
        var prenom = cartePhoto.dataset.prenom, age = (q('.qui', cartePhoto).textContent.match(/,\s*(.*)$/) || [])[1] || '';
        tous('[data-photo-prenom]', dlgPhoto).forEach(function (s) { s.textContent = prenom; });
        tous('[data-photo-prenom2]', dlgPhoto).forEach(function (s) { s.textContent = prenom; });
        q('[data-photo-age]', dlgPhoto).textContent = age ? '· ' + age : '';
        imgPhoto.alt = q('img', a).alt; imgPhoto.src = a.href;
        var bv = q('[data-photo-voter]', dlgPhoto); if (bv) bv.hidden = !q('[data-voter]', cartePhoto);
        dlgPhoto.showModal();
      });
    });
    var pv = q('[data-photo-voter]', dlgPhoto);
    if (pv) pv.addEventListener('click', function () { var b = q('[data-voter]', cartePhoto); dlgPhoto.close(); if (b) b.click(); });
    q('[data-photo-partager]', dlgPhoto).addEventListener('click', function () { var b = q('[data-partager]', cartePhoto); dlgPhoto.close(); if (b) b.click(); });
  }
  tous('[data-fermer]').forEach(function (b) { b.addEventListener('click', function () { b.closest('dialog').close(); }); });
  tous('dialog').forEach(function (g) { g.addEventListener('click', function (e) { if (e.target === g) g.close(); }); });

  /* Les boules de Noël du titre : leur reflet suit le pointeur. */
  var boules = tous('.boule i');
  if (boules.length && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    d.addEventListener('pointermove', function (e) {
      boules.forEach(function (b) {
        var r = b.parentNode.getBoundingClientRect(), dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height / 2);
        var n = Math.sqrt(dx * dx + dy * dy) || 1, k = r.width * 0.2;
        b.style.transform = 'translate(' + (dx / n * k) + 'px,' + (dy / n * k) + 'px)';
      });
    }, { passive: true });
  }

  // Pendant la lecture de la vidéo du Père Noël, toutes les animations de la page sont suspendues : la vidéo reste fluide, même sur un appareil modeste.
  var lecture = false;
  d.querySelectorAll('.video-pn video').forEach(function (film) {
    var etat = function () { lecture = Array.prototype.some.call(d.querySelectorAll('.video-pn video'), function (v) { return !v.paused && !v.ended; }); d.documentElement.classList.toggle('lecture', lecture); };
    film.addEventListener('play', function () { etat(); }); film.addEventListener('playing', function () { etat(); });
    film.addEventListener('pause', function () { etat(); }); film.addEventListener('ended', function () { etat(); });
    film.addEventListener('play', function () { d.querySelectorAll('.video-pn video').forEach(function (autre) { if (autre !== film) autre.pause(); }); });      // une seule vidéo à la fois
  });

  // Lien direct vers une vidéo (lettre d'information, partage) : la page descend sur la vidéo et tente de la lancer.
  // Si le navigateur refuse le son automatique, la vidéo reste prête : un toucher suffit.
  var cible = (location.hash.match(/^#(video-pere-noel|video-lutin)$/) || [])[1];
  if (cible) window.addEventListener('load', function () {
    var bloc = d.getElementById(cible), film = bloc && bloc.querySelector('video'); if (!film) return;
    bloc.scrollIntoView({ block: 'center' });
    var essai = film.play(); if (essai && essai.catch) essai.catch(function () {});
  });

  /* ---- Effets : apparition au défilement, compteurs, cartes inclinées, neige du haut de page ---- */
  var calme = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  d.documentElement.classList.add('js');
  if ('IntersectionObserver' in window && !calme) {
    var obs = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('vu'); obs.unobserve(x.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    tous('.apparait').forEach(function (s) { obs.observe(s); });
    var obsC = new IntersectionObserver(function (es) {
      es.forEach(function (x) {
        if (!x.isIntersecting) return;
        obsC.unobserve(x.target);
        var b = x.target, fin = parseInt(b.getAttribute('data-compte'), 10) || 0, t0 = null;
        if (fin < 2) return;
        (function pas(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1100); b.textContent = Math.round(fin * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(pas); })(performance.now());
      });
    }, { threshold: 0.6 });
    tous('[data-compte]').forEach(function (b) { obsC.observe(b); });
  } else { tous('.apparait').forEach(function (s) { s.classList.add('vu'); }); }
  if (!calme && window.matchMedia && matchMedia('(hover: hover)').matches) {
    tous('.carte').forEach(function (c) {
      c.addEventListener('pointermove', function (e) { var r = c.getBoundingClientRect(); c.style.setProperty('--ry', ((e.clientX - r.left) / r.width - 0.5) * 7 + 'deg'); c.style.setProperty('--rx', (0.5 - (e.clientY - r.top) / r.height) * 7 + 'deg'); });
      c.addEventListener('pointerleave', function () { c.style.removeProperty('--rx'); c.style.removeProperty('--ry'); });
    });
  }
  var hero = q('.hero');
  if (hero && !calme) {
    var toile = d.createElement('canvas'); toile.className = 'neige-h'; toile.setAttribute('aria-hidden', 'true'); hero.insertBefore(toile, hero.firstChild);
    var cx = toile.getContext('2d'), L = 0, H = 0, fl = [], img = 0, visible = true;
    var taille = function () { var r = Math.min(window.devicePixelRatio || 1, 2); L = hero.clientWidth; H = hero.clientHeight; toile.width = L * r; toile.height = H * r; cx.setTransform(r, 0, 0, r, 0, 0); var n = Math.round(Math.min(70, L / 18)); while (fl.length < n) fl.push({ x: Math.random() * L, y: Math.random() * H, r: 1.4 + Math.random() * 3, v: 0.3 + Math.random() * 0.7, d: Math.random() * 6 }); fl.length = n; };
    var dessine = function () {
      if (lecture) { if (visible) img = requestAnimationFrame(dessine); return; }      // rien pendant la vidéo
      cx.clearRect(0, 0, L, H);
      fl.forEach(function (f) { f.y += f.v; f.d += 0.012; f.x += Math.sin(f.d) * 0.4; if (f.y > H + 6) { f.y = -6; f.x = Math.random() * L; } cx.beginPath(); cx.fillStyle = 'rgba(255,255,255,.95)'; cx.shadowColor = 'rgba(120,100,80,.35)'; cx.shadowBlur = 4; cx.arc(f.x, f.y, f.r, 0, 6.2832); cx.fill(); });
      if (visible) img = requestAnimationFrame(dessine);
    };
    taille(); window.addEventListener('resize', taille);
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting && !d.hidden; cancelAnimationFrame(img); if (visible) img = requestAnimationFrame(dessine); }).observe(hero);
    d.addEventListener('visibilitychange', function () { visible = !d.hidden; cancelAnimationFrame(img); if (visible) img = requestAnimationFrame(dessine); });
  }

  /* ---- Carrousel en anneau des dessins (rotation continue, glissement à la souris ou au doigt, inertie) ---- */
  // Pluie de confettis sur le message de remerciement (rien si le visiteur a demandé moins d'animations).
  function confettis(toile) {
    if (!toile || !toile.getContext || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var c = toile.getContext('2d'), l = toile.width = toile.offsetWidth, h = toile.height = toile.offsetHeight;
    var teintes = ['#c1272f', '#e3c98a', '#2f7d4f', '#f3dfae', '#8f2530', '#ffffff'], grains = [], debut = performance.now();
    for (var i = 0; i < 110; i++) grains.push({ x: Math.random() * l, y: -20 - Math.random() * h * .6, vx: (Math.random() - .5) * 2.4, vy: 2 + Math.random() * 3.4, t: 5 + Math.random() * 7, a: Math.random() * 6.3, va: (Math.random() - .5) * .3, k: teintes[i % teintes.length], rond: i % 4 === 0 });
    (function dessiner(n) {
      var ecoule = n - debut; c.clearRect(0, 0, l, h); c.globalAlpha = Math.max(0, 1 - Math.max(0, ecoule - 3200) / 1400);
      grains.forEach(function (g) {
        g.x += g.vx; g.y += g.vy; g.a += g.va; g.vy += .02;
        c.save(); c.translate(g.x, g.y); c.rotate(g.a); c.fillStyle = g.k; c.strokeStyle = 'rgba(20,16,12,.12)';
        if (g.rond) { c.beginPath(); c.arc(0, 0, g.t / 2, 0, 6.3); c.fill(); c.stroke(); } else { c.fillRect(-g.t / 2, -g.t / 4, g.t, g.t / 2); }
        c.restore();
      });
      if (ecoule < 4600) requestAnimationFrame(dessiner); else c.clearRect(0, 0, l, h);
    })(debut);
  }

  var manege = q('[data-manege]');
  if (manege) {
    var anneau = q('.anneau', manege), faces = tous('.face', manege), nb = faces.length;
    var rot = 0, vit = 0, dernier = 0, saisi = false, x0 = 0, parcouru = 0, rayon = 0, enVue = true, boucle = 0;
    var auto = calme ? 0 : 9;                                    // degrés par seconde
    var poser = function () {
      var l = anneau.offsetWidth;
      rayon = (l * 1.22) / (2 * Math.tan(Math.PI / nb));
      faces.forEach(function (f, i) { f.style.transform = 'rotateY(' + (i * 360 / nb) + 'deg) translateZ(' + rayon + 'px)'; });
    };
    var appliquer = function () { anneau.style.transform = 'translateZ(' + (-rayon) + 'px) rotateY(' + rot + 'deg)'; };
    var tourner = function (t) {
      if (lecture) { dernier = 0; if (enVue) boucle = requestAnimationFrame(tourner); return; }      // rien pendant la vidéo
      var dt = dernier ? Math.min((t - dernier) / 1000, 0.1) : 0; dernier = t;
      if (!saisi) { if (Math.abs(vit) > 0.5) { rot += vit * dt; vit *= 0.94; } else { rot += auto * dt; } }
      appliquer();
      if (enVue) boucle = requestAnimationFrame(tourner);
    };
    poser(); appliquer(); window.addEventListener('resize', function () { poser(); appliquer(); });
    manege.addEventListener('pointerdown', function (e) { saisi = true; x0 = e.clientX; parcouru = 0; vit = 0; manege.classList.add('saisi'); });
    window.addEventListener('pointermove', function (e) { if (!saisi) return; var dx = e.clientX - x0; x0 = e.clientX; parcouru += Math.abs(dx); rot += dx * 0.35; vit = dx * 0.35 * 60; if (calme) appliquer(); });
    var lacher = function () { saisi = false; manege.classList.remove('saisi'); };
    window.addEventListener('pointerup', lacher); window.addEventListener('pointercancel', lacher);
    manege.addEventListener('click', function (e) { if (parcouru > 8) { e.preventDefault(); e.stopPropagation(); } }, true);   // un glissement n'est pas un clic
    manege.addEventListener('dragstart', function (e) { e.preventDefault(); });
    new IntersectionObserver(function (es) { enVue = es[0].isIntersecting; cancelAnimationFrame(boucle); dernier = 0; if (enVue) boucle = requestAnimationFrame(tourner); }).observe(manege);
  }

  /* Arrivée par un lien partagé : on amène le visiteur au dessin. */
  var vedette = q('.vedette');
  if (vedette && !location.hash) vedette.scrollIntoView({ block: 'start' });
})();
