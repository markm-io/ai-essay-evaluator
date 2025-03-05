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
async def test_process_csv_single_pass(temp_files):
    """Test processing CSV with a single pass."""
    # Mock dependencies
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv") as mock_validate,
        patch("ai_essay_evaluator.evaluator.processor.read_text_files") as mock_read_files,
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
    ):
        # Setup mock returns
        mock_read_files.side_effect = lambda folder: {"file1.txt": "content"} if folder else {}

        processed_df = pd.DataFrame(
            {
                "student_id": ["001", "002", "003"],
                "essay_response": ["Sample essay 1", "Sample essay 2", "Sample essay 3"],
                "score": [85, 90, 75],
            }
        )
        mock_usages = [MagicMock(prompt_tokens=100, completion_tokens=50)]
        mock_process.return_value = (processed_df, mock_usages)

        # Call the function
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=temp_files["export_folder"],
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=True,
            cost_analysis=True,
            passes=1,
            merge_results=False,
            story_folder=temp_files["story_folder"],
            rubric_folder=temp_files["rubric_folder"],
            question_file=temp_files["question_file"],
        )

        # Verify calls
        mock_validate.assert_called_once()
        assert mock_read_files.call_count == 2
        mock_process.assert_called_once()
        mock_save.assert_called_once()
        mock_analyze.assert_called_once_with(mock_usages)


@pytest.mark.asyncio
async def test_process_csv_multiple_passes_with_merge(temp_files):
    """Test processing CSV with multiple passes and merging results."""
    # Mock dependencies
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files") as mock_read_files,
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.merge_csv_files") as mock_merge,
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
    ):
        # Setup mock returns
        mock_read_files.return_value = {"file1.txt": "content"}

        processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
        mock_usages = [MagicMock(prompt_tokens=100, completion_tokens=50)]
        mock_process.return_value = (processed_df, mock_usages)

        # Call the function
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=temp_files["export_folder"],
            file_name="test_output",
            scoring_format="numeric",
            openai_project="test-project",
            api_key="test-key",
            ai_model="gpt-4",
            log=False,
            cost_analysis=True,
            passes=3,
            merge_results=True,
            story_folder=temp_files["story_folder"],
            rubric_folder=temp_files["rubric_folder"],
            question_file=None,
        )

        # Verify calls
        assert mock_process.call_count == 3
        mock_merge.assert_called_once()
        mock_analyze.assert_called_once()
        # There should be 3 passed usages (3 passes * 1 usage per pass)
        assert len(mock_analyze.call_args[0][0]) == 3


@pytest.mark.asyncio
async def test_process_csv_no_cost_analysis(temp_files):
    """Test processing CSV without cost analysis."""
    # Mock dependencies
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
        patch("ai_essay_evaluator.evaluator.processor.read_text_files"),
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results"),
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
    ):
        processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
        mock_process.return_value = (processed_df, [])

        # Call the function with cost_analysis=False
        await process_csv(
            input_file=temp_files["input_file"],
            export_folder=temp_files["export_folder"],
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
        )

        # Verify analyze_cost was not called
        mock_analyze.assert_not_called()
