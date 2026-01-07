# MF Dashboard - Mutual Fund Portfolio Tracker

A comprehensive mutual fund portfolio management system with support for NAV fetching, XIRR calculations, capital gains analysis, Excel export, Google Sheets integration, and an interactive web dashboard.

## Features

- **Real-time NAV Fetching**: Automatically fetch latest NAV data from MFAPI.in with intelligent caching
- **Financial Calculations**:
  - XIRR (Extended Internal Rate of Return)
  - Absolute returns
  - CAGR (Compound Annual Growth Rate)
  - Capital gains (LTCG/STCG) with tax calculations
- **Multiple PAN Support**: Manage portfolios across multiple PAN accounts
- **CAS Parser**: Import transactions from Consolidated Account Statement PDFs
- **Excel Export**: Generate detailed Excel reports with formulas and formatting
- **Google Sheets Integration**: Custom functions for real-time NAV data in spreadsheets
- **Web Dashboard**: Interactive charts and portfolio visualization
- **Portfolio Analytics**: Performance tracking, top performers, category-wise allocation

## Project Structure

```
mfdashboard/
├── backend/                    # Python backend modules
│   ├── api.py                 # NAV fetching from MFAPI.in
│   ├── calculations.py        # XIRR, returns, capital gains
│   ├── portfolio.py           # Portfolio management
│   ├── cas_parser.py          # CAS PDF parsing
│   └── excel_export.py        # Excel generation
├── google_sheets/             # Google Sheets Apps Script
│   ├── Code.gs               # Custom functions
│   └── README.md             # Installation guide
├── dashboard/                 # Web dashboard
│   ├── index.html            # Main page
│   ├── style.css             # Styling
│   └── app.js                # JavaScript logic
├── data/                      # Data storage
│   ├── cache/                # NAV cache
│   ├── output/               # Generated reports
│   └── sample_portfolio.json # Portfolio template
├── config.py                  # Configuration settings
├── quickstart.py              # Demo script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Navigate to project directory**

```bash
cd mfdashboard
```

2. **Install dependencies**

```bash
# Install core dependencies
pip install -r requirements.txt

# Or install minimal dependencies
pip install requests python-dateutil openpyxl
```

3. **Verify installation**

```bash
python config.py
```

## Quick Start

### 1. Run the Demo

```bash
python quickstart.py
```

This will demonstrate all features including:
- Fetching NAV data
- Portfolio management
- Financial calculations
- Excel export
- Dashboard and Google Sheets setup

### 2. Create Your Portfolio

Edit `data/sample_portfolio.json` with your holdings or use the sample as a template.

### 3. Update NAV Data

```python
from backend.portfolio import Portfolio

# Load portfolio
portfolio = Portfolio.from_file('data/sample_portfolio.json')

# Fetch latest NAV for all holdings
portfolio.update_nav_data()

# Get summary
summary = portfolio.calculate_total_summary()
print(f"Total Invested: ₹{summary['total_invested']:,.2f}")
print(f"Current Value: ₹{summary['current_value']:,.2f}")
print(f"XIRR: {summary['xirr']:.2f}%")
```

### 4. Export to Excel

```python
from backend.excel_export import export_to_excel

# Export portfolio
export_to_excel(portfolio.data, 'data/output/my_portfolio.xlsx')
```

### 5. View Dashboard

```bash
cd dashboard
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Usage Examples

### NAV Fetching

```python
from backend.api import MFAPIClient

client = MFAPIClient()

# Get latest NAV
nav = client.get_latest_nav("119551")
print(f"Scheme: {nav['scheme_name']}")
print(f"NAV: ₹{nav['nav']}")
print(f"Date: {nav['date']}")

# Get NAV history
history = client.get_nav_history("119551", days=365)

# Search schemes
schemes = client.search_schemes("HDFC")
for scheme in schemes[:5]:
    print(f"{scheme['schemeName']} - {scheme['schemeCode']}")
```

### Financial Calculations

```python
from backend.calculations import xirr, calculate_cagr
from datetime import datetime

# XIRR calculation for SIP
transactions = [
    {'date': datetime(2023, 1, 1), 'amount': -10000},
    {'date': datetime(2023, 6, 1), 'amount': -5000},
    {'date': datetime(2024, 1, 1), 'amount': 18000}
]
xirr_value = xirr(transactions)
print(f"XIRR: {xirr_value * 100:.2f}%")

# CAGR calculation
cagr = calculate_cagr(100000, 150000, 1095)  # 3 years
print(f"CAGR: {cagr:.2f}%")
```

### Portfolio Management

```python
from backend.portfolio import Portfolio

# Load and update portfolio
portfolio = Portfolio.from_file('data/sample_portfolio.json')
portfolio.update_nav_data()

# Get top performers
top_funds = portfolio.get_top_performers(limit=5)
for fund in top_funds:
    print(f"{fund['scheme_name']}: {fund['return_pct']:.2f}%")

# Get PAN-wise summary
for pan in portfolio.get_pan_accounts():
    summary = portfolio.calculate_pan_summary(pan)
    print(f"{pan}: ₹{summary['current_value']:,.2f}")
```

