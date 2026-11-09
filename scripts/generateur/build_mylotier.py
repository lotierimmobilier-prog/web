# -*- coding: utf-8 -*-
import os
from common import *
prefix = "../"
SPIRIT_ACTION = "https://extranet2.ics.fr/login_externe.php"
SPIRIT_FORGOT = "https://extranet2.ics.fr/V5/connexion-lotier-mdp-1.html"
body = f'''    <section class="page-hero">
      <span class="orb o1" aria-hidden="true"></span><span class="orb o2" aria-hidden="true"></span>
      <div class="container">
        <nav class="breadcrumb" aria-label="Fil d'Ariane"><a href="{prefix}index.html">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">MyLotier</span></nav>
        <img class="my-logo" src="{prefix}assets/mylotier-logo.svg" alt="MyLotier, espace client" width="330" height="96">
        <h1 class="display page-title">Votre espace client <em class="gold-text">MyLotier.</em></h1>
        <p class="lead">Notre nouvelle plateforme arrive bientôt. En attendant, connectez-vous à SPIRIT pour accéder à votre espace de gestion ou de syndic.</p>
      </div>
    </section>

    <section class="section container my-grid" aria-label="Connexion et nouvelle plateforme">
      <article class="glass my-card my-login" data-r>
        <h2 class="heading">Connexion à SPIRIT</h2>
        <p class="muted">Accès gestion et syndic. Vous avez reçu vos identifiants de l'agence.</p>
        <form class="my-form" action="{SPIRIT_ACTION}" method="post" target="_blank" rel="noopener">
          <input type="hidden" name="groupe" value="lotier">
          <div class="field"><label for="my-login">Identifiant</label><input id="my-login" name="login" type="text" autocomplete="username" autocapitalize="none" spellcheck="false" required></div>
          <div class="field"><label for="my-mdp">Mot de passe</label><input id="my-mdp" name="mdp" type="password" autocomplete="current-password" required></div>
          <button class="btn btn-gold btn-lg" type="submit">Se connecter</button>
        </form>
        <p class="small"><a href="{SPIRIT_FORGOT}" target="_blank" rel="noopener">Mot de passe oublié ?</a></p>
        <p class="small muted">Première connexion ? Cliquez sur « Mot de passe oublié » pour activer votre compte.</p>
        <p class="small muted">Vos identifiants sont envoyés directement à SPIRIT (ICS) : ils ne passent pas par ce site. La connexion s'ouvre dans un nouvel onglet.</p>
      </article>
      <article class="glass my-card my-soon" data-r>
        <span class="soon-badge">Bientôt disponible</span>
        <h2 class="heading">La nouvelle plateforme MyLotier</h2>
        <p class="muted">Nous préparons une nouvelle plateforme pour retrouver vos documents, les actualités de votre copropriété ou de votre bien et la gestion de votre compte, au même endroit.</p>
        <p class="muted">Jusqu'à son ouverture, SPIRIT reste votre accès habituel.</p>
        <h3 class="heading help">Besoin d'aide ?</h3>
        <p class="muted">Un conseiller vous répond au <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> ou à <a href="mailto:contact@lotier-immobilier.com">contact@lotier-immobilier.com</a>.</p>
      </article>
    </section>
'''
ld = [{"@context": "https://schema.org", "@type": "WebPage", "@id": SITE + "/mylotier/", "name": "MyLotier, espace client", "url": SITE + "/mylotier/", "inLanguage": "fr-FR", "isPartOf": {"@id": SITE + "/#website"}},
      breadcrumb_ld([("Accueil", SITE + "/"), ("MyLotier", SITE + "/mylotier/")])]
os.makedirs(f"{ROOT}/mylotier", exist_ok=True)
open(f"{ROOT}/mylotier/index.html", "w", encoding="utf-8").write(
    shell(prefix, "MyLotier, espace client | LOTIER Immobilier", "MyLotier, l'espace client de LOTIER Immobilier : connexion à SPIRIT (gestion et syndic) et nouvelle plateforme bientôt disponible.", "mylotier/", body, ld, "assets/og-lotier.jpg", robots="noindex, follow"))
print("mylotier généré")
