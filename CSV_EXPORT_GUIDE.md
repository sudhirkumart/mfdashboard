# CSV Export Guide

## Overview

The MF Dashboard now supports **CSV export** for all your mutual fund portfolio data. Export your holdings, transactions, and summaries to CSV format for easy use in Excel, Google Sheets, or any spreadsheet application.

## Features

### Three Export Types

1. **Holdings CSV** - Complete holdings with current valuations
2. **Transactions CSV** - All buy/sell transaction history
3. **Summary CSV** - PAN-wise portfolio summary

### Export Options

- **Individual exports** - Export specific data types separately
- **Batch export** - Export all three CSV files at once with timestamps
- **Custom filenames** - Choose your own file names and locations

## Quick Start

### Method 1: Using the Demo Script

```bash
python demo_csv_export.py
```

This will automatically export all CSV files to `data/output/` directory.

### Method 2: Python API

```python
from backend.csv_export import CSVExporter
from backend.portfolio import Portfolio

# Load portfolio
portfolio = Portfolio.from_file('data/sample_portfolio.json')

# Initialize exporter
exporter = CSVExporter()

# Export holdings
exporter.export_holdings(portfolio.data, 'output/holdings.csv')

# Export transactions
exporter.export_transactions(portfolio.data, 'output/transactions.csv')

# Export summary
exporter.export_summary(portfolio.data, 'output/summary.csv')
```

### Method 3: Export All at Once

```python
from backend.csv_export import CSVExporter

exporter = CSVExporter()

# Export all with timestamp
files = exporter.export_all(
    portfolio.data,
    output_dir='data/output',
    prefix='my_portfolio'
)

# Returns paths to all generated files
print(files['holdings'])
print(files['transactions'])
print(files['summary'])
```

### Method 4: Convenience Function

```python
from backend.csv_export import export_to_csv

# Export specific type
export_to_csv(portfolio.data, 'holdings.csv', export_type='holdings')
export_to_csv(portfolio.data, 'transactions.csv', export_type='transactions')
export_to_csv(portfolio.data, 'summary.csv', export_type='summary')
```

## CSV File Formats

### Holdings CSV

**Columns:**
- PAN
- Account Name
- Scheme Code
- Scheme Name
- Folio
- Category
- Units
- Average Buy Price
- Invested Amount
- Current NAV
- Current Value
- Gain/Loss
- Return %
- NAV Date

**Example:**
```csv
PAN,Account Name,Scheme Code,Scheme Name,Units,Invested Amount,Current Value,Gain/Loss,Return %
ABCDE1234F,John Doe,119551,HDFC Top 100 Fund,150.525,100091.25,108453.13,8361.88,8.35
```

### Transactions CSV

**Columns:**
- Date
- PAN
- Scheme Code
- Scheme Name
- Folio
- Type (PURCHASE/REDEMPTION)
- Units
- NAV
- Amount

**Example:**
```csv
Date,PAN,Scheme Name,Type,Units,NAV,Amount
2023-01-15,ABCDE1234F,HDFC Top 100 Fund,PURCHASE,75.525,650.0,49091.25
```

### Summary CSV

**Columns:**
- PAN
- Name
- Email
- Holdings Count
- Invested
- Current Value
- Gain/Loss
- Return %

**Example:**
```csv
PAN,Name,Holdings Count,Invested,Current Value,Gain/Loss,Return %
ABCDE1234F,John Doe,4,622346.21,648790.72,26444.51,4.25
TOTAL,,,6,668143.96,702253.87,34109.91,5.11
```

## Use Cases

### 1. Excel Analysis
Import CSV files into Excel for:
- Custom charts and pivot tables
- Tax calculations
- Portfolio rebalancing analysis
- Performance tracking over time

### 2. Google Sheets
- Import for cloud-based analysis
- Share with family members or advisors
- Use with Google Sheets formulas
- Combine with MF Dashboard Google Sheets functions

### 3. Accounting Software
- Import into Tally, QuickBooks, etc.
- Track investments in your books
- Generate financial reports
- Audit trail maintenance

### 4. Tax Filing
- Provide to CA/tax consultant
- Calculate capital gains
- Generate ITR schedules
- Maintain investment records

