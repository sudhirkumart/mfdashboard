"""
CAS (Consolidated Account Statement) Parser
Parses CAMS/Karvy CAS PDF files and extracts mutual fund transaction data
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 not installed. PDF parsing will not be available.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CASParser:
    """Parser for Consolidated Account Statement (CAS) PDF files"""

    def __init__(self):
        """Initialize CAS parser"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 is required for CAS parsing. Install with: pip install PyPDF2")

        self.transactions = []
        self.folios = {}
        self.pan_data = {}

    def parse_pdf(self, pdf_path: str) -> Dict:
        """
        Parse CAS PDF file

        Args:
            pdf_path: Path to CAS PDF file

        Returns:
            Dictionary with parsed data
        """
        logger.info(f"Parsing CAS PDF: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                # Extract text from all pages
                for page in pdf_reader.pages:
                    text += page.extract_text()

            # Parse the extracted text
            parsed_data = self._parse_text(text)

            logger.info(f"Successfully parsed {len(parsed_data.get('transactions', []))} transactions")
            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise

    def _parse_text(self, text: str) -> Dict:
        """
        Parse extracted text from CAS

        Args:
            text: Extracted text from PDF

        Returns:
            Structured data dictionary
        """
        result = {
            'pan': None,
            'name': None,
            'email': None,
            'folios': {},
            'transactions': []
        }

        # Extract PAN
        pan_match = re.search(r'PAN\s*[:\-]?\s*([A-Z]{5}\d{4}[A-Z])', text, re.IGNORECASE)
        if pan_match:
            result['pan'] = pan_match.group(1)

        # Extract Name (usually after PAN)
        name_match = re.search(r'Name\s*[:\-]?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if name_match:
            result['name'] = name_match.group(1).strip()

        # Extract Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            result['email'] = email_match.group(0)

        # Parse transactions (simplified pattern)
        # This is a basic implementation - real CAS parsing is more complex
        transaction_patterns = [
            # Pattern for purchase/SIP
            r'(\d{2}-\w{3}-\d{4})\s+Purchase.*?(\d+\.\d+)\s+(\d+\.\d+)',
            # Pattern for redemption
            r'(\d{2}-\w{3}-\d{4})\s+Redemption.*?(\d+\.\d+)\s+(\d+\.\d+)',
        ]

        current_scheme = None
        current_folio = None

        lines = text.split('\n')

        for line in lines:
            # Detect scheme name
            if 'Folio No' in line or 'Folio:' in line:
                folio_match = re.search(r'(?:Folio\s*No\.?|Folio)\s*[:\-]?\s*(\w+/\d+)', line, re.IGNORECASE)
                if folio_match:
                    current_folio = folio_match.group(1)

            # Detect scheme name
            scheme_match = re.search(r'([A-Z][\w\s\-&]+(?:Fund|Plan|Scheme))', line)
            if scheme_match and len(scheme_match.group(1)) > 10:
                current_scheme = scheme_match.group(1).strip()

            # Parse transaction line
            for pattern in transaction_patterns:
                match = re.search(pattern, line)
                if match and current_scheme:
                    date_str = match.group(1)
                    units = float(match.group(2))
                    nav = float(match.group(3))

                    txn_type = 'purchase' if 'Purchase' in line or 'SIP' in line else 'redemption'

                    try:
                        txn_date = datetime.strptime(date_str, '%d-%b-%Y')

                        transaction = {
                            'date': txn_date.strftime('%Y-%m-%d'),
                            'scheme_name': current_scheme,
                            'folio': current_folio,
                            'type': txn_type,
                            'units': units if txn_type == 'purchase' else -units,
                            'nav': nav,
                            'amount': units * nav
                        }

                        result['transactions'].append(transaction)

                        # Group by folio
                        if current_folio:
                            if current_folio not in result['folios']:
                                result['folios'][current_folio] = {
                                    'scheme_name': current_scheme,
                                    'transactions': []
                                }
                            result['folios'][current_folio]['transactions'].append(transaction)

                    except ValueError:
                        logger.warning(f"Could not parse date: {date_str}")

        return result

    def parse_text_file(self, text_path: str) -> Dict:
        """
        Parse CAS from plain text file (for testing)

        Args:
            text_path: Path to text file

        Returns:
            Parsed data dictionary
        """
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return self._parse_text(text)

    def export_to_json(self, output_path: str, parsed_data: Dict) -> None:
        """
        Export parsed data to JSON

        Args:
            output_path: Output JSON file path
            parsed_data: Parsed CAS data
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2)

        logger.info(f"Exported parsed data to {output_path}")

    def convert_to_portfolio_format(self, parsed_data: Dict) -> Dict:
        """
        Convert parsed CAS data to portfolio JSON format

        Args:
            parsed_data: Parsed CAS data

        Returns:
            Portfolio format dictionary
        """
        portfolio = {
            'portfolio_name': f"Portfolio_{parsed_data.get('pan', 'unknown')}",
            'created_date': datetime.now().isoformat(),
            'accounts': {}
        }

        pan = parsed_data.get('pan')
        if not pan:
            logger.warning("No PAN found in CAS data")
            pan = 'UNKNOWN'

        # Create account structure
        portfolio['accounts'][pan] = {
            'name': parsed_data.get('name', 'Unknown'),
            'email': parsed_data.get('email', ''),
            'holdings': []
        }

        # Group transactions by scheme
        schemes = {}
        for txn in parsed_data.get('transactions', []):
            scheme_name = txn.get('scheme_name')
            if scheme_name not in schemes:
                schemes[scheme_name] = {
                    'scheme_name': scheme_name,
                    'folio': txn.get('folio'),
                    'transactions': []
                }

            schemes[scheme_name]['transactions'].append({
                'date': txn['date'],
                'units': abs(txn['units']),
                'nav': txn['nav'],
                'type': txn['type']
            })

        # Add holdings
        portfolio['accounts'][pan]['holdings'] = list(schemes.values())

        return portfolio


def parse_cas_file(pdf_path: str, output_json: Optional[str] = None) -> Dict:
    """
    Convenience function to parse CAS file

    Args:
        pdf_path: Path to CAS PDF file
        output_json: Optional output JSON path

    Returns:
        Parsed data dictionary
    """
    parser = CASParser()
    parsed_data = parser.parse_pdf(pdf_path)

    if output_json:
        parser.export_to_json(output_json, parsed_data)

    return parsed_data


if __name__ == "__main__":
    print("CAS Parser Module")
    print("=" * 50)

    if not PDF_AVAILABLE:
        print("\nWARNING: PyPDF2 not installed!")
        print("Install with: pip install PyPDF2")
        print("\nExample usage (when PyPDF2 is installed):")
    else:
        print("\nExample usage:")

    print("""
from backend.cas_parser import CASParser

# Initialize parser
parser = CASParser()

# Parse CAS PDF
parsed_data = parser.parse_pdf('path/to/cas_statement.pdf')

# Export to JSON
parser.export_to_json('data/cas_output.json', parsed_data)

# Convert to portfolio format
portfolio = parser.convert_to_portfolio_format(parsed_data)

# Access data
print(f"PAN: {parsed_data['pan']}")
print(f"Total Transactions: {len(parsed_data['transactions'])}")
print(f"Folios: {list(parsed_data['folios'].keys())}")
""")

    print("\nNote: CAS parsing is complex and depends on the format.")
    print("This implementation provides a basic framework that can be")
    print("extended based on specific CAS formats (CAMS/Karvy).")
