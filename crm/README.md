### CRM Celery and Cron Setup Guide

## Installation
Install Redis:

# bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
Install and activate Python virtual environment (optional but recommended):

# bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
Install Python dependencies:

# bash
pip install -r requirements.txt
Make sure your requirements.txt includes:
celery, django-celery-beat, requests, gql, redis, among others.

Database Migrations
Run database migrations including Celery Beat tables:

# bash
python manage.py migrate
python manage.py migrate django_celery_beat

## Celery Setup
Create crm/celery.py (if not already present):

# python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('crm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
Modify crm/__init__.py to ensure Celery starts with Django:

# python
from .celery import app as celery_app

__all__ = ('celery_app',)

Add Redis Broker Configuration to crm/settings.py:

# python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
Adjust localhost if running inside Docker.

## Running The Application
Start Django Development Server:

# bash
python manage.py runserver
Start Celery worker:

# bash
celery -A crm worker -l info
Start Celery Beat scheduler:

# bash
celery -A crm beat -l info

## Cron Jobs
Configure CRONJOBS in your settings.py for periodic cron tasks.

Example CRONJOBS syntax using django-cron or similar packages (adjust as needed).

## Logs
Cron heartbeat task logs to: /tmp/crm_heartbeat_log.txt

Low stock update task logs to: /tmp/low_stock_updates_log.txt

Weekly CRM reports logged in: /tmp/crm_report_log.txt

Check these logs for task execution details and troubleshooting.

## Additional Notes
Ensure 'django_celery_beat' is in your INSTALLED_APPS.

If import conflicts occur with crm/celery.py, consider renaming the file.

Monitor Celery with tools like Flower:

# bash
pip install flower
celery -A crm flower
then visit http://localhost:5555 to view task progress and details.

Use environment variables to configure Celery and Redis settings for different environments (development, production).