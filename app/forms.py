from os import name
from functools import reduce
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, DateField
from wtforms import SubmitField, PasswordField, SelectField
from wtforms import TextAreaField, IntegerField, BooleanField
from flask_wtf.file import FileAllowed
from wtforms.validators import InputRequired, Length, NumberRange, Optional

import app.database as data
from app.middleware import gtranslator
from app.constants import SUPPORTED_MEDIA_FILES, SUPPORTED_LANGUAGES, PRINTED_TICKET_SCALES
from app.helpers import get_tts_safely


# -- List Tuples of colors, sizes, text background
font_sizes = [("600%", "Very large"), ("500%", "large"), ("400%", "Medium"),
              ("300%", "Small medium"), ("200%", "small"),
              ("150%", "Very small")]
btn_colors = [("btn-success", "Green"), ("btn-info", "Light blue"),
              ("btn-primary", "Blue"), ("btn-danger", "Red"),
              ("btn-link", "White")]
durations = [("500", "Half a second"), ("1000", "One second"),
             ("2000", "Two seconds"), ("3000", "Three seconds"),
             ("4000", "Four seconds"), ("5000", "Five seconds"),
             ("8000", "Eight seconds"), ("10000", "Ten seconds")]
export_tabels = [
    ("User", "Users"),
    ("Roles", "Roles of usesrs"),
    ("Office", "Offices"),
    ("Task", "Tasks"),
    ("Serial", "Tickets"),
    ("Waiting", "Waiting tickets")
]
export_delimiters = [',', '\t', '\n', '*', '#']
export_options = {
    0: 'Comma',
    1: 'Tab',
    2: 'New line',
    3: 'Star',
    4: 'Hashtag'
}
tms = [(0, "First Template"), (1, "Second Template"), (2, "Third Template")]
tts = get_tts_safely()

# -- Customizing and updating touch


class Touch_c(FlaskForm):
    touch = SelectField(coerce=int)
    title = StringField()
    hsize = SelectField(coerce=str)
    hcolor = StringField()
    hfont = StringField()
    hbg = StringField()
    tsize = SelectField(coerce=str)
    tcolor = SelectField(coerce=str)
    tfont = StringField()
    msize = SelectField()
    mcolor = StringField()
    mfont = StringField()
    mduration = SelectField(coerce=str)
    mbg = StringField()
    message = TextAreaField()
    background = SelectField(coerce=int)
    bcolor = StringField()
    naudio = SelectField(coerce=int)
    submit = SubmitField()

    def __init__(self, defLang=None, *args, **kwargs):
        super(Touch_c, self).__init__(*args, **kwargs)
        self.touch.label = gtranslator.translate("Select a template for Touch screen :", 'en', [defLang])
        self.touch.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in tms]
        self.title.label = gtranslator.translate("Enter a title :", 'en', [defLang])
        self.title.validators = [InputRequired(
            gtranslator.translate("Must enter at least 5 letters and Title " +
             "should be maximum of 300 letters", 'en', [defLang])), Length(5, 300)]
        self.hsize.label = gtranslator.translate("Choose title font size :", 'en', [defLang])
        self.hsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.hcolor.label = gtranslator.translate("Select title font color :", 'en', [defLang])
        self.hfont.label = gtranslator.translate("choose a font for title :", 'en', [defLang])
        self.hbg.label = gtranslator.translate("Select heading background color :", 'en', [defLang])
        self.tsize.label = gtranslator.translate("choose task font size :", 'en', [defLang])
        self.tsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.tcolor.label = gtranslator.translate("choose tasks color :", 'en', [defLang])
        self.tcolor.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in btn_colors]
        self.tfont.label = gtranslator.translate("choose tasks font :", 'en', [defLang])
        self.msize.label = gtranslator.translate("choose message font size :", 'en', [defLang])
        self.msize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.mcolor.label = gtranslator.translate("Select message font color :", 'en', [defLang])
        self.mfont.label = gtranslator.translate("Choose message font :", 'en', [defLang])
        self.mduration.label = gtranslator.translate("choose motion effect duration of appearing :", 'en', [defLang])
        self.mduration.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in durations]
        self.mbg.label = gtranslator.translate("Select message background color :", 'en', [defLang])
        self.message.label = gtranslator.translate('Enter a notification message :', 'en', [defLang])
        self.message.validators = [
            InputRequired
            (gtranslator.translate("Must enter at least 5" +
             " letter and Message should" +
             " be maximum of 300 letters ..", 'en', [defLang])),
            Length(5, 300)
        ]
        self.background.label = gtranslator.translate('Select background : ', 'en', [defLang])
        self.bcolor.label = gtranslator.translate('Select a background color : ', 'en', [defLang])
        self.naudio.label = gtranslator.translate('Select audio notification : ', 'en', [defLang])
        self.submit.label = gtranslator.translate('Apply', 'en', [defLang])
        bgs = []
        aud = []
        bgs.append((00, gtranslator.translate("Use color selection", 'en', [defLang])))
        aud.append((00, gtranslator.translate("Disable audio notification", 'en', [defLang])))
        if data.Media.query.count() >= 1:
            for v in data.Media.query.filter_by(img=True):
                bgs.append((v.id, str(v.id) + ".  " + v.name))
            for v in data.Media.query.filter_by(audio=True):
                aud.append((v.id, str(v.id) + ".  " + v.name))
        self.naudio.choices = aud
        self.background.choices = bgs


