# Quick Fix Guide for Excel Import Issue

## Problem
Invested Amount showing as ₹0.00 when importing from Excel

## Immediate Steps to Fix

### Step 1: Clear Browser Cache (IMPORTANT!)
Your browser may be using the old JavaScript code. **You MUST do a hard refresh:**

**Windows/Linux:**
- Press `Ctrl + F5` OR
- Press `Ctrl + Shift + R`

**Mac:**
- Press `Cmd + Shift + R`

This will reload the page and clear the cached JavaScript files.

---

### Step 2: Open Browser Console
1. Press `F12` on your keyboard
2. Click on the "Console" tab
3. Keep this window open

---

### Step 3: Import Your Excel File
1. Go to http://localhost:8000
2. Click the **Import** button
3. Select your Excel file

---

### Step 4: Check Console Output
Look at the console messages. You should see:

**If columns are found correctly:**
```
✓ Found Invested in column: "Invested Amount" = 65000
✓ Found Units in column: "Units" = 100
✓ Found Current NAV in column: "Current NAV" = 720.50
=== Parsed row ===
Scheme Name: HDFC Top 100 Fund
Units: 100
Invested: 65000
Current NAV: 720.50
Current Value: 72050
================
```

**If column is not found:**
```
⚠ Invested column not found. Looking for one of: Invested Amount, Invested, Investment, Cost, Purchase Value, Invested Value, Total Invested, Amount Invested
   Available columns: Scheme Name, Units, Investment Amount, NAV, Market Value
```

---

### Step 5: Fix Column Names (If Needed)

If you see the warning message, your Excel column name doesn't match.

**Option A: Rename in Excel (Recommended)**
1. Open your Excel file
2. Find the column header (usually in row 1)
3. Rename it to one of the supported names:
   - **For Invested**: Use `Invested Amount` or `Invested`
   - **For Units**: Use `Units`
   - **For NAV**: Use `Current NAV` or `NAV`
   - **For Current Value**: Use `Current Value`
4. Save and re-import

**Option B: Tell me the exact column name**
Look at the console warning message where it says "Available columns: ..." and tell me the exact column names. I can add them to the supported list.

---

## Supported Column Names

### Invested Amount (any of these will work):
- Invested Amount ✓
- Invested ✓
- Investment ✓
- Cost ✓
- Purchase Value ✓
- Invested Value ✓
- Total Invested ✓
- Amount Invested ✓

### Units (any of these will work):
- Units ✓
- Unit ✓
- Quantity ✓

### Current NAV (any of these will work):
- Current NAV ✓
- NAV ✓
- Latest NAV ✓
- Current Price ✓
- Price ✓

### Current Value (any of these will work):
- Current Value ✓
- Market Value ✓
- Value ✓
- Total Value ✓

---

## Diagnostic Tool

If you're still having issues, use the test tool:

1. Open `dashboard/test_import.html` in your browser
2. Drag your Excel file onto it
3. It will show you exactly what column names exist
4. Screenshot the results and share

---

## Common Issues

### Issue 1: Browser Cache
**Symptom:** Console doesn't show the new debug messages
**Fix:** Hard refresh with Ctrl+F5 or Ctrl+Shift+R

### Issue 2: Column name has extra spaces
**Symptom:** Console shows "Investment Amount " (with trailing space)
**Fix:** The new code now handles this with case-insensitive and trim matching

### Issue 3: Data is text, not numbers
**Symptom:** Console shows Invested: 0 even though column is found
**Fix:**
1. Open Excel
2. Select the Invested column
3. Format → Number
4. Remove any currency symbols (₹, $)
5. Remove commas (change 1,00,000 to 100000)
6. Save and re-import

### Issue 4: Column name is completely different
**Symptom:** Console warning shows a column name not in the supported list
**Fix:** Share the console output with me and I'll add that column name

---

## What I Changed

The updated code now:
1. ✓ Tries exact column name match first
2. ✓ Falls back to case-insensitive match
3. ✓ Shows detailed console logs for debugging
4. ✓ Warns when columns are not found
5. ✓ Lists all available columns in your Excel

---

## Next Steps

1. **Hard refresh the browser** (Ctrl+F5)
2. **Import your Excel again**
3. **Check the browser console** (F12)
4. **Share the console output** if the issue persists

The console output will tell us exactly what's wrong!
