# Getting Started with MF Dashboard

## Step-by-Step Guide

### Step 1: Verify Installation
```bash
# Check Python version (3.8+ required)
python --version

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Choose Your Interface

#### Option A: Web Dashboard (Recommended)
**Best for:** Visual users who want charts and modern UI

```bash
python web_app.py
```

Then open in browser: http://localhost:5000

**What you can do:**
- View portfolio with pie charts
- Search and add transactions
- Calculate capital gains
- See real-time NAV updates

---

#### Option B: CLI Application
**Best for:** Terminal users, automation, SSH access

```bash
python portfolio_app.py
```

Follow the interactive menu:
1. Add Transaction
2. View Portfolio
3. Calculate Capital Gains
4. View Transactions

---

#### Option C: Python API
**Best for:** Developers, integration, scripting

```python
from mfapi_fetcher import MFAPIFetcher
from portfolio_manager import PortfolioManager

# See example_usage.py for full examples
python example_usage.py
```

---

#### Option D: Google Sheets
**Best for:** Spreadsheet users, sharing with others

1. Create new Google Sheet
2. Extensions > Apps Script
3. Copy code from `sheets_integration.js`
4. Save and authorize
5. Refresh sheet
6. Use "MF Portfolio" menu

---

### Step 3: Add Your First Transaction

#### Via Web Dashboard:
1. Click "Add Transaction" tab
2. Search for scheme (e.g., "HDFC Equity")
3. Select from results
4. Choose BUY or SELL
5. Enter units and NAV
6. Click "Add Transaction"

#### Via CLI:
1. Select option 1 "Add Transaction"
2. Search for scheme
3. Select from results
4. Enter transaction details
5. Confirm

#### Via Python:
```python
from portfolio_manager import PortfolioManager

portfolio = PortfolioManager()
portfolio.add_transaction(
    date='2025-01-01',
    scheme_code='119551',
    scheme_name='HDFC Equity Fund - Direct Growth',
    transaction_type='BUY',
    units=100,
    nav=50.25
)
```

---

### Step 4: View Your Portfolio

The system automatically:
1. Fetches latest NAV from MFAPI.in
2. Caches for fast access
3. Calculates current value
4. Shows gains/losses

**Portfolio shows:**
- Total invested amount
- Current portfolio value
- Absolute gain/loss
- Percentage returns
- Individual holding details

---

### Step 5: Calculate Capital Gains

When you sell units, calculate realized gains:

1. Select "Calculate Capital Gains"
2. Choose fund type:
   - Equity (LTCG: >1 year)
   - Debt (LTCG: >3 years)
3. View report showing:
   - Short Term Capital Gains (STCG)
   - Long Term Capital Gains (LTCG)
   - Detailed transaction-wise breakdown

**Example:**
- Buy 100 units @ Rs.45 on 2024-01-01
- Sell 50 units @ Rs.55 on 2025-01-01
- Result: LTCG of Rs.500 (holding period: 365 days)

---

## Common Workflows

### Workflow 1: Track Existing Portfolio

1. **Gather your data:**
   - Transaction history from AMC/broker
   - Date, scheme, units, NAV for each

2. **Enter transactions:**
   - Start with oldest transaction
   - Add all BUYs first
   - Then add SELLs

3. **View portfolio:**
   - System fetches current NAV
   - Shows total value and gains

### Workflow 2: Calculate Tax

1. **Enter all transactions** (including sells)

2. **Calculate capital gains:**
   - Choose equity or debt
   - System calculates STCG/LTCG

3. **Tax calculation:**
   - Equity STCG: 15%
   - Equity LTCG: 10% (>Rs.1L)
   - Debt STCG: As per slab
   - Debt LTCG: 20% with indexation

### Workflow 3: Regular Monitoring

1. **Open web dashboard:**
   ```bash
   python web_app.py
   ```

2. **Bookmark:** http://localhost:5000

3. **Check daily/weekly:**
   - Portfolio automatically fetches latest NAV
   - See updated values and gains
   - Track performance over time

### Workflow 4: SIP Tracking

For monthly SIP investments:

1. **Add transaction each month:**
   - Date: SIP debit date
   - Type: BUY
   - Units: As per statement
   - NAV: On that date

2. **View average NAV:**
   - Portfolio shows average purchase price
   - Track cost averaging effect

---

## Tips & Best Practices

### Data Entry
- Always use YYYY-MM-DD date format
- Get exact NAV from AMC statement
- Verify scheme code before entering
- Add transactions in chronological order

### Performance
- Cache speeds up repeated queries 50-500x
- Default TTL: 1 hour (configurable)
- Clear cache if you need fresh data
- NAV updates once daily (around 8-9 PM)

### Accuracy
- Match transactions with broker statements
- Verify capital gains with form 16
- Use correct fund type (equity/debt)
- Cross-check scheme codes

### Backup
- `portfolio.json` contains all your data
- Backup this file regularly
- Keep in version control or cloud storage
- Easy to restore or share

---

## Quick Reference

### File Locations
```
portfolio.json       # Your portfolio data
.mfcache/           # Cached API responses
requirements.txt    # Dependencies
```

### Important URLs
- Web Dashboard: http://localhost:5000
- MFAPI.in: https://www.mfapi.in/
- Project Docs: README.md

### Key Commands
```bash
# Run web dashboard
python web_app.py

# Run CLI app
python portfolio_app.py

# Run examples
python example_usage.py

# Quick launcher
python run.py
```

### Keyboard Shortcuts (CLI)
- `Ctrl+C` - Exit/Cancel
- `0` - Back/Exit from menu
- `Enter` - Confirm selection

---

## Troubleshooting

### "No module named 'requests'"
```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"
Edit `web_app.py`, change:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001
```

### "No schemes found"
- Check internet connection
- Verify MFAPI.in is accessible: https://api.mfapi.in/mf
- Try clearing cache

### "Cache not updating"
```python
from mfapi_fetcher import MFAPIFetcher
fetcher = MFAPIFetcher()
fetcher.clear_cache()  # Clear all
# Or
fetcher.clear_cache('119551')  # Clear specific scheme
```

### Portfolio value seems wrong
- Verify NAV values are current
- Check transaction dates are correct
- Ensure units are accurate
- Refresh NAV data

---

## Next Steps

After basic setup:

1. **Explore all features:**
   - Try different views
   - Test capital gains calculator
   - Experiment with charts

2. **Customize:**
   - Adjust cache TTL in code
   - Modify web dashboard styling
   - Add your own calculations

3. **Automate:**
   - Schedule NAV updates
   - Export reports
   - Integrate with other tools

4. **Share:**
   - Use Google Sheets integration
   - Export portfolio data
   - Share reports with advisor

---

## Need Help?

1. **Read documentation:**
   - README.md - Full API reference
   - PROJECT_SUMMARY.md - Technical details
   - This file - Getting started guide

2. **Check examples:**
   - example_usage.py - Python API examples
   - templates/dashboard.html - Web interface code
   - sheets_integration.js - Google Sheets code

3. **Test with sample data:**
   - Use example scheme: 119551 (HDFC fund)
   - Add dummy transactions
   - Practice before real data

---

**Ready to start? Run:** `python run.py`
