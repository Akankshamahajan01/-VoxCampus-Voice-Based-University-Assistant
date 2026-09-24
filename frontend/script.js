/* ═══════════════════════════════════════════════════════════
   VoxCampus — script.js
   Handles: Voice recording, Text queries, Auth, TTS playback
═══════════════════════════════════════════════════════════ */

const API = window.location.origin;

// ── State ──────────────────────────────────────────────────
let mediaRecorder = null;
let audioChunks   = [];
let isRecording   = false;
let ttsEnabled    = true;
let currentUser   = null;

// ── DOM helpers ────────────────────────────────────────────
const $  = (id) => document.getElementById(id);
const on = (id, ev, fn) => { const el = $(id); if (el) el.addEventListener(ev, fn); };

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  restoreSession();
  setupMicButton();
  setupTextInput();
  setupCategoryPills();
  updateTTSButton();
});

// ══════════════════════════════════════════════════════════
// SESSION / AUTH
// ══════════════════════════════════════════════════════════
function restoreSession() {
  const token = localStorage.getItem('voxcampus_token');
  const user  = localStorage.getItem('voxcampus_user');
  if (token && user) {
    currentUser = JSON.parse(user);
    updateNavForUser();
  }
}

function updateNavForUser() {
  const navLogin = $('nav-login');
  const navUser  = $('nav-user');
  const navName  = $('nav-username');
  if (!navLogin) return;
  if (currentUser) {
    navLogin.classList.add('hidden');
    if (navUser)  navUser.classList.remove('hidden');
    if (navName)  navName.textContent = `Hi, ${currentUser.name.split(' ')[0]} 👋`;
    on('logout-btn', 'click', logout);
  } else {
    navLogin.classList.remove('hidden');
    if (navUser) navUser.classList.add('hidden');
  }
}

function logout() {
  localStorage.removeItem('voxcampus_token');
  localStorage.removeItem('voxcampus_user');
  currentUser = null;
  updateNavForUser();
  window.location.href = '/auth';
}

function continueAsGuest() {
  window.location.href = '/';
}

