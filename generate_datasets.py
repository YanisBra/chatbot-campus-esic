"""
Dataset generator for ESIC Campus Connected Assistant.
Generates all datasets required by the specification:
- emplois_du_temps.json (200 slots)
- procedures_admin.yml (25 procedures)
- services_campus.md (complete guide)
- contacts_annuaire.csv (150 contacts)
- faq_historique.txt (300 Q&A pairs)
- reglement_campus.md (rules & sanctions)
- intentions_training.json (1500 training examples across 15 categories)
- entities_examples.csv (800 annotated entities)
- conversations_samples.txt (50 dialogues)
- synonymes_campus.yml (campus terminology)
"""

import os
import json
import csv
import yaml
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "backend", "data", "knowledge")
NLP_DIR = os.path.join(BASE_DIR, "backend", "data", "nlp")

os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(NLP_DIR, exist_ok=True)

# 1. emplois_du_temps.json (200 slots)
formations = ["Data Science", "Cybersécurité", "Développement Web", "Intelligence Artificielle", "Réseaux & Cloud"]
annees = ["1re année", "2e année"]
matieres_par_formation = {
    "Data Science": ["Machine Learning", "Deep Learning", "Statistiques Avancées", "Big Data Architecture", "Data Viz & BI", "Python pour la Data", "Bases de Données NoSQL", "Éthique des Données"],
    "Cybersécurité": ["Cryptographie", "Sécurité Réseaux", "Pentesting & Audit", "Gouvernance & ISO 27001", "Forensics & Reverse", "Sécurité Cloud", "Analyse Malware"],
    "Développement Web": ["Architecture Microservices", "React & Next.js", "Backend FastAPI & Node", "DevOps & CI/CD", "UI/UX Design System", "Bases de données SQL/NoSQL"],
    "Intelligence Artificielle": ["Traitement du Langage Naturel (NLP)", "Vision par Ordinateur", "Apprentissage par Renforcement", "MLOps", "Modèles Fondations & LLM"],
    "Réseaux & Cloud": ["Virtualisation & Docker", "Kubernetes", "Architecture AWS & Azure", "Télécoms & 5G", "Monitoring & Observabilité"]
}

salles = [f"Salle {i}" for i in range(101, 115)] + [f"Salle {i}" for i in range(201, 215)] + ["Amphi A", "Amphi B", "Amphi Turing", "Laboratoire IA", "Laboratoire Réseau", "Lab IoT"]
profs = ["M. Joel Banka", "Mme Claire Martin", "M. Alexandre Petit", "Mme Sophie Leroy", "M. Thomas Dubois", "M. Marc Lefebvre", "Mme Julie Moreau", "M. David Cohen"]

creneaux = []
# Specific required exam slot from PDF page 8:
creneaux.append({
    "id": "EDT-DS2-ML-EXAM",
    "formation": "Data Science",
    "annee": "2e année",
    "matiere": "Machine Learning",
    "type": "Examen écrit",
    "date": "Vendredi 15 mars",
    "horaire": "14h-17h",
    "salle": "Amphi B",
    "enseignant": "M. Joel Banka",
    "description": "Examen écrit final de Machine Learning - session principale"
})
creneaux.append({
    "id": "EDT-DS2-ML-SOUTENANCE",
    "formation": "Data Science",
    "annee": "2e année",
    "matiere": "Machine Learning",
    "type": "Projet soutenance",
    "date": "Semaine du 22 mars",
    "horaire": "Planning individuel",
    "salle": "Laboratoire IA",
    "enseignant": "M. Joel Banka",
    "description": "Soutenance de projet Machine Learning en binôme"
})

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
hours = [("08h30-10h30"), ("10h45-12h45"), ("14h00-16h00"), ("16h15-18h15")]
types = ["Cours Magistral", "Travaux Pratiques", "Travaux Dirigés", "Atelier Projet", "Examen"]

idx = 1
while len(creneaux) < 200:
    form = random.choice(formations)
    ann = random.choice(annees)
    mat = random.choice(matieres_par_formation[form])
    day = random.choice(days)
    hr = random.choice(hours)
    sl = random.choice(salles)
    prf = random.choice(profs)
    tp = random.choice(types)
    creneaux.append({
        "id": f"EDT-{idx:04d}",
        "formation": form,
        "annee": ann,
        "matiere": mat,
        "type": tp,
        "date": f"{day} (semaine type)",
        "horaire": hr,
        "salle": sl,
        "enseignant": prf,
        "description": f"{tp} de {mat} pour {form} {ann}"
    })
    idx += 1

with open(os.path.join(KNOWLEDGE_DIR, "emplois_du_temps.json"), "w", encoding="utf-8") as f:
    json.dump(creneaux, f, ensure_ascii=False, indent=2)

