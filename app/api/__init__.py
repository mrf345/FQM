from flask_restx import Api

from app.api.constants import AUTH_HEADER_KEY


title = 'FQM API'
description = 'Free Queue Manage API'
auth_config = {'apiKey': {'type': 'apiKey',
                          'in': 'headers',
                          'name': AUTH_HEADER_KEY}}

api = Api(title=title,
          description=description,
          authorizations=auth_config,
          validate=True)
