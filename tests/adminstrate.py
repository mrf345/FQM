from uuid import uuid4

from app.database import User, Office, Operators
from app.utils import get_module_columns, get_module_values
from .common import client

def test_update_admin_password(client):
    new_password = 'password'
    response = client.post(
        '/admin_u',
        data=dict(password=new_password),
        follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(1).verify_password(new_password)


def test_list_users(client):
    response = client.get('/users', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    for user in User.query.limit(10):
        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


def test_list_operators(client):
    bundles = []

    with client.application.app_context():
        bundles += [
            (User.get(o.id), Office.get(o.office_id))
            for o in Operators.query.all()
        ]

    for user, office in bundles:
        response = client.get(f'/operators/{office.id}')
        page_content = response.data.decode('utf-8')

        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


def test_add_user(client):
    name = 'test_adding_a_user'
    password = 'testing'
    role = 1
    response = client.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


def test_add_operator(client):
    name = 'test_adding_operator'
    password = 'testing'
    role = 3
    response = client.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


def test_update_user(client):
    name = f'{uuid4()}'.replace('-', '')
    password = 'password'
    new_name = f'{uuid4()}'.replace('-', '')
    role = 1

    client.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    })

    user = User.query.filter_by(name=name).first() 
    response = client.post(f'/user_u/{user.id}', data={
        'name': new_name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(user.id).name == new_name


def test_delete_user(client):
    with client.application.app_context():
        user = User.query.filter(User.id != 1).first()

    response = client.get(f'/user_d/{user.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(user.id) is None


def test_delete_all_users_and_operators(client):
    with client.application.app_context():
        users_length_before = User.query.count()
        operators_length_before = Operators.query.count()

    response = client.get(f'/user_da', follow_redirects=True)

    with client.application.app_context():
        users_length_after = User.query.count()
        operators_length_after = Operators.query.count()

    assert response.status == '200 OK'
    assert users_length_before != users_length_after
    if operators_length_before != 0:  # NOTE: Once in a while flakiness
        assert operators_length_before != operators_length_after
    assert users_length_after == 1  # NOTE: God account won't be deleted
    assert operators_length_after == 0


def test_csv_export(client):
    with client.application.app_context():
        header = get_module_columns(User)
        rows = get_module_values(User)

    response = client.post('/csv', data={
        'table': 'User', 'headers': 1, 'delimiter': 0
    }, follow_redirects=True)
    content = response.data.decode('utf-8').split('\r\n')

    assert response.status == '200 OK'
    assert len(content) > (len(rows) + 1)
    assert ','.join(header) == content.pop(0)

    for row in map(','.join, rows):
        assert row == content.pop(0)


def test_csv_export_headers_disabled_and_tabs(client):
    with client.application.app_context():
        header = get_module_columns(User)
        rows = get_module_values(User)

    response = client.post('/csv', data={
        'table': 'User', 'headers': 0, 'delimiter': 1
    }, follow_redirects=True)
    content = response.data.decode('utf-8').split('\r\n')

    assert response.status == '200 OK'
    assert len(content) > len(rows)
    assert '\t'.join(header) not in content

    for row in map('\t'.join, rows):
        assert row == content.pop(0)
