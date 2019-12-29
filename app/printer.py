# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import uuid
import usb.core
import usb.util
import arabic_reshaper
from escpos import printer as getp
from escpos.printer import Dummy
from datetime import datetime
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
from os import remove, getcwd, path, name, popen, system

from app.utils import r_path, get_with_alias
from app.constants import VERSION
from app.middleware import gtranslator


def get_windows_printers():
    ''' List Windows available printers using `wmic` system command.

    Returns
    -------
        List of available printers on Windows.
    '''
    printers = []

    with popen('wmic printer get sharename') as output:
        printers += [
            p.strip()
            for p in output.read().split('\n\n')[1:]
            if p.strip()
        ]

    return printers


class find_class(object):
    def __init__(self, class_):
        self._class = class_

    def __call__(self, device):
        # first, let's check the device
        if device.bDeviceClass == self._class:
            return True
        # ok, transverse all devices to find an
        # interface that matches our class
        for cfg in device:
            # find_descriptor: what's it?
            intf = usb.util.find_descriptor(cfg, bInterfaceClass=self._class)
            if intf is not None:
                return True

        return False


def get_translation(text, language):
    translated = gtranslator.translate(text, dest=[language])

    if language == 'en':
        translated = get_with_alias().get(text) or translated

    return translated


def printit(printer, ticket, office, tnumber,
            task, cticket, site='https://fqms.github.io', lang='en'):
    printer.set(align='center', height=4, width=4)
    printer.text("FQM\n")
    printer.set(align='center', height=1, width=1)
    printer.text(get_translation('Version ', lang) + VERSION)
    printer.set('center', 'a', 'u', 1, 1)
    printer.text("\n" + site + "\n")
    printer.set(align='center', height=1, width=2)
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='center', height=3, width=3)
    printer.text("\n" + str(ticket) + "\n")
    printer.set(align='center', height=1, width=2)
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='left', height=1, width=1)
    printer.text(f'\n{get_translation("Office : ", lang)}{office}\n')
    printer.text(f'\n{get_translation("Current ticket : ", lang)}{cticket}\n')
    printer.text(f'\n{get_translation("Tickets ahead : ", lang)}{tnumber}\n')
    try:
        printer.text(f'\n{get_translation("Task : ", lang)}{task}\n')
    except Exception:
        pass
    printer.text(f'{get_translation("Time : ", lang)}{datetime.now()[:-7]}\n')
    printer.cut()
    return printer


def print_ticket_windows(pname, a, b, c, d, cit, l, ip):
    content = printit(Dummy(), a, b, c, d, cit, lang=l).output
    file_path = path.join(getcwd(),
                          f'{uuid.uuid4()}'.replace('-', '') + '.txt')

    with open(file_path, 'wb+') as file:
        file.write(content)

    system(f'print /D:\\\localhost\\"{pname}" "{file_path}"')
    path.isfile(file_path) and remove(file_path)


def assign(v, p, in_ep, out_ep):
    try:
        printer = getp.Usb(v, p, 0, in_ep, out_ep)
        printer.text("\n")
        return printer
    except Exception:
        return None


def listp():
    vl = []
    try:
        for ll in usb.core.find(find_all=True, custom_match=find_class(7)):
            cfg = ll.get_active_configuration()
            in_ep = int(cfg[(0, 0)][0].bEndpointAddress)
            out_ep = int(cfg[(0, 0)][1].bEndpointAddress)
            vl.append([ll.idVendor, ll.idProduct, in_ep, out_ep])
    except Exception:
        pass
    return vl


