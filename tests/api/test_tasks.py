import pytest

from app.database import AuthTokens, Task
from app.utils import get_module_columns
from app.api.constants import LIMIT_PER_CHUNK


BASE = '/api/v1/tasks'


@pytest.mark.usefixtures('c')
def test_list_tickets(c):
    auth_token = AuthTokens.get()
    response = c.get(BASE,
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token})

    assert response.status == '200 OK'
    assert len(response.json) > 0
    assert LIMIT_PER_CHUNK > len(response.json)

    for t in response.json:
        assert Task.get(t.get('id')) is not None
        assert all(p in t for p in get_module_columns(Task)) is True
