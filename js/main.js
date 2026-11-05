// LOTIER Immobilier — interactions de la page d'accueil.

(function () {
  var MAIL = 'contact@lotier-immobilier.com';

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

  // ----- Estimation : prépare un e-mail à l'agence -----
  var est = document.getElementById('estimer');
  if (est && est.tagName === 'FORM') {
    est.addEventListener('submit', function (e) {
      e.preventDefault();
      var adresse = document.getElementById('est-adresse').value.trim();
      var tel = document.getElementById('est-tel').value.trim();
      var body = 'Bonjour,\n\nJe souhaite faire estimer mon bien.\n\nAdresse : ' + adresse + '\nTéléphone : ' + tel + '\n\nMerci de me rappeler.';
      window.location.href = 'mailto:' + MAIL + '?subject=' + encodeURIComponent('Demande d\'estimation') + '&body=' + encodeURIComponent(body);
    });
  }

  // ----- Recherche : onglets Acheter / Louer -----
  var modes = {
    vente: { label: 'Budget maximum', hint: 'Ex. 250 000 €' },
    location: { label: 'Loyer maximum', hint: 'Ex. 750 € par mois' }
  };
  var tabs = document.querySelectorAll('[data-mode]');
  var budgetLabel = document.querySelector('label[for="budget"]');
  var budgetInput = document.getElementById('budget');

  function setMode(key) {
    var m = modes[key];
    tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.getAttribute('data-mode') === key)); });
    budgetLabel.textContent = m.label;
    budgetInput.placeholder = m.hint;
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { setMode(t.getAttribute('data-mode')); }); });
  document.getElementById('search-submit').addEventListener('click', function () {
    var a = document.getElementById('annonces');
    if (a) a.scrollIntoView();
  });

  // ----- Sélecteur « Quel est votre projet ? » -----
  var profiles = {
    bailleur: {
      kicker: 'LOCATION',
      title: 'Mettez votre bien en location, l\'esprit tranquille',
      text: 'Nous trouvons le locataire, rédigeons le bail et suivons votre bien au quotidien. À partir de 39,99 € par mois.',
      a1: 'Mettre mon bien en location', h1: 'mailto:gestion@lotier-immobilier.com',
      a2: 'Estimer mon loyer', h2: '#estimer'
    },
    locataire: {
      kicker: 'LOCATION',
      title: 'Trouvez un logement ou joignez l\'équipe',
      text: 'Consultez nos locations disponibles, ou écrivez à l\'équipe pour toute question sur votre logement.',
      a1: 'Voir les locations', h1: '#annonces',
      a2: 'Écrire à la location', h2: 'mailto:gestion@lotier-immobilier.com'
    },
    vendeur: {
      kicker: 'VENTE',
      title: 'Vendez votre bien au bon prix',
      text: 'Nos agents estiment votre bien, le présentent et vous accompagnent jusqu\'à la signature.',
      a1: 'Estimer mon bien', h1: '#estimer',
      a2: 'Confier ma vente', h2: 'mailto:contact@lotier-immobilier.com'
    },
    acquereur: {
      kicker: 'VENTE',
      title: 'Trouvez le bien qui vous correspond',
      text: 'Appartements, maisons, immeubles de rapport : nos agents vous présentent les biens en vente et vous guident dans votre projet.',
      a1: 'Voir les biens en vente', h1: '#annonces',
      a2: 'Parler à un agent', h2: 'mailto:contact@lotier-immobilier.com'
    },
    copro: {
      kicker: 'SYNDIC',
      title: 'Suivez votre copropriété',
      text: 'Entretien de l\'immeuble, budget, assemblées générales : écrivez à l\'équipe syndic pour toute question sur votre résidence.',
      a1: 'Écrire au syndic', h1: 'mailto:syndic@lotier-immobilier.com',
      a2: 'Espace client', h2: '#contact'
    }
  };
  var profileButtons = document.querySelectorAll('[data-profile]');
  var panel = {
    kicker: document.getElementById('panel-kicker'),
    title: document.getElementById('panel-title'),
    text: document.getElementById('panel-text'),
    a1: document.getElementById('panel-a1'),
    a2: document.getElementById('panel-a2')
  };
  function setProfile(key) {
    var p = profiles[key];
    profileButtons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-profile') === key)); });
    panel.kicker.textContent = p.kicker;
    panel.title.textContent = p.title;
    panel.text.textContent = p.text;
    panel.a1.textContent = p.a1; panel.a1.setAttribute('href', p.h1);
    panel.a2.textContent = p.a2; panel.a2.setAttribute('href', p.h2);
  }
  profileButtons.forEach(function (b) { b.addEventListener('click', function () { setProfile(b.getAttribute('data-profile')); }); });

  // ----- Carrousel d'annonces -----
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.track');
    var prev = car.querySelector('[data-dir="-1"]');
    var next = car.querySelector('[data-dir="1"]');
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

  setMode('vente');
  setProfile('bailleur');
})();
