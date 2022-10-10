import sys
import click
from importlib import import_module

from app.main import bundle_app
from app.utils import get_accessible_ips, get_random_available_port, log_error
from app.constants import VERSION
from app.tasks import stop_tasks
from app.database import User


@click.command()
@click.option('--cli', is_flag=True, default=False, help='To use commandline interface instead of GUI.')
@click.option('--quiet', is_flag=True, default=False, help='To silence web server logs.')
@click.option('--reset', is_flag=True, default=False, help='Reset admin default password.')
@click.option('--ip', default=None, help='IP address to stream the service on.')
@click.option('--port', default=None, help='Port to stream the service through.')
def interface(cli, quiet, reset, ip, port):
    ''' FQM command-line interface (CLI):

    * if `--cli` is not used, initializing GUI will be attempted.\n
    * If no `ip` is passed it will default to `127.0.0.1`.\n
    * If no `port` is passed it will default to a random port.\n
    '''
    if reset:
        with bundle_app({'MIGRATION': True}).app_context():
            User.reset_default_password()
            click.echo('Admin password reset successfully')
        return

    app = bundle_app()

    def start_cli():
        alt_ip = ip or get_accessible_ips()[0][1]
        alt_port = port or get_random_available_port(alt_ip)
        app.config['LOCALADDR'] = alt_ip
        app.config['CLI_OR_DEPLOY'] = True
        app.config['QUIET'] = quiet
        app.config['SERVER_NAME'] = f'{alt_ip}:{alt_port}'

        click.echo(click.style(f'FQM {VERSION} is running on http://{alt_ip}:{alt_port}', bold=True, fg='green'))
        click.echo('')
        click.echo(click.style('Press Control-c to stop', blink=True, fg='black', bg='white'))

        try:
            from gevent import monkey, pywsgi
            monkey.patch_socket()
            pywsgi.WSGIServer((str(alt_ip), int(alt_port)),
                             app,
                             log=None if quiet else 'default').serve_forever()
        except KeyboardInterrupt:
            stop_tasks()

    if cli:
        start_cli()
    else:
        try:            
            app.config['CLI_OR_DEPLOY'] = False
            gui_process = import_module('PyQt5.QtWidgets').QApplication(sys.argv)
            window = import_module('app.gui').MainWindow(app)  # NOTE: has to be declared in a var to work properly

            import_module('PyQt5.QtCore').QCoreApplication.processEvents()
            gui_process.exec_()
        except Exception as e:
            if not quiet:
                print('Failed to start PyQt GUI, fallback to CLI.')
                log_error(e, quiet=quiet)

            start_cli()

    stop_tasks()
