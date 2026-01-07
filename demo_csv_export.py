#!/usr/bin/env python3
"""
CSV Export Demo
Demonstrates exporting portfolio data to CSV format
"""

from backend.csv_export import CSVExporter
from backend.portfolio import Portfolio
import config

print("=" * 60)
print("  CSV EXPORT DEMO")
print("=" * 60)

# Load sample portfolio
print("\n1. Loading sample portfolio...")
portfolio = Portfolio.from_file(config.SAMPLE_PORTFOLIO_FILE)
print(f"   > Loaded: {portfolio.data['portfolio_name']}")
print(f"   > Accounts: {len(portfolio.get_pan_accounts())}")
print(f"   > Holdings: {len(portfolio.get_all_holdings())}")

# Initialize CSV exporter
print("\n2. Initializing CSV exporter...")
exporter = CSVExporter()
print("   > CSV exporter ready")

# Export all data
print("\n3. Exporting to CSV files...")
output_dir = config.OUTPUT_DIR
files = exporter.export_all(portfolio.data, str(output_dir), prefix="sample_portfolio")

print("\n   Generated files:")
for file_type, file_path in files.items():
    print(f"   > {file_type.capitalize()}: {file_path}")

# Export individual files with custom names
print("\n4. Exporting individual CSV files...")

# Export holdings
holdings_file = output_dir / "holdings.csv"
exporter.export_holdings(portfolio.data, str(holdings_file))
print(f"   > Holdings exported: {holdings_file}")

# Export transactions
transactions_file = output_dir / "transactions.csv"
exporter.export_transactions(portfolio.data, str(transactions_file))
print(f"   > Transactions exported: {transactions_file}")

# Export summary
summary_file = output_dir / "summary.csv"
exporter.export_summary(portfolio.data, str(summary_file))
print(f"   > Summary exported: {summary_file}")

print("\n" + "=" * 60)
print("  CSV EXPORT COMPLETE!")
print("=" * 60)

print("\nYou can now:")
print("  • Open the CSV files in Excel, Google Sheets, or any spreadsheet")
print("  • Import into your accounting software")
print("  • Use for tax calculations")
print("  • Share with your financial advisor")

print("\nFile locations:")
print(f"  {output_dir}")