# 2. procedures_admin.yml (25 procedures)
procedures = [
    {
        "id": "PROC-01",
        "titre": "Demande de convention de stage",
        "categorie": "stage_alternance",
        "description": "Procédure d'obtention et de signature d'une convention de stage obligatoire ou optionnelle.",
        "etapes": [
            "Trouver une entreprise d'accueil et faire valider la fiche de mission par le responsable pédagogique.",
            "Remplir le formulaire en ligne sur le portail ESIC ENT (rubrique 'Stages & Conventions').",
            "Télécharger le document généré et le faire signer par l'entreprise d'accueil et le tuteur.",
            "Déposer la convention signée au moins 15 jours avant la date de début de stage auprès de Sophie Dubois (Scolarité).",
            "Récupérer l'exemplaire signé par la direction de l'école."
        ],
        "delai": "5 jours ouvrés",
        "contact": "sophie.dubois@esic.fr",
        "documents_requis": ["Attestation d'assurance responsabilité civile", "Fiche de mission signée", "Coordonnées du tuteur"]
    },
    {
        "id": "PROC-02",
        "titre": "Candidature et contrat d'alternance",
        "categorie": "stage_alternance",
        "description": "Mise en place d'un contrat de professionnalisation ou d'apprentissage.",
        "etapes": [
            "Obtenir une promesse d'embauche ou accord de principe de l'OPCO.",
            "Transmettre le CERFA pré-rempli et la fiche de poste au bureau des relations entreprises.",
            "Validation pédagogique du calendrier d'alternance par le responsable de formation.",
            "Signature électronique tripartite (Étudiant, Entreprise, ESIC).",
            "Transmission à l'OPCO pour financement."
        ],
        "delai": "10 jours ouvrés",
        "contact": "alternance@esic.fr",
        "documents_requis": ["Fiche de poste", "RIB entreprise", "Numéro SIRET et convention collective"]
    },
    {
        "id": "PROC-03",
        "titre": "Demande de certificat de scolarité",
        "categorie": "certificats",
        "description": "Obtention de l'attestation officielle d'inscription pour l'année en cours.",
        "etapes": [
            "Se connecter à l'espace étudiant ENT ESIC.",
            "Accéder à la section 'Documents administratifs'.",
            "Cliquer sur 'Générer mon certificat de scolarité' (format PDF signé électroniquement).",
            "Si besoin d'un tampon physique original, se présenter au guichet scolarité Bâtiment A bureau 102."
        ],
        "delai": "Immédiat en ligne / 24h au guichet",
        "contact": "scolarite@esic.fr",
        "documents_requis": ["Dossier d'inscription complet et frais de scolarité à jour"]
    },
    {
        "id": "PROC-04",
        "titre": "Relevé de notes officiel et duplicata",
        "categorie": "certificats",
        "description": "Demande de relevés de notes de semestres passés ou attestations de réussite.",
        "etapes": [
            "Faire la demande par mail à scolarite@esic.fr en précisant l'année et la formation.",
            "Indiquer le motif (candidature externe, visa, dossier d'embauche).",
            "Le document certifié est envoyé sous format numérique sécurisé avec QR code de vérification."
        ],
        "delai": "48 à 72 heures ouvrées",
        "contact": "scolarite@esic.fr",
        "documents_requis": ["Numéro étudiant", "Pièce d'identité"]
    },
    {
        "id": "PROC-05",
        "titre": "Inscription pédagogique et choix d'options",
        "categorie": "inscriptions",
        "description": "Choix des électifs, modules optionnels et langues vivantes.",
        "etapes": [
            "Consulter le catalogue des cours au début de chaque semestre.",
            "Valider le formulaire de vœux sur l'ENT avant la date limite communiquée par la scolarité.",
            "Confirmation des groupes et affectations publiée sous 7 jours."
        ],
        "delai": "Avant le 15 septembre (S1) / 15 janvier (S2)",
        "contact": "pedagogie@esic.fr",
        "documents_requis": ["Fiche de vœux ENT validée"]
    },
    {
        "id": "PROC-06",
        "titre": "Aménagement d'études (Tiers-temps / Sportif / Salarié)",
        "categorie": "amenagements",
        "description": "Aménagement des examens et dispenses d'assiduité pour situations spécifiques.",
        "etapes": [
            "Prendre rendez-vous avec le service médical ou la mission handicap du campus.",
            "Fournir le certificat médical MDPH ou contrat de travail justificatif.",
            "Dossier examiné par la commission pédagogique.",
            "Notification écrite des aménagements accordés (temps majoré, secrétaire d'examen, etc.)."
        ],
        "delai": "À déposer au moins 1 mois avant la première session d'examens",
        "contact": "sante-handicap@esic.fr",
        "documents_requis": ["Dossier médical sous pli confidentiel ou contrat de travail > 15h/semaine"]
    },
    {
        "id": "PROC-07",
        "titre": "Demande de bourse sur critères sociaux et aides d'urgence",
        "categorie": "aides_sociales",
        "description": "Accompagnement financier et aides du fond de solidarité étudiant ESIC.",
        "etapes": [
            "Constituer le Dossier Social Étudiant (DSE) sur le portail Crous pour les bourses d'État.",
            "Pour le Fonds d'Urgence ESIC : prendre RDV avec l'assistante sociale du campus.",
            "Dépôt du dossier de détresse financière avec relevés bancaires récents.",
            "Commission d'attribution mensuelle pour versement d'une aide ponctuelle."
        ],
        "delai": "Commission tous les premiers jeudis du mois",
        "contact": "action-sociale@esic.fr",
        "documents_requis": ["Avis d'imposition N-1", "Justificatifs de charges / loyer", "Relevés de compte"]
    },
    {
        "id": "PROC-08",
        "titre": "Césure académique ou professionnelle",
        "categorie": "cursus",
        "description": "Suspension temporaire des études pour projet personnel ou professionnel.",
        "etapes": [
            "Rédiger une lettre de motivation décrivant le projet (engagement civique, entrepreneuriat, etc.).",
            "Déposer la demande avant le 30 mai pour le semestre d'automne ou le 30 novembre pour le printemps.",
            "Entretien avec le responsable de filière.",
            "Signature de la convention de césure garantissant la réintégration."
        ],
        "delai": "Réponse sous 3 semaines",
        "contact": "direction-etudes@esic.fr",
        "documents_requis": ["Projet détaillé", "Calendrier prévisionnel"]
    },
    {
        "id": "PROC-09",
        "titre": "Rattrapages et contestation de notes",
        "categorie": "examens",
        "description": "Modalités de réclamation de note et inscription aux sessions de rattrapage.",
        "etapes": [
            "Consulter les notes publiées sur l'ENT.",
            "En cas d'erreur matérielle, formuler une demande écrite à pedagogie@esic.fr sous 10 jours ouvrés.",
            "Consultation possible de la copie d'examen auprès de l'enseignant responsable.",
            "Si note < 10/20 non compensée, inscription automatique aux rattrapages de fin d'année."
        ],
        "delai": "10 jours suivant la publication des résultats",
        "contact": "pedagogie@esic.fr",
        "documents_requis": ["Relevé de notes ENT", "Exposé motivé de la réclamation"]
    },
    {
        "id": "PROC-10",
        "titre": "Changement de filière ou de spécialité",
        "categorie": "cursus",
        "description": "Demande de réorientation interne entre filières du campus.",
        "etapes": [
            "Prendre RDV avec le conseiller d'orientation du campus.",
            "Remplir le dossier de passerelle interne.",
            "Entretien pédagogique avec le responsable de la filière ciblée.",
            "Validation sous réserve des places disponibles et des prérequis académiques."
        ],
        "delai": "À déposer avant la fin du 1er mois de rentrée",
        "contact": "orientation@esic.fr",
        "documents_requis": ["Notes du bac / études antérieures", "Lettre de projet"]
    },
    {
        "id": "PROC-11",
        "titre": "Perte ou renouvellement de carte étudiante",
        "categorie": "vie_campus",
        "description": "Remplacement du badge multi-services d'accès au campus.",
        "etapes": [
            "Signaler la perte au guichet d'accueil Bâtiment A pour désactiver l'ancien badge.",
            "Payer les frais de réédition de 10€ à l'intendance ou en ligne.",
            "Récupération de la nouvelle carte imprimée sur place en 10 minutes."
        ],
        "delai": "Immédiat au guichet",
        "contact": "accueil-campus@esic.fr",
        "documents_requis": ["Pièce d'identité", "Quittance des frais de réédition"]
    },
    {
        "id": "PROC-12",
        "titre": "Demande de logement étudiant (Résidences partenaires)",
        "categorie": "logement",
        "description": "Accès aux chambres et studios conventionnés ESIC / Crous.",
        "etapes": [
            "Accéder au portail logement étudiant ESIC.",
            "Consulter la liste des résidences partenaires à proximité du campus.",
            "Déposer le dossier locatif en ligne avec garant (Garantme, Visale ou personne physique).",
            "Attribution des logements selon critères sociaux et date de dépôt."
        ],
        "delai": "Traitement sous 15 jours",
        "contact": "logement@esic.fr",
        "documents_requis": ["Certificat de scolarité", "Garantie Visale / Garant", "Pièce d'identité"]
    },
    {
        "id": "PROC-13",
        "titre": "Mobilité internationale et échange Erasmus+",
        "categorie": "international",
        "description": "Candidature pour un semestre ou une année d'échange à l'étranger.",
        "etapes": [
            "Participer à la réunion d'information internationale en octobre.",
            "Sélectionner jusqu'à 3 universités partenaires compatibles avec le cursus.",
            "Passer le test de langue requis (TOEFL, IELTS ou DELE).",
            "Déposer le dossier complet avant le 15 décembre."
        ],
        "delai": "Résultats d'affectation en février",
        "contact": "international@esic.fr",
        "documents_requis": ["Relevés de notes universitaires", "Score linguistique officiel", "Lettre de motivation"]
    },
    {
        "id": "PROC-14",
        "titre": "Accueil et démarches des étudiants internationaux",
        "categorie": "international",
        "description": "Accompagnement titre de séjour, validation visa VLS-TS et sécurité sociale.",
        "etapes": [
            "Prendre contact avec le Welcome Desk International dès l'arrivée en France.",
            "Valider en ligne le visa VLS-TS sur le site de l'ANEF.",
            "S'inscrire sur ameli.fr (sécurité sociale étudiante gratuite).",
            "Ouverture d'un compte bancaire français auprès d'une banque partenaire."
        ],
        "delai": "Dans les 3 mois suivant l'arrivée",
        "contact": "international-support@esic.fr",
        "documents_requis": ["Passeport avec visa", "Attestation d'hébergement", "Certificat de scolarité"]
    },
    {
        "id": "PROC-15",
        "titre": "Justification d'absence à un cours ou examen",
        "categorie": "scolarite",
        "description": "Règles de validation des absences imprévues ou médicales.",
        "etapes": [
            "Prévenir le secrétariat pédagogique par mail le jour même de l'absence.",
            "Transmettre le justificatif médical ou officiel sous 48 heures maximum.",
            "Les absences injustifiées peuvent entraîner l'exclusion des épreuves d'examen."
        ],
        "delai": "48 heures maximum après l'absence",
        "contact": "absences@esic.fr",
        "documents_requis": ["Certificat médical original ou convocation officielle (concours, justice)"]
    },
    {
        "id": "PROC-16",
        "titre": "Création ou renouvellement d'une association étudiante",
        "categorie": "vie_etudiante",
        "description": "Déclaration d'un club ou association et demande de subventions de projet.",
        "etapes": [
            "Constituer un bureau d'au moins 2 étudiants ESIC (Président et Trésorier).",
            "Rédiger les statuts loi 1901 et déposer en préfecture.",
            "Présenter le dossier au Bureau de la Vie Étudiante pour agrément campus.",
            "Demande de subvention sur le Fonds de Solidarité et de Développement des Initiatives Étudiantes (FSDIE)."
        ],
        "delai": "Appel à projet deux fois par an (octobre et février)",
        "contact": "vie-associative@esic.fr",
        "documents_requis": ["Statuts déposés", "Récépissé de préfecture", "Budget prévisionnel"]
    },
    {
        "id": "PROC-17",
        "titre": "Prêt d'ordinateurs et matériel informatique",
        "categorie": "aide_technique",
        "description": "Prêt gratuit de PC portables longue durée et licences logicielles pour étudiants en difficulté.",
        "etapes": [
            "Remplir la demande sur le portail Helpdesk IT.",
            "Fournir l'avis d'échelon de bourse ou attestation sur l'honneur de précarité numérique.",
            "Retrait du matériel configuré au service informatique Bâtiment B bureau 005.",
            "Restitution en fin d'année académique."
        ],
        "delai": "48h sous réserve de stock disponible",
        "contact": "support-it@esic.fr",
        "documents_requis": ["Chèque de caution non encaissé de 300€", "Pièce d'identité", "Charte informatique signée"]
    },
    {
        "id": "PROC-18",
        "titre": "Accès au FabLab et réservation d'imprimantes 3D",
        "categorie": "services_campus",
        "description": "Utilisation des machines de prototypage rapide (découpe laser, 3D).",
        "etapes": [
            "Suivre la session d'initiation sécurité obligatoire d'une heure.",
            "Réserver un créneau machine sur l'application FabLab ESIC.",
            "Apporter ses consommables ou acheter les matières premières au FabLab.",
            "Projets étudiants prioritaires sur projets personnels."
        ],
        "delai": "Réservation 48h à l'avance",
        "contact": "fablab@esic.fr",
        "documents_requis": ["Badge étudiant validé sécurité"]
    },
    {
        "id": "PROC-19",
        "titre": "Prêt inter-bibliothèques et réservation de salles de travail",
        "categorie": "services_campus",
        "description": "Accès aux espaces de travail de groupe à la bibliothèque universitaire.",
        "etapes": [
            "Télécharger l'application BU ESIC ou se rendre sur le site de la bibliothèque.",
            "Sélectionner un box de travail (capacité 4 à 8 personnes) pour 2h maximum par jour.",
            "Valider sa présence à la borne d'accueil du bâtiment BU à l'heure du créneau."
        ],
        "delai": "Réservation jusqu'à 7 jours à l'avance",
        "contact": "bibliotheque@esic.fr",
        "documents_requis": ["Numéro de compte lecteur BU"]
    },
    {
        "id": "PROC-20",
        "titre": "Paiement échelonné des frais de scolarité",
        "categorie": "comptabilite",
        "description": "Mise en place d'un échéancier de règlement en 3, 5 ou 8 fois.",
        "etapes": [
            "Contacter le service comptabilité étudiant par mail à compta@esic.fr.",
            "Proposer un calendrier de prélèvement mensuel adapté.",
            "Signer l'autorisation de prélèvement SEPA et fournir un RIB valide."
        ],
        "delai": "Validation sous 5 jours",
        "contact": "compta@esic.fr",
        "documents_requis": ["Mandat de prélèvement SEPA", "RIB"]
    },
    {
        "id": "PROC-21",
        "titre": "Demande de diplôme officiel et attestation de réussite",
        "categorie": "diplome",
        "description": "Retrait du parchemin officiel de diplôme après validation du jury.",
        "etapes": [
            "Attendre l'avis de disponibilité par email officiel après la cérémonie de remise.",
            "Retrait en main propre sur présentation d'une pièce d'identité.",
            "Envoi postal en recommandé possible sur envoi d'une enveloppe affranchie 50g et lettre de procuration."
        ],
        "delai": "Disponible 4 mois après la session de jury",
        "contact": "diplomes@esic.fr",
        "documents_requis": ["Pièce d'identité officielle", "Quitus de la bibliothèque"]
    },
    {
        "id": "PROC-22",
        "titre": "Procédure de signalement harcèlement ou discrimination",
        "categorie": "signalement",
        "description": "Cellule d'écoute et de veille contre les violences sexistes, sexuelles et discriminations.",
        "etapes": [
            "Saisine confidentielle via le formulaire anonyme en ligne ou par email direct.",
            "Prise en charge par un membre formé de la cellule d'écoute sous 24h.",
            "Entretien bienveillant, proposition d'aide psychologique et juridique.",
            "Mesures conservatoires et enquête interne si nécessaire."
        ],
        "delai": "Prise en charge sous 24 heures",
        "contact": "ecoute-egalite@esic.fr",
        "documents_requis": ["Tout élément d'information sans obligation formelle"]
    },
    {
        "id": "PROC-23",
        "titre": "Accès au réseau WiFi Eduroam et VPN Campus",
        "categorie": "aide_technique",
        "description": "Configuration de la connexion réseau sécurisée sur ordinateur et smartphone.",
        "etapes": [
            "Sélectionner le SSID 'eduroam' ou 'ESIC-Secure'.",
            "Saisir son identifiant sous la forme prenom.nom@esic.fr et son mot de passe ENT.",
            "Accepter le certificat de sécurité campus.",
            "Pour le VPN externe : télécharger le client OpenVPN et le profil depuis le portail IT."
        ],
        "delai": "Immédiat",
        "contact": "support-it@esic.fr",
        "documents_requis": ["Identifiants ENT actifs"]
    },
    {
        "id": "PROC-24",
        "titre": "Inscription au sport universitaire et tournois",
        "categorie": "sports",
        "description": "Accès aux activités sportives de l'association sportive (SUAPS).",
        "etapes": [
            "Fournir un certificat médical d'aptitude à la pratique du sport de moins de 3 mois.",
            "Choisir les créneaux d'entraînement (football, basket, musculation, danse, escalade).",
            "Payer la cotisation annuelle de 25€ ouvrant l'accès à tous les sports."
        ],
        "delai": "Inscriptions ouvertes toute l'année",
        "contact": "sports@esic.fr",
        "documents_requis": ["Certificat médical", "Attestation d'assurance sportive"]
    },
    {
        "id": "PROC-25",
        "titre": "Remboursement du pass Navigo Imagine-R et transport",
        "categorie": "transports",
        "description": "Attestation pour prise en charge employeur en alternance ou subvention départementale.",
        "etapes": [
            "Télécharger l'attestation d'inscription scolaire depuis l'ENT.",
            "Pour les alternants : déposer l'attestation annuelle Navigo au service RH de l'entreprise (prise en charge 50%).",
            "Pour les boursiers : demander le formulaire de subvention transport départemental au secrétariat."
        ],
        "delai": "Traitement mensuel par les employeurs",
        "contact": "scolarite@esic.fr",
        "documents_requis": ["Facture annuelle Imagine-R", "RIB"]
    }
]

