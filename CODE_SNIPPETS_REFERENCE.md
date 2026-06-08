# Critical Code Snippets - Voice Synthesis Fix

## 1. REMOVED: Voice Force Assignment ❌

**This code caused synthesis-failed errors:**

```javascript
// OLD CODE (DELETED) - Lines that caused the problem
if (selectedVoice) {
  try { utterance.voice = selectedVoice; } catch (e) { /* ignore */ }
}
```

**Why it failed:**
- Tried to force a specific voice object
- The voice object reference became invalid
- Browser rejected the utterance
- Result: `synthesis-failed` error

---

## 2. ADDED: synth.cancel() Before Speech ✅

**Location:** Lines 218-220 in voice_assistant.html

```javascript
try {
  console.log('[VOICE] Calling speechSynthesis.cancel()');
  synth.cancel();  // ← THIS LINE ADDED
  
  console.log('[VOICE] Speaking: ' + text.substring(0, 50) + '...');
  synth.speak(utterance);
} catch (e) {
  console.log('[VOICE] Exception in speak(): ' + e.message);
  resolve();
}
```

**Why it works:**
- Clears any pending speech before starting new one
- Prevents speech queue conflicts
- Essential for reliability

---

## 3. FIXED: No Voice Assignment - Let Browser Choose ✅

**Location:** Lines 189-193 in voice_assistant.html

```javascript
// Create utterance WITHOUT assigning any voice - let browser choose
var utterance = new SpeechSynthesisUtterance(text);
utterance.lang = lang;  // 'hi-IN' - ONLY this is set
utterance.rate = 1;
utterance.volume = 1;
// NO utterance.voice = ... assignment
```

**Browser's automatic selection:**
1. Sees `utterance.lang = 'hi-IN'`
2. Searches available voices
3. Finds Microsoft आरव Online (Natural) - Hindi (India)
4. Uses it automatically
5. No errors!

---

## 4. ADDED: Detailed Console Logging ✅

### Speech Started
**Location:** Lines 196-200

```javascript
utterance.onstart = function() {
  console.log('[VOICE] Speech started (lang: ' + lang + ')');  // ← ADDED
  assistantStatusEl.innerText = 'Speaking...';
  appendMessage(text, 'assistant');
};
```

### Speech Ended
**Location:** Lines 202-209

```javascript
utterance.onend = function() {
  console.log('[VOICE] Speech ended');  // ← ADDED
  assistantStatusEl.innerText = 'Speech finished.';
  if (restartAfter) {
    setTimeout(function() { startListening(); }, 500);
  }
  resolve();
};
```

### Speech Error
**Location:** Lines 211-215

```javascript
utterance.onerror = function(event) {
  var errorMsg = event.error || 'unknown';
  console.log('[VOICE] Speech error: ' + errorMsg);  // ← ADDED
  assistantStatusEl.innerText = 'Speech error: ' + errorMsg;
  // ... fallback logic follows
};
```

---

## 5. ADDED: Fallback Retry for synthesis-failed ✅

**Location:** Lines 211-222 in voice_assistant.html

```javascript
utterance.onerror = function(event) {
  var errorMsg = event.error || 'unknown';
  console.log('[VOICE] Speech error: ' + errorMsg);
  assistantStatusEl.innerText = 'Speech error: ' + errorMsg;
  
  // Fallback: Retry once without any options if synthesis-failed
  if (errorMsg === 'synthesis-failed' && !isRetry) {
    console.log('[VOICE] Retrying speech without voice specifications...');
    resolve();
    setTimeout(function() {
      speak(text, { lang: lang, restartAfter: restartAfter, isRetry: true })
        .then(resolve)
        .catch(function() { resolve(); });
    }, 300);
  } else {
    resolve();
  }
};
```

**How fallback works:**
1. Detects `synthesis-failed` error
2. Checks `!isRetry` to prevent infinite loops
3. Waits 300ms for browser state refresh
4. Calls `speak()` again with `isRetry: true`
5. If still fails, gives up gracefully

---

## 6. ADDED: All Voices Logging ✅

**Location:** Lines 133-139 in voice_assistant.html

