import requests
from flask_babel import _

from app import app


def translate(text_to_translate: str, source_language: str, destination_language: str) -> str:
    """Translates text from source language to destination language. Returns translated text"""

    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')

    request_url = f'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&' \
                  f'from={source_language}&to={destination_language}'
    headers = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'westus2',
    }
    response = requests.post(request_url, headers=headers, json=[{'Text': text_to_translate}])

    if not response.ok:
        return _('Error: the translation service failed.')

    return response.json()[0]['translations'][0]['text']
