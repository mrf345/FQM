from IPython import embed

from app import app
from app.database import *
from app.tasks.celery import *
from app.middleware import *


with app.app_context():
    embed()
