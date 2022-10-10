import schedule
from time import sleep
from importlib import import_module
from threading import Thread

from app.database import BackgroundTask


class TaskBase:
    ''' A base for tasks and mainly an alternative to a QThread, to use when PyQt is not used. '''
    def __init__(self, app):
        self.thread = None
        self.app = app
        self.cut_circuit = False
        self.interval = 5
        self.spinned = False
        self.spinned_once = False
        self.dead = False

    @property
    def quiet(self):
        return self.app.config.get('QUIET', False)

    @property
    def settings(self):
        ''' Get the task settings, or fallback to defaults. '''
        with self.app.app_context():
            return BackgroundTask.get(name=self.__class__.__name__)

    def init(self):
        if not self.app.config.get('CLI_OR_DEPLOY', True):
            PyQt5 = import_module('PyQt5')

            class QThreadBase(PyQt5.QtCore.QThread):
                pass

            if self.__class__ != QThreadBase:
                self.__class__ = QThreadBase
                PyQt5.QtCore.QThread.__init__(self)

            return self.start()

        self.thread = Thread(target=self.run)
        self.thread.start()

    def execution_loop(self):
        def wrapper(todo):
            args, kwargs = (), {}
            task_settings = self.settings
            job = None

            def _doer():
                self.spinned = False

                with self.app.app_context():
                    todo(*args, **kwargs)

                self.spinned = True
                self.spinned_once = True

            if task_settings.time:
                job = getattr(schedule.every(), task_settings.every)\
                    .at(task_settings.time.strftime('%H:%M'))\
                    .do(_doer)
            else:
                job = getattr(schedule.every(), task_settings.every).do(_doer)

            while not self.cut_circuit:
                schedule.run_pending()
                self.sleep()

            schedule.cancel_job(job)

            self.dead = True

        return wrapper

    def none_blocking_loop(self, iterator=[]):
        def wrapper(todo):
            for i in iterator:
                if self.cut_circuit:
                    break

                todo(i)

        return wrapper

    def stop(self):
        self.cut_circuit = True

    def sleep(self, duration=0):
        self.none_blocking_loop(range(duration or self.interval))(lambda _: sleep(1))

    def log(self, message, error=False):
        if not self.quiet:
            if error:
                self.app.logger.exception(message)
            else:
                self.app.logger.info(message)
