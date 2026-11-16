/**
 * ESIC Campus Connected Assistant - Frontend Single Page Application
 * Handles Chatbot, 21" IoT Kiosk Simulation, Real-time Analytics (Admin),
 * Knowledge Base Administration (Admin), and ENT SSO.
 * 
 * Styled according to https://www.esic.fr/ Design System & Art Direction.
 */

// Application State
let currentTab = 'chat';
let activeSessionId = 'session_' + Math.random().toString(36).substring(2, 9);
let activeClientId = 'client_' + Math.random().toString(36).substring(2, 9);
let isTTSEnabled = false;
let isRecording = false;
let speechRecognizer = null;
let activeKioskMode = 'visiteur';
let hourlyChartInstance = null;
let categoryChartInstance = null;
let pendingAdminTab = null;

// Admin Authentication State
let isAdminAuthenticated = false;

// Mock Personas (Academic & Administrative)
const PERSONAS = {
  emma_rousseau: {
    id: "emma_rousseau",
    name: "Emma Rousseau",
    role: "Étudiante 2e année",
    formation: "Data Science",
    annee: "2e année",
    student_id: "ESIC-2024-DS-042",
    email: "emma.rousseau@esic.fr",
    avatar: "👩‍🎓",
    description: "Persona Principal : 20 ans, Data Science 2",
    is_admin: false
  },
  carlos_martinez: {
    id: "carlos_martinez",
    name: "Carlos Martinez",
    role: "Étudiant Erasmus",
    formation: "Data Science",
    annee: "Erasmus (2e année)",
    student_id: "ESIC-2024-INT-109",
    email: "carlos.martinez@esic.fr",
    avatar: "👨‍🎓",
    description: "Persona Secondaire : 23 ans, International (EN/ES)",
    is_admin: false
  },
  sophie_dubois: {
    id: "sophie_dubois",
    name: "Sophie Dubois",
    role: "Responsable Scolarité",
    formation: "Direction Scolarité & Admin",
    annee: "Staff Administrateur",
    student_id: "ADMIN-ESIC-001",
    email: "sophie.dubois@esic.fr",
    avatar: "👩‍💼",
    description: "Persona Administrateur : Responsable Scolarité (Accès Total)",
    is_admin: true
  },
  jean_moreau: {
    id: "jean_moreau",
    name: "Jean Moreau",
    role: "Visiteur / Prospect",
    formation: "Visiteur Lycéen",
    annee: "Terminale",
    student_id: "VISITEUR-2026",
    email: "jean.moreau@gmail.com",
    avatar: "🧑",
    description: "Persona Quaternaire : 18 ans, lycéen",
    is_admin: false
  }
};

let activeUser = PERSONAS.emma_rousseau;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  setupSpeechRecognition();
  updateProfileUI();
  updateAdminUI();
  loadSuggestions();
  loadNotifications();
});

// ==============================================================================
// Admin Authentication & Role Enforcement
// ==============================================================================
function updateAdminUI() {
  const lockAnalytics = document.getElementById('lock-icon-analytics');
  const lockAdmin = document.getElementById('lock-icon-admin');
  const statusPill = document.getElementById('admin-status-pill');
  const statusText = document.getElementById('admin-status-text');
  const dropdownAction = document.getElementById('admin-dropdown-action');

  if (isAdminAuthenticated) {
    if (lockAnalytics) lockAnalytics.textContent = '🔓';
    if (lockAdmin) lockAdmin.textContent = '🔓';
    if (statusPill) {
      statusPill.className = 'esic-badge esic-badge-mint text-[11px] cursor-pointer shadow-sm';
      statusText.innerHTML = '<i class="fa-solid fa-crown text-amber-500 mr-1"></i>Admin Actif (Sophie Dubois)';
      statusPill.onclick = () => logoutAdmin();
      statusPill.title = "Cliquez pour vous déconnecter du mode Administrateur";
    }
    if (dropdownAction) {
      dropdownAction.innerHTML = `
        <button onclick="logoutAdmin()" class="w-full text-left p-2 rounded-lg hover:bg-rose-50 text-rose-700 transition flex items-center space-x-2 text-xs font-semibold">
          <i class="fa-solid fa-right-from-bracket"></i>
          <span>Déconnexion Admin (Retour Étudiant)</span>
        </button>
      `;
    }
  } else {
    if (lockAnalytics) lockAnalytics.textContent = '🔒';
    if (lockAdmin) lockAdmin.textContent = '🔒';
    if (statusPill) {
      statusPill.className = 'esic-badge esic-badge-sombre text-[11px] cursor-pointer';
      statusText.innerHTML = '<i class="fa-solid fa-user-lock mr-1"></i>Accès Étudiant';
      statusPill.onclick = () => openAdminAuthModal('analytics');
      statusPill.title = "Cliquez pour vous connecter en tant qu'Administrateur";
    }
    if (dropdownAction) {
      dropdownAction.innerHTML = `
        <button onclick="openAdminAuthModal('analytics')" class="w-full text-left p-2 rounded-lg hover:bg-amber-50 text-amber-800 transition flex items-center space-x-2 text-xs font-semibold">
          <i class="fa-solid fa-key text-amber-600"></i>
          <span>Connexion Espace Admin</span>
        </button>
      `;
    }
  }
}

