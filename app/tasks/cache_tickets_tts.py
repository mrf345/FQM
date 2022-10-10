from datetime import timedelta
from time import time

from sqlalchemy.sql import not_

from app.tasks.base import TaskBase
from app.database import Serial, Display_store, Aliases, Settings
from app.middleware import gTTs, redis
from app.tasks.celery import CeleryTaskBase, CeleryTasks
from app.utils import log_error
from app.helpers import get_tts_safely


class CacheTicketsMixin:
    use_context = True
    limit = 30
    _cached = []

    @property
    def cached(self):
        return self._cached

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
            String of formatted text-to-speech text ready to use.
        '''
        def _todo():
            single_row_queuing = Settings.get().single_row
            office_text = ''
            tts_text = ''

            if not single_row_queuing:
                office = ticket.office
                prefix = office.prefix if show_prefix else ''
                office_text = f'{prefix}{getattr(office, "name", "")}'
                tts_text = get_tts_safely().get(language, {})\
                                           .get('message')

                if language.startswith('en'):
                    tts_text = tts_text.format(aliases.office)

            return ticket.display_text if single_row_queuing\
                else f'{ticket.display_text}{tts_text}{office_text}'

        if self.use_context:
             with self.app.app_context():
                return _todo()

        return _todo()

    def cache_tickets(self):
        display_settings = Display_store.get()

        if display_settings.announce != 'false':
            aliases = Aliases.get()
            languages = display_settings.announce.split(',')
            tickets_to_remove = Serial.query.filter(Serial.p == True,
                                                    Serial.number.in_(self.cached))
            tickets_to_cache = Serial.query.filter(Serial.p == False,
                                                Serial.number != 100,
                                                not_(Serial.number.in_(self.cached)))\
                                        .order_by(Serial.timestamp)\
                                        .limit(self.limit)

            @self.none_blocking_loop(tickets_to_cache)
            def cache_tickets(ticket):
                successes = []

                @self.none_blocking_loop(languages)
                def loop_languages(language):
                    try:
                        gTTs.say(language,
                                 self.format_announcement_text(ticket,
                                                               aliases,
                                                               language,
                                                               display_settings.prefix))
                        successes.append(language)
                    except Exception as exception:
                        log_error(exception, quiet=self.quiet)
                        self.log(exception, error=True)

                if successes:
                    self.add_to_cached(ticket.number)
                    self.log(f'Cached TTS {ticket.number}')

            @self.none_blocking_loop(tickets_to_remove)
            def remove_processed_tickets_from_cache(ticket):
                self.remove_from_cached(ticket.number)

            self.commit_cached()

    def add_to_cached(self, ticket_number):
        self._cached.append(ticket_number)

    def remove_from_cached(self, ticket_number):
        self._cached.remove(ticket_number)

    def commit_cached(self):
        self._cached = self._cached[:self.limit]


class CacheTicketsAnnouncements(CacheTicketsMixin, TaskBase):
    def __init__(self, app, interval=5, limit=30):
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
        self._app = app
        self.interval = interval
        self.limit = limit
        self._cached = []

    def run(self):
        @self.execution_loop()
        def main():
            self.cache_tickets()


@CeleryTasks.add
class CacheTicketsAnnouncementsCelery(CacheTicketsMixin, CeleryTaskBase):
    proxy = 'CacheTicketsAnnouncements'
    quiet = True
    use_context = False
    cache_expiry = timedelta(hours=1)

    @property
    def cached(self):
        return (
            k.decode('utf-8').split('.')[1]
            for k in redis.scan_iter(f'{self.proxy}\.*')
        )

    def add_to_cached(self, ticket_number):
        redis.set(f'{self.proxy}.{ticket_number}', '', ex=self.cache_expiry)

    def remove_from_cached(self, ticket_number):
        redis.delete(f'{self.proxy}.{ticket_number}')

    def run(self):
        self.cache_tickets()
        print(list(self.cached))

    def none_blocking_loop(self, items):
        def wrapper(func):
            for item in items:
                func(item)

        return wrapper

    def log(self, exception, error=False):
        print(exception)
