import functools
import os
import pickle
from sys import platform
from uuid import uuid4
from flask import url_for, flash, render_template, redirect, session, jsonify, Blueprint
from flask_login import current_user, login_required, login_user

import app.database as data
import app.settings as settings_handlers
from app.middleware import db, gtranslator, redis
from app.utils import log_error, remove_string_noise
from app.forms.core import LoginForm, TouchSubmitForm
from app.helpers import (reject_no_offices, reject_operator, is_operator, reject_not_admin,
                         is_office_operator, is_common_task_operator, decode_links,
                         reject_setting, get_or_reject)
from app.cache import cache_call


core = Blueprint('core', __name__)


class SharedAnnouncementDecorator:
    def __init__(self, wrapped):
        self._wrapped = wrapped
        self.__name__ = wrapped.__name__
        self.__state = {}

    def __call__(self, *args, **kwargs):
        return self._wrapper(*args, **kwargs)

    def get_state(self):
        if os.environ.get('DOCKER'):
            state = redis.get(self.__name__)
            return state and pickle.loads(state)
        else:
            return self.__state

    def set_state(self, state):
        if os.environ.get('DOCKER'):
            return redis.set(self.__name__, pickle.dumps(state))
        else:
            self.__state = state
            return self.__state

    def cache_clear(self):
        if os.environ.get('DOCKER'):
            redis.delete(self.__name__)
        else:
            self.__state.clear()

    def set(self, office_id, status):
        state = self.get_state() or {}
        state[office_id] = status
        state.setdefault('ids', {})[office_id] = uuid4()
        self.set_state(state)

    def get(self, office_id):
        return (self.get_state() or {}).get(office_id)

    def get_id(self, office_id):
        return (self.get_state() or {}).get('ids', {}).get(office_id)

    def _wrapper(self, *args, **kwargs):
        pre_state = state = self.get_state()

        if state is None:
            state = self._get_default_state()

        office_id = kwargs.get('office_id')
        resp = self._wrapped(*args, **kwargs)

        if state.get(office_id):
            state[office_id] = False

        if state != pre_state:
            self.set_state(state)

        return resp

    def _get_default_state(self):
        state = {}

        for o in data.Office.query.all():
            if o.id not in state:
                state[o.id] = False

        if None not in state:
            state[None] = False

        return state


@core.route('/', methods=['GET', 'POST'], defaults={'n': None})
@core.route('/log/<n>', methods=['GET', 'POST'])
def root(n=None):
    ''' welcome view and login. '''
    form = LoginForm()
    has_default_password = data.User.has_default_password()
    wrong_credentials = n == 'a'
    should_redirect = n == 'b'
    single_row = data.Settings.get().single_row

    def logged_in_all_good():
        destination = url_for('manage_app.manage')

        if is_operator() and not single_row:
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


@core.route('/serial/<int:t_id>', methods=['POST', 'GET'], defaults={'office_id': None})
@core.route('/serial/<int:t_id>/<int:office_id>', methods=['GET', 'POST'])
@reject_setting('single_row', True)
@get_or_reject(t_id=data.Task)
def serial(task, office_id=None):
    ''' generate a new ticket and print it. '''
    windows = os.name == 'nt'
    form = TouchSubmitForm()
    task = data.Task.get(task.id)
    office = data.Office.get(office_id)
    touch_screen_stings = data.Touch_store.get()
    ticket_settings = data.Printer.get()
    printed = not touch_screen_stings.n
    numeric_ticket_form = ticket_settings.value == 2
    name_or_number = remove_string_noise(form.name.data or '',
                                         lambda s: s.startswith('0'),
                                         lambda s: s[1:]) or None

    # NOTE: if it is registered ticket, will display the form
    if not form.validate_on_submit() and not printed:
        return render_template('touch.html', title=touch_screen_stings.title,
                               tnumber=numeric_ticket_form, ts=touch_screen_stings,
                               bgcolor=touch_screen_stings.bgcolor, a=4, done=False,
                               page_title='Touch Screen - Enter name ', form=form,
                               dire='multimedia/', alias=data.Aliases.query.first(),
                               office_id=office_id)

    new_ticket, exception = data.Serial.create_new_ticket(task,
                                                          office,
                                                          name_or_number)

    if exception:
        flash('Error: you must have available printer, to use printed', 'danger')
        flash('Notice: make sure that printer is properly connected', 'info')

        if windows:
            flash('Notice: Make sure to make the printer shared on the local network', 'info')
        elif 'linux' in platform:
            flash('Notice: Make sure to execute the command `sudo gpasswd -a $(users) lp` and '
                  'reboot the system', 'info')

        log_error(exception)
        return redirect(url_for('core.root'))

    return redirect(url_for('core.touch', a=1, office_id=office_id))