function openAdminAuthModal(targetTab = 'analytics') {
  pendingAdminTab = targetTab;
  document.getElementById('profile-dropdown').classList.add('hidden');
  const errBox = document.getElementById('admin-login-error');
  if (errBox) errBox.classList.add('hidden');
  document.getElementById('admin-auth-modal').classList.remove('hidden');
}

function closeAdminAuthModal() {
  document.getElementById('admin-auth-modal').classList.add('hidden');
  pendingAdminTab = null;
}

async function handleAdminLoginSubmit(event) {
  if (event) event.preventDefault();
  const username = document.getElementById('admin-login-username').value.trim();
  const password = document.getElementById('admin-login-password').value.trim();
  const errBox = document.getElementById('admin-login-error');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (res.ok) {
      const data = await res.json();
      isAdminAuthenticated = true;
      activeUser = PERSONAS.sophie_dubois;
      updateProfileUI();
      updateAdminUI();
      closeAdminAuthModal();
      
      const tabToOpen = pendingAdminTab || 'analytics';
      switchTab(tabToOpen);
      appendChatMessage('system', `🔐 Authentification réussie : Connecté en tant qu'Administrateur (Sophie Dubois).`);
    } else {
      const err = await res.json();
      if (errBox) {
        errBox.textContent = err.detail || "Identifiants incorrects.";
        errBox.classList.remove('hidden');
      }
    }
  } catch (e) {
    if (errBox) {
      errBox.textContent = "Erreur de connexion au serveur.";
      errBox.classList.remove('hidden');
    }
  }
}

function quickLoginAdmin(targetTab = 'analytics') {
  isAdminAuthenticated = true;
  activeUser = PERSONAS.sophie_dubois;
  updateProfileUI();
  updateAdminUI();
  closeAdminAuthModal();
  switchTab(targetTab || 'analytics');
  appendChatMessage('system', `⭐ Accès Rapide Démo : Connecté avec succès en tant qu'Administrateur (Sophie Dubois).`);
}

function logoutAdmin() {
  isAdminAuthenticated = false;
  activeUser = PERSONAS.emma_rousseau;
  updateProfileUI();
  updateAdminUI();
  switchTab('chat');
  appendChatMessage('system', `🔒 Déconnexion Admin : Vous êtes désormais en profil Étudiante (Emma Rousseau).`);
}

