# -*- coding: utf-8 -*-
# Les 20 articles du blog LOTIER Immobilier.
# Contenu rédigé à titre de repères généraux : relu et validé par l'agence avant publication.
# Un bloc de type liste = élément à puces ; un bloc de type texte = paragraphe.

ARTICLES = [
 dict(slug="diagnostics-immobiliers-obligatoires-vente", cat="Vendre", photo="immeuble",
  alt="Photo d'illustration : immeuble moderne avec balcons", cta="estimation",
  title="Les diagnostics immobiliers obligatoires pour vendre",
  desc="DPE, amiante, plomb, électricité, risques : la liste des diagnostics à fournir quand on vend un bien, leur durée de validité et le bon moment pour les commander.",
  intro="Avant de signer une promesse de vente, le vendeur doit remettre à l'acheteur un dossier de diagnostics techniques. Son contenu dépend de l'âge du bien, de sa nature et de sa localisation. Voici les principaux diagnostics et comment s'y préparer.",
  sections=[
   ("Les diagnostics les plus courants", ["Tous les biens ne sont pas concernés par chaque diagnostic. Selon votre situation, le dossier peut comprendre :", [
     "le diagnostic de performance énergétique (DPE), qui classe le logement de A à G ;",
     "le diagnostic amiante, pour les bâtiments dont le permis de construire a été délivré avant juillet 1997 ;",
     "le constat de risque d'exposition au plomb, pour les logements construits avant 1949 ;",
     "les diagnostics électricité et gaz, lorsque l'installation a plus de quinze ans ;",
     "le diagnostic termites, dans les zones définies par arrêté préfectoral ;",
     "l'état des risques (naturels, miniers, technologiques) de la commune ;",
     "le diagnostic de l'assainissement non collectif, si le bien n'est pas raccordé au tout-à-l'égout ;",
     "le mesurage de la surface privative (loi Carrez) pour un lot de copropriété."]]),
   ("Qui les réalise et pendant combien de temps ils sont valables", ["Les diagnostics sont réalisés par un professionnel certifié, indépendant du vendeur et de l'agence. La durée de validité varie : trois ans pour l'électricité et le gaz lors d'une vente, dix ans pour le DPE, et parfois sans limite lorsque le résultat est négatif, comme pour certains diagnostics amiante ou plomb. Un diagnostic valide peut être réutilisé : gardez-les dans un même dossier."]),
   ("Pourquoi les commander avant la mise en vente", ["Commander les diagnostics dès le départ évite un blocage de dernière minute au moment du compromis. Ils rassurent aussi les acheteurs, qui peuvent chiffrer d'éventuels travaux. Le DPE en particulier pèse de plus en plus sur le prix et sur la visibilité d'une annonce."])],
  retenir=["Le contenu du dossier dépend de l'âge, de la nature et de la localisation du bien.", "Chaque diagnostic a sa propre durée de validité : vérifiez les dates.", "Les commander avant la mise en vente fait gagner du temps."]),

 dict(slug="home-staging-mieux-vendre", cat="Vendre", photo="salon2",
  alt="Photo d'illustration : séjour lumineux et dépouillé", cta="estimation",
  title="Home staging : 8 gestes simples pour mieux vendre",
  desc="Désencombrer, dépersonnaliser, réparer, éclairer : huit gestes peu coûteux pour valoriser votre bien avant les photos et les premières visites.",
  intro="Un acheteur décide en quelques secondes, souvent dès la photo de l'annonce. Le home staging consiste à préparer un bien pour qu'on s'y projette facilement. Pas besoin de gros travaux : quelques gestes suffisent.",
  sections=[
   ("Préparer le terrain", [["Désencombrer : retirez ce qui n'est pas indispensable, surtout dans les entrées, les cuisines et les placards ;", "Dépersonnaliser : photos de famille et collections laissent la place à une ambiance neutre ;", "Nettoyer à fond : vitres, joints, sols, et traitez les odeurs (cuisine, animaux, tabac) ;", "Réparer les petits défauts : poignées, robinets qui fuient, trous aux murs, ampoules grillées."]]),
   ("Mettre en valeur", [["Maximiser la lumière : ouvrez les rideaux, nettoyez les fenêtres, ajoutez des sources lumineuses chaudes ;", "Rafraîchir si besoin : une peinture claire et neutre transforme une pièce pour un coût limité ;", "Soigner les extérieurs : balcon, terrasse ou jardin rangés et fleuris donnent envie ;", "Mettre en scène : un canapé dégagé, une table dressée, un lit fait de façon simple."]]),
   ("Les photos et les visites", ["Les photos sont la vitrine du bien : faites-les en plein jour, une fois le home staging terminé. Pour les visites, aérez, allumez les lumières et laissez les visiteurs circuler librement. Un conseiller peut vous indiquer, pièce par pièce, ce qui vaut la peine d'être fait avant de commencer."])],
  retenir=["Désencombrer et nettoyer valent mieux qu'une rénovation coûteuse.", "Une ambiance neutre et lumineuse aide à se projeter.", "Les photos se font une fois le bien préparé."]),

 dict(slug="mandat-exclusif-ou-simple", seo_title="Mandat exclusif ou simple : que choisir pour vendre ?", cat="Vendre", photo="cles",
  alt="Photo d'illustration : remise de clés d'un logement", cta="contact",
  title="Mandat exclusif ou mandat simple : que choisir pour vendre ?",
  desc="Différences entre mandat simple et mandat exclusif, durée, honoraires, engagement : les points à comparer avant de confier la vente de votre bien.",
  intro="Pour faire appel à une agence, il faut signer un mandat. Il en existe deux grandes formes : le mandat simple et le mandat exclusif. Le bon choix dépend de votre bien, de votre calendrier et du niveau d'accompagnement attendu.",
  sections=[
   ("Le mandat simple", ["Avec un mandat simple, vous pouvez confier votre bien à plusieurs agences et le vendre vous-même. Vous gardez de la liberté, mais l'effort commercial est souvent plus dispersé : chaque agence sait qu'elle n'est pas seule à travailler le dossier. Le bien peut aussi apparaître plusieurs fois sur les portails, parfois avec des prix différents."]),
   ("Le mandat exclusif", ["Avec un mandat exclusif, une seule agence commercialise le bien pendant la durée prévue. En contrepartie de cet engagement, elle investit généralement davantage : photos soignées, communication ciblée, visites organisées, suivi régulier. Vous avez un seul interlocuteur et une vision claire de l'avancement."]),
   ("Ce qu'il faut vérifier avant de signer", [["la durée du mandat et les conditions pour y mettre fin ;", "le montant des honoraires et la personne qui les paie ;", "le prix de vente affiché et la marge de négociation éventuelle ;", "les actions de commercialisation prévues et la fréquence des comptes rendus."], "Le mandat est un contrat écrit et encadré par la loi : prenez le temps de le relire et posez toutes vos questions avant de signer."])],
  retenir=["Mandat simple : liberté, mais une mobilisation souvent moins forte.", "Mandat exclusif : un interlocuteur unique et un suivi plus poussé.", "Relisez la durée, les honoraires et les conditions de fin du mandat."]),

 dict(slug="fixer-le-bon-prix-estimation", seo_title="Fixer le bon prix : l'estimation sérieuse change tout", cat="Vendre", photo="villa",
  alt="Photo d'illustration : villa contemporaine avec piscine", cta="estimation",
  title="Fixer le bon prix : pourquoi une estimation sérieuse change tout",
  desc="Comment un conseiller estime la valeur d'un bien, les erreurs à éviter quand on fixe son prix, et pourquoi un prix trop élevé ralentit la vente.",
  intro="Le prix est le premier critère de réussite d'une vente. Trop bas, vous laissez de l'argent sur la table. Trop haut, le bien reste affiché, perd en attractivité et finit souvent par se vendre moins bien. Une estimation sérieuse s'appuie sur des faits.",
  sections=[
   ("Comment un conseiller estime un bien", ["L'estimation repose d'abord sur la comparaison avec des biens similaires vendus récemment dans le même secteur. Le conseiller tient ensuite compte des caractéristiques propres au bien :", ["la surface, l'étage, l'exposition et la luminosité ;", "l'état général, les travaux faits ou à prévoir ;", "les extérieurs : balcon, terrasse, jardin, stationnement ;", "les charges, la taxe foncière et le diagnostic énergétique ;", "l'environnement : commerces, transports, écoles, nuisances."]]),
   ("Les erreurs fréquentes", ["La première est de se baser sur le prix d'achat ou sur les annonces en cours : un prix affiché n'est pas un prix de vente. La deuxième est de surestimer l'impact de travaux personnels ou de la valeur sentimentale du bien. La troisième est de fixer un prix élevé « pour pouvoir négocier » : les acheteurs comparent, et un bien trop cher est souvent écarté sans visite."]),
   ("La visite fait la différence", ["Un avis de valeur par téléphone donne une fourchette. La visite permet d'affiner : état réel, qualité de l'entretien, atouts qui ne se voient pas sur plan. Un bon prix de départ attire plus de visites au début de la commercialisation, là où l'intérêt est le plus fort."])],
  retenir=["Une estimation sérieuse s'appuie sur des ventes réelles et récentes.", "Un prix trop élevé ralentit la vente et affaiblit la position du vendeur.", "La visite par un conseiller affine la fourchette de prix."]),

 dict(slug="compromis-de-vente-points-de-vigilance", seo_title="Compromis de vente : que vérifier avant de signer ?", cat="Acheter", photo="agent",
  alt="Photo d'illustration : un conseiller remet les clés à un couple", cta="contact",
  title="Compromis de vente : ce qu'il faut vérifier avant de signer",
  desc="Conditions suspensives, dépôt de garantie, délai de rétractation, calendrier jusqu'à l'acte : les points clés à contrôler avant de signer un compromis de vente.",
  intro="Le compromis de vente, ou promesse de vente, engage vendeur et acheteur. C'est le moment où tout se joue : une fois signé, les conditions sont fixées. Prenez le temps de le lire et de poser vos questions.",
  sections=[
   ("Les éléments à contrôler", [["l'identité des parties, la description précise du bien et des annexes (lots, parkings, caves) ;", "le prix, la répartition éventuelle entre le bien et le mobilier, et les honoraires ;", "les diagnostics et, pour une copropriété, le règlement, les procès-verbaux d'assemblée et les charges ;", "la date limite de signature de l'acte authentique."]]),
   ("Les conditions suspensives", ["Ce sont des événements dont dépend la vente. La plus courante est l'obtention du prêt : si la banque refuse dans le délai prévu, l'acheteur peut renoncer sans perdre son dépôt. D'autres existent selon les cas, comme l'obtention d'un permis ou l'absence de servitude non déclarée. Vérifiez leur durée et leurs modalités."]),
   ("Dépôt de garantie, rétractation et calendrier", ["Un dépôt de garantie, souvent de l'ordre de 5 à 10 % du prix, est généralement versé au moment de la signature. L'acquéreur d'un logement dispose ensuite d'un délai de rétractation de dix jours, qui court à compter du lendemain de la réception du compromis. Entre le compromis et l'acte authentique chez le notaire, il faut compter en général deux à trois mois."])],
  retenir=["Lisez le compromis en entier et faites préciser chaque point flou.", "La condition suspensive de prêt protège l'acheteur : surveillez les délais.", "Le délai de rétractation de dix jours ne se renégocie pas."]),

 dict(slug="frais-de-notaire-comprendre", cat="Acheter", photo="cles",
  alt="Photo d'illustration : remise de clés d'un logement", cta="contact",
  title="Frais de notaire : à quoi correspondent-ils vraiment ?",
  desc="Droits de mutation, émoluments, débours : de quoi sont composés les frais de notaire, pourquoi ils sont plus élevés dans l'ancien et comment les budgéter.",
  intro="Les « frais de notaire » ne vont pas tous au notaire. Ils se composent surtout de taxes reversées à l'État et aux collectivités. Bien les connaître permet de calculer un budget d'achat réaliste.",
  sections=[
   ("De quoi se composent-ils ?", [["les droits et taxes (droits de mutation), qui représentent la plus grande part et sont reversés à l'État et aux collectivités ;", "les émoluments du notaire, dont le tarif est réglementé ;", "les débours, c'est-à-dire les frais avancés pour obtenir des documents (cadastre, état civil, urbanisme)."]]),
   ("Ancien ou neuf : un écart important", ["Dans l'ancien, ces frais sont de l'ordre de 7 à 8 % du prix. Dans le neuf, ils sont nettement plus faibles, de l'ordre de 2 à 3 %, car les droits de mutation sont réduits. Pour un bien à 200 000 €, l'écart peut donc dépasser 10 000 €. Le montant exact dépend du prix, de la nature du bien et du département : demandez un calcul précis au notaire."]),
   ("Les intégrer dans votre budget", ["Ces frais ne peuvent généralement pas être inclus dans le prêt immobilier : ils sont à régler avec l'apport personnel. Lorsque vous fixez votre budget, additionnez le prix, les frais de notaire, les éventuels travaux, les frais de déménagement et les frais de dossier de la banque. Un conseiller ou un courtier vous aide à établir ce plan de financement."])],
  retenir=["Les frais de notaire sont surtout des taxes, pas la rémunération du notaire.", "Ils sont plus élevés dans l'ancien que dans le neuf.", "À prévoir sur votre apport, en plus du prix d'achat."]),

 dict(slug="premier-achat-erreurs-a-eviter", cat="Acheter", photo="village",
  alt="Photo d'illustration : village de pierre aux toits de tuiles", cta="contact",
  title="Premier achat immobilier : 6 erreurs à éviter",
  desc="Budget sans marge, charges oubliées, travaux sous-estimés, copropriété non vérifiée : les six erreurs les plus fréquentes lors d'un premier achat.",
  intro="Acheter son premier logement est une étape importante, et chaque erreur coûte cher. Voici les six pièges les plus fréquents, et comment les éviter.",
  sections=[
   ("1. Fixer un budget sans marge", ["Le prix du bien n'est qu'une partie de la dépense. Ajoutez les frais de notaire, les frais de dossier, l'assurance, le déménagement et un petit fonds pour les imprévus. Gardez une marge dans vos mensualités plutôt que de viser le maximum accordé par la banque."]),
   ("2. Oublier les charges et la taxe foncière", ["Charges de copropriété, taxe foncière, assurance, chauffage : ces coûts réguliers pèsent sur le budget mensuel. Demandez les montants au vendeur avant de faire une offre."]),
   ("3. Sous-estimer les travaux", ["Un logement à rafraîchir se chiffre avec des devis, pas à l'œil. Pensez aussi au diagnostic énergétique : un mauvais classement implique souvent des travaux d'isolation ou de chauffage."]),
   ("4. Ne pas vérifier la copropriété", ["Demandez les derniers procès-verbaux d'assemblée générale, le règlement et l'état des charges. Ils révèlent les travaux votés, les litiges éventuels et la santé financière de l'immeuble."]),
   ("5. Se décider trop vite, ou trop tard", ["Visitez plusieurs biens pour comparer, mais soyez prêt à agir quand un bien correspond : financement validé, pièces rassemblées, critères clairs."]),
   ("6. Négliger l'environnement", ["Visitez à différentes heures : bruit, stationnement, commerces, transports. Un logement parfait dans un quartier qui ne vous convient pas reste un mauvais achat."])],
  retenir=["Prévoyez une marge dans votre budget et dans vos mensualités.", "Vérifiez les charges, les travaux et la copropriété avant toute offre.", "Visitez à plusieurs moments de la journée."]),

 dict(slug="visiter-un-appartement-checklist", cat="Acheter", photo="immeuble",
  alt="Photo d'illustration : façade d'immeuble avec balcons", cta="contact",
  title="Visiter un appartement : la check-list de l'acheteur",
  desc="Ce qu'il faut observer et demander pendant une visite : état général, humidité, bruit, parties communes, charges. Une check-list simple à imprimer.",
  intro="Une visite dure souvent moins d'une demi-heure, et elle compte pour un achat qui engage des années. Voici une check-list pour ne rien oublier.",
  sections=[
   ("Dans l'appartement", [["Humidité : traces au plafond, murs qui cloquent, odeurs de renfermé ;", "Fenêtres : état des menuiseries, double vitrage, bruit extérieur une fois fermées ;", "Électricité et plomberie : tableau électrique, prises, pression de l'eau, état des canalisations ;", "Chauffage : type, âge de l'installation, mode de production d'eau chaude ;", "Luminosité et exposition : repassez à une autre heure si possible."]]),
   ("Dans l'immeuble", [["Entrée, escalier, ascenseur : l'entretien des parties communes en dit long sur la gestion ;", "Toiture, façade, caves : signes de vieillissement ou de travaux à venir ;", "Stationnement, local à vélos, accès : pensez à votre quotidien."]]),
   ("Les questions à poser", [["Quel est le montant des charges et de la taxe foncière ?", "Des travaux ont-ils été votés en assemblée générale ?", "Depuis combien de temps le bien est-il à vendre, et pourquoi le vend-on ?", "Quels sont les diagnostics, notamment le classement énergétique ?"], "Prenez des photos si le vendeur l'accepte, notez vos impressions à chaud et comparez avec vos autres visites. N'hésitez pas à revenir une seconde fois."])],
  retenir=["Observez l'humidité, les fenêtres, l'électricité et le chauffage.", "L'état des parties communes reflète la gestion de la copropriété.", "Posez les questions sur les charges, les travaux et le DPE."]),

 dict(slug="meuble-ou-vide-choisir-location", cat="Bailleur", photo="salon2",
  alt="Photo d'illustration : séjour moderne prêt à louer", cta="location",
  title="Louer son bien : meublé ou vide ?",
  desc="Durée du bail, dépôt de garantie, fiscalité, mobilier obligatoire : comparer la location meublée et la location vide pour choisir selon votre projet.",
  intro="Meublé ou vide ? Le choix change la durée du bail, le public visé, le dépôt de garantie et la fiscalité. Il n'y a pas de bonne réponse unique : tout dépend de votre bien et de vos objectifs.",
  sections=[
   ("Les différences principales", [["Durée du bail : en général trois ans pour une location vide, un an pour une location meublée (neuf mois pour un étudiant) ;", "Dépôt de garantie : un mois de loyer hors charges pour du vide, deux mois pour du meublé ;", "Préavis du locataire : trois mois pour du vide, un mois pour du meublé, avec des exceptions possibles pour du vide ;", "Équipement : un logement meublé doit comprendre un mobilier minimum fixé par décret (literie, plaques de cuisson, réfrigérateur, etc.)."]]),
   ("Qui loue quoi ?", ["Le meublé attire des locataires de passage : étudiants, jeunes actifs, mutations professionnelles. Il offre plus de rotation, donc plus d'occasions d'ajuster le loyer, mais aussi plus de remises en état. Le vide convient mieux à des locataires qui s'installent durablement : familles, couples, personnes qui apportent leurs meubles."]),
   ("Fiscalité et rentabilité", ["Les deux formes ne sont pas imposées de la même façon, et le meublé peut permettre un loyer plus élevé. Mais l'investissement de départ (mobilier) et les frais de remplacement existent. Parlez-en à un expert-comptable avant de choisir, car la meilleure formule dépend de votre situation fiscale."])],
  retenir=["Meublé : bail plus court, dépôt plus élevé, mobilier obligatoire.", "Vide : bail plus long, stabilité pour le propriétaire.", "Consultez un expert-comptable pour la fiscalité."]),

 dict(slug="depot-de-garantie-location", cat="Locataire", photo="cles",
  alt="Photo d'illustration : remise de clés d'un logement", cta="location",
  title="Dépôt de garantie : montant, restitution, retenues",
  desc="Montant maximum, délai de restitution et retenues autorisées : tout ce que locataires et propriétaires doivent savoir sur le dépôt de garantie d'une location.",
  intro="Le dépôt de garantie est versé par le locataire à l'entrée dans les lieux. Il sert à couvrir d'éventuels impayés ou dégradations. Le sujet est une source fréquente de désaccords : mieux vaut en connaître les règles.",
  sections=[
   ("Le montant", ["Pour une location vide, le dépôt de garantie ne peut pas dépasser un mois de loyer hors charges. Pour une location meublée, il peut atteindre deux mois de loyer hors charges. Il n'est pas révisé pendant la durée du bail."]),
   ("La restitution", ["Le bailleur doit restituer le dépôt dans un délai d'un mois à compter de la remise des clés si l'état des lieux de sortie est conforme à celui d'entrée, et de deux mois dans le cas contraire. En cas de retard, la loi prévoit une majoration à la charge du bailleur."]),
   ("Les retenues autorisées", ["Le propriétaire peut retenir des sommes justifiées :", ["loyers ou charges impayés ;", "réparations liées à des dégradations qui dépassent l'usure normale ;", "régularisation de charges, selon les cas."], "Il doit fournir des justificatifs (devis, factures). L'usure normale liée à l'ancienneté, comme une peinture qui se patine, ne peut pas être facturée. Un bon état des lieux d'entrée et de sortie, avec des photos, évite la plupart des litiges."])],
  retenir=["Un mois de loyer pour du vide, deux pour du meublé.", "Restitution dans un délai d'un mois ou de deux mois selon l'état des lieux.", "Les retenues doivent être justifiées et ne couvrent pas l'usure normale."]),

 dict(slug="loyers-impayes-reflexes-proprietaire", cat="Bailleur", photo="syndic",
  alt="Photo d'illustration : façade d'immeuble en noir et blanc", cta="location",
  title="Loyers impayés : les bons réflexes du propriétaire",
  desc="Agir tôt, relancer, formaliser, activer la caution ou l'assurance : la marche à suivre quand un locataire ne paie plus son loyer.",
  intro="Un loyer impayé n'est jamais agréable, mais il se traite mieux quand on agit vite et avec méthode. Voici les premiers réflexes, et pourquoi il vaut mieux s'y préparer avant même de louer.",
  sections=[
   ("Agir dès le premier retard", [["contactez le locataire par téléphone puis par écrit : un oubli, un souci bancaire ou une difficulté passagère se règlent souvent à l'amiable ;", "proposez, si la situation le justifie, un échéancier par écrit et signé ;", "conservez toutes les traces : relevés, messages, courriers."]]),
   ("Formaliser la démarche", ["Si le retard persiste, envoyez une lettre de mise en demeure en recommandé. Contactez rapidement la caution si le bail en prévoit une, et votre assureur si vous avez souscrit une garantie contre les loyers impayés. Les délais de déclaration sont courts : vérifiez votre contrat."]),
   ("Si la situation ne se règle pas", ["La procédure pour récupérer les sommes ou le logement est encadrée : commandement de payer délivré par un commissaire de justice, puis recours devant le juge. Elle est longue et protectrice pour le locataire, notamment avec la trêve hivernale qui suspend les expulsions chaque hiver. Mieux vaut être accompagné par un professionnel."]),
   ("Prévenir plutôt que guérir", ["Vérifiez le dossier du locataire avec soin, demandez un garant et envisagez une assurance loyers impayés. Une agence sélectionne les candidats, rédige le bail et assure le suivi : c'est aussi une manière de réduire le risque."])],
  retenir=["Réagissez au premier retard, par téléphone puis par écrit.", "Prévenez la caution et l'assurance dans les délais prévus.", "Un dossier solide au départ réduit le risque d'impayé."]),

 dict(slug="dpe-classes-a-g-comprendre", cat="Bailleur", photo="immeuble",
  alt="Photo d'illustration : immeuble moderne", cta="estimation",
  title="DPE : comprendre les classes A à G",
  desc="Ce que mesure le diagnostic de performance énergétique, sa durée de validité, son impact sur la vente et la location, et comment améliorer la classe d'un logement.",
  intro="Le diagnostic de performance énergétique (DPE) note un logement de A (très économe) à G (très énergivore). Il est obligatoire pour vendre ou louer, et son poids dans les décisions ne cesse de grandir.",
  sections=[
   ("Ce que mesure le DPE", ["Il évalue la consommation d'énergie du logement et ses émissions de gaz à effet de serre, à partir de l'isolation, du mode de chauffage, de la ventilation et de la production d'eau chaude. Il est réalisé par un diagnostiqueur certifié et reste valable dix ans, sauf évolution de la réglementation."]),
   ("L'impact sur la vente et la location", ["Pour la location, la loi interdit progressivement la mise en location des logements les plus énergivores, selon un calendrier fixé par les textes. Pour la vente, un audit énergétique peut être exigé pour certains logements très énergivores, et la classe influe sur le prix et l'attractivité. Les règles évoluent régulièrement : faites vérifier votre situation par un conseiller avant toute décision."]),
   ("Améliorer la classe d'un logement", ["Les leviers les plus efficaces sont souvent :", ["l'isolation des combles, des murs et des planchers ;", "le remplacement des fenêtres et la ventilation ;", "le changement du système de chauffage ;", "un meilleur pilotage (thermostat, programmation)."], "Des aides publiques existent pour financer une partie des travaux. Leurs conditions changent : renseignez-vous auprès d'un conseiller ou d'un service spécialisé avant de commencer."])],
  retenir=["Le DPE classe un logement de A à G et reste valable dix ans.", "La classe énergétique pèse sur la vente et conditionne la location.", "Isolation, ventilation et chauffage sont les leviers principaux."]),

 dict(slug="dossier-de-location-solide", cat="Locataire", photo="salon2",
  alt="Photo d'illustration : séjour lumineux", cta="location",
  title="Constituer un dossier de location solide",
  desc="Pièces à fournir, garants, documents interdits, présentation : comment composer un dossier de location qui rassure le propriétaire et accélère la réponse.",
  intro="Dans les zones où la demande est forte, les dossiers de location sont examinés vite. Un dossier complet et soigné fait gagner du temps et inspire confiance.",
  sections=[
   ("Les pièces habituelles", [["pièce d'identité ;", "justificatif de domicile actuel ;", "justificatifs de revenus : derniers bulletins de salaire, contrat de travail, dernier avis d'imposition ;", "garant : ses pièces d'identité, justificatifs de revenus et de domicile, et acte de cautionnement."]]),
   ("Ce qu'un bailleur ne peut pas demander", ["La liste des documents exigibles est fixée par décret, et certaines pièces ne peuvent pas être réclamées, comme un relevé de compte bancaire, une photo d'identité ou un certificat médical. Si un document ne figure pas sur la liste, vous pouvez refuser de le fournir."]),
   ("Soigner la présentation", ["Beaucoup de propriétaires regardent le rapport entre le loyer et les revenus, souvent autour d'un revenu égal à trois fois le loyer. Ce n'est pas une règle légale, mais un usage courant. Regroupez les pièces dans un seul fichier clair, lisible, nommé de façon cohérente. Un dossier numérique est pratique : il peut s'envoyer en quelques secondes dès que vous trouvez le bon logement.", "Enfin, soyez réactif : répondez vite, visitez, et déposez votre dossier dès que le logement vous correspond."])],
  retenir=["Préparez un dossier complet, lisible et prêt à envoyer.", "La liste des pièces exigibles est limitée par décret.", "La réactivité compte autant que la qualité du dossier."]),

 dict(slug="assemblee-generale-copropriete-preparer", cat="Syndic", photo="syndic",
  alt="Photo d'illustration : immeuble en copropriété", cta="syndic",
  title="Assemblée générale de copropriété : bien se préparer",
  desc="Convocation, ordre du jour, pouvoirs, votes, procès-verbal : le déroulement d'une assemblée générale et les bons réflexes pour y participer.",
  intro="L'assemblée générale est le moment où les copropriétaires décident de la vie de l'immeuble : budget, travaux, contrats. Y participer, c'est peser sur des décisions qui touchent directement vos charges et votre cadre de vie.",
  sections=[
   ("La convocation", ["La convocation est envoyée par le syndic, en général au moins vingt-et-un jours avant la date de l'assemblée. Elle comprend l'ordre du jour et les documents nécessaires pour voter : comptes de l'exercice, budget prévisionnel, devis éventuels. Lisez-les à l'avance : c'est ce qui permet de voter en connaissance de cause."]),
   ("Y participer, ou donner pouvoir", ["Vous pouvez assister à l'assemblée, ou vous faire représenter par un mandataire grâce à un pouvoir. Les votes prennent en compte les tantièmes de chaque lot. Selon la nature de la décision, une majorité simple ou renforcée est nécessaire. Le syndic ou le conseil syndical peuvent vous expliquer ces règles avant la réunion."]),
   ("Après l'assemblée", ["Le procès-verbal retrace les décisions prises. Il est notifié aux copropriétaires, et un copropriétaire opposant ou absent peut contester une décision dans un délai de deux mois à compter de cette notification. Conservez le procès-verbal : il sera utile en cas de vente, car l'acheteur vous le demandera."])],
  retenir=["Lisez la convocation et les documents joints avant l'assemblée.", "Pas disponible ? Donnez un pouvoir pour ne pas perdre votre voix.", "Gardez les procès-verbaux : ils servent lors d'une vente."]),

 dict(slug="charges-copropriete-appel-de-fonds", cat="Syndic", photo="syndic",
  alt="Photo d'illustration : façade d'immeuble", cta="syndic",
  title="Charges de copropriété : lire un appel de fonds",
  desc="Provisions, charges courantes, travaux, fonds de travaux, régularisation : comprendre un appel de fonds de copropriété ligne par ligne.",
  intro="Chaque trimestre, le syndic envoie un appel de fonds. Derrière un montant unique se cachent plusieurs postes. Les comprendre aide à anticiper son budget et à poser les bonnes questions.",
  sections=[
   ("Les provisions du budget", ["Le budget prévisionnel est voté en assemblée générale. Les copropriétaires versent des provisions, en général chaque trimestre, pour couvrir les dépenses courantes : entretien, ascenseur, assurance, eau commune, chauffage collectif, honoraires du syndic."]),
   ("Charges courantes et travaux", ["Les charges courantes reviennent chaque année. Les travaux exceptionnels (ravalement, toiture, ascenseur) font l'objet d'un vote spécifique et d'appels de fonds dédiés. La répartition se fait selon les tantièmes et les clés de répartition prévues au règlement de copropriété."]),
   ("Le fonds de travaux", ["Une cotisation annuelle alimente un fonds de travaux, destiné à financer les gros travaux futurs. Elle est obligatoire dans la plupart des copropriétés, et représente au moins 5 % du budget prévisionnel. Ces sommes restent liées au lot : elles ne sont pas restituées au vendeur lors d'une vente."]),
   ("La régularisation annuelle", ["Une fois les comptes approuvés par l'assemblée, le syndic compare les provisions versées et les dépenses réelles. Selon le résultat, vous recevez un complément à payer ou un avoir. En cas de doute, demandez le détail au syndic ou au conseil syndical : vous avez le droit de consulter les pièces justificatives."])],
  retenir=["Un appel de fonds regroupe provisions, travaux et fonds de travaux.", "La répartition dépend des tantièmes et du règlement de copropriété.", "En cas de doute, demandez le détail au syndic."]),

 dict(slug="travaux-en-copropriete-qui-decide", cat="Syndic", photo="immeuble",
  alt="Photo d'illustration : immeuble moderne avec balcons", cta="syndic",
  title="Travaux en copropriété : qui décide, qui paie ?",
  desc="Parties communes et privatives, vote en assemblée, travaux urgents, financement, plan pluriannuel : comment se décident et se financent les travaux d'un immeuble.",
  intro="Ravalement, toiture, ascenseur, isolation : les travaux en copropriété sont souvent coûteux et se décident ensemble. Qui vote, comment s'organise le chantier, et comment se répartit la facture ?",
  sections=[
   ("Parties communes et parties privatives", ["Les parties communes (façade, toiture, escaliers, canalisations générales) sont gérées collectivement. Les parties privatives (l'intérieur de votre logement) relèvent de vous. Certains travaux privatifs qui touchent aux parties communes, comme une fenêtre en façade, demandent aussi l'accord de l'assemblée."]),
   ("Comment une décision est prise", [["le syndic ou le conseil syndical identifie le besoin et demande des devis ;", "les devis sont présentés en assemblée générale, avec un ordre du jour précis ;", "le vote se fait avec une majorité qui dépend du type de travaux ;", "une fois la décision prise, le syndic organise le chantier et suit les entreprises."], "Les travaux urgents nécessaires à la sauvegarde de l'immeuble peuvent être engagés par le syndic sans attendre l'assemblée."]),
   ("Qui paie, et comment ?", ["La facture est répartie selon les tantièmes. Elle est financée par des appels de fonds échelonnés, par le fonds de travaux, et parfois par un prêt collectif. Des aides publiques existent pour la rénovation énergétique : leurs conditions évoluent, renseignez-vous avant le vote. Un plan pluriannuel de travaux aide à anticiper les dépenses sur plusieurs années plutôt que de les subir."])],
  retenir=["Les travaux de parties communes se décident en assemblée générale.", "Les urgences peuvent être engagées par le syndic sans vote préalable.", "Un plan pluriannuel lisse les dépenses dans le temps."]),

 dict(slug="vivre-a-beziers", cat="Villes", photo="bez-cath", city="beziers",
  alt="La cathédrale Saint-Nazaire dominant l'Orb à Béziers", cta="estimation",
  title="Vivre à Béziers : centre ancien, canal et art de vivre",
  desc="Quartiers, canal du Midi, proximité de la mer, transports : ce qu'il faut savoir avant d'acheter ou de louer à Béziers.",
  intro="Béziers se visite de loin : la cathédrale Saint-Nazaire domine l'Orb, et le Pont Vieux enjambe la rivière depuis des siècles. C'est aussi une ville où l'on vit bien, entre patrimoine, canal du Midi et proximité du littoral.",
  sections=[
   ("Un centre ancien et des promenades", ["Le cœur historique s'organise autour de la cathédrale et des ruelles voisines. Les allées Paul Riquet, grande promenade arborée, rythment la vie du centre-ville avec ses cafés et ses commerces. Les Halles et le jardin du Plateau des Poètes complètent un cadre apprécié des habitants."]),
   ("Le canal du Midi, les écluses et la mer", ["Béziers est bordée par le canal du Midi, inscrit au patrimoine mondial, et ses célèbres écluses de Fonséranes. Les plages de Valras-Plage, de Sérignan et du Cap d'Agde sont toutes proches : un atout pour les familles comme pour les résidences secondaires."]),
   ("Se loger à Béziers", ["On y trouve des appartements dans le centre, des maisons de ville et des maisons avec jardin plus en périphérie. La proximité de l'autoroute et de la gare facilite les déplacements. Avant d'acheter, visitez le quartier à différents moments de la journée, et renseignez-vous sur le stationnement, les commerces et les écoles. L'agence LOTIER a son siège à Béziers, rue Française : un conseiller peut vous guider."])],
  retenir=["Une ville patrimoniale, entre l'Orb, la cathédrale et le canal du Midi.", "La mer est à portée de voiture : Valras-Plage, Sérignan, Cap d'Agde.", "L'agence LOTIER est installée à Béziers."]),

 dict(slug="vivre-a-montpellier", seo_title="Vivre à Montpellier : du centre aux nouveaux quartiers", cat="Villes", photo="montpellier", city="montpellier",
  alt="La place de la Comédie à Montpellier le soir", cta="estimation",
  title="Vivre à Montpellier : du centre historique aux nouveaux quartiers",
  desc="Écusson, Antigone, Port Marianne, Arceaux, tramway : un tour des quartiers de Montpellier avant d'y acheter ou de louer.",
  intro="Montpellier est une ville vivante, étudiante et en pleine évolution. Son centre historique côtoie des quartiers contemporains et un réseau de tramway qui irrigue l'agglomération.",
  sections=[
   ("Le centre historique", ["L'Écusson, cœur ancien de la ville, concentre ruelles piétonnes, places, commerces et vie nocturne. La place de la Comédie en est le point de rendez-vous. On y trouve surtout des appartements dans des immeubles anciens, avec un charme certain mais aussi des contraintes : escaliers, stationnement difficile."]),
   ("Des quartiers très différents", [["Antigone : un quartier néoclassique dessiné par Ricardo Bofill, avec de grandes perspectives et un accès au fleuve ;", "Port Marianne : un quartier récent tourné vers le Lez, avec des programmes neufs et des commerces ;", "Les Arceaux et le Peyrou : des secteurs résidentiels et appréciés, au pied de l'aqueduc Saint-Clément ;", "Beaux-Arts et Boutonnet : des quartiers animés, proches du centre, très demandés des étudiants et des jeunes actifs."]]),
   ("Louer ou acheter à Montpellier", ["La demande est soutenue, notamment pour les petites surfaces proches du tramway et des universités. Pour un investisseur, le profil des locataires (étudiants, actifs en début de carrière) influence le choix du quartier et du type de bien. Un conseiller local vous aide à comparer les secteurs, les charges et les perspectives."])],
  retenir=["Un centre historique piéton et des quartiers contemporains très différents.", "Le tramway est un critère majeur dans le choix d'un logement.", "Un conseiller local aide à comparer les secteurs."]),

 dict(slug="vivre-a-nimes", cat="Villes", photo="nimes", city="nimes",
  alt="Les Arènes de Nîmes sous un ciel bleu", cta="estimation",
  title="Vivre à Nîmes : Arènes, Écusson et art de vivre gardois",
  desc="Centre historique, Maison Carrée, jardins de la Fontaine, quartiers résidentiels : ce qu'il faut savoir avant d'acheter ou de louer à Nîmes.",
  intro="Nîmes est une ville romaine par ses monuments, et méridionale par son art de vivre. Les Arènes, la Maison Carrée et les jardins de la Fontaine en font l'une des villes les plus riches en patrimoine du Languedoc.",
  sections=[
   ("Un patrimoine au quotidien", ["Les Arènes accueillent spectacles et férias. La Maison Carrée, l'un des temples romains les mieux conservés, fait face au Carré d'Art. Les jardins de la Fontaine et la Tour Magne offrent une grande promenade verte à deux pas du centre. Habiter près de ces lieux, c'est profiter d'un cadre rare."]),
   ("Les secteurs à connaître", [["l'Écusson, le centre historique, pour des appartements dans de beaux immeubles anciens ;", "les alentours des jardins de la Fontaine, appréciés pour leur calme et leur verdure ;", "les quartiers résidentiels plus éloignés du centre, avec maisons et stationnement plus faciles ;", "les communes voisines de l'agglomération, pour des maisons avec jardin et plus d'espace."]]),
   ("Se loger à Nîmes", ["Le marché propose appartements de caractère en centre-ville, maisons avec jardin en périphérie et programmes plus récents. Pour un achat comme pour une location, comparez plusieurs secteurs selon vos besoins : proximité du centre, école, accès aux axes routiers, stationnement. Un conseiller peut vous présenter les biens et vous orienter."])],
  retenir=["Une ville riche en patrimoine, du centre ancien aux jardins de la Fontaine.", "Des secteurs très variés : Écusson, quartiers résidentiels, communes voisines.", "L'agence LOTIER dispose d'une agence à Nîmes."]),

 dict(slug="vivre-a-carcassonne", seo_title="Vivre à Carcassonne : la Cité, la Bastide, le canal", cat="Villes", photo="carcassonne", city="carcassonne",
  alt="La Cité médiévale de Carcassonne", cta="estimation",
  title="Vivre à Carcassonne : la Cité, la Bastide et le canal du Midi",
  desc="Cité médiévale, Bastide Saint-Louis, canal du Midi, Lac de la Cavayère : un aperçu de Carcassonne pour acheter ou louer dans l'Aude.",
  intro="Carcassonne, c'est d'abord sa Cité médiévale, inscrite au patrimoine mondial. C'est aussi une ville du quotidien, avec sa Bastide, son canal du Midi et un cadre de vie tourné vers l'Aude et le Minervois.",
  sections=[
   ("Deux villes en une", ["La Cité, fortifiée, domine la ville depuis sa colline. En contrebas, la Bastide Saint-Louis, ville basse au plan en damier, concentre commerces, marchés et vie administrative. Le Pont Vieux relie les deux rives de l'Aude."]),
   ("Un cadre de vie tourné vers l'eau et la nature", ["Le canal du Midi traverse la ville et offre des promenades en bord d'eau. Le lac de la Cavayère, à proximité, permet de se promener, se baigner l'été et pratiquer des activités de plein air. Les vignobles du Minervois et du Cabardès sont tout proches."]),
   ("Acheter ou louer à Carcassonne", ["On y trouve des appartements en centre-ville, des maisons de ville dans la Bastide, des pavillons en périphérie et des maisons de village dans les communes voisines. Selon votre projet (résidence principale, investissement locatif, résidence secondaire), le choix du secteur change. L'agence LOTIER accompagne les projets dans l'Aude, sur le couloir de l'Aude : un conseiller peut vous présenter le marché."])],
  retenir=["Une Cité médiévale et une Bastide aux ambiances très différentes.", "Le canal du Midi et le lac de la Cavayère offrent un cadre de vie nature.", "L'agence LOTIER accompagne les projets dans l'Aude."]),
]
