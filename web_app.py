"""
Flask Web Dashboard for Investments (Mutual Funds & Stocks)

Run: python web_app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_file
from mfapi_fetcher import MFAPIFetcher
from portfolio_manager import PortfolioManager
from backend.csv_export import CSVExporter
from backend.excel_export import ExcelExporter
from backend.data_import import DataImporter
from backend.sheets_integration import GoogleSheetsReader
from datetime import datetime
from pathlib import Path
import json
import os

app = Flask(__name__)
fetcher = MFAPIFetcher()
portfolio = PortfolioManager()

# Ensure output directory exists
OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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
        # Add new transaction (supports both mutual funds and stocks)
        try:
            data = request.json
            portfolio.add_transaction(
                date=data['date'],
                scheme_code=data['scheme_code'],
                scheme_name=data['scheme_name'],
                transaction_type=data['transaction_type'],
                units=float(data['units']),
                nav=float(data['nav']),
                asset_type=data.get('asset_type', 'MUTUAL_FUND'),  # Default to MF for backward compatibility
                exchange=data.get('exchange', ''),
                notes=data.get('notes', '')
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
    """Get portfolio summary and holdings with asset type breakdown"""
    try:
        # Get unique asset identifiers (MF scheme codes + stock symbols)
        mf_codes = portfolio.get_mf_scheme_codes()
        stock_symbols = portfolio.get_stock_symbols()

        if not mf_codes and not stock_symbols:
            return jsonify({
                'success': True,
                'summary': {
                    'total': {'count': 0, 'invested': 0, 'current_value': 0, 'gain_loss': 0, 'gain_loss_pct': 0},
                    'mutual_funds': {'count': 0, 'invested': 0, 'current_value': 0, 'gain_loss': 0, 'gain_loss_pct': 0},
                    'stocks': {'count': 0, 'invested': 0, 'current_value': 0, 'gain_loss': 0, 'gain_loss_pct': 0}
                },
                'holdings': [],
                'holdings_by_type': {'mutual_funds': [], 'stocks': []}
            })

        # Fetch current prices (unified: NAVs for MFs + prices for stocks)
        current_prices = {}

        # Fetch MF NAVs
        for code in mf_codes:
            try:
                nav_data = fetcher.get_latest_nav(code)
                if nav_data:
                    current_prices[code] = float(nav_data['nav'])
            except:
                pass

        # Fetch stock prices from StockPriceManager
        from backend.stock_price_manager import StockPriceManager
        stock_manager = StockPriceManager()

        for symbol in stock_symbols:
            # Symbol format: RELIANCE.NS
            if '.' in symbol:
                parts = symbol.split('.')
                base_symbol = parts[0]
                exchange = "NSE" if parts[1] == "NS" else "BSE"

                price_data = stock_manager.get_price(base_symbol, exchange)
                if price_data:
                    current_prices[symbol] = price_data['price']

        # Get comprehensive summary with asset type breakdown
        portfolio_summary = portfolio.get_portfolio_summary(current_prices)

        # Convert holdings to dict
        all_holdings = [h.to_dict() for h in portfolio_summary['all_holdings']]
        mf_holdings = [h.to_dict() for h in portfolio_summary['holdings_by_type']['mutual_funds']]
        stock_holdings = [h.to_dict() for h in portfolio_summary['holdings_by_type']['stocks']]

        return jsonify({
            'success': True,
            'summary': {
                'total': portfolio_summary['total'],
                'mutual_funds': portfolio_summary['mutual_funds'],
                'stocks': portfolio_summary['stocks']
            },
            'holdings': all_holdings,
            'holdings_by_type': {
                'mutual_funds': mf_holdings,
                'stocks': stock_holdings
            }
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


@app.route('/api/export/json')
def export_json():
    """Export portfolio to JSON"""
    try:
        # Create portfolio data structure
        portfolio_data = _create_portfolio_data()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'portfolio_{timestamp}.json'
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, indent=2)

        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/csv')
def export_csv():
    """Export portfolio to CSV (Holdings)"""
    try:
        portfolio_data = _create_portfolio_data()
        exporter = CSVExporter()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'holdings_{timestamp}.csv'
        filepath = OUTPUT_DIR / filename

        exporter.export_holdings(portfolio_data, str(filepath))

        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/csv/transactions')
def export_csv_transactions():
    """Export transactions to CSV"""
    try:
        portfolio_data = _create_portfolio_data()
        exporter = CSVExporter()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'transactions_{timestamp}.csv'
        filepath = OUTPUT_DIR / filename

        exporter.export_transactions(portfolio_data, str(filepath))

        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/excel')
def export_excel():
    """Export portfolio to Excel"""
    try:
        portfolio_data = _create_portfolio_data()
        exporter = ExcelExporter()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'portfolio_{timestamp}.xlsx'
        filepath = OUTPUT_DIR / filename

        exporter.export_portfolio(portfolio_data, str(filepath))

        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import/json', methods=['POST'])
def import_json():
    """Import portfolio from JSON file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Read and parse JSON
        data = json.load(file)

        # Import transactions
        count = _import_portfolio_data(data)

        return jsonify({
            'success': True,
            'message': f'Successfully imported {count} transactions'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import portfolio from CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Save file temporarily
        temp_path = OUTPUT_DIR / 'temp_import.csv'
        file.save(temp_path)

        # Import using DataImporter
        importer = DataImporter()
        portfolio_data = importer.csv_to_portfolio(
            str(temp_path),
            transactions_csv=None,
            pan="IMPORTED"
        )

        # Import into current portfolio
        count = _import_portfolio_data(portfolio_data)

        # Clean up
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'message': f'Successfully imported {count} transactions'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import/excel', methods=['POST'])
def import_excel():
    """Import portfolio from Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Save file temporarily
        temp_path = OUTPUT_DIR / 'temp_import.xlsx'
        file.save(temp_path)

        # Import using DataImporter
        importer = DataImporter()
        portfolio_data = importer.excel_to_portfolio(str(temp_path), pan="IMPORTED")

        # Import into current portfolio
        count = _import_portfolio_data(portfolio_data)

        # Clean up
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'message': f'Successfully imported {count} transactions'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def _create_portfolio_data():
    """Convert current portfolio manager data to portfolio format"""
    # Get current NAVs for all schemes
    scheme_codes = set(t.scheme_code for t in portfolio.transactions)
    current_navs = {}

    for code in scheme_codes:
        try:
            nav_data = fetcher.get_latest_nav(code)
            if nav_data:
                current_navs[code] = float(nav_data['nav'])
        except:
            pass

    # Get summary to get holdings
    summary = portfolio.get_summary(current_navs)
    holdings = summary['holdings']

    # Build holdings with transactions
    holdings_data = []
    for holding in holdings:
        # Get transactions for this scheme
        scheme_txns = [t for t in portfolio.transactions if t.scheme_code == holding.scheme_code]

        holding_dict = {
            'scheme_code': holding.scheme_code,
            'scheme_name': holding.scheme_name,
            'folio': '',
            'category': '',
            'units': holding.total_units,
            'invested': holding.invested_amount,
            'current_nav': holding.current_nav,
            'current_value': holding.current_value,
            'nav_date': datetime.now().strftime('%Y-%m-%d'),
            'transactions': [
                {
                    'date': t.date,
                    'type': t.transaction_type.lower(),
                    'units': t.units,
                    'nav': t.nav
                }
                for t in scheme_txns
            ]
        }
        holdings_data.append(holding_dict)

    return {
        'portfolio_name': 'My Portfolio',
        'created_date': datetime.now().isoformat(),
        'accounts': {
            'DEFAULT': {
                'name': 'Default Account',
                'email': '',
                'holdings': holdings_data
            }
        }
    }


def _import_portfolio_data(portfolio_data):
    """Import portfolio data into portfolio manager"""
    count = 0

    for pan, account in portfolio_data.get('accounts', {}).items():
        for holding in account.get('holdings', []):
            for txn in holding.get('transactions', []):
                portfolio.add_transaction(
                    date=txn['date'],
                    scheme_code=holding['scheme_code'],
                    scheme_name=holding['scheme_name'],
                    transaction_type=txn['type'].upper(),
                    units=float(txn['units']),
                    nav=float(txn['nav'])
                )
                count += 1

    return count


# ========== STOCK PRICE MANAGEMENT ENDPOINTS ==========

@app.route('/api/stocks/prices', methods=['GET'])
def get_all_stock_prices():
    """Get all cached stock prices"""
    try:
        from backend.stock_price_manager import StockPriceManager
        stock_manager = StockPriceManager()

        all_prices = stock_manager.get_all_prices()

        return jsonify({
            'success': True,
            'prices': all_prices,
            'count': len(all_prices)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks/price', methods=['GET', 'POST'])
def manage_stock_price():
    """Get or set stock price"""
    try:
        from backend.stock_price_manager import StockPriceManager
        stock_manager = StockPriceManager()

        if request.method == 'GET':
            # Get price for specific stock
            symbol = request.args.get('symbol')
            exchange = request.args.get('exchange', 'NSE')

            if not symbol:
                return jsonify({'success': False, 'error': 'Missing symbol parameter'}), 400

            price_data = stock_manager.get_price(symbol, exchange)

            if price_data:
                return jsonify({
                    'success': True,
                    'price': price_data
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'No price found for {symbol}.{exchange}'
                }), 404

        elif request.method == 'POST':
            # Set manual price
            data = request.json

            if not all(k in data for k in ['symbol', 'exchange', 'price']):
                return jsonify({'success': False, 'error': 'Missing required fields: symbol, exchange, price'}), 400

            success = stock_manager.set_manual_price(
                symbol=data['symbol'],
                exchange=data['exchange'],
                price=float(data['price']),
                price_date=data.get('date'),
                company_name=data.get('company_name')
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': f'Price set for {data["symbol"]}.{data["exchange"]}'
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to set price'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stocks/search/<query>', methods=['GET'])
def search_stocks(query):
    """
    Search for stock symbols (initially manual list, future: API integration)
    """
    try:
        # Manual list of popular Indian stocks for now
        # In future, this will call a stock API
        popular_stocks = [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries Limited', 'exchange': 'NSE'},
            {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'exchange': 'NSE'},
            {'symbol': 'INFY.NS', 'name': 'Infosys Limited', 'exchange': 'NSE'},
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank Limited', 'exchange': 'NSE'},
            {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank Limited', 'exchange': 'NSE'},
            {'symbol': 'HINDUNILVR.NS', 'name': 'Hindustan Unilever Limited', 'exchange': 'NSE'},
            {'symbol': 'ITC.NS', 'name': 'ITC Limited', 'exchange': 'NSE'},
            {'symbol': 'SBIN.NS', 'name': 'State Bank of India', 'exchange': 'NSE'},
            {'symbol': 'BHARTIARTL.NS', 'name': 'Bharti Airtel Limited', 'exchange': 'NSE'},
            {'symbol': 'KOTAKBANK.NS', 'name': 'Kotak Mahindra Bank Limited', 'exchange': 'NSE'},
            {'symbol': 'LT.NS', 'name': 'Larsen & Toubro Limited', 'exchange': 'NSE'},
            {'symbol': 'ASIANPAINT.NS', 'name': 'Asian Paints Limited', 'exchange': 'NSE'},
            {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki India Limited', 'exchange': 'NSE'},
            {'symbol': 'WIPRO.NS', 'name': 'Wipro Limited', 'exchange': 'NSE'},
            {'symbol': 'ADANIENT.NS', 'name': 'Adani Enterprises Limited', 'exchange': 'NSE'}
        ]

        # Filter by search query
        query_lower = query.lower()
        filtered_stocks = [
            s for s in popular_stocks
            if query_lower in s['name'].lower() or query_lower in s['symbol'].lower()
        ]

        return jsonify({
            'success': True,
            'stocks': filtered_stocks[:10],  # Limit to 10 results
            'count': len(filtered_stocks)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/insights', methods=['GET'])
def get_insights():
    """
    Fetch insights/tips from Google Spreadsheet.
    Returns:
        JSON with insights data
    """
    try:
        # Google Spreadsheet configuration
        SPREADSHEET_ID = "1Bih9HJltbVwKzhJr3MdkFUB-Hh261oTEFBjI5s7TlR4"
        GID = "756728702"

        # Fetch insights from Google Sheets
        reader = GoogleSheetsReader(SPREADSHEET_ID, GID)
        result = reader.get_insights()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  Investments Dashboard")
    print("=" * 60)
    print("\n  Dashboard URL: http://localhost:5000")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
