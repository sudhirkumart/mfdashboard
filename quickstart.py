#!/usr/bin/env python3
"""
MF Dashboard - Quickstart Demo
Demonstrates the main features of the MF Dashboard application
"""

import json
from datetime import datetime
from pathlib import Path

# Import backend modules
from backend.api import MFAPIClient
from backend.portfolio import Portfolio
from backend.calculations import calculate_portfolio_metrics
from backend.excel_export import export_to_excel
import config


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text):
    """Print a formatted section"""
    print(f"\n--- {text} ---")


def demo_api_client():
    """Demonstrate MF API Client functionality"""
    print_header("1. MF API Client Demo")

    # Initialize API client
    client = MFAPIClient(cache_enabled=True)

    # Popular scheme codes
    hdfc_top100 = "119551"
    axis_bluechip = "118989"

    print_section("Fetching Latest NAV")

    # Fetch latest NAV
    nav_data = client.get_latest_nav(hdfc_top100)
    if nav_data:
        print(f"Scheme: {nav_data['scheme_name']}")
        print(f"Date: {nav_data['date']}")
        print(f"NAV: ₹{nav_data['nav']:.2f}")

    print_section("Fetching NAV History")

    # Fetch 30-day history
    history = client.get_nav_history(hdfc_top100, days=30)
    print(f"Retrieved {len(history)} NAV entries for the last 30 days")
    if history:
        print(f"Latest: {history[0]['date']} - ₹{history[0]['nav']:.2f}")
        print(f"Oldest: {history[-1]['date']} - ₹{history[-1]['nav']:.2f}")

    print_section("Searching Schemes")

    # Search for schemes
    schemes = client.search_schemes("HDFC")
    print(f"Found {len(schemes)} schemes matching 'HDFC'")
    print("Top 5 results:")
    for i, scheme in enumerate(schemes[:5], 1):
        print(f"  {i}. {scheme['schemeName']} (Code: {scheme['schemeCode']})")


def demo_portfolio_management():
    """Demonstrate Portfolio Management"""
    print_header("2. Portfolio Management Demo")

    print_section("Loading Sample Portfolio")

    # Load sample portfolio
    portfolio = Portfolio.from_file(config.SAMPLE_PORTFOLIO_FILE)
    print(f"Portfolio: {portfolio.data['portfolio_name']}")
    print(f"Accounts: {len(portfolio.get_pan_accounts())}")
    print(f"Total Holdings: {len(portfolio.get_all_holdings())}")

    print_section("Updating NAV Data")

    # Update NAV (commented out to avoid API calls in demo)
    # Uncomment the line below to fetch real-time NAV
    # portfolio.update_nav_data()
    print("NAV update skipped in demo (uncomment to enable)")

    print_section("Portfolio Summary")

    # Calculate summary
    summary = portfolio.calculate_total_summary()
    print(f"Total Invested: ₹{summary['total_invested']:,.2f}")
    print(f"Current Value: ₹{summary['current_value']:,.2f}")
    print(f"Total Gain/Loss: ₹{summary['total_gain']:,.2f}")
    print(f"Absolute Return: {summary['absolute_return_pct']:.2f}%")
    if summary['xirr']:
        print(f"XIRR: {summary['xirr']:.2f}%")

    print_section("PAN-wise Summary")

    for pan_summary in summary['pan_summaries']:
        print(f"\nPAN: {pan_summary['pan']}")
        print(f"  Holdings: {pan_summary['holdings_count']}")
        print(f"  Invested: ₹{pan_summary['total_invested']:,.2f}")
        print(f"  Current: ₹{pan_summary['current_value']:,.2f}")
        print(f"  Gain: ₹{pan_summary['total_gain']:,.2f}")

    print_section("Top Performers")

    top_performers = portfolio.get_top_performers(limit=3)
    print("\nTop 3 Performing Holdings:")
    for i, holding in enumerate(top_performers, 1):
        print(f"\n{i}. {holding['scheme_name']}")
        print(f"   Return: {holding['return_pct']:.2f}%")
        print(f"   Invested: ₹{holding['invested']:,.2f}")
        print(f"   Current: ₹{holding['current_value']:,.2f}")

    return portfolio


