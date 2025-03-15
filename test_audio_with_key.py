"""
Test script to verify audio transcription with a valid OpenAI API key.
This script simulates audio data and tests the transcription process.
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
    try:
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
    except ImportError:
        print("NumPy not available. Creating a simple WAV file instead.")

        # Create a simple WAV file without NumPy
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz

            # Create a simple tone (a series of alternating values)
            data = b""
            for i in range(int(16000 * duration)):
                # Simple alternating pattern to create a basic sound
                value = 32767 if i % 50 < 25 else -32767
                data += value.to_bytes(2, byteorder="little", signed=True)

            wav_file.writeframes(data)

        print(f"Created simple test WAV file: {filename}")
        return filename


def test_transcription_with_key(api_key=None):
    """Test transcription with a provided API key."""
    print("\n=== Testing Transcription With API Key ===")

    # Set API key if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        print(f"Set OPENAI_API_KEY to: {api_key[:4]}...{api_key[-4:]}")
    else:
        print("No API key provided, using existing environment variable if available")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return False

    # Create test audio files with different characteristics
    test_files = [
        create_test_wav_file("test_normal.wav", duration=2.0, frequency=440),
        create_test_wav_file("test_short.wav", duration=0.2, frequency=220),
        create_test_wav_file("test_speech.wav", duration=3.0, frequency=880),
    ]

    success = True

    # Test transcription for each file
    for test_file in test_files:
        print(f"\nTesting transcription for: {test_file}")
        try:
            transcription = transcribe_audio(test_file)
            print(f"Transcription result: '{transcription}'")

            # Check if transcription is "You"
            if transcription.lower() == "you":
                print(
                    "WARNING: Transcription is 'You' - this matches the issue reported!"
                )
                print(
                    "This suggests the audio may be too short or lacks speech content."
                )

        except Exception as e:
            print(f"Transcription error: {str(e)}")
            success = False

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Removed test file: {test_file}")

    return success


def simulate_audio_chunk_processing():
    """Simulate the audio chunk processing flow."""
    print("\n=== Simulating Audio Chunk Processing ===")

    # Create a test file
    test_file = create_test_wav_file("test_chunk.wav", duration=1.0)

    # Read the audio file
    with open(test_file, "rb") as f:
        audio_data = f.read()

    # Encode to base64 (simulating frontend)
    base64_data = base64.b64encode(audio_data).decode("utf-8")

    # Add data URL prefix (simulating frontend)
    audio_chunk = f"data:audio/wav;base64,{base64_data}"
    print("Added data URL prefix: data:audio/wav;base64,...")

    # Simulate backend processing
    print("\n--- Backend Processing ---")

    # Check for data URL prefix
    if "base64," in audio_chunk:
        print("Detected data URL prefix")
        # Extract base64 part
        audio_chunk = audio_chunk.split("base64,")[1]
        print("Extracted base64 data after prefix")

    # Decode base64 data
    try:
        decoded_data = base64.b64decode(audio_chunk)
        print(f"Successfully decoded base64 data: {len(decoded_data)} bytes")
    except Exception as e:
        print(f"Error decoding base64 data: {str(e)}")
        return

    # Save to temporary file with WAV headers
    temp_path = f"test_decoded_{datetime.now().strftime('%H%M%S')}.wav"
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

    # Attempt transcription
    print("\n--- Attempting Transcription ---")
    try:
        transcription = transcribe_audio(temp_path)
        print(f"Transcription result: '{transcription}'")
    except Exception as e:
        print(f"Transcription error: {str(e)}")

    # Clean up
    for file in [test_file, temp_path]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed temporary file: {file}")


def main():
    """Main function to run the test script."""
    print("=== Audio Transcription Test Tool ===")

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
        print("This is likely the cause of the 'You you you' transcription issue.")
        print("\nTo fix this issue, you need to:")
        print("1. Get a valid OpenAI API key from https://platform.openai.com/api-keys")
        print(
            "2. Create a .env file in the project root with: OPENAI_API_KEY=your_key_here"
        )
        print("3. Restart the application to load the new environment variable")

        # Ask for a test key
        print("\nWould you like to provide a test API key for this script? (y/n)")
        response = input("> ")
        if response.lower() == "y":
            print("Enter your OpenAI API key:")
            test_key = input("> ")
            if test_key:
                api_key = test_key

    # Test transcription with API key
    if api_key:
        test_transcription_with_key(api_key)
    else:
        print("\nSkipping transcription test due to missing API key")

    # Simulate audio chunk processing
    simulate_audio_chunk_processing()

    print("\n=== Test Complete ===")
    print("Based on the results, here are the likely issues:")
    print(
        "1. Missing OpenAI API key - This is the most likely cause of the 'You you you' issue"
    )
    print("2. Audio format issues - The WAV file format may not be optimal for Whisper")
    print(
        "3. Audio content - Very short or silent audio chunks may result in 'You' transcriptions"
    )
    print("\nRecommended fixes:")
    print("1. Add a valid OpenAI API key to a .env file in the project root")
    print("2. Ensure audio chunks are properly formatted with correct WAV headers")
    print("3. Consider increasing the minimum audio chunk duration")


if __name__ == "__main__":
    main()
