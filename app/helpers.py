import os
import json
from urllib.parse import unquote
from functools import wraps

from flask import current_app, flash, redirect, url_for, request
from flask_login import current_user
from flask import jsonify

import app.database as data
from app.utils import absolute_path, log_error
from app.constants import TICKET_ORDER_NEWEST_PROCESSED
from app.cache import cache_call


class CacheStateDecoratorBase:
    def __init__(self, wrapped):
        self._wrapped = wrapped
        self.state = {}
        self._responses = {}

    def __call__(self, *args, **kwargs):
        key = (str(args), str(kwargs))
        resp  = self._responses.get(key)
        state = self.state.get(key)

        if resp is not None and self.use_cached_state(state):
            return resp

        new_state = self._wrapped(*args, **kwargs)
        self.state[key] = new_state
        self._responses[key] = resp = self.create_response(new_state)

        return resp

    def create_response(self, state):
        pass

    def use_cached_state(self, state):
        pass

    def clear_cache(self):
        self.state.clear()
        self._responses.clear()


class RepeatAnnounceDecorator(CacheStateDecoratorBase):
    key = ('()', '{}')

    def create_response(self, state):
        return jsonify(state)

    def use_cached_state(self, state):
        return not all(state.values())


def is_god():
    ''' Check if the current user is God! '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 1


def is_admin():
    ''' Check if the current user is of the Administrator role. '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 1


def is_operator():
    ''' Check if the current user is of the Operator role. '''
    with current_app.app_context():
        return getattr(current_user, 'role_id', None) == 3


def has_offices():
    ''' Check if there's any offices created yet. '''
    with current_app.app_context():
        return data.Office.query.first() is not None


def is_office_operator(office_id):
    ''' Check if the current user's an office operator.

    Parameters
    ----------
        office_id: int
            id of the office to check for its operators.

    Returns
    -------
        True if a valid operator False if not
    '''
    operator = data.Operators.get(current_user.id)

    return bool(operator and operator.office_id == office_id)


def is_common_task_operator(task_id):
    ''' Check if the current user's an operator of common task.

    Parameters
    ----------
        task_id: int
            common task's id to check for its operators.

    Returns
    -------
        True if a valid operator False if not
    '''
    task = data.Task.get(task_id)

    return any([
        is_office_operator(office.id) for office in (task and task.offices) or []
    ])


def reject_not_god(function):
    ''' Decorator to flash and redirect to `core.root` if current user is not God.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_god() or current_app.config.get('LOGIN_DISABLED'):
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: only main Admin account can access the page', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_god(function):
    ''' Decorator to flash and redirect to `core.root` if current user is God.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if not is_god():
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: main admin account cannot be updated .', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_not_admin(function):
    ''' Decorator to flash and redirect to `core.root` if current user is not administrator.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_admin() or current_app.config.get('LOGIN_DISABLED'):
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: only administrator can access the page', 'danger')
            return redirect(url_for('core.root'))

    return decorated


def reject_operator(function):
    ''' Decorator to flash and redirect to `core.root` if current user is operator.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if is_operator():
            with current_app.app_context():
                if not data.Settings.get().single_row:
                    flash('Error: operators are not allowed to access the page ', 'danger')
                    return redirect(url_for('core.root'))
        return function(*args, **kwargs)

    return decorated


def reject_no_offices(function):
    ''' Decorator to flash and redirect to `manage_app.all_offices`
        if there's not any offices created yet.

    Parameters
    ----------
        function: callable
            the endpoint we want to reject unGodly users to access.

    Returns
    -------
        Decorator for the passed `function`.
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        if has_offices():
            return function(*args, **kwargs)
        with current_app.app_context():
            flash('Error: No offices exist to delete', 'danger')
            return redirect(url_for('manage_app.all_offices'))

    return decorated


def reject_videos_enabled(function):
    ''' Decorator to flash and redirect to `cust_app.video`.

    Parameters
    ----------
        function: callable
            then endpoint to be rejected if videos enabled.

    Returns
    -------
        Decorator for the passed `function`
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        with current_app.app_context():
            enabled = data.Vid.query.first().enable == 1

            if enabled:
                flash('Error: you must disable videos first', 'danger')
                return redirect(url_for('cust_app.video'))

            return function(*args, **kwargs)

    return decorated