// ==============================================================================
// Tab Navigation with Admin Gate
// ==============================================================================
function switchTab(tabName) {
  currentTab = tabName;
  const tabs = ['chat', 'kiosk', 'analytics', 'admin', 'ent'];
  
  tabs.forEach(t => {
    const view = document.getElementById(`view-${t}`);
    const navBtn = document.getElementById(`nav-${t}`);
    if (t === tabName) {
      view.classList.remove('hidden');
      navBtn.classList.add('active-tab');
    } else {
      view.classList.add('hidden');
      navBtn.classList.remove('active-tab');
    }
  });

  // Check Admin Access for Analytics and Knowledge Base
  if (tabName === 'analytics') {
    const gate = document.getElementById('analytics-admin-gate');
    const content = document.getElementById('analytics-content-unlocked');
    if (!isAdminAuthenticated) {
      if (gate) gate.classList.remove('hidden');
      if (content) content.classList.add('hidden');
    } else {
      if (gate) gate.classList.add('hidden');
      if (content) content.classList.remove('hidden');
      loadRealtimeAnalytics();
    }
  } else if (tabName === 'admin') {
    const gate = document.getElementById('admin-kb-gate');
    const content = document.getElementById('admin-kb-content-unlocked');
    if (!isAdminAuthenticated) {
      if (gate) gate.classList.remove('hidden');
      if (content) content.classList.add('hidden');
    } else {
      if (gate) gate.classList.add('hidden');
      if (content) content.classList.remove('hidden');
      loadKnowledgeSummary();
      loadKiosksFleet();
    }
  }
}

// ==============================================================================
// Persona Switcher
// ==============================================================================
function toggleProfileDropdown() {
  const dd = document.getElementById('profile-dropdown');
  dd.classList.toggle('hidden');
}

function selectPersona(personaKey) {
  if (PERSONAS[personaKey]) {
    activeUser = PERSONAS[personaKey];
    if (activeUser.is_admin) {
      isAdminAuthenticated = true;
    } else {
      isAdminAuthenticated = false;
    }
    updateProfileUI();
    updateAdminUI();
    document.getElementById('profile-dropdown').classList.add('hidden');
    appendChatMessage('system', `Profil actif : <strong>${activeUser.name}</strong> (${activeUser.role} - ${activeUser.formation})`);
    
    // Refresh current tab if on analytics or admin
    if (currentTab === 'analytics' || currentTab === 'admin') {
      switchTab(currentTab);
    }
  }
}

function updateProfileUI() {
  document.getElementById('active-avatar').textContent = activeUser.avatar;
  document.getElementById('active-name').textContent = activeUser.name;
  document.getElementById('active-role').textContent = `${activeUser.formation} (${activeUser.annee})`;
  
  // Update ENT tab widgets
  const entAvatar = document.getElementById('ent-avatar');
  const entName = document.getElementById('ent-name');
  const entSubtitle = document.getElementById('ent-subtitle');
  if (entAvatar) entAvatar.textContent = activeUser.avatar;
  if (entName) entName.textContent = activeUser.name;
  if (entSubtitle) entSubtitle.textContent = `${activeUser.role} - ${activeUser.formation} | N° ${activeUser.student_id}`;
}

// ==============================================================================
// Chatbot Interactions (Sprint 1 & Sprint 2)
// ==============================================================================
async function handleChatSubmit(event) {
  if (event) event.preventDefault();
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  input.value = '';
  await sendQuery(query, 'web');
}

function sendQuickQuery(query) {
  sendQuery(query, 'web');
}

async function sendQuery(query, source = 'web') {
  appendChatMessage('user', query);

  // Show typing indicator
  const typingId = showTypingIndicator();

  try {
    const payload = {
      query: query,
      session_id: activeSessionId,
      client_id: activeClientId,
      user_profile: {
        formation: activeUser.formation,
        annee: activeUser.annee,
        name: activeUser.name,
        email: activeUser.email
      },
      source: source
    };

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    removeTypingIndicator(typingId);

    // Render bot response
    appendChatMessage('bot', data.response, data);

    // Speak response if TTS is on
    if (isTTSEnabled) {
      speakText(data.response);
    }

  } catch (err) {
    removeTypingIndicator(typingId);
    appendChatMessage('bot', "⚠️ Impossible de contacter le serveur campus. Vérifiez que l'application est bien en cours d'exécution.");
  }
}

