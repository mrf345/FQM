import os

from celery import Celery
from redis import Redis
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, ALL
from flask_googletrans import translator
from flask_gtts import gtts

from app.constants import MIGRATION_FOLDER


class LazyCelery:
    config = {
        'broker_url': os.environ.get('CELERY_BROKER_URL'),
        'result_backend': os.environ.get('CELERY_RESULT_BACKEND'),
    }

    def __init__(self, flask_app=None):
        self._flask_app = flask_app
        self._celery_app = None

    def init_app(self, flask_app=None):
        if flask_app:
            self._flask_app = flask_app

        # if self._celery_app:
        #     self._celery_app.main = flask_app.import_name

    def _create_app(self):
        self._celery_app = Celery('app.main')
        self._celery_app.conf.update(self.config)

        class ContextTask(self._celery_app.Task):
            def __call__(_, *args, **kwargs):
                if self._flask_app:
                    with self._flask_app.app_context():
                        return _.run(*args, **kwargs)

        self._celery_app.Task = ContextTask

    @property
    def app(self):
        if not self._celery_app:
            self._create_app()

        return self._celery_app


class DictCacheStore:
    def __init__(self, store_key, decode=True):
        self._store_key = store_key
        self._decode = decode

    def __getitem__(self, key):
        value = redis.get(f'{self._store_key}:{key}')

        if value is not None and self._decode:
            return value.decode('utf-8')

        return value

    def __setitem__(self, key, value):
        redis.set(f'{self._store_key}:{key}', value)

    def __delitem__(self, key):
        redis.delete(key)

    def __iter__(self):
        return map(
            lambda k: k.decode('utf-8'),
            redis.scan_iter(f'{self._store_key}:*'),
        )

    def get(self, key, rep=None):
        value = self[key]
        return rep if value is None else value


class RedisGtts(gtts):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._files = self.files

        if os.environ.get('DOCKER'):
            self._files = self.files = DictCacheStore('gTTS')

    def teardown(self):
        if os.environ.get('DOCKER'):
            self.files = {}
            for key in self._files:
                del self._files[key]
        else:
            super().teardown()

    def say(self, lang='en', text='Flask says Hi!'):
        if lang == 'en-us':
            lang = 'en'

        return super().say(lang, text)

    def _handle_exception(self, exception):
        raise exception


# NOTE: Work around for flask imports and registering blueprints
# currently needed for sql alchemy, login manager and flask-uploads

db = SQLAlchemy()
migrate = Migrate(directory=MIGRATION_FOLDER, compare_type=True)
login_manager = LoginManager()
login_manager.login_view = "login"
files = UploadSet('files', ALL)
gtranslator = translator(cache=True,
                         skip_app=True,
                         service_urls=['translate.googleapis.com'])
gTTs = RedisGtts(route=True, failsafe=True, logging=False)
celery_app = LazyCelery()
redis = Redis('redis', db=3)