@core.route('/serial_r/<int:o_id>')
@login_required
@get_or_reject(o_id=data.Office)
def serial_r(office):
    ''' reset by removing tickets of a given office. '''
    single_row = data.Settings.get().single_row
    office = data.Office.get(office.id)
    office_redirection = url_for('manage_app.all_offices')\
        if single_row else url_for('manage_app.offices', o_id=office.id)

    if (is_operator() and not is_office_operator(office.id)) and not single_row:
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    if not office.tickets.first():
        flash('Error: the office is already resetted', 'danger')
        return redirect(office_redirection)

    office.tickets.delete()
    db.session.commit()
    flash('Notice: office has been resetted. ..', 'info')
    return redirect(office_redirection)


@core.route('/serial_ra')
@login_required
@reject_operator
@reject_no_offices
@reject_setting('single_row', True)
def serial_ra():
    ''' reset all offices by removing all tickets. '''
    tickets = data.Serial.query.filter(data.Serial.number != 100)

    if not tickets.first():
        flash('Error: the office is already resetted', 'danger')
        return redirect(url_for('manage_app.all_offices'))

    tickets.delete()
    db.session.commit()
    flash('Notice: office has been resetted. ..', 'info')
    return redirect(url_for('manage_app.all_offices'))


@core.route('/serial_rt/<int:t_id>', defaults={'ofc_id': None})
@core.route('/serial_rt/<int:t_id>/<int:ofc_id>')
@login_required
@reject_setting('single_row', True)
@get_or_reject(t_id=data.Task)
def serial_rt(task, ofc_id=None):
    ''' reset a given task by removing its tickets. '''
    if is_operator() and not is_common_task_operator(task.id):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    task = data.Task.get(task.id)
    tickets = task.tickets

    if ofc_id:
        tickets = tickets.filter_by(office_id=ofc_id)

    if not tickets.first():
        flash('Error: the task is already resetted', 'danger')
        return redirect(url_for('manage_app.task', o_id=task.id, ofc_id=ofc_id))

    tickets.delete()
    db.session.commit()
    flash('Error: the task is already resetted', 'info')
    return redirect(url_for('manage_app.task', o_id=task.id, ofc_id=ofc_id))


@core.route('/pull', defaults={'o_id': None, 'ofc_id': None})
@core.route('/pull/<int:o_id>/<int:ofc_id>')
@login_required
def pull(o_id=None, ofc_id=None):
    ''' pull ticket for specific task and office or globally. '''
    def operators_not_allowed():
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    settings = data.Settings.get()
    strict_pulling = settings.strict_pulling
    single_row = settings.single_row
    task = data.Task.get(0 if single_row else o_id)
    office = data.Office.get(0 if single_row else ofc_id)
    global_pull = not bool(o_id and ofc_id)
    redirection_url = (url_for('manage_app.all_offices')
                       if global_pull or single_row else
                       url_for('manage_app.task', ofc_id=ofc_id, o_id=o_id))

    if global_pull:
        if not single_row and is_operator():
            return operators_not_allowed()
    else:
        if not task:
            flash('Error: wrong entry, something went wrong', 'danger')
            return redirect(url_for('core.root'))

        if is_operator() and not (is_office_operator(ofc_id)
                                  if strict_pulling else
                                  is_common_task_operator(task.id)):
            return operators_not_allowed()

    next_ticket = data.Serial.get_next_ticket(task_id=o_id,
                                              office_id=ofc_id)

    if not next_ticket:
        flash('Error: no tickets left to pull from ..', 'danger')
        return redirect(redirection_url)

    next_ticket.pull(office and office.id or next_ticket.office_id)
    flash('Notice: Ticket has been pulled ..', 'info')
    return redirect(redirection_url)


