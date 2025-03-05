from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.processor import process_csv


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    df = pd.DataFrame(
        {
            "Student Constructed Response": ["This is a test response"],
            "Local Student ID": [12345],
            "Tested Language": ["English"],
            "Enrolled Grade Level": [5],
        }
    )
    csv_path = tmp_path / "test_input.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def export_folder(tmp_path):
    """Create an export folder."""
    folder = tmp_path / "export"
    folder.mkdir()
    return folder


@pytest.fixture
def story_folder(tmp_path):
    """Create a folder with story files."""
    folder = tmp_path / "stories"
    folder.mkdir()
    (folder / "story1.txt").write_text("This is a test story")
    return folder


@pytest.fixture
def rubric_folder(tmp_path):
    """Create a folder with rubric files."""
    folder = tmp_path / "rubrics"
    folder.mkdir()
    (folder / "rubric1.txt").write_text("Test scoring rubric")
    return folder


@pytest.fixture
def question_file(tmp_path):
    """Create a question file."""
    file_path = tmp_path / "question.txt"
    file_path.write_text("Test question")
    return file_path


@pytest.mark.asyncio
async def test_process_csv(sample_csv, export_folder, story_folder, rubric_folder, question_file):
    """Test the process_csv function."""
    # Mock dependencies
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv") as mock_validate,
        patch("ai_essay_evaluator.evaluator.processor.read_text_files") as mock_read_texts,
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
        patch("ai_essay_evaluator.evaluator.processor.merge_csv_files") as mock_merge,
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
    ):
        # Configure mocks
        mock_read_texts.side_effect = lambda folder: {"file1": "content"}

        # Create a response DataFrame with the same rows as input plus score columns
        input_df = pd.read_csv(sample_csv)
        response_df = pd.concat([input_df, pd.DataFrame({"score": [4], "feedback": ["Good work"]})], axis=1)
        mock_process.return_value = response_df

        # Call the function under test
        await process_csv(
            input_file=sample_csv,
            export_folder=export_folder,
            file_name="test_output",
            scoring_format="standard",
            openai_project=True,
            api_key="test_key",
            ai_model="gpt-4o",
            log=True,
            cost_analysis=True,
            passes=2,
            merge_results=True,
            story_folder=story_folder,
            rubric_folder=rubric_folder,
            question_file=question_file,
        )

        # Assertions
        mock_validate.assert_called_once()
        assert mock_read_texts.call_count == 2
        assert mock_process.call_count == 2
        assert mock_save.call_count == 2

        # Check that output paths were properly generated
        expected_output_paths = [export_folder / "test_output_pass_1.csv", export_folder / "test_output_pass_2.csv"]
        mock_merge.assert_called_once_with(expected_output_paths, export_folder / "test_output_merged.csv")
        mock_analyze.assert_called_once()


@pytest.mark.asyncio
async def test_process_csv_single_pass(sample_csv, export_folder):
    """Test process_csv with a single pass and no additional files."""
    with (
        patch("ai_essay_evaluator.evaluator.processor.validate_csv") as mock_validate,
        patch("ai_essay_evaluator.evaluator.processor.process_with_openai", new_callable=AsyncMock) as mock_process,
        patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
        patch("ai_essay_evaluator.evaluator.processor.merge_csv_files") as mock_merge,
        patch("ai_essay_evaluator.evaluator.processor.analyze_cost") as mock_analyze,
    ):
        # Configure mocks
        input_df = pd.read_csv(sample_csv)
        response_df = pd.concat([input_df, pd.DataFrame({"score": [3], "feedback": ["Needs improvement"]})], axis=1)
        mock_process.return_value = response_df

        # Call the function under test with minimal parameters
        await process_csv(
            input_file=sample_csv,
            export_folder=export_folder,
            file_name="minimal_test",
            scoring_format="standard",
            openai_project=True,
            api_key="test_key",
            ai_model="gpt-4o",
            log=False,
            cost_analysis=False,
            passes=1,
            merge_results=False,
            story_folder=None,
            rubric_folder=None,
            question_file=None,
        )

        # Assertions
        mock_validate.assert_called_once()
        mock_process.assert_called_once()
        mock_save.assert_called_once()
        mock_merge.assert_not_called()
        mock_analyze.assert_not_called()
