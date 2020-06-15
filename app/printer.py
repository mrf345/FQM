import uuid
import usb.core
import usb.util
import arabic_reshaper
from escpos import printer as getp
from escpos.printer import Dummy
from datetime import datetime
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
from os import remove, getcwd, path, name, system

from app.utils import absolute_path, get_with_alias, log_error, convert_to_int_or_hex, execute
from app.middleware import gtranslator
from app.constants import VERSION, PRINTED_TICKET_DIMENSIONS, PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH


class find_class(object):
    def __init__(self, class_):
        self._class = class_

    def __call__(self, device):
        if device.bDeviceClass == self._class:
            return True

        for cfg in device:
            intf = usb.util.find_descriptor(cfg, bInterfaceClass=self._class)
            if intf is not None:
                return True

        return False


def get_font_height_width(font='regular', scale=1):
    ''' helper to retrieve the font size based on the given scale.
        TODO: Figure out scaling for Arabic drawn tickets.

    Parameters
    ----------
        font: str
            font to calculate the scaled size for.
        scale: int
            scale to multiple the font size by.

    Returns
    -------
        Dict of scaled `height` and `width`.

    '''
    dimensions = PRINTED_TICKET_DIMENSIONS
    height, width = dimensions.get(font, dimensions['regular'])

    def multiply_within_limit(height_or_width):
        outcome = int(height_or_width * scale)

        # NOTE: Will limit the heightest width and height to avoid raising exception
        # escpos.exceptions.SetVariableError: Set variable out of range
        return (PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                if outcome > PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                else outcome)

    return {'height': multiply_within_limit(height),
            'width': multiply_within_limit(width)}


def get_printers_usb():
    ''' Get list of printers via `PyUSB.core.find`.

    Returns
    -------
        List of printers details. Example::
            [{'vendor': int, 'product': int, 'in_ep': int, 'out_ep': int}, ...]
    '''
    printers = []

    try:
        for printer in usb.core.find(find_all=True, custom_match=find_class(7)):
            details = {}
            details['vendor'] = convert_to_int_or_hex(printer.idVendor)
            details['product'] = convert_to_int_or_hex(printer.idProduct)

            try:
                configuration = printer.get_active_configuration()
                in_ep = configuration[(0, 0)][0].bEndpointAddress
                out_ep = configuration[(0, 0)][1].bEndpointAddress
                details['in_ep'] = convert_to_int_or_hex(in_ep)
                details['out_ep'] = convert_to_int_or_hex(out_ep)
            except Exception:
                pass

            printers.append(details)
    except Exception as exception:
        log_error(exception)

    return printers


def get_printers_cli(windows=False, unix=False):
    '''Get list of printers via `os.system('lpstat - a')`

    Parameters
    ----------
        windows: bool
            if Windows system
        unix: bool
            if unix-like system

    Returns
    -------
        list of printer names.
    '''
    printers = []

    if unix:
        printers += [p.split(' ')[0]
                     for p in execute('lpstat -a', parser='\n')
                     if p.split(' ')]
    elif windows:
        printers += execute('wmic printer get sharename',
                            parser='\n',
                            encoding='utf-16'
                            )[1:]

    return printers


def assign(vendor_id, product_id, in_ep=None, out_ep=None):
    ''' Assign a new printer session and attach it.

    Parameters
    __________
        vendor_id: int
        product_id: int
        in_ep: int
        out_ep: int

    Returns
    -------
        ESCPOS Printer instance.
    '''
    args = [vendor_id, product_id, 0]

    if in_ep and out_ep:
        args += [in_ep, out_ep]

    printer = getp.Usb(*args)
    printer.text("\n")

    return printer


def get_translation(text, language):
    translated = gtranslator.translate(text, dest=[language])

    if language == 'en':
        translated = get_with_alias().get(text) or translated

    return translated


