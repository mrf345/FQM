# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import click
from functools import reduce
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication
from gevent import monkey, pywsgi
from flask import Flask, request, Markup, session, redirect, url_for, flash
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_uploads import configure_uploads
from flask_login import current_user
from flask_qrcode import QRcode
from flask_datepicker import datepicker
from flask_colorpicker import colorpicker
from flask_fontpicker import fontpicker
from flask_less import lessc
from flask_minify import minify
from flask_gtts import gtts

from app.database import db, login_manager, files, version, gtranslator
from app.printer import listp
from app.administrate import administrate
from app.core import core
from app.customize import cust_app
from app.errorsh import errorsh_app
from app.manage import manage_app
from app.ex_functions import mse, r_path, get_accessible_ips, get_random_available_port
from app.data import Settings
from app.gui import MainWindow
from app.constants import SUPPORTED_LANGUAGES, SUPPORTED_MEDIA_FILES


def create_app():
    app = Flask(__name__, static_folder=r_path('static'), template_folder=r_path('templates'))
    PageDown(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + r_path(
        'data.sqlite')
    # Autoreload if templates change
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # flask_upload settings
    # app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # Remove Upload limit. FIX ISSUE
    app.config['UPLOADED_FILES_DEST'] = r_path('static/multimedia')
    app.config['UPLOADED_FILES_ALLOW'] = reduce(lambda sum, group: sum + group, SUPPORTED_MEDIA_FILES)
    app.config['SECRET_KEY'] = os.urandom(24)
    # Initiating extensions before registering blueprints
    Moment(app)
    QRcode(app)
    configure_uploads(app, files)
    login_manager.init_app(app)
    db.init_app(app)
    datepicker(app, local=['static/css/jquery-ui.min.css', 'static/jquery-ui.min.js'])
    colorpicker(app, local=['static/css/spectrum.css', 'static/spectrum.js'])
    fontpicker(app, local=['static/jquery-ui.min.js', 'static/css/jquery-ui.min.css', 'static/webfont.js',
                           'static/webfont.select.js', 'static/css/webfont.select.css'])
    lessc(app)
    minify(app, js=True, caching_limit=3, fail_safe=True,
           bypass=['/touch/<int:a>', '/serial/<int:t_id>', '/display'])
    gtts(app=app, route=True)
    gtranslator.init_app(app)
    # Register blueprints
    app.register_blueprint(administrate)
    app.register_blueprint(core)
    app.register_blueprint(cust_app)
    app.register_blueprint(errorsh_app)
    app.register_blueprint(manage_app)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    return app


def create_db(app):
    # Creating all non-existing tables
    with app.app_context():
        db.create_all()
        db.session.commit()
        mse()


def run_app():
    app = create_app()
    create_db(app)
    if os.name != 'nt':
        # !!! it did not work creates no back-end available error !!!
        # !!! strange bug , do not remove !!!
        if listp():
            pass

    # switching the language with template folder path
    @app.route('/lang_switch/<lang>')
    def lang_switch(lang):
        session['lang'] = lang
        if current_user.is_authenticated:
            return redirect(str(request.referrer))
        return redirect(url_for('core.root'))

    @app.before_first_request
    def default_language():
        if session.get('lang') not in list(SUPPORTED_LANGUAGES.keys()):
            session['lang'] = 'en'

    # Adding error handlers on main app instance
    @app.errorhandler(404)
    @app.errorhandler(500)
    @app.errorhandler(413)
    def page_not_found(error):
        if error == 413:
            flash('Error: file uploaded is too large ', 'danger')
            if current_user.is_authenticated:
                return redirect(url_for('cust_app.multimedia', nn=1))
            return redirect(url_for('core.root'))
        flash('Error: something wrong , or the page is non-existing', 'danger')
        return redirect(url_for('core.root'))

    # Injecting default variables to all templates
    @app.context_processor
    def inject_vars():
        # adding language support var
        ar = session.get('lang') == 'AR'
        # modifying side bar spacing for specific paths
        path = request.path
        admin_routes = ['/users', '/user_a', '/admin_u', '/user_u', '/csvd', '/settings']
        admin_route = any([path in admin_routes, path[:7] in admin_routes, path[:5] in admin_routes])

        return dict(path=path, notifications=Settings.query.first().notifications,
                    adme=admin_route, brp=Markup('<br>'), ar=ar, current_path=request.path,
                    version=version, str=str, defLang=session.get('lang'),
                    checkId=lambda id, records: id in [i.id for i in records])

    @click.command()
    @click.option('--cli', is_flag=True, default=False, help='To use commandline interface instead of GUI.')
    @click.option('--quiet', is_flag=True, default=False, help='To silence web server logs.')
    @click.option('--ip', default=None, help='IP address to stream the service on.')
    @click.option('--port', default=None, help='Port to stream the service through.')
    def interface(cli, quiet, ip, port):
        if cli:
            ip = ip or get_accessible_ips()[0][1]
            port = port or get_random_available_port(ip)
            app.config['LOCALADDR'] = ip

            click.echo(click.style(f'FQM {version} is running on http://{ip}:{port}', bold=True, fg='green'))
            click.echo('')
            click.echo(click.style('Press Control-c to stop', blink=True, fg='black', bg='white'))
            monkey.patch_socket()
            pywsgi.WSGIServer((str(ip), int(port)), app, log=None if quiet else 'default').serve_forever()
        else:
            gui_process = QApplication(sys.argv)
            window = MainWindow(app)  # NOTE: has to be decleared in a var to work properly
            QCoreApplication.processEvents()
            gui_process.exec_()

    interface()
