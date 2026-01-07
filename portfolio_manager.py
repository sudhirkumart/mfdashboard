"""
Mutual Fund Portfolio Manager with Capital Gains Calculator

Manages your mutual fund investments and calculates capital gains
using FIFO (First In First Out) method.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Transaction:
    """Represents a single mutual fund transaction"""
    date: str  # Format: YYYY-MM-DD
    scheme_code: str
    scheme_name: str
    transaction_type: str  # 'BUY' or 'SELL'
    units: float
    nav: float
    amount: float  # Total amount (units * nav)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        return cls(**data)


@dataclass
class Holding:
    """Represents current holdings for a scheme"""
    scheme_code: str
    scheme_name: str
    total_units: float
    average_nav: float
    invested_amount: float
    current_nav: float
    current_value: float
    gain_loss: float
    gain_loss_percentage: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CapitalGain:
    """Represents capital gain from a sale"""
    sale_date: str
    scheme_code: str
    scheme_name: str
    units_sold: float
    sale_nav: float
    sale_amount: float
    purchase_nav: float
    purchase_amount: float
    gain_loss: float
    gain_loss_percentage: float
    holding_period_days: int
    gain_type: str  # 'STCG' (Short Term) or 'LTCG' (Long Term)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PortfolioManager:
    """
    Manages mutual fund portfolio with transaction tracking and capital gains calculation.
    """

    # For equity funds: >1 year is long term, for debt funds: >3 years is long term
    EQUITY_LTCG_DAYS = 365
    DEBT_LTCG_DAYS = 1095

    def __init__(self, portfolio_file: str = "portfolio.json"):
        """
        Initialize portfolio manager.

        Args:
            portfolio_file: Path to JSON file for storing portfolio data
        """
        self.portfolio_file = Path(portfolio_file)
        self.transactions: List[Transaction] = []
        self.load_portfolio()

    def load_portfolio(self) -> None:
        """Load portfolio from file"""
        if self.portfolio_file.exists():
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.transactions = [
                        Transaction.from_dict(t) for t in data.get('transactions', [])
                    ]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading portfolio: {e}")
                self.transactions = []

    def save_portfolio(self) -> None:
        """Save portfolio to file"""
        try:
            data = {
                'transactions': [t.to_dict() for t in self.transactions],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving portfolio: {e}")

    def add_transaction(
        self,
        date: str,
        scheme_code: str,
        scheme_name: str,
        transaction_type: str,
        units: float,
        nav: float
    ) -> Transaction:
        """
        Add a new transaction (buy or sell).

        Args:
            date: Transaction date (YYYY-MM-DD)
            scheme_code: Mutual fund scheme code
            scheme_name: Mutual fund scheme name
            transaction_type: 'BUY' or 'SELL'
            units: Number of units
            nav: NAV at transaction time

        Returns:
            Created transaction object
        """
        amount = units * nav
        transaction = Transaction(
            date=date,
            scheme_code=scheme_code,
            scheme_name=scheme_name,
            transaction_type=transaction_type.upper(),
            units=units,
            nav=nav,
            amount=amount
        )

        self.transactions.append(transaction)
        self.transactions.sort(key=lambda t: t.date)  # Keep sorted by date
        self.save_portfolio()

        return transaction

    def get_holdings(self, current_navs: Dict[str, float]) -> List[Holding]:
        """
        Calculate current holdings with gain/loss.

        Args:
            current_navs: Dictionary mapping scheme_code to current NAV

        Returns:
            List of current holdings
        """
        holdings_dict: Dict[str, Dict[str, Any]] = {}

        for txn in self.transactions:
            scheme_code = txn.scheme_code

            if scheme_code not in holdings_dict:
                holdings_dict[scheme_code] = {
                    'scheme_name': txn.scheme_name,
                    'total_units': 0.0,
                    'invested_amount': 0.0
                }

            holding = holdings_dict[scheme_code]

            if txn.transaction_type == 'BUY':
                holding['total_units'] += txn.units
                holding['invested_amount'] += txn.amount
            elif txn.transaction_type == 'SELL':
                holding['total_units'] -= txn.units
                # Reduce invested amount proportionally
                if holding['total_units'] > 0:
                    avg_nav = holding['invested_amount'] / (holding['total_units'] + txn.units)
                    holding['invested_amount'] -= txn.units * avg_nav
                else:
                    holding['invested_amount'] = 0

        # Create holding objects
        holdings = []
        for scheme_code, data in holdings_dict.items():
            if data['total_units'] <= 0:
                continue  # Skip sold out holdings

            current_nav = current_navs.get(scheme_code, 0)
            average_nav = data['invested_amount'] / data['total_units'] if data['total_units'] > 0 else 0
            current_value = data['total_units'] * current_nav
            gain_loss = current_value - data['invested_amount']
            gain_loss_pct = (gain_loss / data['invested_amount'] * 100) if data['invested_amount'] > 0 else 0

            holding = Holding(
                scheme_code=scheme_code,
                scheme_name=data['scheme_name'],
                total_units=round(data['total_units'], 3),
                average_nav=round(average_nav, 4),
                invested_amount=round(data['invested_amount'], 2),
                current_nav=round(current_nav, 4),
                current_value=round(current_value, 2),
                gain_loss=round(gain_loss, 2),
                gain_loss_percentage=round(gain_loss_pct, 2)
            )
            holdings.append(holding)

        return sorted(holdings, key=lambda h: h.current_value, reverse=True)

    def calculate_capital_gains(
        self,
        scheme_code: Optional[str] = None,
        is_equity: bool = True
    ) -> List[CapitalGain]:
        """
        Calculate capital gains using FIFO method.

        Args:
            scheme_code: Calculate for specific scheme, or None for all
            is_equity: True for equity funds (1 year LTCG), False for debt (3 years)

        Returns:
            List of capital gain records
        """
        ltcg_days = self.EQUITY_LTCG_DAYS if is_equity else self.DEBT_LTCG_DAYS

        # Filter transactions
        transactions = self.transactions
        if scheme_code:
            transactions = [t for t in transactions if t.scheme_code == scheme_code]

        # Group by scheme
        schemes = {}
        for txn in transactions:
            if txn.scheme_code not in schemes:
                schemes[txn.scheme_code] = {
                    'name': txn.scheme_name,
                    'buys': [],
                    'sells': []
                }

            if txn.transaction_type == 'BUY':
                schemes[txn.scheme_code]['buys'].append(txn)
            elif txn.transaction_type == 'SELL':
                schemes[txn.scheme_code]['sells'].append(txn)

        # Calculate gains using FIFO
        capital_gains = []

        for scode, data in schemes.items():
            buy_queue = data['buys'].copy()

            for sell_txn in data['sells']:
                units_to_sell = sell_txn.units

                while units_to_sell > 0 and buy_queue:
                    buy_txn = buy_queue[0]

                    # Calculate units from this buy transaction
                    units_from_buy = min(units_to_sell, buy_txn.units)

                    # Calculate holding period
                    buy_date = datetime.strptime(buy_txn.date, '%Y-%m-%d')
                    sell_date = datetime.strptime(sell_txn.date, '%Y-%m-%d')
                    holding_days = (sell_date - buy_date).days

                    # Calculate gain
                    purchase_amount = units_from_buy * buy_txn.nav
                    sale_amount = units_from_buy * sell_txn.nav
                    gain = sale_amount - purchase_amount
                    gain_pct = (gain / purchase_amount * 100) if purchase_amount > 0 else 0

                    # Determine gain type
                    gain_type = 'LTCG' if holding_days >= ltcg_days else 'STCG'

                    capital_gain = CapitalGain(
                        sale_date=sell_txn.date,
                        scheme_code=scode,
                        scheme_name=data['name'],
                        units_sold=round(units_from_buy, 3),
                        sale_nav=round(sell_txn.nav, 4),
                        sale_amount=round(sale_amount, 2),
                        purchase_nav=round(buy_txn.nav, 4),
                        purchase_amount=round(purchase_amount, 2),
                        gain_loss=round(gain, 2),
                        gain_loss_percentage=round(gain_pct, 2),
                        holding_period_days=holding_days,
                        gain_type=gain_type
                    )
                    capital_gains.append(capital_gain)

                    # Update remaining units
                    units_to_sell -= units_from_buy
                    buy_txn.units -= units_from_buy

                    if buy_txn.units <= 0:
                        buy_queue.pop(0)

        return capital_gains

    def get_summary(self, current_navs: Dict[str, float]) -> Dict[str, Any]:
        """
        Get portfolio summary.

        Args:
            current_navs: Dictionary mapping scheme_code to current NAV

        Returns:
            Summary dictionary with key metrics
        """
        holdings = self.get_holdings(current_navs)

        total_invested = sum(h.invested_amount for h in holdings)
        total_current = sum(h.current_value for h in holdings)
        total_gain = total_current - total_invested
        total_gain_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0

        return {
            'total_schemes': len(holdings),
            'total_invested': round(total_invested, 2),
            'current_value': round(total_current, 2),
            'total_gain_loss': round(total_gain, 2),
            'total_gain_loss_percentage': round(total_gain_pct, 2),
            'holdings': holdings
        }

    def get_transactions_by_scheme(self, scheme_code: str) -> List[Transaction]:
        """Get all transactions for a specific scheme"""
        return [t for t in self.transactions if t.scheme_code == scheme_code]

    def delete_transaction(self, index: int) -> bool:
        """
        Delete a transaction by index.

        Args:
            index: Index in transactions list

        Returns:
            True if deleted, False if index invalid
        """
        if 0 <= index < len(self.transactions):
            self.transactions.pop(index)
            self.save_portfolio()
            return True
        return False
