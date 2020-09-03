from time import sleep
from importlib import import_module
from threading import Thread

from app.utils import create_aliternative_db


class Task:
    ''' A base for tasks and mainly an alternative to a QThread, to use when PyQt is not used. '''
    def __init__(self, app):
        self.thread = None
        self.app = app
        self.cut_circut = False
        self.interval = 5
        self.spinned = False
        self.spinned_once = False

    @property
    def quiet(self):
        return self.app.config.get('QUIET', False)

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

    def execution_loop(self, bundle_db=False):
        def wrapper(todo):
            while not self.cut_circut:
                args = ()

                if bundle_db:
                    args = create_aliternative_db(self.app.config.get('DB_NAME'))

                self.spinned = False
                with self.app.app_context():
                    todo(*args)
                self.spinned = True
                self.spinned_once = True

                if bundle_db:
                    session, db, eng = args

                    session.close()
                    eng.dispose()

                self.sleep()

        return wrapper

    def none_blocking_loop(self, iterator=[]):
        def wrapper(todo):
            for i in iterator:
                if self.cut_circut:
                    break

                todo(i)

        return wrapper

    def stop(self):
        self.cut_circut = True

    def sleep(self, duration=0):
        self.none_blocking_loop(range(duration or self.interval))(lambda _: sleep(1))

    def log(self, message, error=False):
        if not self.quiet:
            if error:
                self.app.logger.exception(message)
            else:
                self.app.logger.info(message)
