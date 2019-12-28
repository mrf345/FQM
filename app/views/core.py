# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from random import choice
from sys import platform
from datetime import datetime
from flask import url_for, flash, render_template, redirect, session, jsonify, Blueprint, current_app
from flask_login import current_user, login_required, login_user

import app.forms as forms
import app.database as data
from app.printer import (
    assign, printit, printit_ar, print_ticket_windows, print_ticket_windows_ar,
    get_windows_printers)
from app.middleware import db
from app.helpers import reject_no_offices, reject_operator, is_operator, reject_not_admin


core = Blueprint('core', __name__)


@core.route('/', methods=['GET', 'POST'])
@core.route('/log/<n>', methods=['GET', 'POST'])
def root(n=None):
    """ the index and login view """
    b = None
    form = forms.Login(session.get('lang'))
    if n is not None and n == 'a':
        n = True
    elif n is not None and n == 'b':
        b = True
    elif n is None:
        n = False
    else:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for('core.root'))
    if data.User.query.first() is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for('core.root'))
    # Check if default password and account
    dpass = False
    if data.User.query.filter_by(id=1).first().verify_password('admin'):
        dpass = True
    if form.validate_on_submit():
        if current_user.is_authenticated:
            flash('Error: wrong entry, something went wrong',
                  'danger')
            return redirect(url_for('core.root'))
        user = data.User.query.filter_by(name=form.name.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                if form.rm.data:
                    login_user(user, remember=True)
                else:
                    login_user(user)
                flash("Notice: logged-in and all good", 'info')
                if b:
                    s = str(session.get('next_url', '/'))
                    session['next_url'] = None
                    return redirect(s)
                else:
                    if is_operator():
                        return redirect(
                            url_for(
                                'manage_app.offices',
                                o_id=data.Operators.query.filter_by(id=current_user.id).first().office_id
                                ))
                    else:
                        return redirect(url_for('manage_app.manage'))
            flash(
                "Error: wrong user name or password",
                'danger')
            return redirect(url_for("core.root", n='a'))
        flash(
            "Error: wrong user name or password",
            'danger')
        return redirect(url_for("core.root", n='a'))
    return render_template("index.html", operators=data.Operators.query,
                           page_title="Free Queue Manager",
                           form=form, n=n, dpass=dpass)


@core.route('/serial/<int:t_id>', methods=['POST', 'GET'])
def serial(t_id):
    """ to generate a new ticket and print it """
    form = forms.Touch_name(session.get('lang'))
    tsk = data.Task.query.filter_by(id=t_id).first()
    if tsk is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("core.root"))
    # if it is registered ticket, will display the form and valuate it
    if not form.validate_on_submit() and data.Touch_store.query.first().n:
        ts = data.Touch_store.query.filter_by(id=0).first()
        tnumber = False
        if data.Printer.query.first().value == 2:
            tnumber = True
        return render_template("touch.html", title=ts.title, tnumber=tnumber,
                               ts=ts, done=False, bgcolor=ts.bgcolor,
                               page_title="Touch Screen - Enter name ",
                               alias=data.Aliases.query.first(),
                               a=4, dire='multimedia/', form=form)
    nm = form.name.data
    n = True if data.Touch_store.query.first().n else False

    # FIX: limit the tickets to the range of waitting tickets, prevent overflow.
    # Assigning the first office in the list
    offices_ids = [o.id for o in data.Task.query.filter_by(id=t_id).first().offices]

    # FIX: to manage racing condition in generating a new number, when overloaded.
    def current_ticket():
        return data.Serial.query.filter(data.Serial.office_id.in_(offices_ids))\
                                .order_by(data.Serial.timestamp.desc())\
                                .first()

    o_id = choice(offices_ids) if len(offices_ids) > 1 else current_ticket().office_id

    if data.Serial.query.filter_by(number=current_ticket().number + 1, office_id=o_id).first() is None:
        if n:  # registered
            db.session.add(data.Serial(current_ticket().number + 1, o_id, t_id, nm, True))
            db.session.commit()
        else:  # printed
            db.session.add(data.Serial(current_ticket().number + 1, o_id, t_id, None, False))
            db.session.commit()
            # adding printer support
            q = data.Printer.query.first()
            ppt = data.Task.query.filter_by(id=t_id).first()
            oot = data.Office.query.filter_by(id=o_id).first()
            tnum = data.Serial.query.filter_by(office_id=o_id, p=False).count()
            cuticket = data.Serial.query.filter_by(office_id=o_id, p=False).first()
            tnum -= 1
            langu = data.Printer.query.first().langu
            # to solve Linux printer permissions
            if os.name == 'nt':
                if get_windows_printers():
                    if langu == 'ar':
                        print_ticket_windows_ar(
                            q.product,
                            oot.prefix + '.' + str(current_ticket().number + 1),
                            oot.prefix + str(oot.name),
                            tnum, ppt.name,
                            oot.prefix + '.' + str(cuticket.number),
                            ip=current_app.config['LOCALADDR'])
                    else:
                        print_ticket_windows(
                            q.product,
                            oot.prefix + '.' + str(current_ticket().number + 1),
                            oot.prefix + str(oot.name),
                            tnum, ppt.name,
                            oot.prefix + '.' + str(cuticket.number), l=langu,
                            ip=current_app.config['LOCALADDR'])
                    p = True
                else:
                    p = None
            else:
                # To Fix 1: Fail safe drivers. [FIXED]
                try:
                    p = assign(int(q.vendor), int(q.product),
                               int(q.in_ep), int(q.out_ep))
                except Exception:
                    p = None
            if p is None:
                flash('Error: you must have available printer, to use printed',
                      'danger')
                flash("Notice: make sure that printer is properly connected",
                      'info')
                if os.name == 'nt':
                    flash(
                        "Notice: Make sure to make the printer shared on the local network",
                        'info')
                elif platform == "linux" or platform == "linux2":
                    flash(
                        "Notice: Make sure to execute the command `sudo gpasswd -a $(users) lp` and reboot the system",
                        'info')
                return redirect(url_for('cust_app.ticket'))
            if os.name != 'nt':
                if langu == 'ar':
                    printit_ar(
                        p,
                        oot.prefix + '.' + str(current_ticket().number + 1),
                        oot.prefix + str(oot.name),
                        tnum, u'' + ppt.name,
                        oot.prefix + '.' + str(cuticket.number))
                else:
                    printit(
                        p,
                        oot.prefix + '.' + str(current_ticket().number + 1),
                        oot.prefix + str(oot.name),
                        tnum, u'' + ppt.name,
                        oot.prefix + '.' + str(cuticket.number), lang=langu)
    else:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for('core.root'))

    # FIX: limit the tickets to the range of waitting tickets, prevent overflow.
    limited_tickets = data.Serial.query.filter_by(p=False)\
                                       .order_by(data.Serial.timestamp)\
                                       .limit(11)

    for a in range(data.Waiting.query.count(), 11):
        for b in limited_tickets.all():
            if data.Waiting.query.filter_by(office_id=b.office_id,
                                            number=b.number, task_id=b.task_id
                                            ).first() is None:
                db.session.add(data.Waiting(b.number, b.office_id, b.task_id, nm, n))
    db.session.commit()
    return redirect(url_for("core.touch", a=1))


