from flask_restx import fields

from app.api import api


TicketSerializer = api.model('Ticket', {
    'id': fields.Integer(required=False, description='ticket identification number.'),
    'number': fields.String(required=False, description='ticket number.'),
    'timestamp': fields.DateTime(required=False, description='date and time of ticket generation.'),
    'date': fields.DateTime(required=False, description='date of ticket generation.'),
    'name': fields.String(required=False, description='registered ticket stored value.'),
    'n': fields.Boolean(required=False, description='ticket is registered.'),
    'p': fields.Boolean(required=False, description='ticket is processed.'),
    'pdt': fields.DateTime(required=False, description='ticket pulled date and time.'),
    'pulledBy': fields.Integer(required=False, description='user id or token id that pulled ticket.'),
    'on_hold': fields.Boolean(required=False, description='ticket is put on hold.'),
    'status': fields.String(required=False, description='ticket processing status.'),
    'office_id': fields.Integer(required=False, description='office ticket belongs to.'),
    'task_id': fields.Integer(required=False, description='task ticket belongs to.'),
})


TaskSerializer = api.model('Task', {
    'id': fields.Integer(required=False, description='task identification number.'),
    'name': fields.String(required=False, description='task name.'),
    'timestamp': fields.DateTime(required=False, description='date and time of task creation.'),
    'hidden': fields.Boolean(required=False, description='task is is hidden in the touch screen.'),
})
