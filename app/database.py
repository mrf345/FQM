# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, ALL
from flask_googletrans import translator

""" Work around for flask imports and registering blueprints
    currently needed for sql alchemy, login manager and flask-uploads"""

# current version
version = "0.4 beta"


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"
files = UploadSet('files', ALL)
gtranslator = translator(cache=True, skip_app=True, fail_safe=True)
