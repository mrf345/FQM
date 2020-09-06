import pytest
from time import sleep

from . import c  # noqa
from app.tasks import stop_tasks

@pytest.fixture
def await_task():
    def waitier(task):
        await_task.__dict__['TASK'] = task

        while not task.spinned_once:
            sleep(1)

    yield waitier

    stop_tasks()
    while not await_task.__dict__['TASK'].dead:
        sleep(1)
