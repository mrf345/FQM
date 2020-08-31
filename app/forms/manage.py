from wtforms import StringField, SelectField, SubmitField, BooleanField, DateField, IntegerField
from wtforms.validators import InputRequired, Length, Optional

from app.forms.base import LocalizedForm
from app.database import Office
from app.constants import TICKET_STATUSES


class OfficeForm(LocalizedForm):
    name = StringField('Enter a unique office name : ',
                       validators=[InputRequired('Required not less than 3 nor more than 300 letters'),
                                   Length(3, 300)])
    prefix = SelectField('Select unique prefix for the office : ',
                         validators=[InputRequired('You must choose a unique prefix')])
    submit = SubmitField('Add office')

    def __init__(self, current_prefix=None, *args, **kwargs):
        super(OfficeForm, self).__init__(*args, **kwargs)
        prefixes = Office.get_all_available_prefixes()
        self.prefix.choices = [(p, p) for p in
                               prefixes + (
                               current_prefix and [current_prefix] or [])]


class TaskForm(LocalizedForm):
    name = StringField('Enter unique title for the task : ',
                       validators=[InputRequired('Required not less than 5 nor more than 300 letters'),
                                   Length(5, 300)])
    hidden = BooleanField('Hide this task :')
    submit = SubmitField('Add')

    # NOTE: stupid workaround to avoid unbound field error
    locals().update({f'check{i}': BooleanField() for i in range(0, 27)})

    def __init__(self, common=False, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        if common:
            translation = self.translate('Office')

            for office in Office.query.all():
                self[f'check{office.id}'].label = f'{translation}{office.name}'


class SearchForm(LocalizedForm):
    number = IntegerField('Please enter a ticket number : ', validators=[Optional()])
    tl = SelectField('Select ticket prefix : ',
                     coerce=int,
                     validators=[InputRequired('You must select a prefix to search for')])
    date = DateField('Select date to search for : ', validators=[Optional()])
    submit = SubmitField('Search')

    def __init__(self, defLang='en', *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        prefix_choices = [(0, self.translate('Without a prefix'))]

        for office in Office.query.all():
            prefix_choices.append((office.id, f'{office.prefix} {office.name}'))

        self.tl.choices = prefix_choices


class ProcessedTicketForm(LocalizedForm):
    printed = BooleanField('Printied ticket :',
                           validators=[InputRequired('')])
    value = StringField('Registered ticket value :')
    status = SelectField('Select ticket current status :',
                         coerce=str,
                         choices=[(s, s) for s in TICKET_STATUSES],
                         validators=[InputRequired('You must chose a ticket status')])
