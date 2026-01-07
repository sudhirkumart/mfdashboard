"""
Interactive Portfolio Calculator CLI Application

Run this to manage your mutual fund portfolio and calculate capital gains.
"""

from mfapi_fetcher import MFAPIFetcher
from portfolio_manager import PortfolioManager
from datetime import datetime
from typing import Optional


class PortfolioApp:
    """Interactive CLI application for portfolio management"""

    def __init__(self):
        self.fetcher = MFAPIFetcher()
        self.portfolio = PortfolioManager()

    def clear_screen(self):
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")

    def print_menu(self, title: str, options: list):
        """Print a menu"""
        print(f"\n{title}")
        print("-" * 70)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print(f"  0. Back/Exit")
        print("-" * 70)

    def get_input(self, prompt: str, input_type=str, allow_empty=False):
        """Get user input with validation"""
        while True:
            value = input(f"{prompt}: ").strip()

            if allow_empty and not value:
                return None

            if not value:
                print("Input cannot be empty!")
                continue

            try:
                return input_type(value)
            except ValueError:
                print(f"Invalid input! Please enter a valid {input_type.__name__}")

    def search_and_select_scheme(self):
        """Search for a scheme and let user select one"""
        query = self.get_input("\nEnter scheme name to search")

        print("\nSearching...")
        schemes = self.fetcher.search_schemes(query)

        if not schemes:
            print("No schemes found!")
            return None

        print(f"\nFound {len(schemes)} schemes:")
        print("-" * 70)

        # Show first 10 results
        display_count = min(10, len(schemes))
        for i, scheme in enumerate(schemes[:display_count], 1):
            print(f"{i}. {scheme['schemeName'][:60]}")
            print(f"   Code: {scheme['schemeCode']}")

        if len(schemes) > 10:
            print(f"\n... and {len(schemes) - 10} more. Refine your search for better results.")

        choice = self.get_input("\nSelect scheme number (0 to cancel)", int)

        if choice == 0 or choice > display_count:
            return None

        return schemes[choice - 1]

    def add_transaction_menu(self):
        """Add a new buy/sell transaction"""
        self.print_header("Add Transaction")

        # Select scheme
        scheme = self.search_and_select_scheme()
        if not scheme:
            return

        scheme_code = scheme['schemeCode']
        scheme_name = scheme['schemeName']

        print(f"\nSelected: {scheme_name}")

        # Transaction type
        print("\nTransaction Type:")
        print("1. BUY")
        print("2. SELL")
        txn_type_choice = self.get_input("Select", int)

        if txn_type_choice not in [1, 2]:
            print("Invalid choice!")
            return

        txn_type = 'BUY' if txn_type_choice == 1 else 'SELL'

        # Get transaction details
        date_str = self.get_input("Date (YYYY-MM-DD) or leave empty for today", str, allow_empty=True)
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        units = self.get_input("Number of units", float)
        nav = self.get_input("NAV at transaction", float)

        # Confirm
        amount = units * nav
        print(f"\nConfirm Transaction:")
        print(f"  Scheme: {scheme_name}")
        print(f"  Type: {txn_type}")
        print(f"  Date: {date_str}")
        print(f"  Units: {units}")
        print(f"  NAV: Rs.{nav}")
        print(f"  Amount: Rs.{amount:.2f}")

        confirm = self.get_input("\nConfirm? (y/n)", str)

        if confirm.lower() == 'y':
            self.portfolio.add_transaction(
                date=date_str,
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                transaction_type=txn_type,
                units=units,
                nav=nav
            )
            print("\nTransaction added successfully!")
        else:
            print("\nTransaction cancelled.")

        input("\nPress Enter to continue...")

    def view_portfolio_menu(self):
        """View current portfolio"""
        self.print_header("Current Portfolio")

        print("Fetching latest NAV data...")

        # Get unique scheme codes
        scheme_codes = set(t.scheme_code for t in self.portfolio.transactions)

        if not scheme_codes:
            print("No transactions found! Add some transactions first.")
            input("\nPress Enter to continue...")
            return

        # Fetch current NAVs
        current_navs = {}
        for code in scheme_codes:
            try:
                nav_data = self.fetcher.get_latest_nav(code)
                if nav_data:
                    current_navs[code] = float(nav_data['nav'])
            except Exception as e:
                print(f"Error fetching NAV for {code}: {e}")

        # Get holdings
        holdings = self.portfolio.get_holdings(current_navs)

        if not holdings:
            print("No current holdings.")
            input("\nPress Enter to continue...")
            return

        # Display holdings
        print("\n" + "=" * 70)
        for i, holding in enumerate(holdings, 1):
            print(f"\n{i}. {holding.scheme_name[:60]}")
            print(f"   Code: {holding.scheme_code}")
            print(f"   Units: {holding.total_units}")
            print(f"   Avg NAV: Rs.{holding.average_nav} | Current NAV: Rs.{holding.current_nav}")
            print(f"   Invested: Rs.{holding.invested_amount:,.2f}")
            print(f"   Current: Rs.{holding.current_value:,.2f}")

            gain_symbol = "+" if holding.gain_loss >= 0 else ""
            color = "↑" if holding.gain_loss >= 0 else "↓"
            print(f"   Gain/Loss: {gain_symbol}Rs.{holding.gain_loss:,.2f} ({gain_symbol}{holding.gain_loss_percentage}%) {color}")

        # Summary
        summary = self.portfolio.get_summary(current_navs)
        print("\n" + "=" * 70)
        print("PORTFOLIO SUMMARY")
        print("-" * 70)
        print(f"Total Schemes: {summary['total_schemes']}")
        print(f"Total Invested: Rs.{summary['total_invested']:,.2f}")
        print(f"Current Value: Rs.{summary['current_value']:,.2f}")

        gain_symbol = "+" if summary['total_gain_loss'] >= 0 else ""
        print(f"Total Gain/Loss: {gain_symbol}Rs.{summary['total_gain_loss']:,.2f} ({gain_symbol}{summary['total_gain_loss_percentage']}%)")
        print("=" * 70)

        input("\nPress Enter to continue...")

    def calculate_capital_gains_menu(self):
        """Calculate and display capital gains"""
        self.print_header("Capital Gains Calculator")

        print("Fund Type:")
        print("1. Equity (Long term: >1 year)")
        print("2. Debt (Long term: >3 years)")
        fund_type = self.get_input("Select", int)

        if fund_type not in [1, 2]:
            print("Invalid choice!")
            return

        is_equity = (fund_type == 1)

        print("\nCalculating capital gains...")
        gains = self.portfolio.calculate_capital_gains(is_equity=is_equity)

        if not gains:
            print("\nNo capital gains found. You need to have SELL transactions.")
            input("\nPress Enter to continue...")
            return

        # Display gains
        print("\n" + "=" * 70)
        print("CAPITAL GAINS REPORT")
        print("=" * 70)

        total_stcg = 0
        total_ltcg = 0

        for i, gain in enumerate(gains, 1):
            print(f"\n{i}. {gain.scheme_name[:60]}")
            print(f"   Sale Date: {gain.sale_date}")
            print(f"   Units Sold: {gain.units_sold}")
            print(f"   Purchase NAV: Rs.{gain.purchase_nav} | Sale NAV: Rs.{gain.sale_nav}")
            print(f"   Purchase Amount: Rs.{gain.purchase_amount:,.2f}")
            print(f"   Sale Amount: Rs.{gain.sale_amount:,.2f}")

            gain_symbol = "+" if gain.gain_loss >= 0 else ""
            print(f"   Gain/Loss: {gain_symbol}Rs.{gain.gain_loss:,.2f} ({gain_symbol}{gain.gain_loss_percentage}%)")
            print(f"   Holding Period: {gain.holding_period_days} days")
            print(f"   Type: {gain.gain_type}")

            if gain.gain_type == 'STCG':
                total_stcg += gain.gain_loss
            else:
                total_ltcg += gain.gain_loss

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(f"Total Short Term Capital Gains (STCG): Rs.{total_stcg:,.2f}")
        print(f"Total Long Term Capital Gains (LTCG): Rs.{total_ltcg:,.2f}")
        print(f"Total Capital Gains: Rs.{total_stcg + total_ltcg:,.2f}")
        print("=" * 70)

        input("\nPress Enter to continue...")

    def view_transactions_menu(self):
        """View all transactions"""
        self.print_header("All Transactions")

        if not self.portfolio.transactions:
            print("No transactions found!")
            input("\nPress Enter to continue...")
            return

        print(f"Total Transactions: {len(self.portfolio.transactions)}\n")
        print("-" * 70)

        for i, txn in enumerate(self.portfolio.transactions, 1):
            print(f"{i}. {txn.date} | {txn.transaction_type} | {txn.scheme_name[:40]}")
            print(f"   Units: {txn.units} | NAV: Rs.{txn.nav} | Amount: Rs.{txn.amount:,.2f}")

        print("-" * 70)

        # Option to delete
        delete_choice = self.get_input("\nEnter transaction number to delete (0 to cancel)", int)

        if delete_choice > 0 and delete_choice <= len(self.portfolio.transactions):
            confirm = self.get_input("Confirm deletion? (y/n)", str)
            if confirm.lower() == 'y':
                self.portfolio.delete_transaction(delete_choice - 1)
                print("Transaction deleted!")
            else:
                print("Deletion cancelled.")

        input("\nPress Enter to continue...")

    def main_menu(self):
        """Main application menu"""
        while True:
            self.clear_screen()
            self.print_header("Mutual Fund Portfolio Calculator")

            options = [
                "Add Transaction (Buy/Sell)",
                "View Portfolio",
                "Calculate Capital Gains",
                "View All Transactions",
                "Exit"
            ]

            self.print_menu("Main Menu", options[:-1])

            choice = self.get_input("\nSelect option", int)

            if choice == 1:
                self.add_transaction_menu()
            elif choice == 2:
                self.view_portfolio_menu()
            elif choice == 3:
                self.calculate_capital_gains_menu()
            elif choice == 4:
                self.view_transactions_menu()
            elif choice == 0:
                print("\nThank you for using Portfolio Calculator!")
                break
            else:
                print("Invalid choice!")
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    app = PortfolioApp()
    app.main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
