from flask import current_app, session
from flask_wtf import FlaskForm

from app.middleware import gtranslator as translator


class LocalizedForm(FlaskForm):
    def translate(self, text, _from='en'):
        '''Convinant helper to translate text.

        Parameters
        ----------
        text : str
            text to be translated.

        Returns
        -------
        str
            translated text.
        '''
        with current_app.app_context():
            language = session.get('lang', 'en')

        return translator.translate(text, _from, [language])

    def __init__(self, *args, **kwargs):
        super(LocalizedForm, self).__init__(*args, **kwargs)

        for prop, obj in vars(self).items():
            if not prop.startswith('check'):
                label = getattr(obj, 'label', '')
                choices = getattr(obj, 'choices', [])
                validators = getattr(obj, 'validators', [])

                if label:
                    getattr(self, prop).label = self.translate(label.text)

                if choices:
                    getattr(self, prop).choices = [(t[0], self.translate(t[1])) for t in choices]

                for v in validators:
                    message = getattr(v, 'message', None)

                    message and setattr(v,
                                        'message',
                                        self.translate(message))
