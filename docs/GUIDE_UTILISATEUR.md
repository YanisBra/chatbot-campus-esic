# 📘 Guide Utilisateur - Assistant Virtuel Campus Connecté ESIC

Bienvenue sur le guide d'utilisation de l'**Assistant Virtuel Campus Connecté & Borne Interactive** de l'ESIC.

---

## 🎯 Présentation Générale
L'assistant virtuel est conçu pour accompagner au quotidien l'ensemble de la communauté du campus :
- **Étudiants** : Emplois du temps, examens, soutenances, démarches de stages et alternance.
- **Étudiants Internationaux & Erasmus** : Accueil multilingue (Français, Anglais, Espagnol), logement, démarches administratives.
- **Visiteurs & Prospects** : Découverte des filières (Data Science, Cyber, Dév Web, IA), plan interactif du campus, prise de contact.

---

## 💬 1. Utilisation du Chatbot Web & Mobile

### 1.1 Accès à l'application
Ouvrez votre navigateur web sur l'adresse locale : `http://127.0.0.1:8000`. L'interface s'adapte automatiquement à votre écran (ordinateur portable, tablette ou smartphone).

### 1.2 Poser une question en langage naturel (US-001)
Saisissez votre question dans le champ texte au bas de l'écran ou cliquez sur une des suggestions proposées.
Exemples de questions comprises par le bot :
- *"À quelle heure ouvre la bibliothèque ?"*
- *"Quels sont les tarifs du resto U ?"*
- *"Comment obtenir ma convention de stage ?"*
- *"Quel est l'email de Sophie Dubois ?"*

### 1.3 Questions avec personnalisation selon votre filière (US-016)
Si vous êtes connecté(e) via votre profil (par exemple en **Data Science 2e année**), vous pouvez poser des questions contextuelles :
- *"Quand sont mes examens de machine learning ?"*
- Le bot vous répondra précisément :
  > **Pour la formation Data Science 2e année, les examens de Machine Learning sont programmés :**  
  > 📅 **Examen écrit** : Vendredi 15 mars, 14h-17h, Amphi B  
  > 📋 **Projet soutenance** : Semaine du 22 mars (planning individuel à venir)

### 1.4 Gestion des questions ambiguës (US-018)
Si votre question est trop générale, par exemple :
- *"Comment faire ma demande ?"*
Le bot vous propose des options claires pour vous guider :
- 🎓 Demande de stage / alternance
- 📄 Certificat de scolarité
- 🏠 Aide au logement
- 💰 Bourse d'études

### 1.5 Escalade vers un responsable humain (US-027)
En cas de litige, réclamation urgente ou situation de blocage (détection automatique de frustration) :
- Exemple : *"C'est inadmissible, j'ai perdu mon stage à cause de votre retard !"*
- L'assistant bascule immédiatement vers un contact personnalisé auprès de **Sophie Dubois (Responsable Scolarité)** :
  - 📧 `sophie.dubois@esic.fr`
  - ☎️ `01.53.90.15.20` (disponible 9h - 17h, Bâtiment A - Bureau 102)

### 1.6 Reconnaissance Vocale et Synthèse Vocale (US-029)
- **Microphone (Speech-to-Text)** : Cliquez sur l'icône micro pour dicter votre question à la voix.
- **Haut-parleur (Text-to-Speech)** : Activez l'icône de son en haut à droite pour que le bot lise les réponses à haute voix.

### 1.7 Évaluation des réponses (US-024)
Sur chaque réponse du bot, vous disposez des boutons 👍 (Utile) et 👎 (Inexacte) pour noter la réponse et laisser un commentaire afin d'améliorer la base de connaissances.

---

## 🖥️ 2. Utilisation de la Borne Tactile IoT (21")

Dans l'onglet **"Borne IoT (21")"**, retrouvez la simulation de l'écran d'accueil tactile installé dans le hall du Bâtiment A :

1. **Mode Visiteur** :
   - Tuiles d'accès direct aux informations clés.
   - **Plan interactif du campus** : Cliquez sur les Bâtiments A, B, C ou D pour afficher immédiatement leurs services associés.
2. **Mode Étudiant (Badge sans contact)** :
   - Cliquez sur **"Badger Emma Rousseau"** ou **"Badger Carlos Martinez"** pour simuler le scan de votre badge étudiant RFID/NFC et charger instantanément votre planning d'examens.
3. **Mode Vocal Mains-Libres** :
   - Interface sonore avec retour visuel animé conçu pour une utilisation debout sans toucher l'écran.
4. **Mode Accessibilité** :
   - Cliquez sur le bouton "Accessibilité" pour basculer en mode **contraste élevé (fond noir / texte jaune)** et police agrandie.

---

## 🌐 3. Support Multilingue (International)

Les étudiants internationaux (Persona Carlos Martinez) peuvent échanger directement en **anglais** ou en **espagnol** :
- Exemples en anglais :
  - *"What are the library opening hours?"*
  - *"How can I contact student affairs?"*
- Exemples en espagnol :
  - *"¿Cuáles son los horarios de la biblioteca?"*
  - *"¿Dónde puedo comer al mediodía?"*

---

## 🔒 4. Confidentialité et Droits RGPD

Cliquez sur votre profil en haut à droite puis sur **"Confidentialité RGPD & Oubli"** :
- **Droit à la portabilité** : Cliquez sur *"Exporter mes données (JSON)"* pour télécharger l'historique complet de votre session.
- **Droit à l'oubli** : Cliquez sur *"Supprimer mes données"* pour effacer définitivement l'ensemble de vos conversations de la base de données.
