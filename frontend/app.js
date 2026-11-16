/**
 * ESIC Campus Connected Assistant - Frontend Single Page Application
 * Handles Chatbot, 21" IoT Kiosk Simulation, Real-time Analytics, Admin KB, and ENT SSO.
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

// Mock Personas
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
    description: "Persona Principal : 20 ans, Data Science 2"
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
    description: "Persona Secondaire : 23 ans, International (EN/ES)"
  },
  sophie_dubois: {
    id: "sophie_dubois",
    name: "Sophie Dubois",
    role: "Responsable Scolarité",
    formation: "Personnel Administratif",
    annee: "Staff",
    student_id: "STAFF-ESIC-007",
    email: "sophie.dubois@esic.fr",
    avatar: "👩‍💼",
    description: "Persona Tertiaire : 42 ans, Responsable Scolarité"
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
    description: "Persona Quaternaire : 18 ans, lycéen"
  }
};

let activeUser = PERSONAS.emma_rousseau;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  setupSpeechRecognition();
  updateProfileUI();
  loadSuggestions();
  loadNotifications();
  // Preload initial analytics and knowledge base stats
  loadRealtimeAnalytics();
  loadKnowledgeSummary();
  loadKiosksFleet();
});

// ==============================================================================
// Tab Navigation
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
      navBtn.classList.remove('text-slate-300');
    } else {
      view.classList.add('hidden');
      navBtn.classList.remove('active-tab');
      navBtn.classList.add('text-slate-300');
    }
  });

  if (tabName === 'analytics') {
    loadRealtimeAnalytics();
  } else if (tabName === 'admin') {
    loadKnowledgeSummary();
    loadKiosksFleet();
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
    updateProfileUI();
    document.getElementById('profile-dropdown').classList.add('hidden');
    // Notify chatbot user profile updated
    appendChatMessage('system', `Profil actif changé : <strong>${activeUser.name}</strong> (${activeUser.role} - ${activeUser.formation})`);
  }
}

function updateProfileUI() {
  document.getElementById('active-avatar').textContent = activeUser.avatar;
  document.getElementById('active-name').textContent = activeUser.name;
  document.getElementById('active-role').textContent = `${activeUser.formation} (${activeUser.annee})`;
  
  // Update ENT tab widgets
  document.getElementById('ent-avatar').textContent = activeUser.avatar;
  document.getElementById('ent-name').textContent = activeUser.name;
  document.getElementById('ent-subtitle').textContent = `${activeUser.role} - ${activeUser.formation} | N° ${activeUser.student_id}`;
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
      <div class="bg-blue-600 text-white p-3.5 rounded-2xl rounded-tr-none max-w-xl text-sm shadow">
        <p class="whitespace-pre-line">${escapeHtml(text)}</p>
      </div>
      <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm shrink-0">
        ${activeUser.avatar}
      </div>
    `;
  } else if (role === 'system') {
    msgWrapper.innerHTML = `
      <div class="w-full text-center my-2">
        <span class="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-400 rounded-full text-xs">
          ${text}
        </span>
      </div>
    `;
  } else {
    // Bot message
    const formattedText = formatMarkdown(text);
    const metaBadges = meta ? `
      <div class="mt-2 pt-2 border-t border-slate-700/60 flex items-center justify-between text-[10px] text-slate-400">
        <div class="flex items-center space-x-2">
          <span class="bg-slate-800 px-2 py-0.5 rounded border border-slate-700 font-mono">Intent: ${meta.intent} (${Math.round(meta.intent_confidence * 100)}%)</span>
          <span class="bg-slate-800 px-2 py-0.5 rounded border border-slate-700 font-mono">Latence: ${meta.latency_ms}ms</span>
          ${meta.escalated ? '<span class="bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30 font-bold">Escalade Humaine</span>' : ''}
        </div>
        <div class="flex items-center space-x-1">
          <button onclick="rateInteraction(${meta.interaction_id}, 1)" class="p-1 hover:text-emerald-400 text-slate-400 transition" title="Réponse utile 👍">
            <i class="fa-regular fa-thumbs-up"></i>
          </button>
          <button onclick="rateInteraction(${meta.interaction_id}, -1)" class="p-1 hover:text-rose-400 text-slate-400 transition" title="Réponse incorrecte 👎">
            <i class="fa-regular fa-thumbs-down"></i>
          </button>
        </div>
      </div>
    ` : '';

    const suggestionsHtml = (meta && meta.suggestions && meta.suggestions.length > 0) ? `
      <div class="mt-2.5 flex flex-wrap gap-1">
        ${meta.suggestions.map(s => `<button onclick="sendQuickQuery('${escapeQuotes(s)}')" class="quick-pill">${escapeHtml(s)}</button>`).join('')}
      </div>
    ` : '';

    msgWrapper.innerHTML = `
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm shrink-0">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="bg-slate-750 text-slate-200 p-4 rounded-2xl rounded-tl-none max-w-xl border border-slate-700 shadow-md text-sm">
        <div class="leading-relaxed prose prose-invert">${formattedText}</div>
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
  const typingDiv = document.createElement('div');
  typingDiv.id = id;
  typingDiv.className = 'flex items-center space-x-2 text-slate-400 text-xs px-2 py-1';
  typingDiv.innerHTML = `
    <div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
    <div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse" style="animation-delay: 0.2s"></div>
    <div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse" style="animation-delay: 0.4s"></div>
    <span class="ml-1 text-[11px] text-slate-400">Recherche dans la base campus...</span>
  `;
  container.appendChild(typingDiv);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

async function resetConversation() {
  await fetch(`/api/chat/reset/${activeSessionId}`, { method: 'POST' });
  activeSessionId = 'session_' + Math.random().toString(36).substring(2, 9);
  const container = document.getElementById('chat-messages');
  container.innerHTML = '';
  appendChatMessage('system', 'Conversation réinitialisée.');
  appendChatMessage('bot', "Bonjour ! Comment puis-je vous aider aujourd'hui ?");
}

// ==============================================================================
// Voice Speech-to-Text & Text-to-Speech (US-029)
// ==============================================================================
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = 'fr-FR';

    speechRecognizer.onstart = () => {
      isRecording = true;
      document.getElementById('voice-btn').classList.add('bg-rose-600', 'text-white', 'animate-pulse');
      document.getElementById('voice-icon').className = 'fa-solid fa-microphone-lines text-base';
    };

    speechRecognizer.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById('chat-input').value = transcript;
      sendQuery(transcript, currentTab === 'kiosk' ? 'borne_iot' : 'web');
    };

    speechRecognizer.onend = () => {
      isRecording = false;
      document.getElementById('voice-btn').classList.remove('bg-rose-600', 'text-white', 'animate-pulse');
      document.getElementById('voice-icon').className = 'fa-solid fa-microphone text-base';
    };

    speechRecognizer.onerror = (e) => {
      console.warn("Speech recognition error:", e);
      isRecording = false;
    };
  } else {
    console.info("Web Speech API not supported in this browser.");
  }
}

function toggleVoiceInput() {
  if (!speechRecognizer) {
    alert("La reconnaissance vocale Web Speech API n'est pas supportée sur ce navigateur.");
    return;
  }
  if (isRecording) {
    speechRecognizer.stop();
  } else {
    speechRecognizer.start();
  }
}

function toggleTTS() {
  isTTSEnabled = !isTTSEnabled;
  const icon = document.getElementById('tts-icon');
  const btn = document.getElementById('tts-toggle-btn');
  if (isTTSEnabled) {
    icon.className = 'fa-solid fa-volume-high text-cyan-400';
    btn.classList.add('bg-cyan-500/20');
  } else {
    icon.className = 'fa-solid fa-volume-xmark';
    btn.classList.remove('bg-cyan-500/20');
    window.speechSynthesis?.cancel();
  }
}

function speakText(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  // Strip markdown symbols for clean speech
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
        <div class="font-bold text-emerald-400 text-sm">${st.prenom} ${st.nom}</div>
        <div class="text-slate-300 text-[11px]">${st.formation} (${st.annee}) | N° ${st.etudiant_id}</div>
        <div class="text-slate-400 text-[10px] mt-1">Badge NFC validé • Prochain examen : Machine Learning (15 mars, Amphi B)</div>
      </div>
    </div>
  `;

  kioskAskQuestion(`Je suis ${st.prenom} ${st.nom} en ${st.formation} ${st.annee}, quand sont mes prochains examens ?`);
}

// ==============================================================================
// Analytics & Dashboard (Sprint 2 - Epic 5)
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
          <td class="py-2 pr-2 text-slate-200 truncate max-w-xs">${escapeHtml(item.question)}</td>
          <td class="py-2 text-right font-bold text-blue-400">${item.count}</td>
        </tr>
      `;
    });

    // Render Continuous Learning
    const recBox = document.getElementById('recommendations-box');
    recBox.innerHTML = '';
    data.continuous_learning_recommendations.forEach(r => {
      recBox.innerHTML += `
        <div class="p-2.5 bg-slate-750 rounded-xl border border-slate-700">
          <div class="flex items-center justify-between font-semibold text-purple-300">
            <span>💡 Sujet : ${escapeHtml(r.topic)}</span>
            <span class="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded">${r.occurrences} requêtes</span>
          </div>
          <p class="text-[11px] text-slate-300 mt-1">${escapeHtml(r.action)}</p>
        </div>
      `;
    });

    // Render Recent Feedbacks
    const fbBox = document.getElementById('recent-feedbacks-box');
    fbBox.innerHTML = '';
    data.recent_feedback.forEach(f => {
      fbBox.innerHTML += `
        <div class="p-2.5 bg-slate-750 rounded-xl border border-slate-700">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-xs ${f.rating > 0 ? 'text-emerald-400' : 'text-rose-400'}">
              ${f.rating > 0 ? '👍 Satisfait' : '👎 Insatisfait'}
            </span>
            <span class="text-[10px] text-slate-400">${new Date(f.timestamp * 1000).toLocaleTimeString()}</span>
          </div>
          <p class="text-slate-300 text-[11px] mt-1 italic">"${escapeHtml(f.comment)}"</p>
        </div>
      `;
    });

    // Render Charts
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
        label: 'Requêtes reçues',
        data: hourlyData,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        fill: true,
        tension: 0.35,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' }, beginAtZero: true }
      }
    }
  });
}

function renderCategoryChart(catData) {
  const ctx = document.getElementById('chart-categories').getContext('2d');
  const labels = Object.keys(catData);
  const values = Object.values(catData);

  if (categoryChartInstance) categoryChartInstance.destroy();

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: [
          '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899',
          '#8b5cf6', '#6366f1', '#14b8a6', '#f97316', '#64748b'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: '#cbd5e1', font: { size: 10 } } }
      }
    }
  });
}

// ==============================================================================
// Admin & Knowledge Base Management (US-025, US-026, US-031)
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
  const keywords = document.getElementById('new-kb-keywords').value;
  const question = document.getElementById('new-kb-question').value;
  const answer = document.getElementById('new-kb-answer').value;

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
          <td class="py-2.5 font-mono text-cyan-400 font-bold">${k.id}</td>
          <td class="py-2.5">
            <span class="font-semibold text-white block">${escapeHtml(k.name)}</span>
            <span class="text-[10px] text-slate-400">${escapeHtml(k.location)}</span>
          </td>
          <td class="py-2.5">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${isOnline ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}">
              ${k.status.toUpperCase()}
            </span>
          </td>
          <td class="py-2.5 font-semibold text-slate-300">${k.battery_level}%</td>
          <td class="py-2.5 font-bold text-blue-400">${k.interactions_count}</td>
          <td class="py-2.5 text-slate-300 capitalize">${k.active_mode}</td>
          <td class="py-2.5 text-right text-slate-400 font-mono text-[11px]">${new Date(k.last_heartbeat * 1000).toLocaleTimeString()}</td>
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
    // Already pre-rendered in HTML
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
