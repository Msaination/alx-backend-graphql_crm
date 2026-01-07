# CRM Setup Guide

This document explains how to set up and run the CRM background tasks using **Redis**, **Celery**, and **Celery Beat**.

---

## 1. Install Redis and Dependencies

### macOS (Homebrew)
```bash
brew install redis
brew services start redis

# Debian/Ubuntu
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

#Verify Redis
redis-cli ping
 #Expected output
 PONG

 # Python Dependencies

# Add to requirements.txt:
celery
django-celery-beat
redis

#Bash
pip install -r requirements.txt

#Run migrations
python manage.py migrate

# Start Celery worker
celery -A crm worker -l info

#Start celery beat
celery -A crm beat -l info

#Verify Logs
/tmp/crm_report_log.txt (log path)

#check file
cat /tmp/crm_report_log.txt

#you should see this
2026-01-07 18:00:00 - Report: 25 customers, 120 orders, 54000.0 revenue


✅ Summary

    Redis provides the broker for Celery.

    Celery workers execute tasks.

    Celery Beat schedules tasks.

    Logs confirm CRM health and reporting.


