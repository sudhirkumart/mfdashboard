# Import Troubleshooting Guide

## Common Issue: "Invested Amount not showing / Zero values"

### Symptoms
- Units import correctly ✓
- Current Value shows correctly ✓
- BUT Invested shows ₹0.00 ✗
- Average Price shows ₹0.00 ✗
- Return % shows "+Infinity%" ✗

### Root Cause
Your Excel/CSV column name doesn't match what the importer expects.

### Solution

#### Quick Fix
**Rename your column to one of these supported names:**

For **Invested Amount**:
- `Invested Amount` (preferred)
- `Invested`
- `Investment`
- `Cost`
- `Purchase Value`

For **Current NAV**:
- `Current NAV` (preferred)
- `NAV`
- `Latest NAV`
- `Current Price`

For **Units**:
- `Units` (preferred)
- `Unit`
- `Quantity`

For **Current Value**:
- `Current Value` (preferred)
- `Market Value`
- `Value`

#### Step-by-Step Fix

1. **Open your Excel file**

2. **Check column headers** (first row)
   - Look at the exact spelling
   - Check for extra spaces
   - Verify capitalization

3. **Rename columns to match supported names**
   - Example: Rename "Investment Amount" → "Invested Amount"
   - Example: Rename "Purchase Cost" → "Invested"

4. **Save and re-import**

### Checking What Columns Were Detected

1. **Open browser console** (F12 key)
2. **Click Import** and select your file
3. **Look for messages like:**
   ```
   Importing from Excel sheet: Holdings
   Columns found: Scheme Name, Folio, Units, Investment, NAV, Market Value
   ```
4. **Compare with supported names above**

### Example: Before & After

**Before (Not Working):**
```
Scheme Name | Units | Investment Amount | Current Price | Market Val
```

**After (Working):**
```
Scheme Name | Units | Invested Amount | Current NAV | Current Value
```

## Other Common Issues

### Issue: "Excel sheet is empty"

**Cause:** No data rows found

**Solutions:**
- Ensure you have at least one data row (besides header)
- Check you're importing the correct sheet
- Verify the sheet isn't filtered/hidden

### Issue: "Must contain holdings data"

**Cause:** Missing required columns

**Solution:** Must have either:
- `Scheme Name` column, OR
- `Scheme Code` column

### Issue: Numbers importing as zero

**Causes:**
1. Column name doesn't match (see above)
2. Numbers formatted as text in Excel
3. Currency symbols in the data (₹, $)
4. Commas in numbers (1,00,000)

**Solutions:**
1. Fix column names
2. In Excel: Format → Number
3. Remove currency symbols
4. Remove commas from numbers

**Good:**
```
100000
150.50
```

**Bad:**
```
₹1,00,000
$150.50
```

### Issue: "+Infinity%" return

**Cause:** Invested amount is 0 (division by zero)

**Solution:** Fix the invested amount column (see main solution above)

### Issue: Scheme name correct but other values zero

**Cause:** Excel has merged cells or blank rows

**Solution:**
- Unmerge all cells
- Delete blank rows
- Ensure data starts from row 2 (row 1 is header)

## Best Practices

### 1. Use Export as Template
```
Dashboard → Export → Excel → Edit → Import
```
This ensures correct column names!

### 2. Match Exported Column Names Exactly
When you export from dashboard, note the exact column names and use the same.

### 3. Test with Sample Data First
Create a simple Excel with 1-2 holdings to test format.

### 4. Keep It Simple
- No merged cells
- No blank rows
- No formulas that reference other sheets
- Plain text/numbers only

### 5. Column Order Doesn't Matter
You can arrange columns in any order, just match the names.

## Debug Checklist

- [ ] Column names match supported names (case-sensitive)
- [ ] No extra spaces in column names
- [ ] Numbers are formatted as numbers (not text)
- [ ] No currency symbols or commas in data
- [ ] At least one data row present
- [ ] Either "Scheme Name" or "Scheme Code" column exists
- [ ] Browser console shows correct columns detected

## Test Your Excel File

### Quick Test Template

Create Excel with these exact columns:

```
Scheme Name | Units | Invested | Current NAV | Current Value
```

Sample data:
```
HDFC Top 100 Fund | 100 | 65000 | 720.50 | 72050
Axis Bluechip Fund | 250 | 10625 | 48.25 | 12062.50
```

If this works but yours doesn't, compare column names character by character.

## Still Not Working?

### Export Example File

1. Go to dashboard: http://localhost:8000
2. Click "Export" → "Export to CSV"
3. Open CSV in Excel
4. Save as .xlsx
5. Try importing this file
6. If it works, compare with your file

### Check Browser Console

1. Press F12 to open browser console
2. Click Import and select your file
3. Look for error messages
4. Check "Columns found:" message
5. Share console output if asking for help

### Manual Fix

If all else fails:
1. Create a new Excel file
2. Copy column names from exported file
3. Copy your data into new file
4. Import new file

## Supported Column Names Reference

### Required (at least one)
- Scheme Name
- Scheme Code

### Financial Data
**Invested:**
- Invested Amount ✓
- Invested ✓
- Investment ✓
- Cost ✓
- Purchase Value ✓

**NAV:**
- Current NAV ✓
- NAV ✓
- Latest NAV ✓
- Current Price ✓

**Units:**
- Units ✓
- Unit ✓
- Quantity ✓

**Value:**
- Current Value ✓
- Market Value ✓
- Value ✓

### Optional
- PAN
- Account Name
- Folio
- Category
- NAV Date
- Gain/Loss (calculated automatically)
- Return % (calculated automatically)

## Contact Support

If issues persist:
1. Check browser console (F12)
2. Note the exact error message
3. List your column names
4. Share a sample row (with sensitive data removed)

---

**Most import issues are due to column name mismatches - double-check your column headers!**