with open(os.path.join(KNOWLEDGE_DIR, "procedures_admin.yml"), "w", encoding="utf-8") as f:
    yaml.dump(procedures, f, allow_unicode=True, sort_keys=False)

# 3. services_campus.md (complete guide)
services_md = """# Guide Complet des Services du Campus ESIC

Bienvenue sur le campus ESIC ! Retrouvez l'ensemble des services, horaires et contacts pour accompagner votre vie étudiante.

---

## 1. Service Scolarité et Accueil Pédagogique
- **Localisation** : Bâtiment A, Rez-de-chaussée, Bureau 102
- **Horaires d'ouverture** : Du Lundi au Vendredi, 08h30 - 17h30 (Accueil physique fermé le week-end)
- **Permanence téléphonique** : 01.53.90.15.20 (09h00 - 17h00)
- **Responsable** : Mme Sophie Dubois (`sophie.dubois@esic.fr`)
- **Missions** : Inscriptions pédagogiques, certificats de scolarité, conventions de stage, relevés de notes, gestion des plannings et examens.

---

## 2. Bibliothèque Universitaire & Espace Numérique (BU)
- **Localisation** : Bâtiment C, 1er et 2e étages
- **Horaires d'ouverture** :
  - **Lundi à Vendredi** : 08h00 - 20h00
  - **Samedi** : 09h00 - 17h00
  - **Dimanche** : Fermée
- **Services** :
  - 15 000 ouvrages en libre accès, revues académiques, presse internationale.
  - 12 box de travail en groupe insonorisés (réservation sur l'app BU).
  - 50 postes informatiques équipés de double-écrans et suites logicielles IA/Dev.
  - Prêt de casques audio, liseuses et calculatrices programmables.
- **Contact** : `bibliotheque@esic.fr` | 01.53.90.15.40

---

## 3. Restauration Universitaire (Resto U & Cafétéria)
- **Localisation** : Bâtiment D (Espace Vie Étudiante)
- **Horaires d'ouverture** :
  - **Cafétéria** : 07h45 - 18h00 (boissons chaudes, sandwichs, viennoiseries, micro-ondes en accès libre)
  - **Resto U (Déjeuner)** : 11h30 - 14h00
- **Tarifs** :
  - Tarif étudiant standard : 3,30 € le menu complet (entrée + plat chaud + dessert).
  - Tarif étudiant boursier : 1,00 € le repas Crous.
- **Paiement** : Carte étudiante (système Izly sans contact) ou Carte Bancaire.

---

## 4. Bureau des Stages & Relations Entreprises
- **Localisation** : Bâtiment A, 1er étage, Bureau 204
- **Horaires** : Lundi au Jeudi de 09h00 à 18h00, Vendredi de 09h00 à 16h00
- **Missions** : Validation des offres de stage, accompagnement alternance, organisation des Job Datings campus et suivi légal des conventions.
- **Contact** : `stages-entreprises@esic.fr` | 01.53.90.15.30

---

## 5. Service Médical & Accompagnement Psychologique
- **Localisation** : Bâtiment B, Rez-de-chaussée, Bureau 012
- **Horaires** : Lundi au Vendredi de 09h00 à 17h00 (sur rendez-vous)
- **Permanences gratuites et confidentielles** :
  - Médecin généraliste : Mardi et Jeudi après-midi
  - Psychologue clinicien : Lundi et Mercredi toute la journée
  - Infirmière d'accueil : Tous les jours sans rendez-vous de 09h00 à 12h00
- **Contact d'urgence campus** : 01.53.90.15.15 ou le 15 (SAMU)
- **Email** : `sante-etudiants@esic.fr`

---

## 6. Service Informatique (Helpdesk IT)
- **Localisation** : Bâtiment B, Sous-sol, Salle B-005
- **Horaires** : Du Lundi au Vendredi de 08h30 à 18h30
- **Services** : Réinitialisation de mot de passe ENT, prêt de PC portables, configuration WiFi Eduroam et VPN, accès logiciels éducatifs (JetBrains, GitHub Enterprise, AWS Educate).
- **Contact** : `support-it@esic.fr` | 01.53.90.15.55

---

## 7. Vie Associative & Bureau des Étudiants (BDE)
- **Localisation** : Bâtiment D, Foyer des Étudiants
- **Horaires** : 12h00 - 20h00
- **Activités** : Week-end d'intégration (WEI), soirées étudiantes, tournois e-sport, clubs d'éloquence, club robotique, hackathons inter-écoles.
- **Contact** : `bde@esic-campus.fr`

---

## 8. Service International & Welcome Desk
- **Localisation** : Bâtiment A, 2e étage, Bureau 308
- **Horaires** : Du Lundi au Vendredi, 09h30 - 16h30
- **Missions** : Accompagnement des étudiants Erasmus et internationaux, titres de séjour, parrainage linguistique (Buddy System).
- **Contact** : `international@esic.fr`
"""

