"""
Create test audio files with different durations to demonstrate the "You" transcription issue.
"""
import wave
import numpy as np
import os

# Create test files with different durations
durations = [0.2, 0.5, 1.0, 2.0]
sample_rate = 16000

# Create output directory
output_dir = "test_audio_files"
os.makedirs(output_dir, exist_ok=True)

for duration in durations:
    # Create a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16).tobytes()
    
    # Write WAV file
    filename = os.path.join(output_dir, f'test_audio_{duration:.1f}s.wav')
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)
    
    print(f'Created {filename}')

# Create a word-like audio file
def create_word_audio(filename, word="hello", duration=1.0):
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
    decay = np.maximum(0, 1 - (t - (duration - decay_time)) / decay_time) * (t > (duration - decay_time))
    sustain = np.ones_like(t) * (t >= attack_time) * (t <= (duration - decay_time))
    
    envelope = attack + sustain + decay - np.minimum(sustain, attack) - np.minimum(sustain, decay)
    
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
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)
    
    print(f"Created word audio file for '{word}': {filename}")

# Create word audio files
words = ["hello", "test", "you"]
for word in words:
    for duration in [0.2, 0.5, 1.0]:
        filename = os.path.join(output_dir, f'word_{word}_{duration:.1f}s.wav')
        create_word_audio(filename, word=word, duration=duration)

print("\nAll test audio files created in the 'test_audio_files' directory")
