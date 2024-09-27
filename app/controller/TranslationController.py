import requests
from flask import Blueprint, request, jsonify

translation_bp = Blueprint('translation', __name__)

@translation_bp.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data['text']
    target_language = data['targetLanguage']

    try:
        # Call the translation API
        translated_text = translate_text(text, target_language)
        return jsonify({'translatedText': translated_text})
    except requests.exceptions.HTTPError as err:
        return jsonify({'error': str(err)}), err.response.status_code

def translate_text(text, target_language):
    request_body = {
        "contents": [
            {
                "parts": [
                    {"text": f'Translate the following text to {target_language}: "{text}". Please return only the translated text.'}
                ]
            }
        ]
    }

    api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyAwrW8-YCiU8fUuZ9uck6D3xJabMogrueU'

    response = requests.post(api_url, json=request_body, headers={'Content-Type': 'application/json'})
    response.raise_for_status()

    data = response.json()
    translated_text = data['candidates'][0]['content']['parts'][0]['text']

    return translated_text