def demo_calculations():
    """Demonstrate Calculation Functions"""
    print_header("3. Financial Calculations Demo")

    from backend.calculations import (
        xirr,
        calculate_absolute_return,
        calculate_cagr,
        calculate_capital_gains
    )

    print_section("XIRR Calculation")

    # Example: SIP of ₹5000 for 12 months
    transactions = [
        {'date': datetime(2023, 1, 1), 'amount': -5000},
        {'date': datetime(2023, 2, 1), 'amount': -5000},
        {'date': datetime(2023, 3, 1), 'amount': -5000},
        {'date': datetime(2023, 4, 1), 'amount': -5000},
        {'date': datetime(2023, 5, 1), 'amount': -5000},
        {'date': datetime(2023, 6, 1), 'amount': -5000},
        {'date': datetime(2024, 1, 3), 'amount': 35000}  # Current value
    ]

    xirr_result = xirr(transactions)
    if xirr_result:
        print(f"Investment: ₹30,000 (6 months SIP)")
        print(f"Current Value: ₹35,000")
        print(f"XIRR: {xirr_result * 100:.2f}%")

    print_section("Absolute Return")

    abs_return = calculate_absolute_return(100000, 125000)
    print(f"Invested: ₹1,00,000")
    print(f"Current: ₹1,25,000")
    print(f"Absolute Return: {abs_return:.2f}%")

    print_section("CAGR")

    cagr = calculate_cagr(100000, 150000, 1095)  # 3 years
    print(f"Invested: ₹1,00,000")
    print(f"Current: ₹1,50,000")
    print(f"Period: 3 years")
    print(f"CAGR: {cagr:.2f}%")

    print_section("Capital Gains")

    purchase_txns = [
        {'date': datetime(2021, 1, 1), 'units': 100, 'nav': 50},
        {'date': datetime(2023, 6, 1), 'units': 50, 'nav': 60}
    ]
    gains = calculate_capital_gains(purchase_txns, current_nav=75)

    print(f"LTCG (Long-term): ₹{gains['ltcg']:,.2f}")
    print(f"STCG (Short-term): ₹{gains['stcg']:,.2f}")
    print(f"Total Gain: ₹{gains['total_gain']:,.2f}")
    print(f"Taxable LTCG: ₹{gains['ltcg_taxable']:,.2f} (after ₹1L exemption)")
    print(f"Taxable STCG: ₹{gains['stcg_taxable']:,.2f}")


def demo_excel_export(portfolio):
    """Demonstrate Excel Export"""
    print_header("4. Excel Export Demo")

    try:
        output_file = config.OUTPUT_DIR / "demo_portfolio.xlsx"

        print(f"Exporting portfolio to Excel...")
        print(f"Output file: {output_file}")

        export_to_excel(portfolio.data, str(output_file))

        print("✓ Export successful!")
        print(f"\nThe Excel file contains:")
        print("  - Summary sheet with portfolio overview")
        print("  - Holdings sheet with formulas")
        print("  - Transactions sheet")
        print("  - PAN-wise summary sheet")

    except ImportError:
        print("⚠ openpyxl not installed. Install with: pip install openpyxl")
    except Exception as e:
        print(f"✗ Export failed: {e}")