function appendChatMessage(role, text, meta = null) {
  const container = document.getElementById('chat-messages');
  const msgWrapper = document.createElement('div');
  msgWrapper.className = `flex items-start space-x-3 chat-message-anim ${role === 'user' ? 'justify-end' : ''}`;

  if (role === 'user') {
    msgWrapper.innerHTML = `
      <div class="chat-bubble-user text-sm shadow-sm">
        <p class="whitespace-pre-line">${escapeHtml(text)}</p>
      </div>
      <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm shrink-0 border bg-white shadow-sm" style="border-color: var(--esic-gris-clair);">
        ${activeUser.avatar}
      </div>
    `;
  } else if (role === 'system') {
    msgWrapper.innerHTML = `
      <div class="w-full text-center my-2">
        <span class="esic-badge esic-badge-mint text-xs">
          ${text}
        </span>
      </div>
    `;
  } else {
    // Bot message
    const formattedText = formatMarkdown(text);
    const metaBadges = meta ? `
      <div class="mt-2.5 pt-2 border-t flex flex-wrap items-center justify-between gap-1 text-[11px]" style="border-color: var(--esic-gris-clair); color: var(--esic-gris-fonce);">
        <div class="flex items-center space-x-1.5 flex-wrap">
          <span class="px-2 py-0.5 rounded border text-[10px] font-mono" style="background-color: var(--esic-gris-tres-clair); border-color: var(--esic-gris-clair);">Intent: ${meta.intent} (${Math.round(meta.intent_confidence * 100)}%)</span>
          <span class="px-2 py-0.5 rounded border text-[10px] font-mono" style="background-color: var(--esic-gris-tres-clair); border-color: var(--esic-gris-clair);">Latence: ${meta.latency_ms}ms</span>
          ${meta.escalated ? '<span class="esic-badge esic-badge-accent text-[9px]">Escalade Humaine</span>' : ''}
        </div>
        <div class="flex items-center space-x-1">
          <button onclick="rateInteraction(${meta.interaction_id}, 1)" class="p-1 hover:text-emerald-600 text-slate-400 transition" title="Réponse utile 👍">
            <i class="fa-regular fa-thumbs-up"></i>
          </button>
          <button onclick="rateInteraction(${meta.interaction_id}, -1)" class="p-1 hover:text-rose-600 text-slate-400 transition" title="Réponse incorrecte 👎">
            <i class="fa-regular fa-thumbs-down"></i>
          </button>
        </div>
      </div>
    ` : '';

    const suggestionsHtml = (meta && meta.suggestions && meta.suggestions.length > 0) ? `
      <div class="mt-3 flex flex-wrap gap-1.5">
        ${meta.suggestions.map(s => `<button onclick="sendQuickQuery('${escapeQuotes(s)}')" class="quick-pill">${escapeHtml(s)}</button>`).join('')}
      </div>
    ` : '';

    msgWrapper.innerHTML = `
      <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" style="background-color: var(--esic-sombre);">
        <i class="fa-solid fa-graduation-cap"></i>
      </div>
      <div class="chat-bubble-bot text-sm">
        <div class="leading-relaxed">${formattedText}</div>
        ${suggestionsHtml}
        ${metaBadges}
      </div>
    `;
  }

  container.appendChild(msgWrapper);
  container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
  const container = document.getElementById('chat-messages');
  const id = 'typing_' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex items-start space-x-3 chat-message-anim';
  div.innerHTML = `
    <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" style="background-color: var(--esic-sombre);">
      <i class="fa-solid fa-graduation-cap"></i>
    </div>
    <div class="chat-bubble-bot p-3 flex items-center space-x-1.5">
      <div class="w-2 h-2 rounded-full bg-slate-400 animate-pulse"></div>
      <div class="w-2 h-2 rounded-full bg-slate-400 animate-pulse delay-100"></div>
      <div class="w-2 h-2 rounded-full bg-slate-400 animate-pulse delay-200"></div>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function resetConversation() {
  await fetch(`/api/chat/reset/${activeSessionId}`, { method: 'POST' });
  const container = document.getElementById('chat-messages');
  container.innerHTML = `
    <div class="flex items-start space-x-3">
      <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" style="background-color: var(--esic-sombre);">
        <i class="fa-solid fa-graduation-cap"></i>
      </div>
      <div class="chat-bubble-bot">
        <p class="font-bold mb-1" style="color: var(--esic-sombre);">Nouvelle conversation initialisée. Bonjour ! 👋</p>
        <p class="text-sm leading-relaxed" style="color: var(--esic-gris-fonce);">
          Comment puis-je vous aider aujourd'hui ? Posez votre question sur les emplois du temps, scolarité, examens ou démarches.
        </p>
        <div class="mt-3 pt-3 border-t flex flex-wrap gap-2" style="border-color: var(--esic-gris-clair);">
          <button onclick="sendQuickQuery('À quelle heure ouvre la bibliothèque ?')" class="quick-pill">📚 Horaires BU</button>
          <button onclick="sendQuickQuery('Quels sont les horaires de la scolarité ?')" class="quick-pill">🏢 Horaires Scolarité</button>
          <button onclick="sendQuickQuery('Je suis en Data Science 2e année, quand sont mes examens de machine learning ?')" class="quick-pill">📅 Examens Machine Learning DS2</button>
          <button onclick="sendQuickQuery('Où manger le midi ?')" class="quick-pill">🍽️ Resto U ce midi</button>
        </div>
      </div>
    </div>
  `;
}

// ==============================================================================
// Web Speech API : Speech-to-Text & Text-to-Speech
// ==============================================================================
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.lang = 'fr-FR';
    speechRecognizer.interimResults = false;

    speechRecognizer.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('chat-input').value = transcript;
      handleChatSubmit(null);
      stopVoiceInput();
    };

    speechRecognizer.onerror = () => stopVoiceInput();
    speechRecognizer.onend = () => stopVoiceInput();
  }
}

function toggleVoiceInput() {
  if (isRecording) {
    stopVoiceInput();
  } else {
    startVoiceInput();
  }
}

function startVoiceInput() {
  if (!speechRecognizer) {
    alert("La reconnaissance vocale n'est pas prise en charge sur ce navigateur.");
    return;
  }
  isRecording = true;
  document.getElementById('voice-icon').className = 'fa-solid fa-circle-dot text-rose-500 animate-ping';
  speechRecognizer.start();
}

function stopVoiceInput() {
  isRecording = false;
  document.getElementById('voice-icon').className = 'fa-solid fa-microphone text-base';
  if (speechRecognizer) speechRecognizer.stop();
}

function toggleTTS() {
  isTTSEnabled = !isTTSEnabled;
  const icon = document.getElementById('tts-icon');
  if (isTTSEnabled) {
    icon.className = 'fa-solid fa-volume-high text-emerald-400';
    speakText("Lecture vocale activée");
  } else {
    icon.className = 'fa-solid fa-volume-xmark text-slate-300';
    window.speechSynthesis.cancel();
  }
}

function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const clean = text.replace(/[*_#`[\]()]/g, '');
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = 'fr-FR';
  window.speechSynthesis.speak(utterance);
}