// ── Auth page ──────────────────────────────────────────────
function switchTab(tab) {
  const loginForm = $('login-form');
  const regForm   = $('register-form');
  const tabLogin  = $('tab-login');
  const tabReg    = $('tab-register');
  if (!loginForm) return;

  clearAuthMessage();
  if (tab === 'login') {
    loginForm.classList.remove('hidden');
    regForm.classList.add('hidden');
    tabLogin.classList.add('active');
    tabReg.classList.remove('active');
  } else {
    regForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    tabReg.classList.add('active');
    tabLogin.classList.remove('active');
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const email    = $('login-email').value.trim();
  const password = $('login-password').value;
  const btn      = $('login-btn');

  setButtonLoading(btn, true, 'Logging in...');
  clearAuthMessage();

  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    localStorage.setItem('voxcampus_token', data.access_token);
    localStorage.setItem('voxcampus_user', JSON.stringify(data.user));
    showAuthMessage('Login successful! Redirecting...', 'success');
    setTimeout(() => window.location.href = '/', 1000);
  } catch (err) {
    showAuthMessage(err.message, 'error');
  } finally {
    setButtonLoading(btn, false, 'Login');
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name     = $('reg-name').value.trim();
  const email    = $('reg-email').value.trim();
  const password = $('reg-password').value;
  const btn      = $('register-btn');

  if (password.length < 6) {
    showAuthMessage('Password must be at least 6 characters', 'error');
    return;
  }

  setButtonLoading(btn, true, 'Creating account...');
  clearAuthMessage();

  try {
    const res = await fetch(`${API}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');

    localStorage.setItem('voxcampus_token', data.access_token);
    localStorage.setItem('voxcampus_user', JSON.stringify(data.user));
    showAuthMessage('Account created! Redirecting...', 'success');
    setTimeout(() => window.location.href = '/', 1000);
  } catch (err) {
    showAuthMessage(err.message, 'error');
  } finally {
    setButtonLoading(btn, false, 'Create Account');
  }
}

function showAuthMessage(msg, type) {
  const el = $('auth-message');
  if (!el) return;
  el.textContent = msg;
  el.className = `auth-message ${type}`;
  el.classList.remove('hidden');
}

function clearAuthMessage() {
  const el = $('auth-message');
  if (el) el.classList.add('hidden');
}

function togglePassword(inputId, btn) {
  const input = $(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈';
  } else {
    input.type = 'password';
    btn.textContent = '👁️';
  }
}

// ══════════════════════════════════════════════════════════
// VOICE RECORDING
// ══════════════════════════════════════════════════════════
function setupMicButton() {
  const btn = $('mic-btn');
  if (!btn) return;

  // Press and hold to record
  btn.addEventListener('mousedown',  startRecording);
  btn.addEventListener('mouseup',    stopRecording);
  btn.addEventListener('mouseleave', stopRecording);

  // Touch support
  btn.addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
  btn.addEventListener('touchend',   (e) => { e.preventDefault(); stopRecording(); });
}

async function startRecording() {
  if (isRecording) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks  = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: getSupportedMimeType() });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };
    mediaRecorder.onstop = handleAudioStop;
    mediaRecorder.start(100);

    isRecording = true;
    setRecordingUI(true);
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      appendMessage('bot', '⚠️ Microphone access denied. Please allow microphone access in your browser settings.', 'system');
    } else {
      appendMessage('bot', `⚠️ Could not start recording: ${err.message}`, 'system');
    }
  }
}

function stopRecording() {
  if (!isRecording || !mediaRecorder) return;
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach(t => t.stop());
  isRecording = false;
  setRecordingUI(false);
}

async function handleAudioStop() {
  if (audioChunks.length === 0) return;

  const blob = new Blob(audioChunks, { type: getSupportedMimeType() });
  if (blob.size < 1000) {
    appendMessage('bot', '⚠️ Recording too short. Please hold the mic button and speak clearly.', 'system');
    return;
  }

  showTyping(true);

  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');
  formData.append('enable_tts', ttsEnabled.toString());
  if (currentUser) formData.append('user_id', currentUser.id);

  try {
    const res = await fetch(`${API}/api/voice/query`, {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    showTyping(false);

    if (!res.ok) {
      appendMessage('bot', `⚠️ ${data.detail || 'Voice query failed. Please try again.'}`, 'error');
      return;
    }

    // Show transcribed text as user message
    if (data.transcribed_text) {
      appendMessage('user', `🎙️ ${data.transcribed_text}`);
    }

    // Show AI response
    appendMessage('bot', data.response_text, data.category, data.audio_base64);

    // Auto-play TTS
    if (ttsEnabled && data.audio_base64) {
      playAudio(data.audio_base64);
    }

    hideWelcome();

  } catch (err) {
    showTyping(false);
    appendMessage('bot', `⚠️ Network error: ${err.message}`, 'error');
  }
}

function getSupportedMimeType() {
  const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg', 'audio/mp4'];
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) return type;
  }
  return 'audio/webm';
}

function setRecordingUI(recording) {
  const btn       = $('mic-btn');
  const statusBar = $('voice-status-bar');
  const heroOrb   = $('hero-orb');

  if (btn) btn.classList.toggle('recording', recording);
  if (statusBar) statusBar.classList.toggle('active', recording);
  if (heroOrb)   heroOrb.classList.toggle('listening', recording);
}

// ══════════════════════════════════════════════════════════
// TEXT QUERY
// ══════════════════════════════════════════════════════════
function setupTextInput() {
  const input = $('text-input');
  if (!input) return;
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTextQuery();
    }
  });
}

async function sendTextQuery() {
  const input = $('text-input');
  if (!input) return;
  const query = input.value.trim();
  if (!query) return;

  input.value = '';
  appendMessage('user', query);
  hideWelcome();
  showTyping(true);

  try {
    const params = new URLSearchParams({ enable_tts: ttsEnabled });
    if (currentUser) params.append('user_id', currentUser.id);

    const res = await fetch(`${API}/api/chat/query?${params}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    showTyping(false);

    if (!res.ok) {
      appendMessage('bot', `⚠️ ${data.detail || 'Query failed. Please try again.'}`, 'error');
      return;
    }

    appendMessage('bot', data.response_text, data.category, data.audio_base64);

    if (ttsEnabled && data.audio_base64) {
      playAudio(data.audio_base64);
    }

  } catch (err) {
    showTyping(false);
    appendMessage('bot', `⚠️ Network error: ${err.message}`, 'error');
  }
}

function useChip(el) {
  const input = $('text-input');
  if (input) {
    input.value = el.textContent;
    sendTextQuery();
  }
}

// ══════════════════════════════════════════════════════════
// CATEGORY PILLS
// ══════════════════════════════════════════════════════════
function setupCategoryPills() {
  document.querySelectorAll('.cat-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const cat = pill.dataset.cat;
      if (cat !== 'all') {
        const questions = {
          courses:    'What courses and programs are available at the university?',
          admissions: 'How do I apply for admission? What are the requirements?',
          fees:       'What is the fee structure for different programs?',
          exams:      'When are the exam schedules and how does the grading work?',
          faculty:    'Tell me about the faculty and departments at the university.'
        };
        if (questions[cat]) {
          const input = $('text-input');
          if (input) input.value = questions[cat];
        }
      }
    });
  });
}

