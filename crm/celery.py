import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")

app = Celery("crm")

# Use Redis as broker
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in crm/tasks.py
app.autodiscover_tasks()
app.conf.broker_url = 'redis://localhost:6379/0'
