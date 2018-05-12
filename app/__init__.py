# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import Flask, request, Markup, session, redirect, url_for, flash
from flask_pagedown import PageDown
from flask_moment import Moment
import os
from gevent.event import Event as thevent
from gevent import monkey, pywsgi
import sys
from time import sleep
from netifaces import interfaces, ifaddresses
from random import randint
from PySide.QtGui import QWidget, QApplication, QIcon, QLabel
from PySide.QtGui import QFont, QToolTip, QPushButton, QMessageBox
from PySide.QtGui import QDesktopWidget, QPixmap
from PySide.QtGui import QComboBox, QVBoxLayout, QHBoxLayout, QFontDatabase
from PySide.QtCore import QCoreApplication, QSize, Qt, QThread, SIGNAL
from socket import socket, AF_INET, SOCK_STREAM
from administrate import administrate
from core import core
from customize import cust_app, mdal
from errorsh import errorsh_app
from manage import manage_app
from ex_functions import mse, check_ping, r_path, get_lang
from database import db, login_manager, files, version
from flask_uploads import configure_uploads
from flask_login import login_required, current_user
from jinja2 import FileSystemLoader
from flask_qrcode import QRcode
from functools import partial
from printer import listp
from flask_datepicker import datepicker
from flask_colorpicker import colorpicker
from flask_fontpicker import fontpicker
from languages import GUI as LANGUAGES


