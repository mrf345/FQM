import pytest
from uuid import uuid4
from random import choice

from app.database import User, Office, Operators, AuthTokens
from app.utils import get_module_columns, get_module_values


@pytest.mark.usefixtures('c')
def test_update_admin_password(c):
    new_password = 'password'
    response = c.post(
        '/admin_u',
        data=dict(password=new_password),
        follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(1).verify_password(new_password)


@pytest.mark.usefixtures('c')
def test_list_users(c):
    response = c.get('/users', follow_redirects=True)
    page_content = response.data.decode('utf-8')

    for user in User.query.limit(10):
        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


@pytest.mark.usefixtures('c')
def test_list_operators(c):
    bundles = []

    with c.application.app_context():
        bundles += [
            (User.get(o.id), Office.get(o.office_id))
            for o in Operators.query.all()
        ]

    for user, office in bundles:
        response = c.get(f'/operators/{office.id}')
        page_content = response.data.decode('utf-8')

        assert f'<strong>{user.id}. {user.name}</strong>' in page_content


@pytest.mark.usefixtures('c')
def test_add_user(c):
    name = 'test_adding_a_user'
    password = 'testing'
    role = 1
    response = c.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


@pytest.mark.usefixtures('c')
def test_add_operator(c):
    name = 'test_adding_operator'
    password = 'testing'
    role = 3
    response = c.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.query.filter_by(name=name).first() is not None


@pytest.mark.usefixtures('c')
def test_update_user(c):
    name = f'{uuid4()}'.replace('-', '')
    password = 'password'
    new_name = f'{uuid4()}'.replace('-', '')
    role = 1

    c.post('/user_a', data={
        'name': name, 'password': password, 'role': role
    })

    user = User.query.filter_by(name=name).first()
    response = c.post(f'/user_u/{user.id}', data={
        'name': new_name, 'password': password, 'role': role
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(user.id).name == new_name


@pytest.mark.usefixtures('c')
def test_update_operator(c):
    office = choice(Office.query.all())
    new_office = choice(Office.query.all())

    while new_office == office:
        new_office = choice(Office.query.all())

    name = f'{uuid4()}'.replace('-', '')
    password = 'password'
    role = 3
    new_name = f'{uuid4()}'.replace('-', '')

    c.post('/user_a', data={
        'name': name, 'password': password, 'role': role, 'offices': office.id
    })

    user = User.query.filter_by(name=name).first()
    response = c.post(f'/user_u/{user.id}', data={
        'name': new_name, 'password': password, 'role': role, 'offices': new_office.id
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(user.id).name == new_name
    assert Operators.get(user.id).office_id == new_office.id


@pytest.mark.usefixtures('c')
def test_delete_user(c):
    user = User.query.filter(User.id != 1).first()

    response = c.get(f'/user_d/{user.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert User.get(user.id) is None


@pytest.mark.usefixtures('c')
def test_delete_all_users_and_operators(c):
    users_length_before = User.query.count()
    operators_length_before = Operators.query.count()

    response = c.get(f'/user_da', follow_redirects=True)

    with c.application.app_context():
        users_length_after = User.query.count()
        operators_length_after = Operators.query.count()

    assert response.status == '200 OK'
    assert users_length_before != users_length_after
    if operators_length_before != 0:  # NOTE: Once in a while flakiness
        assert operators_length_before != operators_length_after
    assert users_length_after == 1  # NOTE: God account won't be deleted
    assert operators_length_after == 0


@pytest.mark.usefixtures('c')
def test_csv_export(c):
    header = get_module_columns(User)
    rows = get_module_values(User)

    response = c.post('/csv', data={
        'table': 'User', 'headers': 1, 'delimiter': 0
    }, follow_redirects=True)
    content = response.data.decode('utf-8').split('\r\n')

    assert response.status == '200 OK'
    assert len(content) > (len(rows) + 1)
    assert ','.join(header) == content.pop(0)

    for row in map(','.join, rows):
        assert row == content.pop(0)


@pytest.mark.usefixtures('c')
def test_csv_export_headers_disabled_and_tabs(c):
    header = get_module_columns(User)
    rows = get_module_values(User)

    response = c.post('/csv', data={
        'table': 'User', 'headers': 0, 'delimiter': 1
    }, follow_redirects=True)
    content = response.data.decode('utf-8').split('\r\n')

    assert response.status == '200 OK'
    assert len(content) > len(rows)
    assert '\t'.join(header) not in content

    for row in map('\t'.join, rows):
        assert row == content.pop(0)


@pytest.mark.usefixtures('c')
def test_list_auth_tokens(c):
    response = c.get('/auth_tokens', follow_redirects=True)
    content = response.data.decode('utf-8')

    assert response.status == '200 OK'

    for t in AuthTokens.query:
        assert f'<strong>{t.id}. {t.name}</strong>' in content
        assert t.token in content
        assert (t.description or 'Empty') in content


@pytest.mark.usefixtures('c')
def test_add_auth_tokens(c):
    token_name = 'testing token'
    token_description = 'testing description'

    response = c.post('/auth_tokens_a', data={
        'name': token_name,
        'description': token_description
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert AuthTokens.get(name=token_name) is not None
    assert AuthTokens.get(description=token_description) is not None


@pytest.mark.usefixtures('c')
def test_update_auth_tokens(c):
    token = AuthTokens.get()
    token_name = 'new testing name'
    token_description = 'new testing description'

    response = c.post(f'/auth_tokens_u/{token.id}', data={
        'name': token_name,
        'description': token_description
    }, follow_redirects=True)

    assert response.status == '200 OK'
    assert AuthTokens.get(token.id).name == token_name
    assert AuthTokens.get(token.id).description == token_description


@pytest.mark.usefixtures('c')
def test_delete_auth_token(c):
    token = AuthTokens.get()

    response = c.get(f'/auth_tokens_d/{token.id}', follow_redirects=True)

    assert response.status == '200 OK'
    assert AuthTokens.get(token.id) is None


@pytest.mark.usefixtures('c')
def test_delete_all_auth_tokens(c):
    response = c.get('/auth_tokens_da', follow_redirects=True)

    assert response.status == '200 OK'
    assert AuthTokens.get() is None