# -- Customizing and updating display


class Display_c(FlaskForm):
    display = SelectField(coerce=int)
    title = StringField()
    background = SelectField(coerce=int)
    hsize = SelectField(coerce=str)
    hcolor = StringField()
    hfont = StringField()
    hbg = StringField()
    tsize = SelectField(coerce=str)
    tcolor = StringField()
    tfont = StringField()
    h2color = StringField()
    h2size = SelectField(coerce=str)
    h2font = StringField()
    ssize = SelectField(coerce=str)
    scolor = StringField()
    sfont = StringField()
    mduration = SelectField(coerce=str)
    rrate = SelectField(coerce=str)
    effect = SelectField(coerce=str)
    repeats = SelectField(coerce=str)
    anr = SelectField(coerce=int)
    anrt = SelectField(coerce=str)
    naudio = SelectField(coerce=int)
    bgcolor = StringField()
    prefix = BooleanField()
    always_show_ticket_number = BooleanField()
    wait_for_announcement = BooleanField()
    submit = SubmitField()
    for shortcode in tts.keys():
        locals()[f'check{shortcode}'] = BooleanField()

    def __init__(self, defLang='en', *args, **kwargs):
        super(Display_c, self).__init__(*args, **kwargs)
        self.display.label = gtranslator.translate('Select a template for Display screen : ', 'en', [defLang])
        self.display.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in tms]
        self.title.label = gtranslator.translate('Enter a title : ', 'en', [defLang])
        self.title.validators = [
            InputRequired(gtranslator.translate("Title should be maximum of 300 letters", 'en', [defLang])),
            Length(0, 300)
        ]
        self.background.label = gtranslator.translate('Select a background : ', 'en', [defLang])
        self.hsize.label = gtranslator.translate('Choose title font size : ', 'en', [defLang])
        self.hsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.hcolor.label = gtranslator.translate('Choose title font color : ', 'en', [defLang])
        self.hfont.label = gtranslator.translate('Choose title font : ', 'en', [defLang])
        self.hbg.label = gtranslator.translate('Choose title background color : ', 'en', [defLang])
        self.tsize.label = gtranslator.translate("choose main heading office font size :", 'en', [defLang])
        self.tsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.tcolor.label = gtranslator.translate("choose main heading office color : ", 'en', [defLang])
        self.tfont.label = gtranslator.translate("choose main heading office font : ", 'en', [defLang])
        self.h2color.label = gtranslator.translate("choose main heading ticket color : ", 'en', [defLang])
        self.h2size.label = gtranslator.translate("choose main heading ticket font size : ", 'en', [defLang])
        self.h2size.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.h2font.label = gtranslator.translate("choose main heading ticket font : ", 'en', [defLang])
        self.ssize.label = gtranslator.translate("choose secondary heading font size : ", 'en', [defLang])
        self.ssize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.scolor.label = gtranslator.translate("choose secondary heading color : ", 'en', [defLang])
        self.sfont.label = gtranslator.translate("choose secondary heading font :", 'en', [defLang])
        self.mduration.label = gtranslator.translate("choose motion effect duration of appearing : ", 'en', [defLang])
        self.mduration.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in durations]
        self.rrate.label = gtranslator.translate("choose page refresh rate : ", 'en', [defLang])
        self.rrate.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in durations]
        self.effect.label = gtranslator.translate("choose visual motion effect for notification : ", 'en', [defLang])
        self.effect.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [
            ("fade", "fade"),
            ("blind", "blind"),
            ("bounce", "bounce"),
            ("clip", "clip"),
            ("drop", "drop"),
            ("explode", "explode"),
            ("fold", "fold"),
            ("highlight", "highlight"),
            ("puff", "puff"),
            ("pulsate", "pulsate"),
            ("scale", "scale"),
            ("shake", "shake"),
            ("size", "size"),
            ("slide", "slide")
        ]]
        self.repeats.label = gtranslator.translate("choose motion effect number of repeats : ", 'en', [defLang])
        self.repeats.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [
            ("1", "1 time"),
            ("2", "2 times"),
            ("3", "3 times"),
            ("4", "4 times"),
            ("5", "5 times"),
            ("7", "7 times"),
            ("8", "8 times"),
            ("9", "9 times"),
            ("10", "10 times")
        ]]
        self.anr.label = gtranslator.translate('Number of announcement repeating : ', 'en', [defLang])
        self.anr.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, 'One time'),
        (2, 'Two times'),
        (3, 'Three times'),
        (4, 'Four time'),
        (5, 'Five times')]]
        self.anrt.label = gtranslator.translate('Type of announcement and notification repeating :', 'en', [defLang])
        self.anrt.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [
            ('each', 'Each: to repeat each announcement and notification'),
            ('whole', 'Whole: to repeat all the announcements and notification as whole')
        ]]
        self.naudio.label = gtranslator.translate("Select audio notification : ", 'en', [defLang])
        self.bgcolor.label = gtranslator.translate("Select a background color : ", 'en', [defLang])
        self.prefix.label = gtranslator.translate("Attach prefix office letter: ", 'en', [defLang])
        self.always_show_ticket_number.label = gtranslator.translate("Always show ticket number: ", 'en', [defLang])
        self.wait_for_announcement.label = gtranslator.translate("Wait for announcement to finish:", 'en', [defLang])
        self.submit.label = gtranslator.translate('Apply', 'en', [defLang])
        bgs = []
        aud = []
        bgs.append((00, gtranslator.translate("Use color selection", 'en', [defLang])))
        aud.append((00, gtranslator.translate("Disable audio notification", 'en', [defLang])))
        if data.Media.query.count() >= 1:
            for v in data.Media.query.filter_by(img=True):
                bgs.append((v.id, str(v.id) + ".  " + v.name))
            for v in data.Media.query.filter_by(audio=True):
                aud.append((v.id, str(v.id) + ".  " + v.name))
        self.naudio.choices = aud
        self.background.choices = bgs
        for shortcode, bundle in tts.items():
            self[f'check{shortcode}'].label = gtranslator.translate(bundle.get('language'),
                                                                    'en',
                                                                    [defLang])


