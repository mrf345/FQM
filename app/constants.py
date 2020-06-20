# Current FQM Version
VERSION = "0.8 beta"

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

USER_ROLES = {
    # NOTE: User roles keyed with their ids.
    1: 'Administrator',
    2: 'Monitor',
    3: 'Operator'
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
