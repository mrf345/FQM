import os
import tempfile
import pytest
from random import choice, randint
from atexit import register

from app.main import create_db, bundle_app
from app.middleware import db
from app.database import User, Operators, Office, Task
from app.utils import r_path


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

PREFIXES = list(map(lambda i: chr(i).upper(), range(97,123)))


@pytest.fixture
def client():
    app = bundle_app({'LOGIN_DISABLED': True, 'WTF_CSRF_ENABLED': False})
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    db_path = r_path('testing.sqlite')
    print(db_path)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    with app.test_client() as client:
        with app.app_context():
            create_db(app)
            teardown()
            fill_offices()
            fill_tasks()
            fill_users()
        yield client

    register(lambda: os.path.isfile(db_path) and os.remove(db_path))
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def teardown(modules=[User, Operators, Task, Office]):
    if modules:
        for record in modules.pop().query.all():
            db.session.delete(record)
    
        db.session.commit()
        return teardown(modules)


def fill_users(entry_number=10, role=None):
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


def fill_offices(entry_number=10):
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


def fill_tasks(entry_number=10):
    for _ in range(entry_number):
        name = f'TEST{randint(10000, 99999999)}'
        offices = []
        # First task will be uncommon task
        number_of_offices = 1 if _ == 0 else choice(range(1, 5))

        while number_of_offices > len(offices):
            office = choice(Office.query.all())

            if office not in offices:
                offices.append(office)
        
        task = Task(name)
        db.session.add(task)
        db.session.commit()
        task.offices = offices
        db.session.commit()


# TODO: get refactor the helper to fit the testing process
# def fill_tickets(entery_number=10, s_task=None):
#     for i in range(entery_number):
#         forin = Task.query if s_task is None else Task.query.filter_by(
#             id=s_task)
#         for task in forin:
#             num = Serial.query.order_by(Serial.timestamp.desc()).first()
#             num = num.number if num is not None else None
#             name = choice(names)
#             t_id = task.id
#             f_id = choice(task.offices).id
#             # if i >= 11: WTF ?!
#             db.session.add(Serial(number=num + 1,
#                                     office_id=f_id,
#                                     task_id=t_id, name=name, n=True))
#     for a in range(Waiting.query.count(), 11):
#         for b in Serial.query.filter_by(p=False).order_by(Serial.timestamp):
#             if Waiting.query.filter_by(office_id=b.office_id,
#                                        number=b.number,
#                                        task_id=b.task_id).first() is None:
#                 db.session.add(Waiting(b.number, b.office_id,
#                                        b.task_id, b.name, b.n))
#     db.session.commit()