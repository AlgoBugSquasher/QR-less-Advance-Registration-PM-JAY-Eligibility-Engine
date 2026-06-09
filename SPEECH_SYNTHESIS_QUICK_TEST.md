# Speech Synthesis Truncation - Quick Test Guide

## 🚀 Quick Test (5 Minutes)

### 1. Open Page & Console
```
1. Go to: http://localhost:5000/voice-assistant
2. Press F12 to open browser DevTools
3. Click "Console" tab
```

### 2. Test Full Message Speaking

**Click "Start Assistant"**
```
Look for in console:
[VOICE] Full text to speak: (should show COMPLETE greeting)
[VOICE] Split into 1 chunk(s)
[VOICE] Speaking chunk: (complete text)
[VOICE] Chunk completed
[VOICE] Full message completed
```

### 3. Test Confirmation Message (Long Text)

**Say: "bukhar" → When asked to confirm say: "haan"**
```
Look for in console:
[VOICE] Full text to speak: आपको General OPD में भेजा जाएगा।
अगर सही है तो 'हाँ' या 'ठीक है' बोलिए।
अगर गलत है तो 'नहीं' बोलिए।
(You will be sent...)

[VOICE] Split into 4 chunk(s)  ← Multiple chunks!
[VOICE] Speaking chunk: आपको General OPD...
[VOICE] Chunk completed
[VOICE] Speaking chunk: अगर सही है...
[VOICE] Chunk completed
... (more chunks)
[VOICE] Full message completed

Listen: ALL instructions spoken (no truncation!)
```

### 4. Test Token Generation

**Say token confirmation phrase**
```
Look for in console:
[VOICE] Token generated - stopping assistant
[VOICE] Full text to speak: आपका टोकन GEN-XXX है। धन्यवाद! (Your token is...)
[VOICE] Split into 1 chunk(s)
[VOICE] Speaking chunk: आपका टोकन...
[VOICE] Chunk completed
[VOICE] Full message completed

Status: ✅ Token Generated Successfully (should appear)
```

---

## ✅ What Should Happen

| Action | Before Fix | After Fix |
|--------|-----------|-----------|
| Long confirmation | Only first part heard | FULL message heard |
| Console logs | No [VOICE] logs | Shows all chunks |
| Text vs Speech | Mismatch (chat shows more) | Perfect match |
| Error messages | Truncated in audio | Complete message |

---

## 🔍 Key Indicators

### ✅ Fix Working
- Console shows: `[VOICE] Split into N chunk(s)` where N > 1
- Multiple `[VOICE] Speaking chunk:` entries
- `[VOICE] Full message completed` at end
- Confirmation text fully heard in audio
- No truncation in speech

### ❌ Still Broken
- Only 1 chunk shown (even for long messages)
- Missing chunk completion logs
- Audio truncated (ends abruptly)
- Chat shows more text than heard

---

## 📊 Expected Console Output Format

```
[VOICE] Full text to speak: <entire text to be spoken>
[VOICE] Split into <N> chunk(s)
[VOICE] Speaking chunk: <chunk 1>
[VOICE] Chunk completed
[VOICE] Speaking chunk: <chunk 2>
[VOICE] Chunk completed
...
[VOICE] Speaking chunk: <chunk N>
[VOICE] Chunk completed
[VOICE] Full message completed
```

---

## 🎯 Test Scenarios

### Scenario 1: Short Message ✅
```
Action: Click "Start Assistant"
Expected: 1 chunk, fully heard
```

### Scenario 2: Long Confirmation Message ✅
```
Action: Say "bukhar" then "haan"
Expected: 4 chunks, all fully heard
Look for: Multiple "Speaking chunk" entries
```

### Scenario 3: Error Message ✅
```
Action: Trigger error (e.g., network issue)
Expected: Complete error message in audio and console
```

### Scenario 4: Token Success ✅
```
Action: Complete full flow
Expected: Token number fully announced
```

---

## 🎉 Success = All Chunks Heard

If you see:
```
[VOICE] Split into 4 chunk(s)
```

You should hear 4 separate pieces of audio, playing one after another.

If you ONLY hear the first part, the old truncation bug is still present.

---

## 💡 Troubleshooting

**Q: Console shows [VOICE] logs but audio still truncated?**
- A: Check browser volume, try different browser, refresh page

**Q: Console doesn't show [VOICE] logs at all?**
- A: Make sure DevTools is open BEFORE clicking Start Assistant

**Q: Only 1 chunk shown for long message?**
- A: Algorithm may have grouped sentences differently - still works if all text heard

---

**Test Duration:** ~5 minutes per scenario
**Success Indicator:** Full confirmation text heard in audio