### 5. Financial Planning
- Share with financial advisor
- Portfolio review meetings
- Investment strategy analysis
- Goal tracking

## Integration with Other Features

### Export After NAV Update

```python
from backend.portfolio import Portfolio
from backend.csv_export import CSVExporter

# Load and update portfolio
portfolio = Portfolio.from_file('data/sample_portfolio.json')
portfolio.update_nav_data()  # Fetch latest NAVs

# Export with latest data
exporter = CSVExporter()
exporter.export_holdings(portfolio.data, 'latest_holdings.csv')
```

### Automated Exports

```python
from datetime import datetime
from backend.csv_export import CSVExporter

exporter = CSVExporter()

# Daily export with date in filename
today = datetime.now().strftime('%Y%m%d')
exporter.export_holdings(
    portfolio.data,
    f'exports/holdings_{today}.csv'
)
```

### Combine with Excel Export

```python
from backend.excel_export import export_to_excel
from backend.csv_export import export_to_csv

# Export both formats
export_to_excel(portfolio.data, 'portfolio.xlsx')
export_to_csv(portfolio.data, 'portfolio.csv', export_type='holdings')
```

## Command Line Usage

You can also use it as a module:

```bash
# Run the demo
python demo_csv_export.py

# Or import in Python
python -c "from backend.csv_export import CSVExporter; from backend.portfolio import Portfolio; p = Portfolio.from_file('data/sample_portfolio.json'); CSVExporter().export_holdings(p.data, 'out.csv')"
```

## File Locations

Default output directory: `data/output/`

Generated files:
- `holdings.csv` - Latest holdings export
- `transactions.csv` - Latest transactions export
- `summary.csv` - Latest summary export
- `sample_portfolio_holdings_YYYYMMDD_HHMMSS.csv` - Timestamped holdings
- `sample_portfolio_transactions_YYYYMMDD_HHMMSS.csv` - Timestamped transactions
- `sample_portfolio_summary_YYYYMMDD_HHMMSS.csv` - Timestamped summary

## Tips

1. **Regular Exports**: Export monthly for tracking performance over time
2. **Backup**: Keep CSV exports as backup of your portfolio data
3. **Version Control**: Use timestamped exports to maintain history
4. **Excel Compatibility**: CSVs open directly in Excel without any conversion
5. **Custom Analysis**: Use CSV data for your own Python/R analysis scripts

## Troubleshooting

### CSV Opens with Wrong Encoding
- Open with UTF-8 encoding in Excel
- Or use Google Sheets (automatically detects encoding)

### Numbers Show as Text
- In Excel: Use "Text to Columns" feature
- Or format cells as numbers

### Special Characters Issue
- Ensure UTF-8 encoding when opening
- Use modern spreadsheet applications

## API Reference

### CSVExporter Class

```python
class CSVExporter:
    def export_holdings(portfolio_data, output_path)
    def export_transactions(portfolio_data, output_path)
    def export_summary(portfolio_data, output_path)
    def export_all(portfolio_data, output_dir, prefix="portfolio")
```

### Convenience Functions

```python
export_to_csv(portfolio_data, output_path, export_type="holdings")
# export_type can be: "holdings", "transactions", or "summary"
```

## Examples

### Export for Tax Filing

```python
from backend.csv_export import CSVExporter

exporter = CSVExporter()

# Export transactions for the financial year
exporter.export_transactions(
    portfolio.data,
    'FY2023-24_transactions.csv'
)

# Export summary for declaration
exporter.export_summary(
    portfolio.data,
    'FY2023-24_portfolio_summary.csv'
)
```

### Monthly Portfolio Report

```python
from datetime import datetime
from backend.csv_export import CSVExporter

# Create monthly export
month = datetime.now().strftime('%Y_%B')
exporter = CSVExporter()

files = exporter.export_all(
    portfolio.data,
    output_dir=f'reports/{month}',
    prefix='monthly_report'
)
```

## Next Steps

1. Run the demo: `python demo_csv_export.py`
2. Check the exported files in `data/output/`
3. Open them in Excel or Google Sheets
4. Integrate CSV export into your workflow
5. Automate regular exports for tracking

---

**CSV Export is now available in MF Dashboard v1.0.0+**
