import pytest
from unittest.mock import patch
from services.question_answering import answer_question

class TestQuestionAnswering:
    @patch('os.getenv')
    def test_answer_question_no_api_key(self, mock_getenv):
        # Setup mock to return None for API key
        mock_getenv.return_value = None
        
        # Test that ValueError is raised when API key is missing
        with pytest.raises(ValueError, match="OpenAI API key is not set"):
            answer_question("test question", "test context")
