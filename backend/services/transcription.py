import os

import openai


def transcribe_audio(audio_file_path, language=None, translate_to=None):
    """
    Transcribe audio using OpenAI's Whisper API.

    Args:
        audio_file_path (str): Path to the audio file
        language (str, optional): Language code of the audio (e.g., 'en', 'es', 'fr')
        translate_to (str, optional): Language code to translate the transcription to

    Returns:
        str: Transcribed text (and optionally translated)
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
                
                # Set up parameters for transcription
                params = {
                    "file": audio_file,
                    "model": "whisper-1",
                }
                
                # Add language parameter if specified
                if language:
                    params["language"] = language
                
                # Use translation endpoint if translate_to is specified
                if translate_to:
                    transcript = client.audio.translations.create(**params)
                else:
                    transcript = client.audio.transcriptions.create(**params)
                
                return transcript.text
            except Exception as e:
                # If there's an error with the newer client, try the older approach
                audio_file.seek(0)  # Reset file pointer to beginning
                
                # Set up parameters for older API
                params = {
                    "model": "whisper-1",
                    "file": audio_file,
                }
                
                # Add language parameter if specified
                if language:
                    params["language"] = language
                
                # Use translation endpoint if translate_to is specified
                if translate_to:
                    response = openai.Audio.translate(**params)
                else:
                    response = openai.Audio.transcribe(**params)

                # Handle different response formats
                if isinstance(response, str):
                    return response
                elif hasattr(response, "text"):
                    return response.text
                elif isinstance(response, dict) and "text" in response:
                    return response["text"]
                else:
                    return str(response)
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Transcription error: {str(e)}")
