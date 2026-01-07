"""
Mutual Fund API Module
Handles NAV data fetching from MFAPI.in with intelligent caching
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MFAPIClient:
    """Client for fetching mutual fund data from MFAPI.in"""

    BASE_URL = "https://api.mfapi.in/mf"
    CACHE_DIR = Path("data/cache")
    CACHE_DURATION_HOURS = 24

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize MFAPI client

        Args:
            cache_enabled: Whether to use cache for API responses
        """
        self.cache_enabled = cache_enabled
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()

    def _get_cache_path(self, scheme_code: str) -> Path:
        """Get cache file path for a scheme"""
        return self.CACHE_DIR / f"{scheme_code}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid"""
        if not cache_path.exists():
            return False

        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age < timedelta(hours=self.CACHE_DURATION_HOURS)

    def _load_from_cache(self, scheme_code: str) -> Optional[Dict]:
        """Load data from cache if available and valid"""
        if not self.cache_enabled:
            return None

        cache_path = self._get_cache_path(scheme_code)
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Loading scheme {scheme_code} from cache")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache for {scheme_code}: {e}")
        return None

    def _save_to_cache(self, scheme_code: str, data: Dict) -> None:
        """Save data to cache"""
        if not self.cache_enabled:
            return

        cache_path = self._get_cache_path(scheme_code)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Cached data for scheme {scheme_code}")
        except Exception as e:
            logger.warning(f"Error saving cache for {scheme_code}: {e}")

    def get_scheme_details(self, scheme_code: str) -> Optional[Dict]:
        """
        Get scheme details including NAV history

        Args:
            scheme_code: Mutual fund scheme code

        Returns:
            Dictionary containing scheme details and NAV data
        """
        # Try cache first
        cached_data = self._load_from_cache(scheme_code)
        if cached_data:
            return cached_data

        # Fetch from API
        try:
            url = f"{self.BASE_URL}/{scheme_code}"
            logger.info(f"Fetching scheme {scheme_code} from API")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Validate response
            if data.get('status') == 'SUCCESS':
                self._save_to_cache(scheme_code, data)
                return data
            else:
                logger.error(f"API returned error for scheme {scheme_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Error fetching scheme {scheme_code}: {e}")
            return None

    def get_latest_nav(self, scheme_code: str) -> Optional[Dict]:
        """
        Get latest NAV for a scheme

        Args:
            scheme_code: Mutual fund scheme code

        Returns:
            Dictionary with date and NAV value
        """
        scheme_data = self.get_scheme_details(scheme_code)
        if scheme_data and 'data' in scheme_data and len(scheme_data['data']) > 0:
            latest = scheme_data['data'][0]
            return {
                'date': latest['date'],
                'nav': float(latest['nav']),
                'scheme_name': scheme_data['meta']['scheme_name']
            }
        return None

    def get_nav_on_date(self, scheme_code: str, target_date: str) -> Optional[float]:
        """
        Get NAV for a specific date (or nearest previous date)

        Args:
            scheme_code: Mutual fund scheme code
            target_date: Date in DD-MM-YYYY format

        Returns:
            NAV value as float
        """
        scheme_data = self.get_scheme_details(scheme_code)
        if not scheme_data or 'data' not in scheme_data:
            return None

        target_dt = datetime.strptime(target_date, '%d-%m-%Y')

        for nav_entry in scheme_data['data']:
            nav_date = datetime.strptime(nav_entry['date'], '%d-%m-%Y')
            if nav_date <= target_dt:
                return float(nav_entry['nav'])

        return None

    def get_nav_history(self, scheme_code: str, days: int = 365) -> List[Dict]:
        """
        Get NAV history for specified number of days

        Args:
            scheme_code: Mutual fund scheme code
            days: Number of days of history to fetch

        Returns:
            List of NAV entries
        """
        scheme_data = self.get_scheme_details(scheme_code)
        if not scheme_data or 'data' not in scheme_data:
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        history = []

        for nav_entry in scheme_data['data']:
            nav_date = datetime.strptime(nav_entry['date'], '%d-%m-%Y')
            if nav_date >= cutoff_date:
                history.append({
                    'date': nav_entry['date'],
                    'nav': float(nav_entry['nav'])
                })
            else:
                break

        return history

    def search_schemes(self, keyword: str) -> List[Dict]:
        """
        Search for schemes by keyword (requires fetching scheme list)

        Args:
            keyword: Search keyword

        Returns:
            List of matching schemes
        """
        try:
            url = self.BASE_URL
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            all_schemes = response.json()
            keyword_lower = keyword.lower()

            matches = [
                scheme for scheme in all_schemes
                if keyword_lower in scheme['schemeName'].lower()
            ]

            return matches[:20]  # Limit to top 20 results

        except requests.RequestException as e:
            logger.error(f"Error searching schemes: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear all cached data"""
        for cache_file in self.CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")


if __name__ == "__main__":
    # Quick test
    client = MFAPIClient()

    # Test with HDFC Top 100 Fund
    scheme_code = "119551"

    print("Testing MFAPIClient...")
    print(f"\nFetching latest NAV for scheme {scheme_code}...")
    nav_data = client.get_latest_nav(scheme_code)
    if nav_data:
        print(f"Scheme: {nav_data['scheme_name']}")
        print(f"Date: {nav_data['date']}")
        print(f"NAV: ₹{nav_data['nav']}")

    print("\nFetching 30-day history...")
    history = client.get_nav_history(scheme_code, days=30)
    print(f"Retrieved {len(history)} NAV entries")

    print("\nSearching for 'HDFC' schemes...")
    schemes = client.search_schemes("HDFC")
    print(f"Found {len(schemes)} schemes")
    for scheme in schemes[:5]:
        print(f"  - {scheme['schemeName']} (Code: {scheme['schemeCode']})")
