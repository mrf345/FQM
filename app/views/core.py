''' This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. '''

import os
from sys import platform
from flask import url_for, flash, render_template, redirect, session, jsonify, Blueprint, current_app
from flask_login import current_user, login_required, login_user

import app.forms as forms
import app.database as data
from app.printer import assign, printit, printit_ar, print_ticket_windows, print_ticket_windows_ar
from app.middleware import db
from app.utils import execute, log_error
from app.helpers import (reject_no_offices, reject_operator, is_operator, reject_not_admin,
                         is_office_operator, is_common_task_operator, refill_waiting_list)


core = Blueprint('core', __name__)


@core.route('/', methods=['GET', 'POST'], defaults={'n': None})
@core.route('/log/<n>', methods=['GET', 'POST'])
def root(n=None):
    ''' welcome view and login. '''
    form = forms.Login(session.get('lang'))
    has_default_password = data.User.has_default_password()
    wrong_credentials = n == 'a'
    should_redirect = n == 'b'

    def logged_in_all_good():
        destination = url_for('manage_app.manage')

        if is_operator():
            destination = url_for('manage_app.offices',
                                  o_id=data.Operators.get(current_user.id).office_id)
        elif should_redirect:
            destination = f'{session.get("next_url", "/")}'
            session['next_url'] = None

        flash('Notice: logged-in and all good', 'info')
        return redirect(destination)

    if form.validate_on_submit():
        if current_user.is_authenticated:
            return logged_in_all_good()

        user = data.User.query.filter_by(name=form.name.data).first()

        if not user or not user.verify_password(form.password.data):
            flash('Error: wrong user name or password', 'danger')
            return redirect(url_for('core.root', n='a'))

        login_user(user, remember=bool(form.rm.data))
        return logged_in_all_good()

    return render_template('index.html', operators=data.Operators.query,
                           page_title='Free Queue Manager', form=form,
                           n=wrong_credentials, dpass=has_default_password)


@core.route('/serial/<int:t_id>', methods=['POST', 'GET'])
@refill_waiting_list
def serial(t_id):
    ''' generate a new ticket and print it. '''
    def printer_failure_redirect(exception):
        flash('Error: you must have available printer, to use printed', 'danger')
        flash('Notice: make sure that printer is properly connected', 'info')

        if os.name == 'nt':
            flash('Notice: Make sure to make the printer shared on the local network', 'info')
        elif 'linux' in platform:
            flash('Notice: Make sure to execute the command `sudo gpasswd -a $(users) lp` and '
                  'reboot the system', 'info')

        log_error(exception)
        return redirect(url_for('core.root'))

    form = forms.Touch_name(session.get('lang'))
    task = data.Task.get(t_id)
    touch_screen_stings = data.Touch_store.query.first()
    ticket_settings = data.Printer.query.first()
    printed = not touch_screen_stings.n
    numeric_ticket_form = ticket_settings.value == 2
    name_or_number = form.name.data or None

    if not task:
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('core.root'))

    # NOTE: if it is registered ticket, will display the form
    if not form.validate_on_submit() and not printed:
        return render_template('touch.html', title=touch_screen_stings.title,
                               tnumber=numeric_ticket_form, ts=touch_screen_stings,
                               bgcolor=touch_screen_stings.bgcolor, a=4, done=False,
                               page_title='Touch Screen - Enter name ', form=form,
                               dire='multimedia/', alias=data.Aliases.query.first())

    # NOTE: Incrementing the ticket number from the last generated ticket globally
    next_number = data.Serial.query.order_by(data.Serial.number.desc())\
                                   .first().number + 1
    office = task.least_tickets_office()

    if printed:
        common_arguments = (f'{office.prefix}.{next_number}',
                            f'{office.prefix}{office.name}',
                            data.Serial.all_office_tickets(office.id).count(),
                            task.name,
                            f'{office.prefix}.{data.Serial.all_office_tickets(office.id).first().number}')

        if os.name == 'nt':  # NOTE: Windows printing
            has_printers = bool(execute('wmic printer get sharename', parser='\n', encoding='utf-16')[1:])

            if has_printers:
                try:
                    (print_ticket_windows_ar
                     if ticket_settings.langu == 'ar' else
                     print_ticket_windows)(ticket_settings.product,
                                           *common_arguments,
                                           ip=current_app.config.get('LOCALADDR'))
                except Exception as exception:
                    return printer_failure_redirect(exception)
        else:
            try:
                printer = assign(int(ticket_settings.vendor), int(ticket_settings.product),
                                 int(ticket_settings.in_ep), int(ticket_settings.out_ep))

                (printit_ar if ticket_settings.langu == 'ar' else printit)(printer,
                                                                           *common_arguments,
                                                                           lang=ticket_settings.langu)
            except Exception as exception:
                return printer_failure_redirect(exception)

    db.session.add(data.Serial(number=next_number, office_id=office.id, task_id=task.id,
                               name=name_or_number, n=not printed))
    db.session.commit()
    return redirect(url_for('core.touch', a=1))


