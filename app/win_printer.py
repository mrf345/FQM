# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import _winreg
import win32com.client
from printer import printit
from os import system, remove, getcwd, path, name
from escpos.printer import Dummy
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from ex_functions import r_path
from database import version


def check_win_p():
    try:
        from pythoncom import CoInitialize as coli
        coli()
        strComputer = "."
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(
            strComputer, "root\cimv2")
        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity")
        for objItem in colItems:
            if "Printing" in str(objItem.
                                 Name) and "USB" in str(objItem.DeviceID):
                return True
    except:
        return None


def printers():
    '''Produces tuples containing a printer and the printer port.
        It i a generator function.'''

    path = r'SYSTEM\CurrentControlSet\Control\Print\Printers'
    hKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, path)
    subkeyCnt, valuesCnt, modtime = _winreg.QueryInfoKey(hKey)

    for n in xrange(subkeyCnt):
        subName = _winreg.EnumKey(hKey, n)
        p2 = path + '\\' + subName
        hK2 = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, p2)

        yield (_winreg.QueryValueEx(hK2, 'Name')[0],
               _winreg.QueryValueEx(hK2, 'Port')[0],
               _winreg.QueryValueEx(hK2, 'ChangeID')[0])
        _winreg.CloseKey(hK2)
    _winreg.CloseKey(hKey)


def listpp():
    lps = []
    try:
        for ups in printers():
            if ups[1][:3] == "USB":
                lps.append(ups[0])
    except:
        pass
    return lps


def printwin(pname, a, b, c, d, cit, l, ip):
    outp = printit(Dummy(), a, b, c, d, cit, lang=l)
    outp = outp.output
    fname = "dummy.txt"
    ffname = path.join(getcwd(), fname)
    f = open(ffname, 'w')
    f.write(outp)
    f.close()
    lh = ip
    txt = 'print /D:\\\%s\\"%s" "%s"' % (lh, pname, ffname)
    system(txt)
    if path.isfile(ffname):
        remove(ffname)


def printwin_ar(pname, ti, ofc, tnu, tas, cticket, ip):
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

    logo = 'FQM ' + version[:4]
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
    sfs = ['dummy.jpg', 'dummy.txt']
    for f in sfs:
        sffs.append(path.join(getcwd(), f))
    mt.save(sfs[0], format="JPEG")
    p = Dummy()
    p.image(sfs[0], fragment_height=tt, high_density_vertical=True)
    p.cut()
    f = open(sfs[1], 'w')
    f.write(p.output)
    p.close()
    f.close()
    lh = ip
    text = 'print /D:\\\%s\\"%s" "%s"' % (lh, pname, sfs[1])
    system(text)
    for f in sffs:
        if path.isfile(f):
            remove(f)
