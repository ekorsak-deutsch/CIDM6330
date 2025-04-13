import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forwarding_audit.settings')

# Create the Celery app
app = Celery('forwarding_audit')

# Load configuration from Django settings, using the key 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task for debugging purposes"""
    print(f'Request: {self.request!r}') 