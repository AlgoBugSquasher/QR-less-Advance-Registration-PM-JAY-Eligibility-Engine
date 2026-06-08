/*
Browser-only Voice Assistant (Hindi/Hinglish)

Uses Web Speech API recognition (webkitSpeechRecognition fallback) and browser `speechSynthesis` for TTS.
Features:
- Continuous hi-IN recognition with automatic restart on unexpected stops.
- Hindi/Hinglish TTS with best-available hi-IN voice selection.
- Robust symptom→department matching using bilingual keyword lists.
- Keeps backend `/voice/generate` POST unchanged for token creation.
*/

// Symptom-to-Department Mapping (Hindi + Hinglish keywords)
const SYMPTOM_DATABASE = {
  GEN: {
    name: 'General OPD',
    keywords: [
      'bukhar','fever','sardi','khansi','sardi khansi','cold','cough','kamzori','weakness',
      'pet dard','pet me dard','pet me jalan','pet dard hai','pet','pet ka dard','ulti','vomiting','ulti ho rahi hai',
      'gas','gas ki problem','acid','acidity','infection','checkup','general','opd','tabiyat'
    ]
  },
  CAR: {
    name: 'Cardiology',
    keywords: [
      'dil','dil me dard','dil ka dard','chest pain','chhati me dard','chhati','heart','heart problem','heart pain',
      'bp','blood pressure','blood pressure high','dhadkan','dharkan','palpitation','chest tightness'
    ]
  },
  ORT: {
    name: 'Orthopedics',
    keywords: [
      'ghutna','ghutne','ghutna dard','ghutne me dard','kamar','kamar dard','back pain','kamardard','reedh ki haddi',
      'haddi','haddi dard','fracture','fracture hua','bone','joint pain','joint','sprain','jodon ka dard'
    ]
  },
  PED: {
    name: 'Pediatrics',
    keywords: [
      'baccha','bacha','bache','baby','child','children','infant','newborn','naya janma','vaccine','vaccination',
      'vaccinate','vaccine lagani hai','vaccine lagwani hai','pediatric','bachche ka checkup'
    ]
  },
  NEU: {
    name: 'Neurology',
    keywords: [
      'sar dard','sar','sir dard','sir','sar me dard','migraine','chakkar','chakkar aa rahe hain','dizziness','dimaag',
      'neurology','brain','seizure','chakkar aana'
    ]
  }
};

// Speech synthesis voice management and Hindi speech helper.
let availableVoices = [];
let selectedVoice = null;
let isSpeaking = false;
let manualStop = false; // true when user explicitly stops listening
let suppressAutoRestart = false; // true while intentionally pausing recognition for TTS
let firstLaunch = true;

function updateAvailableVoices() {
  if (!window.speechSynthesis) return;
  availableVoices = window.speechSynthesis.getVoices() || [];
  selectedVoice = chooseBestHindiVoice(availableVoices);
  console.log('[voice] available voices:', availableVoices.map(v => `${v.name} (${v.lang})`));
  console.log('[voice] selected voice:', selectedVoice ? selectedVoice.name : 'none');
}

function chooseBestHindiVoice(voices) {
  if (!voices || !voices.length) return null;
  let v = voices.find(x => (x.lang || '').toLowerCase() === 'hi-in');
  if (v) return v;
  v = voices.find(x => /hindi|हिन्दी|हिंदी/i.test(x.name || ''));
  if (v) return v;
  v = voices.find(x => /india|indian/i.test(x.name || ''));
  if (v) return v;
  v = voices.find(x => (x.lang || '').toLowerCase().startsWith('hi'));
  if (v) return v;
  v = voices.find(x => (x.name || '').toLowerCase().includes('hindi'));
  if (v) return v;
  return voices[0];
}

if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = updateAvailableVoices;
  setTimeout(updateAvailableVoices, 200);
}

function speak(text, options = { restartAfter: true }) {
  if (!window.speechSynthesis) {
    console.warn('No speechSynthesis available');
    return Promise.resolve();
  }

  const wasListening = listening;
  suppressAutoRestart = true;
  if (recognition && listening) {
    try { recognition.abort(); } catch (e) { try { recognition.stop(); } catch (_) {} }
  }

  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'hi-IN';
  utter.rate = 0.9;
  if (selectedVoice) utter.voice = selectedVoice;

  console.log('[voice] speaking (hi-IN):', text, selectedVoice ? selectedVoice.name : '(default)');

  return new Promise((resolve) => {
    isSpeaking = true;
    utter.onend = () => {
      isSpeaking = false;
      suppressAutoRestart = false;
      if (options.restartAfter && wasListening && !manualStop && currentState !== STATE.DONE) {
        setTimeout(() => startRecognition(), 250);
      }
      resolve();
    };

    utter.onerror = (e) => {
      console.error('TTS error', e);
      isSpeaking = false;
      suppressAutoRestart = false;
      if (options.restartAfter && wasListening && !manualStop && currentState !== STATE.DONE) {
        setTimeout(() => startRecognition(), 500);
      }
      resolve();
    };

    window.speechSynthesis.speak(utter);
  });
}

