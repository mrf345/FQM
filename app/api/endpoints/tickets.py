from http import HTTPStatus
from flask_restx import Resource

from app.api import api
from app.api.auth import token_required
from app.api.serializers import HelloWorldSerializer


def setup_tickets_endpoint():
    endpoint = api.namespace(name='tickets',
                             description='Endpoint to handle tickets CRUD operations.')

    @endpoint.route('/')
    class HelloWorld(Resource):
        ''' Just returns a hello world! '''

        @endpoint.marshal_with(HelloWorldSerializer)
        def get(self):
            ''' Get first HelloWorld. '''
            return 'Hello world!', HTTPStatus.OK

        @endpoint.marshal_with(HelloWorldSerializer)
        @endpoint.expect(HelloWorldSerializer)
        @endpoint.doc(security='apiKey')
        @token_required
        def post(self):
            ''' Create HelloWorld. '''
            return 'Hello world!', HTTPStatus.OK


# TODO: Add Ticket `Serials` CRUD endpoints here. And remove `HelloWorld`.
