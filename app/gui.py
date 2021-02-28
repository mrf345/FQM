import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QSize
from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QWidget, QToolTip, QDesktopWidget, QMessageBox, QComboBox, QLabel,
                             QHBoxLayout)
from PyQt5.QtGui import QFont, QIcon
from gevent import monkey, pywsgi
from gevent.event import Event as thevent

from app.utils import absolute_path, solve_path, get_accessible_ips, get_random_available_port, is_port_available
from app.middleware import gtranslator
from app.constants import SUPPORTED_LANGUAGES, VERSION
from app.tasks import stop_tasks
from app.database import User


class RunnerThread(QThread):
    """ PyQT thread to monitor the web server """
    def __init__(self, ip="127.0.0.1", port=8000, app=None):
        QThread.__init__(self)
        self.ip = ip
        self.port = port
        self.app = app

    def run(self):
        self.stopper = thevent()
        monkey.patch_socket()
        self.app.config['LOCALADDR'] = str(self.ip)
        self.server = pywsgi.WSGIServer((str(self.ip), int(self.port)), self.app, log=None)
        self.server.start()
        self.stopper.wait()

    def stop(self):
        self.stopper.set()
        self.server.stop()


class MainWindow(QWidget):
    def __init__(self, app=None):
        super(MainWindow, self).__init__()
        self.app = app
        global_layout = QVBoxLayout(self)
        icon_path = absolute_path(solve_path('static/images/favicon.png'))
        # NOTE: need to use objective message boxes instead of functions to set font
        self.font = QFont("static/gfonts/Amiri-Regular.ttf", 12, QFont.Bold)
        self.fonts = QFont("static/gfonts/Amiri-Regular.ttf", 10, QFont.Bold)
        # Language support variable
        self.current_language = 'en'
        self.currently_running = False
        icon = QIcon(icon_path)
        self.initiate(icon)
        self.set_center()
        self.set_languages_list(global_layout)
        self.set_about(icon_path, global_layout)
        self.set_ips_and_ports(global_layout)
        self.set_status(global_layout)
        self.set_start_and_stop(global_layout)
        self.setLayout(global_layout)
        selected_ip_and_port = self.select_ips_ports_change()
        self.Process = RunnerThread(selected_ip_and_port[1].split(',')[1], selected_ip_and_port[0], self.app)
        self.activateWindow()
        self.show()

    def initiate(self, icon):
        self.setWindowTitle('Free Queue Manager ' + VERSION)
        self.setGeometry(300, 300, 200, 150)
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.setMinimumHeight(400)
        self.setMaximumHeight(400)
        # Setting Icon
        self.setWindowIcon(icon)
        QToolTip.setFont(self.fonts)

    def set_status(self, global_layout):
        font = self.font
        self.status_icon = QIcon(absolute_path(solve_path('static/images/pause.png')))
        self.status_icon_container = QLabel('Icond', self)
        self.status_icon = self.status_icon.pixmap(70, 70, QIcon.Active, QIcon.On)
        self.status_icon_container.setPixmap(self.status_icon)
        self.status_icon_container.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.status_icon_container.setFont(font)
        self.status_label = QLabel('Texted', self)
        self.status_label.setText(self.get_translation('Server is <u> Not running </u> <br>'))
        self.status_label.setOpenExternalLinks(True)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.status_label.setFont(font)
        self.status_label.setToolTip(self.get_translation('Status of the server'))
        self.status_icon_container.setToolTip(self.get_translation('Status of the server'))
        global_layout.addStretch()
        global_layout.addWidget(self.status_icon_container)
        global_layout.addWidget(self.status_label)
        global_layout.addStretch()

    def set_languages_list(self, global_layout):
        self.languages = SUPPORTED_LANGUAGES
        self.languages_list = QComboBox()
        self.languages_list.addItems(list(self.languages.values()))
        self.languages_list.setCurrentIndex(0)
        self.languages_list.setToolTip(self.get_translation('Select language to change the interface to'))
        self.languages_list.currentIndexChanged.connect(self.handle_language_change)
        global_layout.addWidget(self.languages_list)

    def handle_language_change(self):
        self.current_language = list(self.languages.keys())[self.languages_list.currentIndex()]
        self.languages_list.setToolTip(self.get_translation(
            'Select language to change the interface to'))
        self.title = self.get_translation('About FQM')
        self.about_button.setToolTip(self.get_translation('About FQM'))
        self.start_button.setText(self.get_translation('Start'))
        self.start_button.setToolTip(self.get_translation('Start the server'))
        self.stop_button.setText(self.get_translation('Stop'))
        self.stop_button.setToolTip(self.get_translation('Stop the server'))
        self.reset_button.setText(self.get_translation('Reset admin password'))
        self.reset_button.setToolTip(self.get_translation('Reset admin password'))
        self.select_ip.setToolTip(self.get_translation(
            'Select network interface with IP, so the server runs on it'))
        self.select_port.setToolTip(self.get_translation(
            'Select a port, so the server runs through it'))
        self.status_label.setToolTip(self.get_translation('Status of the server'))
        self.status_icon_container.setToolTip(self.get_translation('Status of the server'))
        if self.currently_running:
            current = self.select_ips_ports_change()
            address = self.get_translation('Server is <u>Running</u> <br> On : ')
            address += u"<a href='http://"
            address += current[1].split(',')[1] + u":" + current[0]
            address += u"'> http://" + current[1].split(',')[1] + u":" + current[0]
            address += u"</a>"
            self.status_label.setText(address)
        else:
            self.status_label.setText(self.get_translation('Server is <u> Not running </u> <br>'))

    def get_translation(self, text):
        current_language = list(self.languages.keys())[self.languages_list.currentIndex()]
        return gtranslator.translate(text, dest=[current_language])

    def current_language(self):
        return list(self.languages.keys())[self.languages_list.currentIndex()]

    def set_ips_and_ports(self, global_layout):
        ips = [' ,'.join(ip_tuple) for ip_tuple in get_accessible_ips()]
        self.select_ip = QComboBox()
        self.select_ip.addItems(ips)
        self.select_ip.setToolTip(self.get_translation(
            'Select network interface with IP, so the server runs on it'))
        self.select_port = QComboBox()
        self.get_ports()
        self.select_port.setToolTip(self.get_translation(
            'Select a port, so the server runs through it'))
        self.select_ip.currentIndexChanged.connect(self.get_ports)
        global_layout.addWidget(self.select_ip)
        global_layout.addWidget(self.select_port)

    def get_ports(self):
        ip = self.select_ips_ports_change()[1].split(',')[1]
        default_ports = ['5000', '8080', '3000', '80', '9931']
        returned_ports = [port for port in default_ports if is_port_available(ip, port)]

        while 10 > len(returned_ports):
            returned_ports.append(get_random_available_port(ip))

        self.select_port.clear()
        self.select_port.addItems([str(port) for port in returned_ports])

    def select_ips_ports_change(self):
        return [self.select_port.currentText(), self.select_ip.currentText()]

    def set_start_and_stop(self, global_layout):
        grid = QVBoxLayout()
        row_1 = QHBoxLayout()
        row_2 = QHBoxLayout()
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setFont(self.fonts)
        self.start_button.setIcon(QIcon(absolute_path(solve_path('static/images/play.png'))))
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setIcon(QIcon(absolute_path(solve_path('static/images/pause.png'))))
        self.reset_button = QPushButton(self.get_translation('Reset admin password'))
        self.reset_button.clicked.connect(self.reset_admin_pass)
        self.start_button.setToolTip(self.get_translation('Start the server'))
        self.stop_button.setToolTip(self.get_translation('Stop the server'))
        self.stop_button.setEnabled(False)
        self.stop_button.setFont(self.fonts)
        row_1.addWidget(self.start_button)
        row_1.addWidget(self.stop_button)
        row_2.addWidget(self.reset_button)
        grid.addLayout(row_1)
        grid.addLayout(row_2)
        global_layout.addLayout(grid)

    def start_server(self):
        current = self.select_ips_ports_change()
        self.Process = RunnerThread(current[1].split(',')[1], current[0], self.app)
        self.Process.setTerminationEnabled(True)
        if not self.Process.isRunning():
            try:
                self.Processport = current[0]
                self.start_button.setEnabled(False)
                self.reset_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.select_ip.setEnabled(False)
                self.select_port.setEnabled(False)
                self.status_icon = QIcon(absolute_path(solve_path('static/images/play.png')))
                self.status_icon = self.status_icon.pixmap(70, 70, QIcon.Active, QIcon.On)
                self.status_icon_container.setPixmap(self.status_icon)
                current = self.select_ips_ports_change()
                address = self.get_translation('Server is <u>Running</u> <br> On : ')
                address += "<a href='http://"
                address += current[1].split(',')[1] + ":" + current[0]
                address += "'> http://" + current[1].split(',')[1] + ":" + current[0]
                address += "</a>"
                self.status_label.setText(address)
                self.status_label.setFont(self.font)
                self.Process.start()
                self.currently_running = True
            except Exception:
                self.before_exit()
        else:
            self.before_exit()

    def stop_server(self):
        if self.Process.isRunning():
            try:
                if self.Process.isRunning:
                    self.Process.stop()
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.reset_button.setEnabled(True)
                self.select_ip.setEnabled(True)
                self.select_port.setEnabled(True)
                self.status_label.setText(self.get_translation('Server is <u> Not running </u> <br>'))
                # removing the last used port to avoid termination error
                current_port_index = self.select_port.currentIndex()
                self.select_port.removeItem(current_port_index)
                self.get_ports()
                self.currently_running = False
            except Exception:
                self.before_exit()
        else:
            self.before_exit()

    def reset_admin_pass(self):
        with self.app.app_context():
            User.reset_default_password()

        QMessageBox.information(
            self,
            self.get_translation('Password reset'),
            self.get_translation('Admin password was reset successfully.'),
            QMessageBox.Ok)

    def set_about(self, icon, global_layout):
        def show_about():
            message = u" <center> "
            message += self.get_translation('All credit reserved to the author of FQM version ') + VERSION + u" "
            message += self.get_translation(', This work is a free, open-source project licensed ')
            message += self.get_translation(' under Mozilla Public License version 2.0 . <br><br>')
            message += self.get_translation(' visit us for more infos and how-tos :<br> ')
            message += u"<br> <b><a href='https://fqms.github.io/'>"
            message += u"https://fqms.github.io </a> </b></center>"
            title = self.get_translation('About FQM')
            return QMessageBox.about(self, title, message)
        self.about_button = QPushButton('', self)
        self.about_button.setIcon(QIcon(icon))
        self.about_button.setIconSize(QSize(150, 70))
        self.about_button.setToolTip(self.get_translation('About FQM'))
        self.about_button.clicked.connect(show_about)
        global_layout.addWidget(self.about_button)

    def closeEvent(self, event=None):  # NOTE: Factory method
        def exiting():
            stop_tasks()
            sys.exit(0)

        if self.currently_running:
            answer = self.exit_question(
                self.get_translation('Exiting while running'),
                self.get_translation('Are you really sure, you want to exit ?'))
            if answer:
                if event is not None:
                    event.accept()
                if self.Process.isRunning():
                    self.Process.stop()
                exiting()
            else:
                if event is not None:
                    event.ignore()
        else:
            if event is not None:
                event.accept()
            if self.Process.isRunning():
                self.Process.stop()
            exiting()

    def exit_question(self, title, msg):
        return QMessageBox.question(
            self, title, msg, QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes

    def before_exit(self):
        if self.Process.isRunning():
            self.Process.stop()
        message = u"<center>"
        message += self.get_translation(' Opps, a critical error has occurred, we will be ')
        message += self.get_translation(
            ' grateful if you can help fixing it, by reporting to us at : <br><br> ')
        message += u"<br><b><a href='https://fqms.github.io/'> "
        message += u"https://fqms.github.io </a></b> </center>"
        QMessageBox.critical(
            self,
            self.get_translation('Critical Error'),
            message,
            QMessageBox.Ok)

    def set_center(self):
        geometry = self.frameGeometry()
        centered = QDesktopWidget().availableGeometry().center()
        geometry.moveCenter(centered)
        self.move(geometry.topLeft())
