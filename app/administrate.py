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
    form = forms.U_admin()
    if session.get('lang') == "AR":
        form = forms.U_admin_ar()
    admin = data.User.query.filter_by(id=1).first()
    if form.validate_on_submit():
        admin.password = form.password.data
        db.session.commit()
        flash(get_lang(2), 'info')
        return redirect(url_for('administrate.logout'))
    return render_template('admin_u.html',
                           snb='#snb3',
                           ptitle="Updating Admin Password",
                           form=form)


@administrate.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role_id != 1:
        flash(get_lang(0), 'danger')
        return redirect(url_for('core.root'))
    form = forms.Settings_f()
    if session.get('lang') == 'AR':
        form = forms.Settings_f_ar()
    ddb = data.Settings.query.first()
    if form.validate_on_submit():
        ddb.ar_d = int(form.ar_d.data) * 1000
        db.session.commit()
        flash(get_lang(3), 'info')
        return redirect(url_for('administrate.settings'))
    form.ar_d.data = ddb.ar_d / 1000
    return render_template('settings.html',
                           snb='#snb3',
                           ptitle="Autoreload druation",
                           form=form)


@administrate.route('/csvd/<t_name>', methods=['GET', 'POST'])
@login_required
def csvd(t_name):
    if current_user.role_id != 1:
        flash(get_lang(0),
              'danger')
        return redirect(url_for('core.root'))
    form = forms.CSV()
    if session.get('lang') == "AR":
        form = forms.CSV_ar()
    t_ids = ['User', 'Office', 'Task', 'Serial',
                     'Waiting', 'Roles']
    if t_name in t_ids:
        t_name = eval('data.' + t_name)
        fn = 'csvd.csv'
        ffn = r_path(fn)
        of = open(ffn, 'wb')
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
                           snb='#snb3',
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
                           snb='#snb3',
                           len=len,
                           offices=data.Office.query,
                           pagination=pagination,
                           usersp=pagination.items,
                           brp=Markup("<br>"),
                           users=data.User.query)


@administrate.route('/user_a', methods=['GET', 'POST'])
@login_required
def user_a():
    if current_user.role_id != 1:
        flash(get_lang(4),
              "danger")
        return redirect(url_for('core.root'))
    form = forms.User_a()
    if session.get('lang') == "AR":
        form = forms.User_a_ar()
    if form.validate_on_submit():
        if data.User.query.filter_by(name=form.name.data).first() is not None:
            flash(get_lang(5),
                  "danger")
            return redirect(url_for('administrate.user_a'))
        db.session.add(data.User(form.name.data,
                                 form.password.data,
                                 form.role.data))
        db.session.commit()
        flash(get_lang(6),
              "info")
        return redirect(url_for('administrate.users'))
    return render_template('user_add.html',
                           form=form, snb='#snb3',
                           ptitle='Add user')


@administrate.route('/user_u/<int:u_id>', methods=['GET', 'POST'])
@login_required
def user_u(u_id):
    if current_user.role_id != 1 and current_user.id != u_id:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    form = forms.User_a()
    if session.get('lang') == "AR":
        form = forms.User_a_ar()
    u = data.User.query.filter_by(id=u_id).first()
    if u is None:
        flash(get_lang(7),
              "danger")
        return redirect(url_for("core.root"))
    if u.id == 1:
        flash(get_lang(8),
              "danger")
        return redirect(url_for("administrate.users"))
    if data.Office.query.filter_by(operator_id=u.id).first() is not None:
        flash(get_lang(9),
              "danger")
        return redirect(url_for("administrate.users"))
    if form.validate_on_submit():
        u.name = form.name.data
        u.password = form.password.data
        u.role_id = form.role.data
        db.session.commit()
        flash(get_lang(10),
              "info")
        return redirect(url_for('administrate.users'))
    form.name.data = u.name
    form.role.data = u.role_id
    return render_template('user_update.html',
                           form=form, snb='#snb3',
                           ptitle='Update user : ' + u.name,
                           u=u)


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
    if data.Office.query.filter_by(operator_id=u.id).first() is not None:
        flash(get_lang(9),
              "danger")
        return redirect(url_for("administrate.users"))
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
        ofc = data.Office.query.filter_by(operator_id=u.id).first()
        if u.id != 1 and ofc is None:
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
