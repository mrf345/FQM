from flask_restx import fields  # noqa

from app.api import api  # noqa


# TODO: Add Serial model serializer here. And remove `HelloWorldSerializer`.

HelloWorldSerializer = api.model('Hellow', {
    'id': fields.Integer(required=False, description='user identification number'),
    'name': fields.String(required=True, description='user full name', max_length=100, min_length=3),
    'role': fields.String(required=True, description='user role name', enum=['Admin', 'User', 'Operator']),
    'address': fields.String(required=False, description='user full address', max_length=200)})
