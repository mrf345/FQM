# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import url_for, flash, request, render_template
from flask import redirect, Markup, session, send_file, Blueprint
from flask_login import current_user, login_required
from flask_login import login_user, logout_user
from datetime import datetime
import forms
import data
from database import db, login_manager
import csv
from ex_functions import get_lang, r_path


administrate = Blueprint('administrate', __name__)


@login_manager.user_loader
def load_user(user_id):
    return data.User.query.get(int(user_id))


@administrate.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


@login_manager.unauthorized_handler
def unauthorized_callback():
    session['next_url'] = request.path
    flash(get_lang(59), 'danger')
    return redirect(url_for("core.root", n='b'))


@administrate.route('/admin_u', methods=['GET', 'POST'])
@login_required
def admin_u():
    if current_user.id != 1:
        flash(get_lang(1), 'danger')
        return redirect(url_for('core.root'))
    form = forms.U_admin(session.get('lang'))
    admin = data.User.query.filter_by(id=1).first()
    if form.validate_on_submit():
        admin.password = form.password.data
        db.session.commit()
        flash(get_lang(2), 'info')
        return redirect(url_for('administrate.logout'))
    return render_template('admin_u.html',
                           navbar='#snb3',
                           ptitle="Updating Admin Password",
                           form=form)


@administrate.route('/csvd/<t_name>', methods=['GET', 'POST'])
@login_required
def csvd(t_name):
    if current_user.role_id != 1:
        flash(get_lang(0),
              'danger')
        return redirect(url_for('core.root'))
    form = forms.CSV(session.get('lang'))
    t_ids = ['User', 'Office', 'Task', 'Serial',
                     'Waiting', 'Roles']
    if t_name in t_ids:
        t_name = eval('data.' + t_name)
        fn = 'csvd.csv'
        ffn = r_path(fn)
        of = open(ffn, 'w+')
        outcsv = csv.writer(of)
        outcsv.writerow([column.name
                         for column in t_name.__mapper__.columns
                         if column.name != 'password_hash'])
        [outcsv.writerow([getattr(curr, column.name)
                          for column in t_name.__mapper__.columns
                          if column.name != 'password_hash'])
         for curr in t_name.query.all()]
        of.close()
        return send_file(ffn, mimetype='csv',
                         as_attachment=True)
    elif t_name != '0':
        flash(get_lang(4),
              'danger')
        return redirect(url_for('core.root'))
    if form.validate_on_submit():
        return redirect(url_for('administrate.csvd',
                                t_name=form.table.data))
    return render_template('csvs.html',
                           navbar='#snb3',
                           ptitle='Export CSV',
                           form=form)


@administrate.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('root'))
    page = request.args.get('page', 1, type=int)
    if page > int(data.User.query.count() / 10) + 1:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('administrate.users'))
    pagination = data.User.query.paginate(page, per_page=10,
                                          error_out=False)
    return render_template('users.html',
                           ptitle='All users',
                           navbar='#snb3',
                           len=len,
                           offices=data.Office.query,
                           pagination=pagination,
                           usersp=pagination.items,
                           operators=data.Operators.query,
                           users=data.User.query)


@administrate.route('/operators/<int:t_id>', methods=['GET', 'POST'])
@login_required
def operators(t_id):
    office = data.Office.query.filter_by(id=t_id).first()
    if office is None:
        flash(get_lang(4),
              "danger")
        return redirect(url_for('root'))
    if current_user.role_id == 3 and data.Operators.query.filter_by(id=current_user.id).first() is None :
        flash(get_lang(0),
              "danger")
        return redirect(url_for('root'))
    page = request.args.get('page', 1, type=int)
    if page > int(data.Operators.query.count() / 10) + 1:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('manage.office', o_id=t_id))
    pagination = data.Operators.query.filter_by(office_id=t_id).paginate(page, per_page=10,
                                          error_out=False)
    return render_template('operators.html',
                           ptitle=str(office.name) + ' operators',
                           len=len,
                           offices=data.Office.query,
                           pagination=pagination,
                           usersp=pagination.items,
                           serial=data.Serial.query,
                           users=data.User.query,
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar="#snb1",
                           dropdown="#dropdown-lvl" + str(t_id),
                           hash="#to" + str(t_id))


