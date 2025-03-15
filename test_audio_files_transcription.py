"""
Test script to transcribe the generated test audio files and demonstrate the "You" issue.
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.transcription import transcribe_audio

def test_audio_files():
    """Test transcription of the generated audio files."""
    print("=== Test Audio Files Transcription ===")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set! Transcription will fail.")
        return
    
    # Directory with test files
    test_dir = "test_audio_files"
    if not os.path.exists(test_dir):
        print(f"Error: Test directory '{test_dir}' not found.")
        return
    
    # Get all WAV files
    wav_files = [f for f in os.listdir(test_dir) if f.endswith(".wav")]
    if not wav_files:
        print(f"No WAV files found in '{test_dir}'.")
        return
    
    # Sort files by type and duration
    tone_files = sorted([f for f in wav_files if f.startswith("test_audio_")])
    word_files = sorted([f for f in wav_files if f.startswith("word_")])
    
    results = {}
    
    # Test tone files
    print("\n=== Testing Tone Files ===")
    for filename in tone_files:
        filepath = os.path.join(test_dir, filename)
        duration = filename.split("_")[-1].replace("s.wav", "")
        
        try:
            print(f"\nTesting {filename} (duration: {duration}s):")
            transcription = transcribe_audio(filepath)
            print(f"Transcription: '{transcription}'")
            
            # Check if transcription is "You"
            if transcription.lower() == "you":
                print("WARNING: Transcription is 'You' - this matches the issue reported!")
            
            results[filename] = transcription
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            results[filename] = f"ERROR: {str(e)}"
    
    # Test word files
    print("\n=== Testing Word Files ===")
    for filename in word_files:
        filepath = os.path.join(test_dir, filename)
        parts = filename.split("_")
        word = parts[1]
        duration = parts[2].replace("s.wav", "")
        
        try:
            print(f"\nTesting '{word}' audio (duration: {duration}s):")
            transcription = transcribe_audio(filepath)
            print(f"Transcription: '{transcription}'")
            
            # Check if transcription is "You"
            if transcription.lower() == "you":
                print("WARNING: Transcription is 'You' - this matches the issue reported!")
            
            results[filename] = transcription
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            results[filename] = f"ERROR: {str(e)}"
    
    # Save results to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_file}")
    
    # Print summary table
    print("\n=== Summary of Transcription Results ===")
    print("Filename | Duration | Transcription")
    print("---------|----------|-------------")
    
    for filename in sorted(results.keys()):
        if "test_audio_" in filename:
            duration = filename.split("_")[-1].replace("s.wav", "")
            print(f"{filename} | {duration}s | {results[filename]}")
    
    print("\n=== Word Audio Results ===")
    print("Word | Duration | Transcription")
    print("-----|----------|-------------")
    
    for filename in sorted([f for f in results.keys() if "word_" in f]):
        parts = filename.split("_")
        word = parts[1]
        duration = parts[2].replace("s.wav", "")
        print(f"{word} | {duration}s | {results[filename]}")
    
    # Analyze results
    short_chunks_with_you = [f for f, t in results.items() if t.lower() == "you" and ("0.2s" in f or "0.5s" in f)]
    longer_chunks_with_you = [f for f, t in results.items() if t.lower() == "you" and ("1.0s" in f or "2.0s" in f)]
    
    print("\n=== Analysis ===")
    print(f"Short chunks (0.2-0.5s) transcribed as 'You': {len(short_chunks_with_you)}/{len([f for f in results.keys() if '0.2s' in f or '0.5s' in f])}")
    print(f"Longer chunks (1.0-2.0s) transcribed as 'You': {len(longer_chunks_with_you)}/{len([f for f in results.keys() if '1.0s' in f or '2.0s' in f])}")
    
    # Conclusion
    print("\n=== Conclusion ===")
    if len(short_chunks_with_you) > len(longer_chunks_with_you):
        print("The test confirms that short audio chunks are more likely to be transcribed as 'You'.")
        print("Our solution of increasing the frontend timeslice and implementing backend buffering should resolve this issue.")
    else:
        print("The test results are inconclusive. Further investigation may be needed.")

if __name__ == "__main__":
    test_audio_files()
