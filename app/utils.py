import os
import sys
from collections import namedtuple
from uuid import uuid4
from traceback import TracebackException
from datetime import datetime
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from netifaces import interfaces, ifaddresses
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import current_app, Flask

import app.database as data
from app.middleware import db
from app.constants import (DEFAULT_PASSWORD, DEFAULT_USER, DATABASE_FILE,
                           BACKGROUNDTASKS_DEFAULTS)


def execute(command, parser=None, encoding='utf-8'):
    '''
    Utility to execute a system command and get its output without
    breaking any ongoing execution loops.

    Parameter
    ---------
        command: str
            system command to execute.
        parser: str
            factor to parse the output and clean it with.
        encoding: str
            encoding to read the command output with.

    Returns
    -------
        System command output as a string or a list if parsed.
    '''
    temp_name = f'{uuid4()}'.replace('-', '') + '.tmp'
    temp_file = absolute_path(temp_name)
    output = ''
    parsed = []

    os.system(f'{command} > "{temp_file}"')
    with open(temp_file, 'r', encoding=encoding) as file:
        output += file.read()
    os.remove(temp_file)

    if parser:
        parsed += [o.strip() for o in output.split(parser) if o.strip()]

    return parsed if parser else output


def absolute_path(relative_path):
    ''' Get an absolute path from a relative one.

    Parameters
    ----------
        relative_path: str
            relative path to make absolute.

    Returns
    -------
        Absolute path from `relative_path`
    '''
    delimiter = '\\' if os.name == 'nt' else '/'
    clean_path = relative_path
    base_path = os.path.dirname(sys.executable)\
        if getattr(sys, 'frozen', False) else os.path.abspath('.')

    if clean_path.startswith(delimiter):
        clean_path = clean_path[len(delimiter):]

    return os.path.join(base_path, clean_path)


def ids (list_of_modules):
    ''' Helper to retrieve list of ids from a list of modules.

    Parameter
    ---------
        list_of_modules: list
            list of SQLAlchemy modules.

    Returns
    -------
        List of ids.
    '''
    return [getattr(m, 'id', None) for m in list_of_modules if getattr(m, 'id', None)]


def get_module_columns(module):
    ''' Utility to retrieve SQLAlchemy module columns names.

    Parameters
    ----------
        module: SQLAlchemy module instance
            module to retrieve its columns names.

    Returns
    -------
        List of module columns names.
    '''
    with current_app.app_context():
        return [
            getattr(column, 'name', None)
            for column in getattr(getattr(module, '__mapper__', None), 'columns', [])
            if getattr(column, 'name', None) != 'password_hash'
        ]


def get_module_values(module, stringify=True):
    ''' Utility to retrieve SQLAlchemy module columns values.

    Parameters
    ----------
        module: SQLAlchemy module instance
            module to retrieve its columns values.
        stringify: boolean
            convert all values to string type.

    Returns
    -------
        List of module columns values.
    '''
    group_of_values = []

    with current_app.app_context():
        query = getattr(module, 'query', [])

        if query and module.__tablename__ == 'serials':
            query = query.filter(module.number != 100)

        for record in query:
            values = [
                getattr(record, getattr(column, 'name', None), None)
                for column in getattr(getattr(module, '__mapper__', None), 'columns', [])
                if getattr(column, 'name', None) != 'password_hash'
            ]

            group_of_values.append(list(map(str, values)) if stringify else values)

    return group_of_values


def log_error(error, quiet=False):
    ''' Utility to log error to `errors.txt` file.

    Parameters
    ----------
        error: Error instance
            error that we want to log.
        quiet: bool
            to log or silence the error.
    '''
    log_file = absolute_path('errors.log')
    formated_error = ''.join(TracebackException.from_exception(error).format())

    not os.path.isfile(log_file) and os.system(f'touch {log_file}')
    with open(log_file, 'a') as file:
        file.write(f'{"#" * 5} {datetime.now()} {"#" * 5}\n')
        file.write(formated_error)

    if not quiet:
        print(formated_error)


def get_accessible_ips():
    ''' Utility to retrieve accessible ips.

    Returns
    -------
        List of accessible ips and the interface name `(interface, ip)`
    '''
    returned_list = []

    for interface in interfaces():
        try:
            returned_list.append((
                # NOTE: Windows doesn't support interface name
                '' if os.name == 'nt' else interface,
                ifaddresses(interface)[2][0].get('addr')
            ))
        except Exception:
            pass

    return returned_list


def is_port_available(ip, port):
    ''' Utility to check if port is available on a given local address.

    Parameters
    ----------
        ip: str
            local ip address to try the port on.
        port: int
            port to check for its availability.

    Returns
    -------
        True if port is available, False if not.
    '''
    available = True
    new_socket = socket(AF_INET, SOCK_STREAM)

    try:
        new_socket.bind((ip, int(port)))
    except Exception:
        available = False
    finally:
        new_socket.close()

    return available


