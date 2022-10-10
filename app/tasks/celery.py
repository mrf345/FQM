from collections import namedtuple
from time import sleep

import schedule

from app.database import BackgroundTask, Serial
from app.middleware import db, celery_app, redis


class CeleryTasks:
    _classes = set()
    _tasks = {}
    _runner = None

    @classmethod
    def add(cls, task):
        cls._classes.add(task)
        return task

    @classmethod
    def register(cls):
        for class_task in cls._classes:
            inst = class_task()
            celery_app.app.register_task(inst)

            if inst.proxy == 'CeleryTasksRunner':
                cls._runner = inst
            else:
                cls._tasks[inst.proxy] = inst


class StartStopTaskMixin:
    def stop(self):
        task_id = redis.get(self.proxy)

        if task_id is not None:
            celery_app.app.control.revoke(task_id.decode('utf-8'), terminate=True)

    def apply_async(self, *args, **kwargs):
        result = super().apply_async(*args, **kwargs)
        redis.set(self.proxy, result.task_id)
        return result


@CeleryTasks.add
class CeleryTasksRunner(StartStopTaskMixin, celery_app.app.Task):
    _running_tasks = {}
    proxy = 'CeleryTasksRunner'

    @property
    def settings(self):
        return namedtuple('Settings', ['enabled'])(True)

    def run(self):
        self._queue_tasks()

        while True:
            schedule.run_pending()
            sleep(1)

    def _queue_tasks(self, tasks=None):
        for task in (tasks or CeleryTasks._tasks.values()):
            if task.settings.enabled and task.proxy not in self._running_tasks:
                if task.settings.time:
                    job = getattr(schedule.every(), task.settings.every)\
                        .at(task.settings.time.strftime('%H:%M'))\
                        .do(task.apply_async)
                else:
                    job = getattr(schedule.every(), task.settings.every) \
                        .do(task.apply_async)

                self._running_tasks[task.proxy] = job

    def stop(self):
        for job in self._running_tasks.values():
            schedule.cancel_job(job)

        for task in CeleryTasks._tasks.values():
            task.stop()

        super().stop()


class CeleryTaskBase(StartStopTaskMixin, celery_app.app.Task):
    @property
    def settings(self):
        return BackgroundTask.get(name=self.proxy)
