from http import HTTPStatus
from flask_restx import Resource
from flask import request

from app.api import api
from app.api.mixins import TokenRequiredMixin
from app.api.serializers import TaskSerializer
from app.api.constants import LIMIT_PER_CHUNK
from app.database import Task


def setup_tasks_endpoint():
    endpoint = api.namespace(name='tasks',
                             description='Endpoint to handle tasks CRUD operations.')

    @endpoint.route('/')
    @endpoint.doc(security='apiKey')
    class ListTasks(TokenRequiredMixin, Resource):
        @endpoint.marshal_list_with(TaskSerializer)
        @endpoint.param('chunk', f'dividing tasks into chunks of {LIMIT_PER_CHUNK}, default is 1.')
        def get(self):
            ''' Get list of tasks. '''
            chunk = request.args.get('chunk', 1, type=int)

            return Task.query.paginate(chunk,
                                       per_page=LIMIT_PER_CHUNK,
                                       error_out=False).items, HTTPStatus.OK
