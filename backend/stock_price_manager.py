"""
Stock Price Manager
Handles manual stock price entry with extensible design for future API integration
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockPriceManager:
    """
    Manages stock prices with manual entry and cache.
    Designed to be extensible for future API integration (yfinance, Alpha Vantage, etc.)
    """

    DEFAULT_CACHE_FILE = "stock_prices.json"

    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE):
        """
        Initialize Stock Price Manager.

        Args:
            cache_file: Path to JSON file for storing stock prices
        """
        self.cache_file = Path(cache_file)
        self.prices: Dict[str, Dict] = {}
        self.load_prices()

    def load_prices(self) -> None:
        """Load cached stock prices from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.prices = json.load(f)
                logger.info(f"Loaded {len(self.prices)} stock prices from cache")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load stock prices: {e}")
                self.prices = {}
        else:
            logger.info("No stock price cache found. Starting with empty cache.")
            self.prices = {}

    def save_prices(self) -> None:
        """Save stock prices to cache file"""
        try:
            # Ensure parent directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.prices, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.prices)} stock prices to cache")
        except IOError as e:
            logger.error(f"Failed to save stock prices: {e}")

    def _normalize_symbol(self, symbol: str, exchange: str) -> str:
        """
        Normalize stock symbol with exchange.

        Args:
            symbol: Stock ticker (e.g., "RELIANCE" or "RELIANCE.NS")
            exchange: Exchange name ("NSE" or "BSE")

        Returns:
            Normalized symbol (e.g., "RELIANCE.NS")
        """
        # Remove existing exchange suffix if present
        base_symbol = symbol.split('.')[0].upper()

        # Add exchange suffix
        if exchange.upper() == "NSE":
            return f"{base_symbol}.NS"
        elif exchange.upper() == "BSE":
            return f"{base_symbol}.BO"  # BSE uses .BO (Bombay)
        else:
            return f"{base_symbol}.{exchange.upper()}"

    def set_manual_price(
        self,
        symbol: str,
        exchange: str,
        price: float,
        price_date: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> bool:
        """
        Set stock price manually.

        Args:
            symbol: Stock ticker (e.g., "RELIANCE")
            exchange: Exchange name ("NSE" or "BSE")
            price: Current price
            price_date: Price date (YYYY-MM-DD format, defaults to today)
            company_name: Optional company name

        Returns:
            bool: True if price was set successfully
        """
        try:
            normalized_symbol = self._normalize_symbol(symbol, exchange)

            if price_date is None:
                price_date = datetime.now().strftime('%Y-%m-%d')

            # Validate price
            if price <= 0:
                logger.error(f"Invalid price: {price}")
                return False

            self.prices[normalized_symbol] = {
                'symbol': normalized_symbol,
                'exchange': exchange.upper(),
                'price': float(price),
                'date': price_date,
                'source': 'manual',
                'updated_at': datetime.now().isoformat()
            }

            # Add company name if provided
            if company_name:
                self.prices[normalized_symbol]['company_name'] = company_name

            self.save_prices()
            logger.info(f"Set price for {normalized_symbol}: Rs.{price}")
            return True

        except Exception as e:
            logger.error(f"Error setting price for {symbol}: {e}")
            return False

    def get_price(self, symbol: str, exchange: str) -> Optional[Dict]:
        """
        Get latest price for a stock.

        Args:
            symbol: Stock ticker
            exchange: Exchange name

        Returns:
            Dictionary with price info, or None if not found
        """
        normalized_symbol = self._normalize_symbol(symbol, exchange)

        if normalized_symbol in self.prices:
            return self.prices[normalized_symbol].copy()

        logger.warning(f"No price found for {normalized_symbol}")
        return None

    def get_all_prices(self) -> Dict[str, Dict]:
        """
        Get all cached stock prices.

        Returns:
            Dictionary of all prices {symbol: price_info}
        """
        return self.prices.copy()

    def get_prices_for_symbols(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get prices for multiple symbols.

        Args:
            symbols: List of normalized symbols (e.g., ["RELIANCE.NS", "TCS.NS"])

        Returns:
            Dictionary mapping symbols to price info
        """
        result = {}
        for symbol in symbols:
            # Try to find the symbol directly
            if symbol in self.prices:
                result[symbol] = self.prices[symbol].copy()
            else:
                result[symbol] = None

        return result

    def delete_price(self, symbol: str, exchange: str) -> bool:
        """
        Delete a stock price from cache.

        Args:
            symbol: Stock ticker
            exchange: Exchange name

        Returns:
            bool: True if deleted successfully
        """
        normalized_symbol = self._normalize_symbol(symbol, exchange)

        if normalized_symbol in self.prices:
            del self.prices[normalized_symbol]
            self.save_prices()
            logger.info(f"Deleted price for {normalized_symbol}")
            return True

        return False

    def update_price(self, symbol: str, exchange: str, new_price: float) -> bool:
        """
        Update existing stock price.

        Args:
            symbol: Stock ticker
            exchange: Exchange name
            new_price: New price value

        Returns:
            bool: True if updated successfully
        """
        normalized_symbol = self._normalize_symbol(symbol, exchange)

        if normalized_symbol not in self.prices:
            logger.warning(f"Price not found for {normalized_symbol}. Use set_manual_price() instead.")
            return False

        return self.set_manual_price(symbol, exchange, new_price)

    def get_cache_info(self) -> Dict:
        """
        Get information about the price cache.

        Returns:
            Dictionary with cache statistics
        """
        total_stocks = len(self.prices)
        exchanges = {}

        for price_info in self.prices.values():
            exchange = price_info.get('exchange', 'UNKNOWN')
            exchanges[exchange] = exchanges.get(exchange, 0) + 1

        return {
            'total_stocks': total_stocks,
            'by_exchange': exchanges,
            'cache_file': str(self.cache_file),
            'last_loaded': datetime.now().isoformat()
        }

    # ========== FUTURE API INTEGRATION ==========

    def fetch_from_api(self, symbol: str, exchange: str) -> Optional[Dict]:
        """
        FUTURE: Fetch price from external API (yfinance, Alpha Vantage, etc.)

        Args:
            symbol: Stock ticker
            exchange: Exchange name

        Returns:
            Price information from API

        Raises:
            NotImplementedError: This is a placeholder for future implementation
        """
        raise NotImplementedError(
            "API integration coming in future version. "
            "Currently only manual price entry is supported. "
            "Future APIs: yfinance, Alpha Vantage, NSE/BSE APIs"
        )

    def enable_api_fetching(self, api_provider: str, api_key: Optional[str] = None):
        """
        FUTURE: Enable automatic price fetching from API.

        Args:
            api_provider: API provider name ("yfinance", "alphavantage", etc.)
            api_key: API key if required

        Raises:
            NotImplementedError: Placeholder for future implementation
        """
        raise NotImplementedError(
            f"API provider '{api_provider}' not yet supported. "
            "Coming soon in future update."
        )


def main():
    """Example usage of StockPriceManager"""
    print("Stock Price Manager - Example Usage")
    print("=" * 60)

    # Initialize manager
    manager = StockPriceManager('test_stock_prices.json')

    # Set manual prices
    print("\nSetting manual prices:")
    manager.set_manual_price("RELIANCE", "NSE", 2850.50, company_name="Reliance Industries")
    manager.set_manual_price("TCS", "NSE", 3450.75, company_name="Tata Consultancy Services")
    manager.set_manual_price("INFY", "NSE", 1520.30, company_name="Infosys Limited")

    # Get price
    print("\nGetting price for RELIANCE:")
    reliance_price = manager.get_price("RELIANCE", "NSE")
    if reliance_price:
        print(f"  {reliance_price['symbol']}: Rs.{reliance_price['price']} ({reliance_price['date']})")

    # Get all prices
    print("\nAll cached prices:")
    all_prices = manager.get_all_prices()
    for symbol, info in all_prices.items():
        company = info.get('company_name', 'Unknown')
        print(f"  {symbol}: Rs.{info['price']} - {company}")

    # Get cache info
    print("\nCache information:")
    cache_info = manager.get_cache_info()
    print(f"  Total stocks: {cache_info['total_stocks']}")
    print(f"  By exchange: {cache_info['by_exchange']}")
    print(f"  Cache file: {cache_info['cache_file']}")

    print("\n" + "=" * 60)
    print("Note: API integration coming soon!")
    print("Future: Automatic price fetching from yfinance, Alpha Vantage, etc.")


if __name__ == '__main__':
    main()