// ==============================================================================
// Feedback & Rating Modal (US-024)
// ==============================================================================
function rateInteraction(interactionId, rating) {
  document.getElementById('feedback-interaction-id').value = interactionId || '';
  document.getElementById('feedback-rating-val').value = rating;
  document.getElementById('feedback-comment').value = '';
  document.getElementById('feedback-modal').classList.remove('hidden');
}

function closeFeedbackModal() {
  document.getElementById('feedback-modal').classList.add('hidden');
}

async function submitFeedbackComment() {
  const iid = document.getElementById('feedback-interaction-id').value;
  const rating = parseInt(document.getElementById('feedback-rating-val').value, 10);
  const comment = document.getElementById('feedback-comment').value.trim();

  await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      interaction_id: iid ? parseInt(iid, 10) : null,
      session_id: activeSessionId,
      rating: rating,
      comment: comment
    })
  });

  closeFeedbackModal();
  appendChatMessage('system', "Merci pour votre évaluation ! Vos retours permettent d'enrichir la base.");
}

// ==============================================================================
// Borne IoT Simulation (Sprint 3 - Epic 7)
// ==============================================================================
function setKioskMode(mode) {
  activeKioskMode = mode;
  ['visiteur', 'etudiant', 'vocal'].forEach(m => {
    document.getElementById(`kiosk-content-${m}`).classList.add('hidden');
    document.getElementById(`kiosk-mode-${m}`).classList.remove('active');
  });

  document.getElementById(`kiosk-content-${mode}`).classList.remove('hidden');
  document.getElementById(`kiosk-mode-${mode}`).classList.add('active');

  // Trigger heartbeat to server
  fetch('/api/kiosks/heartbeat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      kiosk_id: "BORNE-01",
      battery: 100,
      mode: mode
    })
  });
}