# -- Customizing and updating display

class Slide_a(FlaskForm):
    title = StringField()
    hsize = SelectField()
    hcolor = StringField()
    hfont = StringField()
    hbg = StringField()
    subti = StringField()
    tsize = SelectField(coerce=str)
    tcolor = StringField()
    tfont = StringField()
    tbg = StringField()
    background = SelectField(coerce=int)
    bgcolor = StringField()
    submit = SubmitField()

    def __init__(self, defLang='en', *args, **kwargs):
        super(Slide_a, self).__init__(*args, **kwargs)
        self.title.label = gtranslator.translate("Enter a slide title :", 'en', [defLang])
        self.hsize.label = gtranslator.translate("Select a title font size :", 'en', [defLang])
        self.hsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.hcolor.label = gtranslator.translate("Select a title font color :", 'en', [defLang])
        self.hfont.label = gtranslator.translate("Select a title font :", 'en', [defLang])
        self.hbg.label = gtranslator.translate("Select title background color :", 'en', [defLang])
        self.subti.label = gtranslator.translate("Enter a subtitle :", 'en', [defLang])
        self.tsize.label = gtranslator.translate("Select subtitle font size :", 'en', [defLang])
        self.tsize.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in font_sizes]
        self.tcolor.label = gtranslator.translate("Select sub title color :", 'en', [defLang])
        self.tfont.label = gtranslator.translate("Select subtitle font :", 'en', [defLang])
        self.tbg.label = gtranslator.translate("Select subtitle background color :", 'en', [defLang])
        self.background.label = gtranslator.translate("Select background : ", 'en', [defLang])
        self.bgcolor.label = gtranslator.translate("Select background color : ", 'en', [defLang])
        self.submit.label = gtranslator.translate('Add a slide', 'en', [defLang])
        bgs = []
        bgs.append((00, gtranslator.translate("Use color selection", 'en', [defLang])))
        if data.Media.query.count() >= 1:
            for v in data.Media.query.filter_by(img=True):
                bgs.append((v.id, str(v.id) + ".  " + v.name))
        self.background.choices = bgs


