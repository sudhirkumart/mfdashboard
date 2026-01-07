# Edit, Delete & Filter Guide

## New Features Added

Your MF Dashboard now has three powerful new features:

1. ✏️ **Edit Holdings** - Update units, NAV, invested amount directly
2. 🗑️ **Delete Holdings** - Remove individual holdings
3. 🔍 **Filter by PAN/Category** - View specific accounts or fund types

---

## 1. Edit Holdings ✏️

### How to Edit:

1. Find the holding you want to edit in the Holdings table
2. Click the **blue Edit button** (pencil icon) in the Actions column
3. Edit modal opens with editable fields:
   - **Units** - Number of units held
   - **Invested Amount** - Total amount invested
   - **Current NAV** - Latest NAV price
   - **Current Value** - Current market value
   - **Category** - Fund category (Equity/Debt/Hybrid/Liquid/Other)
   - **Folio** - Folio number
4. Make your changes
5. Click **"Save Changes"**
6. ✅ Dashboard refreshes with updated data

### What You Can't Edit:
- **Scheme Name** - Read-only (identifies the holding)
- **PAN** - Can't change which account owns it

### Use Cases:
- 📊 **Update NAV values** monthly
- 💰 **Correct invested amount** if entered wrong
- 🏷️ **Add/update category** for better filtering
- 📝 **Add folio number** if missing

---

## 2. Delete Holdings 🗑️

### How to Delete:

1. Find the holding you want to remove
2. Click the **red Delete button** (trash icon) in the Actions column
3. Confirmation dialog appears:
   ```
   Are you sure you want to delete "HDFC Top 100 Fund"?

   This action cannot be undone.
   ```
4. Click **OK** to confirm or **Cancel** to abort
5. ✅ Holding is removed immediately

### Safety Features:
- **Confirmation required** - Can't delete by accident
- **Last holding protection** - If deleting last holding in an account, you'll be asked if you want to remove the entire account
- **Undo not available** - Export before deleting important holdings!

### Warning:
⚠️ **Deletion is permanent!** Always export your portfolio before deleting holdings.

### Pro Tip:
**Before deleting:** Export to JSON/Excel as backup
```
Export → Export to JSON → Save → Then delete
```

---

## 3. Filter by PAN / Category 🔍

### Filter Options:

#### A. Filter by PAN
- Shows holdings for specific account only
- Dropdown shows: `PAN - Account Name`
- Example: `AAAAA1111A - John Doe`

#### B. Filter by Category
- Filter by fund type:
  - Equity
  - Debt
  - Hybrid
  - Liquid
  - Other

#### C. Search Box
- Search by scheme name, PAN, or folio
- Works with filters (combined filtering)

### How to Use Filters:

**Single Filter:**
1. Select a PAN from "Filter by PAN" dropdown
2. Table shows only that account's holdings

**Multiple Filters:**
1. Select PAN: `AAAAA1111A`
2. Select Category: `Equity`
3. Type in search: `HDFC`
4. ✅ Shows only AAAAA1111A's Equity funds with "HDFC" in the name

**Clear Filters:**
- Click **"Clear"** button to reset all filters

---

## Examples & Use Cases

### Example 1: Update Monthly NAV

**Goal:** Update NAV values for all holdings

1. **Option A - Edit individually:**
   - Click Edit on each holding
   - Update Current NAV and Current Value
   - Save

2. **Option B - Import update (Recommended):**
   - Export current portfolio
   - Update NAV columns in Excel
   - Import with "Merge/Update" mode
   - ✅ All NAVs updated at once

---

### Example 2: View Single Account

**Goal:** See only holdings for PAN "AAAAA1111A"

1. Select `AAAAA1111A` from PAN filter
2. ✅ Table shows only that account's holdings
3. All calculations (summary cards) still show total portfolio

---

### Example 3: Delete Redeemed Holding

**Goal:** Remove a fund you fully redeemed

1. Find the redeemed holding
2. Click Delete (trash icon)
3. Confirm deletion
4. ✅ Holding removed, portfolio updated

---

### Example 4: View All Equity Funds

**Goal:** See only Equity category holdings across all accounts

1. Select "Equity" from Category filter
2. ✅ Shows all Equity funds from all PANs

---

### Example 5: Find Specific Fund

**Goal:** Find "HDFC Top 100 Fund" holdings

1. Type "HDFC Top 100" in search box
2. ✅ Shows only matching funds
3. Optionally add PAN filter to see specific account

---

## Filter Bar Layout

```
┌────────────────────────────────────────────────────────────┐
│  🔍 PAN: [All Accounts ▼]  📁 Category: [All Categories ▼] │
│                                          [✖ Clear] Button   │
└────────────────────────────────────────────────────────────┘
```