@core.route('/pull_unordered/<ticket_id>/<redirect_to>', defaults={'office_id': None})
@core.route('/pull_unordered/<ticket_id>/<redirect_to>/<int:office_id>')
@login_required
@decode_links
@reject_setting('single_row', True)
def pull_unordered(ticket_id, redirect_to, office_id=None):
    office = data.Office.get(office_id)
    ticket = data.Serial.query.filter_by(id=ticket_id).first()
    strict_pulling = data.Settings.get().strict_pulling

    if not ticket or ticket.on_hold:
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('core.root'))

    if is_operator() and not (is_office_operator(ticket.office_id)
                              if strict_pulling else
                              is_common_task_operator(ticket.task_id)):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    ticket.pull((office or ticket.office).id)
    flash('Notice: Ticket has been pulled ..', 'info')
    return redirect(redirect_to)


@core.route('/on_hold/<ticket_id>/<redirect_to>')
@login_required
@decode_links
@reject_setting('single_row', True)
@get_or_reject(ticket_id=data.Serial)
def on_hold(ticket, redirect_to):
    ticket = data.Serial.get(ticket.id)
    strict_pulling = data.Settings.get().strict_pulling

    if is_operator() and not (is_office_operator(ticket.office_id)
                              if strict_pulling else
                              is_common_task_operator(ticket.task_id)):
        flash('Error: operators are not allowed to access the page ', 'danger')
        return redirect(url_for('core.root'))

    ticket.toggle_on_hold()
    flash('Notice: On-hold status has changed successfully', 'info')
    return redirect(redirect_to)


@core.route('/feed', defaults={'office_id': None})
@core.route('/feed/<int:office_id>')
@cache_call('json')
def feed(office_id=None):
    ''' stream list of waiting tickets and current ticket. '''
    display_settings = data.Display_store.get()
    single_row = data.Settings.get().single_row
    current_ticket = data.Serial.get_last_pulled_ticket(office_id)
    empty_text = gtranslator.translate('Empty', dest=[session.get('lang')])
    current_ticket_text = current_ticket and current_ticket.display_text or empty_text
    current_ticket_office_name = current_ticket and current_ticket.office.display_text or empty_text
    current_ticket_task_name = current_ticket and current_ticket.task.name or empty_text

    def _resolve_ticket_index(_index):
        return '' if display_settings.hide_ticket_index else f'{_index + 1}. '

    if single_row:
        tickets_parameters = {
            f'w{_index + 1}': f'{_resolve_ticket_index(_index)}{number}'
            for _index, number in enumerate(range(getattr(current_ticket, 'number', 1) + 1,
                                                  getattr(current_ticket, 'number', 1) + 10))}
    else:
        waiting_tickets = (data.Serial.get_waiting_list_tickets(office_id) + ([None] * 9))[:9]
        tickets_parameters = {
            f'w{_index + 1}':
            f'{_resolve_ticket_index(_index)}{ticket.display_text}' if ticket else empty_text
            for _index, ticket in enumerate(waiting_tickets)}

    # NOTE: Add last 10 processed tickets, for supported template.
    if display_settings.tmp == 3:
        processed_tickets = (data.Serial.get_processed_tickets(office_id, offset=1) + ([None] * 9))[:9]
        tickets_parameters.update({
            f'p{_index + 1}':
            f'{_resolve_ticket_index(_index)}{ticket.display_text}' if ticket else empty_text
            for _index, ticket in enumerate(processed_tickets)})

    # NOTE: Ensure `tickets_parameters` last value is as distinct as the `current_ticket`
    # To fix `uniqueness` not picking up the change in passed waiting list
    tickets_parameters[f'w{len(tickets_parameters)}'] = (current_ticket.name
                                                         if current_ticket.n else
                                                         current_ticket.number
                                                         ) if current_ticket else empty_text

    return jsonify(con=current_ticket_office_name,
                   cot=current_ticket_text,
                   cott=current_ticket_task_name,
                   **tickets_parameters)


