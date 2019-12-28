# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import url_for, flash, request, render_template, redirect
from flask import Blueprint, session
from flask_login import current_user, login_required
from sqlalchemy.sql import and_

import app.forms as forms
import app.database as data
from app.middleware import db
from app.helpers import reject_operator, reject_no_offices, is_operator


manage_app = Blueprint('manage_app', __name__)


@manage_app.route('/manage')
@login_required
def manage():
    """ view for main manage screen """
    ofc = data.Operators.query.filter_by(id=current_user.id).first()
    if is_operator() and ofc is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if ofc is None:
        ofc = 0
    else:
        ofc = ofc.id
    return render_template("manage.html",
                           page_title="Management",
                           navbar="#snb1",
                           ooid=ofc,
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           offices=data.Office.query,
                           operators=data.Operators.query,
                           tasks=data.Task.query)


@manage_app.route('/all_offices')
@login_required
@reject_operator
def all_offices():
    """ lists all offices """
    page = request.args.get('page', 1, type=int)
    tickets = data.Serial.query.filter(data.Serial.number != 100)\
                               .order_by(data.Serial.p, data.Serial.timestamp.desc())
    pagination = tickets.paginate(page, per_page=10, error_out=False)
    last_ticket_pulled = tickets.filter_by(p=True).first()
    last_ticket_office = last_ticket_pulled and data.Office.query\
                                                    .filter_by(id=last_ticket_pulled.office_id)\
                                                    .first()
    return render_template('all_offices.html',
                           officesp=pagination.items,
                           pagination=pagination,
                           len=len,
                           page_title="All Offices",
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           offices=data.Office.query,
                           tasks=data.Task.query,
                           users=data.User.query,
                           operators=data.Operators.query,
                           navbar="#snb1",
                           hash="#da2",
                           last_ticket_pulled=last_ticket_pulled,
                           last_ticket_office=last_ticket_office)


@manage_app.route('/offices/<int:o_id>', methods=['GET', 'POST'])
@login_required
def offices(o_id):
    """ view specific office """
    ofc = data.Office.query.filter_by(id=o_id).first()
    if ofc is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("manage_app.all_offices"))
    if is_operator() and data.Operators.query.filter_by(id=current_user.id, office_id=o_id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    form = forms.Offices_a(upd=ofc.prefix, defLang=session.get('lang'))
    page = request.args.get('page', 1, type=int)
    toGetFrom = data.Serial.query.filter_by(office_id=o_id)
    # To solve tickets from common tasks that are assigned to some other office
    for task in ofc.tasks:
        tickets = data.Serial.query.filter(
            and_(
                data.Serial.task_id == task.id,
                data.Serial.office_id != o_id))
        if tickets.count() > 0:
            toGetFrom = toGetFrom.union(tickets)
    tickets = toGetFrom.filter(data.Serial.number != 100)\
                       .order_by(data.Serial.p)\
                       .order_by(data.Serial.number.desc())
    last_ticket_pulled = tickets.filter_by(p=True).first()
    pagination = tickets.paginate(page, per_page=10, error_out=False)
    if form.validate_on_submit():
        mka = data.Office.query.filter_by(name=form.name.data)
        for f in mka:
            if f.id != o_id:
                flash("Error: name is used by another one, choose another name",
                      'danger')
                return redirect(url_for("manage_app.offices", o_id=o_id))
        ofc.name = form.name.data
        ofc.prefix = form.prefix.data.upper()
        db.session.commit()
        flash("Notice: office has been updated. ",
              'info')
        return redirect(url_for('manage_app.offices', o_id=o_id))
    form.name.data = ofc.name
    form.prefix.data = ofc.prefix.upper()
    return render_template('offices.html',
                           form=form,
                           officesp=pagination.items,
                           pagination=pagination,
                           page_title="Office : " + ofc.prefix + str(ofc.name),
                           o_id=o_id,
                           ooid=ofc,
                           len=len,
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           offices=data.Office.query,
                           tasks=data.Task.query,
                           users=data.User.query,
                           operators=data.Operators.query,
                           navbar="#snb1",
                           dropdown="#dropdown-lvl" + str(o_id),
                           hash="#t1" + str(o_id),
                           last_ticket_pulled=last_ticket_pulled)


@manage_app.route('/office_a', methods=['GET', 'POST'])
@login_required
@reject_operator
def office_a():
    """ to add an office """
    form = forms.Offices_a(defLang=session.get('lang'))
    if form.validate_on_submit():
        if data.Office.query.filter_by(name=form.name.
                                       data).first() is not None:
            flash("Error: name is used by another one, choose another name",
                  'danger')
            return redirect(url_for("manage_app.all_offices"))
        db.session.add(data.Office(form.name.data,
                                   form.prefix.data.upper()))
        db.session.commit()
        flash("Notice: new office been added . ",
              'info')
        return redirect(url_for("manage_app.all_offices"))
    return render_template("office_add.html",
                           form=form,
                           page_title="Adding new office",
                           offices=data.Office.query,
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar="#snb1",
                           hash="#da3",
                           serial=data.Serial.query.filter(data.Serial.number != 100))


@manage_app.route('/office_d/<int:o_id>')
@login_required
@reject_operator
def office_d(o_id):
    """ to delete an office """
    office = data.Office.query.filter_by(id=o_id).first()
    if office is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("manage_app.offices", o_id=o_id))
    if data.Serial.query.filter(and_(data.Serial.office_id == o_id,
                                        data.Serial.number != 100)
                                   ).count() > 0:
        flash("Error: you must reset it, before you delete it ",
              'danger')
        return redirect(url_for("manage_app.offices", o_id=o_id))
    for t in office.tasks:
        db.session.delete(t)
    db.session.delete(office)
    db.session.commit()
    flash("Notice: office and its all tasks been deleted ",
          'info')
    return redirect(url_for("manage_app.all_offices"))