class Slide_c(FlaskForm):
    status = SelectField(coerce=int)
    effect = SelectField()
    navigation = SelectField(coerce=int)
    rotation = SelectField(coerce=str)
    submit = SubmitField()

    def __init__(self, defLang='en', *args, **kwargs):
        super(Slide_c, self).__init__(*args, **kwargs)
        self.status.label = gtranslator.translate("Disable or enable slide-show :", 'en', [defLang])
        self.status.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [
        (1, "Enable"), (2, "Disable")]]
        self.effect.label = gtranslator.translate("Select transition effect :", 'en', [defLang])
        self.effect.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [
        ("fade", "Fade effect"), ("slide", "Slide effect")]]
        self.navigation.label = gtranslator.translate("Slide navigation bars :", 'en', [defLang])
        self.navigation.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, "Enable"),
        (2, "Disable")]]
        self.rotation.label = gtranslator.translate("Slide images rotation :", 'en', [defLang])
        self.rotation.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [("1000", "Every second"),
        ("3000", "Every three seconds"),
        ("5000", "Every five seconds"),
        ("8000", "Every eight seconds"),
        ("60000", "Every minute"),
        ("false", "Disable rotation")]]
        self.submit.label = gtranslator.translate("Apply", 'en', [defLang])


# -- Adding Office


class Offices_a(FlaskForm):
    name = StringField()
    prefix = SelectField()
    submit = SubmitField("Add")

    def __init__(self, upd=None, uid=None, defLang='en', *args, **kwargs):
        super(Offices_a, self).__init__(*args, **kwargs)
        self.name.label = gtranslator.translate("Enter a unique office name : ", 'en', [defLang])
        self.name.validators = [
            InputRequired(gtranslator.translate(
                "Required not less than 3 nor more than 300 letters",
                'en',
                [defLang])), Length(3, 300)]
        self.prefix.label = gtranslator.translate("Select unique prefix for the office : ", 'en', [defLang])
        self.prefix.validators = [InputRequired(gtranslator.translate("You must choose unique prefix", 'en', [defLang]))]
        self.submit.label = gtranslator.translate("Add office", 'en', [defLang])
        prefixs = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'),
                   ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'),
                   ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'),
                   ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'),
                   ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'),
                   ('Y', 'Y'), ('Z', 'Z')]

        for v in data.Office.query.order_by(data.Office.timestamp):
            if (v.prefix, v.prefix) in prefixs:
                prefixs.remove((v.prefix, v.prefix))

        if upd and upd not in prefixs:
            prefixs.append((upd, upd))

        self.prefix.choices = prefixs


