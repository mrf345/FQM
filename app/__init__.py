# -*- coding: utf-8 -*-
''' This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. '''

import sys
import click
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication
from gevent import monkey, pywsgi

from app.main import bundle_app
from app.gui import MainWindow
from app.utils import get_accessible_ips, get_random_available_port
from app.constants import VERSION


def run_app():
    ''' To run the app through a command-line interface. '''
    app = bundle_app()

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

            click.echo(click.style(f'FQM {VERSION} is running on http://{ip}:{port}', bold=True, fg='green'))
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
