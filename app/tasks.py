''' This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/. '''

from time import sleep
from importlib import import_module
from threading import Thread
from sqlalchemy.sql import not_

from app.database import Serial, Display_store, Aliases
from app.middleware import gTTs
from app.utils import log_error


class Task:
    ''' Mainly an alternative to a QThread, to use when PyQt is not used. '''
    def __init__(self, app):
        self.thread = None
        self.app = app

    def alt_start(self):
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


class CacheTicketsAnnouncements(Task):
    def __init__(self, app, interval=1, limit=30):
        ''' Task to cache tickets text-to-speech announcement audio files.

        Parameters
        ----------
            app: Flask app
            interval: int
                duration of sleep between iterations in seconds
            limit: int
                limit of tickets to processes each iteration.
        '''
        super().__init__(app)
        self.app = app
        self.interval = interval
        self.limit = limit
        self.cut_circut = False
        self.cached = []

        # FIXME: Move this hardcoding to the database to be customizable in the future
        self.tts_texts = {
            'en-us': ' , please proceed to the {} number : ',
            'ar': ' : توجه إلى المكتب رقم ',
            'fr': ", s'il vous plaît procéder au numéro de bureau : ",
            'es': ' , por favor diríjase al número de la oficina : ',
            'it': " , si prega di procedere al numero dell'ufficio : "
        }

    def format_announcement_text(self, ticket, aliases, language, show_prefix):
        ''' Helper to format text-to-speech text.

        Parameters
        ----------
            ticket: Serial record
            aliases: Aliases record
            language: str
                language of text-to-speech to produce
            show_prefix: bool
                include the office prefix in the announcement

        Returns
        -------
            String of formated text-to-speech text ready to use.
        '''
        with self.app.app_context():
            office = ticket.office
            prefix = office.prefix if show_prefix else ''
            office_text = f'{prefix}{office.name}'
            tts_text = self.tts_texts.get(language)

            if language == 'en-us':
                tts_text = tts_text.format(aliases.office)

            return f'{ticket.display_text}{tts_text}{office_text}'

    def run(self):
        while not self.cut_circut:
            with self.app.app_context():
                display_settings = Display_store.query.first()

                if display_settings.announce != 'false':
                    aliases = Aliases.query.first()
                    languages = display_settings.announce.split(',')
                    tickets_to_remove = Serial.query.filter(Serial.p == True,
                                                            Serial.number.in_(self.cached))
                    tickets_to_cache = Serial.query.filter(Serial.p == False,
                                                           Serial.number != 100,
                                                           not_(Serial.number.in_(self.cached)))\
                                                   .order_by(Serial.timestamp)\
                                                   .limit(self.limit)

                    for ticket in tickets_to_cache:
                        success = False

                        for language in languages:
                            try:
                                gTTs.say(language,
                                         self.format_announcement_text(ticket,
                                                                       aliases,
                                                                       language,
                                                                       display_settings.prefix))
                                success = True
                            except Exception as exception:
                                log_error(exception)

                        if success:
                            self.cached.append(ticket.number)
                            # TODO: Use a proper logger to integrate with gevent's ongoing one
                            print(f'Cached TTS {ticket.number}')

                    # NOTE: Remove the processed tickets from cache stack
                    for ticket in tickets_to_remove:
                        self.cached.remove(ticket.number)

            # NOTE: cache stack is adhereing to the limit to avoid overflow
            self.cached = self.cached[:self.limit]
            sleep(self.interval)

    def stop(self):
        self.cut_circut = True


TASKS = [CacheTicketsAnnouncements]
THREADS = {}


def start_tasks(app):
    ''' start all tasks in `TASKS`.

    Parameters
    ----------
        app: Flask app

    Returns
    -------
        List of running QThreads.
    '''
    for task in TASKS:
        if task.__name__ not in THREADS:
            THREADS[task.__name__] = task(app)
            THREADS[task.__name__].alt_start()

    return THREADS


def stop_tasks(tasks=[]):
    ''' stop all tasks in `tasks or TASKS`.

    Parameters
    ----------
        tasks: list
            list of task names to stop, if empty will stop all.
    '''
    threads = []

    if tasks:
        threads += [i for i in THREADS.items() if i[0] in tasks]
    else:
        threads += THREADS.items()

    for task, thread in threads:
        print(f'Stopping task: {task} ...')
        thread.stop()