@administrate.route('/user_a', methods=['GET', 'POST'])
@login_required
def user_a():
    if current_user.role_id != 1:
        flash(get_lang(4),
              "danger")
        return redirect(url_for('core.root'))
    form = forms.User_a(session.get('lang'))
    if form.validate_on_submit():
        if data.User.query.filter_by(name=form.name.data).first() is not None:
            flash(get_lang(5),
                  "danger")
            return redirect(url_for('administrate.user_a'))
        db.session.add(data.User(form.name.data,
                                 form.password.data,
                                 form.role.data))
        db.session.commit()
        # Fix: multiple operators for office
        # adding user to Operators list
        if form.role.data == 3:
            db.session.add(data.Operators(
                data.User.query.filter_by(name=form.name.data).first().id,
                form.offices.data
            ))
            db.session.commit()
        flash(get_lang(6),
              "info")
        return redirect(url_for('administrate.users'))
    return render_template('user_add.html',
                           form=form, navbar='#snb3',
                           ptitle='Add user')


@administrate.route('/user_u/<int:u_id>', methods=['GET', 'POST'])
@login_required
def user_u(u_id):
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    form = forms.User_a(session.get('lang'))
    u = data.User.query.filter_by(id=u_id).first()
    if u is None:
        flash(get_lang(7),
              "danger")
        return redirect(url_for("core.root"))
    if u.id == 1:
        flash(get_lang(8),
              "danger")
        return redirect(url_for("administrate.users"))
    if form.validate_on_submit():
        u.name = form.name.data
        u.password = form.password.data
        u.role_id = form.role.data
        # Remove operator if role has changed
        if form.role.data == 3:
            if data.Operators.query.filter_by(id=u.id).first() is None:
                db.session.add(data.Operators(
                    u.id,
                    form.offices.data
                ))
        else:
            toRemove = data.Operators.query.filter_by(id=u.id).first()
            if toRemove is not None:
                db.session.delete(toRemove)
        db.session.commit()
        flash(get_lang(10),
              "info")
        return redirect(url_for('administrate.users'))
    if not form.errors:
        form.name.data = u.name
        form.role.data = u.role_id
        # Fix: multiple operators for office
        # fetch office id if operator
        if u.role_id == 3:
            form.offices.data = data.Operators.query.filter_by(id=u.id).first().office_id
    return render_template('user_add.html',
                           form=form, navbar='#snb3',
                           ptitle='Update user : ' + u.name,
                           u=u, update=True)


@administrate.route('/user_d/<int:u_id>')
@login_required
def user_d(u_id):
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    u = data.User.query.filter_by(id=u_id).first()
    if u is None:
        flash(get_lang(7),
              "danger")
        return redirect(url_for("core.root"))
    if u.id == 1:
        flash(get_lang(8),
              "danger")
        return redirect(url_for("administrate.users"))
    # delete from operators if user is operator
    if u.role_id == 3:
        db.session.delete(data.Operators.query.filter_by(id=u.id).first())
    db.session.delete(u)
    db.session.commit()
    flash(get_lang(11),
          "info")
    return redirect(url_for('administrate.users'))


@administrate.route('/user_da')
@login_required
def user_da():
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    for u in data.User.query:
        # Fix: multiple operators for office
        # ofc = data.Office.query.filter_by(operator_id=u.id).first()
        if u.role_id == 3:
            opt = data.Operators.query.filter_by(id=u.id).first()
            if opt:
                db.session.delete(opt)
        if u.id != 1:
            db.session.delete(u)
    db.session.commit()
    flash(get_lang(12),
          "info")
    return redirect(url_for('administrate.users'))


@administrate.route('/logout')
@login_required
def logout():
    if not current_user.is_authenticated:
        flash(get_lang(13), "danger")
        return redirect(url_for("core.root"))
    logout_user()
    flash(get_lang(14), "info")
    return redirect(url_for("core.root"))