@core.route('/serial_r/<int:o_id>')
@login_required
def serial_r(o_id):
    """ to reset an office by removing its tickets """
    operator = is_operator()

    if data.Office.query.filter_by(id=o_id).first() is None:
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for("manage_app.all_offices"))
    if operator and data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if operator and o_id != data.Operators.query.filter_by(id=current_user.id).first().office_id:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if data.Serial.query.filter_by(office_id=o_id).first() is None:
        flash("Error: the office is already resetted",
              'danger')
        return redirect(url_for("manage_app.offices", o_id=o_id))
    for f in data.Serial.query.filter(data.Serial.office_id == o_id, data.Serial.number != 100):
        data.Waiting.query.filter_by(office_id=f.office_id, number=f.number).delete()

    # NOTE: Queries has to be written fully everytime to avoid sqlalchemy racing condition
    if operator:
        # Prevent operators from deleteing common tasks tickets
        for ticket in data.Serial.query.filter_by(office_id=o_id):
            task = data.Task.query.filter_by(id=ticket.task_id).first()
            query = data.Serial.query.filter(data.Serial.office_id == o_id)

            if len(task.offices) > 1:
                query = query.filter(data.Serial.task_id != task.id)

            query.delete()
    else:
        data.Serial.query.filter_by(office_id=o_id).delete()
    db.session.commit()
    flash("Notice: office has been resetted. ..",
          'info')
    return redirect(url_for("manage_app.offices", o_id=o_id))


