"""
Test script to simulate real speech audio and verify transcription.
This script creates more realistic audio samples to test the transcription service.
"""
import base64
import os
import sys
import wave
from datetime import datetime

import numpy as np

# Add parent directory to path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.transcription import transcribe_audio


def create_speech_like_audio(filename, duration=2.0, sample_rate=16000):
    """Create a test WAV file with speech-like characteristics."""
    # Parameters
    channels = 1
    sample_width = 2  # 16-bit

    # Create a more complex waveform that mimics speech characteristics
    # This uses multiple frequencies and amplitudes to create a more speech-like sound
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Create a mixture of frequencies that might be more recognizable as speech
    frequencies = [200, 400, 600, 800, 1000]
    amplitudes = [0.5, 0.4, 0.3, 0.2, 0.1]

    # Add some amplitude modulation to simulate speech envelope
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)

    # Create the waveform
    waveform = np.zeros_like(t)
    for freq, amp in zip(frequencies, amplitudes):
        waveform += amp * np.sin(2 * np.pi * freq * t)

    # Apply the envelope
    waveform = waveform * envelope

    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.05, len(waveform))
    waveform = waveform + noise

    # Normalize to 16-bit range
    waveform = waveform / np.max(np.abs(waveform)) * 32767

    # Convert to int16
    data = waveform.astype(np.int16).tobytes()

    # Write WAV file
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)

    print(f"Created speech-like audio file: {filename}")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Sample rate: {sample_rate} Hz")
    print(f"  - Channels: {channels}")
    print(f"  - Sample width: {sample_width} bytes")

    return filename


def create_word_audio(filename, word="hello", duration=1.0, sample_rate=16000):
    """Create a test WAV file that might be recognized as a specific word."""
    # Parameters
    channels = 1
    sample_width = 2  # 16-bit

    # Create a waveform with characteristics that might be recognized as the word
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Different frequency patterns for different words
    if word.lower() == "hello":
        # Start with higher pitch, then lower
        freq_pattern = 800 - 400 * np.minimum(1, 2 * t / duration)
    elif word.lower() == "test":
        # Sharp attack, then steady
        freq_pattern = 600 * np.ones_like(t)
        # Add a sharper attack
        attack = np.exp(-5 * t)
        freq_pattern = freq_pattern + 200 * attack
    elif word.lower() == "you":
        # Rising then falling pitch (diphthong-like)
        freq_pattern = 300 + 200 * np.sin(np.pi * t / duration)
    else:
        # Generic pattern
        freq_pattern = 500 * np.ones_like(t)

    # Create amplitude envelope (typical speech envelope)
    # Attack, sustain, decay
    attack_time = 0.1
    decay_time = 0.3

    attack = np.minimum(t / attack_time, 1) * (t < attack_time)
    decay = np.maximum(0, 1 - (t - (duration - decay_time)) / decay_time) * (
        t > (duration - decay_time)
    )
    sustain = np.ones_like(t) * (t >= attack_time) * (t <= (duration - decay_time))

    envelope = (
        attack
        + sustain
        + decay
        - np.minimum(sustain, attack)
        - np.minimum(sustain, decay)
    )

    # Create the waveform
    waveform = np.sin(2 * np.pi * np.cumsum(freq_pattern) / sample_rate)

    # Apply the envelope
    waveform = waveform * envelope

    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.02, len(waveform))
    waveform = waveform + noise

    # Normalize to 16-bit range
    waveform = waveform / np.max(np.abs(waveform)) * 32767

    # Convert to int16
    data = waveform.astype(np.int16).tobytes()

    # Write WAV file
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)

    print(f"Created word audio file for '{word}': {filename}")
    print(f"  - Duration: {duration} seconds")
    print(f"  - Sample rate: {sample_rate} Hz")

    return filename


