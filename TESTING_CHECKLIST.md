# Arogya AI - Real Functionality Testing Checklist

## CRITICAL: This is a REAL TEST document - verify each feature actually works

---

## 1. Symptom Analysis - DYNAMIC TESTING ✓

### Test A: High Severity Keywords
**Input:** "I have severe chest pain and feel dizzy"
**Expected:**
- Severity: HIGH
- Console log: `📊 Severity: High`
- Health score meter: Red (85/100)
- Emergency message visible

**Input:** "I was diagnosed with cancer"
**Expected:**
- Severity: HIGH
- Specialist: Cardiologist or General Physician recommended
- Action: "Seek immediate medical attention"

**Input:** "I am bleeding heavily"
**Expected:**
- Severity: HIGH
- Console shows correct diagnosis

### Test B: Medium Severity Keywords
**Input:** "I have fever and body pain"
**Expected:**
- Severity: MEDIUM
- Console log: `📊 Severity: Medium`
- Health score meter: Amber (50/100)
- Action: "Schedule doctor appointment"

**Input:** "persistent headache for 3 days"
**Expected:**
- Severity: MEDIUM
- Appropriate next steps

### Test C: Low Severity
**Input:** "I feel a bit tired today"
**Expected:**
- Severity: LOW (not MEDIUM)
- Console log: `📊 Severity: Low`
- Health score meter: Green (20/100)
- Action: "Monitor symptoms"

### Verification Steps:
1. Open browser console (F12)
2. Enter symptom on Dashboard
3. Check console logs:
   - `🔍 Symptom Analysis Request:` should show your input
   - `✅ Symptom Analysis Response:` should show full data
   - `📊 Severity:` should show correct level
4. Verify UI matches console output

---

## 2. Map & Hospitals - REAL DATA TESTING ✓

### Test A: Location Permission Granted
**Steps:**
1. Go to /clinics
2. Click "Allow" on location prompt
3. Open console (F12)

**Expected Console Logs:**
```
🗺️ Starting hospital search...
📍 Location obtained: [lat], [lng]
🏥 Fallback hospitals ready: 5
🔍 Calling API: /clinics/nearby?lat=...&lng=...
✅ API Response: {clinics: [...], map_embed_url: "..."}
🏥 Hospitals found: [number]
✅ Hospital search complete
```

**Expected UI:**
- Map loads with user location
- Hospital cards display below map
- Distance shown for each (e.g., "2.3 km")
- Color coding: Green/Yellow/Orange
- Nearest hospital has badge
- "Get Directions" buttons work

### Test B: API Failure (Fallback Test)
**If API fails, should show:**
- Console: `❌ API Error:` followed by `⚠️ Using fallback data`
- UI still shows 5 sample hospitals
- Distances calculated from user location
- All buttons still work

### Test C: Location Permission Denied
**Steps:**
1. Go to /clinics
2. Click "Block" on permission prompt

**Expected:**
- Console: `❌ Geolocation error:`
- UI shows error message
- Retry button available

### Verification:
- [ ] Console logs appear correctly
- [ ] Map displays (even if fallback)
- [ ] Hospital list renders
- [ ] Distance numbers are real (not "0 km")
- [ ] "Get Directions" opens Google Maps

---

## 3. History Saving - PERSISTENCE TESTING ✓

### Test A: Save to History
**Steps:**
1. Open Dashboard
2. Enter symptom: "fever and cough"
3. Submit
4. Check console

**Expected Console Logs:**
```
🔍 Symptom Analysis Request: fever and cough
✅ Symptom Analysis Response: {...}
💾 Saved to History: {id: "...", timestamp: "...", severity: "Medium"}
📜 Current History Count: 1
```

**Verification:**
1. Go to /history page
2. Should see the symptom check listed
3. Severity badge correct
4. Timestamp shown

### Test B: Persistence After Refresh
**Steps:**
1. Check symptom on Dashboard
2. Refresh browser (F5)
3. Go to /history

**Expected:**
- History still shows previous entry
- NOT empty
- Console: `📚 History loaded: [count] items`

### Test C: Multiple Entries
**Steps:**
1. Check 3 different symptoms
2. Go to /history

**Expected:**
- All 3 entries visible
- Newest first (reverse chronological)
- Each has unique timestamp

---

## 4. Delete History - INSTANT UPDATE TESTING ✓

### Test A: Delete Single Item
**Steps:**
1. Go to /history with at least 2 entries
2. Click trash icon on one item
3. Check console

**Expected Console Logs:**
```
🗑️ Deleting item: [id]
✅ Item deleted successfully
📚 History loaded: [count-1] items
```

**Verification:**
- [ ] Item disappears instantly (no page refresh)
- [ ] Other items still visible
- [ ] Console shows successful deletion

### Test B: Clear All History
**Steps:**
1. Go to /history with multiple entries
2. Click "Clear History" button
3. Confirm in dialog
4. Check console

**Expected Console Logs:**
```
🗑️ Clearing all history...
✅ History cleared successfully
```

**Verification:**
- [ ] Confirmation dialog appears before delete
- [ ] All items removed after confirm
- [ ] Empty state message shows
- [ ] Console confirms clear

