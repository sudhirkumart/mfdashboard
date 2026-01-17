#!/bin/bash

###############################################################################
# AWS EC2 Deployment Script for Investments Dashboard
# This script sets up the application on Ubuntu EC2 instance (Free Tier)
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "  Investments Dashboard - AWS Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script should be run as root (use sudo)"
   exit 1
fi

print_status "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y

print_status "Step 2: Installing Python 3 and pip..."
apt-get install -y python3 python3-pip python3-venv git nginx

print_status "Step 3: Creating application user..."
# Create user if doesn't exist
if ! id -u mfdashboard > /dev/null 2>&1; then
    useradd -m -s /bin/bash mfdashboard
    print_status "User 'mfdashboard' created"
else
    print_status "User 'mfdashboard' already exists"
fi

print_status "Step 4: Setting up application directory..."
APP_DIR="/home/mfdashboard/investments-dashboard"

# Create directory if doesn't exist
mkdir -p $APP_DIR
cd $APP_DIR

print_status "Step 5: Copying application files..."
# This assumes you've already uploaded your files to /tmp/app
if [ -d "/tmp/app" ]; then
    cp -r /tmp/app/* $APP_DIR/
    print_status "Files copied from /tmp/app"
else
    print_warning "Upload your application files to /tmp/app first!"
    exit 1
fi

print_status "Step 6: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Step 7: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_status "Step 8: Creating data directories..."
mkdir -p data/output
mkdir -p logs

print_status "Step 9: Setting correct permissions..."
chown -R mfdashboard:mfdashboard $APP_DIR
chmod -R 755 $APP_DIR

print_status "Step 10: Creating systemd service..."
cat > /etc/systemd/system/investments-dashboard.service << 'EOF'
[Unit]
Description=Investments Dashboard Web Application
After=network.target

[Service]
Type=notify
User=mfdashboard
Group=mfdashboard
WorkingDirectory=/home/mfdashboard/investments-dashboard
Environment="PATH=/home/mfdashboard/investments-dashboard/venv/bin"
ExecStart=/home/mfdashboard/investments-dashboard/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /home/mfdashboard/investments-dashboard/logs/access.log \
    --error-logfile /home/mfdashboard/investments-dashboard/logs/error.log \
    web_app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Step 11: Configuring nginx..."
cat > /etc/nginx/sites-available/investments-dashboard << 'EOF'
server {
    listen 80;
    server_name _;  # Accept all domains (replace with your domain if you have one)

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if needed in future)
    location /static {
        alias /home/mfdashboard/investments-dashboard/static;
        expires 30d;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/investments-dashboard /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default nginx page

print_status "Step 12: Testing nginx configuration..."
nginx -t

print_status "Step 13: Starting services..."
systemctl daemon-reload
systemctl enable investments-dashboard
systemctl start investments-dashboard
systemctl restart nginx

print_status "Step 14: Checking service status..."
sleep 3
if systemctl is-active --quiet investments-dashboard; then
    print_status "Service is running!"
else
    print_warning "Service failed to start. Check logs:"
    echo "    sudo journalctl -u investments-dashboard -n 50"
    exit 1
fi

print_status "Step 15: Configuring firewall (UFW)..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp  # For future HTTPS setup
    ufw allow 22/tcp   # SSH
    print_status "Firewall rules added"
fi

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Your dashboard is now accessible at:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_PUBLIC_IP')"
echo ""
echo "Useful commands:"
echo "  Check status:    sudo systemctl status investments-dashboard"
echo "  View logs:       sudo journalctl -u investments-dashboard -f"
echo "  Restart:         sudo systemctl restart investments-dashboard"
echo "  Stop:            sudo systemctl stop investments-dashboard"
echo ""
print_warning "IMPORTANT: Configure AWS Security Group to allow HTTP (port 80)"
echo ""
