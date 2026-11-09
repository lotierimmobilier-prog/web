// LOTIER Immobilier : interactions et animations de la page d'accueil (direction « Isométrique »).
// Aucune dépendance. Les animations respectent « réduire les animations » du système.

/* Une page ouverte par un clic sur un lien démarre en haut (sauf lien avec ancre, retour ou rechargement). */
(function () {
  try {
    var nav = performance.getEntriesByType('navigation')[0];
    if ((!nav || nav.type === 'navigate') && !location.hash) {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      var touched = false;
      ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (t) { window.addEventListener(t, function () { touched = true; }, { once: true, passive: true }); });
      window.addEventListener('load', function () { if (!touched && !location.hash && window.scrollY > 0) window.scrollTo({ top: 0, left: 0, behavior: 'instant' }); });
    }
  } catch (e) { /* navigateur ancien : comportement par défaut */ }
})();

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
      root.classList.toggle('nav-open', open);
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('open');
        root.classList.remove('nav-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Ouvrir le menu');
      }
    });
  }


  // ----- Fenêtre « Nos agences » -----
  var dlg = document.getElementById('agences-dialog');
  if (dlg) {
    document.querySelectorAll('[data-open-agences]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
      });
    });
    dlg.addEventListener('click', function (e) {
      if (e.target === dlg || e.target.closest('[data-close-agences]')) { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); }
    });
  }

  // ----- Cloche des nouveautés -----
  var bell = document.querySelector('[data-bell]');
  var panel = document.getElementById('news-panel');
  if (bell && panel) {
    var badge = bell.querySelector('[data-bell-badge]');
    var ids = [].map.call(panel.querySelectorAll('[data-news-id]'), function (a) { return a.getAttribute('data-news-id'); });
    var KEY = 'lotier-news-seen';
    function seen() { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
    function markSeen() { try { localStorage.setItem(KEY, JSON.stringify(ids)); } catch (e) {} }
    function refresh() {
      var s = seen(), n = ids.filter(function (i) { return s.indexOf(i) < 0; }).length;
      badge.textContent = n; badge.hidden = n === 0;
      bell.setAttribute('aria-label', n ? 'Nouveautés, ' + n + ' à découvrir' : 'Nouveautés');
      if (navToggle) navToggle.classList.toggle('has-news', n > 0);
    }
    function setOpen(o) {
      panel.hidden = !o; bell.setAttribute('aria-expanded', String(o));
      if (o) { markSeen(); refresh(); }
    }
    refresh();
    bell.addEventListener('click', function (e) { e.stopPropagation(); var o = panel.hidden; setOpen(o); if (!o) refresh(); });
    panel.addEventListener('click', function (e) { e.stopPropagation(); });
    document.addEventListener('click', function () { if (!panel.hidden) { setOpen(false); refresh(); } });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { setOpen(false); refresh(); bell.focus(); } });
  }


  // ----- Assistant de chat (portée isolée) -----
  (function () {
  var chat = document.getElementById('chat');
  if (chat) {
    var fab = chat.querySelector('[data-chat-open]'), cp = document.getElementById('chat-panel');
    var log = document.getElementById('chat-log'), chips = document.getElementById('chat-chips');
    var form = document.getElementById('chat-form'), input = document.getElementById('chat-input');
    var P = chat.getAttribute('data-prefix') || '', EP = chat.getAttribute('data-endpoint') || '';
    var TEL = chat.getAttribute('data-phone'), TELL = chat.getAttribute('data-phone-label');
    var history = [], started = false;
    var L = {
      est: ['Estimer mon bien', P + 'index.html#estimer'], rdv: ['Contacter l\'agence', P + 'index.html#contact'],
      hon: ['Nos honoraires', P + 'nos-honoraires/'], blog: ['Les conseils du blog', P + 'blog/index.html'],
      join: ['Devenir agent', P + 'rejoindre/'], cmp: ['Comparatif réseaux et agences', P + 'rejoindre/comparatif/'],
      my: ['Espace client MyLotier', P + 'mylotier/'], faq: ['Questions fréquentes', P + 'index.html#conseils'],
      ann: ['Voir les annonces', P + 'index.html#annonces']
    };
    var KB = [
      { k: ['estim', 'valeur', 'prix de mon', 'combien vaut'], t: 'Pour estimer votre bien, indiquez son adresse et ses caractéristiques dans le formulaire d\'estimation : un conseiller vous recontacte pour affiner avec une visite.', l: ['est', 'blog'] },
      { k: ['rendez', 'rdv', 'rencontr', 'visite'], t: 'Pour échanger avec un conseiller, appelez-nous ou passez par la section contact : il vous répond.', l: ['rdv'], tel: 1 },
      { k: ['honorair', 'frais', 'tarif', 'commission', 'combien coute', 'coût', 'cout'], t: 'Notre barème est détaillé sur la page des honoraires. La gestion locative démarre à 39,99 € par mois. Pour un devis précis, un conseiller vous répond.', l: ['hon'], tel: 1 },
      { k: ['louer', 'location', 'locataire', 'bailleur', 'gestion locative'], t: 'Nous trouvons le locataire, rédigeons le bail et suivons votre bien, avec une gestion locative à partir de 39,99 € par mois.', l: ['rdv', 'blog'] },
      { k: ['vendre', 'vente', 'mandat'], t: 'Estimation, mandat, visites, signature : un conseiller vous accompagne jusqu\'à l\'acte. Commencez par une estimation.', l: ['est', 'blog'] },
      { k: ['acheter', 'achat', 'annonce', 'bien a vendre', 'maison', 'appartement'], t: 'Retrouvez nos biens dans la section annonces, ou dites-nous ce que vous cherchez et un conseiller vous rappelle.', l: ['ann', 'rdv'] },
      { k: ['syndic', 'copro'], t: 'Nous gérons des copropriétés (assemblées générales, charges, travaux). Parlez-en à un conseiller pour une proposition adaptée.', l: ['rdv', 'blog'] },
      { k: ['agence', 'adresse', 'bureau', 'ou etes', 'où êtes', 'trouver'], t: 'Notre siège est au 40 rue Française, 34500 Béziers, et nous avons aussi des agences à Montpellier et Nîmes.', agences: 1 },
      { k: ['horaire', 'ouvert', 'ferme', 'fermé'], t: 'Les horaires sont à confirmer avec l\'agence : le plus simple est de nous appeler.', tel: 1 },
      { k: ['recrut', 'rejoindre', 'devenir agent', 'mandataire', 'emploi', 'travailler'], t: 'Vous souhaitez devenir agent immobilier indépendant avec LOTIER ? Tout est expliqué sur la page dédiée, avec un simulateur de commission.', l: ['join', 'cmp'] },
      { k: ['espace client', 'mylotier', 'my lotier', 'connexion', 'mon espace', 'identifiant'], t: 'MyLotier est l\'espace client de LOTIER. Si vous avez perdu vos accès, contactez l\'agence.', l: ['my'], tel: 1 },
      { k: ['contact', 'joindre', 'telephone', 'téléphone', 'appeler', 'mail'], t: 'Vous pouvez nous joindre par téléphone ou par e-mail à contact@lotier-immobilier.com.', tel: 1 },
      { k: ['bonjour', 'salut', 'bonsoir', 'hello'], t: 'Bonjour ! Dites-moi ce que vous cherchez : estimation, vente, location, syndic ou espace client.', l: ['est', 'faq'] },
      { k: ['merci'], t: 'Avec plaisir ! N\'hésitez pas si vous avez d\'autres questions.', l: [] }
    ];
    var START = [['Estimer mon bien', 'estimer'], ['Vendre', 'vendre'], ['Louer', 'location'], ['Nos agences', 'agence'], ['Parler à un conseiller', 'conseiller']];
    function norm(x) { return x.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
    /* Texte d'Auguste -> noeuds DOM : adresses web et numéros de téléphone deviennent des liens (jamais de HTML injecté). */
    var LIEN = /((?:https?:\/\/|www\.)[^\s<>()]*[^\s<>().,;:!?]|0[1-9](?:[ .]?\d{2}){4})/g;
    function fill(el, text) {
      var s = String(text == null ? '' : text), last = 0, m;
      LIEN.lastIndex = 0;
      while ((m = LIEN.exec(s)) !== null) {
        if (m.index > last) el.appendChild(document.createTextNode(s.slice(last, m.index)));
        var t = m[0], a = document.createElement('a');
        if (/^0/.test(t)) { a.href = 'tel:+33' + t.replace(/[^0-9]/g, '').slice(1); }
        else { a.href = /^www\./i.test(t) ? 'https://' + t : t; a.target = '_blank'; a.rel = 'noopener noreferrer'; }
        a.textContent = t; el.appendChild(a); last = m.index + t.length;
      }
      if (last < s.length) el.appendChild(document.createTextNode(s.slice(last)));
    }
    /* Auguste, l'assistant de Collab : /session ouvre une conversation (jeton, accueil, image), /message répond.
       Sans réponse de Collab (hors ligne, désactivé, trop de messages), les réponses locales ci-dessous prennent le relais. */
    var API = EP.replace(/\/+$/, ''), ORIGIN = '';
    try { ORIGIN = new URL(API).origin; } catch (e) { API = ''; }
    var token = null, offline = !API, opening = null;
    function setAvatar(u) {
      var box = chat.querySelector('[data-chat-avatar]');
      if (!box || !u) return;
      try {
        var x = new URL(u, ORIGIN + '/');
        if (!/^https?:$/.test(x.protocol)) return;
        var im = document.createElement('img'); im.src = x.href; im.alt = ''; im.width = 40; im.height = 40;
        box.textContent = ''; box.appendChild(im); box.hidden = false;
      } catch (e) { /* image d'Auguste indisponible : l'en-tête reste sans image */ }
    }
    function openSession() {
      if (token) return Promise.resolve({ token: token });
      if (offline) return Promise.resolve(null);
      if (opening) return opening;
      opening = fetch(API + '/session', { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.enabled && d.token) { token = d.token; if (d.avatar) setAvatar(d.avatar); return d; }
          offline = true; return null;
        })
        .catch(function () { offline = true; return null; })
        .then(function (d) { opening = null; return d; });
      return opening;
    }
    function envoyer(q) {
      return fetch(API + '/message', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token: token, message: q.slice(0, 1500) }) })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, j: j || {} }; }); });
    }
    function msg(who, text, extra) {
      var d = document.createElement('div'); d.className = 'cm cm-' + who;
      var b = document.createElement('div'); b.className = 'cm-b'; if (who === 'bot') fill(b, text); else b.textContent = text; d.appendChild(b);
      if (extra) { var r = document.createElement('div'); r.className = 'cm-l';
        (extra.l || []).forEach(function (k) { var a = document.createElement('a'); a.href = L[k][1]; a.textContent = L[k][0]; r.appendChild(a); });
        if (extra.agences) { var bt = document.createElement('button'); bt.type = 'button'; bt.textContent = 'Voir les adresses'; bt.addEventListener('click', function () { var dg = document.getElementById('agences-dialog'); if (dg && dg.showModal) { setChat(false); dg.showModal(); } }); r.appendChild(bt); }
        if (extra.tel) { var a2 = document.createElement('a'); a2.href = 'tel:' + TEL; a2.textContent = 'Appeler le ' + TELL; r.appendChild(a2); }
        if (r.childNodes.length) d.appendChild(r); }
      log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
    }
    function local(q) {
      var n = norm(q);
      if (/conseiller|humain|parler a/.test(n)) return { t: 'Bien sûr : un conseiller peut vous répondre par téléphone.', tel: 1, l: ['rdv'] };
      for (var i = 0; i < KB.length; i++) for (var j = 0; j < KB[i].k.length; j++) if (n.indexOf(norm(KB[i].k[j])) > -1) return KB[i];
      return { t: 'Je n\'ai pas la réponse précise à cette question. Un conseiller peut vous aider directement.', tel: 1, l: ['faq', 'rdv'] };
    }
    function reply(q) {
      history.push({ role: 'user', content: q });
      var typing = msg('bot', '…');
      function show(ans) { typing.remove(); if (typeof ans === 'string') { msg('bot', ans); history.push({ role: 'assistant', content: ans }); } else { msg('bot', ans.t, ans); history.push({ role: 'assistant', content: ans.t }); } }
      if (API) {
        openSession().then(function (d) {
          if (!d) return show(local(q));
          return envoyer(q).then(function (x) {
            if (x.j.reply) return show(x.j.reply);
            if (x.status === 404) { token = null; return openSession().then(function (d2) { return d2 ? envoyer(q).then(function (y) { show(y.j.reply || local(q)); }) : show(local(q)); }); }
            if (x.status === 429 && x.j.error) return show(x.j.error);
            show(local(q));
          });
        }).catch(function () { show(local(q)); });
      } else { setTimeout(function () { show(local(q)); }, 450); }
    }
    function ask(q) { q = (q || '').trim(); if (!q) return; msg('user', q); chips.hidden = true; reply(q); }
    function setChat(o) {
      cp.hidden = !o; fab.setAttribute('aria-expanded', String(o)); chat.classList.toggle('open', o);
      if (o) {
        if (!started) {
          started = true;
          var ACCUEIL = 'Bonjour, je suis Auguste, l\'assistant de LOTIER Immobilier, disponible 7j/7. Un conseiller reprend la main dès que vous le souhaitez.';
          var accueilFait = false;
          var accueil = function (t) { if (accueilFait) return; accueilFait = true; msg('bot', t || ACCUEIL); };
          /* l'accueil vient de Collab (réglage de l'agence) ; au bout de 3 s sans réponse, le texte local s'affiche */
          var attente = setTimeout(function () { accueil(); }, 3000);
          openSession().then(function (d) { clearTimeout(attente); accueil(d && d.welcome); });
          START.forEach(function (s) { var b = document.createElement('button'); b.type = 'button'; b.textContent = s[0]; b.addEventListener('click', function () { ask(s[0]); }); chips.appendChild(b); });
        }
        setTimeout(function () { input.focus(); }, 50);
      } else { fab.focus(); }
    }
    fab.addEventListener('click', function () { setChat(cp.hidden); });
    chat.querySelector('[data-chat-close]').addEventListener('click', function () { setChat(false); });
    form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value; input.value = ''; ask(v); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !cp.hidden) setChat(false); });
  }
  })();


  // ----- Ciel : nuages en parallaxe derrière les bandeaux d'en-tête de page -----
  (function () {
    var hosts = document.querySelectorAll('.hero, .page-hero');
    if (!hosts.length) return;
    var NS = 'http://www.w3.org/2000/svg';
    var defs = document.createElementNS(NS, 'svg');
    defs.setAttribute('width', '0'); defs.setAttribute('height', '0'); defs.setAttribute('aria-hidden', 'true'); defs.style.position = 'absolute';
    defs.innerHTML = '<defs><linearGradient id="ng" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="#eef5fd"/><stop offset="1" stop-color="#bdd3ee"/></linearGradient>' +
      '<symbol id="nuage" viewBox="0 0 240 110"><path fill="url(#ng)" d="M50 96c-22 0-38-13-38-30 0-15 12-27 28-29 3-17 20-30 40-30 14 0 26 6 33 16 6-5 14-8 23-8 20 0 36 14 38 32 17 1 30 13 30 28 0 14-14 21-32 21z"/></symbol></defs>';
    document.body.insertBefore(defs, document.body.firstChild);
    var FULL = [[6, 150, 110, -20, 'far', 11], [30, 120, 120, -75, 'far', 13], [52, 140, 105, -50, 'far', 12], [14, 260, 80, -10, 'mid', 9], [46, 300, 90, -55, 'mid', 10], [70, 240, 85, -35, 'mid', 8], [24, 420, 62, -30, 'near', 8], [60, 460, 70, -8, 'near', 9]];
    var LIGHT = [[8, 130, 110, -25, 'far', 11], [55, 150, 105, -70, 'far', 12], [20, 240, 85, -15, 'mid', 9], [50, 280, 95, -60, 'mid', 10]];
    [].forEach.call(hosts, function (host) {
      [].forEach.call(host.querySelectorAll('.orb, .cloud'), function (n) { n.parentNode.removeChild(n); });
      var sky = document.createElement('div'); sky.className = 'sky'; sky.setAttribute('aria-hidden', 'true');
      (host.classList.contains('hero') && !host.classList.contains('hero-tight') ? FULL : LIGHT).forEach(function (c) {
        var el = document.createElement('span'); el.className = 'cl cl-' + c[4];
        el.style.cssText = 'top:' + c[0] + '%;width:' + c[1] + 'px;--d:' + c[2] + 's;--dl:' + c[3] + 's;--b:' + c[5] + 's';
        el.innerHTML = '<svg viewBox="0 0 240 110" aria-hidden="true"><use href="#nuage"/></svg>';
        sky.appendChild(el);
      });
      host.insertBefore(sky, host.firstChild);
    });
  })();

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

  // ----- Boutons magnétiques et cartes inclinables : retirés (effet de démonstration) -----
  if (false) {
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
  var SETS = {
    services: [
    { n: 'Conseil', t: 'Un conseiller à votre écoute', p: 'On commence toujours par vous écouter, avant de parler prix ou calendrier.', a: 'Nous contacter', h: '#contact' },
    { n: 'Location', t: 'Louer l\'esprit tranquille', p: 'Nous trouvons le locataire, rédigeons le bail et suivons votre bien. À partir de 39,99 € par mois.', a: 'Mettre mon bien en location', h: 'mailto:gestion@lotier-immobilier.com' },
    { n: 'Vente', t: 'Vendre au bon prix', p: 'Estimation, mandat, visites, signature : un conseiller vous accompagne jusqu\'à l\'acte.', a: 'Estimer mon bien', h: '#estimer' },
    { n: 'Syndic', t: 'Une copropriété claire', p: 'Assemblées, charges, travaux : une gestion transparente pour votre immeuble.', a: 'Écrire au syndic', h: 'mailto:syndic@lotier-immobilier.com' },
    { n: 'Estimation', t: 'Combien vaut votre bien ?', p: 'Une estimation appuyée sur les ventes récentes de votre quartier.', a: 'Estimer mon bien', h: '#estimer' }
  ],
    parcours: [
      { n: 'Candidature', t: 'Un échange avec l\'équipe', p: 'Présentez votre parcours et vos motivations par téléphone ou avec le formulaire de candidature.', a: 'Postuler', h: '#postuler' },
      { n: 'Carte pro', t: 'On monte votre dossier', p: 'Constitution du dossier de carte professionnelle, valable trois ans.', a: 'Voir les conditions', h: '#conditions' },
      { n: 'Kit et formation', t: 'Une semaine pour démarrer', p: 'Vous recevez votre kit de démarrage et suivez une semaine de formation avec un formateur dédié.', a: 'Voir le parcours', h: '#parcours' },
      { n: 'Premières ventes', t: 'Accompagné dès le début', p: 'Vous démarrez avec l\'équipe à chaque étape, avec un mentor dédié dès votre arrivée.', a: 'Voir le parcours', h: '#parcours' },
      { n: 'Indépendance', t: 'Signez votre indépendance', p: '75 % de commission HT, sans redevance de marque ni quotas imposés.', a: 'Postuler maintenant', h: '#postuler' }
    ]
  };
  var FLOORS = SETS.services;
  var ARIA = 'Immeuble en trois dimensions : chaque étage est un service de l\'agence';


  function isoSvg() {
    var S = 46, W = 3.1, D = 2.5, H = 1.0, ox = 300, oy = 330, c30 = Math.cos(Math.PI / 6), s30 = Math.sin(Math.PI / 6);
    function P(x, y, z) { return [(ox + (x - y) * c30 * S).toFixed(1), (oy + (x + y) * s30 * S - z * S).toFixed(1)].join(','); }
    function poly(pts, cls, style) { return '<polygon class="' + cls + '"' + (style ? ' style="' + style + '"' : '') + ' points="' + pts.map(function (q) { return P(q[0], q[1], q[2]); }).join(' ') + '"/>'; }
    var s = '<svg viewBox="0 0 600 470" role="group" aria-label="' + ARIA + '"><defs><filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter></defs>';
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
    if (isoBox.dataset.floors === 'parcours') { FLOORS = SETS.parcours; ARIA = 'Immeuble en trois dimensions : chaque étage est une étape pour devenir agent LOTIER'; }
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
  var offreInput = document.getElementById('offre');
  function setMode(key) {
    if (!budgetLabel || !budgetInput) return;
    tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.getAttribute('data-mode') === key)); });
    budgetLabel.textContent = modes[key].label;
    budgetInput.placeholder = modes[key].hint;
    if (offreInput) offreInput.value = key;
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { setMode(t.getAttribute('data-mode')); }); });
  // « Rechercher » ouvre Nos annonces avec les critères (?offre=&ville=&bien=&max=) ; les champs vides ne sont pas envoyés.
  var rech = document.getElementById('recherche');
  if (rech) rech.addEventListener('submit', function () {
    [].forEach.call(rech.querySelectorAll('select[name], input[name]:not([type=hidden])'), function (f) { if (!String(f.value).trim()) f.disabled = true; });
    var m = budgetInput && budgetInput.value.replace(/\D/g, ''); if (m) budgetInput.value = m;
  });
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

  // ----- Recrutement : simulateur de commission -----
  var sim = document.getElementById('simulateur');
  if (sim) {
    var range = document.getElementById('sim-range');
    var eur = function (n) { return Math.round(n).toLocaleString('fr-FR') + ' €'; };
    var rows = [['a', 0.55], ['b', 0.65], ['l', 0.75]];
    var runSim = function () {
      var v = +range.value;
      document.getElementById('sim-honoraires').textContent = eur(v);
      rows.forEach(function (r) {
        document.getElementById('sim-' + r[0]).textContent = eur(v * r[1]);
        document.getElementById('bar-' + r[0]).style.width = (r[1] / 0.75 * 100) + '%';
      });
      document.getElementById('sim-gap').textContent = '+ ' + eur(v * (0.75 - 0.65));
    };
    range.addEventListener('input', runSim);
    document.getElementById('sim-replay').addEventListener('click', function () {
      rows.forEach(function (r) { document.getElementById('bar-' + r[0]).style.width = '0%'; });
      void sim.offsetWidth;
      setTimeout(runSim, 60);
    });
    runSim();
  }

  // ----- Recrutement : formulaire de candidature (prépare un e-mail) -----
  var apply = document.getElementById('postuler-form');
  if (apply) {
    apply.addEventListener('submit', function (e) {
      e.preventDefault();
      var g = function (id) { return document.getElementById(id).value.trim(); };
      var body = 'Bonjour,\n\nJe souhaite rejoindre LOTIER Immobilier comme agent commercial indépendant.\n\nNom : ' + g('ap-nom') + '\nTéléphone : ' + g('ap-tel') + '\nE-mail : ' + g('ap-mail') + '\nVille : ' + g('ap-ville') + '\nSituation : ' + g('ap-situation') + '\n\nMessage :\n' + g('ap-msg') + '\n\nMerci de me recontacter.';
      window.location.href = 'mailto:recrutement@lotier-immobilier.com?subject=' + encodeURIComponent('Candidature agent commercial indépendant') + '&body=' + encodeURIComponent(body);
    });
  }
})();

