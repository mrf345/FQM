from random import choice, randint
from sqlalchemy.sql.expression import func
from uuid import uuid4

from .common import client, TEST_PREFIX
from app.database import Task, Office, Serial
from app.middleware import db
from app.utils import ids


def test_management_welcome(client):
    response = client.get('/manage', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert 'Management' in page_content


def test_list_offices(client):
    with client.application.app_context():
        tickets = Serial.query.filter(Serial.number != 100)\
                              .order_by(Serial.p, Serial.timestamp.desc())\
                              .limit(10)

    response = client.get('/all_offices', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for ticket in tickets:
        assert f'<b> {ticket.office.prefix}{ ticket.number }.</b>' in page_content


def test_list_office(client):
    with client.application.app_context():
        office = choice(Office.query.all())
        tickets = Serial.all_office_tickets(office.id)\
                        .filter(Serial.number != 100)\
                        .order_by(Serial.p, Serial.timestamp.desc())\
                        .limit(10)

    response = client.get(f'/offices/{office.id}', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for ticket in tickets:
        assert f'<b> {ticket.office.prefix}{ ticket.number }.</b>' in page_content


def test_update_office(client):
    with client.application.app_context():
        office = choice(Office.query.all())
        office_name = office.name

    updated_office_name = 9999
    response = client.post(f'/offices/{office.id}', data={
        'name': 9999
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert office_name != updated_office_name
    assert Office.get(office.id).name == office_name


def test_add_office(client):
    with client.application.app_context():
        offices_length_before = Office.query.count()

    name = 9999
    response = client.post('/office_a', data={
        'name': name, 'prefix': TEST_PREFIX
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Office.query.count() == (offices_length_before + 1)
    assert Office.query.filter_by(name=name, prefix=TEST_PREFIX)\
                       .first() is not None


def test_add_task(client):
    with client.application.app_context():
        office = Office.query.first()

    name = f'{uuid4()}'.replace('-', '')
    response = client.post(f'/task_a/{office.id}',
                           data={'name': name},
                           follow_redirects=True)
    added_task = Task.query.filter_by(name=name).first()

    assert added_task is not None
    assert office.id in ids(added_task.offices)


def test_add_common_task(client):
    with client.application.app_context():
        offices = Office.query.limit(5).all()

    name = f'{uuid4()}'.replace('-', '')
    response = client.post(f'/common_task_a', data={
        'name': name, **{
            f'check{o.id}': True for o in offices
        }
    }, follow_redirects=True)
    added_task = Task.query.filter_by(name=name).first()

    assert added_task is not None
    assert sorted(ids(added_task.offices)) == sorted(ids(offices))


def test_update_task(client):
    with client.application.app_context():
        task = Task.query.filter(func.length(Task.offices) == 1).first()

    old_name = task.name
    new_name = f'{uuid4()}'.replace('-', '')
    response = client.post(f'/task/{task.id}', data={
        'name': new_name
    }, follow_redirects=True)

    assert Task.query.filter_by(name=old_name).first() is None
    assert Task.query.filter_by(name=new_name).first() is not None


def test_update_common_task_offices(client):
    with client.application.app_context():
        task = Task.get_first_common()
        unchecked_office = task.offices[0]
        checked_office = task.offices[1]
        unchecked_office_tickets_numbers = [
            ticket.number for ticket in Serial.query.filter_by(
                task_id=task.id, office_id=unchecked_office.id
            )
        ]

    old_name = task.name
    new_name = f'{uuid4()}'.replace('-', '')
    response = client.post(f'/task/{task.id}', data={
        'name': new_name,
        f'check{checked_office.id}': True
    }, follow_redirects=True)
    updated_task = Task.query.filter_by(name=new_name).first()

    assert Task.query.filter_by(name=old_name).first() is None
    assert updated_task is not None
    assert len(task.offices) > len(updated_task.offices)
    assert checked_office.id in ids(updated_task.offices)
    assert unchecked_office.id not in ids(updated_task.offices)

    # Test unchecked office tickets were migrated
    for number in unchecked_office_tickets_numbers:
        ticket = Serial.query.filter_by(number=number).first()

        assert ticket is not None
        assert ticket.office_id != unchecked_office.id
