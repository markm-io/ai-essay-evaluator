from unittest.mock import MagicMock, mock_open, patch

import pytest

from ai_essay_evaluator.trainer.uploader import upload_jsonl


class TestUploadJsonl:
    """Test cases for uploading JSONL files to OpenAI."""

    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    @patch("builtins.open", new_callable=mock_open, read_data=b'{"test": "data"}')
    def test_upload_jsonl_with_api_key(self, mock_file, mock_openai_class):
        """Test uploading JSONL with API key provided."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "file-abc123"
        mock_client.files.create.return_value = mock_response

        result = upload_jsonl("test.jsonl", "test-api-key")

        assert result == "file-abc123"
        mock_openai_class.assert_called_once_with(api_key="test-api-key")
        mock_client.files.create.assert_called_once()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "env-api-key"})
    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    @patch("builtins.open", new_callable=mock_open, read_data=b'{"test": "data"}')
    def test_upload_jsonl_with_env_api_key(self, mock_file, mock_openai_class):
        """Test uploading JSONL with API key from environment."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "file-xyz789"
        mock_client.files.create.return_value = mock_response

        result = upload_jsonl("test.jsonl", None)

        assert result == "file-xyz789"
        mock_openai_class.assert_called_once_with(api_key="env-api-key")

    @patch.dict("os.environ", {}, clear=True)
    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    @patch("builtins.open", new_callable=mock_open, read_data=b'{"test": "data"}')
    def test_upload_jsonl_missing_api_key(self, mock_file, mock_openai):
        """Test uploading without API key exits."""
        with pytest.raises(SystemExit) as exc_info:
            upload_jsonl("test.jsonl", None)
        assert exc_info.value.code == 1

    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    @patch("builtins.open", new_callable=mock_open, read_data=b'{"test": "data"}')
    def test_upload_jsonl_openai_error(self, mock_file, mock_openai_class):
        """Test handling OpenAI API error."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.files.create.side_effect = Exception("API Error")

        with pytest.raises(SystemExit) as exc_info:
            upload_jsonl("test.jsonl", "test-api-key")
        assert exc_info.value.code == 1

    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    def test_upload_jsonl_file_not_found(self, mock_openai_class):
        """Test uploading non-existent file exits."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        with pytest.raises(SystemExit) as exc_info:
            upload_jsonl("/nonexistent/file.jsonl", "test-api-key")
        assert exc_info.value.code == 1

    @patch("ai_essay_evaluator.trainer.uploader.OpenAI")
    @patch("builtins.open", new_callable=mock_open, read_data=b'{"test": "data"}')
    def test_upload_jsonl_calls_with_correct_purpose(self, mock_file, mock_openai_class):
        """Test that upload calls OpenAI with correct purpose."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "file-123"
        mock_client.files.create.return_value = mock_response

        upload_jsonl("test.jsonl", "test-api-key")

        # Verify the call includes purpose="fine-tune"
        call_kwargs = mock_client.files.create.call_args.kwargs
        assert call_kwargs["purpose"] == "fine-tune"
