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
        # Language support varibels used by translate func
        self.Arabic = None
        self.Runningo = False
        icon = QIcon(icp)
        self.SelfIinit(icon)
        self.center()
        self.Llists(glo)
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
        self.t.setText("Server is <u> Not running </u> <br>")
        self.t.setOpenExternalLinks(True)
        self.t.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.t.setFont(fontt)
        self.t.setToolTip('Status of the server')
        self.l.setToolTip('Status of the server')
        glo.addStretch()
        glo.addWidget(self.l)
        glo.addWidget(self.t)
        glo.addStretch()

    def Lists(self, glo):
        ips = self.get_ips()
        self.sl = QComboBox()
        self.sl.addItems(ips)
        self.sl.setToolTip(
            'Select network interface with ip, so the server runs on it')
        self.sl2 = QComboBox()
        self.get_ports()
        self.sl2.setToolTip('Select a port, so server runs through it')
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

    def Llists(self, glo):
        hlayout = QHBoxLayout()
        self.lebutton = QPushButton('English', self)
        self.lebutton.setToolTip('Change language to English')
        self.lebutton.setEnabled(False)
        self.lebutton.setFont(self.Arials)
        self.labutton = QPushButton('Arabic', self)
        self.labutton.setFont(self.Arials)
        if os.name == 'nt':
            self.lebutton.setIcon(QPixmap(r_path(
                'static\\images\\english.png')))
            self.labutton.setIcon(QPixmap(r_path(
                'static\\images\\arabic.png')))
        else:
            self.lebutton.setIcon(QPixmap(r_path(
                'static/images/english.png')))
            self.labutton.setIcon(QPixmap(r_path(
                'static/images/arabic.png')))
        self.labutton.setToolTip('Change language to Arabic')
        self.labutton.setEnabled(True)
        self.lebutton.clicked.connect(partial(self.translate, ar=False))
        self.labutton.clicked.connect(self.translate)
        hlayout.addWidget(self.lebutton)
        hlayout.addWidget(self.labutton)
        glo.addLayout(hlayout)

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
        self.mbutton.setToolTip('Start the server')
        self.mbutton2.setToolTip('Stop the server')
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
                if self.Arabic is None:
                    pp = self.slchange()
                    addr = "Server is <u>Running</u> <br>"
                    addr += " On : <a href='http://"
                    addr += pp[1].split(',')[1] + ":" + pp[0]
                    addr += "'> http://" + pp[1].split(',')[1] + ":" + pp[0]
                    addr += "</a>"
                    self.t.setText(addr)
                    self.t.setFont(self.Arial)
                else:
                    pp = self.slchange()
                    addr = u"الخدمة <u>مشغــلة</u> و تبث على : <br>"
                    addr += u"<a href='http://"
                    addr += pp[1].split(',')[1] + u":" + pp[0]
                    addr += u"'> http://" + pp[1].split(',')[1] + u":" + pp[0]
                    addr += u"</a>"
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
                if self.Arabic is None:
                    self.t.setText("Server is <u> Not running </u> <br>")
                else:
                    self.t.setText(u"الــخـدمة <u>متــوقفــة</u><br>")
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
            if nself.Arabic is None:
                Amsg = "<center>All credit reserved to the author of FQM "
                Amsg += " version " + version
                Amsg += ", This work is a free, open-source project licensed "
                Amsg += " under Mozilla Public License version 2.0 . <br><br>"
                Amsg += " visit us for more infos and how-tos :<br> "
                Amsg += "<b><a href='https://fqms.github.io/'> "
                Amsg += "https://fqms.github.io/ </a> </b></center>"
                Amsgb = "About FQM"
            else:
                Amsg = u" <center> "
                Amsg += u" إدارة الحشود الحر النسخة " + version + u" "
                Amsg += u"حقوق نشر هذا البرنامج محفوظة و تخضع "
                Amsg += u" لرخصة البرامج الحرة و مفتوحة المصدر "
                Amsg += u" Mozilla Public License version 2.0 . "
                Amsg += u"<br><br> "
                Amsg += u"للمزيد من المعلومات و الشروحات , قم بزيارة :"
                Amsg += u"<br> <b><a href='https://fqms.github.io/'>"
                Amsg += u"https://fqms.github.io </a> </b></center>"
                Amsgb = u"عن النظام"
            return QMessageBox.about(
                self,
                Amsgb,
                Amsg)
        self.abutton = QPushButton('', self)
        self.abutton.setIcon(QPixmap(icon))
        self.abutton.setIconSize(QSize(150, 70))
        self.abutton.setToolTip('About FQM')
        self.abutton.clicked.connect(partial(show_about, self))
        glo.addWidget(self.abutton)

    def closeEvent(self, event=None):
        if self.Runningo:
            if self.Arabic is None:
                response = self.msgApp(
                    "Exiting while running",
                    "Are you really sure, you want to exit ?")
            else:
                response = self.msgApp(
                    u"تأكيد الخروج",
                    u"تريد بالفعل , الخروج و إيقاف البرنامج ؟")
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
        if self.Arabic is None:
            msgg = "<center>"
            msgg += " Opps, a critical error has occurred, we will be "
            msgg += " grateful if you can help fixing it, by reporting to us "
            msgg += " at : <br><br> "
            msgg += "<b><a href='https://fqms.github.io/'> "
            msgg += "https://fqms.github.io/ </a></b> </center>"
            mm = QMessageBox.critical(
                self,
                "Critical Error",
                msgg,
                QMessageBox.Ok)
        else:
            msgg = u"<center>"
            msgg += u"حدث خطأ فادح في تشغيل النظام , سنكون شاكرين لك إن "
            msgg += u"قمت بتبليغنا عنه , ليتم إصلاحه في أقرب وقت "
            msgg += u"<br>"
            msgg += u"<br><b><a href='https://fqms.github.io/'> "
            msgg += u"https://fqms.github.io </a></b> </center>"
            mm = QMessageBox.critical(
                self,
                u"خطأ في التشغيل",
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

    def translate(self, ar=True):
        if ar:
            self.Arabic = "arabic"
            self.labutton.setEnabled(False)
            self.labutton.setText(u"العربية")
            self.labutton.setToolTip(u"تغير اللغة إلى العربية")
            self.lebutton.setText(u"الإنجليزية")
            self.lebutton.setToolTip(u"تغير اللغة إلى الإنجليزية")
            self.lebutton.setEnabled(True)
            self.Amsgb = u"عن النظام"
            self.abutton.setToolTip(
                u"عن النظام"
            )
            self.mbutton.setText(u"تشغــيل")
            self.mbutton.setToolTip(u"تشغيل الخدمة")
            self.mbutton2.setText(u"إيــقاف")
            self.mbutton2.setToolTip(u"إيقاف الخدمة")
            self.sl.setToolTip(
                u"إختار عنوان IP ليتم بث الخدمة عليه")
            self.sl2.setToolTip(u"إختار منفذ ليتم بث الخدمة من خلاله")
            self.t.setToolTip(u"حالة الخدمة ")
            self.l.setToolTip(u"حالة الخدمة ")
            if self.Runningo:
                pp = self.slchange()
                addr = u"الخدمة <u>مشغــلة</u> و تبث على : <br>"
                addr += u"<a href='http://"
                addr += pp[1].split(',')[1] + u":" + pp[0]
                addr += u"'> http://" + pp[1].split(',')[1] + u":" + pp[0]
                addr += u"</a>"
                self.t.setText(addr)
            else:
                self.t.setText(u"الــخـدمة <u>متــوقفــة</u><br>")
        else:
            self.Arabic = None
            self.lebutton.setEnabled(False)
            self.lebutton.setText("English")
            self.lebutton.setToolTip('Change language to English')
            self.labutton.setEnabled(True)
            self.labutton.setText("Arabic")
            self.labutton.setToolTip('Change language to Arabic')
            self.Amsgb = "About FQM"
            self.abutton.setToolTip('About FQM')
            self.mbutton.setText("Start")
            self.mbutton.setToolTip("Start the server")
            self.mbutton2.setText("Stop")
            self.mbutton2.setToolTip("Stop the server")
            self.sl.setToolTip(
                'Select network interface with ip, so the server runs on it')
            self.sl2.setToolTip('Select a port, so server runs through it')
            self.t.setToolTip('Status of the server')
            self.l.setToolTip('Status of the server')
            if self.Runningo:
                pp = self.slchange()
                addr = "Server is <u>Running</u> <br>"
                addr += " On : <a href='http://"
                addr += pp[1].split(',')[1] + ":" + pp[0]
                addr += "'> http://" + pp[1].split(',')[1] + ":" + pp[0]
                addr += "</a>"
                self.t.setText(addr)
            else:
                self.t.setText("Server is <u> Not running </u> <br>")


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
    # Injecting default varibles to all templates

    @app.context_processor
    def inject_vars():
        # adding language support var
        ar = False
        if session.get('lang') == 'AR':
            ar = True
        # adding browser detection var
        firefox = False
        if session.get('firefox') == 1:
            firefox = True
        # modifing side bar spacing for specific paths
        path = request.path
        adml = ['/users', '/user_a', '/admin_u', '/user_u',
                '/csvd', '/settings']
        adme = False
        if path in adml or path[:7] in adml or path[:5] in adml:
            adme = True
        return dict(is_connected=check_ping, path=path,
                    adme=adme, brp=Markup("<br>"), ar=ar,
                    firefox=firefox, version=version)
    QCoreApplication.processEvents()
    appg.exec_()
