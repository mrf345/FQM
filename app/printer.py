# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import usb.core
import usb.util
from escpos import printer as getp
from datetime import datetime
import os
import sys
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from ex_functions import r_path
from os import remove, getcwd, path, name
from database import version


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


def printit(printer, ticket, office, tnumber,
            task, cticket, site='https://fqms.github.io'):
    printer.set(align='center', height=4, width=4)
    printer.text("FQM\n")
    printer.set(align='center', height=1, width=1)
    printer.text("Version " + version)
    printer.set('center', 'a', 'u', 1, 1)
    printer.text("\n" + site + "\n")
    printer.set(align='center', height=1, width=2)
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='center', height=3, width=3)
    printer.text("\n" + str(ticket) + "\n")
    printer.set(align='center', height=1, width=2)
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='left', height=1, width=1)
    printer.text("\nOffice : " + str(office).encode('utf-8') + "\n")
    printer.text("\nCurrent ticket : " + str(cticket).encode('utf-8') + "\n")
    printer.text("\nTickets ahead : " + str(tnumber) + "\n")
    try:
        printer.text("\nTask : " + str(task) + "\n")
    except:
        pass
    printer.text("\nTime : " + str(datetime.utcnow())[:-7] + "\n")
    printer.cut()
    return printer


def assign(v, p, in_ep, out_ep):
    try:
        printer = getp.Usb(v, p, 0, in_ep, out_ep)
        printer.text("\n")
        return printer
    except:
        return None


def listp():
    vl = []
    for ll in usb.core.find(find_all=True, custom_match=find_class(7)):
        cfg = ll.get_active_configuration()
        in_ep = int(cfg[(0, 0)][0].bEndpointAddress)
        out_ep = int(cfg[(0, 0)][1].bEndpointAddress)
        vl.append([ll.idVendor, ll.idProduct,
                   in_ep, out_ep])
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

    logo = 'FQM 0.2'
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
    except:
        taskt = tas
    task = arabic_reshaper.reshape(taskt)
    task = get_display(task)
    datet = u'الوقت : '
    datet += str(datetime.utcnow())[:-7]
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
