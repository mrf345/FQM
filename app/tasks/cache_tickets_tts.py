from sqlalchemy.sql import not_

from app.tasks.base import TaskBase
from app.database import Serial, Display_store, Aliases, Settings
from app.middleware import gTTs
from app.utils import log_error
from app.helpers import get_tts_safely


class CacheTicketsAnnouncements(TaskBase):
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
        self.app = app
        self.interval = interval
        self.limit = limit
        self.cached = []

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

    def run(self):
        @self.execution_loop()
        def main():
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
                        self.cached.append(ticket.number)
                        self.log(f'Cached TTS {ticket.number}')

                @self.none_blocking_loop(tickets_to_remove)
                def remove_processed_tickets_from_cache(ticket):
                    self.cached.remove(ticket.number)

            # NOTE: cache stack is adhereing to the limit to avoid overflow
            self.cached = self.cached[:self.limit]
