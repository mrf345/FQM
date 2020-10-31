import os

from app.env_vars import VERSION  # noqa


SUPPORTED_LANGUAGES = {
    # NOTE: The officially supported languages.
    'en': 'English',
    'ar': 'Arabic',
    'fr': 'French',
    'it': 'Italian',
    'es': 'Spanish'
}

SUPPORTED_MEDIA_FILES = [
    # NOTE: The officially supported media files.
    ['jpg', 'JPG', 'png', 'PNG'],  # Images
    ['wav', 'WAV', 'mp3', 'MP3'],  # Audio
    ['mp4', 'MP4', 'AVI', 'avi',
     'webm', 'WEBM', 'mkv', 'MKV']  # Video
]


USER_ROLE_ADMIN = 1
USER_ROLE_MONITOR = 2
USER_ROLE_OPERATOR = 3
USER_ROLES = {
    # NOTE: User roles keyed with their ids.
    USER_ROLE_ADMIN: 'Administrator',
    USER_ROLE_MONITOR: 'Monitor',
    USER_ROLE_OPERATOR: 'Operator'
}

PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH = 8
PRINTED_TICKET_SCALES = range(1, 4)
PRINTED_TICKET_DIMENSIONS = {
    # NOTE: Default printer fonts sizing (height, width).
    'regular': (1, 1),
    'logo': (4, 4),
    'spacer': (1, 2),
    'large': (3, 3)
}

DEFAULT_PASSWORD = 'admin'
DEFAULT_USER = 'Admin'

MIGRATION_FOLDER = 'migrations'
DATABASE_FILE = 'data.sqlite'

PREFIXES = [p for p in list(map(lambda i: chr(i).upper(), range(97, 123)))]

TICKET_STATUSES = ['Waiting', 'Processed', 'Unattended']
TICKET_WAITING, TICKET_PROCESSED, TICKET_UNATTENDED = TICKET_STATUSES
TICKET_ORDER_NEWEST = 'newest tickets'
TICKET_ORDER_NEWEST_PROCESSED = 'newest processed tickets'
TICKET_ORDER_OLDEST = 'oldest tickets'
TICKET_ORDER_OLDEST_PROCESSED = 'oldest processed tickets'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))


BACKGROUNDTASKS_DEFAULTS = {
    'CacheTicketsAnnouncements': {'enabled': True, 'every': 'second'},
    'DeleteTickets': {'enabled': False, 'every': 'hour'}
}