@core.route('/serial_ra')
@login_required
@reject_operator
@reject_no_offices
def serial_ra():
    """ to reset all offices by removing all tickets """
    sr = data.Serial.query.filter(data.Serial.number != 100)
    if sr.first() is None:
        flash("Error: the office is already resetted",
              'danger')
        return redirect(url_for("manage_app.all_offices"))
    for f in sr:
        w = data.Waiting.query.filter_by(office_id=f.office_id,
                                         number=f.number).first()
        db.session.delete(f)
        if w is not None:
            db.session.delete(w)
    db.session.commit()
    flash("Notice: office has been resetted. ..",
          'info')
    return redirect(url_for("manage_app.all_offices"))


@core.route('/serial_rt/<int:t_id>', defaults={'ofc_id': None})
@core.route('/serial_rt/<int:t_id>/<int:ofc_id>')
@login_required
def serial_rt(t_id, ofc_id=None):
    """ to reset a task by removing its tickets """
    task = data.Task.query.filter_by(id=t_id).first()

    if task is None:
        flash("Error: No tasks exist to be resetted", 'danger')
        return redirect(url_for("manage_app.all_offices"))
    if is_operator() and data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))

    office_ids = [o.id for o in data.Task.query.filter_by(id=t_id).first().offices]
    if is_operator() and any([
        len(office_ids) > 1,
        ofc_id not in office_ids,
        data.Operators.query.filter_by(id=current_user.id).first().office_id != ofc_id
    ]):
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if data.Serial.query.filter(data.Serial.task_id == t_id, data.Serial.number != 100).first() is None:
        flash("Error: the task is already resetted",
              'danger')
        return redirect(url_for("manage_app.task", o_id=t_id))
    for f in data.Serial.query.filter(data.Serial.task_id == t_id, data.Serial.number != 100):
        w = data.Waiting.query.filter_by(office_id=f.office_id,
                                         number=f.number).first()
        db.session.delete(f)
        if w is not None:
            db.session.delete(w)
    db.session.commit()
    flash("Error: the task is already resetted",
          'info')
    return redirect(url_for("manage_app.task", o_id=t_id, ofc_id=ofc_id))


