"""
CSV Export Module
Exports portfolio data to CSV format for easy import into spreadsheets
"""

import csv
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVExporter:
    """Export portfolio data to CSV files"""

    def __init__(self):
        """Initialize CSV exporter"""
        pass

    def export_holdings(self, portfolio_data: Dict, output_path: str) -> None:
        """
        Export holdings to CSV

        Args:
            portfolio_data: Portfolio data dictionary
            output_path: Output CSV file path
        """
        logger.info(f"Exporting holdings to CSV: {output_path}")

        holdings_rows = []

        # Collect all holdings
        for pan, account in portfolio_data.get('accounts', {}).items():
            for holding in account.get('holdings', []):
                invested = holding.get('invested', 0)
                current_value = holding.get('current_value', 0)
                units = holding.get('units', 0)

                avg_price = invested / units if units > 0 else 0
                gain_loss = current_value - invested
                return_pct = (gain_loss / invested * 100) if invested > 0 else 0

                row = {
                    'PAN': pan,
                    'Account Name': account.get('name', ''),
                    'Scheme Code': holding.get('scheme_code', ''),
                    'Scheme Name': holding.get('scheme_name', ''),
                    'Folio': holding.get('folio', ''),
                    'Category': holding.get('category', ''),
                    'Units': units,
                    'Average Buy Price': round(avg_price, 2),
                    'Invested Amount': round(invested, 2),
                    'Current NAV': holding.get('current_nav', 0),
                    'Current Value': round(current_value, 2),
                    'Gain/Loss': round(gain_loss, 2),
                    'Return %': round(return_pct, 2),
                    'NAV Date': holding.get('nav_date', '')
                }
                holdings_rows.append(row)

        # Write to CSV
        if holdings_rows:
            fieldnames = holdings_rows[0].keys()

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(holdings_rows)

            logger.info(f"Exported {len(holdings_rows)} holdings to {output_path}")
        else:
            logger.warning("No holdings to export")

    def export_transactions(self, portfolio_data: Dict, output_path: str) -> None:
        """
        Export all transactions to CSV

        Args:
            portfolio_data: Portfolio data dictionary
            output_path: Output CSV file path
        """
        logger.info(f"Exporting transactions to CSV: {output_path}")

        transaction_rows = []

        # Collect all transactions
        for pan, account in portfolio_data.get('accounts', {}).items():
            for holding in account.get('holdings', []):
                scheme_name = holding.get('scheme_name', '')
                scheme_code = holding.get('scheme_code', '')

                for txn in holding.get('transactions', []):
                    row = {
                        'Date': txn.get('date', ''),
                        'PAN': pan,
                        'Scheme Code': scheme_code,
                        'Scheme Name': scheme_name,
                        'Folio': holding.get('folio', ''),
                        'Type': txn.get('type', '').upper(),
                        'Units': txn.get('units', 0),
                        'NAV': txn.get('nav', 0),
                        'Amount': round(txn.get('units', 0) * txn.get('nav', 0), 2)
                    }
                    transaction_rows.append(row)

        # Sort by date
        transaction_rows.sort(key=lambda x: x['Date'])

        # Write to CSV
        if transaction_rows:
            fieldnames = transaction_rows[0].keys()

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(transaction_rows)

            logger.info(f"Exported {len(transaction_rows)} transactions to {output_path}")
        else:
            logger.warning("No transactions to export")

    def export_summary(self, portfolio_data: Dict, output_path: str) -> None:
        """
        Export portfolio summary to CSV

        Args:
            portfolio_data: Portfolio data dictionary
            output_path: Output CSV file path
        """
        logger.info(f"Exporting summary to CSV: {output_path}")

        summary_rows = []

        # Overall summary
        total_invested = 0
        total_current = 0
        total_holdings = 0

        for pan, account in portfolio_data.get('accounts', {}).items():
            pan_invested = 0
            pan_current = 0
            holdings_count = len(account.get('holdings', []))

            for holding in account.get('holdings', []):
                pan_invested += holding.get('invested', 0)
                pan_current += holding.get('current_value', 0)

            total_invested += pan_invested
            total_current += pan_current
            total_holdings += holdings_count

            pan_gain = pan_current - pan_invested
            pan_return = (pan_gain / pan_invested * 100) if pan_invested > 0 else 0

            row = {
                'PAN': pan,
                'Name': account.get('name', ''),
                'Email': account.get('email', ''),
                'Holdings Count': holdings_count,
                'Invested': round(pan_invested, 2),
                'Current Value': round(pan_current, 2),
                'Gain/Loss': round(pan_gain, 2),
                'Return %': round(pan_return, 2)
            }
            summary_rows.append(row)

        # Add total row
        total_gain = total_current - total_invested
        total_return = (total_gain / total_invested * 100) if total_invested > 0 else 0

        total_row = {
            'PAN': 'TOTAL',
            'Name': '',
            'Email': '',
            'Holdings Count': total_holdings,
            'Invested': round(total_invested, 2),
            'Current Value': round(total_current, 2),
            'Gain/Loss': round(total_gain, 2),
            'Return %': round(total_return, 2)
        }
        summary_rows.append(total_row)

        # Write to CSV
        if summary_rows:
            fieldnames = summary_rows[0].keys()

            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_rows)

            logger.info(f"Exported summary to {output_path}")

    def export_all(self, portfolio_data: Dict, output_dir: str, prefix: str = "portfolio") -> Dict[str, str]:
        """
        Export all data (holdings, transactions, summary) to separate CSV files

        Args:
            portfolio_data: Portfolio data dictionary
            output_dir: Output directory path
            prefix: Filename prefix (default: "portfolio")

        Returns:
            Dictionary with paths to generated files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        files = {}

        # Export holdings
        holdings_file = output_path / f"{prefix}_holdings_{timestamp}.csv"
        self.export_holdings(portfolio_data, str(holdings_file))
        files['holdings'] = str(holdings_file)

        # Export transactions
        transactions_file = output_path / f"{prefix}_transactions_{timestamp}.csv"
        self.export_transactions(portfolio_data, str(transactions_file))
        files['transactions'] = str(transactions_file)

        # Export summary
        summary_file = output_path / f"{prefix}_summary_{timestamp}.csv"
        self.export_summary(portfolio_data, str(summary_file))
        files['summary'] = str(summary_file)

        logger.info(f"Exported all CSV files to {output_dir}")
        return files


def export_to_csv(portfolio_data: Dict, output_path: str, export_type: str = "holdings") -> None:
    """
    Convenience function to export portfolio to CSV

    Args:
        portfolio_data: Portfolio data dictionary
        output_path: Output CSV file path
        export_type: Type of export - "holdings", "transactions", or "summary"
    """
    exporter = CSVExporter()

    if export_type == "holdings":
        exporter.export_holdings(portfolio_data, output_path)
    elif export_type == "transactions":
        exporter.export_transactions(portfolio_data, output_path)
    elif export_type == "summary":
        exporter.export_summary(portfolio_data, output_path)
    else:
        raise ValueError(f"Invalid export_type: {export_type}. Use 'holdings', 'transactions', or 'summary'")


if __name__ == "__main__":
    print("CSV Export Module")
    print("=" * 50)
    print("\nExample usage:")
    print("""
from backend.csv_export import CSVExporter, export_to_csv

# Initialize exporter
exporter = CSVExporter()

# Export holdings
exporter.export_holdings(portfolio_data, 'output/holdings.csv')

# Export transactions
exporter.export_transactions(portfolio_data, 'output/transactions.csv')

# Export summary
exporter.export_summary(portfolio_data, 'output/summary.csv')

# Export all in one go
files = exporter.export_all(portfolio_data, 'output/', prefix='my_portfolio')
print(files)

# Or use convenience function
export_to_csv(portfolio_data, 'output/holdings.csv', export_type='holdings')
""")
