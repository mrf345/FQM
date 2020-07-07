import pytest
from flask_migrate import upgrade as database_upgrade

from app.constants import MIGRATION_FOLDER
from app.utils import absolute_path


@pytest.mark.usefixtures('c')
def test_upgrading_database(c):
    assert database_upgrade(directory=absolute_path(MIGRATION_FOLDER)) is None
