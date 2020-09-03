from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, ALL
from flask_googletrans import translator
from flask_gtts import gtts

from app.constants import MIGRATION_FOLDER

# NOTE: Work around for flask imports and registering blueprints
# currently needed for sql alchemy, login manager and flask-uploads

db = SQLAlchemy()
migrate = Migrate(directory=MIGRATION_FOLDER, compare_type=True)
login_manager = LoginManager()
login_manager.login_view = "login"
files = UploadSet('files', ALL)
gtranslator = translator(cache=True, skip_app=True, fail_safe=True)
gTTs = gtts(route=True, failsafe=True, logging=False)
