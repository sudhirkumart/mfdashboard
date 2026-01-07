# Excel Import Guide

## Overview

MF Dashboard now supports **direct Excel import** in the web browser! No Python backend needed for .xlsx and .xls files.

## ✨ Features

- ✅ Import Excel files directly in browser
- ✅ Supports .xlsx and .xls formats
- ✅ Automatic sheet detection (looks for "Holdings" sheet)
- ✅ Multi-PAN account support
- ✅ Drag & drop upload
- ✅ Real-time validation and feedback

## 🚀 Quick Start

### Step 1: Prepare Your Excel File

Your Excel file should have a sheet named **"Holdings"** (or it will use the first sheet) with these columns:

**Required Columns:**
- `Scheme Name` OR `Scheme Code`
- `Units`
- `Current NAV`

**Recommended Columns:**
```
PAN | Account Name | Scheme Code | Scheme Name | Folio | Category | Units | Invested Amount | Current NAV | Current Value | NAV Date
```

### Step 2: Import in Dashboard

1. **Open Dashboard**: http://localhost:8000
2. **Click Import**: Green "Import" button in header
3. **Upload Excel**:
   - Drag & drop your .xlsx file, OR
   - Click "Import from Excel" button
4. **Success!**: Dashboard refreshes with your data

## 📊 Excel File Format

### Example Structure

```
Sheet: Holdings

| PAN        | Scheme Name                  | Units | Invested | Current NAV | Current Value |
|------------|------------------------------|-------|----------|-------------|---------------|
| AAAAA1111A | HDFC Top 100 Fund            | 100   | 65000    | 720.50      | 72050         |
| AAAAA1111A | Axis Bluechip Fund           | 250   | 10625    | 48.25       | 12062.50      |
| BBBBB2222B | SBI Small Cap Fund           | 80    | 4968     | 95.80       | 7664          |
```

### Column Details

| Column | Required | Type | Description |
|--------|----------|------|-------------|
| PAN | Optional | Text | PAN number (defaults to "IMPORTED") |
| Account Name | Optional | Text | Account holder name |
| Scheme Code | Optional* | Text | Mutual fund scheme code |
| Scheme Name | Optional* | Text | Full scheme name |
| Folio | Optional | Text | Folio number |
| Category | Optional | Text | Fund category (Equity, Debt, etc.) |
| Units | Required | Number | Number of units held |
| Invested Amount | Recommended | Number | Total amount invested |
| Current NAV | Required | Number | Latest NAV value |
| Current Value | Optional | Number | Current holding value |
| NAV Date | Optional | Date | Date of NAV |

*At least one of Scheme Code or Scheme Name is required

## 🔄 Complete Workflow

### Export → Edit → Import

1. **Export your portfolio**
   ```
   Click "Export" → "Export to Excel" in dashboard
   (Or use Python: python demo_csv_export.py)
   ```

2. **Edit in Excel**
   - Open the exported file
   - Add new holdings
   - Update NAV values
   - Modify transactions
   - Save as .xlsx

3. **Import back**
   - Drag the file into dashboard
   - Or click "Import from Excel"
   - Done!

## 💡 Tips & Best Practices

### 1. Use Exported Files as Templates
The easiest way is to export your current portfolio and use it as a template:
```
Dashboard → Export → Excel → Edit → Import
```

### 2. Sheet Names
- The importer looks for a sheet named **"Holdings"**
- If not found, it uses the **first sheet**
- Make sure your data is in the active sheet

### 3. Data Formatting
- **Numbers**: No commas, use decimal points
  - ✅ Good: `72050.25`
  - ❌ Bad: `72,050.25` or `₹72050`
- **Dates**: Any Excel date format works
- **Text**: Quotes not needed for scheme names

### 4. Multiple Accounts
You can import multiple PAN accounts in one file:
```
| PAN        | Scheme Name     | ... |
|------------|-----------------|-----|
| AAAAA1111A | HDFC Fund       | ... |
| AAAAA1111A | Axis Fund       | ... |
| BBBBB2222B | SBI Fund        | ... |
| BBBBB2222B | ICICI Fund      | ... |
```

### 5. Handling Formulas
- Excel formulas are automatically evaluated
- Current Value can be a formula: `=Units * Current NAV`
- Gain/Loss can be: `=Current Value - Invested Amount`

## 🔧 Troubleshooting

### Issue: "No sheets found in Excel file"
**Solution**: Ensure your Excel file has at least one worksheet with data

### Issue: "Excel sheet is empty"
**Solution**:
- Check that your sheet has data rows (not just headers)
- Verify you're using the correct sheet
- Try exporting and re-importing

### Issue: "Must contain holdings data"
**Solution**: Your Excel must have either:
- A column named "Scheme Name", OR
- A column named "Scheme Code"

### Issue: Numbers importing as text
**Solution**: In Excel:
1. Select the column
2. Format → Number
3. Remove any currency symbols or commas
4. Save and re-import

### Issue: "XLSX is not defined"
**Solution**:
- Refresh your browser page
- Check internet connection (SheetJS loads from CDN)
- Clear browser cache

### Issue: Large file not loading
**Solution**:
- Excel files up to 10MB supported
- For larger files, use Python backend:
  ```bash
  python -c "from backend.data_import import import_from_excel; import_from_excel('large_file.xlsx', 'output.json')"
  ```

## 📝 Sample Excel Files

### Create Sample File

**Method 1: Export from Dashboard**
1. Open http://localhost:8000
2. Click "Export" → "Export to Excel"
3. Opens in Excel - this is your template!

**Method 2: Manual Creation**
1. Open Excel
2. Create sheet named "Holdings"
3. Add headers in first row
4. Add your data starting from row 2
5. Save as .xlsx

**Method 3: From CSV**
1. Export to CSV from dashboard
2. Open CSV in Excel
3. Save As → Excel Workbook (.xlsx)

### Test Import

Try importing one of these:
- `data/sample_import.csv` (save as .xlsx in Excel)
- Any exported Excel file from the dashboard
- Your own portfolio Excel

## 🎯 Common Use Cases

### 1. Bulk Data Entry
- Create Excel with all your holdings
- One row per fund
- Import once instead of manual entry

### 2. Regular Updates
- Export portfolio monthly
- Update NAV values in Excel
- Import to refresh dashboard

### 3. Multiple Sources
- Get data from broker statements
- Format in Excel to match template
- Import into dashboard

### 4. Sharing with Advisor
- Export portfolio to Excel
- Share with financial advisor
- They can review and return
- Import updated version

### 5. Backup and Restore
- Export to Excel regularly
- Keep as backup
- Import anytime to restore

## ⚙️ Technical Details

### Browser Parsing
- Uses SheetJS (xlsx.js) library
- Client-side processing (no server needed)
- Works offline after initial load

### Supported Excel Versions
- Excel 2007+ (.xlsx)
- Excel 97-2003 (.xls)
- LibreOffice Calc
- Google Sheets (export as Excel)

### Performance
- Small files (<1MB): Instant
- Medium files (1-5MB): 1-2 seconds
- Large files (5-10MB): 3-5 seconds

## 🔗 Related

- **CSV Import**: See `CSV_EXPORT_GUIDE.md`
- **JSON Import**: Native support, just drag & drop
- **Python Backend**: For advanced processing see `backend/data_import.py`

---

**Excel import is now fully functional in the browser!** 📊✨

For help: Open http://localhost:8000 and click Import
