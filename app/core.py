# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import url_for, flash, render_template, redirect
from flask import session, jsonify, request, Markup, Blueprint
from flask_login import current_user, login_required, login_user
import os
from random import randint
from gtts import gTTS as gt
from datetime import datetime
import ex_functions
import forms
import data
import printer as ppp
from database import db
from ex_functions import get_lang, say_it
from shutil import rmtree
from multiprocessing.pool import ThreadPool
from sys import platform

core = Blueprint('core', __name__)


@core.route('/', methods=['GET', 'POST'])
@core.route('/log/<n>', methods=['GET', 'POST'])
def root(n=None):
    b = None
    form = forms.Login()
    if session.get('lang') == 'AR':
        form = forms.Login_ar()
    if n is not None and n == 'a':
        n = True
    elif n is not None and n == 'b':
        b = True
    elif n is None:
        n = False
    else:
        flash(get_lang(4),
              "danger")
        return redirect(url_for('core.root'))
    if data.User.query.first() is None:
        flash(get_lang(4),
              "danger")
        return redirect(url_for('core.root'))
    # Check if default password and account
    dpass = False
    if data.User.query.filter_by(id=1).first().verify_password('admin'):
        dpass = True
    if form.validate_on_submit():
        if current_user.is_authenticated:
            flash(get_lang(4),
                  "danger")
            return redirect(url_for('core.root'))
        user = data.User.query.filter_by(name=form.name.data).first()
        if user is not None:
            d = data.Office.query.filter_by(operator_id=user.id).first()
            if user.role_id == 3 and d is None:
                flash(get_lang(15),
                      "danger")
                return redirect(url_for('core.root'))
            if user.verify_password(form.password.data):
                if form.rm.data:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                flash(get_lang(16), "info")
                if b:
                    s = str(session.get('next_url', '/'))
                    session['next_url'] = None
                    return redirect(s)
                else:
                    return redirect(url_for('manage_app.manage'))
            flash(get_lang(17), "danger")
            return redirect(url_for("core.root", n='a'))
        flash(get_lang(17), "danger")
        return redirect(url_for("core.root", n='a'))
    return render_template("index.html",
                           ptitle="Free Queue Manager",
                           form=form, n=n, dpass=dpass)