---

## Actions Column

Each row in the Holdings table now has an **Actions** column with two buttons:

```
┌─────────────┐
│  📝 Edit    │  Blue pencil icon
│  🗑️ Delete  │  Red trash icon
└─────────────┘
```

---

## Keyboard Shortcuts

- **Escape** - Close edit modal
- **Enter** - Submit edit form (when in edit modal)
- **Type in search** - Filter as you type

---

## Tips & Best Practices

### ✅ DO:

1. **Export before bulk edits** - Keep a backup
2. **Use filters** for large portfolios - Easier to navigate
3. **Update category** during edit - Helps with filtering
4. **Use merge mode** for bulk updates - Faster than individual edits
5. **Double-check** before deleting - No undo available

### ❌ DON'T:

1. **Don't delete without backup** - Export first!
2. **Don't forget to clear filters** - Might think data is missing
3. **Don't edit scheme names** - Can't change (identifies holding)
4. **Don't rush deletes** - Read confirmation carefully

---

## Technical Details

### How Edit Works:
1. Finds holding by PAN and index
2. Opens modal with current values
3. Updates holding object in memory
4. Refreshes entire dashboard
5. Recalculates all totals

### How Delete Works:
1. Removes holding from account's holdings array
2. Checks if account is now empty
3. Optionally removes empty account
4. Refreshes dashboard
5. Updates all calculations

### How Filters Work:
1. Filters are applied in real-time (no reload)
2. Multiple filters combine (AND logic)
3. Filters work on rendered rows (client-side)
4. Original data unchanged (non-destructive)

---

## Troubleshooting

### Issue: "Can't see Edit/Delete buttons"

**Solutions:**
1. Hard refresh browser (Ctrl+F5)
2. Check if browser window is narrow (buttons may wrap)
3. Scroll table horizontally if needed

### Issue: "Changes not saving"

**Solutions:**
1. Check browser console (F12) for errors
2. Ensure all required fields are filled
3. Refresh page and try again

### Issue: "Filter not working"

**Solutions:**
1. Clear all filters and try again
2. Check that holdings have category set (edit to add)
3. Refresh page

### Issue: "Deleted wrong holding!"

**Solutions:**
1. If you exported before: Import backup file
2. If not: Manually re-add via Excel import
3. Prevention: Always export before deleting

---

## Browser Console Logs

Open console (F12) to see:

**Edit:**
```
✓ Holding updated successfully
```

**Delete:**
```
✓ Holding deleted successfully
```

---

## Data Persistence

### Important Notes:

- ⚠️ **Changes are in-memory only** - Not automatically saved
- 💾 **To save permanently:** Export to JSON/Excel after editing
- 🔄 **On page refresh:** Changes lost unless exported
- 📤 **Best practice:** Export after every editing session

### Workflow:
```
1. Import portfolio
2. Edit/Delete holdings as needed
3. Export to JSON/Excel
4. Next session: Import that file
```

---

## Summary Table

| Feature | Icon | Color | Action | Undo? |
|---------|------|-------|--------|-------|
| **Edit** | ✏️ Pencil | Blue | Opens modal to edit values | Yes (before save) |
| **Delete** | 🗑️ Trash | Red | Removes holding permanently | No |
| **Filter PAN** | 👤 User | - | Show specific account | Yes (clear filter) |
| **Filter Category** | 📁 Filter | - | Show specific category | Yes (clear filter) |
| **Search** | 🔍 Search | - | Find by text | Yes (clear search) |

---

## Quick Reference Card

```
╔════════════════════════════════════════════════╗
║  EDIT, DELETE & FILTER - QUICK REFERENCE       ║
╠════════════════════════════════════════════════╣
║                                                ║
║  ✏️ EDIT:   Click blue button → Edit → Save    ║
║  🗑️ DELETE: Click red button → Confirm         ║
║  🔍 FILTER: Select PAN/Category → Auto-filter  ║
║  ✖️ CLEAR:  Click "Clear" button               ║
║                                                ║
║  💡 TIP: Export before deleting!               ║
╚════════════════════════════════════════════════╝
```

---

## What's Next?

Future enhancements could include:
- Undo/Redo functionality
- Bulk edit multiple holdings
- Advanced filtering (date ranges, value ranges)
- Sort by column
- Export filtered data only

---

**Your dashboard is now fully equipped to manage holdings efficiently!** 🎉

For more help:
- Import/Export: See `IMPORT_MODES_GUIDE.md`
- Column mapping: See `TROUBLESHOOTING_IMPORT.md`
- General usage: See `README.md`
