"""
Financial Calculations Module
Provides XIRR, returns, and capital gains calculations for mutual fund portfolios
"""

from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def xirr(transactions: List[Dict[str, any]], guess: float = 0.1) -> Optional[float]:
    """
    Calculate XIRR (Extended Internal Rate of Return) using Newton-Raphson method

    Args:
        transactions: List of dicts with 'date' (datetime) and 'amount' (float)
                     Investments are negative, redemptions/current value are positive
        guess: Initial guess for IRR (default 0.1 = 10%)

    Returns:
        XIRR as decimal (e.g., 0.12 for 12%) or None if calculation fails
    """
    if not transactions or len(transactions) < 2:
        logger.warning("XIRR requires at least 2 transactions")
        return None

    # Sort transactions by date
    sorted_txns = sorted(transactions, key=lambda x: x['date'])

    # Base date (first transaction date)
    base_date = sorted_txns[0]['date']

    # Convert dates to days from base date
    days_amounts = []
    for txn in sorted_txns:
        days = (txn['date'] - base_date).days
        days_amounts.append((days, txn['amount']))

    # Newton-Raphson method
    max_iterations = 100
    tolerance = 1e-6

    rate = guess

    for iteration in range(max_iterations):
        # Calculate NPV and its derivative
        npv = 0
        dnpv = 0

        for days, amount in days_amounts:
            factor = (1 + rate) ** (days / 365.0)
            npv += amount / factor
            dnpv -= (days / 365.0) * amount / (factor * (1 + rate))

        # Check convergence
        if abs(npv) < tolerance:
            return rate

        # Newton-Raphson update
        if abs(dnpv) < 1e-10:
            logger.warning("XIRR derivative too small, calculation may be inaccurate")
            break

        rate = rate - npv / dnpv

        # Prevent extreme values
        if rate < -0.99:
            rate = -0.99
        elif rate > 10:
            rate = 10

    logger.warning(f"XIRR did not converge after {max_iterations} iterations")
    return rate if abs(npv) < 0.01 else None


def calculate_absolute_return(invested: float, current_value: float) -> float:
    """
    Calculate absolute return percentage

    Args:
        invested: Total amount invested
        current_value: Current portfolio value

    Returns:
        Absolute return as percentage
    """
    if invested == 0:
        return 0.0
    return ((current_value - invested) / invested) * 100


