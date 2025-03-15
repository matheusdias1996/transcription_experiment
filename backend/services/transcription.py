import openai
import os

def transcribe_audio(audio_file_path):
    """
    Transcribe audio using OpenAI's Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    # Get API key from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Check if API key is set
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set in environment variables")
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            # For newer OpenAI client versions (0.27.0+)
            try:
                client = openai.OpenAI(api_key=openai.api_key)
                transcript = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1"
                )
                return transcript.text
            except Exception as e:
                # If there's an error with the newer client, try the older approach
                audio_file.seek(0)  # Reset file pointer to beginning
                response = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file
                )
                
                # Handle different response formats
                if isinstance(response, str):
                    return response
                elif hasattr(response, 'text'):
                    return response.text
                elif isinstance(response, dict) and 'text' in response:
                    return response['text']
                else:
                    return str(response)
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Transcription error: {str(e)}") 