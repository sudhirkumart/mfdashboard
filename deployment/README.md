# Deployment Files

This folder contains everything needed to deploy your Investments Dashboard to AWS EC2 Free Tier.

---

## Files Overview

### 📘 Documentation
- **AWS_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
  - EC2 instance setup
  - Security configuration
  - Domain setup (optional)
  - SSL/HTTPS setup (optional)
  - Backup strategies
  - Troubleshooting

- **QUICK_START.md** - Simplified 20-minute deployment guide
  - Essential steps only
  - Quick reference commands

### 🔧 Configuration Files
- **deploy_ec2.sh** - Automated deployment script
  - Installs all dependencies
  - Sets up Python environment
  - Configures nginx & systemd
  - Starts all services

- **investments-dashboard.service** - Systemd service file
  - Auto-start on boot
  - Auto-restart on failure
  - Runs with dedicated user

- **nginx-config** - Nginx reverse proxy configuration
  - Routes port 80 to application
  - Handles static files
  - Configures timeouts & buffers

---

## Deployment Approach

```
┌─────────────────┐
│   Your Laptop   │
└────────┬────────┘
         │ 1. Upload files via SCP/Git
         ▼
┌─────────────────┐
│   EC2 Instance  │
│   (Ubuntu)      │
├─────────────────┤
│  2. Run deploy  │
│     script      │
└────────┬────────┘
         │ 3. Script installs:
         ├── Python 3 + pip
         ├── nginx
         ├── Gunicorn (WSGI server)
         └── Application dependencies
         │
         ▼
┌─────────────────┐
│   Gunicorn      │ Runs Flask app on port 5000
├─────────────────┤
│   Nginx         │ Reverse proxy on port 80
├─────────────────┤
│   Systemd       │ Manages service lifecycle
└─────────────────┘
         │
         ▼
    Accessible via
    http://YOUR_IP
```

---

## Quick Start

1. **Read** QUICK_START.md (20 minutes)
2. **Follow** the 5 simple steps
3. **Access** your dashboard at http://YOUR_IP

For detailed information, backup strategies, SSL setup, and troubleshooting, see **AWS_DEPLOYMENT_GUIDE.md**.

---

## Architecture

### Production Stack:
- **OS:** Ubuntu 22.04 LTS
- **Web Server:** Nginx (reverse proxy)
- **App Server:** Gunicorn (3 workers)
- **Framework:** Flask
- **Python:** 3.10+
- **Process Manager:** Systemd

### Why This Stack?
- ✅ Production-ready
- ✅ Auto-restart on failure
- ✅ Handles concurrent requests
- ✅ Scales easily (add more workers)
- ✅ Industry standard

---

## Security Features

✅ Application runs as non-root user (`mfdashboard`)
✅ Nginx handles all public traffic (not Flask directly)
✅ Firewall configuration included
✅ Process isolation via systemd
✅ Automatic service restart on crash
✅ Comprehensive logging

---

## Monitoring & Logs

### Service Status:
```bash
sudo systemctl status investments-dashboard
```

### Application Logs:
```bash
# Real-time logs
sudo journalctl -u investments-dashboard -f

# Last 50 lines
sudo journalctl -u investments-dashboard -n 50

# Access logs
tail -f /home/mfdashboard/investments-dashboard/logs/access.log

# Error logs
tail -f /home/mfdashboard/investments-dashboard/logs/error.log
```

---

## Maintenance Commands

### Restart Application:
```bash
sudo systemctl restart investments-dashboard
```

### Update Application:
```bash
cd /home/mfdashboard/investments-dashboard
git pull  # If using git
sudo systemctl restart investments-dashboard
```

### Backup Data:
```bash
sudo tar -czf ~/backup.tar.gz \
  /home/mfdashboard/investments-dashboard/portfolio.json \
  /home/mfdashboard/investments-dashboard/stock_prices.json
```

### Check Resource Usage:
```bash
# CPU & Memory
top

# Disk space
df -h

# Application memory
ps aux | grep gunicorn
```

---

## Free Tier Economics

### What's Free (12 months):
- ✅ 750 hours/month EC2 t2.micro
- ✅ 30 GB EBS storage
- ✅ 15 GB data transfer out
- ✅ 1 Million API requests (CloudWatch)

### After Free Tier:
- EC2 t2.micro: ~$8.50/month
- EBS 8GB: ~$0.80/month
- Data transfer: ~$1-2/month
- **Total: ~$10-12/month**

---

## Scaling Options

As your usage grows:

### Vertical Scaling (Better Performance):
```bash
# From AWS Console:
1. Stop instance
2. Change instance type to t3.small
3. Start instance
```

### Horizontal Scaling (More Reliability):
- Add Application Load Balancer
- Multiple EC2 instances
- Auto Scaling Group
- RDS for database

---

## Support

### Need Help?
1. Check **AWS_DEPLOYMENT_GUIDE.md** troubleshooting section
2. Review application logs
3. Check AWS documentation
4. Verify security group settings

### Common Issues:
- **Can't access:** Check security group port 80
- **Service down:** Check `systemctl status`
- **Out of memory:** Add swap space (guide included)
- **Permission errors:** Check file ownership

---

## File Permissions

After deployment, your files will have:

```
/home/mfdashboard/investments-dashboard/
├── web_app.py              (755)
├── portfolio.json          (644)
├── stock_prices.json       (644)
├── requirements.txt        (644)
├── venv/                   (755)
└── logs/                   (755)
```

All owned by `mfdashboard:mfdashboard`

---

## Next Steps After Deployment

1. ✅ Verify dashboard is accessible
2. ✅ Add your portfolio data
3. ✅ Set up automatic backups
4. ⬜ (Optional) Add custom domain
5. ⬜ (Optional) Enable HTTPS/SSL
6. ⬜ (Optional) Set up monitoring alerts
7. ⬜ (Optional) Add authentication

---

## Questions?

- 📖 Full Guide: AWS_DEPLOYMENT_GUIDE.md
- 🚀 Quick Deploy: QUICK_START.md
- 🔧 Troubleshooting: See full guide section
- 📊 Monitoring: CloudWatch metrics included

---

**Ready to deploy?** Start with `QUICK_START.md`!
