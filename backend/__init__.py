"""
MF Dashboard Backend Package
Provides core functionality for mutual fund portfolio management
"""

from backend.api import MFAPIClient
from backend.calculations import (
    xirr,
    calculate_absolute_return,
    calculate_cagr,
    calculate_capital_gains,
    calculate_sip_returns,
    calculate_portfolio_metrics
)
from backend.portfolio import Portfolio, PortfolioManager
from backend.cas_parser import CASParser, parse_cas_file
from backend.excel_export import ExcelExporter, export_to_excel
from backend.csv_export import CSVExporter, export_to_csv
from backend.data_import import DataImporter, import_from_csv, import_from_excel

__version__ = "1.0.0"
__author__ = "MF Dashboard Team"

__all__ = [
    'MFAPIClient',
    'xirr',
    'calculate_absolute_return',
    'calculate_cagr',
    'calculate_capital_gains',
    'calculate_sip_returns',
    'calculate_portfolio_metrics',
    'Portfolio',
    'PortfolioManager',
    'CASParser',
    'parse_cas_file',
    'ExcelExporter',
    'export_to_excel',
    'CSVExporter',
    'export_to_csv',
    'DataImporter',
    'import_from_csv',
    'import_from_excel',
]