// ══════════════════════════════════════════════════════════
// CHAT UI
// ══════════════════════════════════════════════════════════
function appendMessage(role, text, category = null, audioB64 = null) {
  const messages = $('messages');
  if (!messages) return;

  const wrap = document.createElement('div');
  wrap.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user' ? '👤' : '🎙️';

  const body = document.createElement('div');
  body.className = 'msg-body';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = formatMessage(text);

  const meta = document.createElement('div');
  meta.className = 'msg-meta';
  meta.textContent = formatTime(new Date());

  if (category && role === 'bot') {
    const catTag = document.createElement('span');
    catTag.className = 'msg-category';
    catTag.textContent = category;
    meta.appendChild(catTag);
  }

  // Play TTS button for bot messages with audio
  if (role === 'bot' && audioB64) {
    const playBtn = document.createElement('button');
    playBtn.className = 'play-tts-btn';
    playBtn.title = 'Play voice response';
    playBtn.textContent = '🔊';
    playBtn.onclick = () => playAudio(audioB64);
    meta.appendChild(playBtn);
  }

  body.appendChild(bubble);
  body.appendChild(meta);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  messages.appendChild(wrap);

  scrollToBottom();
}

function formatMessage(text) {
  // Convert markdown-ish to HTML for display
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/•\s/g, '• ')
    .replace(/\n/g, '<br/>');
}

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showTyping(show) {
  const el = $('typing-indicator');
  if (!el) return;
  el.classList.toggle('hidden', !show);
  if (show) scrollToBottom();
}

function scrollToBottom() {
  const win = $('chat-window');
  if (win) win.scrollTop = win.scrollHeight;
}

function hideWelcome() {
  const welcome = document.querySelector('.chat-welcome');
  if (welcome) welcome.style.display = 'none';
}

function scrollToAssistant() {
  const el = $('assistant');
  if (el) el.scrollIntoView({ behavior: 'smooth' });
}

// ══════════════════════════════════════════════════════════
// TTS PLAYBACK
// ══════════════════════════════════════════════════════════
function playAudio(base64) {
  const audio = $('tts-audio');
  if (!audio) return;
  try {
    audio.src = `data:audio/wav;base64,${base64}`;
    audio.play().catch(e => console.warn('Audio play failed:', e));
  } catch (e) {
    console.warn('TTS playback error:', e);
  }
}

function toggleTTS() {
  ttsEnabled = !ttsEnabled;
  updateTTSButton();
}

function updateTTSButton() {
  const btn = $('tts-toggle');
  if (!btn) return;
  btn.textContent = ttsEnabled ? '🔊' : '🔇';
  btn.title = ttsEnabled ? 'Voice response ON (click to mute)' : 'Voice response OFF (click to unmute)';
  btn.classList.toggle('active', ttsEnabled);
}

// ══════════════════════════════════════════════════════════
// UTILITY
// ══════════════════════════════════════════════════════════
function setButtonLoading(btn, loading, text) {
  if (!btn) return;
  btn.disabled = loading;
  btn.querySelector('span') ? btn.querySelector('span').textContent = text : (btn.textContent = text);
}


// ══════════════════════════════════════════════════════════
// ABOUT SECTION — Tabs + Animated Counters
// ══════════════════════════════════════════════════════════

function switchAboutTab(tabId, btn) {
  // Deactivate all tabs and panels
  document.querySelectorAll('.about-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.about-panel').forEach(p => p.classList.remove('active'));

  // Activate selected
  btn.classList.add('active');
  const panel = document.getElementById('tab-' + tabId);
  if (panel) panel.classList.add('active');
}

// Animated counter — counts up from 0 to target value
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const duration = 1200;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// Trigger counters when about section scrolls into view
function setupCounterObserver() {
  const counters = document.querySelectorAll('.astat-num');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && entry.target.textContent === '0') {
        animateCounter(entry.target);
      }
    });
  }, { threshold: 0.4 });

  counters.forEach(c => observer.observe(c));
}

document.addEventListener('DOMContentLoaded', () => {
  setupCounterObserver();
});
