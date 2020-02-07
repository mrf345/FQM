import pytest
from random import choice

from .common import client, NAMES, TEST_REPEATS
from app.middleware import db
from app.utils import ids, absolute_path
from app.database import (Task, Office, Serial, Waiting, Settings, Touch_store,
                          Waiting_c, Display_store, Touch_store)

def test_welcome_root_and_login(client):
    response = client.post('/log/a', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert 'Free Queue Manager' in page_content


def test_new_registered_ticket(client):
    with client.application.app_context():
        # NOTE: set ticket setting to registered
        touch_screen_settings = Touch_store.query.first()
        touch_screen_settings.n = True
        db.session.commit()

        task = choice(Task.query.all())
        last_ticket = Serial.query.filter_by(task_id=task.id)\
                                  .order_by(Serial.number.desc()).first()

    name = 'TESTING REGISTERED TICKET'
    response = client.post(f'/serial/{task.id}', data={
        'name': name
    }, follow_redirects=True)
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    assert response.status == '200 OK'
    assert last_ticket.number != new_ticket.number
    assert new_ticket.name == name


def test_new_printed_ticket_fail(client):
    with client.application.app_context():
        # NOTE: set ticket setting to printed
        touch_screen_settings = Touch_store.query.first()
        touch_screen_settings.n = False
        db.session.commit()

        task = choice(Task.query.all())
        last_ticket = Serial.query.filter_by(task_id=task.id)\
                                  .order_by(Serial.number.desc()).first()


    response = client.post(f'/serial/{task.id}', follow_redirects=True)
    page_content = response.data.decode('utf-8')
    new_ticket = Serial.query.filter_by(task_id=task.id)\
                             .order_by(Serial.number.desc()).first()

    with open(absolute_path('errors.log'), 'r') as errors_log:
        errors_log_content = errors_log.read()

    assert response.status == '200 OK'
    assert new_ticket.id == last_ticket.id
    assert "ValueError: invalid literal for int() with base 10: ' '" in errors_log_content


def test_reset_office(client):
    with client.application.app_context():
        ticket = Serial.query.order_by(Serial.number.desc()).first()
        office = Office.get(ticket.office_id)
        tickets = Serial.query.filter_by(office_id=office.id).all()

    response = client.get(f'/serial_r/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.filter_by(office_id=office.id).count() != len(tickets)
    assert Serial.query.filter(Serial.office_id == office.id, Serial.number != 100)\
                       .count() == 0


def test_reset_task(client):
    with client.application.app_context():
        task = Task.query.first()
        office = choice(task.offices)
        tickets = Serial.query.filter_by(office_id=office.id, task_id=task.id)\
                              .all()

    response = client.get(f'/serial_rt/{task.id}/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.filter_by(task_id=task.id).count() != len(tickets)
    assert Serial.query.filter(Serial.task_id == task.id, Serial.number != 100)\
                       .count() == 0


def test_reset_all(client):
    with client.application.app_context():
        all_tickets = Serial.query.all()

    response = client.get('/serial_ra', follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.count() != len(all_tickets)
    assert Serial.query.count() == Task.query.count()
    assert Waiting.query.count() == 0


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_generate_new_tickets(_, client):
    with client.application.app_context():
        # NOTE: set ticket setting to registered
        touch_screen_settings = Touch_store.query.first()
        touch_screen_settings.n = True
        db.session.commit()

        tickets_before = Serial.query.order_by(Serial.number.desc()).all()
        last_ticket = Serial.query.order_by(Serial.number.desc()).first()
        random_task = choice(Task.query.all())

    name = choice(NAMES)
    response = client.post(f'/serial/{random_task.id}', data={
        'name': name
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Serial.query.count() > len(tickets_before)
    assert Serial.query.order_by(Serial.number.desc())\
                       .first()\
                       .number == (last_ticket.number + 1)


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_pull_tickets_from_all(_, client):
    with client.application.app_context():
        ticket_to_be_pulled = Serial.query.order_by(Serial.number)\
                                          .filter(Serial.number != 100, Serial.p != True)\
                                          .first()
        in_waiting = Waiting.query.filter_by(number=ticket_to_be_pulled.number)\
                                  .first()

    response = client.get(f'/pull', follow_redirects=True)

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert Serial.query.filter_by(number=ticket_to_be_pulled.number,
                                  office_id=ticket_to_be_pulled.office_id,
                                  task_id=ticket_to_be_pulled.task_id,
                                  p=True)\
                       .order_by(Serial.number)\
                       .first() is not None
    assert Waiting.query.count() == (10 if in_waiting else 11)  # NOTE: last ticket pulled deducted


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_pull_tickets_from_common_task(_, client):
    with client.application.app_context():
        task = Task.get_first_common()
        office = choice(task.offices)
        ticket_to_be_pulled = Serial.query.order_by(Serial.number)\
                                          .filter(Serial.number != 100, Serial.p != True,
                                                  Serial.task_id == task.id)\
                                          .first()
        in_waiting = Waiting.query.filter_by(number=ticket_to_be_pulled.number)\
                                  .first()

    response = client.get(f'/pull/{task.id}/{office.id}', follow_redirects=True)
    pulled_ticket = Serial.query.filter_by(number=ticket_to_be_pulled.number,
                                           office_id=office.id,
                                           task_id=task.id,
                                           p=True)\
                                .order_by(Serial.number)\
                                .first()

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert pulled_ticket is not None
    assert pulled_ticket.task_id == task.id
    assert pulled_ticket.office_id == office.id
    assert Waiting.query.count() == (10 if in_waiting else 11)  # NOTE: last ticket pulled deducted


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_pull_common_task_strict_pulling(_, client):
    with client.application.app_context():
        # NOTE: Enabling strict pulling
        settings = Settings.get()
        settings.strict_pulling = True
        db.session.commit()

        # NOTE: Finding the proper next common ticket to be pulled
        ticket_to_be_pulled = None
        tickets = Serial.query.order_by(Serial.number)\
                              .filter(Serial.number != 100, Serial.p != True)\
                              .all()

        for ticket in tickets:
            task = Task.get(ticket.task_id)
            office = Office.get(ticket.office_id)

            if task.common:
                ticket_to_be_pulled = ticket
                break

    response = client.get(f'/pull/{task.id}/{office.id}', follow_redirects=True)
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
    assert Waiting.query.count() == 10


def test_feed_stream_tickets(client):
    client.get('/pull', follow_redirects=True) # NOTE: initial pull to fill stacks

    with client.application.app_context():
        tickets = Waiting.query.limit(8)\
                               .all()
        current_ticket = Waiting_c.query.first()

    response = client.get('/feed', follow_redirects=True)

    assert response.status == '200 OK'
    assert response.json.get('con') == current_ticket.oname
    assert response.json.get('cot') == current_ticket.tname
    assert response.json.get('cott') == getattr(current_ticket,
                                                'name' if current_ticket.n
                                                else 'ticket')

    for i, ticket in enumerate(tickets):
        assert (ticket.name
                if ticket.n else
                ticket.number) in response.json.get(f'w{i + 1}')


def test_display_screen(client):
    with client.application.app_context():
        display_settings = Display_store.query.first()

    response = client.get('/display', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert display_settings.title in page_content


def test_touch_screen(client):
    with client.application.app_context():
        touch_screen_settings = Touch_store.query.first()

    response = client.get('/touch/0', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert touch_screen_settings.title in page_content