### CAS Parsing

```python
from backend.cas_parser import CASParser

parser = CASParser()

# Parse CAS PDF
parsed_data = parser.parse_pdf('path/to/cas_statement.pdf')

# Convert to portfolio format
portfolio = parser.convert_to_portfolio_format(parsed_data)

# Export to JSON
parser.export_to_json('data/output/portfolio.json', parsed_data)
```

## Google Sheets Integration

### Setup

1. Open Google Sheets
2. Go to **Extensions** > **Apps Script**
3. Copy code from `google_sheets/Code.gs`
4. Save and authorize

### Available Functions

```
=MFNAV("119551")                          → Latest NAV
=MFNAVDATE("119551", "01-12-2023")       → NAV on specific date
=MFSCHEMENAME("119551")                   → Scheme name
=MFXIRR(A2:A10, B2:B10)                  → XIRR calculation
=MFABSRETURN(100000, 125000)             → Absolute return %
=MFCAGR(100000, 150000, 3)               → CAGR %
```

See `google_sheets/README.md` for detailed documentation.

## Web Dashboard

The dashboard provides:
- Portfolio summary cards (invested, current value, gains, XIRR)
- Interactive charts (allocation pie chart, performance bar chart)
- Holdings table with search functionality
- PAN-wise account summaries
- Export options (Excel, JSON, PDF)

Features sample data for demonstration. Connect to your portfolio JSON for live data.

## Configuration

Edit `config.py` to customize:

```python
CACHE_DURATION_HOURS = 24              # Cache NAV data for 24 hours
LTCG_EXEMPTION_EQUITY = 100000        # ₹1 lakh LTCG exemption
EXCEL_EXPORT_DIR = "data/output"      # Export directory
```

## Finding Scheme Codes

### Method 1: MFAPI.in Website
Visit https://www.mfapi.in/ and search for your fund

### Method 2: API Search
```python
from backend.api import MFAPIClient

client = MFAPIClient()
schemes = client.search_schemes("HDFC Top 100")
for scheme in schemes:
    print(f"{scheme['schemeName']}: {scheme['schemeCode']}")
```

### Popular Schemes
- HDFC Top 100: 119551
- Axis Bluechip: 118989
- SBI Small Cap: 120503
- Parag Parikh Flexi Cap: 122639

## Capital Gains Tax (India)

### Equity Funds
- **Long-term** (>1 year): 10% above ₹1 lakh exemption
- **Short-term** (≤1 year): 15%

### Debt Funds
- **Long-term** (>3 years): 20% with indexation
- **Short-term** (≤3 years): As per income tax slab

The system automatically calculates LTCG/STCG using FIFO method.

## API Data Source

This project uses **MFAPI.in** (https://www.mfapi.in/) for NAV data:
- Free and open API
- Daily NAV updates
- Historical data available
- No authentication required

## Troubleshooting

### Import Errors
```bash
pip install requests openpyxl PyPDF2
```

### NAV Not Updating
- Check internet connection
- Verify scheme codes are correct
- Clear cache: Delete files in `data/cache/`
- Test API: https://api.mfapi.in/mf/119551

### Excel Export Fails
```bash
pip install openpyxl
```

### CAS Parser Issues
```bash
pip install PyPDF2
```

## File Structure

### Backend Modules
- `api.py` - NAV fetching with caching (22KB)
- `calculations.py` - Financial calculations (9KB)
- `portfolio.py` - Portfolio management (11KB)
- `cas_parser.py` - PDF parsing (8KB)
- `excel_export.py` - Excel export (10KB)

### Google Sheets
- `Code.gs` - Apps Script functions (8KB)
- `README.md` - Setup guide (6KB)

### Dashboard
- `index.html` - Web interface (6KB)
- `style.css` - Styling (7KB)
- `app.js` - Logic and charts (9KB)

## Development

### Running Tests
```bash
# Test individual modules
python -m backend.api
python -m backend.calculations
python -m backend.portfolio
```

### Code Style
The project follows PEP 8 guidelines with comprehensive documentation.

## Contributing

Contributions are welcome! Areas for improvement:
- Additional chart types in dashboard
- Enhanced CAS parser for multiple formats
- PDF report generation
- Mobile app integration
- Tax report generation
- SIP planner
- Goal tracking

## Disclaimer

This software is for informational purposes only and does not constitute financial advice. Users should:
- Verify all calculations independently
- Consult with financial advisors for investment decisions
- Check tax calculations with tax professionals
- Understand that past performance doesn't guarantee future returns

NAV data is sourced from MFAPI.in. The authors are not responsible for data accuracy.

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Acknowledgments

- **MFAPI.in** for providing free mutual fund data API
- **Chart.js** for dashboard visualizations
- **openpyxl** for Excel generation
- All contributors and users of this project

---

**Version**: 1.0.0
**Last Updated**: January 2024

Made with care for Indian mutual fund investors
