from random import choice
from app.middleware import db
from app.database import Task, Office, Serial, Waiting, User
from random import choice, randint
from app.__init__ import create_app

# To use any of the following functions, example :
# with create_app().app_context():
#      fill_tickets()
# Random names to use in filling
names = ('Aaron Enlightened', 'Abbott Father', 'Abel Breath', 'Abner Father',
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


def fill_tickets(entery_number=10, s_task=None):
    for i in range(entery_number):
        forin = Task.query if s_task is None else Task.query.filter_by(
            id=s_task)
        for task in forin:
            num = Serial.query.order_by(Serial.timestamp.desc()).first()
            num = num.number if num is not None else None
            name = choice(names)
            t_id = task.id
            f_id = choice(task.offices).id
            # if i >= 11: WTF ?!
            db.session.add(Serial(number=num + 1,
                                    office_id=f_id,
                                    task_id=t_id, name=name, n=True))
    for a in range(Waiting.query.count(), 11):
        for b in Serial.query.filter_by(p=False).order_by(Serial.timestamp):
            if Waiting.query.filter_by(office_id=b.office_id,
                                       number=b.number,
                                       task_id=b.task_id).first() is None:
                db.session.add(Waiting(b.number, b.office_id,
                                       b.task_id, b.name, b.n))
    db.session.commit()


def fill_users(entery_number=10, role=choice(range(1, 4))):
    for _ in range(entery_number):
        def recur():
            snm = "TEST" + str(randint(10000, 99999999))
            go = True if User.query.filter_by(name=snm
                                              ).first() is None else False
            if not go:
                return recur()
            db.session.add(User(snm, snm, role))
        recur()
    db.session.commit()


def delete_users(entery_number=1, allr=True, logit=False):
    forin = User.query if allr else range(entery_number)
    counter = 0
    for user in forin:
        if user.name.startswith('TEST'):
            db.session.delete(user)
            counter += 1
    db.session.commit()
    if logit:
        print(str(counter) + " : Users been deleted.")
