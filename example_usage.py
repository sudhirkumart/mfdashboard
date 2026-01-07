"""
Example usage of MFAPIFetcher

This script demonstrates various features of the MFAPI fetcher with caching.
"""

from mfapi_fetcher import MFAPIFetcher
import time


def main():
    # Initialize fetcher with custom cache settings
    # Cache TTL set to 30 minutes (1800 seconds)
    fetcher = MFAPIFetcher(cache_ttl=1800)

    print("=" * 60)
    print("MFAPI Fetcher - Example Usage")
    print("=" * 60)

    # 1. Get cache information
    print("\n1. Cache Information:")
    print("-" * 60)
    cache_info = fetcher.get_cache_info()
    print(f"Cache directory: {cache_info['cache_dir']}")
    print(f"Cached files: {cache_info['total_files']}")
    print(f"Cache size: {cache_info['total_size_mb']} MB")
    print(f"Cache TTL: {cache_info['cache_ttl_seconds']} seconds")

    # 2. Search for mutual fund schemes
    print("\n2. Searching for Mutual Fund Schemes:")
    print("-" * 60)
    search_query = "HDFC Equity"
    print(f"Searching for: '{search_query}'")

    start_time = time.time()
    schemes = fetcher.search_schemes(search_query)
    elapsed = time.time() - start_time

    print(f"Found {len(schemes)} schemes in {elapsed:.2f} seconds")
    print("\nFirst 5 results:")
    for i, scheme in enumerate(schemes[:5], 1):
        print(f"  {i}. {scheme['schemeName']} (Code: {scheme['schemeCode']})")

    # 3. Get detailed scheme information
    if schemes:
        print("\n3. Getting Detailed Scheme Information:")
        print("-" * 60)
        selected_scheme = schemes[0]
        scheme_code = selected_scheme['schemeCode']

        print(f"Fetching details for: {selected_scheme['schemeName']}")

        start_time = time.time()
        scheme_details = fetcher.get_scheme(scheme_code)
        elapsed = time.time() - start_time

        print(f"Fetched in {elapsed:.2f} seconds")
        print(f"\nScheme Information:")
        print(f"  Name: {scheme_details['meta']['scheme_name']}")
        print(f"  Code: {scheme_details['meta']['scheme_code']}")
        print(f"  Category: {scheme_details['meta'].get('scheme_category', 'N/A')}")
        print(f"  Type: {scheme_details['meta'].get('scheme_type', 'N/A')}")

        # 4. Get latest NAV
        print("\n4. Latest NAV:")
        print("-" * 60)
        nav_info = fetcher.get_latest_nav(scheme_code)
        if nav_info:
            print(f"  Date: {nav_info['date']}")
            print(f"  NAV: Rs.{nav_info['nav']}")

        # 5. Show historical NAV data
        print("\n5. Historical NAV (Last 5 days):")
        print("-" * 60)
        if 'data' in scheme_details and scheme_details['data']:
            for i, record in enumerate(scheme_details['data'][:5], 1):
                print(f"  {i}. {record['date']}: Rs.{record['nav']}")

        # 6. Demonstrate caching benefit
        print("\n6. Demonstrating Cache Benefit:")
        print("-" * 60)
        print("Fetching same scheme again...")

        start_time = time.time()
        scheme_details_cached = fetcher.get_scheme(scheme_code)
        elapsed_cached = time.time() - start_time

        print(f"Cached fetch: {elapsed_cached:.4f} seconds")
        print(f"Speedup: {elapsed / elapsed_cached:.1f}x faster!")

    # 7. Get all schemes (warning: large response)
    print("\n7. Getting All Schemes:")
    print("-" * 60)
    print("Fetching complete list of schemes...")

    start_time = time.time()
    all_schemes = fetcher.get_all_schemes()
    elapsed = time.time() - start_time

    print(f"Total schemes available: {len(all_schemes)}")
    print(f"Fetched in {elapsed:.2f} seconds")

    # 8. Cache statistics after operations
    print("\n8. Updated Cache Information:")
    print("-" * 60)
    cache_info = fetcher.get_cache_info()
    print(f"Cached files: {cache_info['total_files']}")
    print(f"Cache size: {cache_info['total_size_mb']} MB")

    # 9. Clear specific cache (optional)
    print("\n9. Cache Management:")
    print("-" * 60)
    print("You can clear cache using:")
    print("  - fetcher.clear_cache()           # Clear all cache")
    print(f"  - fetcher.clear_cache('{scheme_code}')  # Clear specific scheme")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
