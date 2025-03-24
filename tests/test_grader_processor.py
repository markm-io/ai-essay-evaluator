import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.processor import process_csv


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {"student_id": ["001", "002", "003"], "essay_response": ["Sample essay 1", "Sample essay 2", "Sample essay 3"]}
    )


@pytest.fixture
def temp_files(tmp_path):
    """Setup temporary files for testing."""
    # Create input CSV file
    input_file = tmp_path / "test_input.csv"
    pd.DataFrame(
        {"student_id": ["001", "002", "003"], "essay_response": ["Sample essay 1", "Sample essay 2", "Sample essay 3"]}
    ).to_csv(input_file, index=False)

    # Create sample story and rubric files
    story_folder = tmp_path / "stories"
    story_folder.mkdir()
    (story_folder / "story1.txt").write_text("This is a test story")

    rubric_folder = tmp_path / "rubrics"
    rubric_folder.mkdir()
    (rubric_folder / "rubric1.txt").write_text("Test rubric content")

    question_file = tmp_path / "question.txt"
    question_file.write_text("Test question?")

    export_folder = tmp_path / "exports"

    return {
        "input_file": input_file,
        "export_folder": export_folder,
        "story_folder": story_folder,
        "rubric_folder": rubric_folder,
        "question_file": question_file,
    }


@pytest.mark.asyncio
async def test_process_csv_with_logging(temp_files):
    """Test processing CSV with logging enabled."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.logging.basicConfig") as mock_log_config,
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze_cost,
        patch("ai_essay_evaluator.evaluator.processor.logging.getLogger") as mock_get_logger,
        patch("typer.echo"),
    ):
        # Setup mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Create real dict for cost data instead of MagicMock
        mock_analyze_cost.return_value = {
            "total_cached_tokens": 1000,
            "total_uncached_tokens": 500,
            "total_cost": 0.05,
            "duration_seconds": 10.5,
        }

        processed_df = pd.DataFrame(
            {
                "student_id": ["001", "002", "003"],
                "essay_response": ["Sample essay 1", "Sample essay 2", "Sample essay 3"],
                "score": [85, 90, 75],
            }
        )

        # Use real list of response objects that won't cause format issues
        class MockResponse:
            def __str__(self):
                return "Response"

            def __format__(self, format_spec):
                return str(self)

        mock_process.return_value = (processed_df, [MockResponse()])

        # Call function with logging enabled
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=Path(temp_files["export_folder"]),
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=True,
            cost_analysis=True,
            passes=1,
            merge_results=False,
            story_folder=Path(temp_files["story_folder"]),
            rubric_folder=Path(temp_files["rubric_folder"]),
            question_file=Path(temp_files["question_file"]),
            start_time=time.time(),
            show_progress=False,
            calculate_totals=True,
        )

        # Verify logging was configured
        mock_log_config.assert_called_once()
        assert mock_get_logger.call_count >= 1


@pytest.mark.asyncio
async def test_process_csv_with_progress_bar(temp_files):
    """Test processing CSV with progress bar enabled."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv") as mock_validate,
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost"),
        patch("typer.progressbar") as mock_progress_bar,
    ):
        # Create a sample DataFrame that will be passed to process_with_openai
        input_df = pd.DataFrame(
            {"student_id": ["001", "002", "003"], "essay_response": ["Essay 1", "Essay 2", "Essay 3"]}
        )
        mock_validate.return_value = input_df

        # Create a mock progress bar that tracks updates
        progress_context = MagicMock()
        mock_progress_bar.return_value.__enter__.return_value = progress_context

        # Setup the return value for process_with_openai
        processed_df = pd.DataFrame(
            {
                "student_id": ["001", "002", "003"],
                "essay_response": ["Essay 1", "Essay 2", "Essay 3"],
                "score": [85, 90, 75],
            }
        )

        # Instead of using a callback, directly update the progress bar in our mock
        async def mock_process_impl(df, *args, **kwargs):
            # Manually update progress bar for each row in df
            for _ in range(len(df)):
                if kwargs.get("progress_callback"):
                    progress_context.update.assert_not_called()  # Should not be called yet
                    # Call the progress callback
                    await kwargs["progress_callback"]()
                    # Verify the callback updated the progress bar
                    progress_context.update.assert_called_with(1)
                    progress_context.reset_mock()
            return processed_df, []

        mock_process.side_effect = mock_process_impl

        # Call the function with progress bar enabled
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=Path(temp_files["export_folder"]),
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=False,
            cost_analysis=False,
            passes=1,
            merge_results=False,
            story_folder=None,
            rubric_folder=None,
            question_file=None,
            start_time=time.time(),
            show_progress=True,  # Enable progress bar
            calculate_totals=False,
        )

        # Verify process_with_openai was called with the right arguments
        mock_process.assert_called_once()
        # Don't check progress_context.update.call_count as we reset it in our mock
        assert mock_progress_bar.called