# -- Adding Task

class Task_a(FlaskForm):
    name = StringField()
    hidden = BooleanField()
    submit = SubmitField("Add")
    # Stupid workaround to avoid unbound field error
    for i in range(0, 1000):
        locals()['check%i' % i] = BooleanField()

    def __init__(self, defLang='en', common=False, *args, **kwargs):
        super(Task_a, self).__init__(*args, **kwargs)
        self.name.label = gtranslator.translate("Enter unique title for the task : ", 'en', [defLang])
        self.name.validators = [
            InputRequired(
                gtranslator.translate("Required not less than 5 nor more than 300 letters", 'en', [defLang])),
            Length(5, 300)]
        self.hidden.label = gtranslator.translate("Hide this task :", 'en', [defLang])
        if common:
            for office in data.Office.query.all():
                self['check%i' % office.id].label = '%s %s:' % (
                    gtranslator.translate("Office", 'en', [defLang]), office.name)


# -- Searching serials

class Search_s(FlaskForm):
    number = IntegerField(validators=[Optional()])
    tl = SelectField(coerce=int)
    date = DateField(validators=[Optional()])
    submit = SubmitField("Search")

    def __init__(self, defLang='en', *args, **kwargs):
        super(Search_s, self).__init__(*args, **kwargs)
        self.number.label = gtranslator.translate("Please enter a ticket number : ", 'en', [defLang])
        self.tl.label = gtranslator.translate("Select ticket prefix : ", 'en', [defLang])
        self.tl.validators = [InputRequired(gtranslator.translate(
            "You must select a prefix to search for", 'en', [defLang]))]
        self.date.label = gtranslator.translate("Select date to search for : ", 'en', [defLang])
        prf = []
        prf.append((0, gtranslator.translate("Without a prefix", 'en', [defLang])))
        for v in data.Office.query:
            p = data.Office.query.filter_by(id=v.id).first()
            if p is not None:
                prf.append((p.id, p.prefix +
                            str(p.name) + " , Prefix: " + p.prefix))
        self.tl.choices = prf


# -- Users Forms

