"""
Debug script to simulate audio recording and transcription.
This script helps diagnose issues with the audio recording and transcription process.
"""
import base64
import os
import sys
import wave
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.transcription import transcribe_audio


def create_test_wav_file(filename, duration=1.0, frequency=440):
    """Create a test WAV file with sine wave."""
    import numpy as np

    # Parameters
    sample_rate = 16000
    channels = 1
    sample_width = 2  # 16-bit

    # Create a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16).tobytes()

    # Write WAV file
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)

    print(f"Created test WAV file: {filename}")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Sample rate: {sample_rate} Hz")
    print(f"  - Channels: {channels}")
    print(f"  - Sample width: {sample_width} bytes")
    print(f"  - Frequency: {frequency} Hz")

    return filename


def simulate_audio_chunk_processing(audio_file, with_data_url=True):
    """Simulate the audio chunk processing flow."""
    print("\n=== Simulating Audio Chunk Processing ===")

    # Read the audio file
    with open(audio_file, "rb") as f:
        audio_data = f.read()

    # Encode to base64 (simulating frontend)
    base64_data = base64.b64encode(audio_data).decode("utf-8")

    # Add data URL prefix if requested (simulating frontend)
    if with_data_url:
        audio_chunk = f"data:audio/wav;base64,{base64_data}"
        print("Added data URL prefix: data:audio/wav;base64,...")
    else:
        audio_chunk = base64_data
        print("Using raw base64 data (no prefix)")

    # Print base64 data length
    print(f"Base64 data length: {len(base64_data)} characters")

    # Simulate backend processing
    print("\n--- Backend Processing ---")

    # Check for data URL prefix
    if "base64," in audio_chunk:
        print("Detected data URL prefix")
        # Extract base64 part
        audio_chunk = audio_chunk.split("base64,")[1]
        print("Extracted base64 data after prefix")
    else:
        print("No data URL prefix detected")

    # Decode base64 data
    try:
        decoded_data = base64.b64decode(audio_chunk)
        print(f"Successfully decoded base64 data: {len(decoded_data)} bytes")
    except Exception as e:
        print(f"Error decoding base64 data: {str(e)}")
        return

    # Save to temporary file with WAV headers
    temp_path = f"debug_output_{datetime.now().strftime('%H%M%S')}.wav"
    try:
        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(decoded_data)
        print(f"Saved decoded data to WAV file: {temp_path}")
    except Exception as e:
        print(f"Error creating WAV file: {str(e)}")
        return

    # Check if OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
        print("Transcription will fail without an API key.")
        return
    else:
        print(f"\nFound OpenAI API key: {api_key[:4]}...{api_key[-4:]}")

    # Attempt transcription
    print("\n--- Attempting Transcription ---")
    try:
        transcription = transcribe_audio(temp_path)
        print(f"Transcription result: '{transcription}'")
    except Exception as e:
        print(f"Transcription error: {str(e)}")

    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)
        print(f"Removed temporary file: {temp_path}")


def main():
    """Main function to run the debug script."""
    print("=== Audio Recording and Transcription Debug Tool ===")

    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
        print("Setting a temporary test key for debugging...")
        os.environ["OPENAI_API_KEY"] = "sk-test-key-for-debugging"

    # Create test audio files with different characteristics
    test_files = [
        create_test_wav_file("debug_normal.wav", duration=2.0, frequency=440),
        create_test_wav_file("debug_short.wav", duration=0.2, frequency=220),
        create_test_wav_file("debug_long.wav", duration=5.0, frequency=880),
    ]

    # Process each test file
    for test_file in test_files:
        # Test with data URL prefix
        simulate_audio_chunk_processing(test_file, with_data_url=True)

        # Test without data URL prefix
        simulate_audio_chunk_processing(test_file, with_data_url=False)

    print("\n=== Debug Complete ===")
    print("Check the output above for any errors or issues.")
    print("If you see 'You' in the transcription results for short audio,")
    print(
        "it may indicate that the audio is too short or lacks sufficient speech content."
    )


if __name__ == "__main__":
    main()
