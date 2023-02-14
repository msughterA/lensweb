# django_db_task/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lensweb.settings")

app = Celery("lensweb")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
