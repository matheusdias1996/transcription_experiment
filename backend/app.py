import base64
import io
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from services.question_answering import answer_question, answer_question_stream
from services.transcription import transcribe_audio, translate_text

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variable to store ongoing transcription
ongoing_transcription = ""


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Save the audio file temporarily
    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)

    # Transcribe the audio
    try:
        transcription = transcribe_audio(temp_path)
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


@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.json
    if not data or "text" not in data or "target_language" not in data:
        return jsonify({"error": "Text and target language are required"}), 400

    text = data["text"]
    target_language = data["target_language"]

    try:
        translated_text = translate_text(text, target_language)
        return jsonify({"translation": translated_text})
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"Translation error: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500


# WebSocket event handlers
@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("audio_chunk")
def handle_audio_chunk(data):
    global ongoing_transcription

    try:
        # Decode the base64 audio chunk
        audio_data = base64.b64decode(data["audio_chunk"])

        # Save to a temporary file
        temp_path = "temp_chunk.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_data)

        try:
            # Check if this is a dummy chunk (for testing environments without microphone)
            is_dummy = len(audio_data) < 100 and b"dummy" in audio_data
            
            if is_dummy:
                # For dummy data, simulate transcription with sample text
                import random
                sample_texts = [
                    "This is a simulated transcription.",
                    "Testing the real-time transcription feature.",
                    "The weather today is sunny and warm.",
                    "I'm recording this message for testing purposes.",
                    "The quick brown fox jumps over the lazy dog."
                ]
                chunk_transcription = random.choice(sample_texts)
            else:
                # Real transcription for actual audio
                chunk_transcription = transcribe_audio(temp_path)

            # Update the ongoing transcription
            if chunk_transcription:
                ongoing_transcription += " " + chunk_transcription
                ongoing_transcription = ongoing_transcription.strip()

            # Emit the updated transcription
            emit("transcription_update", {"transcription": ongoing_transcription})

            # Clean up
            os.remove(temp_path)
        except Exception as e:
            emit("error", {"message": str(e)})
    except Exception as e:
        emit("error", {"message": f"Error processing audio chunk: {str(e)}"})


@socketio.on("reset_transcription")
def handle_reset_transcription():
    global ongoing_transcription
    ongoing_transcription = ""
    emit("transcription_update", {"transcription": ongoing_transcription})


@socketio.on("ask_question")
def handle_question(data):
    global ongoing_transcription

    question = data["question"]

    if not ongoing_transcription:
        emit("answer_update", {"answer": "No transcription available yet."})
        return

    try:
        # For testing without API key, use simulated streaming response
        if not os.getenv("OPENAI_API_KEY"):
            # Simulate streaming response
            emit("answer_update", {"answer": "Based on the transcription, ", "final": False})
            socketio.sleep(1)
            emit("answer_update", {"answer": "Based on the transcription, the weather ", "final": False})
            socketio.sleep(1)
            emit("answer_update", {"answer": "Based on the transcription, the weather today is ", "final": False})
            socketio.sleep(1)
            emit("answer_update", {"answer": "Based on the transcription, the weather today is sunny and warm.", "final": False})
            socketio.sleep(1)
            emit("answer_update", {"answer": "", "final": True})
            return
            
        # Get streaming answer
        answer_stream = answer_question_stream(question, ongoing_transcription)

        # Send answer chunks as they become available
        for answer_chunk in answer_stream:
            emit("answer_update", {"answer": answer_chunk, "final": False})
            socketio.sleep(1)  # Small delay to simulate streaming

        # Signal end of answer
        emit("answer_update", {"answer": "", "final": True})
    except Exception as e:
        emit("error", {"message": str(e)})


if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=True, log_output=True)