### Test C: Persistence After Delete
**Steps:**
1. Delete an item
2. Refresh browser
3. Go to /history

**Expected:**
- Deleted item stays deleted (not reappearing)
- LocalStorage updated correctly

---

## 5. Dashboard UX - IMMEDIATE FEEDBACK TESTING ✓

### Test A: Result Display
**Steps:**
1. Enter symptom on Dashboard
2. Submit

**Expected:**
- Loading animation appears immediately
- Console shows: `🔍 Symptom Analysis Request:`
- After response:
  - Loading disappears
  - Result card displays below input
  - Health score meter visible
  - Doctor recommendation card shows
  - Next steps listed

**NO page reload required - result shows in-place**

### Test B: Multiple Queries
**Steps:**
1. Check symptom #1
2. Result displays
3. Check symptom #2
4. New result replaces old one

**Verification:**
- Previous result replaced (not accumulated)
- Console shows both requests
- History saves both entries

---

## 6. Console Debugging - VERIFY LOGS ✓

### Required Console Logs

**Symptom Analysis:**
- `🔍 Symptom Analysis Request: [input]`
- `✅ Symptom Analysis Response: {...}`
- `📊 Severity: [High/Medium/Low]`
- `🏥 Diagnosis: [diagnosis]`
- `💾 Saved to History: {...}`
- `📜 Current History Count: [number]`

**Map/Hospitals:**
- `🗺️ Starting hospital search...`
- `📍 Location obtained: [lat], [lng]`
- `🏥 Fallback hospitals ready: [number]`
- `🔍 Calling API: [url]`
- `✅ API Response: {...}`
- `🏥 Hospitals found: [number]`

**History:**
- `📜 Loading history...`
- `📚 History loaded: [count] items`
- `🗑️ Deleting item: [id]`
- `✅ Item deleted successfully`
- `🗑️ Clearing all history...`
- `✅ History cleared successfully`

**Errors (if any):**
- `❌ Symptom analysis error:`
- `❌ API Error:`
- `❌ Geolocation error:`
- `❌ Failed to clear history`

---

## 7. Known Working Features (Verified)

✅ **Backend Symptom Analysis**
- Rule-based + AI hybrid working
- Severity correctly classified
- Returns proper JSON

✅ **Backend Hospital API**
- `/api/clinics/nearby` returns real data
- OpenStreetMap Overpass API integrated
- Fallback data available

✅ **LocalStorage History**
- Saves correctly
- Persists after refresh
- Delete works
- Clear all works

✅ **UI Components**
- Health score meter displays
- Doctor recommendations show
- Loading states work
- Error boundaries prevent crashes

---

## 8. Testing Workflow

### Quick Test (5 minutes)
1. Dashboard: Check one symptom → verify console logs
2. History: Go to /history → verify entry saved
3. Map: Go to /clinics → verify hospitals load

### Full Test (15 minutes)
1. Test all 3 severity levels
2. Test map with location granted
3. Test history save/delete
4. Refresh browser and verify persistence
5. Check console for all expected logs

### Production Test (before deploy)
1. Run all tests above
2. Test on mobile browser
3. Test with slow network
4. Test with location denied
5. Verify fallbacks work

---

## 9. Failure Scenarios to Test

### What if OpenStreetMap API is down?
- **Expected:** Fallback hospitals display
- **Console:** `⚠️ Using fallback data`
- **Result:** User still sees 5 sample hospitals

### What if user denies location?
- **Expected:** Error message with retry button
- **Console:** `❌ Geolocation error:`
- **Result:** No crash, helpful message

### What if localStorage is full?
- **Expected:** Console error but app doesn't crash
- **Console:** `Failed to save symptom check:`
- **Result:** Feature fails gracefully

### What if backend is down?
- **Expected:** Error message to user
- **Console:** `❌ Symptom analysis error:`
- **Result:** Friendly error, not white screen

---

## 10. Success Criteria

A feature is **WORKING** if:
1. ✅ Console logs appear as documented
2. ✅ UI updates immediately (no reload needed)
3. ✅ Data persists after refresh
4. ✅ Errors are handled gracefully
5. ✅ User gets helpful feedback

A feature is **BROKEN** if:
1. ❌ No console logs appear
2. ❌ UI doesn't update
3. ❌ Data doesn't persist
4. ❌ White screen or crash
5. ❌ No error message

---

## Test Results Template

Copy and fill this out:

```
Date: ___________
Tester: ___________

[ ] Symptom Analysis - High severity works
[ ] Symptom Analysis - Medium severity works  
[ ] Symptom Analysis - Low severity works
[ ] Console logs for analysis appear
[ ] Map loads with location permission
[ ] Hospitals display correctly
[ ] Console logs for map appear
[ ] History saves after symptom check
[ ] History persists after refresh
[ ] Delete single item works
[ ] Clear all history works
[ ] Console logs for history appear
[ ] Dashboard shows result in-place
[ ] No white screens or crashes
[ ] All error messages user-friendly

Notes:
___________________________________________
```

---

**IMPORTANT:** If any test fails, check console for errors FIRST before claiming feature is broken.
