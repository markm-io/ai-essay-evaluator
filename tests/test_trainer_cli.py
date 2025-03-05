from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_essay_evaluator.trainer.cli import trainer_app


@pytest.fixture
def runner():
    return CliRunner()


def test_trainer_app_commands():
    """Test that trainer app has all expected commands."""
    # Get the commands from the app
    commands = [cmd.name for cmd in trainer_app.registered_commands]

    # Check if all expected commands are in the list
    assert "generate" in commands
    assert "validate" in commands
    assert "merge" in commands
    assert "upload" in commands
    assert "fine-tune" in commands


def test_generate_command_output(runner):
    """Test that the generate command shows help correctly."""
    result = runner.invoke(trainer_app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "Generate JSONL file from input files" in result.stdout


@patch("ai_essay_evaluator.trainer.cli.generate_jsonl")
def test_generate_command(mock_generate_jsonl, runner):
    """Test the generate command functionality."""
    mock_generate_jsonl.return_value = "test_output.jsonl"

    result = runner.invoke(
        trainer_app,
        [
            "generate",
            "--story-folder",
            "test_folder",
            "--question",
            "question.txt",
            "--rubric",
            "rubric.txt",
            "--csv",
            "model_testing.csv",
            "--output",
            "test_output.jsonl",
            "--scoring-format",
            "extended",
        ],
    )

    assert result.exit_code == 0
    mock_generate_jsonl.assert_called_once_with(
        "test_folder", "question.txt", "rubric.txt", "model_testing.csv", "test_output.jsonl", "extended"
    )
    assert "✅ JSONL file generated: test_output.jsonl" in result.stdout


def test_generate_command_invalid_format(runner):
    """Test the generate command with invalid scoring format."""
    result = runner.invoke(
        trainer_app,
        [
            "generate",
            "--story-folder",
            "test_folder",
            "--question",
            "question.txt",
            "--rubric",
            "rubric.txt",
            "--csv",
            "model_testing.csv",
            "--output",
            "test_output.jsonl",
            "--scoring-format",
            "invalid_format",
        ],
    )

    assert result.exit_code != 0
    assert "Format must be 'extended', 'item-specific', or 'short'" in result.stdout


@patch("ai_essay_evaluator.trainer.cli.validate_jsonl")
def test_validate_command(mock_validate_jsonl, runner):
    """Test the validate command functionality."""
    mock_validate_jsonl.return_value = True

    result = runner.invoke(trainer_app, ["validate", "--file", "test.jsonl", "--scoring-format", "extended"])

    assert result.exit_code == 0
    mock_validate_jsonl.assert_called_once_with("test.jsonl", "extended")
    assert "✅ JSONL file is valid!" in result.stdout


@patch("ai_essay_evaluator.trainer.cli.merge_jsonl_files")
def test_merge_command(mock_merge_jsonl_files, runner):
    """Test the merge command functionality."""
    mock_merge_jsonl_files.return_value = "merged.jsonl"

    result = runner.invoke(trainer_app, ["merge", "--folder", "test_folder", "--output", "merged.jsonl"])

    assert result.exit_code == 0
    mock_merge_jsonl_files.assert_called_once_with("test_folder", "merged.jsonl")
    assert "✅ Merged JSONL file created: merged.jsonl" in result.stdout


@patch("ai_essay_evaluator.trainer.cli.upload_jsonl")
def test_upload_command(mock_upload_jsonl, runner):
    """Test the upload command functionality."""
    mock_upload_jsonl.return_value = "file-123456"

    result = runner.invoke(trainer_app, ["upload", "--file", "test.jsonl", "--api-key", "test_key"])

    assert result.exit_code == 0
    mock_upload_jsonl.assert_called_once_with("test.jsonl", "test_key")
    assert "✅ JSONL file uploaded! File ID: file-123456" in result.stdout


@patch("ai_essay_evaluator.trainer.cli.validate_jsonl")
@patch("ai_essay_evaluator.trainer.cli.upload_jsonl")
@patch("ai_essay_evaluator.trainer.cli.create_fine_tuning_job")
def test_fine_tune_with_file(mock_create_job, mock_upload, mock_validate, runner):
    """Test the fine_tune command with file input."""
    mock_validate.return_value = True
    mock_upload.return_value = "file-123456"

    result = runner.invoke(
        trainer_app, ["fine-tune", "--file", "test.jsonl", "--api-key", "test_key", "--scoring-format", "extended"]
    )

    assert result.exit_code == 0
    mock_validate.assert_called_once_with("test.jsonl", "extended")
    mock_upload.assert_called_once_with("test.jsonl", "test_key")
    mock_create_job.assert_called_once_with("file-123456", "test_key")


@patch("ai_essay_evaluator.trainer.cli.create_fine_tuning_job")
def test_fine_tune_with_file_id(mock_create_job, runner):
    """Test the fine_tune command with file_id input."""
    result = runner.invoke(trainer_app, ["fine-tune", "--file-id", "file-123456", "--api-key", "test_key"])

    assert result.exit_code == 0
    mock_create_job.assert_called_once_with("file-123456", "test_key")


def test_fine_tune_no_inputs(runner):
    """Test the fine_tune command with no inputs."""
    result = runner.invoke(trainer_app, ["fine-tune"])

    assert result.exit_code == 0
    # Remove the ❌ emoji if it's not actually in the output
    assert "You must provide either --file or --file-id" in result.stdout
