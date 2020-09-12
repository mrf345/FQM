from functools import wraps
from http import HTTPStatus
from flask import request, current_app
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

        auth_token = AuthTokens.get(token=token)

        if not auth_token:
            return abort(code=HTTPStatus.UNAUTHORIZED,
                         message='Authentication is required')

        try:
            setattr(args[0], 'auth_token', auth_token)
        except Exception:
            pass

        return function(*args, **kwargs)

    return decorator


def get_or_reject(**models):
    def wrapper(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            with current_app.app_context():
                new_kwargs = {}

                for kwarg, model in models.items():
                    if not kwarg.startswith('_'):
                        record = model.get(kwargs.get(kwarg))
                        column_name = getattr(model, '__tablename__', ' ')[:-1]

                        if not record:
                            abort(message=models.get('_message', 'Model instance not found.'),
                                  code=HTTPStatus.NOT_FOUND)

                        if column_name == 'serial':
                            column_name = 'ticket'

                        new_kwargs[column_name] = record

                for kwarg, value in kwargs.items():
                    if kwarg not in new_kwargs and kwarg not in models:
                        new_kwargs[kwarg] = value

                if len(kwargs.keys()) != len(new_kwargs.keys()):
                    raise AttributeError('Modules list mismatch arguments.')

                return function(*args, **new_kwargs)
        return decorator
    return wrapper
