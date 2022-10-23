import pytest
import os
import escpos.printer
from random import choice
from unittest.mock import MagicMock, ANY

import app.views.core
import app.printer
import app.database
import app.utils
from .. import NAMES, TEST_REPEATS, fill_tickets, do_until_truthy
from app.middleware import db
from app.utils import absolute_path
from app.database import (Task, Office, Serial, Settings, Touch_store, Display_store,
                          Printer, Aliases)


@pytest.mark.usefixtures('c')
def test_welcome_root_and_login(c):
    response = c.post('/log/a', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert 'Free Queue Manager' in page_content


@pytest.mark.usefixtures('c')
def test_new_registered_ticket(c):
    touch_screen_settings = Touch_store.query.first()
    touch_screen_settings.n = True
    db.session.commit()

    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING REGISTERED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name


@pytest.mark.usefixtures('c')
def test_new_noisy_registered_ticket(c):
    touch_screen_settings = Touch_store.query.first()
    touch_screen_settings.n = True
    db.session.commit()

    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = '0002020000'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name[3:]


@pytest.mark.usefixtures('c')
def test_new_printed_ticket(c, monkeypatch):
    last_ticket = None
    mock_printer = MagicMock()
    monkeypatch.setattr(escpos.printer, 'Usb', mock_printer)

    # NOTE: set ticket setting to printed
    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    printer_settings.vendor = 150
    printer_settings.product = 3
    printer_settings.in_ep = 170
    printer_settings.out_ep = 170
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    assert mock_printer().image.call_count == 1
    assert mock_printer().cut.call_count == 1
    assert mock_printer().close.call_count == 1


@pytest.mark.skip('FIXME: refactor to use PrintedTicket image generator')
@pytest.mark.usefixtures('c')
def test_new_printed_ticket_with_aliases(c, monkeypatch):
    last_ticket = None
    mock_printer = MagicMock()
    monkeypatch.setattr(escpos.printer, 'Usb', mock_printer)

    # NOTE: set ticket setting to printed
    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    printer_settings.vendor = 150
    printer_settings.product = 3
    printer_settings.in_ep = 170
    printer_settings.out_ep = 170
    # NOTE: setting aliases
    office_alt = 'Department'
    task_alt = 'Mission'
    ticket_alt = 'Token'
    aliases = Aliases.get()
    aliases.office = office_alt
    aliases.task = task_alt
    aliases.ticket = ticket_alt
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()
    office = new_ticket.office
    tickets = Serial.all_office_tickets(office.id, desc=False)\
                    .filter(Serial.number != new_ticket.number)
    cur_ticket = tickets.first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    assert mock_printer().text.call_count == 12
    assert mock_printer().set.call_count == 7
    mock_printer().set.assert_called_with(align='left', height=1, width=1)
    mock_printer().cut.assert_called_once()
    mock_printer().text.assert_any_call(f'\n{office_alt} : {office.prefix}{office.name}\n')
    mock_printer().text.assert_any_call(f'\n{office.prefix}.{new_ticket.number}\n')
    mock_printer().text.assert_any_call(f'\n{ticket_alt}s ahead : {tickets.count()}\n')
    mock_printer().text.assert_any_call(f'\n{task_alt} : {new_ticket.task.name}\n')
    mock_printer().text.assert_any_call(
        f'\nCurrent {ticket_alt.lower()} : {office.prefix}.{cur_ticket and cur_ticket.number}\n')


@pytest.mark.usefixtures('c')
def test_new_printed_ticket_windows(c, monkeypatch):
    last_ticket = None
    printer_name = 'testing_printer'
    printer_path = 'testing_path'
    printer_full_path = os.path.join(os.getcwd(), f'{printer_path}.txt')
    mock_uuid = MagicMock()
    mock_uuid.uuid4 = MagicMock(return_value=printer_path)
    mock_os = MagicMock()
    mock_os.name = 'nt'
    mock_os.path.join.return_value = printer_full_path
    mock_system = MagicMock()
    mock_printer = MagicMock()
    mock_printer().output = b'testing_text'
    monkeypatch.setattr(app.printer, 'os', mock_os)
    monkeypatch.setattr(app.printer, 'name', 'nt')
    monkeypatch.setattr(app.printer, 'uuid', mock_uuid)
    monkeypatch.setattr(app.printer, 'system', mock_system)
    monkeypatch.setattr(escpos.printer, 'Dummy', mock_printer)

    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    printer_settings.name = printer_name
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    mock_system.assert_called_once_with(
        f'print /D:\\\localhost\\"{printer_name}" "{printer_full_path}"') # noqa


@pytest.mark.usefixtures('c')
def test_new_printed_ticket_lp(c, monkeypatch):
    last_ticket = None
    printer_name = 'testing_printer'
    printer_path = 'testing_path'
    printer_full_path = os.path.join(os.getcwd(), f'{printer_path}.txt')
    mock_uuid = MagicMock()
    mock_uuid.uuid4 = MagicMock(return_value=printer_path)
    mock_os = MagicMock()
    mock_os.name = 'linux'
    mock_system = MagicMock()
    monkeypatch.setattr(app.views.core, 'os', mock_os)
    monkeypatch.setattr(app.printer, 'name', 'linux')
    monkeypatch.setattr(app.printer, 'uuid', mock_uuid)
    monkeypatch.setattr(app.printer, 'system', mock_system)

    settings = Settings.get()
    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    settings.lp_printing = True
    touch_screen_settings.n = False
    printer_settings.name = printer_name
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    mock_system.assert_called_once_with(
        f'lp -d "{printer_name}" -o raw "{printer_full_path}"')


@pytest.mark.usefixtures('c')
def test_new_printed_ticket_arabic(c, monkeypatch):
    last_ticket = None
    mock_printer = MagicMock()
    mock_pil = MagicMock()
    mock_pil.truetype().getsize.return_value = (0, 0)
    mock_pos = MagicMock()
    mock_pos().output = b''
    monkeypatch.setattr(escpos.printer, 'Usb', mock_printer)
    monkeypatch.setattr(app.printer, 'ImageDraw', mock_pil)
    monkeypatch.setattr(app.printer, 'Image', mock_pil)
    monkeypatch.setattr(app.printer, 'ImageFont', mock_pil)
    monkeypatch.setattr(escpos.printer, 'Dummy', mock_pos)


    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    printer_settings.vendor = 150
    printer_settings.product = 3
    printer_settings.in_ep = 170
    printer_settings.out_ep = 170
    printer_settings.langu = 'ar'
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    assert mock_printer().text.call_count == 1
    mock_printer().cut.assert_called_once()
    mock_printer().close.assert_called_once()
    mock_printer().image.assert_called_once_with(ANY,
                                                 fragment_height=520,
                                                 high_density_vertical=True)


@pytest.mark.usefixtures('c')
def test_new_printed_ticket_windows_arabic(c, monkeypatch):
    last_ticket = None
    printer_name = 'testing_printer'
    printer_path = 'testing_path'
    printer_full_path = os.path.join(os.getcwd(), f'{printer_path}.txt')
    mock_uuid = MagicMock()
    mock_uuid.uuid4 = MagicMock(return_value=printer_path)
    mock_os = MagicMock()
    mock_os.name = 'nt'
    mock_system = MagicMock()
    mock_pil = MagicMock()
    mock_pil.truetype().getsize.return_value = (0, 0)
    mock_pos = MagicMock()
    mock_pos().output = b''
    monkeypatch.setattr(app.printer, 'os', mock_os)
    monkeypatch.setattr(app.printer, 'name', 'nt')
    monkeypatch.setattr(app.printer, 'uuid', mock_uuid)
    monkeypatch.setattr(app.printer, 'system', mock_system)
    monkeypatch.setattr(app.printer, 'ImageDraw', mock_pil)
    monkeypatch.setattr(app.printer, 'Image', mock_pil)
    monkeypatch.setattr(app.printer, 'ImageFont', mock_pil)
    monkeypatch.setattr(escpos.printer, 'Dummy', mock_pos)


    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    touch_screen_settings.n = False
    printer_settings.name = printer_name
    printer_settings.langu = 'ar'
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    assert mock_system.call_count == 1
    assert (
        f'print /D:\\\localhost\\"{printer_name}"' in
        mock_system.call_args_list[0].args[0]
    )

@pytest.mark.usefixtures('c')
def test_new_printed_ticket_lp_arabic(c, monkeypatch):
    last_ticket = None
    printer_name = 'testing_printer'
    printer_path = 'testing_path'
    printer_full_path = os.path.join(os.getcwd(), f'{printer_path}.txt')
    mock_uuid = MagicMock()
    mock_uuid.uuid4 = MagicMock(return_value=printer_path)
    mock_os = MagicMock()
    mock_os.name = 'linux'
    mock_system = MagicMock()
    mock_pil = MagicMock()
    mock_pil.truetype().getsize.return_value = (0, 0)
    mock_pos = MagicMock()
    mock_pos().output = b''
    monkeypatch.setattr(app.views.core, 'os', mock_os)
    monkeypatch.setattr(app.printer, 'name', 'linux')
    monkeypatch.setattr(app.printer, 'uuid', mock_uuid)
    monkeypatch.setattr(app.printer, 'system', mock_system)
    monkeypatch.setattr(app.printer, 'ImageDraw', mock_pil)
    monkeypatch.setattr(app.printer, 'Image', mock_pil)
    monkeypatch.setattr(app.printer, 'ImageFont', mock_pil)
    monkeypatch.setattr(escpos.printer, 'Dummy', mock_pos)
    

    settings = Settings.get()
    printer_settings = Printer.get()
    touch_screen_settings = Touch_store.get()
    settings.lp_printing = True
    touch_screen_settings.n = False
    printer_settings.name = printer_name
    printer_settings.langu = 'ar'
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    name = 'TESTING PRINTED TICKET'
    response = c.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name
    mock_system.assert_called_once_with(
        f'lp -d "{printer_name}" -o raw "{printer_full_path}"')


@pytest.mark.usefixtures('c')
def test_new_printed_ticket_fail(c):
    touch_screen_settings = Touch_store.query.first()
    touch_screen_settings.n = False
    db.session.commit()
    task = choice(Task.query.all())
    last_ticket = Serial.query.filter_by(task_id=task.id)\
                              .order_by(Serial.number.desc()).first()

    response = c.post(f'/serial/{task.id}', follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    with open(absolute_path('errors.log'), 'r') as errors_log:
        errors_log_content = errors_log.read()

    assert response.status == '200 OK'
    assert new_ticket.id == last_ticket.id
    assert bool(errors_log_content)


@pytest.mark.usefixtures('c')
def test_reset_office(c):
    ticket = Serial.query.order_by(Serial.number.desc()).first()
    office = Office.get(ticket.office_id)
    tickets = Serial.query.filter_by(office_id=office.id).all()

    response = c.get(f'/serial_r/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.filter_by(office_id=office.id).count() != len(tickets)
    assert Serial.query.filter(Serial.office_id == office.id, Serial.number != 100)\
                       .count() == 0


@pytest.mark.usefixtures('c')
def test_reset_task(c):
    task = Task.query.first()
    office = choice(task.offices)

    def getter():
        tickets = Serial.query.filter_by(office_id=office.id,
                                         task_id=task.id)\
                              .all()

        return len(tickets) > 1 and tickets

    tickets = do_until_truthy(fill_tickets, getter)

    response = c.get(f'/serial_rt/{task.id}/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.filter_by(task_id=task.id).count() != len(tickets)
    assert Serial.query.filter(Serial.task_id == task.id, Serial.number != 100)\
                       .count() == 0


@pytest.mark.usefixtures('c')
def test_reset_all(c):
    all_tickets = Serial.query.all()

    response = c.get('/serial_ra', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.count() != len(all_tickets)
    assert Serial.query.count() == Task.query.count()


@pytest.mark.usefixtures('c')
@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_generate_new_tickets(_, c):
    touch_screen_settings = Touch_store.query.first()
    touch_screen_settings.n = True
    db.session.commit()
    tickets_before = Serial.query.order_by(Serial.number.desc()).all()
    last_ticket = Serial.query.order_by(Serial.number.desc()).first()
    random_task = choice(Task.query.all())

    name = choice(NAMES)
    response = c.post(f'/serial/{random_task.id}', data={
        'name': name
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.count() > len(tickets_before)
    assert Serial.query.order_by(Serial.number.desc())\
                       .first()\
                       .number == (last_ticket.number + 1)


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_pull_tickets_from_all(_, c):
    ticket_to_be_pulled = do_until_truthy(
        fill_tickets,
        lambda: Serial.query.order_by(Serial.number)
                            .filter(Serial.number != 100, Serial.p != True)
                            .first())

    response = c.get(f'/pull', follow_redirects=True)

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert Serial.get(ticket_to_be_pulled.id).number == ticket_to_be_pulled.number
    assert Serial.get(ticket_to_be_pulled.id).p is True


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_pull_random_ticket(_, c):
    ticket = choice(Serial.query.filter_by(n=False)
                                .limit(10)
                                .all())
    office = choice(ticket.task.offices)

    c.get(f'/pull_unordered/{ticket.id}/testing/{office.id}')

    assert Serial.query.filter_by(id=ticket.id).first().p is True


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_pull_tickets_from_common_task(_, c):
    settings = Settings.get()
    settings.strict_pulling = False
    db.session.commit()
    task = Task.get_first_common()
    office = choice(task.offices)
    ticket_to_be_pulled = do_until_truthy(
        fill_tickets,
        lambda: Serial.query.order_by(Serial.number)
                            .filter(Serial.number != 100,
                                    Serial.p != True,
                                    Serial.task_id == task.id)
                            .first())

    response = c.get(f'/pull/{task.id}/{office.id}', follow_redirects=True)
    pulled_ticket = Serial.get(ticket_to_be_pulled.id)

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert pulled_ticket is not None
    assert pulled_ticket.task_id == task.id
    assert pulled_ticket.office_id == office.id


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_pull_common_task_strict_pulling(_, c):
    def getter():
        tickets = Serial.query.order_by(Serial.number)\
                              .filter(Serial.number != 100, Serial.p != True)\
                              .all()

        for ticket in tickets:
            task = Task.get(ticket.task_id)
            office = Office.get(ticket.office_id)

            if task.common:
                return ticket, office, task

    ticket_to_be_pulled, office, task = do_until_truthy(fill_tickets, getter)

    response = c.get(f'/pull/{task.id}/{office.id}', follow_redirects=True)
    pulled_ticket = Serial.query.filter_by(number=ticket_to_be_pulled.number,
                                           office_id=office.id,
                                           task_id=task.id,
                                           p=True)\
                                .order_by(Serial.number)\
                                .first()

    assert response.status == '200 OK'
    assert pulled_ticket is not None
    assert pulled_ticket.task_id == task.id
    assert pulled_ticket.office_id == office.id


@pytest.mark.usefixtures('c')
def test_pull_ticket_on_hold(c):
    ticket_to_be_pulled = None

    ticket_to_be_pulled = Serial.query.order_by(Serial.number)\
                                      .filter(Serial.number != 100, Serial.p != True)\
                                      .first()

    c.get(f'/on_hold/{ticket_to_be_pulled.id}/testing')
    response = c.get(f'/pull', follow_redirects=True)

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert Serial.query.filter_by(number=ticket_to_be_pulled.number,
                                  office_id=ticket_to_be_pulled.office_id,
                                  task_id=ticket_to_be_pulled.task_id,
                                  p=True)\
                       .order_by(Serial.number)\
                       .first() is None


@pytest.mark.usefixtures('c')
def test_feed_stream_tickets_preferences_enabled(c):
    c.get('/pull', follow_redirects=True)  # NOTE: initial pull to fill stacks

    display_settings = Display_store.query.first()
    display_settings.prefix = True
    display_settings.always_show_ticket_number = True
    display_settings.tmp = 3
    db.session.commit()
    tickets = Serial.get_waiting_list_tickets(limit=8)
    processed_tickets = Serial.get_processed_tickets(limit=8, offset=1)
    current_ticket = Serial.get_last_pulled_ticket()

    response = c.get('/feed', follow_redirects=True)

    assert response.status == '200 OK'
    assert response.json.get('con') == current_ticket.office.display_text
    assert response.json.get('cott') == current_ticket.task.name
    assert response.json.get('cot') == current_ticket.display_text

    for i, ticket in enumerate(tickets):
        assert ticket.name in response.json.get(f'w{i + 1}')
        assert f'{ticket.office.prefix}{ticket.number}' in response.json.get(f'w{i + 1}')

    for i, ticket in enumerate(processed_tickets):
        assert ticket.name in response.json.get(f'p{i + 1}')
        assert f'{ticket.office.prefix}{ticket.number}' in response.json.get(f'p{i + 1}')


@pytest.mark.usefixtures('c')
def test_feed_office_with_preferences_enabled(c):
    c.get('/pull', follow_redirects=True)  # NOTE: initial pull to fill stacks

    display_settings = Display_store.query.first()
    display_settings.prefix = True
    display_settings.always_show_ticket_number = True
    db.session.commit()
    current_ticket = Serial.get_last_pulled_ticket()
    tickets = Serial.get_waiting_list_tickets(office_id=current_ticket.office.id,
                                              limit=8)

    response = c.get(f'/feed/{current_ticket.office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert response.json.get('con') == current_ticket.office.display_text
    assert response.json.get('cott') == current_ticket.task.name
    assert response.json.get('cot') == current_ticket.display_text

    for i, ticket in enumerate(tickets):
        assert ticket.name in response.json.get(f'w{i + 1}')
        assert f'{ticket.office.prefix}{ticket.number}' in response.json.get(f'w{i + 1}')


@pytest.mark.usefixtures('c')
def test_feed_stream_tickets_preferences_disabled(c):
    c.get('/pull', follow_redirects=True)  # NOTE: initial pull to fill stacks

    display_settings = Display_store.query.first()
    display_settings.prefix = False
    display_settings.always_show_ticket_number = False
    db.session.commit()
    tickets = Serial.get_waiting_list_tickets(limit=8)
    current_ticket = Serial.get_last_pulled_ticket()

    response = c.get('/feed', follow_redirects=True)

    assert response.status == '200 OK'
    assert response.json.get('con') == current_ticket.office.display_text
    assert response.json.get('cott') == current_ticket.task.name
    assert response.json.get('cot') == current_ticket.display_text

    for i, ticket in enumerate(tickets):
        assert ticket.name in response.json.get(f'w{i + 1}')
        assert f'{ticket.office.prefix}{ticket.number}' not in response.json.get(f'w{i + 1}')


@pytest.mark.usefixtures('c')
def test_display_screen(c):
    display_settings = Display_store.query.first()

    response = c.get('/display', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert display_settings.title in page_content


@pytest.mark.usefixtures('c')
def test_touch_screen(c):
    touch_screen_settings = Touch_store.query.first()
    tasks = Task.query.all()

    response = c.get('/touch/0', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert touch_screen_settings.title in page_content
    for task in tasks:
        assert task.name in page_content


@pytest.mark.usefixtures('c')
def test_touch_screen_office(c):
    office = choice(Office.query.all())
    touch_screen_settings = Touch_store.query.first()
    tasks = Task.query.filter(Task.offices.contains(office))

    response = c.get(f'/touch/0/{office.id}', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert touch_screen_settings.title in page_content
    for task in tasks:
        assert task.name in page_content


@pytest.mark.usefixtures('c')
def test_toggle_setting(c):
    setting = 'visual_effects'
    setting_value = getattr(Settings.get(), setting)

    c.get(f'/settings/{setting}/testing')
    assert getattr(Settings.get(), setting) == (not setting_value)


@pytest.mark.usefixtures('c')
def test_repeat_announcement(c):
    c.get('/set_repeat_announcement/0')
    assert c.get('/repeat_announcement').json.get('status') is False

    c.get('/set_repeat_announcement/1')
    assert c.get('/repeat_announcement').json.get('status') is True
