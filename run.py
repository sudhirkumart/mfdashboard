"""
Quick launcher for MF Dashboard

Choose how you want to run the application.
"""

import sys

def main():
    print("\n" + "="*60)
    print("  MF Dashboard - Portfolio Manager")
    print("="*60)
    print("\nSelect application mode:")
    print("  1. CLI Application (Terminal interface)")
    print("  2. Web Dashboard (Browser interface)")
    print("  3. API Fetcher Server (Standalone MF data API)")
    print("  4. API Example")
    print("  0. Exit")
    print("-"*60)

    choice = input("\nEnter choice: ").strip()

    if choice == "1":
        print("\nLaunching CLI Application...\n")
        import portfolio_app
        portfolio_app.main()
    elif choice == "2":
        print("\nLaunching Web Dashboard...")
        print("Open http://localhost:5000 in your browser\n")
        import web_app
    elif choice == "3":
        print("\nLaunching API Fetcher Server...")
        print("API Documentation: http://localhost:8000/docs")
        print("API Root: http://localhost:8000\n")
        import fetcher_api
    elif choice == "4":
        print("\nRunning API Example...\n")
        import example_usage
        example_usage.main()
    elif choice == "0":
        print("\nGoodbye!")
    else:
        print("\nInvalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
