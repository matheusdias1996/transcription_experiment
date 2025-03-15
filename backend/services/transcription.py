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

def translate_text(text, target_language):
    """
    Translate text to the target language using OpenAI's API.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (e.g., 'en', 'es', 'fr')
        
    Returns:
        str: Translated text
    """
    # Get API key from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Check if API key is set
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set in environment variables")
    
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        # Use GPT-4o for translation as requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a translator. Translate the following text to {target_language}. Only respond with the translated text, nothing else."},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Translation error: {str(e)}")