def printit(printer, ticket, office, tnumber,
            task, cticket, site='https://fqms.github.io', lang='en',
            scale=1):
    printer.set(align='center', **get_font_height_width('logo', scale))
    printer.text("FQM\n")
    printer.set(align='center', **get_font_height_width('regular', scale))
    printer.text(get_translation('Version ', lang) + VERSION)
    printer.set('center', 'a', 'u', **get_font_height_width('regular', scale))
    printer.text("\n" + site + "\n")
    printer.set(align='center', **get_font_height_width('spacer', scale))
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='center', **get_font_height_width('large', scale))
    printer.text("\n" + str(ticket) + "\n")
    printer.set(align='center', **get_font_height_width('spacer', scale))
    printer.text("\n" + '-' * 15 + "\n")
    printer.set(align='left', **get_font_height_width('regular', scale))
    printer.text(f'\n{get_translation("Office : ", lang)}{office}\n')
    printer.text(f'\n{get_translation("Current ticket : ", lang)}{cticket}\n')
    printer.text(f'\n{get_translation("Tickets ahead : ", lang)}{tnumber}\n')
    try:
        printer.text(f'\n{get_translation("Task : ", lang)}{task}\n')
    except Exception:
        pass
    printer.text(f'{get_translation("Time : ", lang)}{datetime.now().__str__()[:-7]}\n')
    printer.cut()
    return printer


def print_ticket_cli(printer, ticket, office, tickets_ahead, task, current_ticket,
                     host='localhost', language='en', scale=1, windows=False, unix=False):
    '''Print a ticket through the Command-Line interface.

    Parameters
    ----------
    printer : str
        the printer name.
    ticket : int
        ticket number.
    office : str
        office number and prefix.
    tickets_ahead : int
        number of tickets ahead.
    task : str
        task's name.
    current_ticket : int
        current ticket in the queue.
    host : str, optional
        host to find printer on, by default 'localhost'
    language : str, optional
        printing language, by default 'en'
    scale : int, optional
        ticket font scale, by default 1
    windows : bool, optional
        if printing on Windows, by default False
    unix : bool, optional
        if printing on Unix-like, by default False
    '''
    ticket_content = printit(Dummy(), ticket, office, tickets_ahead, task,
                             current_ticket, lang=language, scale=scale).output
    file_path = path.join(getcwd(),
                          f'{uuid.uuid4()}'.replace('-', '') + '.txt')

    with open(file_path, 'wb+') as file:
        file.write(ticket_content)

    if unix:
        system(f'lp -d "{printer}" -o raw "{file_path}"')
    elif windows:
        system(f'print /D:\\\{host}\\"{printer}" "{file_path}"')

    if path.isfile(file_path):
        remove(file_path)


def printit_ar(pname, ti, ofc, tnu, tas, cticket, **kwargs):
    def fsizeit(text, t, f):
        ltxt = "A" * len(t)
        return f.getsize(t)

    def center(text, t, f):
        fs1, fs2 = fsizeit(text, t, f)
        return ((text.size[0] - fs1) / 2, (text.size[1] - fs2) / 2)
    if name == 'nt':
        fpath = absolute_path('static\\gfonts\\arial.ttf')
    else:
        fpath = absolute_path('static/gfonts/arial.ttf')
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
    pname.image(finame, fragment_height=tt, high_density_vertical=True)
    pname.cut()
    pname.close()
    if path.isfile(finame):
        remove(finame)


def print_ticket_cli_ar(pname, ti, ofc, tnu, tas, cticket, host='localhost', **kwargs):
    def fsizeit(text, t, f):
        return f.getsize(t)

    def center(text, t, f):
        fs1, fs2 = fsizeit(text, t, f)
        return ((text.size[0] - fs1) / 2, (text.size[1] - fs2) / 2)

    fpath = absolute_path('static/gfonts/arial.ttf')
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

    if kwargs.get('windows'):
        system(f'print /D:\\\{host}\\"{pname}" "{sffs[1]}"')
    elif kwargs.get('unix'):
        system(f'lp -d "{pname}" -o raw "{sffs[1]}"')

    for f in sffs:
        if path.isfile(f):
            remove(f)
