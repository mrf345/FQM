from functools import wraps
from http import HTTPStatus
from flask import request
from flask_restx import abort

from app.database import AuthTokens
from app.api.constants import AUTH_HEADER_KEY


def token_required(function):
    # FIXME: This a basic approach to verifying tokens, that's insecure especially
    # without HTTPS, this needs to be replaced with a login based authentication
    # and expiraing temporary tokens rather than constant ones, for better security.
    @wraps(function)
    def decorator(*args, **kwargs):
        token = request.headers.get(AUTH_HEADER_KEY)
        token_chunks = token.split(' ') if token else []

        if len(token_chunks) > 1:
            token = token_chunks[1]

        if not AuthTokens.get(token=token):
            return abort(code=HTTPStatus.UNAUTHORIZED,
                         message='Authentication is required')

        return function(*args, **kwargs)

    return decorator
