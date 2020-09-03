import os
from app.main import bundle_app # noqa

# NOTE: uncomment out while genrating migration
# app = bundle_app({'MIGRATION': True})

application = bundle_app({
    'CLI_OR_DEPLOY': True,
    'GUNICORN': 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '')})  # noqa
