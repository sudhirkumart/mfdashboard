# AWS EC2 Free Tier Deployment Guide

Complete guide to deploy your Investments Dashboard on AWS EC2 Free Tier.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Launch EC2 Instance](#step-1-launch-ec2-instance)
3. [Step 2: Connect to Your Instance](#step-2-connect-to-your-instance)
4. [Step 3: Upload Your Application](#step-3-upload-your-application)
5. [Step 4: Run Deployment Script](#step-4-run-deployment-script)
6. [Step 5: Access Your Dashboard](#step-5-access-your-dashboard)
7. [Backup & Maintenance](#backup--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### What You Need:
- AWS Account (with Free Tier eligible)
- Your application files (this folder)
- SSH client (Terminal on Mac/Linux, PuTTY on Windows, or AWS Session Manager)
- Basic command line knowledge

### AWS Free Tier Limits:
- **750 hours/month** of t2.micro instance (enough for 24/7 operation)
- **30 GB** of EBS storage
- **15 GB** of bandwidth out
- **Free for 12 months**

---

## Step 1: Launch EC2 Instance

### 1.1 Sign in to AWS Console
- Go to: https://console.aws.amazon.com/
- Navigate to **EC2** service

### 1.2 Launch Instance
Click **"Launch Instance"** and configure:

#### Instance Settings:
```
Name: investments-dashboard
Application and OS Images (AMI): Ubuntu Server 22.04 LTS (Free tier eligible)
Instance type: t2.micro (Free tier eligible)
```

#### Key Pair (for SSH access):
```
1. Click "Create new key pair"
2. Name: investments-dashboard-key
3. Key pair type: RSA
4. Private key format: .pem (Mac/Linux) or .ppk (Windows/PuTTY)
5. Download and SAVE this file securely!
```

#### Network Settings:
```
Create security group or use existing:
Name: investments-dashboard-sg

Inbound rules:
1. SSH (Port 22) - Source: My IP (your current IP)
2. HTTP (Port 80) - Source: 0.0.0.0/0 (anywhere)
3. HTTPS (Port 443) - Source: 0.0.0.0/0 (optional, for future SSL)
```

#### Storage:
```
Size: 8 GB (Free Tier includes up to 30 GB)
Volume type: General Purpose SSD (gp3)
```

#### Advanced Details (Optional):
Leave defaults

### 1.3 Launch Instance
- Review and click **"Launch Instance"**
- Wait 2-3 minutes for instance to start

### 1.4 Note Your Instance Details
```
Public IPv4 address: 3.xxx.xxx.xxx (example)
Public IPv4 DNS: ec2-3-xxx-xxx-xxx.compute-1.amazonaws.com
```

---

## Step 2: Connect to Your Instance

### Option A: Using AWS Console (Easiest)
1. Select your instance in EC2 console
2. Click **"Connect"** button
3. Choose **"EC2 Instance Connect"** tab
4. Click **"Connect"**
5. A browser terminal opens automatically!

### Option B: Using SSH (Mac/Linux/Windows)

#### Mac/Linux:
```bash
# Set correct permissions on key file
chmod 400 investments-dashboard-key.pem

# Connect to instance
ssh -i investments-dashboard-key.pem ubuntu@YOUR_PUBLIC_IP

# Example:
ssh -i investments-dashboard-key.pem ubuntu@3.xxx.xxx.xxx
```

#### Windows (using PowerShell):
```powershell
ssh -i investments-dashboard-key.pem ubuntu@YOUR_PUBLIC_IP
```

#### Windows (using PuTTY):
1. Open PuTTY
2. Host: ubuntu@YOUR_PUBLIC_IP
3. Port: 22
4. Connection > SSH > Auth: Browse to your .ppk key file
5. Click "Open"

### First Time Connection:
```
The authenticity of host '3.xxx.xxx.xxx' can't be established.
Are you sure you want to continue connecting (yes/no)? yes
```

Type `yes` and press Enter.

---

## Step 3: Upload Your Application

### Method 1: Using SCP (Recommended for small files)

#### On Your Local Computer:
```bash
# Navigate to your project folder
cd C:\Users\Win-10\OneDrive\Documents\GitHub\mfdashboard

# Create a zip of your application (excluding unnecessary files)
# Windows PowerShell:
Compress-Archive -Path * -DestinationPath mfdashboard.zip -Force

# Mac/Linux:
zip -r mfdashboard.zip . -x "*.git*" "*__pycache__*" "*.pyc" "venv/*"

# Upload to EC2
scp -i investments-dashboard-key.pem mfdashboard.zip ubuntu@YOUR_PUBLIC_IP:/tmp/app.zip
```

#### On Your EC2 Instance:
```bash
# Create directory and extract
mkdir -p /tmp/app
cd /tmp/app
sudo apt-get update
sudo apt-get install -y unzip
unzip /tmp/app.zip
```

### Method 2: Using Git (Recommended for version control)

#### On Your EC2 Instance:
```bash
# Install git
sudo apt-get update
sudo apt-get install -y git

# Clone from GitHub (if you have a repo)
cd /tmp
git clone https://github.com/YOUR_USERNAME/mfdashboard.git app

# OR upload manually first, then:
cd /tmp/app
```

### Method 3: Using AWS Console (For small files)
1. Select instance in EC2 console
2. Click **"Connect"** > **"EC2 Instance Connect"**
3. In terminal, create directory: `mkdir -p /tmp/app`
4. Use built-in file upload feature (top-right corner)
5. Upload files one by one or as zip

---

## Step 4: Run Deployment Script

### 4.1 Make Script Executable
```bash
cd /tmp/app/deployment
chmod +x deploy_ec2.sh
```

### 4.2 Run Deployment
```bash
sudo ./deploy_ec2.sh
```

The script will:
- Install Python, pip, nginx
- Create application user
- Set up virtual environment
- Install dependencies
- Configure systemd service
- Configure nginx reverse proxy
- Start all services

**This takes 5-10 minutes.**

### 4.3 Expected Output
```
==========================================
  Investments Dashboard - AWS Deployment
==========================================

[+] Step 1: Updating system packages...
[+] Step 2: Installing Python 3 and pip...
[+] Step 3: Creating application user...
...
[+] Step 15: Configuring firewall (UFW)...

==========================================
  Deployment Complete!
==========================================

Your dashboard is now accessible at:
  http://3.xxx.xxx.xxx

Useful commands:
  Check status:    sudo systemctl status investments-dashboard
  View logs:       sudo journalctl -u investments-dashboard -f
  Restart:         sudo systemctl restart investments-dashboard
  Stop:            sudo systemctl stop investments-dashboard
```

---

## Step 5: Access Your Dashboard

### 5.1 Get Your Public IP
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

Or check in AWS EC2 Console.

### 5.2 Open in Browser
```
http://YOUR_PUBLIC_IP

Example: http://3.xxx.xxx.xxx
```

### 5.3 Verify It's Working
You should see:
- "Investments Dashboard" title
- Portfolio tab
- All features working

---

## Backup & Maintenance

### Daily Automatic Backup Script

Create backup script:
```bash
sudo nano /home/mfdashboard/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/mfdashboard/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/mfdashboard/investments-dashboard"

mkdir -p $BACKUP_DIR

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz \
    $APP_DIR/portfolio.json \
    $APP_DIR/stock_prices.json \
    $APP_DIR/stock_insights.json 2>/dev/null

# Keep only last 7 days
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable:
```bash
sudo chmod +x /home/mfdashboard/backup.sh
sudo chown mfdashboard:mfdashboard /home/mfdashboard/backup.sh
```

Schedule with cron:
```bash
sudo crontab -u mfdashboard -e

# Add this line (runs daily at 2 AM):
0 2 * * * /home/mfdashboard/backup.sh >> /home/mfdashboard/backup.log 2>&1
```

### Download Backups to Local
```bash
# On your local computer:
scp -i investments-dashboard-key.pem ubuntu@YOUR_PUBLIC_IP:/home/mfdashboard/backups/data_*.tar.gz ./
```

### Update Application
```bash
# SSH to server
ssh -i investments-dashboard-key.pem ubuntu@YOUR_PUBLIC_IP

# Switch to app directory
cd /home/mfdashboard/investments-dashboard

# Activate virtual environment
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Or upload new files and copy them

# Restart service
sudo systemctl restart investments-dashboard
```

---

## Troubleshooting

### Service Not Starting

Check logs:
```bash
sudo journalctl -u investments-dashboard -n 50 --no-pager
```

Check status:
```bash
sudo systemctl status investments-dashboard
```

### Can't Access Dashboard

1. **Check Security Group:**
   - AWS Console > EC2 > Security Groups
   - Ensure port 80 is open (0.0.0.0/0)

2. **Check nginx:**
   ```bash
   sudo systemctl status nginx
   sudo nginx -t  # Test configuration
   ```

3. **Check application:**
   ```bash
   sudo systemctl status investments-dashboard
   ```

4. **Test locally on server:**
   ```bash
   curl http://localhost:5000
   curl http://localhost
   ```

### Permission Errors

Fix permissions:
```bash
sudo chown -R mfdashboard:mfdashboard /home/mfdashboard/investments-dashboard
sudo chmod -R 755 /home/mfdashboard/investments-dashboard
```

### Out of Memory

Check memory:
```bash
free -h
```

Add swap space (if needed):
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### View Application Logs

Real-time logs:
```bash
sudo journalctl -u investments-dashboard -f
```

Access logs:
```bash
tail -f /home/mfdashboard/investments-dashboard/logs/access.log
```

Error logs:
```bash
tail -f /home/mfdashboard/investments-dashboard/logs/error.log
```

---

## Cost Optimization

### Free Tier Tips:

1. **Use t2.micro only** (750 hours/month free)
2. **Stop instance when not needed:**
   ```bash
   # From AWS Console or CLI
   aws ec2 stop-instances --instance-ids i-xxxxx
   ```
   - Stopped instances don't count towards 750 hours
   - EBS storage still charges (but very minimal)

3. **Monitor usage:**
   - AWS Billing Dashboard
   - Set up billing alerts

4. **Delete snapshots/AMIs** you don't need

5. **Use CloudWatch Free Tier:**
   - 10 metrics
   - 10 alarms
   - 1 million API requests

### After Free Tier (Month 13+):

Expected costs:
- t2.micro: ~$8-10/month
- EBS 8GB: ~$0.80/month
- Data transfer: ~$1-2/month (normal usage)

**Total: ~$10-13/month**

To reduce:
- Use t3.micro (~$7.5/month, better than t2.micro)
- Or upgrade to t3.small (~$15/month) for better performance

---

## Setting Up a Domain (Optional)

### Using Route 53 (AWS):
1. Register domain (~$12/year for .com)
2. Create hosted zone
3. Add A record pointing to EC2 IP

### Using External Domain:
1. Buy domain (Namecheap, GoDaddy, etc.)
2. Add A record: `@ -> YOUR_EC2_IP`
3. Wait for DNS propagation (5-60 minutes)

### Update Nginx Config:
```bash
sudo nano /etc/nginx/sites-available/investments-dashboard

# Change:
server_name _;

# To:
server_name yourdomain.com www.yourdomain.com;

# Restart nginx
sudo systemctl restart nginx
```

---

## Adding HTTPS/SSL (Optional but Recommended)

### Using Let's Encrypt (Free SSL):

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# 1. Enter email
# 2. Agree to terms
# 3. Choose redirect option (recommended: 2)

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

Now access via: `https://yourdomain.com`

---

## Security Best Practices

### 1. Change SSH Port (Optional)
```bash
sudo nano /etc/ssh/sshd_config
# Change: Port 22 -> Port 2222
sudo systemctl restart sshd

# Update Security Group to allow port 2222
```

### 2. Disable Root Login
```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 3. Enable UFW Firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Regular Updates
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 5. Add Authentication (Future Enhancement)
Consider adding login to your dashboard:
- Flask-Login
- OAuth (Google/GitHub)
- Basic HTTP auth via nginx

---

## Monitoring Setup

### CloudWatch Monitoring:

1. AWS Console > CloudWatch
2. Enable detailed monitoring (optional)
3. Create alarms:
   - CPU > 80%
   - Disk usage > 80%
   - Network errors

### Simple Uptime Monitoring:

Free services:
- UptimeRobot (https://uptimerobot.com)
- Pingdom (https://www.pingdom.com)

---

## Need Help?

### Useful Commands Reference:

```bash
# Service management
sudo systemctl status investments-dashboard
sudo systemctl start investments-dashboard
sudo systemctl stop investments-dashboard
sudo systemctl restart investments-dashboard
sudo systemctl enable investments-dashboard

# View logs
sudo journalctl -u investments-dashboard -f
tail -f /home/mfdashboard/investments-dashboard/logs/error.log

# Check processes
ps aux | grep gunicorn
netstat -tulpn | grep :5000

# Disk usage
df -h
du -sh /home/mfdashboard/investments-dashboard/*

# Memory usage
free -h

# Test nginx config
sudo nginx -t
sudo systemctl restart nginx

# Check open ports
sudo netstat -tulpn | grep LISTEN
```

---

## Success Checklist

- [ ] EC2 instance launched (t2.micro, Ubuntu 22.04)
- [ ] Security group allows HTTP (port 80)
- [ ] SSH key saved securely
- [ ] Application files uploaded to /tmp/app
- [ ] Deployment script executed successfully
- [ ] Service is running: `sudo systemctl status investments-dashboard`
- [ ] Dashboard accessible at http://YOUR_IP
- [ ] Portfolio data loads correctly
- [ ] Can add transactions
- [ ] Stock prices tab works
- [ ] Insights tab displays data from Google Sheets
- [ ] Backup script configured
- [ ] (Optional) Domain configured
- [ ] (Optional) SSL/HTTPS enabled

---

## Congratulations!

Your Investments Dashboard is now running 24/7 on AWS Free Tier!

Access it anytime at: **http://YOUR_PUBLIC_IP**

Questions? Check the troubleshooting section or AWS documentation.