class Login(FlaskForm):
    name = StringField()
    password = PasswordField()
    rm = BooleanField()
    submit = SubmitField("Login")

    def __init__(self, defLang='en', *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.name.label = gtranslator.translate('Enter user name : ', 'en', [defLang])
        self.name.validators = [InputRequired(
        gtranslator.translate("Required not less than 5 nor more than 200 letters", 'en', [defLang])),
        Length(5, 200)]
        self.password.label = gtranslator.translate("Enter password : ", 'en', [defLang])
        self.password.validators = [InputRequired(
            gtranslator.translate("Password must be at least of 5 and at most 15 letters", 'en', [defLang])),
        Length(5, 15)]
        self.rm.label = gtranslator.translate("Remember me : ", 'en', [defLang])


class User_a(FlaskForm):
    name = StringField()
    password = PasswordField()
    role = SelectField(coerce=int)
    offices = SelectField(coerce=int)
    submit = SubmitField("Add")

    def __init__(self, defLang='en', *args, **kwargs):
        super(User_a, self).__init__(*args, **kwargs)
        self.name.label = gtranslator.translate("Enter a unique user name : ", 'en', [defLang])
        self.name.validators = [InputRequired(gtranslator.translate(
            "Required not less than 5 nor more than 200 letters", 'en', [defLang])), Length(5, 200)]
        self.password.label = gtranslator.translate("Enter password : ", 'en', [defLang])
        self.password.validators = [InputRequired(gtranslator.translate(
            "Password must be at least of 5 and at most 15 letters", 'en', [defLang])), Length(5, 15)]
        self.role.label = gtranslator.translate("Select a role for the user : ", 'en', [defLang])
        self.role.validators = [InputRequired(gtranslator.translate("You must select a role to add user in", 'en', [defLang]))]
        self.offices.label = gtranslator.translate("Select office to assing the operator to : ", 'en', [defLang])
        self.offices.validators = [Optional()]
        self.role.choices = [(v.id, v.name) for v in data.Roles.query if v.id != 3]
        self.offices.choices = [(o.id, 'Office : ' + str(o.name) + o.prefix) for o in data.Office.query]

        # Hide operators role, if no offices created yet
        if data.Office.query.count() > 0:
            self.role.choices += [(3, data.Roles.query.filter_by(id=3).first().name)]


# Multimedia upload form

class Multimedia(FlaskForm):
    mf = FileField()
    submit = SubmitField("Upload")

    def __init__(self, defLang='en', *args, **kwargs):
        super(Multimedia, self).__init__(*args, **kwargs)
        self.mf.label = gtranslator.translate("Select multimedia file :", 'en', [defLang])
        self.mf.validators = [FileAllowed(
            reduce(lambda sum, group: sum + group, SUPPORTED_MEDIA_FILES),
            gtranslator.translate('make sure you followed the given conditions !', 'en', [defLang])
        )]


# Add name to ticket form

class Touch_name(FlaskForm):
    name = StringField()
    submit = SubmitField("Register")

    def __init__(self, defLang='en', *args, **kwargs):
        super(Touch_name, self).__init__(*args, **kwargs)
        self.name.validators = [InputRequired
        (gtranslator.translate("Required not less than 5 nor more than 300 letters", 'en', [defLang])),
        Length(3, 300)]


# Download CSV form ------

class CSV(FlaskForm):
    headers = SelectField(coerce=int)
    delimiter = SelectField(coerce=int)
    table = SelectField(coerce=str)
    submit = SubmitField('Extract table')

    def __init__(self, defLang='en', *args, **kwargs):
        super(CSV, self).__init__(*args, **kwargs)
        self.headers.label = gtranslator.translate('Show headers in the CSV file :', 'en', [defLang])
        self.headers.choices = [
            (t[0], gtranslator.translate(t[1], 'en', [defLang]))
            for t in [(1, 'Enable'), (0, 'Disable')]]
        self.delimiter.label = gtranslator.translate('Character to separate the CSV fields with :', 'en', [defLang])
        self.delimiter.choices = list(export_options.items())
        self.table.label = gtranslator.translate('Select table to download its csv :', 'en', [defLang])
        self.table.choices = [(e[0], gtranslator.translate(e[1], 'en', [defLang])) for e in export_tabels]

# Updating admin form

class U_admin(FlaskForm):
    password = PasswordField()
    submit = SubmitField('Update Admin')

    def __init__(self, defLang='en', *args, **kwargs):
        super(U_admin, self).__init__(*args, **kwargs)
        self.password.label = gtranslator.translate("Enter password : ", 'en', [defLang])
        self.password.validators = [InputRequired(
            gtranslator.translate("Password must be at least of 5 and at most 15 letters", 'en', [defLang])),
        Length(5, 15)]


# Video form

class Video(FlaskForm):
    video = SelectField(coerce=int)
    enable = SelectField(validators=[InputRequired()], coerce=int)
    ar = SelectField(validators=[InputRequired()], coerce=int)
    controls = SelectField(validators=[InputRequired()], coerce=int)
    mute = SelectField(validators=[InputRequired()], coerce=int)
    submit = SubmitField('Set video')

    def __init__(self, defLang='en', *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        self.video.label = gtranslator.translate("Select uploaded video to use : ", 'en', [defLang])
        self.video.validators = [
        InputRequired(
            gtranslator.translate("You must select a video to be used", 'en', [defLang]))]
        self.enable.label = gtranslator.translate("Enable or disable video : ", 'en', [defLang])
        self.enable.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, "Enable"),
        (2, "Disable")]]
        self.ar.label = gtranslator.translate("Auto replaying the video : ", 'en', [defLang])
        self.ar.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, "Enable"),
        (2, "Disable")]]
        self.controls.label = gtranslator.translate("Enable or disable video controls : ", 'en', [defLang])
        self.controls.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, "Enable"),
        (2, "Disable")]]
        self.mute.label = gtranslator.translate("Mute sound : ", 'en', [defLang])
        self.mute.choices = [(t[0], gtranslator.translate(t[1], 'en', [defLang])) for t in [(1, "Enable"),
        (2, "Disable")]]
        vds = []
        if data.Media.query.filter_by(vid=True).count() >= 1:
            vds.append((00, gtranslator.translate("Do not assign video", 'en', [defLang])))
            for v in data.Media.query.filter_by(vid=True):
                vds.append((v.id, str(v.id) + ".  " + v.name))
        else:
            vds.append((00, gtranslator.translate("No videos were found", 'en', [defLang])))
        self.video.choices = vds