@core.route('/repeat_announcement', defaults={'office_id': None})
@core.route('/repeat_announcement/<int:office_id>')
@SharedAnnouncementDecorator
def repeat_announcement(office_id=None):
    ''' get repeat TTS announcement. '''
    return jsonify(
        status=repeat_announcement.get(office_id),
        id=repeat_announcement.get_id(office_id),
    )


@core.route('/set_repeat_announcement/<int:status>', defaults={'office_id': None})
@core.route('/set_repeat_announcement/<int:status>/<int:office_id>')
@login_required
def set_repeat_announcement(status, office_id=None):
    ''' set repeat TTS announcement status. '''
    active = bool(status)
    repeat_announcement.set(office_id, active)
    return jsonify(status=active)


@core.route('/display', defaults={'office_id': None})
@core.route('/display/<int:office_id>')
@cache_call()
def display(office_id=None):
    ''' display screen view. '''
    display_settings = data.Display_store.query.first()
    slideshow_settings = data.Slides_c.query.first()
    slides = data.Slides.query.order_by(data.Slides.id.desc()).all() or None
    aliases_settings = data.Aliases.query.first()
    video_settings = data.Vid.query.first()
    feed_url = url_for('core.feed', office_id=office_id)

    return render_template('display.html',
                           audio=1 if display_settings.audio == 'true' else 0,
                           audio_2=1 if display_settings.announce != 'false' else 0,
                           ss=slides, sli=slideshow_settings, ts=display_settings,
                           slides=data.Slides.query, tv=display_settings.tmp,
                           page_title='Display Screen', anr=display_settings.anr,
                           alias=aliases_settings, vid=video_settings,
                           feed_url=feed_url, office_id=office_id)


@core.route('/touch/<int:a>', defaults={'office_id': None})
@core.route('/touch/<int:a>/<int:office_id>')
@cache_call()
@reject_setting('single_row', True)
def touch(a, office_id=None):
    ''' touch screen view. '''
    form = TouchSubmitForm()
    touch_screen_stings = data.Touch_store.query.first()
    numeric_ticket_form = data.Printer.query.first().value == 2
    aliases_settings = data.Aliases.query.first()
    office = data.Office.get(office_id)
    tasks = data.Task.query.filter_by(hidden=False)\
                           .order_by(data.Task.timestamp)

    if office:
        tasks = tasks.filter(data.Task.offices.contains(office))

    return render_template('touch.html', ts=touch_screen_stings, tasks=tasks.all(),
                           tnumber=numeric_ticket_form, page_title='Touch Screen',
                           alias=aliases_settings, form=form, d=a == 1,
                           a=touch_screen_stings.tmp, office_id=office_id)


@core.route('/settings/<setting>', defaults={'togo': None})
@core.route('/settings/<setting>/<togo>')
@login_required
@reject_not_admin
@decode_links
def settings(setting, togo=None):
    ''' toggle a setting. '''
    togo = togo or '/'
    settings = data.Settings.get()

    if not settings:
        flash('Error: Failed to find settings in the database', 'danger')
        return redirect(togo)

    toggled_setting_value = not bool(getattr(settings, setting, True))

    getattr(settings_handlers, setting, lambda s: '')(toggled_setting_value)
    settings.__setattr__(setting, toggled_setting_value)
    db.session.commit()
    flash(f'Notice: Setting got {"Enabled" if toggled_setting_value else "Disabled"} successfully.',
          'info')

    return redirect(togo)
