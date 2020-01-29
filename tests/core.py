import pytest
from random import choice

from .common import client, NAMES, TEST_REPEATS
from app.database import Task, Office, Serial
from app.middleware import db
from app.utils import ids


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


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_generate_new_tickets(_, client):
    with client.application.app_context():
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


@pytest.mark.parametrize('_', range(TEST_REPEATS))
def test_pull_tickets_from_commmon_task(_, client):
    with client.application.app_context():
        task = Task.get_first_common()
        ticket_to_be_pulled = Serial.query.order_by(Serial.number)\
                                          .filter(Serial.number != 100, Serial.p != True,
                                                  Serial.task_id == task.id)\
                                          .first()

    response = client.get(f'/pull/{task.id}/{choice(task.offices).id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert ticket_to_be_pulled is not None
    assert ticket_to_be_pulled.p is False
    assert Serial.query.filter_by(number=ticket_to_be_pulled.number,
                                  office_id=ticket_to_be_pulled.office_id,
                                  task_id=ticket_to_be_pulled.task_id,
                                  p=True)\
                       .order_by(Serial.number)\
                       .first() is not None