@core.route('/serial/<int:t_id>', methods=['POST', 'GET'])
@login_required
def serial(t_id):
    ex_functions.mse()
    form = forms.Touch_name()
    if session.get('lang') == "AR":
        form = forms.Touch_name_ar()
    tsk = data.Task.query.filter_by(id=t_id).first()
    if tsk is None:
        flash(get_lang(4),
              "danger")
        return redirect(url_for("core.root"))
    oid = data.Office.query.filter_by(operator_id=current_user.id).first()
    if current_user.role_id == 3 and oid is None:
        flash(get_lang(18),
              "danger")
        return redirect(url_for('core.root'))
    if current_user.role_id == 3 and tsk.office_id != oid.id:
        flash(get_lang(18),
              "danger")
        return redirect(url_for('core.root'))
    if not form.validate_on_submit() and data.Touch_store.query.first().n:
        ts = data.Touch_store.query.filter_by(id=0).first()
        return render_template("touch.html", title=ts.title,
                               ts=ts, done=False, bgcolor=ts.bgcolor,
                               ptitle="Touch Screen - Enter name ",
                               a=4, dire='multimedia/', form=form)
    nm = form.name.data
    if nm is None:
        n = False
    else:
        n = True
    o_id = data.Task.query.filter_by(id=t_id).first().office_id
    ln = data.Serial.query.filter_by(
        office_id=o_id).order_by(data.Serial
                                 .timestamp.desc(
                                 )).first().number
    sr = data.Serial.query.filter_by(number=ln + 1, office_id=o_id,
                                     task_id=t_id).first()
    if sr is None:
        if n:
            db.session.add(data.Serial(ln + 1, o_id, t_id, nm, n))
        else:
            db.session.add(data.Serial(ln + 1, o_id, t_id, None, False))
            # adding printer support
            q = data.Printer.query.first()
            ppt = data.Task.query.filter_by(id=t_id).first()
            oot = data.Office.query.filter_by(id=o_id).first()
            tnum = data.Serial.query.filter_by(office_id=o_id, p=None).count()
            cuticket = data.Serial.query.filter_by(
                office_id=o_id, p=None).first()
            tnum -= 1
            langu = data.Printer.query.first().langu
            # to solve Linux printer permissions
            if os.name == 'nt':
                # to solve windows shared printers
                import win_printer
                from pythoncom import CoInitialize as coli
                coli()
                chk = win_printer.check_win_p()
                chl = len(win_printer.listpp())
                if chl >= 1 and chk is True:
                    if langu == 2:
                        win_printer.printwin_ar(
                            q.product,
                            oot.prefix + '.' + str(ln + 1),
                            oot.prefix + str(oot.name),
                            tnum, ppt.name,
                            oot.prefix + '.' + str(cuticket.number))
                    else:
                        win_printer.printwin(
                            q.product,
                            oot.prefix + '.' + str(ln + 1),
                            oot.prefix + str(oot.name),
                            tnum, ppt.name,
                            oot.prefix + '.' + str(cuticket.number))
                    p = True
                else:
                    p = None
            else:
                try:
                    p = ppp.assign(int(q.vendor), int(q.product),
                                   int(q.in_ep), int(q.out_ep))
                except:
                    p = None
            if p is None:
                flash(get_lang(19),
                      'danger')
                flash(get_lang(20),
                      "info")
                if os.name == 'nt':
                    flash(get_lang(57), "info")
                elif platform == "linux" or platform == "linux2":
                    flash(get_lang(58), "info")
                return redirect(url_for('cust_app.ticket'))
            if os.name != 'nt':
                if langu == 1:
                    ppp.printit(p,
                                oot.prefix + '.' + str(ln + 1),
                                oot.prefix + str(oot.name),
                                tnum, u'' + ppt.name,
                                oot.prefix + '.' + str(cuticket.number))
                else:
                        ppp.printit_ar(p,
                                       oot.prefix + '.' + str(ln + 1),
                                       oot.prefix + str(oot.name),
                                       tnum, u'' + ppt.name,
                                       oot.prefix + '.' + str(cuticket.number))
        db.session.commit()
    else:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('core.root'))
    for a in range(data.Waiting.query.count(), 11):
        for b in data.Serial.query.filter_by(
                p=None).order_by(data.Serial.timestamp):
            if data.Waiting.query.filter_by(office_id=b.office_id,
                                            number=b.number, task_id=b.task_id
                                            ).first() is None:
                db.session.add(data.Waiting(b.number, b.office_id,
                                            b.task_id, nm, n))
        db.session.commit()
    return redirect(url_for("core.touch", a=1))


@core.route('/serial_r/<int:o_id>')
@login_required
def serial_r(o_id):
    if data.Office.query.filter_by(id=o_id).first() is None:
        flash(get_lang(4), "danger")
        return redirect(url_for("manage_app.all_offices"))
    sr = data.Serial.query.filter_by(office_id=o_id)
    oid = data.Office.query.filter_by(operator_id=current_user.id).first()
    if current_user.role_id == 3 and oid is None:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if current_user.role_id == 3 and o_id != oid.id:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if sr.first() is None:
        flash(get_lang(21),
              "danger")
        return redirect(url_for("manage_app.offices", o_id=o_id))
    for f in sr:
        w = data.Waiting.query.filter_by(office_id=f.office_id,
                                         number=f.number).first()
        db.session.delete(f)
        if w is not None:
            db.session.delete(w)
    db.session.commit()
    flash(get_lang(22),
          "info")
    return redirect(url_for("manage_app.offices", o_id=o_id))


@core.route('/serial_ra')
@login_required
def serial_ra():
    if data.Office.query.first() is None:
        flash(get_lang(54), "danger")
        return redirect(url_for("manage_app.all_offices"))
    if current_user.role_id == 3:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    sr = data.Serial.query
    if sr.first() is None:
        flash(get_lang(21),
              "danger")
        return redirect(url_for("manage_app.all_offices"))
    for f in sr:
        w = data.Waiting.query.filter_by(office_id=f.office_id,
                                         number=f.number).first()
        db.session.delete(f)
        if w is not None:
            db.session.delete(w)
    db.session.commit()
    flash(get_lang(22),
          "info")
    return redirect(url_for("manage_app.all_offices"))


