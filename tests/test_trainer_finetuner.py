from unittest.mock import MagicMock, patch

import pytest

from ai_essay_evaluator.trainer.finetuner import create_fine_tuning_job


class TestCreateFineTuningJob:
    """Test cases for creating fine-tuning jobs."""

    @patch("ai_essay_evaluator.trainer.finetuner.OpenAI")
    def test_create_fine_tuning_job_with_api_key(self, mock_openai_class):
        """Test creating fine-tuning job with API key provided."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "ftjob-abc123"
        mock_client.fine_tuning.jobs.create.return_value = mock_response

        result = create_fine_tuning_job("file-xyz789", "test-api-key")

        assert result == "ftjob-abc123"
        mock_openai_class.assert_called_once_with(api_key="test-api-key")
        mock_client.fine_tuning.jobs.create.assert_called_once_with(
            training_file="file-xyz789", model="gpt-4o-mini-2024-07-18"
        )

    @patch.dict("os.environ", {"OPENAI_API_KEY": "env-api-key"})
    @patch("ai_essay_evaluator.trainer.finetuner.OpenAI")
    def test_create_fine_tuning_job_with_env_api_key(self, mock_openai_class):
        """Test creating fine-tuning job with API key from environment."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "ftjob-xyz789"
        mock_client.fine_tuning.jobs.create.return_value = mock_response

        result = create_fine_tuning_job("file-abc123", None)

        assert result == "ftjob-xyz789"
        mock_openai_class.assert_called_once_with(api_key="env-api-key")

    @patch.dict("os.environ", {}, clear=True)
    def test_create_fine_tuning_job_missing_api_key(self):
        """Test creating job without API key exits."""
        with pytest.raises(SystemExit) as exc_info:
            create_fine_tuning_job("file-123", None)
        assert exc_info.value.code == 1

    @patch("ai_essay_evaluator.trainer.finetuner.OpenAI")
    def test_create_fine_tuning_job_openai_error(self, mock_openai_class):
        """Test handling OpenAI API error."""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.fine_tuning.jobs.create.side_effect = Exception("API Error")

        with pytest.raises(SystemExit) as exc_info:
            create_fine_tuning_job("file-123", "test-api-key")
        assert exc_info.value.code == 1

    @patch("ai_essay_evaluator.trainer.finetuner.OpenAI")
    def test_create_fine_tuning_job_custom_model(self, mock_openai_class):
        """Test creating fine-tuning job with custom model."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "ftjob-custom"
        mock_client.fine_tuning.jobs.create.return_value = mock_response

        result = create_fine_tuning_job("file-123", "test-api-key", model="gpt-4")

        assert result == "ftjob-custom"
        mock_client.fine_tuning.jobs.create.assert_called_once_with(training_file="file-123", model="gpt-4")

    @patch("ai_essay_evaluator.trainer.finetuner.OpenAI")
    def test_create_fine_tuning_job_default_model(self, mock_openai_class):
        """Test that default model is used when not specified."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.id = "ftjob-123"
        mock_client.fine_tuning.jobs.create.return_value = mock_response

        create_fine_tuning_job("file-123", "test-api-key")

        call_kwargs = mock_client.fine_tuning.jobs.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o-mini-2024-07-18"
