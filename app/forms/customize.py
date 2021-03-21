import os
from functools import reduce
from wtforms.validators import InputRequired, Length, Optional
from flask_wtf.file import FileAllowed
from wtforms import StringField, SelectField, SubmitField, BooleanField, TextAreaField, FileField
from wtforms_components import TimeField

from app.forms.base import LocalizedForm
from app.forms.constents import (FONT_SIZES, BTN_COLORS, DURATIONS, TOUCH_TEMPLATES, DISPLAY_TEMPLATES,
                                 ANNOUNCEMENT_REPEATS, ANNOUNCEMENT_REPEAT_TYPE, VISUAL_EFFECTS,
                                 VISUAL_EFFECT_REPEATS, BOOLEAN_SELECT_1, TICKET_TYPES,
                                 TICKET_REGISTERED_TYPES, SLIDE_EFFECTS, SLIDE_DURATIONS, EVERY_OPTIONS)
from app.database import Media
from app.constants import SUPPORTED_MEDIA_FILES, SUPPORTED_LANGUAGES, PRINTED_TICKET_SCALES
from app.helpers import get_tts_safely


class TouchScreenForm(LocalizedForm):
    touch = SelectField('Select a template for Touch screen :',
                        coerce=int,
                        choices=TOUCH_TEMPLATES)
    title = StringField('Enter a title :',
                        validators=[InputRequired('Must enter at least 5 letters and Title '
                                                  'should be maximum of 300 letters'),
                                    Length(5, 300)])
    hsize = SelectField('Choose title font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    hcolor = StringField('Select title font color :')
    hfont = StringField('choose a font for title :')
    hbg = StringField('Select heading background color :')
    tsize = SelectField('choose task font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    tcolor = SelectField('choose tasks color :',
                         coerce=str,
                         choices=BTN_COLORS)
    tfont = StringField('choose tasks font :')
    msize = SelectField('choose message font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    mcolor = StringField('Select message font color :')
    mfont = StringField('Choose message font :')
    mduration = SelectField('choose motion effect duration of appearing :',
                            coerce=str,
                            choices=DURATIONS)
    mbg = StringField('Select message background color :')
    message = TextAreaField('Enter a notification message :',
                            validators=[InputRequired('Must enter at least 5 letter and Message'
                                                      'should be maximum of 300 letters ..'),
                                        Length(5, 300)])
    bcolor = StringField('Select a background color : ')
    background = SelectField('Select background : ',
                             coerce=int,
                             choices=[(0, 'Use color selection')])
    naudio = SelectField('Select audio notification : ',
                         coerce=int,
                         choices=[(0, 'Disable audio notification')])
    submit = SubmitField('Apply')

    def __init__(self, *args, **kwargs):
        super(TouchScreenForm, self).__init__(*args, **kwargs)
        for m in Media.get_all_images():
            self.background.choices += [(m.id, f'{m.id}. {m.name}')]

        for m in Media.get_all_audios():
            self.naudio.choices += [(m.id, f'{m.id}. {m.name}')]


class DisplayScreenForm(LocalizedForm):
    display = SelectField('Select a template for Display screen : ',
                          coerce=int,
                          choices=DISPLAY_TEMPLATES)
    title = StringField('Enter a title : ',
                        validators=[InputRequired('Title should be maximum of 300 letters'),
                                    Length(0, 300)])
    background = SelectField('Select a background : ',
                             coerce=int,
                             choices=[(0, 'Use color selection')])
    hsize = SelectField('Choose title font size : ',
                        coerce=str,
                        choices=FONT_SIZES)
    hcolor = StringField('Choose title font color : ')
    hfont = StringField('Choose title font : ')
    hbg = StringField('Choose title background color : ')
    tsize = SelectField('choose main heading office font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    tcolor = StringField('choose main heading office color : ')
    tfont = StringField('choose main heading office font : ')
    h2color = StringField('choose main heading ticket color : ')
    h2size = SelectField('choose main heading ticket font size :',
                         coerce=str,
                         choices=FONT_SIZES)
    h2font = StringField('choose main heading ticket font : ')
    ssize = SelectField('choose secondary heading font size : ',
                        coerce=str,
                        choices=FONT_SIZES)
    scolor = StringField('choose secondary heading color : ')
    sfont = StringField('choose secondary heading font :')
    mduration = SelectField('choose motion effect duration of appearing : ',
                            coerce=str,
                            choices=DURATIONS)
    rrate = SelectField('choose page refresh rate : ',
                        coerce=str,
                        choices=DURATIONS)
    effect = SelectField('choose visual motion effect for notification : ',
                         coerce=str,
                         choices=VISUAL_EFFECTS)
    repeats = SelectField('choose motion effect number of repeats : ',
                          coerce=str,
                          choices=VISUAL_EFFECT_REPEATS)
    anr = SelectField('Number of announcement repeating : ',
                      coerce=int,
                      choices=ANNOUNCEMENT_REPEATS)
    anrt = SelectField('Type of announcement and notification repeating :',
                       coerce=str,
                       choices=ANNOUNCEMENT_REPEAT_TYPE)
    naudio = SelectField('Select audio notification : ',
                         coerce=int,
                         choices=[(0, 'Disable audio notification')])
    bgcolor = StringField('Select a background color : ')
    prefix = BooleanField('Attach prefix office letter: ')
    always_show_ticket_number = BooleanField('Always show ticket number: ')
    wait_for_announcement = BooleanField('Wait for announcement to finish:')
    hide_ticket_index = BooleanField('Hide ticket index number:')
    submit = SubmitField('Apply')

    for shortcode in get_tts_safely().keys():
        locals()[f'check{shortcode}'] = BooleanField()

    def __init__(self, *args, **kwargs):
        super(DisplayScreenForm, self).__init__(*args, **kwargs)
        for m in Media.get_all_images():
            self.background.choices += [(m.id, f'{m.id}. {m.name}')]

        for m in Media.get_all_audios():
            self.naudio.choices += [(m.id, f'{m.id}. {m.name}')]

        for shortcode, bundle in get_tts_safely().items():
            self[f'check{shortcode}'].label = self.translate(bundle.get('language'))


class SlideAddForm(LocalizedForm):
    title = StringField('Enter a slide title :')
    hsize = SelectField('Select a title font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    hcolor = StringField('Select a title font color :')
    hfont = StringField('Select a title font :')
    hbg = StringField('Select title background color :')
    subti = StringField('Enter a subtitle :')
    tsize = SelectField('Select subtitle font size :',
                        coerce=str,
                        choices=FONT_SIZES)
    tcolor = StringField('Select sub title color :')
    tfont = StringField('Select subtitle font :')
    tbg = StringField('Select subtitle background color :')
    background = SelectField('Select background : ',
                             coerce=int,
                             choices=[(0, 'Use color selection')])
    bgcolor = StringField('Select background color : ')
    submit = SubmitField('Add a slide')

    def __init__(self, *args, **kwargs):
        super(SlideAddForm, self).__init__(*args, **kwargs)
        for m in Media.get_all_images():
            self.background.choices += [(m.id, f'{m.id}. {m.name}')]


class SlideSettingsForm(LocalizedForm):
    status = SelectField('Disable or enable slide-show :',
                         coerce=int,
                         choices=BOOLEAN_SELECT_1)
    effect = SelectField('Select transition effect :',
                         coerce=str,
                         choices=SLIDE_EFFECTS)
    navigation = SelectField('Slide navigation bars :',
                             coerce=int,
                             choices=BOOLEAN_SELECT_1)
    rotation = SelectField('Slide images rotation :',
                           coerce=str,
                           choices=SLIDE_DURATIONS)
    submit = SubmitField('Apply')


class MultimediaForm(LocalizedForm):
    mf = FileField('Select multimedia file :',
                   validators=[FileAllowed(
                       reduce(lambda sum, group: sum + group, SUPPORTED_MEDIA_FILES),
                       'make sure you followed the given conditions !')])
    submit = SubmitField('Upload')


class VideoForm(LocalizedForm):
    video = SelectField('Select uploaded video to use : ',
                        coerce=int,
                        choices=[(0, 'Do not assign video')])
    enable = SelectField('Enable or disable video : ',
                         coerce=int,
                         choices=BOOLEAN_SELECT_1)
    ar = SelectField('Auto replaying the video : ',
                     coerce=int,
                     choices=BOOLEAN_SELECT_1)
    controls = SelectField('Enable or disable video controls : ',
                           coerce=int,
                           choices=BOOLEAN_SELECT_1)
    mute = SelectField('Mute sound : ',
                       coerce=int,
                       choices=BOOLEAN_SELECT_1)
    submit = SubmitField('Set video')

    def __init__(self, defLang='en', *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        videos = Media.get_all_videos()

        for v in videos:
            self.video.choices.append((v.id, f'{v.id}. {v.name}'))

        if not videos:
            self.video.choices = [(0, self.translate('No videos were found'))]


class TicketForm(LocalizedForm):
    kind = SelectField('Select type of ticket to use : ',
                       coerce=int,
                       choices=TICKET_TYPES)
    value = SelectField('Select a value of registering : ',
                        coerce=int,
                        choices=TICKET_REGISTERED_TYPES)
    langu = SelectField('Select language of printed ticket : ',
                        choices=list(SUPPORTED_LANGUAGES.items()),
                        coerce=str)
    printers = SelectField('Select a usb printer : ',
                           coerce=str,
                           choices=[('00', 'No printers were found')])
    scale = SelectField('Select font scaling measurement for printed tickets :',
                        coerce=int)
    header = StringField('Enter a text header : ')
    sub = StringField('Enter a text sub-header : ')
    submit = SubmitField('Set ticket')

    def __init__(self, inspected_printers_from_view, lp_printing, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        # NOTE: here so it won't be localized.
        self.scale.choices = [(i, f'x{i}') for i in PRINTED_TICKET_SCALES]

        if inspected_printers_from_view:
            self.printers.choices = []

            for printer in inspected_printers_from_view:
                if os.name == 'nt' or lp_printing:
                    self.printers.choices.append((f'{printer}', f'Printer Name: {printer}'))
                else:
                    vendor, product = printer.get('vendor'), printer.get('product')
                    in_ep, out_ep = printer.get('in_ep'), printer.get('out_ep')
                    identifier = f'{vendor}_{product}'

                    if in_ep and out_ep:
                        identifier += f'_{in_ep}_{out_ep}'

                    self.printers.choices.append((identifier, f'Printer ID: {vendor}_{product}'))


class AliasForm(LocalizedForm):
    _message = 'Alias must be at least of 2 and at most 10 letters'
    office = StringField('Enter alias for office : ',
                         validators=[InputRequired(_message), Length(2, 10)])
    task = StringField('Enter alias for task : ',
                       validators=[InputRequired(_message), Length(2, 10)])
    ticket = StringField('Enter alias for ticket : ',
                         validators=[InputRequired(_message), Length(2, 10)])
    name = StringField('Enter alias for name : ',
                       validators=[InputRequired(_message), Length(2, 10)])
    number = StringField('Enter alias for number : ',
                         validators=[InputRequired(_message), Length(2, 10)])


class BackgroundTasksForms(LocalizedForm):
    _every_message = 'Time range to repeat the task within :'
    _time_message = 'Specific time to execute the task in :'
    cache_tts_enabled = BooleanField('Enable caching text-to-speech announcements :')
    cache_tts_every = SelectField(_every_message,
                                  coerce=str,
                                  choices=[(o, o) for o in EVERY_OPTIONS])
    delete_tickets_enabled = BooleanField('Enable deleting tickets :')
    delete_tickets_every = SelectField(_every_message,
                                       coerce=str,
                                       choices=[(o, o) for o in EVERY_OPTIONS])
    delete_tickets_time = TimeField(_time_message,
                                    validators=[Optional()])