@manage_app.route('/office_da')
@login_required
@reject_operator
@reject_no_offices
def office_da():
    """ to delete all offices """
    if data.Serial.query.filter(data.Serial.number != 100).count():
        flash("Error: you must reset it, before you delete it ",
              'danger')
        return redirect(url_for("manage_app.all_offices"))
    for s in data.Serial.query:
        db.session.delete(s)
    for f in data.Office.query:
        for t in f.tasks:
            db.session.delete(t)
        db.session.delete(f)
    db.session.commit()
    flash("Notice: office and its all tasks been deleted ",
          'info')
    return redirect(url_for("manage_app.all_offices"))


pll = []


@manage_app.route('/search', methods=['GET', 'POST'])
@login_required
@reject_operator
def search():
    """ to search for tickets """
    form = forms.Search_s(session.get('lang'))
    if form.validate_on_submit() or request.args.get("page"):
        from sqlalchemy import text
        from sqlalchemy.sql import and_
        terms = []
        counter = 0
        global pll
        if request.args.get("page"):
            ll = pll
        else:
            ll = [form.number.data, form.date.data, form.tl.data]
            pll = ll
        for l in ll:
            counter += 1
            if l is not None:
                if counter == 1:
                    if len(str(l)) >= 2:
                        terms.append(text("number=" + str(ll[0])))
                elif counter == 2:
                    if len(str(l)) >= 2:
                        terms.append(
                            text("date='" + ll[1].strftime('%Y-%m-%d') + "'"))
                elif counter == 3:
                    if l != 0:
                        terms.append(text("office_id=" + str(ll[2])))
        if len(terms) == 0:
            flash("Error: fault in search parameters",
                  'danger')
            return redirect(url_for("manage_app.search"))
        serials = data.Serial.query.filter(and_(*terms))
        if serials.first() is None or serials.order_by(data.Serial.id.desc()).first() == 100:
            flash(
                "Notice: Sorry, no matching results were found ",
                'info')
            return redirect(url_for("manage_app.search"))
        page = request.args.get('page', 1, type=int)
        pagination = data.Serial.query.filter(and_(*terms), data.Serial.number != 100)\
                                      .order_by(data.Serial.timestamp.desc())\
                                      .paginate(page, per_page=10, error_out=False)
        return render_template("search_r.html",
                               serials=serials,
                               page_title="Tickets search",
                               offices=data.Office.query,
                               tasks=data.Task.query,
                               users=data.User.query,
                               pagination=pagination,
                               serialsp=pagination.items,
                               operators=data.Operators.query,
                               len=len,
                               navbar="#snb1",
                               hash="#da1",
                               serial=data.Serial.query.filter(data.Serial.number != 100))
    return render_template("search.html",
                           form=form,
                           page_title="Tickets search",
                           offices=data.Office.query,
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar="#snb1",
                           hash="#da1",
                           serial=data.Serial.query.filter(data.Serial.number != 100))


