// LOTIER Immobilier — interactions de la page d'accueil.

(function () {
  // ----- Recherche : onglets Acheter / Louer / Estimer -----
  var modes = {
    vente: { label: 'BUDGET MAXIMUM', hint: 'Ex. 250 000 €', action: 'Rechercher', showCity: true },
    location: { label: 'LOYER MAXIMUM', hint: 'Ex. 750 € par mois', action: 'Rechercher', showCity: true },
    estimer: { label: 'ADRESSE DU BIEN', hint: 'Ex. 12 rue Française, Béziers', action: 'Estimer mon bien', showCity: false }
  };

  var tabs = document.querySelectorAll('[data-mode]');
  var cityField = document.getElementById('field-ville');
  var budgetLabel = document.querySelector('label[for="budget"]');
  var budgetInput = document.getElementById('budget');
  var submit = document.getElementById('search-submit');

  function setMode(key) {
    var m = modes[key];
    tabs.forEach(function (t) {
      t.setAttribute('aria-pressed', String(t.getAttribute('data-mode') === key));
    });
    cityField.hidden = !m.showCity;
    budgetLabel.textContent = m.label;
    budgetInput.placeholder = m.hint;
    submit.textContent = m.action;
  }

  tabs.forEach(function (t) {
    t.addEventListener('click', function () { setMode(t.getAttribute('data-mode')); });
  });

  // ----- Sélecteur « Quel est votre projet ? » -----
  var profiles = {
    bailleur: {
      kicker: 'LOCATION',
      title: 'Mettez votre bien en location, l\'esprit tranquille',
      text: 'Nous trouvons le locataire, rédigeons le bail et suivons votre bien au quotidien. À partir de 39,99 € par mois.',
      a1: 'Mettre mon bien en location', h1: 'mailto:gestion@lotier-immobilier.com',
      a2: 'Estimer mon loyer', h2: '#recherche'
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
      a1: 'Estimer mon bien', h1: '#recherche',
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
    profileButtons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-profile') === key));
    });
    panel.kicker.textContent = p.kicker;
    panel.title.textContent = p.title;
    panel.text.textContent = p.text;
    panel.a1.textContent = p.a1;
    panel.a1.setAttribute('href', p.h1);
    panel.a2.textContent = p.a2;
    panel.a2.setAttribute('href', p.h2);
  }

  profileButtons.forEach(function (b) {
    b.addEventListener('click', function () { setProfile(b.getAttribute('data-profile')); });
  });

  setMode('vente');
  setProfile('bailleur');
})();
