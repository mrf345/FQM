# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db


class Office(db.Model):
    __tablename__ = "offices"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, unique=True)
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    prefix = db.Column(db.String(2))

    def __init__(self, name, prefix):
        self.name = name
        self.prefix = prefix


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))

    def __init__(self, name, office_id):
        self.name = name
        self.office_id = office_id


class Serial(db.Model):
    __tablename__ = "serials"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    date = db.Column(db.Date(), default=datetime.utcnow().date)
    name = db.Column(db.String(300), nullable=True)
    n = db.Column(db.Boolean)
    p = db.Column(db.Boolean)
    # stands for proccessed , which be modified after been processed
    pdt = db.Column(db.DateTime())
    # Fix: adding pulled by feature to tickets
    pulledBy = db.Column(db.Integer)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def __init__(self, number=100,
                 office_id=1,
                 task_id=1, pulledBy = 01,
                 name=None, n=False, p=False):
        self.number = number
        self.office_id = office_id
        self.task_id = task_id
        self.name = name
        self.n = n
        # fixing mass use tickets multi operators conflict
        self.p = p
        self.pulledBy = pulledBy

class Waiting(db.Model):
    __tablename__ = "waitings"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(300), nullable=True)
    n = db.Column(db.Boolean)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def __init__(self, number, office_id, task_id, name=None, n=False):
        self.number = number
        self.office_id = office_id
        self.task_id = task_id
        self.name = name
        self.n = n


class Waiting_c(db.Model):
    __tablename__ = "waitings_c"
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String)
    oname = db.Column(db.String)
    tname = db.Column(db.String)
    n = db.Column(db.Boolean)
    name = db.Column(db.String(300), nullable=True)

    def __init__(self, ticket="Empty", oname="Empty", tname="Empty",
                 n=False, name=None):
        self.id = 0
        self.ticket = ticket
        self.oname = oname
        self.tname = tname
        self.n = n
        self.name = name


class Operators(db.Model):
    __tablename__ = "operators"
    crap = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))

    def __init__(self, id, office_id):
        self.id = id
        self.office_id = office_id


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, name, password, role_id):
        self.password = password
        self.name = name
        self.role_id = role_id

    def __str__(self):
        return "<%r>" % self.name

    @property
    def password(self):
        raise AttributeError('password not for reading !!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)


class Printer(db.Model):
    __tablename__ = "printers"
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=True, unique=True)
    product = db.Column(db.String(100), unique=True)
    in_ep = db.Column(db.Integer, nullable=True)
    out_ep = db.Column(db.Integer, nullable=True)
    active = db.Column(db.Boolean())
    langu = db.Column(db.String(100))
    value = db.Column(db.Integer)

    def __init__(self, vendor=" ", product=" ",
                 in_ep=0, out_ep=0, active=False,
                 langu='en', value=1):
        self.vendor = vendor
        self.product = product
        self.in_ep = in_ep
        self.out_ep = out_ep
        self.active = active
        self.value = value


# 00 Configuration Tabels 00 #
# -- Touch custimization table


class Touch_store(db.Model):
    __tablename__ = 'touchs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    message = db.Column(db.Text())
    hsize = db.Column(db.String(100))
    hcolor = db.Column(db.String(100))
    hbg = db.Column(db.String(100))
    tsize = db.Column(db.String(100))
    tcolor = db.Column(db.String(100))
    msize = db.Column(db.String(100))
    mcolor = db.Column(db.String(100))
    mbg = db.Column(db.String(100))
    audio = db.Column(db.String(100))
    hfont = db.Column(db.String(100))
    mfont = db.Column(db.String(100))
    tfont = db.Column(db.String(100))
    mduration = db.Column(db.String(100))
    bgcolor = db.Column(db.String(100))
    p = db.Column(db.Boolean)
    n = db.Column(db.Boolean)
    tmp = db.Column(db.Integer)
    akey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)
    ikey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)

    def __init__(self, id=0, title="Please select a task to pull a tick for",
                 hsize="500%", hcolor="rgb(129, 200, 139)",
                 hbg="rgba(0, 0, 0, 0.50)", tsize="400%",
                 mbg="rgba(0, 0, 0, 0.50)", msize="400%",
                 mcolor="rgb(255, 255, 0)", tcolor="btn-danger",
                 message="Ticket has been issued, pleas wait your turn",
                 audio="bell_sound.wav", hfont="El Messiri", mfont="Mada",
                 tfont="Amiri", ikey=1, tmp=2, akey=5,
                 mduration="3000", bgcolor="bg_dark.jpg", p=False, n=True):
        self.id = 0
        self.hfont = hfont
        self.mfont = mfont
        self.tfont = tfont
        self.mduration = mduration
        self.title = title
        self.message = message
        self.hsize = hsize
        self.hcolor = hcolor
        self.hbg = hbg
        self.tsize = tsize
        self.tcolor = tcolor
        self.msize = msize
        self.mcolor = mcolor
        self.mbg = mbg
        self.audio = audio
        self.bgcolor = bgcolor
        self.ikey = ikey
        self.akey = akey
        self.p = p
        self.n = n
        self.tmp = tmp


