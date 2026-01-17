# AWS Free Tier - Quick Start Guide

**Estimated time: 20-30 minutes**

---

## Quick Steps

### 1. Launch EC2 Instance (5 minutes)

1. Go to AWS Console > EC2 > Launch Instance
2. Settings:
   - **Name:** investments-dashboard
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Type:** t2.micro (Free tier)
   - **Key pair:** Create new > Download .pem file
   - **Security Group:** Allow SSH (22), HTTP (80), HTTPS (443)
   - **Storage:** 8 GB
3. Click **Launch**

### 2. Connect to Instance (2 minutes)

**Easiest Method:**
1. Select instance > Click **Connect** button
2. Choose **EC2 Instance Connect** tab
3. Click **Connect**

**OR using SSH:**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 3. Upload Application (5 minutes)

**Method A - Using SCP (from your computer):**
```bash
# Create zip of application
cd C:\Users\Win-10\OneDrive\Documents\GitHub\mfdashboard
Compress-Archive -Path * -DestinationPath app.zip -Force

# Upload to EC2
scp -i your-key.pem app.zip ubuntu@YOUR_IP:/tmp/app.zip

# On EC2, extract:
mkdir -p /tmp/app
cd /tmp/app
sudo apt-get install -y unzip
unzip /tmp/app.zip
```

**Method B - Manual upload via AWS Console:**
1. Connect via EC2 Instance Connect
2. Use file upload button (top-right)
3. Upload files to /tmp/app

### 4. Deploy (10 minutes)

```bash
cd /tmp/app/deployment
chmod +x deploy_ec2.sh
sudo ./deploy_ec2.sh
```

Wait for script to complete. It will show your dashboard URL at the end.

### 5. Access Dashboard

Open browser: `http://YOUR_PUBLIC_IP`

**Done!** Your dashboard is live 24/7 on AWS Free Tier.

---

## Quick Commands

```bash
# Check if running
sudo systemctl status investments-dashboard

# Restart service
sudo systemctl restart investments-dashboard

# View logs
sudo journalctl -u investments-dashboard -f

# Backup data
sudo cp /home/mfdashboard/investments-dashboard/*.json ~/backup/
```

---

## Troubleshooting

**Can't access dashboard?**
1. Check Security Group allows port 80
2. Run: `sudo systemctl status investments-dashboard`
3. Run: `sudo systemctl status nginx`

**Service failed?**
1. View logs: `sudo journalctl -u investments-dashboard -n 50`
2. Check permissions: `ls -la /home/mfdashboard/investments-dashboard`

---

## What's Next?

- [ ] Set up automatic backups (see full guide)
- [ ] Add your own domain name (optional)
- [ ] Enable HTTPS with Let's Encrypt (optional)
- [ ] Set up monitoring/alerts (optional)

See **AWS_DEPLOYMENT_GUIDE.md** for detailed instructions on these topics.

---

## Free Tier Limits

✅ 750 hours/month of t2.micro (24/7 for 12 months)
✅ 30 GB storage
✅ 15 GB bandwidth out/month

**After 12 months:** ~$10-13/month

---

## Need Help?

1. Check full deployment guide: `AWS_DEPLOYMENT_GUIDE.md`
2. AWS Documentation: https://docs.aws.amazon.com/ec2/
3. Common issues covered in troubleshooting section