@core.route('/serial_rt/<int:t_id>')
@login_required
def serial_rt(t_id):
    if data.Task.query.filter_by(id=t_id).first() is None:
        flash(get_lang(54), "danger")
        return redirect(url_for("manage_app.all_offices"))
    sr = data.Serial.query.filter_by(task_id=t_id)
    oid = data.Office.query.filter_by(operator_id=current_user.id).first()
    if current_user.role_id == 3 and oid is None:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if current_user.role_id == 3 and t_id != oid.id:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if sr.first() is None:
        flash(get_lang(23),
              "danger")
        return redirect(url_for("manage_app.task", o_id=t_id))
    for f in sr:
        w = data.Waiting.query.filter_by(office_id=f.office_id,
                                         number=f.number).first()
        db.session.delete(f)
        if w is not None:
            db.session.delete(w)
    db.session.commit()
    flash(get_lang(24),
          "info")
    return redirect(url_for("manage_app.task", o_id=t_id))


@core.route('/pull/<int:o_id>')
@login_required
def pull(o_id):
    if os.name == 'nt':
        path = ex_functions.r_path('static\\tts\\')
    else:
        path = ex_functions.r_path('static/tts/')
    if data.Office.query.filter_by(id=o_id).first() is None:
        flash(get_lang(4), "danger")
        return redirect(url_for("manage_app.offices", o_id=o_id))
    oid = data.Office.query.filter_by(operator_id=current_user.id).first()
    if current_user.role_id == 3 and oid is None:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if current_user.role_id == 3 and o_id != oid.id:
        flash(get_lang(17),
              "danger")
        return redirect(url_for('core.root'))
    if data.Serial.query.filter_by(p=None).count() >= 0:
        for a in range(data.Waiting.query.count(), 11):
            for b in data.Serial.query.filter_by(p=None).order_by(
                    data.Serial.timestamp):
                if data.Waiting.query.filter_by(office_id=b.office_id,
                                                number=b.number,
                                                task_id=b.task_id
                                                ).first() is None:
                    db.session.add(data.Waiting(b.number, b.office_id,
                                                b.task_id, b.name, b.n))
        db.session.commit()
    else:
        flash(get_lang(25), "danger")
        return redirect(url_for("manage_app.offices", o_id=o_id))
    cs = data.Waiting.query.filter_by(office_id=o_id).first()
    if cs is None:
        flash(get_lang(25), "danger")
        return redirect(url_for("manage_app.offices", o_id=o_id))
    ocs = data.Office.query.filter_by(id=o_id).first()
    toc = data.Task.query.filter_by(id=cs.task_id).first().name
    # adding to current waiting
    cl = data.Waiting_c.query.first()
    cl.ticket = ocs.prefix + str(cs.number)
    cl.oname = ocs.prefix + str(ocs.name)
    cl.tname = toc
    cl.n = cs.n
    cl.name = cs.name
    data.db.session.add(cl)
    db.session.commit()
    # Adding text to speech
    lang = data.Display_store.query.first()
    office = cl.oname
    if lang.announce != "false":
        if os.path.isdir(path):
            rmtree(path)
        os.mkdir(path)
        if cl.n:
            ticket = cl.name
            if lang.announce == "ar":
                ms = "الرجاء من المدعوا "
                ms += (ticket).encode('utf-8')
                ms += " , التوجه إلى مكتب رقم "
                ms += (office).encode('utf-8')
                ms += " ."
            elif lang.announce == "en-us":
                ms = (ticket
                      ).encode('utf-8'
                               ) + " , please proceed to the office number : "
                ms += str(office) + " ."
            elif lang.announce == "both":
                ms = "الرجاء من المدعوا "
                ms += (ticket).encode('utf-8')
                ms += " , التوجه إلى مكتب رقم "
                ms += (office).encode('utf-8')
                ms += " ."
                ms2 = (ticket
                       ).encode('utf-8'
                                ) + " , please proceed to the office number : "
                ms2 += str(office) + " ."
        else:
            ticket = cl.ticket
            if lang.announce == "ar":
                ms = "الرجاء من صاحب الرقم "
                ms += (ticket).encode('utf-8')
                ms += " , التوجه إلى مكتب رقم "
                ms += (office).encode('utf-8') + " ."
            elif lang.announce == "en-us":
                ms = "The number : " + (ticket).encode('utf-8')
                ms += " , please proceed to the office number : "
                ms += str(office) + " ."
            elif lang.announce == "both":
                ms = "الرجاء من صاحب الرقم "
                ms += (ticket).encode('utf-8')
                ms += " , التوجه إلى مكتب رقم "
                ms += (office).encode('utf-8') + " ."
                ms2 = "The number : " + (ticket).encode('utf-8')
                ms2 += " , please proceed to the office number : "
                ms2 += str(office) + " ."
        fname = str(randint(1, 10000)) + ".mp3"
        lang.afile = fname
        db.session.add(lang)
        db.session.commit()
        fpath = path + fname
        # Applying threading for GTTS
        pool = ThreadPool(processes=2)
        if lang.announce == "both":
            fname2 = "ar_" + fname
            path2 = path + fname2
            pool.apply_async(say_it, (ms, "ar", path2))
            pool.apply_async(say_it, (ms2, "en-us", fpath))
        else:
            pool.apply_async(say_it, (ms, lang.announce, fpath))
        pool.close()
        pool.join()
    # last check for available tickets and final commit
    sr = data.Serial.query.filter_by(office_id=cs.office_id,
                                     task_id=cs.task_id,
                                     number=cs.number).first()
    if sr is None:
        flash(get_lang(25), "danger")
        return redirect(url_for("manage_app.offices", o_id=o_id))
    sr.p = True
    sr.pdt = datetime.utcnow()
    db.session.delete(cs)
    db.session.add(sr)
    db.session.commit()
    flash(get_lang(26), "info")
    return redirect(url_for("manage_app.offices", o_id=o_id))


