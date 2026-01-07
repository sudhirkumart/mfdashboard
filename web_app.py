"""
Flask Web Dashboard for Mutual Fund Portfolio

Run: python web_app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
from mfapi_fetcher import MFAPIFetcher
from portfolio_manager import PortfolioManager
from datetime import datetime
import json

app = Flask(__name__)
fetcher = MFAPIFetcher()
portfolio = PortfolioManager()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/search/<query>')
def search_schemes(query):
    """Search for mutual fund schemes"""
    try:
        schemes = fetcher.search_schemes(query)
        return jsonify({'success': True, 'schemes': schemes[:20]})  # Limit to 20 results
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scheme/<scheme_code>')
def get_scheme(scheme_code):
    """Get scheme details"""
    try:
        details = fetcher.get_scheme(scheme_code)
        return jsonify({'success': True, 'data': details})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions', methods=['GET', 'POST', 'DELETE'])
def transactions():
    """Manage transactions"""
    if request.method == 'GET':
        # Get all transactions
        txns = [t.to_dict() for t in portfolio.transactions]
        return jsonify({'success': True, 'transactions': txns})

    elif request.method == 'POST':
        # Add new transaction
        try:
            data = request.json
            portfolio.add_transaction(
                date=data['date'],
                scheme_code=data['scheme_code'],
                scheme_name=data['scheme_name'],
                transaction_type=data['transaction_type'],
                units=float(data['units']),
                nav=float(data['nav'])
            )
            return jsonify({'success': True, 'message': 'Transaction added'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    elif request.method == 'DELETE':
        # Delete transaction
        try:
            index = int(request.args.get('index'))
            if portfolio.delete_transaction(index):
                return jsonify({'success': True, 'message': 'Transaction deleted'})
            else:
                return jsonify({'success': False, 'error': 'Invalid index'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio summary and holdings"""
    try:
        # Get unique scheme codes
        scheme_codes = set(t.scheme_code for t in portfolio.transactions)

        if not scheme_codes:
            return jsonify({
                'success': True,
                'summary': {
                    'total_schemes': 0,
                    'total_invested': 0,
                    'current_value': 0,
                    'total_gain_loss': 0,
                    'total_gain_loss_percentage': 0
                },
                'holdings': []
            })

        # Fetch current NAVs
        current_navs = {}
        for code in scheme_codes:
            try:
                nav_data = fetcher.get_latest_nav(code)
                if nav_data:
                    current_navs[code] = float(nav_data['nav'])
            except:
                pass

        # Get summary
        summary = portfolio.get_summary(current_navs)

        # Convert holdings to dict
        holdings = [h.to_dict() for h in summary['holdings']]
        del summary['holdings']

        return jsonify({
            'success': True,
            'summary': summary,
            'holdings': holdings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/capital-gains')
def get_capital_gains():
    """Calculate capital gains"""
    try:
        is_equity = request.args.get('is_equity', 'true').lower() == 'true'
        gains = portfolio.calculate_capital_gains(is_equity=is_equity)

        # Calculate totals
        total_stcg = sum(g.gain_loss for g in gains if g.gain_type == 'STCG')
        total_ltcg = sum(g.gain_loss for g in gains if g.gain_type == 'LTCG')

        return jsonify({
            'success': True,
            'gains': [g.to_dict() for g in gains],
            'summary': {
                'total_stcg': round(total_stcg, 2),
                'total_ltcg': round(total_ltcg, 2),
                'total': round(total_stcg + total_ltcg, 2)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Mutual Fund Portfolio Dashboard")
    print("=" * 60)
    print("\n  Dashboard URL: http://localhost:5000")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
