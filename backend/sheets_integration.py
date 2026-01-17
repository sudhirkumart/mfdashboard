"""
Google Sheets Integration
Fetches insights and tips from a public Google Spreadsheet
"""

import csv
import logging
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.error
from io import StringIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsReader:
    """
    Reads data from a public Google Spreadsheet using CSV export.
    No authentication required for publicly shared sheets.
    """

    def __init__(self, spreadsheet_id: str, gid: str = "0"):
        """
        Initialize Google Sheets reader.

        Args:
            spreadsheet_id: The Google Spreadsheet ID from the URL
            gid: The sheet GID (default "0" for first sheet)
        """
        self.spreadsheet_id = spreadsheet_id
        self.gid = gid
        # CSV export URL for public sheets
        self.csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"

    def fetch_sheet_data(self) -> Optional[str]:
        """
        Fetch CSV data from the Google Sheet.

        Returns:
            CSV data as string, or None if fetch fails
        """
        try:
            logger.info(f"Fetching data from Google Sheets: {self.spreadsheet_id}")

            # Create request with headers to mimic browser
            req = urllib.request.Request(
                self.csv_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            # Make request
            with urllib.request.urlopen(req, timeout=10) as response:
                # Read response
                csv_data = response.read().decode('utf-8')
                logger.info(f"Successfully fetched sheet data ({len(csv_data)} bytes)")
                return csv_data

        except urllib.error.URLError as e:
            logger.error(f"Network error fetching sheet: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching sheet data: {e}")
            return None

    def parse_csv_to_rows(self, csv_data: str) -> List[Dict[str, Any]]:
        """
        Parse CSV data into list of row dictionaries.

        Args:
            csv_data: CSV data as string

        Returns:
            List of dictionaries, each representing a row
        """
        try:
            if not csv_data:
                logger.warning("No CSV data to parse")
                return []

            # Parse CSV
            csv_file = StringIO(csv_data)
            reader = csv.DictReader(csv_file)

            rows = []
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                rows.append(dict(row))

            logger.info(f"Parsed {len(rows)} rows from CSV")
            return rows

        except Exception as e:
            logger.error(f"Error parsing CSV data: {e}")
            return []

    def get_insights(self) -> Dict[str, Any]:
        """
        Fetch and parse insights from the sheet.

        Returns:
            Dictionary with 'success' flag and 'data' containing parsed rows
        """
        csv_data = self.fetch_sheet_data()

        if not csv_data:
            return {
                'success': False,
                'error': 'Failed to fetch data from Google Sheets. Make sure the sheet is publicly accessible.',
                'data': []
            }

        rows = self.parse_csv_to_rows(csv_data)

        return {
            'success': True,
            'data': rows,
            'count': len(rows)
        }


def main():
    """Example usage"""
    print("Google Sheets Integration - Example Usage")
    print("=" * 60)

    # Example spreadsheet
    spreadsheet_id = "1Bih9HJltbVwKzhJr3MdkFUB-Hh261oTEFBjI5s7TlR4"
    gid = "756728702"

    reader = GoogleSheetsReader(spreadsheet_id, gid)
    result = reader.get_insights()

    if result['success']:
        print(f"\nSuccessfully fetched {result['count']} rows")
        print("\nFirst 3 rows:")
        for i, row in enumerate(result['data'][:3], 1):
            print(f"\n{i}. {row}")
    else:
        print(f"\nError: {result['error']}")


if __name__ == '__main__':
    main()
