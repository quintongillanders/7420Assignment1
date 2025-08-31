import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_reservation.settings')
app = Celery('room_reservation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()