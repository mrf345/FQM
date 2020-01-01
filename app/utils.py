# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
from traceback import TracebackException
from datetime import datetime
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from netifaces import interfaces, ifaddresses
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import current_app

import app.database as data
from app.middleware import db


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


def log_error(error):
    ''' Utility to log error to `errors.txt` file.

    Parameters
    ----------
        error: Error instance
            error that we want to log.
    '''
    log_file = r_path('errors.log')

    not os.path.isfile(log_file) and os.system(f'touch {log_file}')
    with open(log_file, 'a') as file:
        file.write(f'{"#" * 5} {datetime.now()} {"#" * 5}\n')
        file.write(''.join(TracebackException.from_exception(error).format()))


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


def get_with_alias():
    ''' to solve querying aliases without app_context in languages. '''
    class Aliases(object):
        office = 'office'
        ticket = 'ticket'
        task = 'task'

    alias = Aliases()
    base_path = os.path.abspath('.')

    try:
        base_path = sys._MEIPASS
    except Exception:
        pass

    try:
        if os.path.isfile(os.path.join(base_path, 'data.sqlite')):
            Base = automap_base()
            engine = create_engine('sqlite:///' + os.path.join(base_path, 'data.sqlite'))
            Base.prepare(engine, reflect=True)
            if hasattr(Base.classes, 'aliases'):
                Aliases = Base.classes.aliases
                session = Session(engine)
                alias = session.query(Aliases).first()
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


def mse():
    lodb = [data.Display_store,
            data.Touch_store,
            data.Slides_c, data.Settings,
            data.Vid, data.Waiting_c,
            data.Printer, data.Aliases]
    # -- make sure objects are created,
    # And if not create an auto filled one
    for t in lodb:
        if t.query.first() is None:
            db.session.add(t())
    # fill in user roles if not existed
    if data.Roles.query.first() is None:
        for r in range(1, 4):
            ra = data.Roles()
            ra.id = r
            if r == 1:
                ra.name = 'Administrator'
            elif r == 2:
                ra.name = 'Monitor'
            else:
                ra.name = 'Operator'
            db.session.add(ra)
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


def r_path(relative_path):
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    # Fixing multimedia folder not found issue
    if '/' in relative_path or '\\' in relative_path:
        relative_path = ('\\' if os.name == 'nt' else '/').join(
            relative_path.split('\\' if os.name == 'nt' else '/'))
    return os.path.join(base_path, relative_path)


def solve_path(path):
    ''' fix path for window os '''
    return path.replace('/', '\\') if os.name == 'nt' else path
