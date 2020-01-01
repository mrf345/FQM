# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from csv import DictWriter
from flask import url_for, flash, request, render_template, redirect, session, send_file, Blueprint
from flask_login import current_user, login_required, logout_user
from datetime import datetime

import app.database as data
from app.middleware import db, login_manager
import app.forms as forms
from app.utils import absolute_path, get_module_columns, get_module_values
from app.helpers import reject_not_god, reject_not_admin, reject_god


administrate = Blueprint('administrate', __name__)


@login_manager.user_loader
def load_user(user_id):
    ''' getting the current user '''
    return data.User.query.get(int(user_id))


@administrate.before_request
def update_last_seen():
    ''' adding the last time user logged in '''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


@login_manager.unauthorized_handler
def unauthorized_callback():
    ''' if user not logged in '''
    session['next_url'] = request.path

    flash('Error: login is required to access the page', 'danger')
    return redirect(url_for('core.root', n='b'))


@administrate.route('/admin_u', methods=['GET', 'POST'])
@login_required
@reject_not_god
def admin_u():
    ''' updating main admin account password '''
    form = forms.U_admin(session.get('lang'))
    admin = data.User.get(1)

    if form.validate_on_submit():
        admin.password = form.password.data

        db.session.commit()
        flash('Notice: admin password has been updated.', 'info')
        return redirect(url_for('administrate.logout'))

    return render_template('admin_u.html',
                           navbar='#snb3',
                           page_title='Updating Admin Password',
                           form=form)


@administrate.route('/csv', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def csv():
    ''' to export tables to `.csv` file '''
    form = forms.CSV(session.get('lang'))

    if form.validate_on_submit():
        tabels = [t[0] for t in forms.export_tabels]

        if form.table.data not in tabels:
            flash('Error: wrong entry, something went wrong', 'danger')
            return redirect(url_for('core.root'))

        module = getattr(data, form.table.data, None)
        csv_path = absolute_path(f'csv_{form.table.data}.csv')
        delimiter = forms.export_delimiters[form.delimiter.data]

        with open(csv_path, 'w+') as csv_file:
            fields = get_module_columns(module)
            csv_buffer = DictWriter(csv_file, delimiter=delimiter, fieldnames=fields)
            rows = [
                {fields[i]: value for i, value in enumerate(values)}
                for values in get_module_values(module)
            ]

            form.headers.data and csv_buffer.writeheader()
            csv_buffer.writerows(rows)

        return send_file(csv_path, mimetype='csv', as_attachment=True)

    return render_template('csvs.html',
                           navbar='#snb3',
                           page_title='Export CSV',
                           form=form)


@administrate.route('/users', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def users():
    ''' to list all users '''
    page = request.args.get('page', 1, type=int)
    pagination = data.User.query.paginate(page, per_page=10, error_out=False)

    return render_template('users.html',
                           page_title='All users',
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
    ''' to list operators of an office '''
    office = data.Office.query.filter_by(id=t_id).first()

    if office is None:
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('root'))

    if getattr(current_user, 'role_id', None) == 3 and\
       data.Operators.query.filter_by(id=current_user.id).first() is None:
        flash('Error: only administrator can access the page', 'danger')
        return redirect(url_for('root'))

    page = request.args.get('page', 1, type=int)
    pagination = data.Operators.query.filter_by(office_id=t_id)\
                                     .paginate(page, per_page=10, error_out=False)

    return render_template('operators.html',
                           page_title=str(office.name) + ' operators',
                           len=len,
                           offices=data.Office.query,
                           pagination=pagination,
                           usersp=pagination.items,
                           serial=data.Serial.query,
                           users=data.User.query,
                           tasks=data.Task.query,
                           operators=data.Operators.query,
                           navbar='#snb1',
                           dropdown='#dropdown-lvl' + str(t_id),
                           hash='#to' + str(t_id))


@administrate.route('/user_a', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def user_a():
    ''' to add a user '''
    form = forms.User_a(session.get('lang'))

    if form.validate_on_submit():
        if data.User.query.filter_by(name=form.name.data).first() is not None:
            flash('Error: user name already exists, choose another name',
                  'danger')
            return redirect(url_for('administrate.user_a'))

        db.session.add(data.User(form.name.data, form.password.data, form.role.data))
        db.session.commit()

        # Fix: multiple operators for office
        # adding user to Operators list
        if form.role.data == 3:
            db.session.add(data.Operators(
                data.User.query.filter_by(name=form.name.data).first().id,
                form.offices.data
            ))
            db.session.commit()

        flash('Notice: user has been added .', 'info')
        return redirect(url_for('administrate.users'))

    return render_template('user_add.html',
                           form=form,
                           navbar='#snb3',
                           page_title='Add user',
                           offices_count=data.Office.query.count())


@administrate.route('/user_u/<int:u_id>', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def user_u(u_id):
    ''' to update user '''
    form = forms.User_a(session.get('lang'))
    user = data.User.query.filter_by(id=u_id).first()

    if user is None:
        flash('Error: user selected does not exist, something wrong !', 'danger')
        return redirect(url_for('core.root'))

    if user.id == 1:
        return reject_god(lambda: None)()

    if form.validate_on_submit():
        user.name = form.name.data
        user.password = form.password.data
        user.role_id = form.role.data

        # Remove operator if role has changed
        if form.role.data == 3:
            if data.Office.query.filter_by(id=form.offices.data).first() is None:
                flash('Error: Office selected does not exist!', 'danger')
                return redirect(url_for('core.root'))

            if data.Operators.query.filter_by(id=user.id).first() is None:
                db.session.add(data.Operators(
                    user.id,
                    form.offices.data
                ))
        else:
            to_delete = data.Operators.query.filter_by(id=user.id).first()
            if to_delete is not None:
                db.session.delete(to_delete)

        db.session.commit()
        flash('Notice: user is updated . ', 'info')
        return redirect(url_for('administrate.users'))

    if not form.errors:
        form.name.data = user.name
        form.role.data = user.role_id

        if user.role_id == 3:
            form.offices.data = data.Operators.get(user.id).office_id

    return render_template('user_add.html',
                           form=form, navbar='#snb3',
                           page_title='Update user : ' + user.name,
                           u=user, update=True,
                           offices_count=data.Office.query.count())


@administrate.route('/user_d/<int:u_id>')
@login_required
@reject_not_admin
def user_d(u_id):
    ''' to delete user '''
    user = data.User.query.filter_by(id=u_id).first()

    if user is None:
        flash('Error: user selected does not exist, something wrong !', 'danger')
        return redirect(url_for('core.root'))

    if user.id == 1:
        return reject_god(lambda: None)()

    if user.role_id == 3:
        db.session.delete(data.Operators.get(user.id))
        db.session.commit()

    db.session.delete(user)
    db.session.commit()
    flash('Notice: user is deleted .', 'info')
    return redirect(url_for('administrate.users'))


@administrate.route('/user_da')
@login_required
@reject_not_admin
def user_da():
    ''' to delete all users '''
    for user in data.User.query:
        if user.role_id == 3:
            operator = data.Operators.get(id=user.id)
            operator and db.session.delete(operator)

        if user.id != 1:
            db.session.delete(user)

    db.session.commit()
    flash('Notice: all unassigned users got deleted.', 'info')
    return redirect(url_for('administrate.users'))


@administrate.route('/logout')
@login_required
def logout():
    ''' to logout the current user '''
    if not current_user.is_authenticated:
        flash('Error: you cannot logout without a login !', 'danger')
        return redirect(url_for('core.root'))

    logout_user()
    flash('Notice: logout is done.', 'info')
    return redirect(url_for('core.root'))