def test_speech_like_audio():
    """Test transcription with speech-like audio."""
    print("\n=== Testing Speech-Like Audio ===")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return

    # Create speech-like audio files with different durations
    durations = [0.5, 1.0, 2.0, 3.0]
    results = {}

    for duration in durations:
        test_file = f"test_speech_{duration:.1f}s.wav"
        create_speech_like_audio(test_file, duration=duration)

        try:
            print(f"\nTesting transcription for {duration:.1f}s speech-like audio:")
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
    print("\n=== Analysis of Speech-Like Audio Results ===")
    print("Duration | Transcription")
    print("---------|--------------")
    for duration in sorted(results.keys()):
        print(f"{duration:.1f}s    | {results[duration]}")


def test_specific_words():
    """Test transcription with audio designed to sound like specific words."""
    print("\n=== Testing Specific Word Audio ===")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return

    # Test different words
    words = ["hello", "test", "you", "world"]
    durations = [0.5, 1.0, 2.0]
    results = {}

    for word in words:
        for duration in durations:
            test_file = f"test_word_{word}_{duration:.1f}s.wav"
            create_word_audio(test_file, word=word, duration=duration)

            try:
                print(f"\nTesting transcription for '{word}' ({duration:.1f}s):")
                transcription = transcribe_audio(test_file)
                print(f"Transcription result: '{transcription}'")

                # Check if transcription matches the word
                if transcription.lower() == word.lower():
                    print(f"SUCCESS: Transcription matches the intended word '{word}'!")
                elif transcription.lower() == "you":
                    print(
                        "WARNING: Transcription is 'You' - this matches the issue reported!"
                    )

                results[(word, duration)] = transcription

            except Exception as e:
                print(f"Transcription error: {str(e)}")
                results[(word, duration)] = f"ERROR: {str(e)}"

            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

    # Analyze results
    print("\n=== Analysis of Word Audio Results ===")
    print("Word   | Duration | Transcription")
    print("-------|----------|-------------")
    for word, duration in sorted(results.keys()):
        print(f"{word:6} | {duration:.1f}s     | {results[(word, duration)]}")


def test_buffer_solution():
    """Test a solution that buffers multiple short chunks before transcription."""
    print("\n=== Testing Buffer Solution ===")

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return

    # Create multiple short chunks
    chunk_duration = (
        0.2  # Duration of each chunk in seconds (below the "You" threshold)
    )
    num_chunks = 5  # Number of chunks to combine

    # Create individual chunks
    chunk_files = []
    for i in range(num_chunks):
        chunk_file = f"test_buffer_chunk_{i}.wav"
        create_word_audio(chunk_file, word="hello", duration=chunk_duration)
        chunk_files.append(chunk_file)

    # Test individual chunks
    print("\nTesting individual short chunks:")
    for chunk_file in chunk_files:
        try:
            transcription = transcribe_audio(chunk_file)
            print(f"{chunk_file}: '{transcription}'")
        except Exception as e:
            print(f"{chunk_file}: ERROR - {str(e)}")

    # Combine chunks into a single file
    combined_file = "test_buffer_combined.wav"

    try:
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
                print("This confirms that buffering short chunks is a viable solution!")
        except Exception as e:
            print(f"Combined transcription error: {str(e)}")

    except Exception as e:
        print(f"Error combining chunks: {str(e)}")

    # Clean up
    for file in chunk_files + [combined_file]:
        if os.path.exists(file):
            os.remove(file)


def main():
    """Main function to run the test script."""
    print("=== Real Audio Simulation Test Tool ===")

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nWARNING: OPENAI_API_KEY environment variable is not set!")
        print("This is likely the cause of the 'You you you' transcription issue.")
        return

    # Test with speech-like audio
    test_speech_like_audio()

    # Test with specific word audio
    test_specific_words()

    # Test buffer solution
    test_buffer_solution()

    print("\n=== Test Complete ===")
    print("Based on the results, here are the recommended solutions:")
    print("1. Increase the audio chunk duration in the frontend (currently 1 second)")
    print(
        "2. Implement a buffer in the backend to accumulate short chunks before transcription"
    )
    print("3. Add a minimum audio length check to filter out very short chunks")
    print("\nRecommended implementation:")
    print(
        "1. Modify frontend/scripts/recorder.js to increase timeslice from 1000ms to 2000ms"
    )
    print(
        "2. Modify backend/app.py to buffer audio chunks until they reach a minimum length of 0.5s"
    )


if __name__ == "__main__":
    main()