/* Bandeau cookies : le choix est mémorisé localement (aucun traceur n'est actif tant que ce site n'en utilise pas). */
(function () {
  var KEY = 'lotier-cookies-v1', box = null;
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function saved() { try { var r = read(); return r ? JSON.parse(r).choix : null; } catch (e) { return null; } }
  function save(v) {
    try { localStorage.setItem(KEY, JSON.stringify({ choix: v, date: new Date().toISOString() })); } catch (e) {}
    try { if (v === 'essentiels') localStorage.setItem('umami.disabled', '1'); else localStorage.removeItem('umami.disabled'); } catch (e) {}
  }
  /* Mesure d'audience Umami (sans cookie) : active par défaut, désactivée si le visiteur l'a refusée. */
  (function () {
    if (saved() === 'essentiels') { try { localStorage.setItem('umami.disabled', '1'); } catch (e) {} return; }
    var s = document.createElement('script'); s.defer = true; s.src = 'https://cloud.umami.is/script.js';
    s.setAttribute('data-website-id', 'b7d7a94e-20ba-4db7-b476-349fb21557f6'); document.head.appendChild(s);
  })();
  var chat = document.getElementById('chat');
  var prefix = chat ? chat.getAttribute('data-prefix') || '' : '';
  function close() { if (box) { box.remove(); box = null; } }
  function open() {
    if (box) return;
    box = document.createElement('div');
    box.className = 'cookie-banner';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-labelledby', 'ck-title');
    box.innerHTML =
      '<img class="ck-logo" src="' + prefix + 'assets/lotier-logo.png" alt="" width="110" height="37">' +
      '<h2 id="ck-title">Les cookies de LOTIER</h2>' +
      '<p>Comme pour tout bien immobilier, on a besoin de vous faire signer quelque chose. Nos cookies servent à mémoriser vos préférences, rien de plus, promis (pas de clause abusive dans nos CGV). Ce site ne dépose aucun cookie publicitaire. Sa fréquentation est mesurée sans cookie (pages vues, provenance) : vous pouvez le refuser ci-dessous. <a href="' + prefix + 'lotier-rgpd/#cookies">Registre RGPD</a></p>' +
      '<div class="ck-actions"><button type="button" class="btn btn-primary" data-ck="ok">Ok pour moi</button>' +
      '<button type="button" class="btn btn-ghost" data-ck="non">Refuser</button>' +
      '<button type="button" class="btn btn-ghost" data-ck="perso">Je choisis</button></div>' +
      '<div class="ck-choix" hidden><label><input type="checkbox" checked disabled> Essentiels : mémoriser vos préférences (toujours actifs)</label>' +
      '<label><input type="checkbox" id="ck-stats" checked> Mesure d’audience sans cookie (décochez pour la refuser)</label>' +
      '<button type="button" class="btn btn-primary" data-ck="valider">Valider mon choix</button></div>';
    document.body.appendChild(box);
    if (saved() === 'essentiels') box.querySelector('#ck-stats').checked = false;
    box.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-ck]'); if (!b) return;
      var a = b.getAttribute('data-ck');
      if (a === 'perso') { box.querySelector('.ck-choix').hidden = false; b.hidden = true; return; }
      save(a === 'ok' ? 'tout' : a === 'non' ? 'essentiels' : (box.querySelector('#ck-stats').checked ? 'tout' : 'essentiels'));
      close();
    });
  }
  document.addEventListener('click', function (ev) { if (ev.target.closest('[data-cookie-open]')) open(); });
  if (!read()) setTimeout(open, 900);
})();