function toggleAccessibilityMode() {
  document.body.classList.toggle('accessibility-mode');
}

async function kioskAskQuestion(query) {
  const box = document.getElementById('kiosk-dialogue-box');
  box.innerHTML += `<div class="text-blue-300 font-semibold mt-2">👤 Visiteur : ${query}</div>`;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        session_id: 'kiosk_session',
        client_id: 'BORNE-01',
        source: 'borne_iot'
      })
    });
    const data = await res.json();
    box.innerHTML += `<div class="text-emerald-300 mt-1">🤖 Borne ESIC : ${formatMarkdown(data.response)}</div>`;
    box.scrollTop = box.scrollHeight;
    if (isTTSEnabled) speakText(data.response);
  } catch (err) {
    box.innerHTML += `<div class="text-rose-400 mt-1">Erreur de communication avec la borne centrale.</div>`;
  }
}

function kioskShowBuilding(letter) {
  const box = document.getElementById('building-detail-box');
  box.classList.remove('hidden');
  const details = {
    'A': "<strong>Bâtiment A</strong> : Accueil central, Service Scolarité (Sophie Dubois - Bureau 102), Direction pédagogique (Joel Banka - 201), Bureau des Stages (204).",
    'B': "<strong>Bâtiment B</strong> : Laboratoires IA, Laboratoire Réseau & Cloud, Pôle Cybersécurité, Helpdesk IT (B-005), Service Médical (012).",
    'C': "<strong>Bâtiment C</strong> : Bibliothèque Universitaire (BU) sur 2 niveaux, 12 Box de travail insonorisés, FabLab et espace impression 3D.",
    'D': "<strong>Bâtiment D</strong> : Restaurant Universitaire (Resto U 11h30-14h), Cafétéria avec micro-ondes, Foyer des Étudiants et local du BDE."
  };
  box.innerHTML = details[letter] || "Bâtiment campus.";
}

async function kioskScanBadge(cardId) {
  const res = await fetch('/api/kiosks/badge-scan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ card_id: cardId })
  });
  const data = await res.json();
  const st = data.student;

  const resDiv = document.getElementById('badge-scan-result');
  resDiv.classList.remove('hidden');
  resDiv.innerHTML = `
    <div class="flex items-center space-x-3">
      <span class="text-2xl">${st.photo ? '👩‍🎓' : '🧑‍🎓'}</span>
      <div>
        <div class="font-bold text-emerald-800 text-sm">${st.prenom} ${st.nom}</div>
        <div class="text-slate-600 text-[11px]">${st.formation} (${st.annee}) | N° ${st.etudiant_id}</div>
        <div class="text-emerald-700 text-[10px] mt-1 font-semibold">✓ Badge NFC validé • Prochain examen : Machine Learning (15 mars, Amphi B)</div>
      </div>
    </div>
  `;

  kioskAskQuestion(`Je suis ${st.prenom} ${st.nom} en ${st.formation} ${st.annee}, quand sont mes prochains examens ?`);
}