def reject_slides_enabled(function):
    ''' Decorator to flash and redirect to `cust_app.slide_c`.

    Parameters
    ----------
        function: callable
            then endpoint to be rejected if slides enabled.

    Returns
    -------
        Decorator for the passed `function`
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        with current_app.app_context():
            enabled = data.Slides_c.query.first().status == 1

            if enabled:
                flash('Error: you must disable slide-show first', 'danger')
                return redirect(url_for('cust_app.video'))

            return function(*args, **kwargs)

    return decorated


def reject_setting(setting, status):
    '''Decorator to reject and flash if setting match status.

    Parameters
    ----------
    setting : str
        flag setting name.
    status : bool
        flag setting status.
    '''
    def wrapper(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            with current_app.app_context():
                if getattr(data.Settings.get(), setting, False) == status:
                    flash(
                        f'Error: flag setting {setting} must be {"disabled" if status else "enabled"}',
                        'danger')
                    return redirect(url_for('core.root'))
            return function(*args, **kwargs)
        return decorator
    return wrapper


def get_or_reject(**models):
    '''Get list of database records from a list or flash message.

    Parameters
    ----------
    models : list
        list of SQLAlchemy models to get from.
    '''
    def wrapper(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            with current_app.app_context():
                new_kwargs = {}

                for kwarg, model in models.items():
                    record = model.get(kwargs.get(kwarg))
                    column_name = getattr(model, '__tablename__', ' ')[:-1]

                    if not record:
                        flash('Error: wrong entry, something went wrong', 'danger')
                        return redirect(url_for('core.root'))

                    if column_name == 'serial':
                        column_name = 'ticket'

                    new_kwargs[column_name] = record

                for kwarg, value in kwargs.items():
                    if kwarg not in new_kwargs and kwarg not in models:
                        new_kwargs[kwarg] = value

                if len(kwargs.keys()) != len(new_kwargs.keys()):
                    raise AttributeError('Modules list mismatch arguments.')

                return function(*args, **new_kwargs)
        return decorator
    return wrapper


def decode_links(function):
    ''' Decorator to `urllib.parse.unquote` string arguments.

    Returns
    -------
        Decorator for the passed `function`
    '''
    @wraps(function)
    def decorated(*args, **kwargs):
        clean_args = [unquote(a) if type(a) is str else a for a in args]
        clean_kwargs = {k: unquote(v) if type(v) is str else v for k, v in kwargs.items()}

        return function(*clean_args, **clean_kwargs)

    return decorated


def ticket_orders(function):
    ''' Decorator to get and pass ticket orders.

    Parameters
    ----------
    function : callable

    Returns
    -------
    callable
        decorated function
    '''
    @wraps(function)
    def decorator(*args, **kwargs):
        with current_app.app_context():
            order_by = request.args.get('order_by',
                                        TICKET_ORDER_NEWEST_PROCESSED)
            orders = list(data.Serial.ORDERS.keys())

            return function(*args,
                            **{**kwargs,
                               'order_by': order_by,
                               'order_kwargs': {'order_by': order_by,
                                                'orders': orders}})

    return decorator


def get_tts_safely():
    ''' Helper to read gTTS data from `static/tts.json` file safely.

    Parameters
    ----------
        failsafe: boolean
            to silence any encountered errors.

    Returns
    -------
        Dict of gTTS content. Example::
        {"en-us": {"langauge": "English", "message": "new ticket!"}, ...}
    '''
    tts_path = os.path.join(absolute_path('static'), 'tts.json')
    tts_content = {}

    try:
        with open(tts_path, encoding='utf-8') as tts_file:
            tts_content.update(json.load(tts_file))
    except Exception as e:
        log_error(e)
        tts_content.update({'en-us': {'language': 'English',
                                      'message': ' , please proceed to the {} number : '}})

    return tts_content


@cache_call(None)
def get_all_offices_cached():
    return data.Office.query.all()

@cache_call(None)
def get_settings_cached():
    return data.Settings.get()

@cache_call(None)
def get_number_of_active_tickets_cached():
    return data.Serial.query.filter_by(p=False).count()

@cache_call(None)
def get_number_of_active_tickets_office_cached(*args, **kwargs):
    return (
        data.Serial.all_office_tickets(*args, **kwargs)
        .filter_by(p=False)
        .count()
    )

@cache_call(None)
def get_number_of_active_tickets_task_cached(*args, **kwargs):
    return (
        data.Serial.all_task_tickets(*args, **kwargs)
        .filter_by(p=False)
        .count()
    )
