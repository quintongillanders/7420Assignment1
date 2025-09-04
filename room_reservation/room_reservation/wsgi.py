"""
WSGI config for room_reservation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'room_reservation.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    logging.error(f"WSGI application failed to load: {e}")
    sys.stderr.write(f"WSGI application failed to load: {e}\n")
    raise
