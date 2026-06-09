# Quick Reference: Department Stats Auto-Update

## Files Changed Summary

| File | Change | Purpose |
|------|--------|---------|
| `app/routes/token.py` | Added `/api/departments/stats` endpoint | Provides fresh queue data via API |
| `app/templates/manual_token_redesigned.html` | Added JavaScript functions & integrated refresh | Handles dynamic UI updates after token generation |
| `app/templates/departments.html` | Replaced page reload with AJAX refresh | Improved background statistics refresh |

## Key Functions

### Backend: `/api/departments/stats`
```python
# Returns all departments with current queue info
# Response: {"success": true, "departments": [...]}
```

### Frontend: `formatWaitTime(waitMinutes)`
```javascript
// Converts numbers to human-readable format
// 0 → "No wait", 120 → "2h", 45 → "45 min"
```

### Frontend: `updateDepartmentCard(deptCode, stats)`
```javascript
// Updates a single card's queue info with pulse animation
// Called for each department after generating token
```

### Frontend: `refreshDepartmentStats(highlightDeptCode)`
```javascript
// Fetches fresh stats from API and updates all cards
// Called immediately after successful token generation
```

## Workflow

```
User Generates Token
    ↓
Token Created in Database
    ↓
Call refreshDepartmentStats(deptCode)
    ↓
Fetch /api/departments/stats
    ↓
Update Each Department Card
    ↓
Pulse Animation Shows Change
    ↓
User Sees Updated Statistics (NO Page Reload)
```

## Test the Feature

1. Navigate to `/token/departments`
2. Select a department
3. Generate token
4. **Observe:** Department card queue count increases instantly
5. **NO:** Page doesn't reload, no F5 needed

## Verify It Works

**Check Console:**
```javascript
// Open DevTools (F12) → Console
// Generate a token
// You should see no errors
// Network tab should show GET to /api/departments/stats
```

**Check Elements:**
```javascript
// Inspect the department card
// Queue value should update instantly
// Pulse animation should be visible
```

## Performance Impact

- **Before:** Full page reload every 30 seconds (CPU intensive)
- **After:** AJAX requests every 60 seconds + event-driven updates (lightweight)
- **Result:** Better performance, smoother UX

## Backward Compatibility

✅ All existing functionality preserved:
- Token generation logic unchanged
- Database operations unchanged
- UI structure unchanged
- Still works if JavaScript disabled (minimal graceful degradation)

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Card not updating | API endpoint missing | Verify `/api/departments/stats` exists |
| Wrong values shown | Cache issue | Clear browser cache (Ctrl+Shift+Delete) |
| Animation not visible | CSS not loaded | Check stylesheet in browser DevTools |
| No department refresh | JavaScript error | Check console for JS errors |

## For Developers

### Add Similar Feature to Another Page

1. Create API endpoint returning fresh data
2. Create `refreshData()` function using fetch
3. Create `updateElement()` function updating DOM
4. Call after action completes
5. Add optional animation

### Modify Refresh Interval

In `departments.html`:
```javascript
// Change 60000 to desired milliseconds
setInterval(function() {
    // ...
}, 60000);  // ← Change this number
```

### Modify Animation

In `manual_token_redesigned.html`:
```javascript
// Adjust animation CSS
'@keyframes pulse {' +
'  0%, 100% { opacity: 1; }' +
'  50% { opacity: 0.6; }' +  // ← Change opacity
'}' 
```

### Debug API Response

Add to browser console while on department page:
```javascript
fetch('/api/departments/stats')
  .then(r => r.json())
  .then(data => console.log('API Response:', data));
```

---

**Last Updated:** 2026-06-09  
**Status:** ✅ Production Ready  
**Version:** 1.0
