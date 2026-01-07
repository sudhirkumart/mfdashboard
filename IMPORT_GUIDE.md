# Import Guide - MF Dashboard

## Overview

MF Dashboard now supports importing portfolio data from **CSV, Excel, and JSON** files directly in the web dashboard or via Python backend.

## Web Dashboard Import (Browser-based)

### Supported Formats
- ✅ **CSV** - Full support (client-side parsing)
- ✅ **Excel (.xlsx, .xls)** - Full support (client-side via SheetJS)
- ✅ **JSON** - Full support (native)

### How to Import

1. **Open the Dashboard**
   - Visit http://localhost:8000

2. **Click Import Button**
   - Green "Import" button in the header

3. **Choose Your Method**
   - **Drag & Drop**: Drag your CSV/JSON file onto the upload area
   - **Browse**: Click the upload area to select a file
   - **Quick Import**: Click specific format buttons (CSV/Excel/JSON)

4. **Wait for Processing**
   - File uploads and processes automatically
   - Success message appears when done

5. **View Your Data**
   - Dashboard refreshes with imported data
   - All charts and tables update automatically

## CSV Format Requirements

Your CSV file must include these columns:

### Minimal Required Columns
- `Scheme Name` or `Scheme Code` (at least one)
- `Units`
- `Current NAV`

### Recommended Columns
```csv
PAN,Account Name,Scheme Code,Scheme Name,Folio,Category,Units,Invested Amount,Current NAV,Current Value,NAV Date
```

### Example CSV
```csv
PAN,Account Name,Scheme Code,Scheme Name,Units,Invested Amount,Current NAV,Current Value
ABCDE1234F,John Doe,119551,HDFC Top 100 Fund,100,65000,720.50,72050
ABCDE1234F,John Doe,118989,Axis Bluechip Fund,250,10625,48.25,12062.50
```

### Sample File
A ready-to-use sample CSV is provided at:
```
data/sample_import.csv
```

## JSON Format

JSON files should follow this structure:

```json
{
  "portfolio_name": "My Portfolio",
  "accounts": {
    "ABCDE1234F": {
      "name": "Account Name",
      "email": "email@example.com",
      "holdings": [
        {
          "scheme_code": "119551",
          "scheme_name": "HDFC Top 100 Fund",
          "folio": "12345678",
          "category": "Equity",
          "units": 100,
          "invested": 65000,
          "current_nav": 720.50,
          "current_value": 72050,
          "nav_date": "03-01-2024",
          "transactions": []
        }
      ]
    }
  }
}
```

Sample: `data/sample_portfolio.json`

## Python Backend Import

For Excel files or advanced CSV processing:

### Command Line
```bash
# Import from CSV
python -c "from backend.data_import import import_from_csv; import_from_csv('holdings.csv', 'transactions.csv', 'output.json')"

# Import from Excel
python -c "from backend.data_import import import_from_excel; import_from_excel('portfolio.xlsx', 'output.json')"

# Run demo
python demo_import.py
```

### Python Script
```python
from backend.data_import import import_from_csv, import_from_excel

# Import from CSV
portfolio = import_from_csv(
    holdings_csv='data/output/holdings.csv',
    transactions_csv='data/output/transactions.csv',
    output_json='data/imported.json',
    pan='ABCDE1234F'
)

# Import from Excel
portfolio = import_from_excel(
    excel_path='data/portfolio.xlsx',
    output_json='data/imported.json',
    pan='ABCDE1234F'
)

print(f"Imported {len(portfolio['accounts'])} account(s)")
```

## Step-by-Step: Export & Re-import

### 1. Export Your Current Portfolio
```bash
# Export to CSV
python demo_csv_export.py
```

This creates:
- `data/output/holdings.csv`
- `data/output/transactions.csv`
- `data/output/summary.csv`

### 2. Edit the CSV (Optional)
- Open in Excel or Google Sheets
- Add/edit holdings
- Update NAV values
- Save as CSV

