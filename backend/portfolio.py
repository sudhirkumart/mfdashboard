"""
Portfolio Management Module
Manages multiple PAN accounts and mutual fund holdings
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from backend.api import MFAPIClient
from backend.calculations import (
    calculate_portfolio_metrics,
    calculate_capital_gains,
    xirr
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Portfolio:
    """Manages a mutual fund portfolio with multiple holdings"""

    def __init__(self, portfolio_data: Dict, api_client: Optional[MFAPIClient] = None):
        """
        Initialize portfolio

        Args:
            portfolio_data: Portfolio configuration dict
            api_client: MFAPIClient instance (creates new if None)
        """
        self.data = portfolio_data
        self.api_client = api_client or MFAPIClient()

    @classmethod
    def from_file(cls, file_path: str, api_client: Optional[MFAPIClient] = None):
        """Load portfolio from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data, api_client)

    def save(self, file_path: str) -> None:
        """Save portfolio to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        logger.info(f"Portfolio saved to {file_path}")

    def get_pan_accounts(self) -> List[str]:
        """Get list of all PAN accounts"""
        return list(self.data.get('accounts', {}).keys())

    def get_holdings_by_pan(self, pan: str) -> List[Dict]:
        """Get all holdings for a specific PAN"""
        accounts = self.data.get('accounts', {})
        if pan not in accounts:
            logger.warning(f"PAN {pan} not found")
            return []
        return accounts[pan].get('holdings', [])

    def get_all_holdings(self) -> List[Dict]:
        """Get all holdings across all PANs"""
        all_holdings = []
        for pan in self.get_pan_accounts():
            holdings = self.get_holdings_by_pan(pan)
            for holding in holdings:
                holding['pan'] = pan
                all_holdings.append(holding)
        return all_holdings

    def update_nav_data(self) -> None:
        """Fetch latest NAV for all holdings"""
        logger.info("Updating NAV data for all holdings...")

        for pan in self.get_pan_accounts():
            holdings = self.get_holdings_by_pan(pan)

            for holding in holdings:
                scheme_code = holding.get('scheme_code')
                if not scheme_code:
                    continue

                # Fetch latest NAV
                nav_data = self.api_client.get_latest_nav(scheme_code)

                if nav_data:
                    holding['current_nav'] = nav_data['nav']
                    holding['nav_date'] = nav_data['date']
                    holding['scheme_name'] = nav_data.get('scheme_name', holding.get('scheme_name'))

                    # Calculate current value
                    total_units = sum(txn.get('units', 0) for txn in holding.get('transactions', []))
                    holding['units'] = total_units
                    holding['current_value'] = total_units * nav_data['nav']

                    # Calculate invested amount
                    invested = sum(
                        txn.get('units', 0) * txn.get('nav', 0)
                        for txn in holding.get('transactions', [])
                    )
                    holding['invested'] = invested
                    holding['gain_loss'] = holding['current_value'] - invested

                    logger.info(f"Updated {holding.get('scheme_name', scheme_code)}")

    def calculate_pan_summary(self, pan: str) -> Dict:
        """Calculate summary metrics for a PAN account"""
        holdings = self.get_holdings_by_pan(pan)

        if not holdings:
            return {
                'pan': pan,
                'total_invested': 0,
                'current_value': 0,
                'total_gain': 0,
                'holdings_count': 0
            }

        # Prepare holdings for metrics calculation
        prepared_holdings = []
        for holding in holdings:
            # Convert transaction dates from strings to datetime
            transactions = []
            for txn in holding.get('transactions', []):
                txn_copy = txn.copy()
                if isinstance(txn_copy['date'], str):
                    txn_copy['date'] = datetime.strptime(txn_copy['date'], '%Y-%m-%d')
                txn_copy['amount'] = -txn_copy['units'] * txn_copy['nav']  # Negative for investment
                transactions.append(txn_copy)

            prepared_holdings.append({
                'invested': holding.get('invested', 0),
                'current_value': holding.get('current_value', 0),
                'transactions': transactions
            })

        metrics = calculate_portfolio_metrics(prepared_holdings)
        metrics['pan'] = pan
        metrics['holdings_count'] = len(holdings)

        return metrics

    def calculate_total_summary(self) -> Dict:
        """Calculate summary for entire portfolio across all PANs"""
        all_summaries = []

        for pan in self.get_pan_accounts():
            summary = self.calculate_pan_summary(pan)
            all_summaries.append(summary)

        # Aggregate totals
        total_invested = sum(s['total_invested'] for s in all_summaries)
        total_current = sum(s['current_value'] for s in all_summaries)
        total_gain = total_current - total_invested

        # Calculate overall XIRR
        all_transactions = []
        for holding in self.get_all_holdings():
            for txn in holding.get('transactions', []):
                txn_copy = txn.copy()
                if isinstance(txn_copy['date'], str):
                    txn_copy['date'] = datetime.strptime(txn_copy['date'], '%Y-%m-%d')
                txn_copy['amount'] = -txn_copy['units'] * txn_copy['nav']
                all_transactions.append(txn_copy)

        # Add current value
        all_transactions.append({
            'date': datetime.now(),
            'amount': total_current
        })

        overall_xirr = xirr(all_transactions)
        overall_xirr_pct = overall_xirr * 100 if overall_xirr else None

        return {
            'total_invested': total_invested,
            'current_value': total_current,
            'total_gain': total_gain,
            'absolute_return_pct': (total_gain / total_invested * 100) if total_invested > 0 else 0,
            'xirr': overall_xirr_pct,
            'accounts_count': len(all_summaries),
            'total_holdings': sum(s['holdings_count'] for s in all_summaries),
            'pan_summaries': all_summaries
        }

    def get_top_performers(self, limit: int = 5) -> List[Dict]:
        """Get top performing holdings by absolute return percentage"""
        all_holdings = self.get_all_holdings()

        # Filter holdings with valid data
        valid_holdings = [
            h for h in all_holdings
            if h.get('invested', 0) > 0 and h.get('current_value', 0) > 0
        ]

        # Calculate return percentage
        for holding in valid_holdings:
            gain = holding['current_value'] - holding['invested']
            holding['return_pct'] = (gain / holding['invested']) * 100

        # Sort by return percentage
        sorted_holdings = sorted(valid_holdings, key=lambda x: x['return_pct'], reverse=True)

        return sorted_holdings[:limit]

    def get_holdings_by_category(self) -> Dict[str, List[Dict]]:
        """Group holdings by asset category"""
        categories = {}

        for holding in self.get_all_holdings():
            category = holding.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(holding)

        return categories

    def add_transaction(self, pan: str, scheme_code: str, transaction: Dict) -> bool:
        """
        Add a transaction to a holding

        Args:
            pan: PAN account number
            scheme_code: Scheme code
            transaction: Transaction dict with date, units, nav, type

        Returns:
            True if successful, False otherwise
        """
        if pan not in self.data.get('accounts', {}):
            logger.error(f"PAN {pan} not found")
            return False

        holdings = self.get_holdings_by_pan(pan)

        # Find existing holding or create new
        holding = None
        for h in holdings:
            if h.get('scheme_code') == scheme_code:
                holding = h
                break

        if not holding:
            # Create new holding
            holding = {
                'scheme_code': scheme_code,
                'transactions': []
            }
            self.data['accounts'][pan]['holdings'].append(holding)

        # Add transaction
        if 'transactions' not in holding:
            holding['transactions'] = []

        holding['transactions'].append(transaction)
        logger.info(f"Added transaction for scheme {scheme_code} in PAN {pan}")

        return True


class PortfolioManager:
    """Manages multiple portfolios"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize portfolio manager

        Args:
            data_dir: Directory to store portfolio files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.api_client = MFAPIClient()

    def list_portfolios(self) -> List[str]:
        """List all available portfolios"""
        portfolio_files = self.data_dir.glob("portfolio_*.json")
        return [f.stem for f in portfolio_files]

    def load_portfolio(self, name: str) -> Optional[Portfolio]:
        """Load a portfolio by name"""
        file_path = self.data_dir / f"{name}.json"
        if not file_path.exists():
            logger.error(f"Portfolio {name} not found")
            return None

        return Portfolio.from_file(str(file_path), self.api_client)

    def create_portfolio(self, name: str, initial_data: Optional[Dict] = None) -> Portfolio:
        """Create a new portfolio"""
        if initial_data is None:
            initial_data = {
                'portfolio_name': name,
                'created_date': datetime.now().isoformat(),
                'accounts': {}
            }

        portfolio = Portfolio(initial_data, self.api_client)
        file_path = self.data_dir / f"{name}.json"
        portfolio.save(str(file_path))

        logger.info(f"Created portfolio: {name}")
        return portfolio


