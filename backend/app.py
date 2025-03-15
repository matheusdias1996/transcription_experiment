import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from services.question_answering import answer_question
from services.transcription import transcribe_audio

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    
    # Get language parameters from the request
    language = request.form.get("language")
    translate_to = request.form.get("translate_to")

    # Save the audio file temporarily
    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)

    # Transcribe the audio
    try:
        transcription = transcribe_audio(temp_path, language, translate_to)
        os.remove(temp_path)  # Clean up
        return jsonify({"transcription": transcription})
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
                transcription = error_str.split("HTTP code 200 from API (")[1].split(
                    ")"
                )[0]
                os.remove(temp_path)  # Clean up
                return jsonify({"transcription": transcription})
            except:
                pass

        os.remove(temp_path)  # Clean up
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route("/api/question", methods=["POST"])
def question():
    data = request.json
    if not data or "question" not in data or "transcription" not in data:
        return jsonify({"error": "Question and transcription are required"}), 400

    question_text = data["question"]
    transcription = data["transcription"]

    try:
        answer = answer_question(question_text, transcription)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