# -- Touch customization table


class Display_store(db.Model):
    __tablename__ = 'displays'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    hsize = db.Column(db.String(100))
    hcolor = db.Column(db.String(100))
    h2size = db.Column(db.String(100))
    h2color = db.Column(db.String(100))
    h2font = db.Column(db.String(100))
    hbg = db.Column(db.String(100))
    tsize = db.Column(db.String(100))
    tcolor = db.Column(db.String(100))
    ssize = db.Column(db.String(100))
    scolor = db.Column(db.String(100))
    audio = db.Column(db.String(10))
    hfont = db.Column(db.String(100))
    tfont = db.Column(db.String(100))
    sfont = db.Column(db.String(100))
    mduration = db.Column(db.String(100))
    rrate = db.Column(db.String(100))
    announce = db.Column(db.String(100))
    anr = db.Column(db.Integer)
    anrt = db.Column(db.String(100))
    effect = db.Column(db.String(100))
    repeats = db.Column(db.String(100))
    bgcolor = db.Column(db.String(100))
    tmp = db.Column(db.Integer)
    akey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)
    ikey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)
    vkey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)

    def __init__(self, id=0, title="FQM Queue Management",
                 hsize="500%", hcolor="rgb(129, 200, 139)", h2size="600%",
                 h2color="rgb(184, 193, 255)", h2font="Mada",
                 hbg="rgba(0, 0, 0, 0.5)", tsize="600%",
                 tcolor="rgb(184, 193, 255)", ssize="500%",
                 scolor="rgb(224, 224, 224)", audio="bell_sound.wav",
                 hfont="El Messiri", tfont="Mada", repeats="3", effect="fade",
                 sfont="Amiri", mduration="3000", rrate="2000",
                 announce="en-us", ikey=4, vkey=6, akey=5,
                 anr=2, anrt="each", bgcolor="rgb(0,0,0)", tmp=0):
        self.id = 0
        self.tfont = tfont
        self.hfont = hfont
        self.h2font = h2font
        self.sfont = sfont
        self.mduration = mduration
        self.rrate = rrate
        self.title = title
        self.hsize = hsize
        self.hcolor = hcolor
        self.hsize = hsize
        self.hcolor = hcolor
        self.h2color = h2color
        self.h2size = h2size
        self.hcolor = hcolor
        self.hbg = hbg
        self.tsize = tsize
        self.tcolor = tcolor
        self.ssize = ssize
        self.scolor = scolor
        self.audio = audio
        self.announce = announce
        self.bgcolor = bgcolor
        self.tmp = tmp
        self.anr = anr
        self.anrt = anrt
        self.effect = effect
        self.repeats = repeats
        self.ikey = ikey
        self.vkey = vkey
        self.akey = akey

# -- Slides storage table


class Slides(db.Model):
    __tablename__ = "slides"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    hsize = db.Column(db.String(100))
    hcolor = db.Column(db.String(100))
    hfont = db.Column(db.String(100))
    hbg = db.Column(db.String(100))
    subti = db.Column(db.String(300))
    tsize = db.Column(db.String(100))
    tcolor = db.Column(db.String(100))
    tfont = db.Column(db.String(100))
    tbg = db.Column(db.String(100))
    bname = db.Column(db.String(300))
    ikey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)


# -- ^^ Slides custimization table

class Slides_c(db.Model):
    __tablename__ = "slides_c"
    id = db.Column(db.Integer, primary_key=True)
    rotation = db.Column(db.String(100))
    navigation = db.Column(db.Integer)
    effect = db.Column(db.String(100))
    status = db.Column(db.Integer)

    def __init__(self, rotation="3000",
                 navigation=2, effect="slide",
                 status=2):
        self.id = 0
        self.rotation = rotation
        self.effect = effect
        self.status = status
        self.navigation = navigation


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    vid = db.Column(db.Boolean())
    audio = db.Column(db.Boolean())
    img = db.Column(db.Boolean())
    used = db.Column(db.Boolean())
    name = db.Column(db.String(50))

    def __init__(self, vid=False, audio=False,
                 img=False, used=False, name="   "):
        self.vid = vid
        self.audio = audio
        self.img = img
        self.used = used
        self.name = name


class Vid(db.Model):
    __tablename__ = "vids"
    id = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(300))
    enable = db.Column(db.Integer)
    ar = db.Column(db.Integer)
    controls = db.Column(db.Integer)
    mute = db.Column(db.Integer)
    vkey = db.Column(db.Integer, db.ForeignKey("media.id",
                                               ondelete='cascade'),
                     nullable=True)

    def __init__(self, vname="Tokyo.mp4", enable=1, ar=1, controls=1,
                 mute=2, vkey=6):
        self.vname = vname
        self.enable = enable
        self.ar = ar
        self.controls = controls
        self.mute = mute
        self.vkey = vkey
