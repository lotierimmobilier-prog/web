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
      });
    });
    var pm = q('[data-partager-merci]');
    if (pm) pm.addEventListener('click', function () {
      var m = q('#merci');
      ouvrirPartage(m.dataset.prenom, m.dataset.prenom + ' participe au concours de Noël de LOTIER Immobilier ! Son dessin de la maison du Père Noël sera en ligne sous 12 heures. Les votes ouvrent le 15 décembre, un vote par jour :', m.dataset.url);
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
  tous('[data-fermer]').forEach(function (b) { b.addEventListener('click', function () { b.closest('dialog').close(); }); });
  tous('dialog').forEach(function (g) { g.addEventListener('click', function (e) { if (e.target === g) g.close(); }); });

  /* Arrivée par un lien partagé : on amène le visiteur au dessin. */
  var vedette = q('.vedette');
  if (vedette && !location.hash) vedette.scrollIntoView({ block: 'start' });
})();
