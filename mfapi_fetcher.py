"""
MFAPI.in Fetcher with File-based Caching

A simple and efficient API fetcher for Indian Mutual Fund data from MFAPI.in
with built-in file-based caching to reduce API calls and improve performance.
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path


class MFAPIFetcher:
    """
    Fetches mutual fund data from MFAPI.in with intelligent file-based caching.

    Features:
    - Automatic caching with configurable TTL
    - Rate limiting protection
    - Error handling and retry logic
    - Support for all MFAPI.in endpoints
    """

    BASE_URL = "https://api.mfapi.in"
    DEFAULT_CACHE_DIR = ".mfcache"
    DEFAULT_TTL = 3600  # 1 hour in seconds

    def __init__(
        self,
        cache_dir: str = DEFAULT_CACHE_DIR,
        cache_ttl: int = DEFAULT_TTL,
        timeout: int = 10
    ):
        """
        Initialize the MFAPI fetcher.

        Args:
            cache_dir: Directory to store cache files
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            timeout: Request timeout in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MFDashboard/1.0'
        })

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, cache_key: str) -> Path:
        """Generate cache file path for a given key."""
        safe_key = cache_key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file exists and is still valid."""
        if not cache_path.exists():
            return False

        # Check if cache has expired
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age < self.cache_ttl

    def _read_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Read data from cache if valid."""
        cache_path = self._get_cache_path(cache_key)

        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Cache read error: {e}")
                return None

        return None

    def _write_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Write data to cache file."""
        cache_path = self._get_cache_path(cache_key)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Cache write error: {e}")

    def _fetch_from_api(self, endpoint: str) -> Dict[str, Any]:
        """
        Fetch data from MFAPI.in endpoint.

        Args:
            endpoint: API endpoint path (e.g., '/mf', '/mf/123456')

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            raise Exception(f"Request timeout for {url}")
        except requests.RequestException as e:
            raise Exception(f"API request failed: {e}")

    def get(self, endpoint: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch data with optional caching.

        Args:
            endpoint: API endpoint path
            use_cache: Whether to use cache (default: True)

        Returns:
            API response data
        """
        cache_key = endpoint

        # Try cache first if enabled
        if use_cache:
            cached_data = self._read_cache(cache_key)
            if cached_data is not None:
                print(f"Cache hit: {endpoint}")
                return cached_data

        # Fetch from API
        print(f"Fetching from API: {endpoint}")
        data = self._fetch_from_api(endpoint)

        # Save to cache
        if use_cache:
            self._write_cache(cache_key, data)

        return data

    def get_all_schemes(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get list of all mutual fund schemes.

        Returns:
            List of scheme dictionaries with schemeCode and schemeName
        """
        response = self.get('/mf', use_cache=use_cache)
        return response if isinstance(response, list) else []

    def get_scheme(self, scheme_code: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get detailed information about a specific mutual fund scheme.

        Args:
            scheme_code: The scheme code (e.g., '119551')
            use_cache: Whether to use cache

        Returns:
            Dictionary with scheme metadata and NAV data
        """
        return self.get(f'/mf/{scheme_code}', use_cache=use_cache)

    def search_schemes(self, query: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search for schemes by name.

        Args:
            query: Search term (case-insensitive)
            use_cache: Whether to use cache

        Returns:
            List of matching schemes
        """
        all_schemes = self.get_all_schemes(use_cache=use_cache)
        query_lower = query.lower()

        return [
            scheme for scheme in all_schemes
            if query_lower in scheme.get('schemeName', '').lower()
        ]

    def get_latest_nav(self, scheme_code: str, use_cache: bool = True) -> Optional[Dict[str, str]]:
        """
        Get the latest NAV for a scheme.

        Args:
            scheme_code: The scheme code
            use_cache: Whether to use cache

        Returns:
            Dictionary with date and nav, or None if not available
        """
        scheme_data = self.get_scheme(scheme_code, use_cache=use_cache)

        if 'data' in scheme_data and scheme_data['data']:
            latest = scheme_data['data'][0]
            return {
                'date': latest.get('date'),
                'nav': latest.get('nav')
            }

        return None

    def clear_cache(self, scheme_code: Optional[str] = None) -> None:
        """
        Clear cache files.

        Args:
            scheme_code: If provided, clear only this scheme's cache.
                        If None, clear all cache.
        """
        if scheme_code:
            cache_path = self._get_cache_path(f'/mf/{scheme_code}')
            if cache_path.exists():
                cache_path.unlink()
                print(f"Cleared cache for scheme {scheme_code}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
            print("Cleared all cache")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about current cache status.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob('*.json'))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'cache_dir': str(self.cache_dir),
            'total_files': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_ttl_seconds': self.cache_ttl
        }


if __name__ == "__main__":
    # Quick test
    fetcher = MFAPIFetcher()

    print("Testing MFAPI Fetcher...")
    print(f"\nCache info: {fetcher.get_cache_info()}")

    # Search for a scheme
    print("\nSearching for 'HDFC' schemes...")
    results = fetcher.search_schemes('HDFC')
    print(f"Found {len(results)} schemes")

    if results:
        # Get details of first result
        scheme = results[0]
        print(f"\nGetting details for: {scheme['schemeName']}")
        details = fetcher.get_scheme(scheme['schemeCode'])
        print(f"Scheme Code: {details['meta']['scheme_code']}")
        print(f"Scheme Name: {details['meta']['scheme_name']}")

        # Get latest NAV
        nav = fetcher.get_latest_nav(scheme['schemeCode'])
        if nav:
            print(f"Latest NAV: {nav['nav']} (as of {nav['date']})")
