from wtforms import StringField, SubmitField, PasswordField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from app.forms.base import LocalizedForm
from app.forms.constents import BOOLEAN_SELECT, EXPORT_OPTIONS, EXPORT_TABLES
from app.database import Office
from app.constants import USER_ROLES


class UserForm(LocalizedForm):
    name = StringField('Enter a unique user name : ',
                       validators=[InputRequired('Required not less than 5 nor more than 200 letters'),
                                   Length(5, 200)])
    password = PasswordField('Enter password : ',
                             validators=[InputRequired('Password must be at least of 5 and at most 15 letters'),
                                         Length(5, 15)])
    role = SelectField('Select a role for the user : ',
                       coerce=int,
                       validators=[InputRequired('You must select a role to add user in')])
    offices = SelectField('Select office to assing the operator to : ',
                          coerce=int,
                          validators=[Optional()])
    submit = SubmitField('Add')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.offices.choices = [(o.id, f'{self.translate("Office : ")}{o.prefix}{o.name}')
                                for o in Office.query.all()]

        has_offices = bool(Office.get())
        for _id, role in USER_ROLES.items():
            if _id != 3 or has_offices:
                self.role.choices = (self.role.choices or []) + [(_id, role)]


class CSVForm(LocalizedForm):
    headers = SelectField('Show headers in the CSV file :',
                          coerce=int,
                          choices=BOOLEAN_SELECT)
    delimiter = SelectField('Character to separate the CSV fields with :',
                            coerce=int)
    table = SelectField('Select table to download its csv :',
                        coerce=str,
                        choices=EXPORT_TABLES)
    submit = SubmitField('Extract table')

    def __init__(self, *args, **kwargs):
        super(CSVForm, self).__init__(*args, **kwargs)
        self.delimiter.choices = list(EXPORT_OPTIONS.items())  # NOTE: here, so it won't get localized.


class AdminForm(LocalizedForm):
    password = PasswordField('Enter password : ',
                             validators=[InputRequired('Password must be at least of 5 and at most 15 letters'),
                                         Length(5, 15)])
    submit = SubmitField('Update Admin')


class AuthTokensForm(LocalizedForm):
    name = StringField('Enter token name : ',
                       validators=[InputRequired('Required not less than 1 nor more than 100 letters'),
                                   Length(1, 100)])
    description = TextAreaField('Enter token description : ', validators=[Optional()])
    token = StringField('Authentication Token : ', validators=[Optional()])