@core.route('/feed', methods=['GET'])
def feed():
    # Checking if autorefreash is due and do it
    autoref = None
    if session.get('autoref') == 1:
        autoref = 1
        session['autoref'] = None
    hl = []
    co = data.Waiting_c.query.first()
    if co is None:
        con = "Empty"
        cot = "Empty"
        cott = "Empty"
    else:
        con = co.oname
        cott = co.tname
        if co.n:
            cot = co.name
        else:
            cot = co.ticket
    if data.Serial.query.count() <= 1:
        return redirect(url_for("core.touch", a=1))
    c = 0
    for s in data.Waiting.query.order_by(data.Waiting.id):
        c += 1
        cs = str(c) + ". "
        prf = data.Office.query.filter_by(id=s.office_id).first().prefix
        if s.n:
            bap = (prf).encode('utf-8') + "."
            bap += (s.name).encode('utf-8')
            hl.append(cs.encode('utf-8') + bap)
        else:
            hl.append(cs + prf + str(s.number))
    for a in range(len(hl), 8):
        hl.append("Empty")
    # fixing identical changes bug
    hcounter = data.Waiting.query.order_by(data.Waiting.id).first()
    if hcounter is not None:
        hcounter = hcounter.number
    else:
        hcounter = "Empty"
    # End of fix
    f = data.Display_store.query.filter_by(id=0).first()
    if f.announce != "false" and f.afile != " ":
        af = f.afile
    else:
        af = "Empty"
    return jsonify(con=con, cot=cot, cott=cott,
                   w1=hl[0], w2=hl[1], w3=hl[2],
                   w4=hl[3], w5=hl[4], w6=hl[5],
                   w7=hl[6], w8=hl[7],
                   w9=hcounter, anf=af, refre=autoref)


@core.route('/display')
@login_required
def display():
    ts = data.Display_store.query.first()
    sli = data.Slides_c.query.first()
    ex_functions.mse()
    if data.Slides.query.count() > 0:
        ss = data.Slides.query.order_by(data.Slides.id.desc())
    else:
        ss = None
    if data.Display_store.query.first().audio == "true":
        audio = 1
    else:
        audio = 0
    if data.Display_store.query.first().announce != "false":
        audio_2 = 1
    else:
        audio_2 = 0
    return render_template("display.html",
                           ss=ss, sli=sli, audio=audio,
                           audio_2=audio_2, ts=ts,
                           slides=data.Slides.query,
                           tv=ts.tmp,
                           ptitle="Display Screen",
                           anr=ts.anr,
                           vid=data.Vid.query.first())


@core.route('/touch/<int:a>')
@login_required
def touch(a):
    if a != 0 and a != 1:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('core.root'))
    d = False
    if a == 1:
        d = True
    form = forms.Touch_name()
    if session.get('lang') == "AR":
        form = forms.Touch_name_ar()
    ex_functions.mse()
    ts = data.Touch_store.query.filter_by(id=0).first()
    if data.Task.query.count() > 0:
        t = data.Task.query.order_by(data.Task.timestamp)
    else:
        t = 0
    return render_template("touch.html",
                           ts=ts, tasks=t,
                           ptitle="Touch Screen",
                           form=form, a=ts.tmp, d=d)
