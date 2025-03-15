from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.transcription import transcribe_audio, translate_text
from services.question_answering import answer_question

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    # Save the audio file temporarily
    temp_path = 'temp_audio.wav'
    audio_file.save(temp_path)
    
    # Transcribe the audio
    try:
        transcription = transcribe_audio(temp_path)
        os.remove(temp_path)  # Clean up
        return jsonify({'transcription': transcription})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Transcription error: {str(e)}")
        print(f"Error details: {error_details}")
        
        # Check if the error message contains a transcription
        error_str = str(e)
        if "HTTP code 200" in error_str and ")" in error_str:
            # Extract the transcription from the error message
            try:
                transcription = error_str.split("HTTP code 200 from API (")[1].split(")")[0]
                os.remove(temp_path)  # Clean up
                return jsonify({'transcription': transcription})
            except:
                pass
                
        os.remove(temp_path)  # Clean up
        return jsonify({'error': f"Transcription failed: {str(e)}"}), 500

@app.route('/api/question', methods=['POST'])
def question():
    data = request.json
    if not data or 'question' not in data or 'transcription' not in data:
        return jsonify({'error': 'Question and transcription are required'}), 400
    
    question_text = data['question']
    transcription = data['transcription']
    
    try:
        answer = answer_question(question_text, transcription)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    if not data or 'text' not in data or 'target_language' not in data:
        return jsonify({'error': 'Text and target language are required'}), 400
    
    text = data['text']
    target_language = data['target_language']
    
    try:
        translated_text = translate_text(text, target_language)
        return jsonify({'translation': translated_text})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Translation error: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({'error': f"Translation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True) 
