import os

from .main import bundle_app
from .middleware import celery_app
from .tasks.celery import CeleryTasks


app_settings = {}
app = None
celery = None


if os.environ.get('MIGRATION'):
    app_settings['MIGRATION'] = True

if os.environ.get('DOCKER'):
    app_settings['CLI_OR_DEPLOY'] = True
    app_settings['GUNICORN'] = True

if app_settings:
    app = bundle_app(app_settings)
    celery_app.init_app(app)
    celery = celery_app.app
    CeleryTasks.register()
