import pytest
from unittest.mock import patch, mock_open
from services.transcription import transcribe_audio

class TestTranscription:
    @patch('os.getenv')
    def test_transcribe_audio_no_api_key(self, mock_getenv):
        # Setup mock to return None for API key
        mock_getenv.return_value = None
        
        # Test that ValueError is raised when API key is missing
        with pytest.raises(ValueError, match="OpenAI API key is not set"):
            transcribe_audio("fake_path.wav")
