import pytest
from random import choice
from sqlalchemy.sql.expression import func
from uuid import uuid4

from .. import TEST_PREFIX, get_first_office_with_tickets
from app.database import Task, Office, Serial
from app.utils import ids
from app.constants import TICKET_UNATTENDED


@pytest.mark.usefixtures('c')
def test_management_welcome(c):
    response = c.get('/manage', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert 'Management' in page_content


@pytest.mark.usefixtures('c')
def test_list_offices(c):
    tickets = Serial.query.filter(Serial.number != 100)\
                          .order_by(Serial.p, Serial.timestamp.desc())\
                          .limit(10)

    response = c.get('/all_offices', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for ticket in tickets:
        assert f'<b> {ticket.office.prefix}{ ticket.number }.</b>' in page_content


@pytest.mark.usefixtures('c')
def test_list_office(c):
    office = choice(Office.query.all())
    tickets = Serial.all_office_tickets(office.id)\
                    .filter(Serial.number != 100)\
                    .order_by(Serial.p, Serial.timestamp.desc())\
                    .limit(10)

    response = c.get(f'/offices/{office.id}', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for ticket in tickets:
        assert f'<b> {office.prefix}{ticket.number}.</b>' in page_content


@pytest.mark.usefixtures('c')
def test_list_office_with_common_task(c):
    task = Task.get_first_common()
    office = choice(task.offices)
    tickets = Serial.all_office_tickets(office.id)\
                    .filter(Serial.number != 100)\
                    .order_by(Serial.p, Serial.timestamp.desc())\
                    .limit(10)

    response = c.get(f'/offices/{office.id}', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for ticket in tickets:
        assert f'<b> {office.prefix}{ticket.number}.</b>' in page_content


@pytest.mark.usefixtures('c')
def test_delete_office_before_reset(c):
    office = get_first_office_with_tickets(c)
    response = c.get(f'/office_d/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Office.get(office.id) is not None


@pytest.mark.usefixtures('c')
def test_delete_office_after_reset(c):
    office = choice(Office.query.all())
    migrated_common_tasks = [t for t in office.tasks if t.common]

    c.get(f'/serial_r/{office.id}')  # NOTE: reseting office before deleting it
    response = c.get(f'/office_d/{office.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert Office.query.filter_by(name=office.name).first() is None

    for task in migrated_common_tasks:
        assert Task.get(task.id) is not None


@pytest.mark.usefixtures('c')
def test_delete_all_offices(c):
    offices_length = Office.query.count()
    tasks_length = Task.query.count()
    tickets_length = Serial.query.count()

    c.get(f'/serial_ra', follow_redirects=True)  # NOTE: reseting office before deleting it
    response = c.get(f'/office_da', follow_redirects=True)

    assert response.status == '200 OK'
    assert offices_length != 0
    assert Office.query.count() == 0
    assert tasks_length != 0
    assert Task.query.count() == 0
    assert tickets_length != 0
    assert Serial.query.count() == 0


@pytest.mark.usefixtures('c')
def test_search(c):
    office = get_first_office_with_tickets(c)
    ticket = Serial.query.filter(Serial.office_id == office.id,
                                 Serial.number != 100)\
                         .first()

    response = c.post('/search', data={
        'number': ticket.number, 'tl': office.id
    }, follow_redirects=True)
    page_content = response.data.decode('utf-8')

    assert response.status == '200 OK'
    assert ticket is not None
    assert f'<b> {Office.get(ticket.office_id).prefix}{ticket.number}.</b>' in page_content


@pytest.mark.usefixtures('c')
def test_update_office(c):
    office = choice(Office.query.all())
    office_name = office.name
    updated_office_name = 'updated999'

    response = c.post(f'/offices/{office.id}', data={
        'name': updated_office_name,
        'prefix': office.prefix
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert office_name != updated_office_name
    assert Office.get(office.id).name == updated_office_name


@pytest.mark.usefixtures('c')
def test_add_office(c):
    offices_length_before = Office.query.count()
    name = 9999

    response = c.post('/office_a', data={
        'name': name, 'prefix': TEST_PREFIX
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert Office.query.count() == (offices_length_before + 1)
    assert Office.query.filter_by(name=name, prefix=TEST_PREFIX)\
                       .first() is not None


@pytest.mark.usefixtures('c')
def test_add_task(c):
    office = Office.query.first()
    name = f'{uuid4()}'.replace('-', '')

    c.post(f'/task_a/{office.id}',
           data={'name': name},
           follow_redirects=True)

    added_task = Task.query.filter_by(name=name).first()

    assert added_task is not None
    assert office.id in ids(added_task.offices)


def test_add_common_task(c):
    offices = Office.query.limit(5).all()
    name = f'{uuid4()}'.replace('-', '')

    c.post(f'/common_task_a', data={
        'name': name, **{
            f'check{o.id}': True for o in offices
        }
    }, follow_redirects=True)

    added_task = Task.query.filter_by(name=name).first()

    assert added_task is not None
    assert sorted(ids(added_task.offices)) == sorted(ids(offices))


@pytest.mark.usefixtures('c')
def test_update_task(c):
    task = Task.query.filter(func.length(Task.offices) == 1).first()
    old_name = task.name
    new_name = f'{uuid4()}'.replace('-', '')

    c.post(f'/task/{task.id}', data={
        'name': new_name
    }, follow_redirects=True)

    assert Task.query.filter_by(name=old_name).first() is None
    assert Task.query.filter_by(name=new_name).first() is not None


@pytest.mark.usefixtures('c')
def test_update_common_task_offices(c):
    task = Task.get_first_common()
    unchecked_office = task.offices[0]
    checked_office = task.offices[1]
    unchecked_office_tickets_numbers = [
        ticket.number for ticket in Serial.all_clean().filter_by(
            task_id=task.id, office_id=unchecked_office.id
        )]
    old_name = task.name
    new_name = f'{uuid4()}'.replace('-', '')

    c.post(f'/task/{task.id}', data={
        'name': new_name,
        f'check{checked_office.id}': True
    }, follow_redirects=True)

    updated_task = Task.query.filter_by(name=new_name).first()

    assert Task.query.filter_by(name=old_name).first() is None
    assert updated_task is not None
    assert len(task.offices) >= len(updated_task.offices)
    assert checked_office.id in ids(updated_task.offices)
    assert unchecked_office.id not in ids(updated_task.offices)

    # Test unchecked office tickets were migrated
    for number in unchecked_office_tickets_numbers:
        ticket = Serial.query.filter_by(number=number).first()

        assert ticket is not None
        assert ticket.office_id != unchecked_office.id


@pytest.mark.usefixtures('c')
def test_update_ticket(c):
    ticket = Serial.get()

    if not ticket.p:
        ticket.pull(ticket.office.id)

    assert ticket.status != TICKET_UNATTENDED

    c.post(f'/serial_u/{ticket.id}/testing', data={
        'value': ticket.name,
        'printed': not ticket.n,
        'status': TICKET_UNATTENDED
    })

    assert Serial.get(ticket.id).status == TICKET_UNATTENDED
