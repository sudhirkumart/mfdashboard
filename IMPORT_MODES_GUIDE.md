# Import Modes Guide

## Overview

The MF Dashboard now supports **two import modes** when importing Excel, CSV, or JSON files:

1. **Replace All** - Clears existing data and imports fresh
2. **Merge/Update** - Adds to existing data or updates holdings

---

## Import Modes Explained

### 1️⃣ Replace All Mode (Default)

**When to use:**
- First time import
- Starting fresh with new data
- Want to clear everything and reload

**What it does:**
- ❌ Deletes all existing portfolio data
- ✅ Imports the new file as fresh data
- Result: Only the imported data remains

**Example:**
```
Before: 2 accounts (PAN1, PAN2) with 10 holdings
Import: Excel with 1 account (PAN3) with 5 holdings
After:  1 account (PAN3) with 5 holdings
```

---

### 2️⃣ Merge/Update Mode

**When to use:**
- Adding new mutual fund schemes to existing portfolio
- Adding a new PAN account
- Updating NAV values for existing holdings
- Monthly portfolio updates

**What it does:**
- ✅ Keeps all existing data
- ✅ Adds new accounts if PAN is new
- ✅ Adds new holdings to existing accounts
- ✅ Updates existing holdings (matches by Scheme Code or Scheme Name)

**How it merges:**
1. **New PAN Account** → Added as new account
2. **Existing PAN + New Scheme** → Adds new holding to account
3. **Existing PAN + Existing Scheme** → Updates the holding (units, invested, NAV, etc.)

**Example:**
```
Before: PAN1 with HDFC Fund, Axis Fund
Import: Excel with PAN1 (SBI Fund) + PAN2 (ICICI Fund)
After:  PAN1 with HDFC, Axis, SBI + PAN2 with ICICI
```

---

## Step-by-Step Usage

### How to Use Replace All Mode

1. Click **Import** button
2. Select **"Replace All"** radio button (default)
3. Choose your Excel/CSV/JSON file
4. ✅ All existing data is replaced with imported data

### How to Use Merge/Update Mode

1. Click **Import** button
2. Select **"Merge/Update"** radio button
3. Choose your Excel/CSV/JSON file
4. ✅ New data is added/merged with existing data

---

## Real-World Examples

### Example 1: Monthly NAV Update

**Scenario:** You have 2 PANs with 15 holdings. You want to update NAV values.

**Steps:**
1. Export current portfolio to Excel
2. Open Excel and update the "Current NAV" and "Current Value" columns
3. Save the Excel file
4. Import with **Merge/Update** mode
5. ✅ All NAV values are updated, no data lost

---

### Example 2: Adding New Investment

**Scenario:** You invested in a new mutual fund scheme.

**Steps:**
1. Create Excel with 1 row:
   ```
   PAN       | Scheme Name          | Units | Invested | Current NAV | Current Value
   YOUR_PAN  | New Fund Name        | 100   | 50000    | 500         | 50000
   ```
2. Import with **Merge/Update** mode
3. ✅ New holding added to your existing portfolio

---

### Example 3: Adding Family Member's Portfolio

**Scenario:** You have your portfolio (PAN1), want to add spouse's portfolio (PAN2).

**Steps:**
1. Create Excel with spouse's holdings (use PAN2 in PAN column)
2. Import with **Merge/Update** mode
3. ✅ PAN2 account is added, your PAN1 data remains intact

---

### Example 4: Starting Fresh

**Scenario:** You want to clear everything and start over.

**Steps:**
1. Create new Excel with all your current holdings
2. Import with **Replace All** mode
3. ✅ Old data cleared, fresh import loaded

---

## How Holdings Are Matched (Merge Mode)

When merging, the system identifies duplicate holdings by:

1. **Scheme Code** (if available and matching)
2. **Scheme Name** (if Scheme Code not available)

### Example - Same holding detected:

```
Existing: HDFC Top 100 Fund, Scheme Code: 119551
Imported: HDFC Top 100 Fund, Scheme Code: 119551
Result:   ✅ Updates existing holding (not duplicated)
```

### Example - Different holding:

```
Existing: HDFC Top 100 Fund
Imported: Axis Bluechip Fund
Result:   ✅ Adds as new holding
```

---

## Tips & Best Practices

### ✅ DO:

1. **Use Merge mode for updates** - Safer, doesn't delete data
2. **Export before importing** - Keep a backup
3. **Check console (F12)** - See detailed merge logs
4. **Use consistent scheme names** - Helps matching
5. **Include Scheme Code** - More reliable matching

### ❌ DON'T:

1. **Don't use Replace if unsure** - You'll lose data
2. **Don't mix scheme names** - "HDFC Fund" vs "HDFC Top 100" won't match
3. **Don't forget PAN column** - Needed to merge correctly

---

## Console Logging

Open browser console (F12) when importing to see detailed logs:

**Merge Mode Logs:**
```
=== Merging Portfolio Data ===
Existing accounts: 2
Imported accounts: 1
→ Merging holdings for account: AAAAA1111A
  ✓ Updated holding: HDFC Top 100 Fund
  ✓ Added new holding: SBI Small Cap Fund
=== Merge Complete ===
Total accounts after merge: 2
Total holdings after merge: 16
```

---

## Common Scenarios

### Scenario: "I imported but lost my old data!"

**Problem:** Used Replace mode accidentally
**Solution:**
1. If you exported before: Import that backup file
2. If not: Unfortunately data is lost
3. **Prevention:** Always export before importing, use Merge mode for updates

### Scenario: "Duplicate holdings appearing"

**Problem:** Scheme names don't match exactly
**Solution:**
1. Use exact same scheme names in Excel
2. Include Scheme Code column
3. Check browser console for matching logs

### Scenario: "New PAN not showing"

**Problem:** Imported with empty PAN column
**Solution:**
1. Add PAN column in Excel
2. Fill with actual PAN numbers
3. Re-import with Merge mode

### Scenario: "How to update just NAV values?"

**Solution:**
1. Export current portfolio
2. Update only NAV and Current Value columns
3. Import with **Merge/Update** mode
4. ✅ Only NAV values updated

---

## File Format Requirements

Works with all supported formats:
- ✅ **Excel** (.xlsx, .xls)
- ✅ **CSV** (.csv)
- ✅ **JSON** (.json)

### Required Columns (Minimum):
- PAN (or defaults to "IMPORTED")
- Scheme Name OR Scheme Code
- Units
- Current NAV

### Recommended Columns:
```
PAN | Account Name | Scheme Code | Scheme Name | Units | Invested Amount | Current NAV | Current Value
```

---

## Summary

| Mode | Existing Data | New Accounts | New Holdings | Update Holdings | Use Case |
|------|--------------|--------------|--------------|-----------------|----------|
| **Replace All** | ❌ Deleted | ✅ Imported | ✅ Imported | ✅ Imported | Fresh start, complete reload |
| **Merge/Update** | ✅ Kept | ✅ Added | ✅ Added | ✅ Updated | Monthly updates, add investments |

---

## Need Help?

1. Open browser console (F12) to see merge logs
2. Check `TROUBLESHOOTING_IMPORT.md` for common issues
3. Refer to `EXCEL_IMPORT_GUIDE.md` for Excel-specific help

---

**Pro Tip:** When in doubt, use **Merge/Update** mode - it's safer and doesn't delete your existing data!
