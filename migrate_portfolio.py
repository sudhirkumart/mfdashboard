"""
Portfolio Migration Script
Adds new fields (asset_type, exchange, notes) to existing portfolio transactions.
Safe to run multiple times - idempotent operation.
"""

import json
from pathlib import Path
from datetime import datetime


def migrate_portfolio(portfolio_file='portfolio.json'):
    """
    Migrate existing portfolio to new schema with stock support.

    Args:
        portfolio_file: Path to portfolio JSON file

    Returns:
        bool: True if migration was successful or not needed
    """
    portfolio_path = Path(portfolio_file)

    if not portfolio_path.exists():
        print(f"Portfolio file '{portfolio_file}' not found. No migration needed.")
        return True

    print(f"Migrating portfolio: {portfolio_file}")
    print("-" * 60)

    # Load existing portfolio
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading portfolio file: {e}")
        return False

    # Check if migration is needed
    transactions = data.get('transactions', [])
    if not transactions:
        print("No transactions found. Portfolio is empty.")
        return True

    # Check if already migrated
    needs_migration = False
    for txn in transactions:
        if 'asset_type' not in txn or 'exchange' not in txn or 'notes' not in txn:
            needs_migration = True
            break

    if not needs_migration:
        print("Portfolio already migrated. No changes needed.")
        return True

    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = portfolio_path.with_suffix(f'.backup_{timestamp}.json')

    try:
        import shutil
        shutil.copy2(portfolio_path, backup_file)
        print(f"[OK] Backup created: {backup_file}")
    except IOError as e:
        print(f"[FAIL] Failed to create backup: {e}")
        return False

    # Migrate transactions
    migrated_count = 0
    for txn in transactions:
        changed = False

        if 'asset_type' not in txn:
            txn['asset_type'] = 'MUTUAL_FUND'
            changed = True

        if 'exchange' not in txn:
            txn['exchange'] = ''
            changed = True

        if 'notes' not in txn:
            txn['notes'] = ''
            changed = True

        if changed:
            migrated_count += 1

    # Save migrated portfolio
    try:
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Migrated {migrated_count} transaction(s)")
        print(f"[OK] Portfolio saved: {portfolio_file}")
        print()
        print("Migration completed successfully!")
        return True
    except IOError as e:
        print(f"[FAIL] Failed to save migrated portfolio: {e}")
        print(f"Your original portfolio is backed up at: {backup_file}")
        return False


def verify_migration(portfolio_file='portfolio.json'):
    """
    Verify that the migration was successful.

    Args:
        portfolio_file: Path to portfolio JSON file

    Returns:
        bool: True if portfolio is properly migrated
    """
    portfolio_path = Path(portfolio_file)

    if not portfolio_path.exists():
        return True  # No file to verify

    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False

    transactions = data.get('transactions', [])

    for txn in transactions:
        if 'asset_type' not in txn:
            return False
        if 'exchange' not in txn:
            return False
        if 'notes' not in txn:
            return False

    return True


def main():
    """Main entry point for migration script"""
    print()
    print("=" * 60)
    print("  Portfolio Migration Tool")
    print("  Adding Stock Support to Mutual Fund Portfolio")
    print("=" * 60)
    print()

    # Migrate default portfolio
    success = migrate_portfolio('portfolio.json')

    # Verify migration
    if success:
        print()
        print("Verifying migration...")
        if verify_migration('portfolio.json'):
            print("[OK] Verification successful!")
        else:
            print("[FAIL] Verification failed. Please check the portfolio file.")

    print()
    print("=" * 60)
    print()

    # Offer to migrate other portfolio files
    print("To migrate other portfolio files, run:")
    print("  python migrate_portfolio.py")
    print()
    print("Or use in Python:")
    print("  from migrate_portfolio import migrate_portfolio")
    print("  migrate_portfolio('path/to/your/portfolio.json')")
    print()


if __name__ == '__main__':
    main()
