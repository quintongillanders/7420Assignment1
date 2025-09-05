import os

if os.environ.get('VERCEL') != '1':
    from .celery import app as celery_app
    __all__ = ('celery_app',)