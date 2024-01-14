# dostana/celery.py
from celery import Celery

app = Celery('dostana', broker='pyamqp://guest:guest@localhost//')  # Update the broker URL accordingly

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
