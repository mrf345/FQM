# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import data
from database import db
import os
from httplib import HTTPConnection as htp
from flask import session
import languages as LANGUAGES
from database import gtranslator
# Extra functions


def mse():
    lodb = [data.Display_store,
            data.Touch_store,
            data.Slides_c,
            data.Vid, data.Waiting_c,
            data.Printer]
    # -- make sure objects are created,
    # And if not create an auto filled one
    for t in lodb:
        if t.query.first() is None:
            db.session.add(t())
    # fill in user roles if not existed
    if data.Roles.query.first() is None:
        for r in range(1, 4):
            ra = data.Roles()
            ra.id = r
            if r == 1:
                ra.name = 'Administrator'
            elif r == 2:
                ra.name = 'Monitor'
            else:
                ra.name = 'Operator'
            db.session.add(ra)
    for o in data.Office.query:
        if data.Serial.query.filter_by(office_id=o.id).first() is None:
            tk = data.Task.query.filter_by(office_id=o.id).first()
            if tk is not None:
                dd = data.Serial(100, o.id, tk.id, None, False)
                dd.p = True
                db.session.add(dd)
            else:
                dd = data.Serial(100, o.id, 1, None, False)
                dd.p = True
                db.session.add(dd)
    db.session.commit()


def getFolderSize(folder):
    # -- get a folder size
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return str(total_size / 1024 / 1024)


def check_ping():
    rl = False
    try:
        tt = htp("www.google.com", 80, 1000)
        tt.request('HEAD', '/')
        tt.close()
        rl = True
    except:
        pass
    print rl
    return rl


def r_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_lang(i_num):
    """ function to get the set language and return the correct flash
    messages list """
    return LANGUAGES.flashMessages[i_num]


def transAll():
    """ to translate all flash messages """
    for l in LANGUAGES.flashMessages:
        gtranslator.translate(l, 'en', ['ar', 'fr', 'it', 'es'])
    return True


def solve_path(path):
    """ fix path for window os """
    return path.replace('/', '\\') if os.name == 'nt' else path