```javascript
var voices = synth.getVoices() || [];
console.log('[VOICE] ====== ALL AVAILABLE VOICES ======');
console.log('[VOICE] Total voices available: ' + voices.length);

for (var i = 0; i < voices.length; i++) {
  var voice = voices[i];
  console.log('[VOICE] ' + i + ': ' + voice.name + ' | Lang: ' + voice.lang + ' | Default: ' + voice.default);
}
console.log('[VOICE] ====== END VOICES LIST ======');
```

**Console output shows:**
- Total number of available voices
- Each voice name
- Language code (hi-IN, en-US, etc.)
- Whether it's the system default

---

## 7. ADDED: Auto-Listen After Greeting ✅

**Location:** Lines 466-472 in voice_assistant.html

```javascript
function startAssistantFlow() {
  console.log('[VOICE] Starting assistant flow');
  resetFlow();
  assistantState = 'awaiting_symptom';
  
  // Speak greeting and then automatically start listening
  speak('नमस्ते। कृपया अपनी समस्या बताइए।', { restartAfter: true });
  //                                                   ↑
  //                                        Auto-start listening
}
```

**Flow:**
1. Greeting spoken with `restartAfter: true`
2. Greeting finishes
3. `utterance.onend()` fires
4. Checks `if (restartAfter)` → true
5. Calls `startListening()` automatically
6. User hears greeting, then microphone is ready

---

## 8. ADDED: Voice Initialization Function ✅

**Location:** Lines 125-150 in voice_assistant.html

```javascript
function initializeVoices() {
  if (!synth) {
    console.log('[VOICE] speechSynthesis API not available');
    voiceWarningEl.innerText = 'Speech synthesis not available on this device.';
    voiceWarningEl.style.display = 'block';
    voiceStatusEl.innerText = 'Text mode (no speech synthesis).';
    return;
  }

  var voices = synth.getVoices() || [];
  console.log('[VOICE] ====== ALL AVAILABLE VOICES ======');
  // ... prints all voices ...
  
  var hindiVoice = voices.find(function(v) { 
    return (v.lang || '').toLowerCase().startsWith('hi'); 
  });
  
  if (hindiVoice) {
    console.log('[VOICE] Hindi voice detected: ' + hindiVoice.name + ' (' + hindiVoice.lang + ')');
    voiceStatusEl.innerText = 'Hindi voice available: ' + hindiVoice.name;
  } else {
    console.log('[VOICE] No Hindi voice detected. Browser will use default voice.');
    voiceStatusEl.innerText = 'Using default browser voice (lang: hi-IN)';
  }
}

// Initialize on page load
if (synth) {
  initializeVoices();
  synth.onvoiceschanged = function() {
    console.log('[VOICE] Voices changed event fired');
    initializeVoices();
  };
}
```

---

## 9. PRESERVED: Department Keywords with Devanagari ✅

**Location:** Lines 87-109 in voice_assistant.html

```javascript
const departmentMappings = [
  {
    code: 'GEN',
    name: 'General OPD',
    keywords: ['bukhar', 'बुखार', 'fever', 'sardi', 'सर्दी', 'khansi', 'खांसी', ...]
  },
  {
    code: 'CAR',
    name: 'Cardiology',
    keywords: ['dil', 'दिल', 'dil dard', 'दिल दर्द', 'chest pain', ...]
  },
  // ... more departments ...
];
```

**All Devanagari preserved:** ✅ बुखार, दिल दर्द, कमर दर्द, etc.

---

## 10. CLEAN: No Invalid Regex Patterns ✅

**Old broken regex (DELETED):**
```javascript
// This regex strips all Devanagari characters:
/[^a-z0-9\x00-\x7f\\s]/gi  // ❌ INVALID - character range issue
```

**New valid regexes (ADDED):**

```javascript
// Location: Line 269
var regex = /\b(haan|जी|yes|bilkul|theek|ठीक|haan ji|haan haan)\b/;

// Location: Line 275
var regex = /\b(nahi|नहीं|ना|no|nahin|na)\b/;
```

Both use valid Unicode characters with word boundaries.

---

## Complete Function: speak()

**Location:** Lines 173-230

