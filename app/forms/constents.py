FONT_SIZES = [('600%', 'Very large'), ('500%', 'large'), ('400%', 'Medium'),
              ('300%', 'Small medium'), ('200%', 'small'),
              ('150%', 'Very small')]

BTN_COLORS = [('btn-success', 'Green'), ('btn-info', 'Light blue'),
              ('btn-primary', 'Blue'), ('btn-danger', 'Red'),
              ('btn-link', 'White')]

DURATIONS = [('500', 'Half a second'), ('1000', 'One second'),
             ('2000', 'Two seconds'), ('3000', 'Three seconds'),
             ('4000', 'Four seconds'), ('5000', 'Five seconds'),
             ('8000', 'Eight seconds'), ('10000', 'Ten seconds')]

EXPORT_TABLES = [('User', 'Users'), ('Roles', 'Roles of usesrs'),
                 ('Office', 'Offices'), ('Task', 'Tasks'),
                 ('Serial', 'Tickets'), ('Waiting', 'Waiting tickets')]
EXPORT_DELIMETERS = [',', '\t', '\n', '*', '#']
EXPORT_OPTIONS = {0: 'Comma', 1: 'Tab', 2: 'New line', 3: 'Star', 4: 'Hashtag'}

TOUCH_TEMPLATES = [(0, 'First Template'), (1, 'Second Template'), (2, 'Third Template')]
DISPLAY_TEMPLATES = TOUCH_TEMPLATES + [(3, 'Fourth Template')]


BOOLEAN_SELECT = [(1, 'Activated'), (0, 'Deactivated')]
BOOLEAN_SELECT_1 = [(1, 'Activated'), (2, 'Deactivated')]

VISUAL_EFFECTS = [('fade', 'fade'), ('blind', 'blind'), ('bounce', 'bounce'),
                  ('clip', 'clip'), ('drop', 'drop'), ('explode', 'explode'),
                  ('fold', 'fold'), ('highlight', 'highlight'), ('puff', 'puff'),
                  ('pulsate', 'pulsate'), ('scale', 'scale'), ('shake', 'shake'),
                  ('size', 'size'), ('slide', 'slide')]
VISUAL_EFFECT_REPEATS = [(f'{i}', f'{i} {"time" if i == 1 else "times"}')
                         for i in range(1, 11)]

ANNOUNCEMENT_REPEATS = [(i, f'{i} {"time" if i == 1 else "times"}') for i in range(1, 6)]
ANNOUNCEMENT_REPEAT_TYPE = [
    ('each', 'Each: to repeat each announcement and notification'),
    ('whole', 'Whole: to repeat all the announcements and notification as whole')]

TICKET_TYPES = [(1, 'Registered'), (2, 'Printed')]
TICKET_REGISTERED_TYPES = [(1, 'Name'), (2, 'Number')]

SLIDE_EFFECTS = [('fade', 'Fade effect'), ('slide', 'Slide effect')]
SLIDE_DURATIONS = [('1000', 'Every second'), ('3000', 'Every three seconds'),
                   ('5000', 'Every five seconds'), ('8000', 'Every eight seconds'),
                   ('60000', 'Every minute'), ('false', 'Disable rotation')]

EVERY_TIME_OPTIONS = ['day', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'sunday']
EVERY_OPTIONS = ['second', 'minute', 'hour', 'week'] + EVERY_TIME_OPTIONS