// Match symptoms in transcript against symptom database.
// Returns { dept_code, score, dept_obj } with highest match, or null if no match.
function findDepartmentBySymptoms(transcript) {
  const raw = String(transcript || '').toLowerCase();
  console.log('[voice] raw transcript:', raw);

  let best = { code: 'GEN', score: 0, matched: [] };

  for (const [code, info] of Object.entries(SYMPTOM_DATABASE)) {
    let score = 0;
    const matched = [];
    for (const kw of info.keywords) {
      if (!kw) continue;
      if (raw.includes(kw)) {
        score++;
        matched.push(kw);
      }
    }
    if (score > best.score) {
      best = { code, score, matched };
    }
  }

  const dept = AVAILABLE_DEPARTMENTS.find(d => d.dept_code === best.code) || { dept_code: best.code, name: SYMPTOM_DATABASE[best.code].name };
  console.log('[voice] matched keywords:', best.matched.join(', '));
  console.log('[voice] selected department:', dept.name, dept.dept_code);
  return { dept_code: dept.dept_code || best.code, score: best.score, dept_obj: dept, matched: best.matched };
}

// State Machine States
const STATE = {
  GREETING: 'greeting',
  LISTENING_SYMPTOM: 'listening_symptom',
  DEPT_IDENTIFIED: 'dept_identified',
  CONFIRMING: 'confirming',
  GENERATING: 'generating',
  DONE: 'done'
};

// Speech recognition setup (continuous hi-IN)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let listening = false;
let currentState = STATE.GREETING;
let identifiedDept = null;
let isRestarting = false;
let lastTranscript = '—';

const micBtn = document.getElementById('micBtn');
const listeningIndicator = document.getElementById('listeningIndicator');
const transcriptEl = document.getElementById('transcript');
const resultArea = document.getElementById('resultArea');
const repeatBtn = document.getElementById('repeatBtn');
const cancelBtn = document.getElementById('cancelBtn');
const homeBtn = document.getElementById('homeBtn');
const langSelect = document.getElementById('langSelect');

function updateListeningState(state) {
  listening = state;
  listeningIndicator.textContent = state ? 'Listening...' : 'Not listening';
  micBtn.textContent = state ? '⏹️ Stop' : '🎤 Start';
}

function startRecognition() {
  if (!SpeechRecognition) {
    speak('Yeh browser speech recognition support nahi karta.');
    return;
  }

  if (recognition && listening) return;

  recognition = new SpeechRecognition();
  recognition.lang = 'hi-IN';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.continuous = true;

  recognition.onstart = () => {
    updateListeningState(true);
    manualStop = false;
  };

  recognition.onresult = (event) => {
    let text = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      text += event.results[i][0].transcript;
    }
    text = text.trim();
    if (!text) return;
    lastTranscript = text;
    transcriptEl.textContent = text;
    console.log('[voice] onresult:', text);
    processVoiceInput(text);
  };

  recognition.onerror = (e) => {
    console.error('SpeechRecognition error', e);
    speak('Kuchh samasya hui. Kripya dobara bolen.');
  };

  recognition.onend = () => {
    updateListeningState(false);
    recognition = null;
    if (!manualStop && !suppressAutoRestart && currentState !== STATE.DONE) {
      console.log('[voice] recognition ended unexpectedly — restarting');
      setTimeout(() => startRecognition(), 400);
    }
  };

  try { recognition.start(); } catch (e) { console.error('startRecognition failed', e); }
}

function stopRecognition() {
  if (recognition) {
    try { recognition.abort(); } catch (e) { try { recognition.stop(); } catch (_) {} }
    recognition = null;
  }
  updateListeningState(false);
}