// ==============================================================================
// Analytics & Dashboard (Sprint 2 - Epic 5 - Admin Only)
// ==============================================================================
async function loadRealtimeAnalytics() {
  try {
    const res = await fetch('/api/analytics/realtime');
    const data = await res.json();
    const m = data.metrics;

    // Update KPI cards
    document.getElementById('kpi-total').textContent = m.total_questions_all_time;
    document.getElementById('kpi-resolution').textContent = `${m.resolution_rate_percent}%`;
    document.getElementById('kpi-satisfaction').textContent = `${m.average_satisfaction_stars} / 5`;
    document.getElementById('kpi-latency').textContent = `${m.average_latency_ms} ms`;
    document.getElementById('kpi-hours').textContent = `${m.hours_saved_scolarite} h`;
    document.getElementById('kpi-savings').textContent = `${m.financial_savings_euros} €`;

    // Render Top 10 Questions
    const topTbody = document.getElementById('top-questions-tbody');
    topTbody.innerHTML = '';
    data.top_10_questions.forEach(item => {
      topTbody.innerHTML += `
        <tr>
          <td class="py-2 pr-2 text-slate-800 truncate max-w-xs">${escapeHtml(item.question)}</td>
          <td class="py-2 text-right font-bold" style="color: var(--esic-accent);">${item.count}</td>
        </tr>
      `;
    });

    // Render Continuous Learning
    const recBox = document.getElementById('recommendations-box');
    recBox.innerHTML = '';
    data.continuous_learning_recommendations.forEach(r => {
      recBox.innerHTML += `
        <div class="p-2.5 rounded-xl border" style="background-color: var(--esic-gris-tres-clair); border-color: var(--esic-gris-clair);">
          <div class="flex items-center justify-between font-semibold" style="color: var(--esic-accent-texte);">
            <span>💡 Sujet : ${escapeHtml(r.topic)}</span>
            <span class="esic-badge esic-badge-mint text-[9px]">${r.occurrences} requêtes</span>
          </div>
          <p class="text-[11px] text-slate-600 mt-1">${escapeHtml(r.action)}</p>
        </div>
      `;
    });

    // Render Recent Feedbacks
    const fbBox = document.getElementById('recent-feedbacks-box');
    fbBox.innerHTML = '';
    data.recent_feedback.forEach(f => {
      fbBox.innerHTML += `
        <div class="p-2.5 rounded-xl border" style="background-color: var(--esic-gris-tres-clair); border-color: var(--esic-gris-clair);">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-xs ${f.rating > 0 ? 'text-emerald-700' : 'text-rose-700'}">
              ${f.rating > 0 ? '👍 Satisfait' : '👎 Insatisfait'}
            </span>
            <span class="text-[10px] text-slate-400">${new Date(f.timestamp * 1000).toLocaleTimeString()}</span>
          </div>
          <p class="text-slate-700 text-[11px] mt-1 italic">"${escapeHtml(f.comment)}"</p>
        </div>
      `;
    });

    // Render Charts styled with ESIC DA colors
    renderHourlyChart(data.hourly_trend_last_24h);
    renderCategoryChart(data.category_distribution);

  } catch (err) {
    console.error("Error loading analytics:", err);
  }
}

function renderHourlyChart(hourlyData) {
  const ctx = document.getElementById('chart-hourly').getContext('2d');
  const labels = Array.from({ length: 24 }, (_, i) => `${i}h`);

  if (hourlyChartInstance) hourlyChartInstance.destroy();

  hourlyChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Requêtes étudiantes',
        data: hourlyData,
        borderColor: '#5dbe9c',
        backgroundColor: 'rgba(93, 190, 156, 0.15)',
        pointBackgroundColor: '#07294d',
        fill: true,
        tension: 0.35,
        borderWidth: 2.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
        },
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(7, 41, 77, 0.06)' },
          ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
        }
      }
    }
  });
}

function renderCategoryChart(dist) {
  const ctx = document.getElementById('chart-categories').getContext('2d');
  const labels = Object.keys(dist);
  const data = Object.values(dist);

  if (categoryChartInstance) categoryChartInstance.destroy();

  // Official ESIC palette: Sombre (#07294d), Primaire (#5dbe9c), Secondaire (#48a2db), Accent (#2770ff), Amber (#f2a541)
  const esicColors = [
    '#07294d', '#5dbe9c', '#48a2db', '#2770ff', '#f2a541',
    '#49a988', '#2073a8', '#123aad', '#15795a', '#f59e0b',
    '#8b5cf6', '#06b6d4', '#64748b', '#0d9488', '#e11d48'
  ];

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: esicColors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 10,
            color: '#07294d',
            font: { family: 'Inter', size: 10, weight: '500' }
          }
        }
      }
    }
  });
}

// ==============================================================================
// Knowledge Base Administration (Sprint 1 & Sprint 2 - Epic 6 - Admin Only)
// ==============================================================================
async function loadKnowledgeSummary() {
  try {
    const res = await fetch('/api/knowledge/summary');
    const data = await res.json();

    document.getElementById('kb-schedules-count').textContent = data.schedules_count;
    document.getElementById('kb-procedures-count').textContent = data.procedures_count;
    document.getElementById('kb-contacts-count').textContent = data.contacts_count;
    document.getElementById('kb-faq-count').textContent = data.faq_count;
    document.getElementById('kb-dynamic-count').textContent = data.dynamic_items_count;
  } catch (err) {
    console.error("Error loading knowledge summary:", err);
  }
}