@core.route('/pull', defaults={'o_id': None, 'ofc_id': None})
@core.route('/pull/<int:o_id>/<int:ofc_id>')
@login_required
def pull(o_id=None, ofc_id=None):
    """ to change the state of a ticket to be pulled """
    # FIX: pulling tickets by task_id instead of office_id
    # to allow for pulling form specific office
    if o_id is not None:
        if data.Task.query.filter_by(id=o_id).first() is None:
            flash('Error: wrong entry, something went wrong', 'danger')
            return redirect(url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))
    if is_operator() and data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if o_id is not None:
        if is_operator() and data.Operators.query.filter_by(id=current_user.id).first().office_id not in\
                [o.id for o in data.Task.query.filter_by(id=o_id).first().offices]:
            flash("Error: operators are not allowed to access the page ", 'danger')
            return redirect(url_for('core.root'))
    else:
        if is_operator():
            flash("Error: operators are not allowed to access the page ", 'danger')
            return redirect(url_for('core.root'))
    # Loading up the 10 waiting list
    # FIX: limit the tickets to the range of waitting tickets, prevent overflow.
    limited_tickets = data.Serial.query.filter_by(p=False)\
                                       .order_by(data.Serial.timestamp)\
                                       .limit(11)
    if data.Serial.query.filter_by(p=False).count() >= 0:
        for a in range(data.Waiting.query.count(), 11):
            for b in limited_tickets.all():
                if data.Waiting.query.filter_by(office_id=b.office_id,
                                                number=b.number,
                                                task_id=b.task_id
                                                ).first() is None:
                    db.session.add(data.Waiting(b.number, b.office_id,
                                                b.task_id, b.name, b.n))
        db.session.commit()
    else:
        flash(
            "Error: no tickets left to pull from ..",
            'danger')
        return redirect(url_for('manage_app.all_offices') if o_id is None else url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))
    # Setting the office in case it's not pull from all
    # The goal is to specify the exact office responsible for the pull
    # and update the about to be pulled tickets with responsible office
    if ofc_id is not None and o_id is not None:
        if len(data.Task.query.filter_by(id=o_id).first().offices) > 1:
            for record in [data.Serial, data.Waiting]:
                record = record.query.filter_by(task_id=o_id).first()
                if record is not None:
                    if data.Office.query.filter_by(id=ofc_id).first() is not None:
                        record.office_id = ofc_id
                        db.session.commit()
                    else:
                        flash("Error: office used to pull is non existing", 'danger')
                        return redirect(url_for("core_app.root"))
    cs = data.Waiting.query.all() if o_id is None else data.Waiting.query.filter_by(task_id=o_id, office_id=ofc_id).first()
    if cs is None:
        flash(
            "Error: no tickets left to pull from ..",
            'danger')
        return redirect(url_for('manage_app.all_offices') if o_id is None else url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))
    # Fix: pulling tickets by task_id instead of office_id
    # have to switch positions
    # --- Reassigning cs seems to fix it
    # Fix: pulling tickets by task_id instead of office_id
    # modifying removing from  waiting with task_id 
    cs = data.Waiting.query.filter_by(**({'task_id': o_id, 'office_id': ofc_id} if o_id is not None else {})).first()
    if cs is None:
        flash("Error: no tickets left to pull from ..", 'danger')
        return redirect(url_for('manage_app.all_offices') if o_id is None else url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))
    # adding to current waiting
    pIt = data.Display_store.query.first().prefix
    ocs = data.Office.query.filter_by(id=cs.office_id).first()
    cl = data.Waiting_c.query.first()
    cl.ticket = (ocs.prefix if pIt else '') + str(cs.number)
    cl.oname = (ocs.prefix if pIt else '') + str(ocs.name)
    cl.tname = data.Task.query.filter_by(id=cs.task_id).first().name
    cl.n = cs.n
    cl.name = cs.name
    db.session.commit()

    next_ticket = data.Serial.query.order_by(data.Serial.timestamp)\
                                   .filter(data.Serial.number != 100,
                                           data.Serial.p != True)

    if o_id:
        next_ticket = next_ticket.filter(data.Serial.task_id == cs.task_id)

    if ofc_id:
        next_ticket = next_ticket.filter(data.Serial.office_id == cs.office_id)

    next_ticket = next_ticket.first()

    if not next_ticket:
        flash("Error: no tickets left to pull from ..", 'danger')
        return redirect(url_for('manage_app.all_offices') if o_id is None else url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))

    next_ticket.p = True
    next_ticket.pdt = datetime.utcnow()
    next_ticket.pulledBy = getattr(current_user, 'id', None)

    db.session.add(next_ticket)
    db.session.delete(cs)
    db.session.commit()
    flash("Notice: Ticket has been pulled ..", 'info')
    return redirect(url_for('manage_app.all_offices') if o_id is None else url_for("manage_app.task", **({'ofc_id': ofc_id, 'o_id': o_id} if ofc_id else {'o_id': o_id})))