// Process voice input based on current state in the conversation.
function processVoiceInput(text) {
  const t = String(text || '').toLowerCase();

  if (currentState === STATE.GREETING || currentState === STATE.LISTENING_SYMPTOM) {
    const match = findDepartmentBySymptoms(t);
    identifiedDept = match.dept_obj;

    const deptName = identifiedDept ? identifiedDept.name : 'General OPD';
    const msg = match.score > 0
      ? `Aapke lakshanon ke aadhar par ${deptName} suggest kiya gaya hai. Kya main aapka token generate kar doon?`
      : `Main aapki department pehchaan nahi kar paya. Aapko General OPD assign kiya gaya hai. Kya main aapka token generate kar doon?`;

    resultArea.innerHTML = `<div class="token-card">${msg}</div>`;
    currentState = STATE.CONFIRMING;
    speak(msg);
    return;
  }

  if (currentState === STATE.CONFIRMING) {
    const yesKeywords = ['haan','haa','bilkul','theek','ठीक','haan ji','ha','yes'];
    const noKeywords = ['nahi','na','nahin','nah'];
    const shouldGenerate = yesKeywords.some(k => t.includes(k));
    const shouldCancel = noKeywords.some(k => t.includes(k));

    if (shouldGenerate) {
      generateTokenViaAPI();
      return;
    }
    if (shouldCancel) {
      const msg = 'Prakriya radd kar di gayi.';
      resultArea.innerHTML = `<div class="error">${msg}</div>`;
      speak(msg, { restartAfter: false });
      resetVoiceFlow();
      manualStop = true;
      return;
    }

    speak('Kripya haan ya na mein jawab dein.');
    return;
  }
}

// Call backend API to generate token for the identified department.
async function generateTokenViaAPI() {
  if (!identifiedDept) {
    speak('Kuchh gadbad hui. Kripya dobara koshish karein.');
    return;
  }

  currentState = STATE.GENERATING;
  speak('Aapka token generate kiya ja raha hai.', { restartAfter: true });

  try {
    const res = await fetch('/voice/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dept_code: identifiedDept.dept_code,
        dept_name: identifiedDept.name
      })
    });

    const data = await res.json();
    if (res.ok && data.token) {
      const token = data.token;
      const speakText = `Aapka token ${token.token_number} generate ho gaya hai. Kripya apni baari ka intezar karein.`;
      resultArea.innerHTML = `\n        <div class=\"token-card\">\n          <div style=\"font-size: 1.5rem; font-weight: bold;\">Token: ${token.token_number}</div>\n          <div style=\"margin-top: 8px;\">${speakText}</div>\n        </div>\n      `;
      speak(speakText, { restartAfter: false });
      currentState = STATE.DONE;
      manualStop = true;
    } else {
      const err = data.error || 'Token create nahi ho paya.';
      resultArea.innerHTML = `<div class=\"error\">${err}</div>`;
      speak(err);
      resetVoiceFlow();
    }
  } catch (e) {
    console.error(e);
    const msg = 'Server mein kuchh gadbad hui. Kripya dobara koshish karein.';
    resultArea.innerHTML = `<div class=\"error\">${msg}</div>`;
    speak(msg);
    resetVoiceFlow();
  }
}

// Reset conversation flow to initial state.
function resetVoiceFlow() {
  currentState = STATE.GREETING;
  identifiedDept = null;
  transcriptEl.textContent = '—';
  resultArea.innerHTML = '';
  stopRecognition();
}

// Event listeners for buttons
micBtn.addEventListener('click', async () => {
  try {
    if (firstLaunch) {
      console.log('[voice] greeting started');
      // Speak greeting and wait until finished, then start recognition
      await speak('Namaste. Aapko kya takleef hai? Kripya apni samasya batayein.');
      console.log('[voice] greeting finished');
      // After greeting finished, start recognition
      console.log('[voice] recognition started');
      startRecognition();
      firstLaunch = false;
      currentState = STATE.LISTENING_SYMPTOM;
      return;
    }

    // Subsequent clicks: toggle listening
    if (listening) {
      manualStop = true;
      stopRecognition();
      return;
    } else {
      manualStop = false;
      startRecognition();
      return;
    }
  } catch (e) {
    console.error('micBtn handler error', e);
  }
});

repeatBtn.addEventListener('click', () => {
  const text = lastTranscript || transcriptEl.textContent || '';
  if (text && text !== '—') speak(`Aapne kaha: ${text}`);
});

cancelBtn.addEventListener('click', () => {
  manualStop = true;
  stopRecognition();
  resetVoiceFlow();
  speak('Prakriya radd kar di gayi.', { restartAfter: false });
});

homeBtn.addEventListener('click', () => {
  window.location.href = '/';
});