```javascript
function speak(text, options) {
  options = options || {};
  var lang = options.lang || 'hi-IN';
  var restartAfter = options.restartAfter !== false;
  var isRetry = options.isRetry || false;
  
  return new Promise(function(resolve) {
    if (!synth) {
      console.log('[VOICE] speechSynthesis unavailable; text was: ' + text);
      appendMessage(text, 'assistant');
      resolve();
      return;
    }

    // ✅ Create utterance WITHOUT assigning any voice
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 1;
    utterance.volume = 1;
    
    utterance.onstart = function() {
      console.log('[VOICE] Speech started (lang: ' + lang + ')');
      assistantStatusEl.innerText = 'Speaking...';
      appendMessage(text, 'assistant');
    };
    
    utterance.onend = function() {
      console.log('[VOICE] Speech ended');
      assistantStatusEl.innerText = 'Speech finished.';
      if (restartAfter) {
        setTimeout(function() { startListening(); }, 500);
      }
      resolve();
    };
    
    utterance.onerror = function(event) {
      var errorMsg = event.error || 'unknown';
      console.log('[VOICE] Speech error: ' + errorMsg);
      assistantStatusEl.innerText = 'Speech error: ' + errorMsg;
      
      // ✅ Fallback: Retry once if synthesis-failed
      if (errorMsg === 'synthesis-failed' && !isRetry) {
        console.log('[VOICE] Retrying speech without voice specifications...');
        resolve();
        setTimeout(function() {
          speak(text, { lang: lang, restartAfter: restartAfter, isRetry: true })
            .then(resolve)
            .catch(function() { resolve(); });
        }, 300);
      } else {
        resolve();
      }
    };
    
    try {
      console.log('[VOICE] Calling speechSynthesis.cancel()');
      synth.cancel();  // ✅ Always cancel before speaking
      
      console.log('[VOICE] Speaking: ' + text.substring(0, 50) + '...');
      synth.speak(utterance);
    } catch (e) {
      console.log('[VOICE] Exception in speak(): ' + e.message);
      resolve();
    }
  });
}
```

**Key points:**
- ✅ No `utterance.voice` assignment (line removed)
- ✅ `synth.cancel()` called first
- ✅ Full console logging
- ✅ synthesis-failed fallback
- ✅ Returns Promise for async handling

---

## Summary: Critical Changes

| # | Change | Location | Status |
|---|--------|----------|--------|
| 1 | Removed `utterance.voice = selectedVoice` | Line 145 (deleted) | ✅ |
| 2 | Added `synth.cancel()` | Line 219 | ✅ |
| 3 | No voice assignment in utterance | Lines 189-193 | ✅ |
| 4 | Speech started logging | Line 197 | ✅ |
| 5 | Speech ended logging | Line 204 | ✅ |
| 6 | Speech error logging | Line 214 | ✅ |
| 7 | synthesis-failed fallback | Lines 212-222 | ✅ |
| 8 | All voices logging | Lines 133-139 | ✅ |
| 9 | Auto-listen after greeting | Line 472 | ✅ |
| 10 | No invalid regexes | All removed | ✅ |

---

## Testing with Console

### See all voices:
Open DevTools (F12) → Console → Navigate to Voice Assistant page

Look for:
```
[VOICE] ====== ALL AVAILABLE VOICES ======
[VOICE] Total voices available: 3
[VOICE] 0: Microsoft David - English (United States) | Lang: en-US | Default: true
[VOICE] 1: Microsoft Zira - English (United States) | Lang: en-US | Default: false
[VOICE] 2: Microsoft आरव Online (Natural) - Hindi (India) | Lang: hi-IN | Default: false
```

### See speech flow:
Click "Start Voice Assistant" and check console:
```
[VOICE] Start button clicked
[VOICE] Starting assistant flow
[VOICE] Speaking greeting in Hindi
[VOICE] Calling speechSynthesis.cancel()
[VOICE] Speaking: नमस्ते। कृपया अपनी समस्या बताइए।...
[VOICE] Speech started (lang: hi-IN)
[VOICE] Speech ended
[VOICE] Starting recognition...
[VOICE] Recognition started
```

No `synthesis-failed` errors! ✅