/* Page des agents : la liste est lue dans data/agents.json (le HTML sert de secours sans JavaScript), avec filtre par secteur. */
(function () {
  var bar = document.querySelector('.agents-filter');
  var wrap = document.querySelector('.agent-sects');
  if (!bar || !wrap) return;
  var prefix = (document.getElementById('chat') || {}).getAttribute ? document.getElementById('chat').getAttribute('data-prefix') || '' : '';
  function el(tag, cls, txt) { var n = document.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function link(href, cls, label, blank) { var a = el('a', cls, label); a.href = href; if (blank) { a.target = '_blank'; a.rel = 'noopener'; } return a; }
  function safeUrl(u) { try { var x = new URL(u, location.href); return /^https?:$/.test(x.protocol) ? x.href : null; } catch (e) { return null; } }
  function initials(n) { return n.split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join('').toUpperCase(); }
  function card(a, names) {
    var c = el('article', 'glass agent-card'), head = el('div', 'agent-head'), h = el('div');
    if (a.photo) { var im = el('img', 'agent-photo'); im.src = prefix + a.photo; im.alt = ''; im.width = 72; im.height = 72; im.loading = 'lazy'; head.appendChild(im); }
    else head.appendChild(el('span', 'agent-photo agent-ini', initials(a.nom)));
    h.appendChild(el('h3', null, a.nom)); if (a.role) h.appendChild(el('p', 'small muted', a.role));
    head.appendChild(h); c.appendChild(head);
    var tags = el('div', 'tags'); (a.secteurs || []).forEach(function (id) { if (names[id]) tags.appendChild(el('span', 'tag', names[id])); }); c.appendChild(tags);
    if (a.communes) c.appendChild(el('p', 'small muted', a.communes));
    var links = el('div', 'agent-links');
    if (a.telephone) links.appendChild(link('tel:' + a.telephone.replace(/[^0-9+]/g, ''), '', a.telephone));
    if (a.email) links.appendChild(link('mailto:' + a.email, '', a.email));
    var site = a.site && safeUrl(a.site); if (site) links.appendChild(link(site, '', 'Voir le mini-site', true));
    c.appendChild(links); return c;
  }
  function render(data) {
    var names = {}; data.secteurs.forEach(function (s) { names[s.id] = s.nom; });
    bar.textContent = '';
    var all = el('button', 'chip-link is-on', 'Tous les secteurs'); all.type = 'button'; all.setAttribute('data-sect', 'all'); all.setAttribute('aria-pressed', 'true'); bar.appendChild(all);
    wrap.textContent = '';
    data.secteurs.forEach(function (s) {
      var b = el('button', 'chip-link', s.nom); b.type = 'button'; b.setAttribute('data-sect', s.id); b.setAttribute('aria-pressed', 'false'); bar.appendChild(b);
      var sec = el('section', 'agent-sect'); sec.setAttribute('data-sect', s.id);
      var h2 = el('h2', 'heading', s.nom + ' '); h2.appendChild(el('span', 'muted small', s.dept || '')); sec.appendChild(h2);
      var grid = el('div', 'agent-grid'), list = data.agents.filter(function (a) { return (a.secteurs || []).indexOf(s.id) > -1; });
      if (list.length) list.forEach(function (a) { grid.appendChild(card(a, names)); });
      else { var p = el('p', 'muted agent-empty', 'Aucun agent référencé sur ce secteur pour le moment. '); p.appendChild(link(prefix + 'index.html#contact', 'text-link', "Contacter l'agence")); p.appendChild(document.createTextNode('.')); grid.appendChild(p); }
      sec.appendChild(grid); wrap.appendChild(sec);
    });
  }
  function apply(id) {
    wrap.querySelectorAll('.agent-sect').forEach(function (s) { s.hidden = id !== 'all' && s.getAttribute('data-sect') !== id; });
    bar.querySelectorAll('[data-sect]').forEach(function (b) { var on = b.getAttribute('data-sect') === id; b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
  }
  bar.addEventListener('click', function (ev) { var b = ev.target.closest('[data-sect]'); if (b) apply(b.getAttribute('data-sect')); });
  if (window.fetch) fetch(wrap.getAttribute('data-src'), { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : Promise.reject(); })
    .then(function (d) { if (d && Array.isArray(d.secteurs) && Array.isArray(d.agents)) render(d); }).catch(function () { /* HTML de secours conservé */ });
})();

/* WebMCP : expose quelques actions du site aux agents du navigateur (navigator.modelContext).
   Aucune donnée n'est envoyée : les outils lisent les coordonnées publiques, ouvrent une page
   ou préparent le formulaire d'estimation (c'est la personne qui valide l'envoi). */
(function () {
  var mc = navigator.modelContext;
  if (!mc || typeof mc.registerTool !== 'function') return;
  var ORIGIN = 'https://lotier.immo';
  var PAGES = { accueil: '/', vente: '/vente/', location: '/location/', syndic: '/syndic/', honoraires: '/nos-honoraires/', 'notre-service': '/notre-service/', 'a-propos': '/a-propos/', contact: '/contact/', blog: '/blog/', agents: '/nos-agents/', rejoindre: '/rejoindre/', 'espace-client': '/mylotier/' };
  function out(t) { return { content: [{ type: 'text', text: t }] }; }
  function reg(tool) { try { mc.registerTool(tool); } catch (e) { /* outil déjà déclaré ou API indisponible */ } }

  reg({
    name: 'get_agency_contact',
    description: 'Coordonnées de LOTIER Immobilier : téléphone, e-mail, agences (Béziers, Montpellier, Nîmes, Carcassonne).',
    inputSchema: { type: 'object', properties: {} },
    annotations: { readOnlyHint: true },
    execute: function () {
      return out('LOTIER Immobilier, agence immobilière indépendante. Téléphone : 04 67 11 28 31. E-mail : contact@lotier-immobilier.com. Agences : Béziers (siège), Montpellier, Nîmes, Carcassonne. Détails : ' + ORIGIN + '/contact/');
    }
  });

  reg({
    name: 'open_page',
    description: 'Ouvre une page du site LOTIER Immobilier : accueil, vente, location, syndic, honoraires, notre-service, a-propos, contact, blog, agents, rejoindre, espace-client.',
    inputSchema: { type: 'object', properties: { page: { type: 'string', enum: Object.keys(PAGES), description: 'Page à ouvrir.' } }, required: ['page'] },
    execute: function (args) {
      var p = PAGES[args && args.page];
      if (!p) return out('Page inconnue. Pages disponibles : ' + Object.keys(PAGES).join(', ') + '.');
      window.location.href = ORIGIN + p;
      return out('Ouverture de ' + ORIGIN + p);
    }
  });

  reg({
    name: 'prepare_estimation_request',
    description: "Prépare la demande d'estimation gratuite : ouvre le formulaire d'estimation avec l'adresse du bien. La personne vérifie puis valide elle-même l'envoi.",
    inputSchema: { type: 'object', properties: { address: { type: 'string', description: 'Adresse du bien à estimer.' } }, required: ['address'] },
    execute: function (args) {
      var adr = document.getElementById('est-adresse');
      if (!adr) { window.location.href = ORIGIN + '/#estimer'; return out("Ouverture du formulaire d'estimation : " + ORIGIN + '/#estimer'); }
      adr.value = String((args && args.address) || '').slice(0, 200);
      var f = document.getElementById('estimer'); if (f && f.scrollIntoView) f.scrollIntoView({ behavior: 'smooth', block: 'center' });
      adr.focus();
      return out("Adresse saisie dans le formulaire d'estimation. La personne doit ajouter son téléphone et valider.");
    }
  });
})();

/* Page Nos annonces : filtres (vente/location, type de bien, département, ville, budget) et tri. Le HTML contient déjà toutes les annonces ;
   l'état se lit et s'écrit dans l'adresse (?offre=vente&bien=maison&dep=34&ville=Béziers&min=100000&max=300000&tri=prix-asc) pour partager une recherche. */
(function () {
  var root = document.querySelector('[data-annonces]');
  if (!root) return;
  var grid = root.querySelector('[data-ann-grid]'), cards = [].slice.call(grid.querySelectorAll('.card'));
  var el = function (k) { return root.querySelector('[data-ann-' + k + ']'); };
  var bien = el('bien'), dep = el('dep'), city = el('city'), pmin = el('pmin'), pmax = el('pmax'), sort = el('sort');
  var count = el('count'), empty = el('empty'), resets = [].slice.call(root.querySelectorAll('[data-ann-reset]'));
  var offre = '', allCities = [].slice.call(city.options).slice(1).map(function (o) { return { v: o.value, dep: o.getAttribute('data-dep') || '' }; });
  cards.forEach(function (c, i) { c.setAttribute('data-ann-i', i); });
  var BUDGETS = {
    vente: [50000, 75000, 100000, 150000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000],
    location: [300, 400, 500, 600, 700, 800, 1000, 1200, 1500, 2000]
  };
  var eur = function (n) { return n.toLocaleString('fr-FR').replace(/ | /g, ' ') + ' €'; };
  function fillBudget(keepMin, keepMax) {
    var list = BUDGETS[offre];
    [[pmin, 'Aucun minimum', keepMin], [pmax, 'Aucun maximum', keepMax]].forEach(function (x) {
      var sel = x[0]; sel.innerHTML = '';
      if (!list) { sel.add(new Option('Choisir vente ou location', '')); sel.disabled = true; return; }
      sel.disabled = false; sel.add(new Option(x[1], ''));
      list.forEach(function (n) { sel.add(new Option(eur(n) + (offre === 'location' ? '/mois' : ''), String(n))); });
      if (x[2] && +x[2] > 0 && list.indexOf(+x[2]) < 0) sel.add(new Option(eur(+x[2]) + (offre === 'location' ? '/mois' : ''), String(+x[2])));   // montant saisi sur l'accueil
      if (x[2]) sel.value = x[2];
    });
  }
  function fillCities() {
    var keep = city.value; city.innerHTML = ''; city.add(new Option('Toutes les villes', ''));
    allCities.forEach(function (c) { if (!dep.value || c.dep === dep.value) { var o = new Option(c.v, c.v); o.setAttribute('data-dep', c.dep); city.add(o); } });
    city.value = [].some.call(city.options, function (o) { return o.value === keep; }) ? keep : '';
  }
  function ok(c) {
    var p = +c.getAttribute('data-ann-prix') || 0, lo = +pmin.value || 0, hi = +pmax.value || 0;
    if (offre && c.getAttribute('data-ann-type') !== offre) return false;
    if (bien.value && c.getAttribute('data-ann-bien') !== bien.value) return false;
    if (dep.value && c.getAttribute('data-ann-dep') !== dep.value) return false;
    if (city.value && c.getAttribute('data-ann-ville') !== city.value) return false;
    if (lo && p < lo) return false;
    if (hi && (!p || p > hi)) return false;
    return true;
  }
  function order() {
    var t = sort.value, k = t.split('-')[0] === 'surf' ? 'data-ann-surf' : 'data-ann-prix', d = t.indexOf('desc') > -1 ? -1 : 1;
    var list = cards.slice().sort(function (a, b) {
      if (!t) return a.getAttribute('data-ann-i') - b.getAttribute('data-ann-i');
      var x = +a.getAttribute(k), y = +b.getAttribute(k);
      if (!x && !y) return 0; if (!x) return 1; if (!y) return -1;   // sans valeur : toujours en dernier
      return (x - y) * d;
    });
    list.forEach(function (c) { grid.appendChild(c); });
  }
  function write() {
    var q = new URLSearchParams();
    [['offre', offre], ['bien', bien.value], ['dep', dep.value], ['ville', city.value], ['min', pmin.value], ['max', pmax.value], ['tri', sort.value]].forEach(function (x) { if (x[1]) q.set(x[0], x[1]); });
    try { history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : '')); } catch (e) { /* adresse non modifiable : sans importance */ }
  }
  function apply() {
    var n = 0, actif = !!(offre || bien.value || dep.value || city.value || pmin.value || pmax.value);
    order();
    cards.forEach(function (c) { var v = ok(c); c.hidden = !v; if (v) n++; });
    count.textContent = n + (n > 1 ? ' annonces' : ' annonce') + (actif ? ' sur ' + cards.length : '');
    empty.hidden = n > 0;
    resets[0].hidden = !actif; write();
  }
  function setOffre(v) {
    offre = v;
    root.querySelectorAll('[data-ann-type-btn]').forEach(function (x) { var on = x.getAttribute('data-ann-type-btn') === v; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', on ? 'true' : 'false'); });
  }
  root.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-ann-type-btn]');
    if (b) { setOffre(b.getAttribute('data-ann-type-btn')); fillBudget('', ''); apply(); return; }
    if (ev.target.closest('[data-ann-reset]')) {
      setOffre(''); bien.value = dep.value = pmin.value = pmax.value = sort.value = ''; fillCities(); fillBudget('', ''); apply();
    }
  });
  dep.addEventListener('change', function () { fillCities(); apply(); });
  [bien, city, pmin, pmax, sort].forEach(function (s) { s.addEventListener('change', apply); });
  // état initial depuis l'adresse
  var q = new URLSearchParams(location.search), g = function (k) { return q.get(k) || ''; };
  setOffre(/^(vente|location)$/.test(g('offre')) ? g('offre') : '');
  bien.value = g('bien'); dep.value = g('dep'); fillCities();
  if (g('ville') && ![].some.call(city.options, function (o) { return o.value === g('ville'); })) city.add(new Option(g('ville') + ' (aucune annonce)', g('ville')));   // ville cherchée sans annonce : on le dit, on n'affiche pas tout
  city.value = g('ville'); if (city.value !== g('ville')) city.value = '';
  var num = function (k) { return g(k).replace(/\D/g, ''); };
  fillBudget(num('min'), num('max')); sort.value = g('tri'); if (sort.value !== g('tri')) sort.value = '';
  apply();
})();

