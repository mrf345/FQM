import os # noqa
from app.main import bundle_app # noqa

# NOTE: uncomment out while genrating migration
# app = bundle_app({'MIGRATION': True})

# NOTE: uncomment out when running with gunicorn
# application = bundle_app({
#     'CLI_OR_DEPLOY': True,
#     'GUNICORN': 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '')})  # noqa
