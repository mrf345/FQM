import pytest
from time import sleep

from . import c  # noqa
from app.tasks import stop_tasks, get_task

@pytest.fixture
def get_bg_task():
    def waitier(task_name):
        task = get_task(task_name)
        get_bg_task.__dict__['TASK'] = task

        if not task:
            raise AttributeError(f'Background Task `{task_name}` is not running.')

        while not task.spinned_once:
            sleep(1)

        return task

    yield waitier

    stop_tasks()
    while not get_bg_task.__dict__['TASK'].dead:
        sleep(1)