@manage_app.route('/task/<int:o_id>', methods=['POST', 'GET'], defaults={'ofc_id': None})
@manage_app.route('/task/<int:o_id>/<int:ofc_id>', methods=['POST', 'GET'])
@login_required
def task(o_id, ofc_id=None):
    """ view for specific task
        now office_id is only optional to /pull and sb_manage, otherwise it will pick the first
        in the task.offices list
    """
    task = data.Task.query.filter_by(id=o_id).first()
    if task is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("core.root"))
    form = forms.Task_a(session.get('lang'), True if len(task.offices) > 1 else False)
    if is_operator() and data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    office_ids = [o.id for o in task.offices]
    if request.method == 'POST' and is_operator() and any([
        len(office_ids) > 1,
        ofc_id not in office_ids,
        data.Operators.query.filter_by(id=current_user.id).first().office_id != ofc_id
    ]):
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    page = request.args.get('page', 1, type=int)
    tickets = data.Serial.query.filter(data.Serial.task_id == o_id, data.Serial.number != 100)\
                               .order_by(data.Serial.timestamp.desc())
    last_ticket_pulled = tickets.filter_by(p=True).first()
    pagination = tickets.paginate(page, per_page=10, error_out=False)
    if form.validate_on_submit():
        mka = data.Task.query.filter_by(name=form.name.data)
        for f in mka:
            if f.id != o_id:
                flash("Error: name is used by another one, choose another name",
                      'danger')
                return redirect(url_for("manage_app.task", o_id=o_id))
        task.name = form.name.data
        if len(task.offices) > 1:
            toValidate = []
            for office in data.Office.query.all():
                if form['check%i' % office.id].data:
                    if office not in task.offices:
                        task.offices.append(office)
                elif form['check%i' % office.id].data is False:
                    if office in task.offices:
                        # Attaching dependent tickets to another common office
                        for ticket in data.Serial.query.filter_by(
                            office_id=office.id).all():
                            ticket.office_id = task.offices[0].id
                        for waiting in data.Waiting.query.filter_by(
                            office_id=office.id).all():
                            waiting.office_id = task.offices[0].id
                        db.session.commit()
                        task.offices.remove(office)
                toValidate.append(form['check%i' % office.id].data)
            if len(toValidate) > 0 and True not in toValidate:
                flash("Error: one office must be selected at least",
                'danger')
                return redirect(url_for("manage_app.common_task_a"))
        db.session.add(task)
        db.session.commit()
        flash("Notice: task has been updated .",
              'info')
        return redirect(url_for("manage_app.task", o_id=o_id))
    if not form.errors:
        form.name.data = task.name
        for office in task.offices:
            form['check%i' % office.id].data = True
    if not ofc_id:
        # to workaround indexing sidebar without rewriting the whole thing
        ofc_id = task.offices[0].id
    return render_template('tasks.html',
                           form=form,
                           page_title="Task : " + task.name,
                           tasksp=pagination.items,
                           pagination=pagination,
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           o_id=o_id,
                           ofc_id=ofc_id,
                           common=True if len(task.offices) > 1 else False,
                           len=len,
                           offices=data.Office.query,
                           tasks=data.Task.query,
                           users=data.User.query,
                           operators=data.Operators.query,
                           task=task,
                           navbar="#snb1",
                           dropdown="#dropdown-lvl%i" % ofc_id, # dropdown a list of offices
                           hash="#tt%i%i" % (ofc_id, o_id),
                           last_ticket_pulled=last_ticket_pulled,
                           edit_task=len(task.offices) == 1 or not is_operator())


