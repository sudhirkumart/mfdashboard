#!/bin/bash

# Fix Permissions Script for Investments Dashboard
# Run this script on EC2 if you encounter permission errors

echo "Fixing permissions for Investments Dashboard..."

# Navigate to application directory
cd ~/mfdashboard || exit 1

# Create data/output directory if it doesn't exist
mkdir -p data/output

# Set proper permissions
chmod 755 data
chmod 755 data/output

# Make the current user owner of these directories
sudo chown -R ubuntu:ubuntu data/

# Set permissions for portfolio files
if [ -f "portfolio.json" ]; then
    chmod 644 portfolio.json
fi

if [ -f "stock_prices.json" ]; then
    chmod 644 stock_prices.json
fi

# Verify permissions
echo ""
echo "Current permissions:"
ls -la data/
ls -la data/output/

echo ""
echo "✓ Permissions fixed!"
echo "Now restart the application:"
echo "  sudo systemctl restart investments-dashboard"
