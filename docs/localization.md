## How do i add support for my language ?

#### User interface localization:
The localization texts are generated and cached within a large `.json` object, that can be modified manually
to add support to additional languages. Let's take an example of adding support to German language:

1. You'll have to get the short-code for your language, in this case it will be `de` for german. if you're not sure checkout this [list of codes](https://www.loc.gov/standards/iso639-2/php/code_list.php).
2. You'll add the short-code as a key and the translation as a value to every object in `gt_cached.json` [here](https://github.com/mrf345/FQM/blob/master/gt_cached.json). Let's take one translation object as an example:

> Before adding German translation
```json
"Administrators": {
    "ar": "\u0627\u0644\u0645\u0633\u0624\u0648\u0644\u064a\u0646",
    "en": "Administrators",
    "es": "Administradores",
    "fr": "Administrateurs",
    "it": "Amministratori"
},
```

> After adding German translation
```json
"Administrators": {
    "ar": "\u0627\u0644\u0645\u0633\u0624\u0648\u0644\u064a\u0646",
    "en": "Administrators",
    "es": "Administradores",
    "fr": "Administrateurs",
    "it": "Amministratori",
    "de": "Administratoren"
},
```

3. The final step is to add it to the list of supported languages in `app/constants.py` [here](https://github.com/mrf345/FQM/blob/master/app/constants.py#L4-L11):

> Before adding German language
```python
SUPPORTED_LANGUAGES = {
    # NOTE: The officially supported languages.
    'en': 'English',
    'ar': 'Arabic',
    'fr': 'French',
    'it': 'Italian',
    'es': 'Spanish'
}
```

> After adding German language
```python
SUPPORTED_LANGUAGES = {
    # NOTE: The officially supported languages.
    'en': 'English',
    'ar': 'Arabic',
    'fr': 'French',
    'it': 'Italian',
    'es': 'Spanish',
    'de': 'German',
}
```


#### Text-to-speech localization:
The text-to-speech supported languages and announcement messages are stored in `statics/tts.json` [here](https://github.com/mrf345/FQM/blob/master/static/tts.json).
Let's take adding support to German text-to-speech announcements as an example:

1. You'll have to get the short-code for your language, in this case it will be `de` for german. if you're not sure checkout this [list of codes](https://www.loc.gov/standards/iso639-2/php/code_list.php).
2. You'll add the short-code as a key in this case `de` and an object containing the language name and announcement message as a value. Example:

> Before adding german language announcement
```json
{
    "en-us": {
        "language": "English",
        "message": " , please proceed to the {} number : "
    },
    "ar": {
        "language": "Arabic",
        "message": " : توجه إلى المكتب رقم "
    },
    "fr": {
        "language": "French",
        "message": ", s'il vous plaît procéder au numéro de bureau : "
    },
    "es": {
        "language": "Spanish",
        "message": " , por favor diríjase al número de la oficina : "
    },
    "it": {
        "language": "Italian",
        "message": " , si prega di procedere al numero dell'ufficio : "
    }
}
```

> After adding german language announcement
```json
{
    "en-us": {
        "language": "English",
        "message": " , please proceed to the {} number : "
    },
    "ar": {
        "language": "Arabic",
        "message": " : توجه إلى المكتب رقم "
    },
    "fr": {
        "language": "French",
        "message": ", s'il vous plaît procéder au numéro de bureau : "
    },
    "es": {
        "language": "Spanish",
        "message": " , por favor diríjase al número de la oficina : "
    },
    "it": {
        "language": "Italian",
        "message": " , si prega di procedere al numero dell'ufficio : "
    },
    "de": {
        "language": "German",
        "message": "Bitte fahren Sie mit der Büronummer fort"
    },
}
```


#### TODO: Printer localization
