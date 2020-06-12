from unittest.mock import MagicMock
from click.testing import CliRunner

import app.cli
from app.cli import interface


def test_cli_start(monkeypatch):
    runner = CliRunner()
    port = '8888'
    ip = '0.0.0.0'
    mock_bundle_app = MagicMock()
    mock_pywsgi = MagicMock()
    mock_monkey = MagicMock()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'pywsgi', mock_pywsgi)
    monkeypatch.setattr(app.cli, 'monkey', mock_monkey)
    runner.invoke(interface, ['--cli', '--port', port, '--ip', ip, '--quiet'])

    mock_bundle_app().config['QUIET'] is True
    mock_bundle_app().config['CLI_OR_DEPLOY'] is True
    mock_bundle_app().config['LOCALADDR'] == ip
    mock_monkey.patch_socket.assert_called_once_with()
    mock_pywsgi.WSGIServer.assert_called_once_with((ip, int(port)), mock_bundle_app(), log=None)
    mock_pywsgi.WSGIServer().serve_forever.assert_called_once_with()


def test_gui_start(monkeypatch):
    runner = CliRunner()
    mock_bundle_app = MagicMock()
    mock_import = MagicMock()
    mock_sys = MagicMock()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'import_module', mock_import)
    monkeypatch.setattr(app.cli, 'sys', mock_sys)
    runner.invoke(interface, [])

    mock_bundle_app().config['CLI_OR_DEPLOY'] is False
    mock_import().QApplication.assert_called_once_with(mock_sys.argv)
    mock_import().MainWindow.assert_called_once_with(mock_bundle_app())
    mock_import().QCoreApplication.processEvents.assert_called_once_with()
    mock_import().QApplication().exec_.assert_called_once_with()


def test_gui_cli_fallback(monkeypatch):
    runner = CliRunner()
    mock_bundle_app = MagicMock()
    mock_sys = MagicMock()
    mock_pywsgi = MagicMock()
    mock_monkey = MagicMock()

    def mock_import():
        raise AttributeError()

    monkeypatch.setattr(app.cli, 'bundle_app', mock_bundle_app)
    monkeypatch.setattr(app.cli, 'import_module', mock_import)
    monkeypatch.setattr(app.cli, 'sys', mock_sys)
    monkeypatch.setattr(app.cli, 'pywsgi', mock_pywsgi)
    monkeypatch.setattr(app.cli, 'monkey', mock_monkey)
    runner.invoke(interface, [])

    mock_bundle_app().config['QUIET'] is True
    mock_bundle_app().config['CLI_OR_DEPLOY'] is True
    mock_pywsgi.WSGIServer().serve_forever.assert_called_once_with()
