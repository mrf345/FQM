from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Length

from app.forms.base import LocalizedForm


class LoginForm(LocalizedForm):
    name = StringField('Enter user name : ',
                       validators=[InputRequired('Required not less than 5 nor more than 200 letters'),
                                   Length(5, 200)])
    password = PasswordField('Enter password : ',
                             validators=[InputRequired('Password must be at least of 5 and at most 15 letters'),
                                         Length(5, 15)])
    rm = BooleanField('Remember me : ')
    submit = SubmitField('Login')


class TouchSubmitForm(LocalizedForm):
    name = StringField('',
                       validators=[InputRequired('Required not less than 3 nor more than 300 letters'),
                                   Length(3, 500)])
    submit = SubmitField('Register')
