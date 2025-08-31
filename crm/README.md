# CRM Celery and Celery Beat Setup

### Installation

1. Install Redis:

sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis


2. Install requirements:

pip install -r requirements.txt


3. Run migrations:

python manage.py migrate

4. Start Celery worker:

celery -A crm worker -l info


5. Start Celery Beat scheduler:

celery -A crm beat -l info


6. Verify logs:

Check weekly reports in `/tmp/crm_report_log.txt`.
