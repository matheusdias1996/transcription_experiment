"""
Test script to analyze audio chunk sizes and their impact on transcription.
This script helps diagnose why short audio chunks result in "You" transcriptions.
"""
import base64
import os
import sys
import wave
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.transcription import transcribe_audio


def create_test_wav_file(filename, duration=1.0, frequency=440, sample_rate=16000):
    """Create a test WAV file with sine wave."""
    try:
        import numpy as np

        # Parameters
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
            wav_file.setframerate(sample_rate)  # 16kHz

            # Create a simple tone (a series of alternating values)
            data = b""
            for i in range(int(sample_rate * duration)):
                # Simple alternating pattern to create a basic sound
                value = 32767 if i % 50 < 25 else -32767
                data += value.to_bytes(2, byteorder="little", signed=True)

            wav_file.writeframes(data)

        print(f"Created simple test WAV file: {filename}")
        return filename


def test_chunk_sizes():
    """Test different audio chunk sizes and their transcription results."""
    print("\n=== Testing Different Audio Chunk Sizes ===")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return

    # Test different durations
    durations = [0.1, 0.2, 0.5, 1.0, 2.0, 3.0]
    results = {}

    for duration in durations:
        test_file = f"test_chunk_{duration:.1f}s.wav"
        create_test_wav_file(test_file, duration=duration)

        try:
            print(f"\nTesting transcription for {duration:.1f}s audio chunk:")
            transcription = transcribe_audio(test_file)
            print(f"Transcription result: '{transcription}'")

            # Check if transcription is "You"
            if transcription.lower() == "you":
                print(
                    "WARNING: Transcription is 'You' - this matches the issue reported!"
                )

            results[duration] = transcription

        except Exception as e:
            print(f"Transcription error: {str(e)}")
            results[duration] = f"ERROR: {str(e)}"

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

    # Analyze results
    print("\n=== Analysis of Chunk Size Impact ===")
    print("Duration | Transcription")
    print("---------|--------------")
    for duration in sorted(results.keys()):
        print(f"{duration:.1f}s    | {results[duration]}")

    # Find threshold where "You" stops appearing
    you_threshold = None
    for duration in sorted(results.keys()):
        if results[duration].lower() != "you":
            you_threshold = duration
            break

    if you_threshold:
        print(f"\nThreshold where 'You' stops appearing: {you_threshold:.1f} seconds")
        print(f"Recommended minimum chunk size: {you_threshold:.1f} seconds")
    else:
        print("\nCould not determine a threshold where 'You' stops appearing")


def test_combined_chunks():
    """Test if combining multiple short chunks improves transcription."""
    print("\n=== Testing Combined Audio Chunks ===")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return

    # Create multiple short chunks
    chunk_duration = 0.5  # Duration of each chunk in seconds
    num_chunks = 4  # Number of chunks to combine

    # Create individual chunks
    chunk_files = []
    for i in range(num_chunks):
        chunk_file = f"test_chunk_{i}.wav"
        create_test_wav_file(
            chunk_file, duration=chunk_duration, frequency=440 + i * 100
        )
        chunk_files.append(chunk_file)

    # Test individual chunks
    print("\nTesting individual chunks:")
    for chunk_file in chunk_files:
        try:
            transcription = transcribe_audio(chunk_file)
            print(f"{chunk_file}: '{transcription}'")
        except Exception as e:
            print(f"{chunk_file}: ERROR - {str(e)}")

    # Combine chunks into a single file
    combined_file = "test_combined_chunks.wav"

    try:
        import numpy as np

        # Read all chunks
        combined_data = np.array([], dtype=np.int16)
        sample_rate = 16000

        for chunk_file in chunk_files:
            with wave.open(chunk_file, "rb") as wav_file:
                # Verify sample rate
                if wav_file.getframerate() != sample_rate:
                    print(f"Warning: {chunk_file} has different sample rate")

                # Read frames
                frames = wav_file.readframes(wav_file.getnframes())
                chunk_data = np.frombuffer(frames, dtype=np.int16)
                combined_data = np.append(combined_data, chunk_data)

        # Write combined file
        with wave.open(combined_file, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(combined_data.tobytes())

        print(f"\nCreated combined file: {combined_file}")
        print(f"  - Total duration: {num_chunks * chunk_duration:.1f} seconds")

        # Test combined file
        try:
            print("\nTesting combined chunks:")
            transcription = transcribe_audio(combined_file)
            print(f"Combined transcription: '{transcription}'")

            # Check if transcription is "You"
            if transcription.lower() == "you":
                print("WARNING: Combined transcription is still 'You'!")
            else:
                print("SUCCESS: Combined transcription is different from 'You'")
        except Exception as e:
            print(f"Combined transcription error: {str(e)}")

    except ImportError:
        print("NumPy not available. Skipping combined chunk test.")

    # Clean up
    for file in chunk_files + [combined_file]:
        if os.path.exists(file):
            os.remove(file)


def main():
    """Main function to run the test script."""
    print("=== Audio Chunk Size Analysis Tool ===")

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
        print("This is likely the cause of the 'You you you' transcription issue.")
        return

    # Test different chunk sizes
    test_chunk_sizes()

    # Test combined chunks
    test_combined_chunks()

    print("\n=== Test Complete ===")
    print("Based on the results, here are the likely solutions:")
    print("1. Increase the audio chunk duration in the frontend (currently 1 second)")
    print("2. Combine multiple audio chunks before sending to the API")
    print("3. Add a minimum audio length check to filter out very short chunks")
    print("\nRecommended implementation:")
    print(
        "1. Modify frontend/scripts/recorder.js to increase timeslice from 1000ms to 2000ms or more"
    )
    print(
        "2. Modify backend/app.py to buffer audio chunks until they reach a minimum length"
    )


if __name__ == "__main__":
    main()