# Printers form

class Printer_f(FlaskForm):
    kind = SelectField(coerce=int)
    value = SelectField(coerce=int)
    langu = SelectField(choices=list(SUPPORTED_LANGUAGES.items()), coerce=str)
    printers = SelectField(coerce=str)
    scale = SelectField(coerce=int)
    submit = SubmitField('Set ticket')

    def __init__(self, inspected_printers_from_view, lp_printing, defLang='en', *args, **kwargs):
        super(Printer_f, self).__init__(*args, **kwargs)
        self.kind.label = gtranslator.translate("Select type of ticket to use : ", 'en', [defLang])
        self.kind.choices = [
            (t[0], gtranslator.translate(t[1], 'en', [defLang]))
            for t in [(1, 'Registered'), (2, 'Printed')]]
        self.value.label = gtranslator.translate("Select a value of registering : ", 'en', [defLang])
        self.value.choices = [
            (t[0], gtranslator.translate(t[1], 'en', [defLang]))
            for t in [(1, 'Name'), (2, 'Number')]]
        self.langu.label = gtranslator.translate("Select language of printed ticket : ", 'en', [defLang])
        self.printers.label = gtranslator.translate('Select a usb printer : ', 'en', [defLang])
        self.scale.label = gtranslator.translate('Select font scaling measurement for printed tickets :',
                                                 'en', [defLang])
        self.scale.choices = [(i, f'x{i}') for i in PRINTED_TICKET_SCALES]
        printer_choices = []

        if inspected_printers_from_view:
            for printer in inspected_printers_from_view:
                if name == 'nt' or lp_printing:
                    printer_choices.append((f'{printer}', f'Printer Name: {printer}'))
                else:
                    vendor, product = printer.get('vendor'), printer.get('product')
                    in_ep, out_ep = printer.get('in_ep'), printer.get('out_ep')
                    identifier = f'{vendor}_{product}'

                    if in_ep and out_ep:
                        identifier += f'_{in_ep}_{out_ep}'

                    printer_choices.append((identifier, f'Printer ID: {vendor}_{product}'))
        else:
            printer_choices.append(('00', gtranslator.translate("No printers were found", 'en', [defLang])))

        self.printers.choices = printer_choices


# Aliases form

class Alias(FlaskForm):
    office = StringField()
    task = StringField()
    ticket = StringField()
    name = StringField()
    number = StringField()

    def __init__(self, defLang='en', *args, **kwargs):
        super(Alias, self).__init__(*args, **kwargs)
        self.office.validators = self.task.validators = self.ticket.validators = self.name.validators = self.number.validators = [
            InputRequired(
                gtranslator.translate("Alias must be at least of 2 and at most 10 letters", 'en', [defLang])
            ), Length(2, 10)
        ]
        self.office.label = gtranslator.translate('Enter alias for office : ', 'en', [defLang])
        self.task.label = gtranslator.translate('Enter alias for task : ', 'en', [defLang])
        self.ticket.label = gtranslator.translate('Enter alias for ticket : ', 'en', [defLang])
        self.name.label = gtranslator.translate('Enter alias for name : ', 'en', [defLang])
        self.number.label = gtranslator.translate('Enter alias for number : ', 'en', [defLang])
