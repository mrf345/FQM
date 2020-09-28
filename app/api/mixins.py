from functools import wraps
from http import HTTPStatus
from flask import current_app, request
from flask_restx import abort

from app.database import AuthTokens
from app.api.constants import AUTH_HEADER_KEY


class TokenRequiredMixin:
    auth_methods = ['get', 'post', 'put', 'patch', 'delete']
    auth_message = 'Authentication is required'
    auth_http_code = HTTPStatus.UNAUTHORIZED
    auth_token = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for auth_method in self.auth_methods:
            method = getattr(self, auth_method, None)

            if method:
                setattr(self, auth_method, self._check_auth_token(method))

    def _check_auth_token(self, function):
        # FIXME: This a basic approach to verifying tokens, that's insecure especially
        # without HTTPS, this needs to be replaced with a login based authentication
        # and expiraing temporary tokens rather than constant ones, for better security.
        @wraps(function)
        def decorator(*args, **kwargs):
            token = request.headers.get(AUTH_HEADER_KEY)
            token_chunks = token.split(' ') if token else []

            if len(token_chunks) > 1:
                token = token_chunks[1]

            self.auth_token = AuthTokens.get(token=token)

            if not self.auth_token:
                return abort(code=self.auth_http_code,
                             message=self.auth_message)

            return function(*args, **kwargs)
        return decorator


class GetOrRejectMixin:
    gor_methods = ['get', 'put', 'patch', 'delete']
    module = None
    kwarg = ''
    slug = ''
    gor_message = ''
    gor_http_code = HTTPStatus.NOT_FOUND

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.slug and self.kwarg:
            self.slug = self.kwarg.split('_')[0]

        if not self.gor_message and self.slug:
            self.gor_message = f'{self.slug.title()} not found'

        if self.module and self.kwarg:
            for gor_method in self.gor_methods:
                method = getattr(self, gor_method, None)

                if method:
                    setattr(self, gor_method, self._get_or_reject(method))

    def _get_or_reject(self, function):
        @wraps(function)
        def decorator(*args, **kwargs):
            if self.module and self.kwarg:
                kwarg = kwargs.get(self.kwarg)

                if kwarg:
                    with current_app.app_context():
                        record = self.module.get(kwarg)

                    if not record:
                        abort(code=self.gor_http_code,
                              message=self.gor_message)

                    setattr(self, self.slug, record)

            return function(*args, **kwargs)
        return decorator
