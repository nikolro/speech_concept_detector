from flask import Flask, request, jsonify
from markupsafe import Markup
from flask_cors import CORS
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_template():
    with open('speech_concept_detector/template.html', 'r') as file:
        return file.read()

def create_dictionary_with_gpt4(words_list):
    try:
        # Convert words_list to proper format if it's a string
        if isinstance(words_list, str):
            words_list = [word.strip() for word in words_list.split(',') if word.strip()]
        elif isinstance(words_list, (list, tuple, set)):
            words_list = [str(word).strip() for word in words_list if str(word).strip()]
        else:
            raise ValueError("words_list must be a string, list, tuple, or set")

        # Don't process if no valid words
        if not words_list:
            return {}

        # Create the system prompt
        system_prompt = f"""
        You are a dictionary expert. For each word in this list: {words_list},
        provide a clear, concise, and accurate definition.
        Rules:
        1. Focus on the most common meaning unless context suggests otherwise
        2. Keep definitions clear and understandable
        3. Format exactly as shown:
        DEFINITIONS:
        word1: definition1
        word2: definition2
        Only include words from the provided list. Do not add extra words.
        """
        # Make API call to GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ", ".join(words_list)}
            ],
            temperature=0.7  # Balanced between creativity and consistency
        )
        
        # Process the response
        content = response.choices[0].message.content
        
        # Parse the definitions into a dictionary
        definitions = {}
        if 'DEFINITIONS:' in content:
            lines = content.split('DEFINITIONS:')[1].strip().split('\n')
            for line in lines:
                if ':' in line:
                    word, definition = line.split(':', 1)
                    # Remove any part of speech indicators if they exist
                    cleaned_definition = definition.strip()
                    if cleaned_definition.startswith('('):
                        pos_end = cleaned_definition.find(')')
                        if pos_end != -1:
                            cleaned_definition = cleaned_definition[pos_end + 1:].strip()
                    definitions[word.strip()] = cleaned_definition

        return definitions

    except Exception as e:
        print(f"Error in create_dictionary_with_gpt4: {str(e)}")
        return None

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    template = get_template()
    return Markup(template)

@app.route('/get_definitions', methods=['POST'])
def get_definitions():
    try:
        data = request.get_json()
        keywords = data.get('keywords')
        if not keywords:
            return jsonify({'error': 'Missing keywords'}), 400
            
        definitions = create_dictionary_with_gpt4(keywords)
        
        if definitions is None:
            return jsonify({'error': 'Failed to generate definitions'}), 500
            
        return jsonify({'definitions': definitions})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True)