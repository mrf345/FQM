# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
from random import randint
from socket import socket, AF_INET, SOCK_STREAM
from netifaces import interfaces, ifaddresses

import app.data as data
from app.database import db


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
    for o in data.Office.query:
        if data.Serial.query.filter_by(office_id=o.id).first() is None:
            tk = o.tasks
            if len(tk) > 0:
                for t in tk:
                    dd = data.Serial(100, o.id, t.id, None, False)
                    dd.p = True
                    db.session.add(dd)
            else:
                dd = data.Serial(100, o.id, 1, None, False)
                dd.p = True
                db.session.add(dd)
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
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    # Fixing multimedia folder not found issue
    if '/' in relative_path or '\\' in relative_path:
        relative_path = ('\\' if os.name == 'nt' else '/').join(
            relative_path.split('\\' if os.name == 'nt' else '/'))
    return os.path.join(base_path, relative_path)


def solve_path(path):
    """ fix path for window os """
    return path.replace('/', '\\') if os.name == 'nt' else path


def get_accessible_ips():
    """ Utility to retrieve accessible ips.

    Returns
    -------
        List of accessible ips and the interface name `(interface, ip)`
    """
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
    """ Utility to check if port is available on a given local address.

    Parameters
    ----------
        ip: str
            local ip address to try the port on.
        port: int
            port to check for its availability.

    Returns
    -------
        True if port is available, False if not.
    """
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
    """ Utility to get an available port to listen on.

    Parameters
    ----------
        ip: str
            local ip address to try the port on.

    Returns
    -------
        Interger of any available random port.
    """
    available_port = None

    while not available_port:
        random_port = randint(1000, 9999)
        available_port = is_port_available(ip, random_port) and random_port

    return available_port