def create_app():
    app = Flask(__name__, static_folder=r_path('static'),
                template_folder=r_path('templates'))
    if getattr(sys, 'frozen', False):
        basedir = os.path.dirname(sys.executable)
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
    # bootstrap = Bootstrap(app)
    pagedown = PageDown(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + r_path(
        'data.sqlite')
    # Autoreload if templates change
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # flask_upload settings
    # app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # Remove Upload limit. FIX ISSUE
    app.config['UPLOADED_FILES_DEST'] = r_path('static/multimedia')
    app.config['UPLOADED_FILES_ALLOW'] = mdal
    app.config['SECRET_KEY'] = os.urandom(24)
    # Intiating extensions before registering blueprints
    moment = Moment(app)
    qrc = QRcode(app)
    configure_uploads(app, files)
    login_manager.init_app(app)
    db.init_app(app)
    datepicker(app, local=['static/css/jquery-ui.min.css', 'static/jquery-ui.min.js'])
    colorpicker(app, local=['static/css/spectrum.css', 'static/spectrum.js'])
    fontpicker(app, local=[
        'static/jquery-ui.min.js',
        'static/css/jquery-ui.min.css',
        'static/webfont.js',
        'static/webfont.select.js',
        'static/css/webfont.select.css'
    ])
    # Register blueprints
    app.register_blueprint(administrate)
    app.register_blueprint(core)
    app.register_blueprint(cust_app)
    app.register_blueprint(errorsh_app)
    app.register_blueprint(manage_app)
    return app


def create_db(app):
    # Creating all non-existing tables
    with app.app_context():
        db.create_all()
        db.session.commit()
        mse()


class rwser(QThread):
    """ pyside thread to monitor the web server """
    def __init__(self, ip="127.0.0.1", port=8000, app=None):
        QThread.__init__(self)
        self.ip = ip
        self.port = port
        self.app = app

    def run(self):
        self.stopper = thevent()
        monkey.patch_all()
        self.serv = pywsgi.WSGIServer(
            (str(self.ip),
             int(self.port)),
            self.app,
            log=None)
        try:  # gevent server known to have isuues on stopping
            self.serv.start()
            self.stopper.wait()
        except:
            print 'Error STA webserver : please, help us improve by reporting'
            print "to us on : \n\thttps://fqms.github.io/"
            sys.exit(0)

    def stop(self):
        try:
            self.stopper.set()
            self.serv.stop()
        except:
            print 'Error STD webserver : please, help us improve by reporting'
            print "to us on : \n\thttps://fqms.github.io/"
            sys.exit(0)


# Gui Class

class NewWindow(QWidget):
    def __init__(self, app=None):
        super(NewWindow, self).__init__()
        self.app = app
        glo = QVBoxLayout(self)
        if os.name == 'nt':
            icp = r_path('static\\images\\favicon.png')
        else:
            icp = r_path('static/images/favicon.png')
        # need to used objective message boxs instead of functions to set font
        self.Arial = QFont("", 15, QFont.Bold)
        self.Arials = QFont("", 10, QFont.Bold)
        # Language support variable 
        self.Language = 'en'
        self.Runningo = False
        icon = QIcon(icp)
        self.SelfIinit(icon)
        self.center()
        self.langsList(glo)
        self.set_Abutton(icp, glo)
        self.Lists(glo)
        self.Flabel(glo)
        self.set_button(glo)
        self.setLayout(glo)
        mip = self.slchange()
        self.P = rwser(mip[1].split(',')[1], mip[0], self.app)
        self.activateWindow()
        self.show()

    def SelfIinit(self, icon):
        self.setWindowTitle('Free Queue Manager ' + version)
        self.setGeometry(300, 300, 200, 150)
        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.setMinimumHeight(400)
        self.setMaximumHeight(400)
        # Setting Icon
        self.setWindowIcon(icon)
        QToolTip.setFont(self.Arials)

    def Flabel(self, glo):
        fontt = self.Arial
        if os.name == 'nt':
            self.ic1 = QIcon(r_path('static\\images\\pause.png'))
        else:
            self.ic1 = QIcon(r_path('static/images/pause.png'))
        self.l = QLabel('Icond', self)
        self.ic1 = self.ic1.pixmap(70, 70, QIcon.Active, QIcon.On)
        self.l.setPixmap(self.ic1)
        self.l.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.l.setFont(fontt)
        self.t = QLabel('Texted', self)
        self.t.setText(self.getTrans('11'))
        self.t.setOpenExternalLinks(True)
        self.t.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.t.setFont(fontt)
        self.t.setToolTip(self.getTrans('9'))
        self.l.setToolTip(self.getTrans('9'))
        glo.addStretch()
        glo.addWidget(self.l)
        glo.addWidget(self.t)
        glo.addStretch()

    def langsList(self, glo):
        self.langs = {
            # languages to be displayed in select
            'en': 'English',
            'ar': 'Arabic',
            'fr': 'French',
            'it': 'Italian',
            'es': 'Spanish'
        }
        self.langs_list = QComboBox()
        self.langs_list.addItems(self.langs.values())
        self.langs_list.setCurrentIndex(1)
        self.langs_list.setToolTip(self.getTrans('1'))
        self.langs_list.currentIndexChanged.connect(self.langChange)
        glo.addWidget(self.langs_list)
        
    def langChange (self):
        self.language = list(self.langs.keys())[self.langs_list.currentIndex()]
        self.langs_list.setToolTip(self.getTrans('1'))
        self.Amsgb = self.getTrans('2')
        self.abutton.setToolTip(
            self.getTrans('2')
        )
        self.mbutton.setText(self.getTrans('3'))
        self.mbutton.setToolTip(self.getTrans('4'))
        self.mbutton2.setText(self.getTrans('5'))
        self.mbutton2.setToolTip(self.getTrans('6'))
        self.sl.setToolTip(
            self.getTrans('7')
        )
        self.sl2.setToolTip(self.getTrans('8'))
        self.t.setToolTip(self.getTrans('9'))
        self.l.setToolTip(self.getTrans('9'))
        if self.Runningo:
            pp = self.slchange()
            addr = self.getTrans('10')
            addr += u"<a href='http://"
            addr += pp[1].split(',')[1] + u":" + pp[0]
            addr += u"'> http://" + pp[1].split(',')[1] + u":" + pp[0]
            addr += u"</a>"
            self.t.setText(addr)
        else:
            self.t.setText(self.getTrans('11'))
    
    def getTrans(self, index):
        lang = list(self.langs.keys())[self.langs_list.currentIndex()]
        try:
            return LANGUAGES[lang][index]
        except Exception:
            return None

    def Lists(self, glo):
        ips = self.get_ips()
        self.sl = QComboBox()
        self.sl.addItems(ips)
        self.sl.setToolTip(self.getTrans('7'))
        self.sl2 = QComboBox()
        self.get_ports()
        self.sl2.setToolTip('8')
        self.sl.currentIndexChanged.connect(self.get_ports)
        glo.addWidget(self.sl)
        glo.addWidget(self.sl2)

    def get_ports(self, nauto=True):
        d_ports = ['5000', '8080', '3000', '80', '9931']
        m_ports = []
        while len(m_ports) < 10:
            mip = self.slchange()
            for p in d_ports:
                s = socket(AF_INET, SOCK_STREAM)
                try:
                    s.bind((mip[1].split(',')[1], int(p)))
                    s.close()
                    m_ports.append(p)
                except:
                    s.close()
                d_ports.remove(p)
            s = socket(AF_INET, SOCK_STREAM)
            p = randint(1000, 9999)
            try:
                s.bind((mip[1].split(',')[1], p))
                s.close()
                m_ports.append(str(p))
            except:
                s.close()
            if len(m_ports) >= 10:
                break
        self.sl2.clear()
        self.sl2.addItems(m_ports)

    def slchange(self):
        return [self.sl2.currentText(), self.sl.currentText()]

    def set_button(self, glo):
        hlayout = QHBoxLayout()
        self.mbutton = QPushButton('Start', self)
        self.mbutton.clicked.connect(self.s_server)
        self.mbutton.setFont(self.Arials)
        if os.name == 'nt':
            self.mbutton.setIcon(QPixmap(r_path('static\\images\\play.png')))
        else:
            self.mbutton.setIcon(QPixmap(r_path('static/images/play.png')))
        self.mbutton2 = QPushButton('Stop', self)
        self.mbutton2.clicked.connect(self.st_server)
        if os.name == 'nt':
            self.mbutton2.setIcon(QPixmap(r_path('static\\images\\pause.png')))
        else:
            self.mbutton2.setIcon(QPixmap(r_path('static/images/pause.png')))
        self.mbutton.setToolTip(self.getTrans('4'))
        self.mbutton2.setToolTip(self.getTrans('6'))
        self.mbutton2.setEnabled(False)
        self.mbutton2.setFont(self.Arials)
        hlayout.addWidget(self.mbutton)
        hlayout.addWidget(self.mbutton2)
        glo.addLayout(hlayout)

    def s_server(self):
        mip = self.slchange()
        self.P = rwser(mip[1].split(',')[1], mip[0], self.app)
        self.P.setTerminationEnabled(True)
        if not self.P.isRunning():
            try:
                self.pport = mip[0]
                self.mbutton.setEnabled(False)
                self.mbutton2.setEnabled(True)
                self.sl.setEnabled(False)
                self.sl2.setEnabled(False)
                if os.name == 'nt':
                    self.ic1 = QIcon(r_path('static\\images\\play.png'))
                else:
                    self.ic1 = QIcon(r_path('static/images/play.png'))
                self.ic1 = self.ic1.pixmap(70, 70, QIcon.Active, QIcon.On)
                self.l.setPixmap(self.ic1)
                pp = self.slchange()
                addr = self.getTrans('10')
                addr += "<a href='http://"
                addr += pp[1].split(',')[1] + ":" + pp[0]
                addr += "'> http://" + pp[1].split(',')[1] + ":" + pp[0]
                addr += "</a>"
                self.t.setText(addr)
                self.t.setFont(self.Arial)
                self.P.start()
                self.Runningo = True
            except:
                self.eout()
        else:
            self.eout()

    def st_server(self):
        if self.P.isRunning():
            try:
                if self.P.isRunning:
                    self.P.stop()
                self.mbutton.setEnabled(True)
                self.mbutton2.setEnabled(False)
                self.sl.setEnabled(True)
                self.sl2.setEnabled(True)
                self.t.setText(self.getTrans('11'))
                # removing the last used port to avoid termination error
                cind = self.sl2.currentIndex()
                self.sl2.removeItem(cind)
                self.get_ports()
                self.Runningo = False
            except:
                self.eout()
        else:
            self.eout()

    def set_Abutton(self, icon, glo):
        def show_about(nself):
            Amsg = u" <center> "
            Amsg += self.getTrans('12') + version + u" "
            Amsg += self.getTrans('13')
            Amsg += self.getTrans('14')
            Amsg += self.getTrans('15')
            Amsg += u"<br> <b><a href='https://fqms.github.io/'>"
            Amsg += u"https://fqms.github.io </a> </b></center>"
            Amsgb = self.getTrans('2')
            return QMessageBox.about(
                self,
                Amsgb,
                Amsg)
        self.abutton = QPushButton('', self)
        self.abutton.setIcon(QPixmap(icon))
        self.abutton.setIconSize(QSize(150, 70))
        self.abutton.setToolTip(self.getTrans('2'))
        self.abutton.clicked.connect(partial(show_about, self))
        glo.addWidget(self.abutton)

    def closeEvent(self, event=None):
        if self.Runningo:
            response = self.msgApp(
                self.getTrans('16'),
                self.getTrans('17'))
            if response == 'y':
                if event is not None:
                    event.accept()
                if self.P.isRunning():
                    self.P.stop()
                sys.exit(0)
            else:
                if event is not None:
                    event.ignore()
        else:
            if event is not None:
                event.accept()
            if self.P.isRunning():
                self.P.stop()
            sys.exit(0)

    def msgApp(self, title, msg):
        uinfo = QMessageBox.question(self, title,
                                     msg, QMessageBox.Yes | QMessageBox.No)
        if uinfo == QMessageBox.Yes:
            return 'y'
        if uinfo == QMessageBox.No:
            return 'n'

    def eout(self):
        if self.P.isRunning():
            self.P.stop()
        msgg = u"<center>"
        msgg += self.getTrans('18')
        msgg += self.getTrans('19')
        msgg += u"<br><b><a href='https://fqms.github.io/'> "
        msgg += u"https://fqms.github.io </a></b> </center>"
        mm = QMessageBox.critical(
            self,
            self.getTrans('20'),
            msgg,
            QMessageBox.Ok)

    def center(self):
        qrect = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qrect.moveCenter(cp)
        self.move(qrect.topLeft())

    def get_ips(self):
        il = []
        for i in interfaces():
            try:
                if os.name != 'nt':
                    inf = i + " ,"
                else:
                    inf = ' ,'
                inf += ifaddresses(i)[2][0].get('addr')
                il.append(inf)
            except:
                pass
        return il


def run_app():
    app = create_app()
    create_db(app)
    appg = QApplication(sys.argv)
    if os.name != 'nt':
        # !!! it did not work creates no back-end available error !!!
        # !!! strange bug , do not remove !!!
        if listp():
            pass
    window = NewWindow(app)

    # switching the language with template folder path
    @app.route('/lang_switch/<int:lang>')
    def lang_switch(lang):
        if lang == 1:
            session['lang'] = 'AR'
        else:
            session['lang'] = 'EN'
        if current_user.is_authenticated:
            return redirect(str(request.referrer))
        return redirect(url_for('core.root'))
    # Adding error handlers on main app instance

    @app.errorhandler(404)
    @app.errorhandler(500)
    @app.errorhandler(413)
    def page_not_found(error):
        if error == 413:
            flash(get_lang(55), "danger")
            if current_user.is_authenticated:
                return redirect(url_for('cust_app.multimedia', nn=1))
            return redirect(url_for('core.root'))
        flash(get_lang(56), "danger")
        return redirect(url_for('core.root'))
    # Injecting default variables to all templates

    @app.context_processor
    def inject_vars():
        # adding language support var
        ar = False
        if session.get('lang') == 'AR':
            ar = True
        # modifing side bar spacing for specific paths
        path = request.path
        adml = ['/users', '/user_a', '/admin_u', '/user_u',
                '/csvd', '/settings']
        adme = False
        if path in adml or path[:7] in adml or path[:5] in adml:
            adme = True
        return dict(is_connected=check_ping, path=path,
                    adme=adme, brp=Markup("<br>"), ar=ar,
                    version=version)
    QCoreApplication.processEvents()
    appg.exec_()
