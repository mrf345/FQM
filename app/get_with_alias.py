import sys
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from os import path

try:
    base_path = sys._MEIPASS
except Exception:
    base_path = path.abspath(".")

class Replace(object):
    office = "office"
    ticket = "ticket"
    task = "task"


try:
    if path.isfile(path.join(base_path, 'data.sqlite')):
        Base = automap_base()
        engine = create_engine('sqlite:///' + path.join(base_path, 'data.sqlite'))
        Base.prepare(engine, reflect=True)
        if hasattr(Base.classes, 'aliases'):
            Aliases = Base.classes.aliases
            session = Session(engine)
            alias = session.query(Aliases).first()
    else:
        alias = Replace()
except Exception:
    alias = Replace()


def get_with_alias():
    """ to solve querying aliases without app_context in languages """
    return {
        "Version ": "Version ",
        "\nOffice : ": "\n" + alias.office + " : ",
        "\nCurrent ticket : ": "\nCurrent " + alias.ticket + " : ",
        "\nTickets ahead : ": "\n" + alias.ticket + "s ahead : ",
        "\nTask : ": "\n" + alias.task + " : ",
        "\nTime : ": "\nTime : "
    }
