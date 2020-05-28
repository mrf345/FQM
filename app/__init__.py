# -*- coding: utf-8 -*-
''' This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. '''

import sys
import click
from importlib import import_module
from gevent import monkey, pywsgi

from app.main import bundle_app
from app.utils import get_accessible_ips, get_random_available_port
from app.constants import VERSION
from app.tasks import stop_tasks

# NOTE: uncomment out while genrating migration
# app = bundle_app({'MIGRATION': True})


def run_app():
    ''' To run the app through a command-line interface. '''
    @click.command()
    @click.option('--cli', is_flag=True, default=False, help='To use commandline interface instead of GUI.')
    @click.option('--quiet', is_flag=True, default=False, help='To silence web server logs.')
    @click.option('--ip', default=None, help='IP address to stream the service on.')
    @click.option('--port', default=None, help='Port to stream the service through.')
    def interface(cli, quiet, ip, port):
        app = bundle_app()

        def start_cli():
            alt_ip = ip or get_accessible_ips()[0][1]
            alt_port = port or get_random_available_port(alt_ip)
            app.config['LOCALADDR'] = alt_ip
            app.config['CLI_OR_DEPLOY'] = True

            click.echo(click.style(f'FQM {VERSION} is running on http://{alt_ip}:{alt_port}', bold=True, fg='green'))
            click.echo('')
            click.echo(click.style('Press Control-c to stop', blink=True, fg='black', bg='white'))
            monkey.patch_socket()

            try:
                pywsgi.WSGIServer((str(alt_ip), int(alt_port)), app, log=None if quiet else 'default').serve_forever()
            except KeyboardInterrupt:
                stop_tasks()

        if cli:
            start_cli()
        else:
            try:
                app.config['CLI_OR_DEPLOY'] = False
                gui_process = import_module('PyQt5.QtWidgets').QApplication(sys.argv)
                window = import_module('app.gui').MainWindow(app)  # NOTE: has to be decleared in a var to work properly

                import_module('PyQt5.QtCore').QCoreApplication.processEvents()
                gui_process.exec_()
            except Exception as e:
                print('Failed to start PyQt GUI, fallback to CLI.')
                print(e)
                start_cli()
    interface()
