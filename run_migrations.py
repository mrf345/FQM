from flask_migrate import upgrade as database_upgrade

from app import app
from app.constants import MIGRATION_FOLDER
from app.utils import absolute_path, create_default_records


with app.app_context():
    database_upgrade(directory=absolute_path(MIGRATION_FOLDER))
    create_default_records()