def calculate_cagr(invested: float, current_value: float, days: int) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate

    Args:
        invested: Total amount invested
        current_value: Current portfolio value
        days: Number of days invested

    Returns:
        CAGR as percentage or None if invalid inputs
    """
    if invested <= 0 or current_value <= 0 or days <= 0:
        return None

    years = days / 365.0
    if years < 0.01:  # Less than 3-4 days
        return None

    cagr = (((current_value / invested) ** (1 / years)) - 1) * 100
    return cagr


def calculate_capital_gains(transactions: List[Dict], current_nav: float,
                           redemption_units: float = 0) -> Dict:
    """
    Calculate capital gains with FIFO method

    Args:
        transactions: List of purchase transactions with 'date', 'units', 'nav'
        current_nav: Current NAV for unrealized gains
        redemption_units: Units being redeemed (0 for current holdings)

    Returns:
        Dictionary with LTCG, STCG breakdown
    """
    # Sort transactions by date (FIFO)
    sorted_txns = sorted(transactions, key=lambda x: x['date'])

    ltcg = 0.0  # Long-term capital gains (>3 years for debt, >1 year for equity)
    stcg = 0.0  # Short-term capital gains

    current_date = datetime.now()
    units_to_process = redemption_units if redemption_units > 0 else sum(t['units'] for t in sorted_txns)

    for txn in sorted_txns:
        if units_to_process <= 0:
            break

        units = min(txn['units'], units_to_process)
        purchase_nav = txn['nav']
        holding_days = (current_date - txn['date']).days

        # Calculate gain/loss
        gain = units * (current_nav - purchase_nav)

        # Classify as LTCG or STCG (using equity: >1 year = LTCG)
        if holding_days > 365:
            ltcg += gain
        else:
            stcg += gain

        units_to_process -= units

    return {
        'ltcg': ltcg,
        'stcg': stcg,
        'total_gain': ltcg + stcg,
        'ltcg_taxable': max(0, ltcg - 100000),  # LTCG exemption up to 1 lakh
        'stcg_taxable': stcg
    }


def calculate_sip_returns(monthly_investment: float, months: int,
                         final_value: float) -> Dict:
    """
    Calculate returns for SIP investments

    Args:
        monthly_investment: Monthly SIP amount
        months: Number of months
        final_value: Current value of SIP

    Returns:
        Dictionary with total invested, returns, and XIRR
    """
    total_invested = monthly_investment * months

    # Create transaction list for XIRR
    transactions = []
    start_date = datetime.now()

    # Monthly investments (negative cash flow)
    for i in range(months):
        txn_date = datetime(start_date.year, start_date.month, 1) - \
                   timedelta(days=i * 30)
        transactions.append({
            'date': txn_date,
            'amount': -monthly_investment
        })

    # Final value (positive cash flow)
    transactions.append({
        'date': datetime.now(),
        'amount': final_value
    })

    sip_xirr = xirr(transactions)
    sip_xirr_pct = sip_xirr * 100 if sip_xirr else None

    return {
        'total_invested': total_invested,
        'current_value': final_value,
        'absolute_return': final_value - total_invested,
        'absolute_return_pct': calculate_absolute_return(total_invested, final_value),
        'xirr': sip_xirr_pct
    }


def calculate_portfolio_metrics(holdings: List[Dict]) -> Dict:
    """
    Calculate comprehensive portfolio metrics

    Args:
        holdings: List of holdings with 'invested', 'current_value', 'transactions'

    Returns:
        Dictionary with aggregated portfolio metrics
    """
    total_invested = sum(h['invested'] for h in holdings)
    total_current = sum(h['current_value'] for h in holdings)

    # Collect all transactions for XIRR
    all_transactions = []
    for holding in holdings:
        if 'transactions' in holding:
            all_transactions.extend(holding['transactions'])

    # Add current value as final transaction
    all_transactions.append({
        'date': datetime.now(),
        'amount': total_current
    })

    portfolio_xirr = xirr(all_transactions)
    portfolio_xirr_pct = portfolio_xirr * 100 if portfolio_xirr else None

    # Calculate weighted average holding period
    total_days = 0
    total_weight = 0
    for holding in holdings:
        if 'transactions' in holding and holding['transactions']:
            avg_date = min(t['date'] for t in holding['transactions'])
            days = (datetime.now() - avg_date).days
            weight = holding['current_value']
            total_days += days * weight
            total_weight += weight

    avg_holding_days = total_days / total_weight if total_weight > 0 else 0

    return {
        'total_invested': total_invested,
        'current_value': total_current,
        'total_gain': total_current - total_invested,
        'absolute_return_pct': calculate_absolute_return(total_invested, total_current),
        'xirr': portfolio_xirr_pct,
        'avg_holding_days': int(avg_holding_days),
        'avg_holding_years': round(avg_holding_days / 365, 2)
    }


from datetime import timedelta


if __name__ == "__main__":
    # Test XIRR calculation
    print("Testing Financial Calculations...\n")

    # Example: Invested ₹10,000 on Jan 1, 2023, current value ₹12,500
    test_transactions = [
        {'date': datetime(2023, 1, 1), 'amount': -10000},
        {'date': datetime(2023, 6, 1), 'amount': -5000},
        {'date': datetime(2024, 1, 5), 'amount': 18000}
    ]

    xirr_result = xirr(test_transactions)
    print(f"XIRR: {xirr_result * 100:.2f}%" if xirr_result else "XIRR: Could not calculate")

    # Test absolute return
    abs_return = calculate_absolute_return(15000, 18000)
    print(f"Absolute Return: {abs_return:.2f}%")

    # Test CAGR
    cagr_result = calculate_cagr(10000, 12500, 365)
    print(f"CAGR: {cagr_result:.2f}%" if cagr_result else "CAGR: N/A")

    # Test capital gains
    print("\nCapital Gains Calculation:")
    purchase_txns = [
        {'date': datetime(2021, 1, 1), 'units': 100, 'nav': 50},
        {'date': datetime(2023, 6, 1), 'units': 50, 'nav': 60}
    ]
    gains = calculate_capital_gains(purchase_txns, current_nav=75)
    print(f"LTCG: ₹{gains['ltcg']:.2f}")
    print(f"STCG: ₹{gains['stcg']:.2f}")
    print(f"Total Gain: ₹{gains['total_gain']:.2f}")

    # Test SIP returns
    print("\nSIP Returns:")
    sip_metrics = calculate_sip_returns(5000, 24, 135000)
    print(f"Invested: ₹{sip_metrics['total_invested']:,.0f}")
    print(f"Current: ₹{sip_metrics['current_value']:,.0f}")
    print(f"Returns: {sip_metrics['absolute_return_pct']:.2f}%")
    print(f"XIRR: {sip_metrics['xirr']:.2f}%" if sip_metrics['xirr'] else "XIRR: N/A")