@core.route('/serial_r/<int:o_id>')
@login_required
def serial_r(o_id):
    ''' reset by removing tickets of a given office. '''
    office = data.Office.get(o_id)

    if is_operator() and not is_office_operator(o_id):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    if not office.tickets.first():
        flash('Error: the office is already resetted', 'danger')
        return redirect(url_for('manage_app.offices', o_id=o_id))

    data.Waiting.query.filter_by(office_id=office.id).delete()
    office.tickets.delete()
    db.session.commit()
    flash('Notice: office has been resetted. ..', 'info')
    return redirect(url_for("manage_app.offices", o_id=o_id))


@core.route('/serial_ra')
@login_required
@reject_operator
@reject_no_offices
def serial_ra():
    ''' reset all offices by removing all tickets. '''
    tickets = data.Serial.query.filter(data.Serial.number != 100)

    if not tickets.first():
        flash('Error: the office is already resetted', 'danger')
        return redirect(url_for('manage_app.all_offices'))

    data.Waiting.query.delete()
    tickets.delete()
    db.session.commit()
    flash('Notice: office has been resetted. ..', 'info')
    return redirect(url_for('manage_app.all_offices'))


@core.route('/serial_rt/<int:t_id>', defaults={'ofc_id': None})
@core.route('/serial_rt/<int:t_id>/<int:ofc_id>')
@login_required
def serial_rt(t_id, ofc_id=None):
    ''' reset a given task by removing its tickets. '''
    task = data.Task.get(t_id)

    if not task:
        flash('Error: No tasks exist to be resetted', 'danger')
        return redirect(url_for('manage_app.all_offices'))

    if is_operator() and not is_common_task_operator(task.id):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    tickets = task.tickets

    if ofc_id:
        tickets = tickets.filter_by(office_id=ofc_id)

    if not tickets.first():
        flash('Error: the task is already resetted', 'danger')
        return redirect(url_for('manage_app.task', o_id=t_id, ofc_id=ofc_id))

    data.Waiting.drop(tickets)
    tickets.delete()
    db.session.commit()
    flash('Error: the task is already resetted', 'info')
    return redirect(url_for('manage_app.task', o_id=t_id, ofc_id=ofc_id))


@core.route('/pull', defaults={'o_id': None, 'ofc_id': None})
@core.route('/pull/<int:o_id>/<int:ofc_id>')
@login_required
@refill_waiting_list
def pull(o_id=None, ofc_id=None):
    ''' pull ticket for specific task and office or globally. '''
    def operators_not_allowed():
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    task = data.Task.get(o_id)
    office = data.Office.get(ofc_id)
    show_prefix = data.Display_store.get().prefix
    strict_pulling = data.Settings.get().strict_pulling
    global_pull = not bool(o_id and ofc_id)
    general_redirection = redirect(url_for('manage_app.all_offices')
                                   if global_pull else
                                   url_for('manage_app.task', ofc_id=ofc_id, o_id=o_id))

    if global_pull:
        if is_operator():
            return operators_not_allowed()
    else:
        if not task:
            flash('Error: wrong entry, something went wrong', 'danger')
            return redirect(url_for('core.root'))

        if is_operator() and not (is_office_operator(ofc_id)
                                  if strict_pulling else
                                  is_common_task_operator(task.id)):
            return operators_not_allowed()

    next_tickets = data.Serial.query.filter(data.Serial.number != 100,
                                            data.Serial.p != True)
    next_ticket = None

    if not global_pull:
        next_ticket = next_tickets.filter(data.Serial.task_id == task.id)

        if strict_pulling:
            next_ticket = next_ticket.filter(data.Serial.office_id == office.id)

    next_ticket = (next_tickets if global_pull else next_ticket)\
        .order_by(data.Serial.timestamp)\
        .first()

    if not next_ticket:
        flash('Error: no tickets left to pull from ..', 'danger')
        return general_redirection

    office = office or data.Office.get(next_ticket.office_id)
    task = task or data.Task.get(next_ticket.task_id)

    data.Waiting_c.assume(next_ticket, office, task, show_prefix)
    next_ticket.pull(office.id)
    data.Waiting.drop([next_ticket])

    flash('Notice: Ticket has been pulled ..', 'info')
    return general_redirection