async function handleAddKnowledge(event) {
  event.preventDefault();
  const category = document.getElementById('new-kb-category').value;
  const question = document.getElementById('new-kb-question').value.trim();
  const answer = document.getElementById('new-kb-answer').value.trim();
  const keywords = document.getElementById('new-kb-keywords').value.trim();

  await fetch('/api/knowledge/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, question, answer, keywords })
  });

  alert("Fiche ajoutée avec succès ! Le chatbot est immédiatement à jour.");
  document.getElementById('new-kb-question').value = '';
  document.getElementById('new-kb-answer').value = '';
  document.getElementById('new-kb-keywords').value = '';
  loadKnowledgeSummary();
}

async function loadKiosksFleet() {
  try {
    const res = await fetch('/api/kiosks');
    const data = await res.json();
    const tbody = document.getElementById('kiosks-monitoring-tbody');
    tbody.innerHTML = '';

    data.kiosks.forEach(k => {
      const isOnline = k.status === 'online';
      tbody.innerHTML += `
        <tr>
          <td class="py-2.5 font-mono font-bold" style="color: var(--esic-accent);">${k.id}</td>
          <td class="py-2.5">
            <span class="font-bold block" style="color: var(--esic-sombre);">${escapeHtml(k.name)}</span>
            <span class="text-[10px] text-slate-500">${escapeHtml(k.location)}</span>
          </td>
          <td class="py-2.5">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isOnline ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
              ${k.status.toUpperCase()}
            </span>
          </td>
          <td class="py-2.5 font-semibold text-slate-700">${k.battery_level}%</td>
          <td class="py-2.5 font-bold" style="color: var(--esic-sombre);">${k.interactions_count}</td>
          <td class="py-2.5 text-slate-600 capitalize">${k.active_mode}</td>
          <td class="py-2.5 text-right text-slate-500 font-mono text-[11px]">${new Date(k.last_heartbeat * 1000).toLocaleTimeString()}</td>
        </tr>
      `;
    });
  } catch (err) {
    console.error("Error loading kiosks fleet:", err);
  }
}

// ==============================================================================
// Proactive Notifications & Suggestions (Sprint 8)
// ==============================================================================
async function loadNotifications() {
  try {
    const res = await fetch('/api/notifications');
    const data = await res.json();
    if (data.notifications && data.notifications.length > 0) {
      const first = data.notifications[0];
      document.getElementById('proactive-text').textContent = `${first.title} : ${first.message}`;
    }
  } catch (e) {}
}

async function loadSuggestions() {
  try {
    const res = await fetch('/api/chat/suggestions');
    const data = await res.json();
  } catch (e) {}
}

// ==============================================================================
// RGPD Modal & Data Portability / Deletion
// ==============================================================================
function openRgpdModal() {
  document.getElementById('profile-dropdown').classList.add('hidden');
  document.getElementById('rgpd-modal').classList.remove('hidden');
}

function closeRgpdModal() {
  document.getElementById('rgpd-modal').classList.add('hidden');
}

async function exportMyData() {
  const res = await fetch(`/api/rgpd/export/${activeSessionId}`);
  const data = await res.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `esic_conversations_${activeSessionId}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

async function purgeMyData() {
  if (confirm("Confirmez-vous la suppression définitive de toutes vos interactions (Droit à l'oubli RGPD) ?")) {
    await fetch(`/api/rgpd/delete/${activeSessionId}`, { method: 'DELETE' });
    closeRgpdModal();
    resetConversation();
    alert("Toutes vos données ont été effacées avec succès.");
  }
}

// ==============================================================================
// Utilities
// ==============================================================================
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'");
}

function formatMarkdown(text) {
  if (!text) return '';
  let out = escapeHtml(text);
  // Bold
  out = out.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Lists
  out = out.replace(/\n- /g, '<br>• ');
  // Newlines
  out = out.replace(/\n/g, '<br>');
  return out;
}
