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
# Global variables for audio buffering
audio_buffer = b""
buffer_sample_rate = 16000  # 16kHz sample rate
# Minimum buffer size to avoid "You" transcriptions
# OpenAI Whisper API transcribes very short audio chunks (< 0.5s) as "You"
min_buffer_size = 8000  # 0.5 seconds of audio at 16kHz


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
    # Add global variables for audio buffering
    global audio_buffer
    global buffer_sample_rate
    global min_buffer_size

    try:
        # Get the base64 audio chunk
        audio_chunk_data = data["audio_chunk"]

        # Check if the data contains a data URL prefix (e.g., "data:audio/wav;base64,")
        if "base64," in audio_chunk_data:
            # Extract the base64 part after the prefix
            audio_chunk_data = audio_chunk_data.split("base64,")[1]

        # Decode the base64 audio chunk
        audio_data = base64.b64decode(audio_chunk_data)

        # Check if this is a dummy chunk (for testing environments without microphone)
        is_dummy = len(audio_data) < 100 and b"dummy" in audio_data

        # For real audio (not dummy), implement buffering
        if not is_dummy:
            global audio_buffer
            # Add current chunk to buffer
            audio_buffer += audio_data

            # If buffer is too small, store it and wait for more chunks
            if len(audio_buffer) < min_buffer_size:
                # Just update the UI with current transcription, don't process yet
                emit("transcription_update", {"transcription": ongoing_transcription})
                return

            # Use the buffered audio instead of just the current chunk
            audio_data = audio_buffer
            # Reset buffer after using it
            audio_buffer = b""

        # Save to a temporary file with proper WAV headers
        temp_path = "temp_chunk.wav"

        # Create a proper WAV file with appropriate headers
        import wave

        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz (Whisper's preferred sample rate)
            wav_file.writeframes(audio_data)

        try:
            if is_dummy:
                # For dummy data, simulate transcription with sample text
                import random

                sample_texts = [
                    "This is a simulated transcription.",
                    "Testing the real-time transcription feature.",
                    "The weather today is sunny and warm.",
                    "I'm recording this message for testing purposes.",
                    "The quick brown fox jumps over the lazy dog.",
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
            # Clean up in case of error
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # Provide clear error message for API key issues
            if "API key" in str(e) or "authentication" in str(e).lower():
                emit(
                    "error",
                    {
                        "message": "OpenAI API key is missing or invalid. Please check your configuration."
                    },
                )
            else:
                emit("error", {"message": str(e)})
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"Audio chunk processing error: {str(e)}")
        print(f"Error details: {error_details}")
        emit("error", {"message": f"Error processing audio chunk: {str(e)}"})


@socketio.on("reset_transcription")
def handle_reset_transcription():
    global ongoing_transcription
    global audio_buffer
    ongoing_transcription = ""
    audio_buffer = b""  # Reset audio buffer when transcription is reset
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
            emit(
                "answer_update",
                {"answer": "Based on the transcription, ", "final": False},
            )
            socketio.sleep(1)
            emit(
                "answer_update",
                {"answer": "Based on the transcription, the weather ", "final": False},
            )
            socketio.sleep(1)
            emit(
                "answer_update",
                {
                    "answer": "Based on the transcription, the weather today is ",
                    "final": False,
                },
            )
            socketio.sleep(1)
            emit(
                "answer_update",
                {
                    "answer": "Based on the transcription, the weather today is sunny and warm.",
                    "final": False,
                },
            )
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
