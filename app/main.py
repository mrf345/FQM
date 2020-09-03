import os
from functools import reduce
from urllib.parse import quote
from flask import Flask, request, Markup, session, redirect, url_for, flash, render_template
from flask_migrate import upgrade as database_upgrade
from flask_moment import Moment
from flask_uploads import configure_uploads
from flask_login import current_user
from flask_qrcode import QRcode
from flask_datepicker import datepicker
from flask_colorpicker import colorpicker
from flask_fontpicker import fontpicker
from flask_minify import minify
from sqlalchemy.exc import OperationalError

from app.middleware import db, login_manager, files, gtranslator, gTTs, migrate
from app.printer import get_printers_usb
from app.views.administrate import administrate
from app.views.core import core
from app.views.customize import cust_app
from app.views.manage import manage_app
from app.utils import absolute_path, log_error, create_default_records
from app.database import Settings, Serial, Office
from app.tasks import start_tasks
from app.constants import (SUPPORTED_LANGUAGES, SUPPORTED_MEDIA_FILES, VERSION, MIGRATION_FOLDER,
                           DATABASE_FILE, SECRET_KEY)


def create_app(config={}):
    ''' Create the flask app and setup extensions and blueprints.

    Returns
    -------
        app: Flask app
            app with settings and blueprints loadeds.
    '''
    app = Flask(__name__, static_folder=absolute_path('static'), template_folder=absolute_path('templates'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{absolute_path(DATABASE_FILE)}?check_same_thread=False'
    app.config['DB_NAME'] = DATABASE_FILE
    # Autoreload if templates change
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # flask_upload settings
    # app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # Remove Upload limit. FIX ISSUE
    app.config['UPLOADED_FILES_DEST'] = absolute_path('static/multimedia')
    app.config['UPLOADED_FILES_ALLOW'] = reduce(lambda sum, group: sum + group, SUPPORTED_MEDIA_FILES)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config.update(config)

    # Initiating extensions before registering blueprints
    Moment(app)
    QRcode(app)
    configure_uploads(app, files)
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    datepicker(app, local=['static/css/jquery-ui.min.css', 'static/jquery-ui.min.js'])
    colorpicker(app, local=['static/css/spectrum.css', 'static/spectrum.min.js'])
    fontpicker(app, local=['static/jquery-ui.min.js', 'static/css/jquery-ui.min.css', 'static/webfont.min.js',
                           'static/webfont.select.min.js', 'static/css/webfont.select.css'])
    gTTs.init_app(app)
    gtranslator.init_app(app)

    if app.config.get('GUNICORN', False):
        gtranslator.readonly = True
    else:
        minify(app, js=True, cssless=True, caching_limit=3, fail_safe=True, bypass=['.min.*'])

    # Register blueprints
    app.register_blueprint(administrate)
    app.register_blueprint(core)
    app.register_blueprint(cust_app)
    app.register_blueprint(manage_app)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    return app


def create_db(app, testing=False):
    ''' Creating all non-existing tables and load initial data.

    Parameters
    ----------
        app: Flask app
            app to use its context to create tables and load initial data.
        testing: bool
            flag to disable migrations, mainly used during integration testing.
    '''
    with app.app_context():
        if not os.path.isfile(absolute_path(app.config.get('DB_NAME'))):
            db.create_all()
        else:
            try:
                database_upgrade(directory=absolute_path(MIGRATION_FOLDER))
            except Exception as exception:
                if not isinstance(exception, OperationalError):
                    log_error(exception, quiet=os.name == 'nt')
        create_default_records()


def bundle_app(config={}):
    ''' Create a Flask app, set settings, load extensions, blueprints and create database. '''
    app = create_app(config)

    # NOTE: avoid creating or interacting with the database during migration
    if not app.config.get('MIGRATION', False):
        create_db(app)

        if not app.config.get('GUNICORN', False):
            # FIXME: Tasks are disabled when `GUNICORN` is running. We should implement a new
            # tasks module with celery that works seemlessly alongside gunicorn.
            start_tasks(app)

    if os.name != 'nt':
        # !!! it did not work creates no back-end available error !!!
        # !!! strange bug , do not remove !!!
        if get_printers_usb():
            pass

    @app.route('/language_switch/<language>')
    def language_switch(language):
        ''' Endpoint to switch the default language.

        Parameters
        ----------
            language: str
                language short form to switch to.
        '''
        session['lang'] = language

        if current_user.is_authenticated:
            return redirect(str(request.referrer))

        return redirect(url_for('core.root'))

    @app.before_first_request
    def default_language():
        ''' Set the default language before the first request. '''
        if session.get('lang') not in list(SUPPORTED_LANGUAGES.keys()):
            session['lang'] = 'en'

    @app.errorhandler(404)
    @app.errorhandler(500)
    @app.errorhandler(413)
    def page_not_found(error):
        ''' Adding error handlers on main app instance. '''
        if getattr(error, 'code', None) == 413:
            flash('Error: file uploaded is too large ', 'danger')
            if current_user.is_authenticated:
                return redirect(url_for('cust_app.multimedia', nn=1))
            return redirect(url_for('core.root'))

        getattr(error, 'code', None) != 404 and log_error(error)
        flash('Error: something wrong , or the page is non-existing', 'danger')
        return redirect(url_for('core.root'))

    @app.route('/nojs/<int:enabled_js>')
    def nojs(enabled_js):
        ''' Handle JavaScript disabled or not supported. '''
        if enabled_js == 1:
            next_url = session.get('next_url', '/')

            if next_url != '/':
                return redirect(next_url)

            return redirect(url_for('core.root'))
        return render_template('nojs.html', page_title='Javascript is disabled')

    def moment_wrapper(moment):
        ''' Temproray moment wrapper to add `.toTime()` and `.toNow()`
            TODO: Remove and update Flask-Moment when PR's mereged.
        '''
        def toTime(*args, **kwargs):
            content = str(moment.fromTime(*args, **kwargs))

            return Markup(content.replace('from(', 'to('))

        def toNow(*args, **kwargs):
            content = str(moment.fromNow(*args, **kwargs))

            return Markup(content.replace('fromNow(', 'toNow('))

        setattr(moment, 'toTime', toTime)
        setattr(moment, 'toNow', toNow)
        return moment

    @app.context_processor
    def inject_vars():
        ''' Injecting default variables to all templates. '''
        ar = session.get('lang') == 'AR'  # adding language support var

        # modifying side bar spacing for specific paths
        path = request.path
        admin_routes = ['/users', '/user_a', '/admin_u', '/user_u', '/csv', '/settings']
        admin_route = any([path in admin_routes, path[:7] in admin_routes, path[:5] in admin_routes])

        return dict(path=path, adme=admin_route, brp=Markup('<br>'), ar=ar, version=VERSION, str=str,
                    defLang=session.get('lang'), getattr=getattr, settings=Settings.get(), Serial=Serial,
                    checkId=lambda id, records: id in [i.id for i in records], offices=Office.query.all(),
                    moment_wrapper=moment_wrapper, current_path=quote(request.path, safe=''),
                    windows=os.name == 'nt', unix=os.name != 'nt', next=next, it=iter,
                    setattr=lambda *args, **kwargs: setattr(*args, **kwargs) or '')

    return app