def demo_cas_parser():
    """Demonstrate CAS Parser"""
    print_header("5. CAS Parser Demo")

    print("CAS Parser allows you to import transactions from PDF statements.")
    print("\nUsage example:")
    print("""
from backend.cas_parser import CASParser

# Initialize parser
parser = CASParser()

# Parse CAS PDF
parsed_data = parser.parse_pdf('path/to/cas_statement.pdf')

# Convert to portfolio format
portfolio = parser.convert_to_portfolio_format(parsed_data)

# Save as JSON
with open('portfolio.json', 'w') as f:
    json.dump(portfolio, f, indent=2)
""")

    try:
        from backend.cas_parser import CASParser
        print("\n✓ CAS Parser available (PyPDF2 installed)")
    except ImportError:
        print("\n⚠ PyPDF2 not installed. Install with: pip install PyPDF2")


def demo_dashboard():
    """Demonstrate Web Dashboard"""
    print_header("6. Web Dashboard Demo")

    dashboard_path = config.DASHBOARD_DIR / "index.html"

    print("Web Dashboard provides a visual interface for your portfolio.")
    print(f"\nDashboard location: {dashboard_path}")
    print("\nTo view the dashboard:")
    print("  1. Open dashboard/index.html in your web browser")
    print("  2. Or run a local web server:")
    print("     cd dashboard")
    print("     python -m http.server 8000")
    print("  3. Visit: http://localhost:8000")

    print("\nFeatures:")
    print("  - Portfolio summary cards")
    print("  - Interactive charts (allocation, performance)")
    print("  - Holdings table with search")
    print("  - PAN-wise account summary")
    print("  - Export options (Excel, JSON, PDF)")


def demo_google_sheets():
    """Demonstrate Google Sheets Integration"""
    print_header("7. Google Sheets Integration")

    print("Custom functions for Google Sheets:")
    print("\nAvailable functions:")
    print("  =MFNAV(\"scheme_code\")           - Get latest NAV")
    print("  =MFNAVDATE(\"code\", \"date\")      - Get NAV on date")
    print("  =MFSCHEMENAME(\"scheme_code\")    - Get scheme name")
    print("  =MFXIRR(dates, amounts)         - Calculate XIRR")
    print("  =MFABSRETURN(invested, current) - Absolute return")
    print("  =MFCAGR(invested, current, yrs) - Calculate CAGR")

    print("\nInstallation:")
    print("  1. Open Google Sheets")
    print("  2. Extensions > Apps Script")
    print("  3. Copy code from google_sheets/Code.gs")
    print("  4. Save and authorize")

    print(f"\nDetailed instructions: {config.GOOGLE_SHEETS_SCRIPT_DIR / 'README.md'}")


def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("  MF DASHBOARD - QUICKSTART DEMO")
    print("  Version: " + config.VERSION)
    print("=" * 60)

    print("\nThis demo showcases the main features of MF Dashboard.")
    print("Press Ctrl+C to exit at any time.\n")

    try:
        # 1. API Client Demo
        demo_api_client()

        # 2. Portfolio Management
        portfolio = demo_portfolio_management()

        # 3. Calculations
        demo_calculations()

        # 4. Excel Export
        demo_excel_export(portfolio)

        # 5. CAS Parser
        demo_cas_parser()

        # 6. Web Dashboard
        demo_dashboard()

        # 7. Google Sheets
        demo_google_sheets()

        # Summary
        print_header("Demo Complete!")
        print("\nNext Steps:")
        print("  1. Customize sample_portfolio.json with your holdings")
        print("  2. Run portfolio.update_nav_data() to fetch real-time NAVs")
        print("  3. Export to Excel for detailed analysis")
        print("  4. Set up Google Sheets integration")
        print("  5. View the web dashboard")

        print("\nUseful Commands:")
        print("  python quickstart.py         - Run this demo")
        print("  python config.py             - View configuration")
        print("  python -m backend.api        - Test API client")
        print("  python -m backend.portfolio  - Test portfolio")

        print("\nDocumentation:")
        print("  README.md                    - Main documentation")
        print("  google_sheets/README.md      - Google Sheets guide")
        print("  data/sample_portfolio.json   - Portfolio template")

        print("\n" + "=" * 60)
        print("  Thank you for using MF Dashboard!")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
