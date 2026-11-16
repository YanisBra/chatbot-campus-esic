# 🛠️ Guide Administrateur - Assistant Virtuel Campus Connecté ESIC

Ce guide est destiné aux équipes de la **DSI**, aux **responsables de scolarité (Sophie Dubois)** et aux **analystes pédagogiques** administrant la solution.

---

## 🏛️ 1. Architecture Technique Globale

L'application est architecturée en services modulaires :
```
[Frontend Web Responsive & Borne IoT] 
         │ (HTTP / JSON REST API)
         ▼
[Backend FastAPI Engine]
   ├── [Module Sécurité] : Rate Limiting (10 req/min), Anti-Injection, XSS & Anonymisation PII
   ├── [NLP Pipeline] :
   │     ├── Intent Classifier (15 classes, TF-IDF + Logistic Regression, >85% précision)
   │     ├── NER Extractor (FORMATION, DATE, SERVICE, PERSONNE, LIEU)
   │     ├── Sentiment & Urgency Detector (neutre, frustration, urgent, satisfaction)
   │     └── Semantic Similarity (Cosine Similarity sur FAQ avec seuil > 0.70)
   ├── [Services Métier] :
   │     ├── Knowledge Service (EDT 200 créneaux, 25 procédures, annuaire 150 contacts)
   │     ├── Analytics Service (10 KPIs en temps réel, calcul ROI)
   │     └── IoT Kiosk Service (Heartbeats, télémétrie, scan RFID)
   └── [Base de Données] : SQLite 3 (Interactions, Feedbacks, Fiches dynamiques, Bornes IoT)
```

---

## 📊 2. Dashboard Analytics & Mesure du ROI (US-019 à US-023)

Accessible via l'onglet **"Analytics & ROI"** :

### 2.1 Les 10 Métriques Temps Réel
1. **Volume Total de Questions** : Nombre d'interactions enregistrées depuis le déploiement.
2. **Taux de Résolution sans Escalade** : Pourcentage de questions traitées automatiquement sans solliciter un agent (cible > 75%).
3. **Score Moyen de Satisfaction** : Calculé sur une échelle de 1 à 5 étoiles à partir des votes étudiants 👍/👎.
4. **Temps de Réponse Moyen (Latence)** : Mesuré en millisecondes (garanti < 2 secondes).
5. **Heures Économisées Scolarité (ROI)** : Basé sur 5 minutes de traitement économisées par question résolue.
6. **Économies Financières (€)** : Valorisation sur la base du coût horaire moyen du secrétariat.
7. **Courbe d'Activité sur 24h** : Détection des pics horaires pour adapter les permanences d'accueil physique.
8. **Répartition des Catégories (15 Classes)** : Emplois du temps, bourses, stages, contacts, etc.
9. **Top 10 des Questions Fréquentes** : Liste en direct des requêtes les plus formulées.
10. **Avis & Retours Qualitatifs** : Visualisation des commentaires laissés par les étudiants.

---

## 📚 3. Gestion de la Base de Connaissances (US-025, US-026)

Accessible via l'onglet **"Base de Connaissances"** :
1. **Statut des Données Chargées** :
   - 200 créneaux d'emplois du temps (`emplois_du_temps.json`)
   - 25 fiches procédures administratives (`procedures_admin.yml`)
   - 150 contacts de l'annuaire campus (`contacts_annuaire.csv`)
   - 300 paires de questions/réponses historiques (`faq_historique.txt`)
2. **Ajout d'une nouvelle fiche en direct** :
   - Choisissez la catégorie.
   - Saisissez les mots-clés de recherche.
   - Entrez la question type et la réponse officielle.
   - Cliquez sur **"Ajouter à la base active"** : la mise à jour est instantanée sans redémarrage de serveur.

---

## 📡 4. Supervision de la Flotte de Bornes IoT (US-031)

Le tableau de supervision affiche l'état de santé de chaque borne du campus :
- `BORNE-01` : Bâtiment A - Hall Central
- `BORNE-02` : Bâtiment C - Entrée BU
- `BORNE-03` : Bâtiment D - Hall Resto U
- `BORNE-04` : Bâtiment B - Pôle Tech & Labos IA

**Indicateurs supervisés** :
- Statut de connexion (`ONLINE` vert, `WARNING` orange si heartbeat > 90s, `OFFLINE` rouge si > 180s).
- Niveau de charge batterie.
- Compteur cumulé d'interactions tactiles / vocales.
- Mode actuellement actif sur la borne (Visiteur, Étudiant, Vocal).

---

## 🛡️ 5. Sécurité, Filtrage et RGPD

### 5.1 Sécurité Applicative
- **Anti-Prompt Injection** : Détection et blocage immédiat des motifs de jailbreak (*"ignore previous instructions"*, *"system prompt reveal"*, etc.).
- **Anti-XSS & Injections de Code** : Sanitisation HTML stricte et échappement des caractères de contrôle.
- **Rate Limiting** : Blocage automatique au-delà de 10 requêtes par minute par adresse IP ou identifiant client.

### 5.2 Conformité RGPD
- **Anonymisation** : Filtrage à la volée des emails, numéros de téléphone et numéros de sécurité sociale avant toute écriture en base de logs.
- **Durée de conservation** : Rétention maximale de 6 mois.
- **Endpoints de Conformité** :
  - `DELETE /api/rgpd/delete/{client_or_session_id}` : Suppression irréversible de l'historique (Droit à l'oubli).
  - `GET /api/rgpd/export/{session_id}` : Export portable au format JSON (Droit à la portabilité).

---

## 🚀 6. Déploiement et Maintenance

### Déploiement Local Rapide
```bash
./run.sh
```

### Déploiement via Docker
```bash
docker compose up --build -d
```

### Exécution des Tests de Recette
```bash
./venv/bin/pytest backend/tests/ -v
```
Le rapport de tests vérifie l'ensemble des 20 critères d'acceptation fonctionnels, la précision NLP > 85%, et la tenue de charge à 100 utilisateurs simultanés.