### 3. Import Back
**Option A: Web Dashboard**
1. Open http://localhost:8000
2. Click "Import" button
3. Select `holdings.csv`
4. Done!

**Option B: Python**
```bash
python demo_import.py
```

### 4. View in Dashboard
- Dashboard reloads automatically
- All charts update
- New holdings appear in table

## Common Issues & Solutions

### Issue: "CSV file is empty or invalid"
**Solution:** Ensure your CSV has:
- Header row with column names
- At least one data row
- Proper CSV formatting

### Issue: "CSV must contain holdings data"
**Solution:** Your CSV must have either:
- `Scheme Name` column, OR
- `Scheme Code` column

### Issue: Numbers not parsing correctly
**Solution:**
- Remove currency symbols (₹, $)
- Remove commas from numbers
- Use decimal points, not commas

### Issue: Excel import shows "XLSX is not defined"
**Solution:** Refresh your browser page to load the SheetJS library. If the issue persists, check your internet connection as the library loads from CDN.

## File Size Limits

### Web Dashboard
- **CSV**: Up to 5MB (thousands of holdings)
- **Excel**: Up to 10MB (most portfolios)
- **JSON**: Up to 10MB

### Python Backend
- **All formats**: No practical limit
- Handles large portfolios efficiently

## Data Validation

The importer automatically:
- ✅ Validates required fields
- ✅ Converts data types (strings to numbers)
- ✅ Skips empty rows
- ✅ Handles quoted CSV fields
- ✅ Groups by PAN account
- ✅ Filters out TOTAL rows

## Tips for Best Results

1. **Use Exported CSVs as Templates**
   - Export your current portfolio
   - Use as template for new entries

2. **Keep Column Names Exact**
   - Match exported column names exactly
   - Case-sensitive matching

3. **Clean Your Data**
   - Remove special characters
   - Ensure consistent date formats
   - Check for duplicate rows

4. **Test with Sample First**
   - Try importing `data/sample_import.csv`
   - Verify format works before using your data

5. **Backup Before Import**
   - Export current portfolio first
   - Save as backup before importing new data

## Advanced: Programmatic Import

### Import Multiple Files
```python
from backend.data_import import DataImporter

importer = DataImporter()

# Import from multiple CSVs
portfolio1 = importer.csv_to_portfolio('holdings1.csv', pan='PAN1')
portfolio2 = importer.csv_to_portfolio('holdings2.csv', pan='PAN2')

# Merge portfolios
merged = {
    'portfolio_name': 'Merged Portfolio',
    'accounts': {**portfolio1['accounts'], **portfolio2['accounts']}
}

importer.save_portfolio(merged, 'merged.json')
```

### Custom Field Mapping
```python
from backend.data_import import DataImporter

importer = DataImporter()
holdings = importer.import_holdings_csv('custom.csv')

# Modify as needed
for holding in holdings:
    holding['custom_field'] = 'value'

# Save
portfolio = importer.csv_to_portfolio(...)
```

## Export-Import Workflow Example

```bash
# 1. Export current portfolio
python demo_csv_export.py

# 2. Edit CSV in Excel
# (Manual step - add/edit data)

# 3. Import edited CSV
python demo_import.py

# 4. View in dashboard
# Open http://localhost:8000 and click Import
# Select the generated JSON file
```

## Support

### Quick Test
```bash
# Test CSV import
python demo_import.py

# Test web dashboard
# 1. Open http://localhost:8000
# 2. Click "Import"
# 3. Select data/sample_import.csv
```

### Troubleshooting
1. Check CSV format matches examples
2. Ensure required columns present
3. Verify file encoding (UTF-8 recommended)
4. Test with sample files first

---

**Happy Importing!** 📊

For more help, see:
- `README.md` - Main documentation
- `CSV_EXPORT_GUIDE.md` - Export documentation
- `demo_import.py` - Working examples