def get_random_available_port(ip):
    ''' Utility to get an available port to listen on.

    Parameters
    ----------
        ip: str
            local ip address to try the port on.

    Returns
    -------
        Interger of any available random port.
    '''
    available_port = None

    while not available_port:
        random_port = randint(1000, 9999)
        available_port = is_port_available(ip, random_port) and random_port

    return available_port


def create_aliternative_db(db_name=None):
    ''' Utility to create an alternative database SQLAlchemy session.

    Parameters
    ----------
        db_name: name of the database file.

    Returns
    -------
        session: SQLAlchemy Session
        classes SQLAlchemy Base.classes
    '''
    session = None
    classes = None

    try:
        db_path = absolute_path(db_name or DATABASE_FILE)
        base = automap_base()
        engine = create_engine(f'sqlite:///{db_path}?check_same_thread=False')

        base.prepare(engine, reflect=True)

        session = Session(engine)
        classes = base.classes
    except Exception as e:
        log_error(e)

    return session, classes, engine


def get_with_alias(db_name=None):
    ''' Resolve querying aliases without app_context in languages.

    Parameters
    ----------
        db_name: name of the database file.

    Returns
    -------
        Dict of texts with aliases embodied.
    '''
    alias = namedtuple(
        'alias', ['office', 'ticket', 'task']
    )('office', 'ticket', 'task')

    try:
        session, db, eng = create_aliternative_db(db_name)
        alias = session.query(db.aliases).first()
    except Exception:
        pass

    return {
        'Version ': 'Version ',
        '\nOffice : ': '\n' + alias.office + ' : ',
        '\nCurrent ticket : ': '\nCurrent ' + alias.ticket + ' : ',
        '\nTickets ahead : ': '\n' + alias.ticket + 's ahead : ',
        '\nTask : ': '\n' + alias.task + ' : ',
        '\nTime : ': '\nTime : '
    }


def convert_to_int_or_hex(value):
    ''' Covert string or hex string to int or int/16.

    Parameters
    ----------
        value: str
            value to convert to int.

    Returns
    -------
        Int of converted value.
    '''
    try:
        return int(value)
    except Exception:
        try:
            return int(value, 16)
        except Exception:
            pass


def is_iterable(arg):
    ''' Check if passed argument is iterable.

    Parameters
    ----------
    arg : any
        argument to check if it's iterable

    Returns
    -------
    bool
        if iterable
    '''
    try:
        for i in arg:
            return True
    except Exception:
        return False


def remove_string_noise(string, condition, getter):
    '''remove noise from the start of a given string.

    Parameters
    ----------
    string : str
        string to remove its starting noise.
    condition : function(new_string)
        function to determine if subtracting from strign should continue.
    getter : function(string) -> new_string:
        function to parse new string if condition is met.

    Returns
    -------
    strgin
        clear of noise string.
    '''
    clean_string = string

    while clean_string and condition(clean_string):
        clean_string = getter(clean_string)

    return clean_string


def find(getter, to_iter):
    '''Find an item in an iterable.

    Parameters
    ----------
    getter : callable
        function to find an item by.
    to_iter : iterable
        iterable to find an item within.
    '''
    for i in to_iter:
        if getter(i):
            return i


def get_bp_endpoints(blueprint):
    '''Get blueprint endpoints.

    Parameters
    ----------
    blueprint : Flask.Blueprint

    Returns
    -------
    List
        Blueprint list of endpoints.
    '''
    temp_app = Flask(__name__)

    temp_app.register_blueprint(blueprint)

    return [str(p) for p in temp_app.url_map.iter_rules()]


def create_default_records():
    ''' create database necessary records, if not existing. '''
    tables = [data.Display_store, data.Touch_store, data.Slides_c,
              data.Settings, data.Vid, data.Printer, data.Aliases]

    # NOTE: Create default records, if non-existing.
    for table in tables:
        if not table.query.first():
            db.session.add(table())
    db.session.commit()
    data.Roles.load_roles()

    # NOTE: Add default user account if not existing
    if not data.User.query.first():
        db.session.add(data.User(name=DEFAULT_USER,
                                 password=DEFAULT_PASSWORD,
                                 role_id=1))
        db.session.commit()

    for task, settings in BACKGROUNDTASKS_DEFAULTS.items():
        task_settings = data.BackgroundTask.get(name=task)

        if not task_settings:
            db.session.add(data.BackgroundTask(task, **settings))
            db.session.commit()


def getFolderSize(folder, safely=False):
    # -- get a folder size
    if safely and not os.path.isdir(folder):
        os.makedirs(folder)
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return int(float(total_size / 1024 / 1024))


def solve_path(path):
    ''' fix path for window os '''
    return path.replace('/', '\\') if os.name == 'nt' else path
