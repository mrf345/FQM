from http import HTTPStatus
from flask_restx import Resource, abort
from flask import request

from app.api import api
from app.api.helpers import token_required, get_or_reject
from app.api.serializers import TicketSerializer
from app.api.constants import LIMIT_PER_CHUNK
from app.database import Serial, Task, Office
from app.middleware import db


def setup_tickets_endpoint():
    endpoint = api.namespace(name='tickets',
                             description='Endpoint to handle tickets CRUD operations.')

    @endpoint.route('/')
    class ListDeleteAndCreateTickets(Resource):
        @endpoint.marshal_list_with(TicketSerializer)
        @endpoint.param('processed', 'get only processed tickets, by default False.')
        @endpoint.param('chunk', f'dividing tickets into chunks of {LIMIT_PER_CHUNK}, default is 1.')
        @endpoint.doc(security='apiKey')
        @token_required
        def get(self):
            ''' Get list of tickets. '''
            chunk = request.args.get('chunk', 1, type=int)
            processed = request.args.get('processed', False, type=bool)
            tickets = Serial.all_clean()

            if processed:
                tickets = tickets.filter_by(p=True)

            return tickets.paginate(chunk,
                                    per_page=LIMIT_PER_CHUNK,
                                    error_out=False).items, HTTPStatus.OK

        @endpoint.doc(security='apiKey')
        @token_required
        def delete(self):
            ''' Delete all tickets. '''
            Serial.all_clean().delete()
            db.session.commit()
            return '', HTTPStatus.NO_CONTENT

        @endpoint.marshal_with(TicketSerializer)
        @endpoint.expect(TicketSerializer)
        @endpoint.doc(security='apiKey')
        @token_required
        def post(self):
            ''' Generate a new ticket. '''
            registered = api.payload.get('n', False)
            name_or_number = api.payload.get('name', None)
            task = Task.get(api.payload.get('task_id', None))
            office = Office.get(api.payload.get('office_id', None))

            if not task:
                abort(message='Task not found', code=HTTPStatus.NOT_FOUND)

            if registered and not name_or_number:
                abort(message='Name must be entered for registered tickets.',
                      code=HTTPStatus.NOT_FOUND)

            ticket, exception = Serial.create_new_ticket(task,
                                                         office,
                                                         name_or_number)

            if exception:
                abort(message=str(exception))

            return ticket, HTTPStatus.OK

    @endpoint.route('/<int:ticket_id>')
    class GetAndUpdateTicket(Resource):
        @endpoint.marshal_with(TicketSerializer)
        @endpoint.doc(security='apiKey')
        @token_required
        @get_or_reject(ticket_id=Serial, _message='Ticket not found')
        def get(self, ticket):
            ''' Get a specific ticket. '''
            return ticket, HTTPStatus.OK

        @endpoint.marshal_with(TicketSerializer)
        @endpoint.expect(TicketSerializer)
        @endpoint.doc(security='apiKey')
        @token_required
        def put(self, ticket_id):
            ''' Update a specific ticket. '''
            ticket = Serial.get(ticket_id)

            if not ticket:
                abort(message='Ticket not found', code=HTTPStatus.NOT_FOUND)

            api.payload.pop('id', '')
            ticket.query.update(api.payload)
            db.session.commit()
            return ticket, HTTPStatus.OK

        @endpoint.doc(security='apiKey')
        @token_required
        @get_or_reject(ticket_id=Serial, _message='Ticket not found')
        def delete(self, ticket):
            ''' Delete a specific ticket. '''
            db.session.delete(ticket)
            db.session.commit()
            return '', HTTPStatus.NO_CONTENT

    @endpoint.route('/pull')
    class PullTicket(Resource):
        @endpoint.marshal_with(TicketSerializer)
        @endpoint.param('ticket_id', 'to pull a specific ticket with, by default None.')
        @endpoint.param('office_id', 'to pull a specific ticket from, by default None.')
        @endpoint.doc(security='apiKey')
        @token_required
        def get(self):
            ''' Pull a ticket from the waiting list. '''
            ticket_id = request.args.get('ticket_id', None, type=int)
            office_id = request.args.get('office_id', None, type=int)
            ticket = Serial.get(ticket_id)

            if ticket_id and not ticket:
                abort(message='Ticket not found', code=HTTPStatus.NOT_FOUND)

            next_ticket = ticket or Serial.get_next_ticket()

            if not next_ticket:
                abort(message='No tickets left to pull', code=HTTPStatus.NOT_FOUND)

            next_ticket.pull(office_id, self.auth_token and self.auth_token.id)
            return next_ticket, HTTPStatus.OK
