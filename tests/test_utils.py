import pytest
import os

from . import DB_NAME
from app.middleware import db
from app.database import (Aliases)
from app.utils import (get_with_alias, execute, absolute_path)


@pytest.mark.usefixtures('c')
def test_get_with_alias(c, monkeypatch):
    office = 't_office'
    task = 't_task'
    ticket = 't_ticket'
    aliases = Aliases.get()
    aliases.office = office
    aliases.task = task
    aliases.ticket = ticket
    db.session.commit()

    alt_aliases = get_with_alias(DB_NAME)

    assert office in alt_aliases.get('\nOffice : ')
    assert ticket in alt_aliases.get('\nCurrent ticket : ')
    assert task in alt_aliases.get('\nTask : ')


def test_execute():
    path = absolute_path('static')

    assert sorted(execute(f'ls {path}', parser='\n')) == sorted(os.listdir(path))