@core.route('/pull_unordered/<ticket_id>/<redirect_to>', defaults={'office_id': None})
@core.route('/pull_unordered/<ticket_id>/<redirect_to>/<office_id>')
@login_required
@refill_waiting_list
def pull_unordered(ticket_id, redirect_to, office_id=None):
    office = data.Office.get(office_id)
    ticket = data.Serial.query.filter_by(id=ticket_id).first()
    strict_pulling = data.Settings.get().strict_pulling
    show_prefix = data.Display_store.get().prefix

    if not ticket:
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('core.root'))

    if is_operator() and not (is_office_operator(ticket.office_id)
                              if strict_pulling else
                              is_common_task_operator(ticket.task_id)):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    office = office or ticket.office

    data.Waiting_c.assume(ticket, office, ticket.task, show_prefix)
    ticket.pull(office.id)
    data.Waiting.drop([ticket])

    flash('Notice: Ticket has been pulled ..', 'info')
    return redirect(f'{redirect_to}'.replace('(', '/'))


@core.route('/feed')
def feed():
    ''' stream list of waiting tickets and current ticket. '''
    display_settings = data.Display_store.query.first()
    show_prefix = display_settings.prefix
    current_ticket = data.Waiting_c.query.first()
    office_name = getattr(current_ticket, 'oname', 'Empty')
    task_name = getattr(current_ticket, 'tname', 'Empty')
    name_or_number = getattr(current_ticket,
                             'name' if current_ticket and current_ticket.n else 'ticket',
                             'Empty')

    def get_prefix(ticket):
        return f'{ticket.office.prefix}.' if show_prefix else ''

    waiting_tickets = (data.Waiting.query.limit(9).all() + ([None] * 9))[:9]
    waiting_list_parameters = {
        f'w{_index + 1}':
        f'{_index + 1}. {get_prefix(ticket)}{ticket.name if ticket.n else ticket.number}'
        if ticket else 'Empty'
        for _index, ticket in enumerate(waiting_tickets)
    }

    # NOTE: Ensure `waiting_list_parameters` last value is as distinct as the `current_ticket`
    # To fix `uniqueness` not picking up the change in passed waiting list
    waiting_list_parameters[f'w{len(waiting_list_parameters)}'] = name_or_number

    return jsonify(con=office_name, cot=name_or_number, cott=task_name,
                   replay='yes' if display_settings.r_announcement else 'no',
                   **waiting_list_parameters)


@core.route('/repeat_announcement', methods=['POST', 'GET'], defaults={'reached': False})
@core.route('/repeat_announcement/<reached>', methods=['POST', 'GET'])
@login_required
def repeat_announcement(reached=False):
    ''' repeat TTS announcement. '''
    display_settings = data.Display_store.query.first()
    display_settings.r_announcement = not reached

    db.session.commit()
    return 'success'


@core.route('/display')
def display():
    ''' display screen view. '''
    display_settings = data.Display_store.query.first()
    slideshow_settings = data.Slides_c.query.first()
    slides = data.Slides.query.order_by(data.Slides.id.desc()).all() or None
    aliases_settings = data.Aliases.query.first()
    video_settings = data.Vid.query.first()

    return render_template('display.html',
                           audio=1 if display_settings.audio == 'true' else 0,
                           audio_2=1 if display_settings.announce != 'false' else 0,
                           ss=slides, sli=slideshow_settings, ts=display_settings,
                           slides=data.Slides.query, tv=display_settings.tmp,
                           page_title='Display Screen', anr=display_settings.anr,
                           alias=aliases_settings, vid=video_settings)


@core.route('/touch/<int:a>')
def touch(a):
    ''' touch screen view. '''
    form = forms.Touch_name_ar() if session.get('lang') == 'AR' else forms.Touch_name()
    tasks = data.Task.query.order_by(data.Task.timestamp).all() or 0
    touch_screen_stings = data.Touch_store.query.first()
    numeric_ticket_form = data.Printer.query.first().value == 2
    aliases_settings = data.Aliases.query.first()

    return render_template('touch.html', ts=touch_screen_stings, tasks=tasks,
                           tnumber=numeric_ticket_form, page_title='Touch Screen',
                           alias=aliases_settings, form=form, d=a == 1,
                           a=touch_screen_stings.tmp)


@core.route('/settings/<setting>/<togo>')
@login_required
@reject_not_admin
def settings(setting, togo):
    ''' toggle a setting. '''
    settings = data.Settings.get()
    togo = f'{togo}'.replace('(', '/')

    if not settings:
        flash('Error: Failed to find settings in the database', 'danger')
        return redirect(togo)

    toggled_setting_value = not bool(getattr(settings, setting, True))

    settings.__setattr__(setting, toggled_setting_value)
    db.session.commit()
    flash(f'Notice: Setting got {"Enabled" if toggled_setting_value else "Disabled"} successfully.',
          'info')

    return redirect(togo)