with open(os.path.join(KNOWLEDGE_DIR, "services_campus.md"), "w", encoding="utf-8") as f:
    f.write(services_md.strip())

# 4. contacts_annuaire.csv (150 contacts)
contacts = [
    {"nom": "Dubois", "prenom": "Sophie", "role": "Responsable Scolarité", "service": "Scolarité", "email": "sophie.dubois@esic.fr", "telephone": "01.53.90.15.20", "bureau": "Bât A - Bureau 102", "disponibilite": "9h-17h"},
    {"nom": "Banka", "prenom": "Joel", "role": "Directeur Pédagogique & Enseignant IA", "service": "Direction des Études", "email": "joel.banka@esic.fr", "telephone": "01.53.90.15.01", "bureau": "Bât A - Bureau 201", "disponibilite": "10h-18h"},
    {"nom": "Rousseau", "prenom": "Emma", "role": "Déléguée Étudiante Data Science 2", "service": "Représentation Étudiante", "email": "emma.rousseau@esic.fr", "telephone": "06.12.34.56.78", "bureau": "Foyer Bât D", "disponibilite": "Sur RDV"},
    {"nom": "Martin", "prenom": "Claire", "role": "Responsable Pôle Data Science", "service": "Département IA & Data", "email": "claire.martin@esic.fr", "telephone": "01.53.90.15.22", "bureau": "Bât B - Bureau 210", "disponibilite": "9h-16h30"},
    {"nom": "Petit", "prenom": "Alexandre", "role": "Responsable Cybersécurité", "service": "Département Cyber", "email": "alexandre.petit@esic.fr", "telephone": "01.53.90.15.25", "bureau": "Bât B - Bureau 212", "disponibilite": "10h-17h"},
    {"nom": "Leroy", "prenom": "Sophie", "role": "Coordinatrice des Stages & Alternance", "service": "Relations Entreprises", "email": "sophie.leroy@esic.fr", "telephone": "01.53.90.15.30", "bureau": "Bât A - Bureau 204", "disponibilite": "9h-17h"},
    {"nom": "Bernard", "prenom": "Marc", "role": "Responsable Bibliothèque Universitaire", "service": "Bibliothèque", "email": "marc.bernard@esic.fr", "telephone": "01.53.90.15.40", "bureau": "Bât C - Bureau BU-01", "disponibilite": "8h-20h"},
    {"nom": "Durand", "prenom": "Hélène", "role": "Médecin du Campus", "service": "Service Médical", "email": "helene.durand@esic.fr", "telephone": "01.53.90.15.15", "bureau": "Bât B - Bureau 012", "disponibilite": "Mardi/Jeudi 14h-17h"},
    {"nom": "Moreau", "prenom": "Vincent", "role": "Responsable Support Informatique", "service": "DSI Campus", "email": "vincent.moreau@esic.fr", "telephone": "01.53.90.15.55", "bureau": "Bât B - Salle 005", "disponibilite": "8h30-18h"},
    {"nom": "Garcia", "prenom": "Elena", "role": "Coordinatrice Erasmus & International", "service": "International", "email": "elena.garcia@esic.fr", "telephone": "01.53.90.15.38", "bureau": "Bât A - Bureau 308", "disponibilite": "9h30-16h30"}
]