@core.route('/feed', methods=['GET'], defaults={'disable': None})
@core.route('/feed/<int:disable>', methods=['GET'])
def feed(disable=None):
    """ to send a json stream of the current tickets """
    toMod = data.Display_store.query.first()
    if disable:
        toMod.r_announcement = False
        db.session.add(toMod)
        db.session.commit()
        return 'success'
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
    # FIX: after overlading with 1500+ tickets querying without limit,
    # will overflow the server causing it to crash miserably 🤦‍♂️
    for s in data.Waiting.query.order_by(data.Waiting.id).limit(11):
        c += 1
        cs = str(c) + ". "
        prf = data.Office.query.filter_by(id=s.office_id).first().prefix
        pIt = data.Display_store.query.first().prefix
        if s.n:
            hl.append(f'{cs}{(prf + ".") if pIt else ""}{s.name}')
        else:
            hl.append(f'{cs}{(prf if pIt else "")}{s.number}')
    for a in range(len(hl), 8):
        hl.append("Empty")
    # fixing identical changes bug
    # adding intended modification in case of recal 
    hcounter = co.ticket if co else data.Waiting.query.order_by(data.Waiting.id).first()
    hcounter = hcounter.number if not co and hcounter is not None else "Empty"
    # End of fix
    # ensure unique val to instigate renouncement, with emptying session 
    return jsonify(con=con, cot=cot, cott=cott,
                   w1=hl[0], w2=hl[1], w3=hl[2],
                   w4=hl[3], w5=hl[4], w6=hl[5],
                   w7=hl[6], w8=hl[7], w9=hcounter,
                   replay='yes' if toMod.r_announcement else 'no')


@core.route('/rean', methods=['POST'])
def rean():
    """ to set receive $.post json and activate re-announcement """
    if current_user.is_authenticated:
        toMod = data.Display_store.query.first()
        toMod.r_announcement = True
        db.session.add(toMod)
        db.session.commit()
        return 'success'
    else:
        return 'fail'


@core.route('/display')
def display():
    """ the display screen view """
    ts = data.Display_store.query.first()
    sli = data.Slides_c.query.first()
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
                           page_title="Display Screen",
                           anr=ts.anr,
                           alias=data.Aliases.query.first(),
                           vid=data.Vid.query.first())


@core.route('/touch/<int:a>')
def touch(a):
    """ the touch screen view """
    d = False
    if a == 1:
        d = True
    form = forms.Touch_name()
    if session.get('lang') == "AR":
        form = forms.Touch_name_ar()
    ts = data.Touch_store.query.filter_by(id=0).first()
    if data.Task.query.count() > 0:
        t = data.Task.query.order_by(data.Task.timestamp)
    else:
        t = 0
    tnumber = False
    if data.Printer.query.first().value == 2:
        tnumber = True
    return render_template("touch.html",
                           ts=ts, tasks=t, tnumber=tnumber,
                           page_title="Touch Screen",
                           alias=data.Aliases.query.first(),
                           form=form, a=ts.tmp, d=d)


@core.route('/notifications/<togo>')
@login_required
@reject_not_admin
def notifications(togo):
    """ to toggle the front-end notifications """
    settings = data.Settings.query.filter_by(id=0).first()
    if settings is not None:
        settings.notifications = False if settings.notifications else True
        db.session.add(settings)
        db.session.commit()
        flash("Notice: Notification got " + (
            "Enabled" if settings.notifications else "Disabled"
        ) + " successfully", 'info')
    else:
        flash("Error: Failed to find settings in the database", 'danger')
    return redirect(togo.replace('(', '/'))
