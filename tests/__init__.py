import os
import copy
import pytest
import atexit
import shutil
from random import choice, randint

from app.main import bundle_app
from app.middleware import db
from app.database import (User, Operators, Office, Task, Serial, Media, Touch_store,
                          Display_store, Vid, Slides_c, Slides, Aliases, Printer,
                          Settings, AuthTokens)
from app.utils import absolute_path, is_iterable
from app.tasks import stop_tasks
from app.views.core import touch


NAMES = ('Aaron Enlightened', 'Abbott Father', 'Abel Breath', 'Abner Father',
         'Abraham Exalted', 'Adam Man', 'Addison Son', 'Adler Eagle',
         'Adley The Just', 'Adrian Dark', 'Aedan Fire', 'Alan Handsome',
         'Alastair Defender', 'Albern Noble', 'Albert Bright', 'Albion Fair',
         'Alden Guardian', 'Aldis Old', 'Aldrich Leader',
         'Alexander Protector', 'Alfred Wise', 'Avery Elfin Ruler',
         'Alvin Friend', 'Ambrose Immortal', 'Amery Industrious',
         'Amos A Burden', 'Andrew Valiant', 'Angus Unique', 'Ansel Nobel',
         'Anthony Priceless', 'Archer Bowman', 'Archibald Prince',
         'Arlen Pledge', 'Arnold Eagle', 'Arvel Wept', 'Atwater Waterside',
         'Atwood Forest', 'Aubrey Ruler', 'Austin Helpful',
         'Axel Peace', 'Baird Bard', 'Baldwin Friend', 'Barnaby Prophet',
         'Baron Nobleman', 'Barrett Bear-Like', 'Barry Marksman',
         'Bartholomew Warlike', 'Basil King-like')
TEST_PREFIX = 'Z'
PREFIXES = [p for p in list(map(lambda i: chr(i).upper(), range(97, 123))) if p != TEST_PREFIX]

MODULES = [Serial, User, Operators, Task, Office, Media, Slides, AuthTokens]
DEFAULT_MODULES = [Touch_store, Display_store, Vid, Slides_c, Aliases, Printer, Settings]
DB_NAME = 'testing.sqlite'
DB_PATH = absolute_path(DB_NAME)
TEST_REPEATS = 3
ENTRY_NUMBER = 4


def teardown_tables(modules):
    if modules:
        modules.pop().query.delete()
        db.session.commit()
        return teardown_tables(modules)


def setup_data():
    db.create_all()
    teardown_tables(copy.copy(MODULES))
    recreate_defaults(DEFAULT_MODULES)
    fill_offices()
    fill_tasks()
    fill_users()
    fill_tickets()
    fill_slides()
    fill_tokens()    


def recreate_defaults(models):
    for model in models:
        model.query.delete()
        db.session.commit()

        db.session.add(model())
        db.session.commit()


def fill_users(entry_number=ENTRY_NUMBER, role=None):
    for _ in range(entry_number):
        def recur():
            role_id = role or choice(range(1, 4))
            snm = "TEST" + str(randint(10000, 99999999))
            go = True if User.query.filter_by(name=snm).first() is None else False

            if not go:
                return recur()
            user = User(snm, snm, role_id)

            db.session.add(user)
            db.session.commit()
            role_id == 3 and db.session.add(Operators(
                id=user.id,
                office_id=choice(Office.query.all()).id
            ))

        recur()
    db.session.commit()


def fill_offices(entry_number=ENTRY_NUMBER):
    for _ in range(entry_number):
        prefix = choice([
            p for p in PREFIXES
            if not Office.query.filter_by(prefix=p).first()
        ] or [None]) or None

        prefix and db.session.add(Office(
            randint(10000, 9999999),
            prefix
        ))

    db.session.commit()


def fill_tasks(entry_number=ENTRY_NUMBER):
    for _ in range(entry_number):
        name = f'TEST{randint(10000, 99999999)}'
        offices = []
        # First task will be uncommon task and the second is common
        number_of_offices = 1 if _ == 0 else 2 if _ == 1 else choice(range(1, 5))

        while number_of_offices > len(offices):
            office = choice(Office.query.all())

            if office not in offices:
                offices.append(office)

        task = Task(name)
        db.session.add(task)
        db.session.commit()
        task.offices = offices
        # Add tasks initial tickets
        db.session.add(Serial(number=100, office_id=office.id, task_id=task.id))
        db.session.commit()


def fill_tickets(entry_number=ENTRY_NUMBER * 2):
    for _ in range(entry_number):
        last_ticket = Serial.query.order_by(Serial.number.desc()).first()
        number = (last_ticket.number if last_ticket else 100) + 1
        name = choice(NAMES)
        task = choice(Task.query.all())
        office = choice(task.offices)

        db.session.add(Serial(number=number, office_id=office.id,
                              task_id=task.id, name=name, n=True))
    db.session.commit()


def fill_slides(entry_number=ENTRY_NUMBER):
    for i in range(entry_number):
        slide = Slides()
        slide.title = f'{i}_testing'
        slide.bname = f'{i}_testing.ext'

        db.session.add(slide)

    db.session.commit()


def fill_tokens(entry_number=ENTRY_NUMBER):
    for i in range(entry_number):
        db.session.add(AuthTokens(choice(NAMES)))

    db.session.commit()


def get_first_office_with_tickets(client):
    with client.application.app_context():
        offices = Office.query.all()

        while offices:
            office = offices.pop()

            if Serial.query.filter(Serial.number != 100,
                                   Serial.office_id == office.id)\
                           .first():
                return office


def do_until_truthy(todo, getter):
    value = getter()

    while not (all(value) if is_iterable(value) else value):
        todo()
        value = getter()

    return value


def clear_cache():
    touch.cache_clear()


@atexit.register
def before_exit():
    os.path.isfile(DB_PATH) and os.remove(DB_PATH)
    os.path.isfile(absolute_path('errors.log')) and os.remove(absolute_path('errors.log'))


@pytest.fixture
def c():
    dump_db = f'{DB_PATH}.backup'
    dump_exists = os.path.isfile(dump_db)

    if dump_exists:
        shutil.copyfile(dump_db, DB_PATH)

    app_config = {'LOGIN_DISABLED': True,
                  'WTF_CSRF_ENABLED': False,
                  'TESTING': True,
                  'DB_NAME': DB_NAME,
                  'SQLALCHEMY_DATABASE_URI': f'sqlite:///{DB_PATH}?check_same_thread=False'}
    app = bundle_app(app_config)

    stop_tasks()
    clear_cache()
    with app.test_client() as client:
        with app.app_context():
            if not dump_exists:
                setup_data()
                shutil.copyfile(DB_PATH, dump_db)
            yield client
