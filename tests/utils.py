import pytest

from .common import DB_NAME
from app.middleware import db
from app.utils import (get_with_alias)
from app.database import (Aliases)


@pytest.mark.usefixture('c')
def test_get_with_alias(c, monkeypatch):
    office = 't_office'
    task = 't_task'
    ticket = 't_ticket'

    with c.application.app_context():
        aliases = Aliases.get()
        aliases.office = office
        aliases.task = task
        aliases.ticket = ticket

        db.session.commit()

    alt_aliases = get_with_alias(DB_NAME)

    assert office in alt_aliases.get('\nOffice : ')
    assert ticket in alt_aliases.get('\nCurrent ticket : ')
    assert task in alt_aliases.get('\nTask : ')
