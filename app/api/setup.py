from flask import Blueprint

from app.api import api
from app.api.endpoints.tickets import setup_tickets_endpoint
from app.api.endpoints.tasks import setup_tasks_endpoint


def setup_api():
    blueprint = setup_api.__dict__.get('blueprint')

    if blueprint:
        return blueprint

    blueprint = setup_api.__dict__['blueprint'] = Blueprint('api', __name__)

    api.init_app(blueprint)
    setup_tickets_endpoint()
    setup_tasks_endpoint()

    return blueprint
