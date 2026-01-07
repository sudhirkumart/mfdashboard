"""
Configuration Module for MF Dashboard
Centralized configuration for the mutual fund dashboard application
"""

from pathlib import Path
import os

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
OUTPUT_DIR = DATA_DIR / "output"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
MFAPI_BASE_URL = "https://api.mfapi.in/mf"
CACHE_DURATION_HOURS = 24  # Cache NAV data for 24 hours
REQUEST_TIMEOUT = 10  # seconds

# Portfolio Configuration
DEFAULT_PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
SAMPLE_PORTFOLIO_FILE = DATA_DIR / "sample_portfolio.json"

# Excel Export Configuration
EXCEL_EXPORT_DIR = OUTPUT_DIR
EXCEL_DEFAULT_FILENAME = "portfolio_export.xlsx"

# PDF/CAS Configuration
CAS_UPLOAD_DIR = DATA_DIR / "cas_uploads"
CAS_UPLOAD_DIR.mkdir(exist_ok=True)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = DATA_DIR / "mf_dashboard.log"

# Capital Gains Tax Configuration (India - as of 2024)
LTCG_THRESHOLD_DAYS_EQUITY = 365  # Long-term if held > 1 year
LTCG_THRESHOLD_DAYS_DEBT = 1095  # Long-term if held > 3 years
LTCG_EXEMPTION_EQUITY = 100000  # ₹1 lakh exemption for equity LTCG
LTCG_TAX_RATE_EQUITY = 10.0  # 10% above exemption
STCG_TAX_RATE_EQUITY = 15.0  # 15% for equity
LTCG_TAX_RATE_DEBT = 20.0  # 20% with indexation
STCG_TAX_RATE_DEBT = 30.0  # As per income tax slab

# Dashboard Configuration
DASHBOARD_DIR = BASE_DIR / "dashboard"
DASHBOARD_PORT = 8000
DASHBOARD_HOST = "localhost"

# Google Sheets Configuration
GOOGLE_SHEETS_SCRIPT_DIR = BASE_DIR / "google_sheets"

# Scheme Categories (for classification)
SCHEME_CATEGORIES = {
    'equity': ['equity', 'large cap', 'mid cap', 'small cap', 'multi cap', 'flexi cap'],
    'debt': ['debt', 'liquid', 'gilt', 'credit risk', 'banking', 'dynamic bond'],
    'hybrid': ['hybrid', 'balanced', 'aggressive', 'conservative', 'arbitrage'],
    'index': ['index', 'etf', 'fof'],
    'other': ['other', 'solution oriented']
}

# Common Scheme Codes (for quick reference)
POPULAR_SCHEMES = {
    'HDFC Top 100': '119551',
    'Axis Bluechip': '118989',
    'SBI Small Cap': '120503',
    'ICICI Prudential Bluechip': '120465',
    'Parag Parikh Flexi Cap': '122639',
    'SBI Liquid Fund': '119183',
    'HDFC Hybrid Equity': '103009'
}

# Display Formats
CURRENCY_FORMAT = "₹{:,.2f}"
PERCENTAGE_FORMAT = "{:.2f}%"
DATE_FORMAT = "%d-%m-%Y"
DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"

# Calculation Settings
XIRR_MAX_ITERATIONS = 100
XIRR_TOLERANCE = 1e-6
XIRR_DEFAULT_GUESS = 0.1

# Web Server Settings (for serving dashboard)
SERVER_CONFIG = {
    'host': DASHBOARD_HOST,
    'port': DASHBOARD_PORT,
    'debug': os.getenv("DEBUG", "False").lower() == "true",
    'threaded': True
}

# Export Settings
EXPORT_FORMATS = ['excel', 'json', 'pdf', 'csv']

# API Rate Limiting (to be respectful to MFAPI.in)
API_RATE_LIMIT_CALLS = 100
API_RATE_LIMIT_PERIOD = 60  # seconds

# Feature Flags
ENABLE_CAS_PARSING = True
ENABLE_EXCEL_EXPORT = True
ENABLE_PDF_EXPORT = False  # Requires additional dependencies
ENABLE_GOOGLE_SHEETS = True

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    LOG_LEVEL = "WARNING"
    CACHE_DURATION_HOURS = 12
elif os.getenv("ENVIRONMENT") == "development":
    LOG_LEVEL = "DEBUG"
    CACHE_DURATION_HOURS = 1

# Version
VERSION = "1.0.0"
APP_NAME = "MF Dashboard"

# Print configuration (for debugging)
def print_config():
    """Print current configuration"""
    print(f"\n{APP_NAME} v{VERSION} Configuration")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Cache Directory: {CACHE_DIR}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"API Base URL: {MFAPI_BASE_URL}")
    print(f"Cache Duration: {CACHE_DURATION_HOURS} hours")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Dashboard: http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