@manage_app.route('/task_d/<int:t_id>', defaults={'ofc_id': None})
@manage_app.route('/task_d/<int:t_id>/<int:ofc_id>')
@login_required
def task_d(t_id, ofc_id=None):
    """ to delete a task """
    task = data.Task.query.filter_by(id=t_id).first()

    if task is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("core.root"))

    office_ids = [o.id for o in task.offices]
    if is_operator() and any([
        len(office_ids) > 1,
        ofc_id not in office_ids,
        data.Operators.query.filter_by(id=current_user.id).first().office_id != ofc_id
    ]):
        flash("Error: operators are not allowed to access the page ", 'danger')
        return redirect(url_for('core.root'))
    if data.Serial.query.filter(and_(data.Serial.task_id == t_id,
                                     data.Serial.number != 100)).count() > 0:
        flash("Error: you must reset it, before you delete it ",
              'danger')
        return redirect(url_for("manage_app.task", o_id=t_id))

    evil = data.Serial.query.filter_by(task_id=t_id, number=100).first()
    if evil is not None:
        db.session.delete(evil)
    db.session.delete(data.Task.query.filter_by(id=t_id).first())
    db.session.commit()
    flash("Notice: task has been deleted .",
          'info')
    return redirect(url_for("manage_app.offices", o_id=ofc_id) if ofc_id else url_for("manage_app.all_offices"))


@manage_app.route('/common_task_a', methods=['GET', 'POST'])
@login_required
@reject_operator
def common_task_a():
    """ to add a common task """
    if data.Office.query.count() <= 1:
        flash("Error: not enough offices exist to add a common task",
        'danger')
        return redirect(url_for("manage_app.all_offices"))
    form = forms.Task_a(session.get('lang'), True)
    if form.validate_on_submit():
        task = data.Task(form.name.data)
        if data.Task.query.filter_by(name=form.name.data).first() is not None:
            flash("Error: name is used by another one, choose another name",
                  'danger')
            return redirect(url_for("manage_app.common_task_a"))
        toValidate = []
        for office in data.Office.query.all():
            if form['check%i' % office.id].data and office not in task.offices:
                task.offices.append(office)
            toValidate.append(form['check%i' % office.id].data)
        if len(toValidate) > 0 and True not in toValidate:
            flash("Error: one office must be selected at least",
            'danger')
            return redirect(url_for("manage_app.common_task_a"))
        db.session.add(task)
        db.session.commit()
        flash("Notice: a common task has been added.", 'info')
        return redirect(url_for("manage_app.all_offices"))
    return render_template("task_add.html", form=form,
                           offices=data.Office.query,
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar="#snb1", common=True,
                           page_title="Add a common task",
                           hash="#da6")


@manage_app.route('/task_a/<int:o_id>', methods=['GET', 'POST'])
@login_required
def task_a(o_id):
    """ to add a task """
    form = forms.Task_a(session.get('lang'))
    office = data.Office.query.filter_by(id=o_id).first()
    if office is None:
        flash('Error: wrong entry, something went wrong',
              'danger')
        return redirect(url_for("core.root"))
    if is_operator() and data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if is_operator() and o_id != data.Operators.query.filter_by(id=current_user.id).first().office_id:
        flash("Error: operators are not allowed to access the page ",
              'danger')
        return redirect(url_for('core.root'))
    if form.validate_on_submit():
        if data.Task.query.filter_by(name=form.name.data).first() is not None:
            flash("Error: name is used by another one, choose another name",
                  'danger')
            return redirect(url_for("manage_app.task_a", o_id=o_id))
        task = data.Task(form.name.data)
        task.offices.append(office)
        db.session.add(task)
        db.session.commit()
        flash("Notice: New task been added.", 'info')
        return redirect(url_for("manage_app.offices", o_id=o_id))
    return render_template("task_add.html", form=form,
                           offices=data.Office.query,
                           serial=data.Serial.query.filter(data.Serial.number != 100),
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar="#snb1", common=False,
                           dropdown="#dropdown-lvl" + str(o_id),
                           hash="#t3" + str(o_id),
                           page_title="Add new task")