if __name__ == "__main__":
    # Quick test
    print("Testing Portfolio Management...\n")

    # Create sample portfolio
    sample_data = {
        'portfolio_name': 'Test Portfolio',
        'accounts': {
            'ABCDE1234F': {
                'name': 'John Doe',
                'holdings': [
                    {
                        'scheme_code': '119551',
                        'scheme_name': 'HDFC Top 100 Fund',
                        'category': 'Equity',
                        'transactions': [
                            {
                                'date': '2023-01-15',
                                'units': 100,
                                'nav': 650,
                                'type': 'purchase'
                            }
                        ]
                    }
                ]
            }
        }
    }

    portfolio = Portfolio(sample_data)
    print(f"Portfolio: {portfolio.data['portfolio_name']}")
    print(f"PAN Accounts: {portfolio.get_pan_accounts()}")
    print(f"Total Holdings: {len(portfolio.get_all_holdings())}")

    # Update NAV
    print("\nUpdating NAV data...")
    portfolio.update_nav_data()

    # Calculate summary
    print("\nCalculating summary...")
    summary = portfolio.calculate_total_summary()
    print(f"Total Invested: ₹{summary['total_invested']:,.2f}")
    print(f"Current Value: ₹{summary['current_value']:,.2f}")
    print(f"Total Gain: ₹{summary['total_gain']:,.2f}")
    print(f"Return: {summary['absolute_return_pct']:.2f}%")
    if summary['xirr']:
        print(f"XIRR: {summary['xirr']:.2f}%")