@pytest.mark.asyncio
async def test_process_csv_multiple_passes(temp_files):
    """Test processing CSV with multiple passes."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.merge_csv_files") as mock_merge,
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost"),
        patch("typer.echo") as mock_echo,
    ):
        # Setup mocks
        processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
        mock_process.return_value = (processed_df, [MagicMock()])

        # Call function with multiple passes
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=Path(temp_files["export_folder"]),
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=False,
            cost_analysis=True,
            passes=3,
            merge_results=True,
            story_folder=None,
            rubric_folder=None,
            question_file=None,
            start_time=time.time(),
            show_progress=False,
            calculate_totals=True,
        )

        # Verify multiple passes were processed
        assert mock_process.call_count == 3
        mock_merge.assert_called_once()
        assert mock_echo.call_count >= 3  # Echo for each pass


@pytest.mark.asyncio
async def test_process_csv_handles_exception(temp_files):
    """Test that process_csv properly handles exceptions."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.logging.getLogger") as mock_get_logger,
    ):
        # Setup mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Make process_with_openai raise an exception
        mock_process.side_effect = Exception("Test error")

        # Call function and check that exception is raised
        with pytest.raises(Exception, match="Test error"):
            await process_csv(
                input_file=temp_files["input_file"],
                export_folder=Path(temp_files["export_folder"]),
                file_name="test_output",
                scoring_format="numeric",
                openai_project="test-project",
                api_key="test-key",
                ai_model="gpt-4",
                log=True,
                cost_analysis=False,
                passes=1,
                merge_results=False,
                story_folder=None,
                rubric_folder=None,
                question_file=None,
                start_time=time.time(),
                show_progress=False,
                calculate_totals=True,
            )

        # Verify the error was logged
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_process_csv_cost_analysis_output(temp_files):
    """Test that cost analysis data is properly processed and displayed."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
        patch("typer.echo") as mock_echo,
        patch("pandas.DataFrame.to_csv") as mock_to_csv,
        patch("ai_essay_evaluator.evaluator.processor.logging.getLogger") as mock_get_logger,
    ):
        # Setup mocks
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
        mock_process.return_value = (processed_df, [MagicMock()])

        # Mock the cost analysis return value
        mock_analyze.return_value = {"total_cached_tokens": 1000, "total_uncached_tokens": 500, "total_cost": 0.1234}

        # Call function with cost analysis enabled
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=Path(temp_files["export_folder"]),
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=True,
            cost_analysis=True,
            passes=1,
            merge_results=False,
            story_folder=None,
            rubric_folder=None,
            question_file=None,
            start_time=time.time() - 10,  # 10 seconds ago
            show_progress=False,
            calculate_totals=True,
        )

        # Verify cost analysis was called and results processed
        mock_analyze.assert_called_once()
        mock_to_csv.assert_called_once()
        assert mock_echo.call_count >= 3  # Should see cost summary outputs

        # Verify duration was added to cost data
        duration_arg = mock_analyze.return_value.get("duration_seconds")
        assert duration_arg is not None


@pytest.mark.asyncio
async def test_process_csv_without_calculate_totals(temp_files):
    """Test processing CSV without calculating totals."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
        patch("ai_essay_evaluator.evaluator.processor.merge_csv_files") as mock_merge,
    ):
        # Setup mocks
        processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
        mock_process.return_value = (processed_df, [])

        # Call function without calculate_totals
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=Path(temp_files["export_folder"]),
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=False,
            cost_analysis=False,
            passes=2,
            merge_results=True,
            story_folder=None,
            rubric_folder=None,
            question_file=None,
            start_time=time.time(),
            show_progress=False,
            calculate_totals=False,
        )

        # Verify save_results and merge_csv_files were called with calculate_totals=False
        mock_save.assert_called_with(processed_df, mock_save.call_args[0][1], False)
        mock_merge.assert_called_with(mock_merge.call_args[0][0], mock_merge.call_args[0][1], "numeric", False)