/* Fiche d'annonce : galerie de photos (flèches, clavier, balayage au doigt, miniatures, plein écran). */
(function () {
  var g = document.querySelector('[data-gal]');
  if (!g) return;
  var main = g.querySelector('[data-ann-main]'), thumbs = [].slice.call(g.querySelectorAll('.ann-thumb'));
  var stage = g.querySelector('[data-gal-stage]'), box = g.querySelector('[data-gal-box]'), big = g.querySelector('[data-gal-big]');
  var srcs = thumbs.map(function (t) { return t.getAttribute('data-ann-photo'); });
  if (!srcs.length && main) srcs = [main.getAttribute('src')];
  var n = srcs.length, i = 0;
  function show(k, quiet) {
    i = (k + n) % n;
    if (main) main.src = srcs[i];
    thumbs.forEach(function (t, j) { t.classList.toggle('is-on', j === i); t.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    [].forEach.call(g.querySelectorAll('[data-gal-count], [data-gal-count2]'), function (c) { c.textContent = (i + 1) + ' / ' + n; });
    if (box && box.open && big) big.src = srcs[i];
    var t = thumbs[i];
    if (t && !quiet) { var bar = t.parentNode; if (bar && bar.scrollTo) bar.scrollTo({ left: t.offsetLeft - (bar.clientWidth - t.offsetWidth) / 2, behavior: 'smooth' }); }
    if (n > 1) { var nx = new Image(); nx.src = srcs[(i + 1) % n]; }   // la photo suivante est déjà chargée quand on clique
  }
  function openBox() {
    if (!box || !big) return;
    big.src = srcs[i]; big.alt = main ? main.alt : '';
    if (box.showModal) box.showModal(); else box.setAttribute('open', '');
  }
  g.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-gal-prev]'); if (b) { show(i - 1); return; }
    b = ev.target.closest('[data-gal-next]'); if (b) { show(i + 1); return; }
    b = ev.target.closest('.ann-thumb'); if (b) { show(+b.getAttribute('data-gal-i')); return; }
    b = ev.target.closest('[data-gal-goto]'); if (b) { show(+b.getAttribute('data-gal-goto'), true); openBox(); return; }
    if (ev.target.closest('[data-gal-close]')) { if (box.close) box.close(); else box.removeAttribute('open'); return; }
    if (ev.target.closest('[data-gal-open]') || ev.target === main) { openBox(); return; }
    if (box && ev.target === box) { if (box.close) box.close(); else box.removeAttribute('open'); }
  });
  g.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowLeft') { show(i - 1); ev.preventDefault(); }
    else if (ev.key === 'ArrowRight') { show(i + 1); ev.preventDefault(); }
    else if (ev.key === 'Enter' && ev.target === stage) { openBox(); ev.preventDefault(); }
  });
  [stage, box].forEach(function (el) {
    if (!el || n < 2) return;
    var x0 = null;
    el.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    el.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 40) show(i + (dx < 0 ? 1 : -1)); }, { passive: true });
  });
  show(0, true);
})();


/* Avis Google par widget tiers : le script n'est chargé qu'après un clic (aucun traceur tiers au chargement de la page). */
(function () {
  var box = document.querySelector('[data-avis-widget]');
  if (!box) return;
  var btn = box.querySelector('[data-avis-load]');
  btn.addEventListener('click', function () {
    var type = box.getAttribute('data-type'), id = box.getAttribute('data-id');
    if (!/^[A-Za-z0-9_-]{6,64}$/.test(id)) return;
    var s = document.createElement('script'), zone = document.createElement('div');
    if (type === 'trustindex') { s.src = 'https://cdn.trustindex.io/loader.js?' + id; zone.className = 'avis-zone'; }
    else if (type === 'elfsight') { s.src = 'https://static.elfsight.com/platform/platform.js'; zone.className = 'elfsight-app-' + id; zone.setAttribute('data-elfsight-app-lazy', ''); }
    else return;
    s.async = true; s.defer = true;
    box.innerHTML = ''; box.classList.add('is-loaded'); box.appendChild(zone); zone.appendChild(s);
  });
})();
