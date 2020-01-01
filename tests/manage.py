from sqlalchemy.sql.expression import func
from uuid import uuid4

from .common import client
from app.database import Task, Office
from app.middleware import db
from app.utils import ids


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
    # TODO: test tickets migration after you refactor `common.fill_tickets()`
    with client.application.app_context():
        common_task = None
        tasks = Task.query.all()

        while not common_task:
            task = tasks.pop()

            if len(task.offices) > 1:
                common_task = task

        unchecked_office = task.offices[0]
        checked_office = task.offices[1]

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
