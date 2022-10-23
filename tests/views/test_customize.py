import os
import pytest
import io
import usb.core
from unittest.mock import MagicMock
from collections import namedtuple

import app.printer
import app.views.customize
import app.tasks.cache_tickets_tts
from app.middleware import db
from app.helpers import get_tts_safely
from app.database import (Touch_store, Display_store, Printer, Slides_c,
                          Vid, Media, Slides, Aliases, Settings, Serial)


@pytest.mark.usefixtures('c')
def test_welcome_customize(c):
    response = c.get('/customize', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert 'Customization' in page_content


@pytest.mark.usefixtures('c')
def test_ticket_registered(c):
    with c.application.app_context():
        touch_screen_settings = Touch_store.get()
        touch_screen_settings.n = True
        db.session.commit()

    printer_value = 1
    response = c.post('/ticket',
                      data={'value': printer_value},
                      follow_redirects=True)

    assert response.status == '200 OK'
    assert Printer.get().value == printer_value
    assert Printer.get().active is False
    assert Touch_store.get().n is True


@pytest.mark.usefixtures('c')
def test_ticket_printed(c, monkeypatch):
    vendor = 50
    product = 3
    in_ep = 130
    out_ep = 170
    in_config = namedtuple('in_config', ['bEndpointAddress'])
    usb_device = namedtuple('usb', ['get_active_configuration', 'idVendor', 'idProduct'])
    mock_usb_find = MagicMock(return_value=[usb_device(
        lambda: {(0, 0): [in_config(in_ep), in_config(out_ep)]},
        vendor,
        product)])
    monkeypatch.setattr(usb.core, 'find', mock_usb_find)

    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    db.session.commit()

    printer_value = 1
    kind = 2  # NOTE: Printed
    lang = 'en'
    printers = f'{vendor}_{product}_{in_ep}_{out_ep}'
    scale = 2
    response = c.post('/ticket', data={
        'value': printer_value,
        'kind': kind,
        'langu': lang,
        'printers': printers,
        'scale': scale
    }, follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert Touch_store.get().n is False
    assert Printer.get().active is True
    assert Printer.get().value == printer_value
    assert Printer.get().langu == lang
    assert Printer.get().scale == scale
    assert Printer.get().in_ep == in_ep
    assert Printer.get().out_ep == out_ep
    assert Printer.get().vendor == vendor
    assert Printer.get().product == product
    assert f'value="{printers}"' in page_content
    assert mock_usb_find.call_count == 2


@pytest.mark.usefixtures('c')
def test_ticket_printed_windows(c, monkeypatch):
    name = 'testing_printer'
    secondName = 'second_testing_printer'
    printers = ['', name, secondName]
    mock_execute = MagicMock(return_value=printers)
    mock_os = MagicMock()
    mock_os.name = 'nt'
    monkeypatch.setattr(app.printer, 'execute', mock_execute)
    monkeypatch.setattr(app.views.customize, 'os', mock_os)
    monkeypatch.setattr(app.forms.customize, 'os', mock_os)

    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    db.session.commit()

    printer_value = 1
    kind = 2  # NOTE: Printed
    lang = 'en'
    scale = 2
    response = c.post('/ticket', data={
        'value': printer_value,
        'kind': kind,
        'langu': lang,
        'printers': name,
        'scale': scale
    }, follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert Touch_store.get().n is False
    assert Printer.get().active is True
    assert Printer.get().value == printer_value
    assert Printer.get().langu == lang
    assert Printer.get().scale == scale
    assert Printer.get().name == name
    assert f'value="{name}"' in page_content
    assert mock_execute.call_count == 2
    mock_execute.assert_called_with('wmic printer get sharename',
                                    parser='\n',
                                    encoding='utf-16')


@pytest.mark.usefixtures('c')
def test_ticket_printed_lp(c, monkeypatch):
    name = 'testing_printer'
    secondName = 'testing_second_printer'
    printers = [f'{name} description stuff testing',
                f'{secondName} description stuff testing']
    mock_execute = MagicMock(return_value=printers)
    monkeypatch.setattr(app.printer, 'execute', mock_execute)
    monkeypatch.setattr(app.views.customize, 'os', MagicMock(name='linux'))
    monkeypatch.setattr(app.forms.customize, 'os', MagicMock(name='nt'))

    settings = Settings.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    settings.lp_printing = True
    db.session.commit()

    printer_value = 1
    kind = 2  # NOTE: Printed
    lang = 'en'
    scale = 2
    response = c.post('/ticket', data={
        'value': printer_value,
        'kind': kind,
        'langu': lang,
        'printers': secondName,
        'scale': scale
    }, follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert Touch_store.get().n is False
    assert Printer.get().active is True
    assert Printer.get().value == printer_value
    assert Printer.get().langu == lang
    assert Printer.get().scale == scale
    assert Printer.get().name == secondName
    assert f'value="{secondName}"' in page_content
    assert mock_execute.call_count == 2
    mock_execute.assert_called_with('lpstat -a', parser='\n')


@pytest.mark.usefixtures('c')
def test_video(c):
    name = 'testing.mp4'
    ar = 1
    controls = 2
    mute = 2
    enable = 1

    slides_settings = Slides_c.get()
    slides_settings.status = False
    video_settings = Vid.get()
    video_settings.enabled = True
    video = Media(True, name=name)
    db.session.add(video)
    db.session.commit()
    video_id = video.id

    response = c.post('/video', data={
        'video': video_id,
        'ar': ar,
        'enable': enable,
        'mute': mute,
        'controls': controls
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Vid.get().enable == enable
    assert Vid.get().vname == name
    assert Vid.get().mute == mute
    assert Vid.get().ar == ar
    assert Vid.get().controls == controls
    assert Vid.get().vkey == video_id
    assert Media.get(video_id).used is True


@pytest.mark.usefixtures('c')
def test_slideshow(c):
    slides_settings = Slides_c.get()
    slides_settings.status = True
    video_settings = Vid.get()
    video_settings.enabled = False
    db.session.commit()

    response = c.get('/slideshow', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    for slide in Slides.query.all():
        assert f'{slide.id}. {slide.title}' in page_content


@pytest.mark.usefixtures('c')
def test_add_slide(c):
    slides_settings = Slides_c.get()
    slides_settings.status = True
    video_settings = Vid.get()
    video_settings.enabled = False
    db.session.commit()

    properties = {'title': 'testing_title',
                  'hsize': '150%',
                  'hcolor': 'testing_hcolor',
                  'hfont': 'testing_hfont',
                  'hbg': 'testing_hbg',
                  'subti': 'teesting_subti',
                  'tsize': '150%',
                  'tcolor': 'testing_tcolor',
                  'tfont': 'testing_tfont',
                  'tbg': 'testing_tbg'}
    data = {'background': 0, **properties}
    response = c.post('/slide_a', data=data, follow_redirects=True)

    assert response.status == '200 OK'
    for key, value in properties.items():
        assert Slides.query.filter_by(**{key: value}).first() is not None


@pytest.mark.usefixtures('c')
def test_add_slide_image(c):
    slides_settings = Slides_c.get()
    slides_settings.status = True
    video_settings = Vid.get()
    video_settings.enabled = False
    background = Media(img=True, name='testing.jpg')
    db.session.add(background)
    db.session.commit()
    background_id = background.id

    properties = {'title': 'testing_title',
                  'hsize': '150%',
                  'hcolor': 'testing_hcolor',
                  'hfont': 'testing_hfont',
                  'hbg': 'testing_hbg',
                  'subti': 'teesting_subti',
                  'tsize': '150%',
                  'tcolor': 'testing_tcolor',
                  'tfont': 'testing_tfont',
                  'tbg': 'testing_tbg'}
    data = {'background': background_id, **properties}
    response = c.post('/slide_a', data=data, follow_redirects=True)

    assert response.status == '200 OK'
    assert background_id != 0
    for key, value in properties.items():
        slide = Slides.query.filter_by(**{key: value}).first()

        assert slide is not None
        assert slide.ikey == background_id


@pytest.mark.usefixtures('c')
def test_update_slide(c):
    slides_settings = Slides_c.get()
    slides_settings.status = True
    db.session.commit()

    rotation = '3000'
    navigation = 2
    effect = 'fade'
    status = 1
    response = c.post('/slide_c', data={
        'rotation': rotation,
        'navigation': navigation,
        'effect': effect,
        'status': status
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Slides_c.get().rotation == rotation
    assert Slides_c.get().navigation == navigation
    assert Slides_c.get().effect == effect
    assert Slides_c.get().status == status


@pytest.mark.usefixtures('c')
def test_remove_slide(c):
    slide = Slides.get()
    response = c.get(f'/slide_r/{slide.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Slides.get(slide.id) is None


@pytest.mark.usefixtures('c')
def test_multimedia(c):
    name = 'test.jpg'
    content = b'testing image'
    data = {'mf': (io.BytesIO(content), name)}

    response = c.post('/multimedia/1',
                      data=data,
                      follow_redirects=True,
                      content_type='multipart/form-data')

    assert response.status == '200 OK'
    assert Media.query.filter_by(name=name).first() is not None


@pytest.mark.usefixtures('c')
def test_multimedia_wrong_extension(c):
    name = 'test.wrn'
    content = b'testing wrong'
    data = {'mf': (io.BytesIO(content), name)}

    response = c.post('/multimedia/1',
                      data=data,
                      follow_redirects=True,
                      content_type='multipart/form-data')

    assert response.status == '200 OK'
    assert Media.query.filter_by(name=name).first() is None


@pytest.mark.usefixtures('c')
def test_delete_multimedia(c):
    media = Media(True, False, False, False, 'testing.mp3')
    db.session.add(media)
    db.session.commit()
    media_id = media.id

    response = c.get(f'/multi_del/{media_id}', follow_redirects=True)

    assert media_id != 0
    assert response.status == '200 OK'
    assert Media.get(media_id) is None


@pytest.mark.usefixtures('c')
def test_display_screen_customization(c):
    properties = {
        'title': 'testing',
        'hsize': '500%',
        'hcolor': 'testing',
        'hbg': 'testing',
        'tsize': '200%',
        'tcolor': 'testing',
        'h2size': '150%',
        'h2color': 'testing',
        'ssize': '500%',
        'scolor': 'testing',
        'mduration': '2000',
        'hfont': 'testing',
        'tfont': 'testing',
        'h2font': 'testing',
        'sfont': 'testing',
        'rrate': '2000',
        'anr': 3,
        'anrt': 'each',
        'effect': 'bounce',
        'repeats': '2',
        'prefix': True,
        'always_show_ticket_number': True,
        'bgcolor': 'testing',
        'hide_ticket_index': True
    }
    data = {f'check{s}': True for s in get_tts_safely().keys()}
    data.update({'display': 1,
                 'background': 0,
                 'naudio': 0,
                 **properties})

    response = c.post('/displayscreen_c/1', data=data, follow_redirects=True)

    assert response.status == '200 OK'
    for key, value in properties.items():
        assert getattr(Display_store.get(), key, None) == value


@pytest.mark.usefixtures('c')
def test_touch_screen_customization(c):
    properties = {
        'title': 'testing',
        'hsize': '500%',
        'hcolor': 'testing',
        'hbg': 'testing',
        'mbg': 'testing',
        'tsize': '200%',
        'tcolor': 'btn-info',
        'msize': '300%',
        'mcolor': 'testing',
        'mduration': '1000',
        'hfont': 'testing',
        'tfont': 'testing',
        'mfont': 'testing',
        'message': 'testing',
    }

    data = {'touch': 2,
            'background': 0,
            'naudio': 0,
            **properties}

    response = c.post('/touchscreen_c/1', data=data, follow_redirects=True)

    assert response.status == '200 OK'
    for key, value in properties.items():
        assert getattr(Touch_store.get(), key, None) == value


@pytest.mark.usefixtures('c')
def test_aliases(c):
    data = {
        'office': 't_office',
        'task': 't_task',
        'ticket': 't_ticket',
        'name': 't_name',
        'number': 't_number',
    }

    response = c.post('/alias', data=data, follow_redirects=True)

    assert response.status == '200 OK'
    for key, value in data.items():
        assert getattr(Aliases.get(), key, None) == value


@pytest.mark.skipif(
    bool(os.getenv('DOCKER')),
    reason='Not supported in docker setup',
)
@pytest.mark.usefixtures('c', 'get_bg_task')
def test_background_tasks_cache_tts(c, get_bg_task, monkeypatch):
    mock_gTTs = MagicMock()
    monkeypatch.setattr(app.tasks.cache_tickets_tts, 'gTTs', mock_gTTs)
    task_enabled = True
    task_every = 'second'

    response = c.post('/background_tasks', data={
        'cache_tts_enabled': task_enabled,
        'cache_tts_every': task_every,
        'delete_tickets_enabled': False,
        'delete_tickets_every': 'day',
        'delete_tickets_time': '12:12'
    }, follow_redirects=True)
    task = get_bg_task('CacheTicketsAnnouncements')

    assert response.status == '200 OK'
    assert task.settings.enabled == task_enabled
    assert task.settings.every == task_every
    assert task.settings.time is None
    assert mock_gTTs.say.called is True


@pytest.mark.skipif(
    bool(os.getenv('DOCKER')),
    reason='Not supported in docker setup',
)
@pytest.mark.usefixtures('c', 'get_bg_task')
def test_background_tasks_delete_tickets(c, get_bg_task):
    task_enabled = True
    task_every = 'second'
    task_time = None

    response = c.post('/background_tasks', data={
        'cache_tts_enabled': False,
        'cache_tts_every': 'second',
        'delete_tickets_enabled': task_enabled,
        'delete_tickets_every': task_every,
        'delete_tickets_time': task_time
    }, follow_redirects=True)
    task = get_bg_task('DeleteTickets')

    assert response.status == '200 OK'
    assert task.settings.enabled == task_enabled
    assert task.settings.every == task_every
    assert task.settings.time is None
    assert Serial.all_clean().count() == 0
