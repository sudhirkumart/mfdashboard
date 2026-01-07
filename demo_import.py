#!/usr/bin/env python3
"""
Import Demo Script
Demonstrates importing portfolio data from CSV/Excel files
"""

from backend.data_import import DataImporter, import_from_csv, import_from_excel
from backend.portfolio import Portfolio
import config

print("=" * 60)
print("  DATA IMPORT DEMO")
print("=" * 60)

# First, let's export some data to test the import
print("\n1. Exporting sample data for testing...")

from backend.csv_export import CSVExporter

portfolio = Portfolio.from_file(config.SAMPLE_PORTFOLIO_FILE)
exporter = CSVExporter()

# Export to CSV
exporter.export_holdings(portfolio.data, str(config.OUTPUT_DIR / "test_holdings.csv"))
exporter.export_transactions(portfolio.data, str(config.OUTPUT_DIR / "test_transactions.csv"))
print("   > Exported test CSV files")

# Now let's import them back
print("\n2. Importing data from CSV...")

importer = DataImporter()

# Method 1: Import using convenience function
imported_portfolio = import_from_csv(
    holdings_csv=str(config.OUTPUT_DIR / "test_holdings.csv"),
    transactions_csv=str(config.OUTPUT_DIR / "test_transactions.csv"),
    output_json=str(config.OUTPUT_DIR / "imported_portfolio.json"),
    pan="IMPORTED"
)

print(f"   > Imported {len(imported_portfolio['accounts'])} account(s)")

for pan, account in imported_portfolio['accounts'].items():
    print(f"   > PAN {pan}: {len(account['holdings'])} holdings")

# Method 2: Using DataImporter class directly
print("\n3. Using DataImporter class...")

holdings = importer.import_holdings_csv(str(config.OUTPUT_DIR / "test_holdings.csv"))
print(f"   > Imported {len(holdings)} holdings")

transactions = importer.import_transactions_csv(str(config.OUTPUT_DIR / "test_transactions.csv"))
print(f"   > Imported {len(transactions)} transactions")

# Convert to portfolio format
print("\n4. Converting to portfolio format...")

portfolio_data = importer.csv_to_portfolio(
    holdings_csv=str(config.OUTPUT_DIR / "test_holdings.csv"),
    transactions_csv=str(config.OUTPUT_DIR / "test_transactions.csv"),
    pan="ABCDE1234F",
    account_name="Imported Account"
)

print(f"   > Created portfolio: {portfolio_data['portfolio_name']}")
print(f"   > Accounts: {len(portfolio_data['accounts'])}")

# Save to file
output_file = config.OUTPUT_DIR / "my_imported_portfolio.json"
importer.save_portfolio(portfolio_data, str(output_file))
print(f"   > Saved to: {output_file}")

# Test Excel import (if openpyxl is available)
print("\n5. Testing Excel import...")

try:
    # First export to Excel
    from backend.excel_export import export_to_excel

    excel_file = config.OUTPUT_DIR / "test_portfolio.xlsx"
    export_to_excel(portfolio.data, str(excel_file))
    print(f"   > Exported test Excel file: {excel_file}")

    # Now import it back
    imported_from_excel = import_from_excel(
        excel_path=str(excel_file),
        output_json=str(config.OUTPUT_DIR / "imported_from_excel.json"),
        pan="EXCEL_IMPORT"
    )

    print(f"   > Imported from Excel: {len(imported_from_excel['accounts'])} accounts")

except ImportError:
    print("   > Excel import requires openpyxl: pip install openpyxl")
except Exception as e:
    print(f"   > Excel import error: {e}")

print("\n" + "=" * 60)
print("  IMPORT DEMO COMPLETE!")
print("=" * 60)

print("\nGenerated files:")
print(f"  - {config.OUTPUT_DIR / 'imported_portfolio.json'}")
print(f"  - {config.OUTPUT_DIR / 'my_imported_portfolio.json'}")

print("\nYou can now:")
print("  1. Export your portfolio to CSV/Excel")
print("  2. Edit the files as needed")
print("  3. Import them back into the dashboard")
print("  4. Use the web dashboard import feature for JSON files")

print("\nUsage:")
print("  python demo_import.py")