def printit_ar(pname, ti, ofc, tnu, tas, cticket):
    def fsizeit(text, t, f):
        ltxt = "A" * len(t)
        return f.getsize(t)

    def center(text, t, f):
        fs1, fs2 = fsizeit(text, t, f)
        return ((text.size[0] - fs1) / 2, (text.size[1] - fs2) / 2)
    if name == 'nt':
        fpath = r_path('static\\gfonts\\arial.ttf')
    else:
        fpath = r_path('static/gfonts/arial.ttf')
    fonts = [ImageFont.truetype(fpath, 50),
             ImageFont.truetype(fpath, 30),
             ImageFont.truetype(fpath, 25)]

    logo = 'FQM ' + VERSION[:4]
    title = u'نظام إدارة الحشود الحر'
    title = arabic_reshaper.reshape(title)
    title = get_display(title)
    link = 'http://fqms.github.io'
    border = "#" * 20
    ticket = str(ti)
    officet = u'المكتب : ' + ofc
    office = arabic_reshaper.reshape(officet)
    office = get_display(office)
    try:
        taskt = u'المهمة : ' + tas
    except Exception:
        taskt = tas
    task = arabic_reshaper.reshape(taskt)
    task = get_display(task)
    datet = u'الوقت : '
    datet += str(datetime.now())[:-7]
    date = arabic_reshaper.reshape(datet)
    date = get_display(date)
    aheadt = u'تذاكر قبلك : '
    aheadt += str(tnu)
    ahead = arabic_reshaper.reshape(aheadt)
    ahead = get_display(ahead)
    cutit = u'التذكرة الحالية : '
    cutit += str(cticket)
    cuti = arabic_reshaper.reshape(cutit)
    cuti = get_display(cuti)

    w = 400
    bt_1 = Image.new('RGB', (w, 60), "white")
    bt_2 = Image.new('RGB', (w, 60), "white")
    bt_3 = Image.new('RGB', (w, 60), "white")
    st_1 = Image.new('RGB', (w, 50), "white")
    st_2 = Image.new('RGB', (w, 50), "white")
    st_3 = Image.new('RGB', (w, 50), "white")
    st_4 = Image.new('RGB', (w, 50), "white")
    st_5 = Image.new('RGB', (w, 50), "white")
    st_6 = Image.new('RGB', (w, 50), "white")
    st_7 = Image.new('RGB', (w, 50), "white")
    st_8 = Image.new('RGB', (w, 50), "white")
    tt = 50 * 8
    tt += 60 * 3
    mt = Image.new('RGB', (w, tt), "white")

    bd_1 = ImageDraw.Draw(bt_1)
    bd_2 = ImageDraw.Draw(bt_2)
    bd_3 = ImageDraw.Draw(bt_3)
    sd_1 = ImageDraw.Draw(st_1)
    sd_2 = ImageDraw.Draw(st_2)
    sd_3 = ImageDraw.Draw(st_3)
    sd_4 = ImageDraw.Draw(st_4)
    sd_5 = ImageDraw.Draw(st_5)
    sd_6 = ImageDraw.Draw(st_6)
    sd_7 = ImageDraw.Draw(st_7)
    sd_8 = ImageDraw.Draw(st_8)
    md = ImageDraw.Draw(mt)

    b = "black"
    bd_1.text(center(bt_1, logo, fonts[0]), logo,
              font=fonts[0], fill=b)
    bd_2.text(center(bt_2, title, fonts[1]), title,
              font=fonts[1], fill=b)
    bd_3.text(center(bt_3, ticket, fonts[0]), ticket,
              font=fonts[0], fill=b)
    sd_1.text(center(st_1, link, fonts[2]), link, font=fonts[2], fill=b)
    sd_2.text(center(st_2, border, fonts[2]), border, font=fonts[2], fill=b)
    sd_3.text(center(st_3, border, fonts[2]), border, font=fonts[2], fill=b)
    sd_4.text(center(st_4, office, fonts[2]), office, font=fonts[2], fill=b)
    sd_5.text(center(st_5, task, fonts[2]), task, font=fonts[2], fill=b)
    sd_6.text(center(st_6, date, fonts[2]), date, font=fonts[2], fill=b)
    sd_7.text(center(st_7, ahead, fonts[2]), ahead, font=fonts[2], fill=b)
    sd_8.text(center(st_8, cuti, fonts[2]), cuti, font=fonts[2], fill=b)

    tts = 0
    mt.paste(bt_1, (0, 0))
    tts += bt_1.size[1]
    mt.paste(bt_2, (0, tts))
    tts += bt_2.size[1]
    mt.paste(st_1, (0, tts))
    tts += st_1.size[1]
    mt.paste(st_2, (0, tts))
    tts += st_2.size[1]
    mt.paste(bt_3, (0, tts))
    tts += bt_3.size[1]
    mt.paste(st_3, (0, tts))
    tts += st_3.size[1]
    mt.paste(st_4, (0, tts))
    tts += st_4.size[1]
    mt.paste(st_8, (0, tts))
    tts += st_8.size[1]
    mt.paste(st_7, (0, tts))
    tts += st_7.size[1]
    mt.paste(st_5, (0, tts))
    tts += st_5.size[1]
    mt.paste(st_6, (0, tts))

    iname = 'dummy.jpg'
    finame = path.join(getcwd(), iname)
    mt.save(iname, format="JPEG")
    pname.image(iname, fragment_height=tt, high_density_vertical=True)
    pname.cut()
    pname.close()
    if path.isfile(finame):
        remove(finame)


