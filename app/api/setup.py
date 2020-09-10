from flask import Blueprint

from app.api import api
from app.api.endpoints.tickets import setup_tickets_endpoint


def setup_api():
    blueprint = Blueprint('api', __name__)

    api.init_app(blueprint)
    setup_tickets_endpoint()

    return blueprint