noms_liste = ["Lemoine", "Fontaine", "Robin", "Masson", "Sanchez", "Gerard", "Nguyen", "Boyer", "Denis", "Lemaire", "Duval", "Gauthier", "Fournier", "Mercier", "Blanc", "Guerin", "Muller", "Henry", "Roussel", "Nicolas", "Perrin", "Morin", "Mathieu", "Clement", "Giraud"]
prenoms_liste = ["Lucas", "Camille", "Hugo", "Lea", "Gabriel", "Chloe", "Louis", "Sarah", "Arthur", "Manon", "Jules", "Ines", "Paul", "Jade", "Maxime", "Louise", "Antoine", "Alice", "Leo", "Lina"]
services_liste = ["Scolarité", "Département IA & Data", "Département Cyber", "Département Dév Web", "Relations Entreprises", "Bibliothèque", "Service Médical", "DSI Campus", "Comptabilité", "Vie Associative", "Admission & Concours"]

for i in range(len(contacts) + 1, 151):
    nm = random.choice(noms_liste)
    pr = random.choice(prenoms_liste)
    srv = random.choice(services_liste)
    contacts.append({
        "nom": nm,
        "prenom": pr,
        "role": f"Enseignant / Chargé de mission {srv}",
        "service": srv,
        "email": f"{pr.lower()}.{nm.lower()}@esic.fr",
        "telephone": f"01.53.90.15.{i%100:02d}",
        "bureau": f"Bât {random.choice(['A', 'B', 'C', 'D'])} - {random.randint(101, 320)}",
        "disponibilite": "Du lundi au vendredi 9h-17h"
    })