def print_ticket_windows_ar(pname, ti, ofc, tnu, tas, cticket, ip):
    def fsizeit(text, t, f):
        return f.getsize(t)

    def center(text, t, f):
        fs1, fs2 = fsizeit(text, t, f)
        return ((text.size[0] - fs1) / 2, (text.size[1] - fs2) / 2)

    if name == 'nt':
        fpath = r_path('static\\gfonts\\arial.ttf')
    else:
        fpath = r_path('static/gfonts/arial.ttf')
    fonts = [ImageFont.truetype(fpath, 50),
             ImageFont.truetype(fpath, 30),
             ImageFont.truetype(fpath, 25)]

    logo = 'FQM ' + VERSION[:4]
    title = u'نظام إدارة الحشود الحر'
    title = arabic_reshaper.reshape(title)
    title = get_display(title)
    link = 'http://fqms.github.io'
    border = "#" * 20
    ticket = str(ti)
    officet = u'المكتب : ' + ofc
    office = arabic_reshaper.reshape(officet)
    office = get_display(office)
    try:
        taskt = u'المهمة : ' + tas
    except Exception:
        taskt = tas
    task = arabic_reshaper.reshape(taskt)
    task = get_display(task)
    datet = u'الوقت : '
    datet += str(datetime.now())[:-7]
    date = arabic_reshaper.reshape(datet)
    date = get_display(date)
    aheadt = u'تذاكر قبلك : '
    aheadt += str(tnu)
    ahead = arabic_reshaper.reshape(aheadt)
    ahead = get_display(ahead)
    cutit = u'التذكرة الحالية : '
    cutit += str(cticket)
    cuti = arabic_reshaper.reshape(cutit)
    cuti = get_display(cuti)

    w = 400
    bt_1 = Image.new('RGB', (w, 60), "white")
    bt_2 = Image.new('RGB', (w, 60), "white")
    bt_3 = Image.new('RGB', (w, 60), "white")
    st_1 = Image.new('RGB', (w, 50), "white")
    st_2 = Image.new('RGB', (w, 50), "white")
    st_3 = Image.new('RGB', (w, 50), "white")
    st_4 = Image.new('RGB', (w, 50), "white")
    st_5 = Image.new('RGB', (w, 50), "white")
    st_6 = Image.new('RGB', (w, 50), "white")
    st_7 = Image.new('RGB', (w, 50), "white")
    st_8 = Image.new('RGB', (w, 50), "white")
    tt = 50 * 8
    tt += 60 * 3
    mt = Image.new('RGB', (w, tt), "white")

    bd_1 = ImageDraw.Draw(bt_1)
    bd_2 = ImageDraw.Draw(bt_2)
    bd_3 = ImageDraw.Draw(bt_3)
    sd_1 = ImageDraw.Draw(st_1)
    sd_2 = ImageDraw.Draw(st_2)
    sd_3 = ImageDraw.Draw(st_3)
    sd_4 = ImageDraw.Draw(st_4)
    sd_5 = ImageDraw.Draw(st_5)
    sd_6 = ImageDraw.Draw(st_6)
    sd_7 = ImageDraw.Draw(st_7)
    sd_8 = ImageDraw.Draw(st_8)
    md = ImageDraw.Draw(mt)

    b = "black"
    bd_1.text(center(bt_1, logo, fonts[0]), logo,
              font=fonts[0], fill=b)
    bd_2.text(center(bt_2, title, fonts[1]), title,
              font=fonts[1], fill=b)
    bd_3.text(center(bt_3, ticket, fonts[0]), ticket,
              font=fonts[0], fill=b)
    sd_1.text(center(st_1, link, fonts[2]), link, font=fonts[2], fill=b)
    sd_2.text(center(st_2, border, fonts[2]), border, font=fonts[2], fill=b)
    sd_3.text(center(st_3, border, fonts[2]), border, font=fonts[2], fill=b)
    sd_4.text(center(st_4, office, fonts[2]), office, font=fonts[2], fill=b)
    sd_5.text(center(st_5, task, fonts[2]), task, font=fonts[2], fill=b)
    sd_6.text(center(st_6, date, fonts[2]), date, font=fonts[2], fill=b)
    sd_7.text(center(st_7, ahead, fonts[2]), ahead, font=fonts[2], fill=b)
    sd_8.text(center(st_8, cuti, fonts[2]), cuti, font=fonts[2], fill=b)

    tts = 0
    mt.paste(bt_1, (0, 0))
    tts += bt_1.size[1]
    mt.paste(bt_2, (0, tts))
    tts += bt_2.size[1]
    mt.paste(st_1, (0, tts))
    tts += st_1.size[1]
    mt.paste(st_2, (0, tts))
    tts += st_2.size[1]
    mt.paste(bt_3, (0, tts))
    tts += bt_3.size[1]
    mt.paste(st_3, (0, tts))
    tts += st_3.size[1]
    mt.paste(st_4, (0, tts))
    tts += st_4.size[1]
    mt.paste(st_8, (0, tts))
    tts += st_8.size[1]
    mt.paste(st_7, (0, tts))
    tts += st_7.size[1]
    mt.paste(st_5, (0, tts))
    tts += st_5.size[1]
    mt.paste(st_6, (0, tts))

    sffs = []
    sfs = [
        f'{uuid.uuid4()}'.replace('-', '') + '.jpg',
        f'{uuid.uuid4()}'.replace('-', '') + '.txt'
    ]

    for f in sfs:
        sffs.append(path.join(getcwd(), f))
    mt.save(sfs[0], format="JPEG")
    p = Dummy()
    p.image(sfs[0], fragment_height=tt, high_density_vertical=True)
    p.cut()
    f = open(sfs[1], 'wb+')
    f.write(p.output)
    p.close()
    f.close()

    text = f'print /D:\\\localhost\\"{pname}" "{sfs[1]}"'
    system(text)
    for f in sffs:
        if path.isfile(f):
            remove(f)