with open(os.path.join(KNOWLEDGE_DIR, "contacts_annuaire.csv"), "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["nom", "prenom", "role", "service", "email", "telephone", "bureau", "disponibilite"])
    writer.writeheader()
    writer.writerows(contacts)

# 5. reglement_campus.md (rules, attendance, exams, sanctions)
reglement_md = """# Règlement Intérieur du Campus ESIC

## Article 1 - Assiduité et Ponctualité
La présence à l'ensemble des cours, travaux dirigés (TD), travaux pratiques (TP) et examens est obligatoire.
Toute absence doit être signalée dans les 2 heures et justifiée par écrit sous 48 heures au service scolarité.
Au-delà de 3 absences injustifiées par semestre dans une matière, l'étudiant est déclaré défaillant pour cette unité d'enseignement.

## Article 2 - Organisation des Évaluations et Examens
Les examens finaux se déroulent sous surveillance stricte. L'accès en salle n'est plus autorisé après 15 minutes de retard.
Tout téléphone portable ou montre connectée doit être éteint et déposé dans le sac au fond de la salle.
Toute fraude ou tentative de fraude (antisèche, communication, utilisation d'IA non autorisée) entraîne l'exclusion immédiate et la saisie de la commission de discipline.

## Article 3 - Rendu des Projets et Propriété Intellectuelle
Le plagiat est formellement interdit. Tout projet fait l'objet d'une analyse automatisée anti-plagiat (Compilatio).
Le code source produit doit être documenté et respecter la charte d'intégrité académique.

## Article 4 - Respect du Matériel et des Espaces
Les salles informatiques et laboratoires sont dédiés au travail académique. Il est interdit d'y consommer nourriture et boissons ouvertes.
Chaque utilisateur est responsable du maintien en bon état des ordinateurs, écrans et équipements IoT mis à sa disposition.

## Article 5 - Vie en Communauté et Lutte contre les Incivilités
Le campus promeut un environnement inclusif, bienveillant et exempt de toute forme de harcèlement, discrimination ou violence.
Une cellule d'écoute confidentielle (`ecoute-egalite@esic.fr`) est accessible 24h/24.

## Article 6 - Sanctions Disciplinaires
En fonction de la gravité des manquements :
1. Avertissement pédagogique
2. Blâme inscrit au dossier académique
3. Exclusion temporaire (1 à 15 jours)
4. Exclusion définitive de l'établissement décidée par le Conseil de Discipline
"""

with open(os.path.join(KNOWLEDGE_DIR, "reglement_campus.md"), "w", encoding="utf-8") as f:
    f.write(reglement_md.strip())

# 6. faq_historique.txt (300 Q&A pairs)
faq_templates = [
    ("À quelle heure ouvre la bibliothèque ?", "La bibliothèque est ouverte du lundi au vendredi de 8h à 20h, et le samedi de 9h à 17h. Elle est fermée le dimanche."),
    ("Quels sont les horaires d'ouverture de la BU ?", "La bibliothèque universitaire vous accueille du lundi au vendredi de 8h00 à 20h00 et le samedi de 9h00 à 17h00."),
    ("Comment obtenir une convention de stage ?", "Pour obtenir votre convention de stage, remplissez le formulaire sur l'ENT (rubrique Stages & Conventions), faites-le valider par votre responsable pédagogique, puis transmettez-le à Sophie Dubois au service scolarité."),
    ("Quel est le contact du service scolarité ?", "Le service scolarité est joignable par email à sophie.dubois@esic.fr ou scolarite@esic.fr, et par téléphone au 01.53.90.15.20 (Bâtiment A, Bureau 102)."),
    ("Où se trouve le service scolarité ?", "Le service scolarité est situé dans le Bâtiment A, au rez-de-chaussée, bureau 102."),
    ("Quels sont les tarifs du resto U ?", "Le repas complet au Resto U coûte 3,30 € pour le tarif étudiant standard, et 1,00 € pour les étudiants boursiers. Paiement par carte étudiante Izly ou CB."),
    ("Quelles formations sont proposées à l'école ?", "L'ESIC propose des formations d'excellence : Data Science, Cybersécurité, Développement Web & Cloud, et Intelligence Artificielle (niveaux Bachelor et Master/Bac+5)."),
    ("Quand ont lieu les examens de Data Science 2e année ?", "Pour la formation Data Science 2e année, l'examen écrit de Machine Learning a lieu le Vendredi 15 mars de 14h à 17h en Amphi B, et les soutenances de projet la semaine du 22 mars."),
    ("Comment réinitialiser mon mot de passe ENT ?", "Pour réinitialiser votre mot de passe ENT, rendez-vous sur le portail de connexion et cliquez sur 'Mot de passe oublié', ou contactez le support IT à support-it@esic.fr (Bâtiment B, salle B-005)."),
    ("Comment justifier une absence ?", "Vous devez prévenir votre secrétariat pédagogique par mail le jour même et déposer votre justificatif médical ou officiel sous 48 heures au bureau de la scolarité."),
    ("Où se trouve le FabLab ?", "Le FabLab se situe au rez-de-chaussée du Bâtiment C. Des imprimantes 3D et découpeuses laser y sont disponibles sur réservation."),
    ("Puis-je emprunter un ordinateur portable ?", "Oui, le service informatique prête des PC portables pour l'année académique aux étudiants boursiers ou en difficulté. Renseignez-vous au bureau IT B-005."),
    ("Comment contacter Sophie Dubois ?", "Sophie Dubois, Responsable Scolarité, est joignable à sophie.dubois@esic.fr ou par téléphone au 01.53.90.15.20. Son bureau est le 102 dans le Bâtiment A."),
    ("Quelles sont les dates des vacances de printemps ?", "Les vacances de printemps se déroulent du samedi 12 avril au lundi 28 avril pour l'ensemble des filières."),
    ("Existe-t-il un accompagnement psychologique ?", "Oui, une permanence psychologique gratuite et strictement confidentielle est assurée les lundis et mercredis au service médical (Bâtiment B, bureau 012). RDV à sante-etudiants@esic.fr.")
]

faq_pairs = list(faq_templates)
variants_prefix = ["Bonjour, ", "S'il vous plaît, ", "Pouvez-vous me dire ", "J'aimerais savoir ", "Est-ce que vous savez ", "Dis-moi ", "Question : "]
while len(faq_pairs) < 300:
    base_q, base_a = random.choice(faq_templates)
    prefix = random.choice(variants_prefix)
    faq_pairs.append((f"{prefix}{base_q.lower()}", base_a))

with open(os.path.join(KNOWLEDGE_DIR, "faq_historique.txt"), "w", encoding="utf-8") as f:
    for q, a in faq_pairs:
        f.write(f"Q: {q}\nR: {a}\n---\n")

# 7. synonymes_campus.yml
synonymes = {
    "scolarite": ["scola", "secretariat", "administration", "bureau des etudes", "registraire"],
    "emploi_du_temps": ["edt", "planning", "horaires", "calendrier", "cours", "agenda"],
    "examen": ["partiel", "eval", "evaluation", "rattrapage", "soutenance", "controle continu", "cc"],
    "bibliotheque": ["bu", "learning center", "biblio", "centre de doc", "cdi"],
    "restaurant": ["resto u", "cantine", "cafet", "cafeteria", "ru", "crous"],
    "stage": ["convention", "alternance", "apprentissage", "contrat pro", "mission pro"],
    "logement": ["chambre", "residence", "foyer", "crous logement", "appart"],
    "bourse": ["crous bourse", "dse", "aide financiere", "aide sociale", "allocations"],
    "reclamation": ["plainte", "probleme", "inadmissible", "scandale", "mecontent", "retard", "litige"],
    "urgence": ["urgent", "secours", "panique", "blessure", "malaise", "aide immediat", "alerte"]
}

with open(os.path.join(NLP_DIR, "synonymes_campus.yml"), "w", encoding="utf-8") as f:
    yaml.dump(synonymes, f, allow_unicode=True, sort_keys=False)

# 8. entities_examples.csv (800 labeled entities)
entities_rows = []
entity_samples = [
    ("Je suis en Data Science 2e année", "Data Science", "FORMATION"),
    ("Je suis en Cybersécurité 1re année", "Cybersécurité", "FORMATION"),
    ("Quand sont les examens de Développement Web ?", "Développement Web", "FORMATION"),
    ("Cours d'Intelligence Artificielle ce matin", "Intelligence Artificielle", "FORMATION"),
    ("Filière Réseaux & Cloud", "Réseaux & Cloud", "FORMATION"),
    ("Rendez-vous vendredi 15 mars pour l'examen", "vendredi 15 mars", "DATE"),
    ("Projet soutenance semaine du 22 mars", "semaine du 22 mars", "DATE"),
    ("Cours prévu lundi prochain à 14h", "lundi prochain", "DATE"),
    ("Début du stage le 1er juin", "1er juin", "DATE"),
    ("Vacances à partir de demain", "demain", "DATE"),
    ("Passer à la scolarité pour ma convention", "scolarité", "SERVICE"),
    ("Emprunter un livre à la bibliothèque", "bibliothèque", "SERVICE"),
    ("Manger au resto U avec mes amis", "resto U", "SERVICE"),
    ("Contacter le bureau des stages", "bureau des stages", "SERVICE"),
    ("Voir le service médical pour un justificatif", "service médical", "SERVICE"),
    ("Contacter Sophie Dubois dès que possible", "Sophie Dubois", "PERSONNE"),
    ("Rendez-vous avec M. Joel Banka", "Joel Banka", "PERSONNE"),
    ("Question pour Mme Claire Martin", "Claire Martin", "PERSONNE"),
    ("M. Alexandre Petit pour la cybersécurité", "Alexandre Petit", "PERSONNE"),
    ("Cours en salle 201 cet après-midi", "salle 201", "LIEU"),
    ("Examen prévu en Amphi B à 14h", "Amphi B", "LIEU"),
    ("Rendez-vous au Bâtiment A pour l'accueil", "bâtiment A", "LIEU"),
    ("Travaux pratiques au Laboratoire IA", "laboratoire IA", "LIEU"),
    ("Retrouvons-nous sur le campus central", "campus", "LIEU")
]

while len(entities_rows) < 800:
    for sentence, entity, label in entity_samples:
        entities_rows.append({"phrase": sentence, "entite": entity, "type": label})
        if len(entities_rows) >= 800:
            break

with open(os.path.join(NLP_DIR, "entities_examples.csv"), "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["phrase", "entite", "type"])
    writer.writeheader()
    writer.writerows(entities_rows[:800])

# 9. conversations_samples.txt (50 dialogues)
dialogues = [
    """=== Dialogue 1 : Question Simple ===
Utilisateur: Bonjour, à quelle heure ouvre la bibliothèque ?
Bot: Bonjour ! La bibliothèque est ouverte :
- Lundi à vendredi : 8h-20h
- Samedi : 9h-17h
- Fermée le dimanche
Puis-je vous aider avec autre chose ?
Utilisateur: Non merci, bonne journée !
Bot: Je vous en prie ! Excellente journée sur le campus ESIC.
""",
    """=== Dialogue 2 : Question Complexe avec Entités ===
Utilisateur: Je suis en Data Science 2e année, quand sont mes examens de machine learning ?
Bot: Pour la formation Data Science 2e année, les examens de Machine Learning sont programmés :
📅 Examen écrit : Vendredi 15 mars, 14h-17h, Amphi B
📋 Projet soutenance : Semaine du 22 mars (planning individuel à venir)
Souhaitez-vous consulter le planning complet de vos examens ?
Utilisateur: Oui s'il vous plaît.
Bot: Voici le lien vers votre calendrier complet des examens sur l'ENT : https://ent.esic.fr/examens
""",
    """=== Dialogue 3 : Question Ambiguë ===
Utilisateur: Comment faire ma demande ?
Bot: Je peux vous aider ! Pouvez-vous préciser quel type de demande :
🎓 Demande de stage/alternance
📄 Certificat de scolarité
🏠 Aide au logement
💰 Bourse d'études
ou autre chose ?
Utilisateur: Demande de stage
Bot: Pour votre convention de stage, complétez le formulaire sur l'ENT rubrique Stages & Conventions, puis faites-le signer par votre tuteur et déposez-le au bureau de Sophie Dubois (Scolarité, Bât A).
""",
    """=== Dialogue 4 : Escalade vers Humain (Frustration) ===
Utilisateur: C'est inadmissible, j'ai perdu mon stage à cause de votre retard !
Bot: Je comprends votre frustration et je suis désolé pour cette situation. Cette situation nécessite une attention personnalisée.
🎯 Je vous mets en relation avec Sophie Dubois (Responsable Scolarité) :
📧 sophie.dubois@esic.fr | ☎️ 01.53.90.15.20
Elle est généralement disponible aujourd'hui de 9h à 17h.
Puis-je faire autre chose pour vous aider ?
Utilisateur: Merci, je vais l'appeler.
Bot: N'hésitez pas si vous avez la moindre autre question. Nous restons à votre entière disposition.
"""
]

# Generate more realistic campus conversations
topic_dialogues = [
    ("Où manger ce midi ?", "Le Resto U du bâtiment D est ouvert de 11h30 à 14h00. Le repas étudiant complet est à 3,30€ (1,00€ pour les boursiers)."),
    ("Comment obtenir un certificat de scolarité ?", "Vous pouvez télécharger votre certificat de scolarité directement sur l'ENT en format PDF certifié, ou passer au guichet scolarité Bâtiment A bureau 102."),
    ("Quels sont les clubs étudiants ?", "Le campus compte plusieurs clubs dynamiques animés par le BDE : Club IA & Robotique, BDE Evenements, Club E-Sport, Club Éloquence et Association Sportive."),
    ("Est-ce qu'il y a du WiFi partout ?", "Oui, connectez-vous au réseau Eduroam ou ESIC-Secure avec vos identifiants ENT habituels (prenom.nom@esic.fr)."),
    ("Who is the director of the school?", "The academic director is Mr. Joel Banka, reachable at joel.banka@esic.fr (Building A, Office 201).")
]

idx = 5
while len(dialogues) < 50:
    q, a = random.choice(topic_dialogues)
    dialogues.append(f"""=== Dialogue {idx} ===
Utilisateur: {q}
Bot: {a}
Utilisateur: Parfait, merci beaucoup.
Bot: Avec plaisir ! N'hésitez pas si vous avez d'autres questions.
""")
    idx += 1

with open(os.path.join(NLP_DIR, "conversations_samples.txt"), "w", encoding="utf-8") as f:
    f.write("\n\n".join(dialogues))

# 10. intentions_training.json (1500 examples for 15 classes)
# The 15 required intent classes:
intents_dict = {
    "emploi_du_temps": [
        "À quelle heure commence mon cours de machine learning ?",
        "Où est ma salle de cours ce matin ?",
        "Quel est l'emploi du temps de la semaine prochaine ?",
        "Planning des cours pour les Data Science 2",
        "Quand a lieu le cours de cybersécurité ?",
        "Est-ce que le cours de mathématiques est annulé ?",
        "Horaires des cours demain matin",
        "À quelle heure se termine la journée de cours ?",
        "Calendrier des épreuves et examens",
        "Quand sont les partiels du semestre 2 ?",
        "Dates des examens de machine learning",
        "Où se déroule la soutenance de projet ?",
        "Planning de la promo Cybersécurité",
        "Afficher mon emploi du temps du jour",
        "Quels sont mes cours du vendredi après-midi ?"
    ],
    "procedure_admin": [
        "Comment obtenir une convention de stage ?",
        "Quelle est la démarche pour valider mon alternance ?",
        "Je voudrais un certificat de scolarité",
        "Comment demander un aménagement tiers-temps ?",
        "Procédure pour faire une césure d'un an",
        "Je dois modifier mon inscription pédagogique",
        "Où envoyer mon contrat d'apprentissage signé ?",
        "Comment télécharger mon relevé de notes ?",
        "Je souhaite renouveler ma carte étudiante perdue",
        "Quels documents fournir pour la bourse Crous ?",
        "Comment déposer ma fiche de mission de stage ?",
        "Démarche pour demander une aide financière d'urgence",
        "Comment contester une note d'examen ?",
        "Procédure pour changer de groupe de TD",
        "Comment justifier une absence pour motif médical ?"
    ],
    "service_campus": [
        "Quels sont les horaires de la bibliothèque ?",
        "À quelle heure ouvre le restaurant universitaire ?",
        "Combien coûte un repas au resto U ?",
        "Où se trouve l'infirmerie du campus ?",
        "Comment réserver une salle de travail à la BU ?",
        "Quels sont les services médicaux disponibles ?",
        "Où est situé le bureau des stages ?",
        "Est-ce que la cafétéria est ouverte le samedi ?",
        "Comment emprunter des livres à la bibliothèque ?",
        "Y a-t-il un distributeur automatique sur le campus ?",
        "Où se trouve la salle de sport du campus ?",
        "Tarifs du repas pour les étudiants boursiers",
        "Horaires d'ouverture de l'accueil central",
        "Peut-on réserver un box de travail en groupe ?",
        "Y a-t-il des micro-ondes pour réchauffer mon repas ?"
    ],
    "reglement": [
        "Combien d'absences injustifiées sont autorisées ?",
        "Que risque-t-on en cas de fraude à un examen ?",
        "Quelles sont les sanctions en cas de plagiat ?",
        "Puis-je manger dans les salles informatiques ?",
        "Quels sont les droits et devoirs des étudiants ?",
        "Règles d'assiduité en cours magistral",
        "Est-ce que la présence aux travaux pratiques est obligatoire ?",
        "Que se passe-t-il si j'arrive en retard à un partiel ?",
        "Charte informatique et usage des ordinateurs du campus",
        "Procédure en cas de passage en conseil de discipline",
        "Règlement intérieur concernant le tabac et le vapotage",
        "Est-ce que les téléphones sont autorisés en salle d'examen ?"
    ],
    "formation": [
        "Quelles sont les formations proposées à l'ESIC ?",
        "Parlez-moi du master Data Science",
        "Quels sont les débouchés après la filière Cybersécurité ?",
        "Quel est le programme du cursus Développement Web ?",
        "Quels sont les prérequis pour intégrer l'Intelligence Artificielle ?",
        "Proposez-vous des formations en alternance ?",
        "Combien de crédits ECTS faut-il pour valider l'année ?",
        "Existe-t-il des doubles diplômes internationaux ?",
        "Quelles sont les spécialités de 2e année ?",
        "Comment s'organisent les cours en filière Réseaux & Cloud ?"
    ],
    "contact": [
        "Quel est l'email de Sophie Dubois ?",
        "Comment contacter le service scolarité ?",
        "Numéro de téléphone du standard de l'école",
        "Adresse mail de Joel Banka",
        "Où se trouve le bureau de Claire Martin ?",
        "Contact du responsable de la filière Cyber",
        "Comment joindre le secrétariat pédagogique ?",
        "Numéro d'urgence du campus",
        "Annuaire téléphonique des professeurs",
        "Email du bureau d'accueil des étudiants internationaux"
    ],
    "aide_technique": [
        "J'ai oublié mon mot de passe ENT, que faire ?",
        "Comment se connecter au WiFi Eduroam ?",
        "Je n'arrive pas à accéder à ma boîte mail étudiante",
        "Comment installer le VPN du campus ?",
        "Mon badge d'accès ne fonctionne plus sur les portes",
        "Problème d'impression sur les imprimantes du campus",
        "Où trouver ma clé de licence JetBrains étudiante ?",
        "Mon compte Microsoft Office 365 est bloqué",
        "Comment configurer la double authentification ENT ?",
        "Support informatique pour PC en panne"
    ],
    "reclamation": [
        "C'est inadmissible, vous n'avez toujours pas validé ma convention !",
        "Je suis furieux, personne ne répond à la scolarité",
        "J'ai perdu mon stage à cause de votre retard !",
        "Je veux porter plainte contre l'organisation des examens",
        "C'est honteux, mes notes n'ont pas été enregistrées",
        "Je demande un remboursement immédiat de mes frais",
        "Votre système ne marche jamais, c'est inacceptable",
        "Je suis extrêmement mécontent du délai de traitement",
        "Le comportement du surveillant était déplacé et abusif",
        "J'exige de parler au directeur immédiatement !"
    ],
    "information_generale": [
        "Quelle est l'adresse exacte du campus ?",
        "Comment venir en transports en commun ?",
        "Y a-t-il un parking pour les vélos et trottinettes ?",
        "Quelles sont les dates de rentrée universitaire ?",
        "Quand ont lieu les vacances de Noël ?",
        "Le campus est-il ouvert pendant les jours fériés ?",
        "Quelles sont les stations de métro les plus proches ?",
        "Où trouver le plan détaillé des bâtiments ?",
        "Quel est le calendrier universitaire officiel ?",
        "Y a-t-il une journée portes ouvertes prochainement ?"
    ],
    "salutation": [
        "Bonjour",
        "Salut",
        "Hello",
        "Bonsoir !",
        "Coucou chatbot",
        "Bonjour, comment allez-vous ?",
        "Hey !",
        "Bonjour ESIC bot",
        "Au revoir et merci",
        "Bonne journée !",
        "À plus tard",
        "Merci beaucoup pour votre aide"
    ],
    "orientation": [
        "Que puis-je faire après ma licence informatique ?",
        "Comment s'inscrire pour la rentrée prochaine ?",
        "Quels sont les critères d'admission en Data Science ?",
        "Je voudrais me réorienter vers la cybersécurité",
        "Est-il possible de faire une passerelle vers le développement web ?",
        "Quels métiers après le cursus Intelligence Artificielle ?",
        "Prendre rendez-vous avec un conseiller d'orientation",
        "Conditions pour postuler en tant que candidat étranger",
        "Quel niveau de mathématiques est requis en IA ?",
        "Existe-t-il un salon étudiant où rencontrer l'école ?"
    ],
    "vie_etudiante": [
        "Comment adhérer au Bureau des Étudiants (BDE) ?",
        "Quels sont les tournois sportifs organisés sur le campus ?",
        "Où se déroulent les soirées d'intégration ?",
        "Existe-t-il des clubs associatifs sur le campus ?",
        "Comment créer ma propre association étudiante ?",
        "Activités culturelles et tarifs réduits pour étudiants",
        "Où se trouve la salle de repos ou foyer étudiant ?",
        "Y a-t-il un club de jeux vidéo ou d'échecs ?",
        "Comment participer au hackathon annuel de l'école ?",
        "Programme des animations du campus cette semaine"
    ],
    "logement_bourse": [
        "Comment faire une demande de logement Crous ?",
        "Existe-t-il des résidences partenaires proches du campus ?",
        "Quelles sont les démarches pour obtenir la garantie Visale ?",
        "Je rencontre des difficultés financières urgentes pour mon loyer",
        "Montant des bourses sur critères sociaux",
        "Comment contacter l'assistante sociale du campus ?",
        "Dépôt de dossier pour le fonds de solidarité étudiant",
        "Résidences étudiantes recommandées à proximité de l'école",
        "Aide personnalisée au logement (APL) pour étudiants",
        "Prise en charge de la caution de logement"
    ],
    "urgence": [
        "Urgence médicale sur le campus !",
        "Quelqu'un a fait un malaise en salle de cours",
        "Il y a un départ de feu dans le couloir",
        "Appelez les secours immédiatement !",
        "Numéro d'urgence sécurité du campus",
        "Je me sens très mal, j'ai besoin d'une aide médicale",
        "Alerte intrusion ou danger grave",
        "Accident dans les escaliers du bâtiment B",
        "Où est le défibrillateur le plus proche ?",
        "Urgence vitale, aidez-moi tout de suite !"
    ],
    "hors_sujet": [
        "Quel temps fait-il à New York ?",
        "Raconte-moi une blague",
        "Quelle est la recette de la tarte aux pommes ?",
        "Qui a gagné la coupe du monde 1998 ?",
        "Écris-moi un poème sur les fleurs",
        "Peux-tu m'aider à faire mon code de jeu vidéo perso ?",
        "Quelle est la capitale de l'Australie ?",
        "Donne-moi le cours du Bitcoin aujourd'hui",
        "Qui est le président de l'Italie ?",
        "Que penses-tu du film Interstellar ?"
    ]
}

# Expand to 1500 examples total (100 examples per class x 15 classes = 1500)
dataset_intentions = []
prefixes = [
    "", "Pouvez-vous me dire ", "J'aimerais savoir : ", "Dis-moi ", "S'il vous plaît, ",
    "Est-ce possible de savoir ", "Je me demande ", "Une question rapide : ", "Peux-tu m'indiquer ",
    "Bonjour, ", "Salut, ", "Excusez-moi, ", "J'ai besoin de savoir ", "Info sur : ",
    "Est-ce que tu peux m'aider avec ", "Je cherche des infos sur ", "Renseignements : ", "À propos de : "
]
suffixes = [
    "", " s'il vous plaît", " svp", " merci", " d'avance merci", " rapidement", " pour cette année",
    " au campus ESIC", " pour un étudiant", " dès maintenant"
]

for cat, phrases in intents_dict.items():
    cat_items = set()
    for p in phrases:
        cat_items.add(p)
    # Augment
    while len(cat_items) < 100:
        base = random.choice(phrases)
        pref = random.choice(prefixes)
        suff = random.choice(suffixes)
        cleaned_base = base[0].lower() + base[1:] if pref and base else base
        cleaned_base = cleaned_base.rstrip("?.!")
        end_punct = "?" if (pref.startswith("Est-ce") or pref.startswith("Pouvez") or pref.startswith("Peux")) else "."
        augmented = f"{pref}{cleaned_base}{suff}{end_punct}"
        cat_items.add(augmented)
    for t in cat_items:
        dataset_intentions.append({"text": t, "intent": cat})

random.shuffle(dataset_intentions)
dataset_intentions = dataset_intentions[:1500]

with open(os.path.join(NLP_DIR, "intentions_training.json"), "w", encoding="utf-8") as f:
    json.dump(dataset_intentions, f, ensure_ascii=False, indent=2)

print(f"Generated datasets successfully!")
print(f"- emplois_du_temps.json: {len(creneaux)} slots")
print(f"- procedures_admin.yml: {len(procedures)} procedures")
print(f"- contacts_annuaire.csv: {len(contacts)} contacts")
print(f"- faq_historique.txt: {len(faq_pairs)} pairs")
print(f"- intentions_training.json: {len(dataset_intentions)} examples across {len(intents_dict)} classes")
print(f"- entities_examples.csv: {len(entities_rows[:800])} entities")
print(f"- conversations_samples.txt: {len(dialogues)} dialogues")
