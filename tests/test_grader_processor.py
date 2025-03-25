from pathlib import Path

import pandas as pd
import pytest


# A dummy asynchronous logger class to simulate logging in tests.
class DummyAsyncLogger:
    def __init__(self, enabled):
        self.enabled = enabled
        self.log_calls = []
        self.closed = False
        self._log_file = "dummy.log"

    async def log(self, level, message, **kwargs):
        self.log_calls.append((level, message))

    def get_log_file(self):
        return self._log_file

    def close(self):
        self.closed = True


# Fixture: simple CSV without "Passes" column.
@pytest.fixture
def dummy_csv(tmp_path: Path) -> Path:
    file = tmp_path / "input.csv"
    df = pd.DataFrame({"Student Constructed Response": ["Essay 1", "Essay 2", "Essay 3"]})
    df.to_csv(file, index=False)
    return file


# Fixture: CSV with "Passes" column.
@pytest.fixture
def dummy_csv_with_passes(tmp_path: Path) -> Path:
    file = tmp_path / "input.csv"
    df = pd.DataFrame({"Student Constructed Response": ["Essay 1", "Essay 2", "Essay 3"], "Passes": [2, 2, 2]})
    df.to_csv(file, index=False)
    return file


# # Test processing without a progress bar and without additional files.
# @pytest.mark.asyncio
# async def test_process_csv_without_progress(dummy_csv, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#     processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
#     usage_list = []
#     dummy_async_logger = DummyAsyncLogger(enabled=False)
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv") as mock_validate,
#         patch("ai_essay_evaluator.evaluator.processor.normalize_response_text", side_effect=lambda df: df),
#         patch("ai_essay_evaluator.evaluator.processor.read_text_files", return_value={}),
#         patch(
#             "ai_essay_evaluator.evaluator.processor.process_with_openai",
#             new_callable=AsyncMock,
#             return_value=(processed_df, usage_list),
#         ) as mock_process,
#         patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#     ):
#         start_time = time.time()
#         await process_csv(
#             input_file=str(dummy_csv),
#             export_folder=export_folder,
#             file_name="output",
#             scoring_format="numeric",
#             openai_project="test-project",
#             api_key="test-key",
#             ai_model="gpt-4",
#             log=False,
#             cost_analysis=False,
#             passes=1,
#             merge_results=False,
#             story_folder=None,
#             rubric_folder=None,
#             question_file=None,
#             start_time=start_time,
#             show_progress=False,
#             calculate_totals=True,
#         )
#         # One pass so save_results and process_with_openai are each called once.
#         assert mock_save.call_count == 1
#         assert mock_process.call_count == 1
#         # Logger should be closed after processing.
#         assert dummy_async_logger.closed


# # Test processing with an enabled progress bar.
# @pytest.mark.asyncio
# async def test_process_csv_with_progress(dummy_csv, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#     processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
#     usage_list = []
#     dummy_async_logger = DummyAsyncLogger(enabled=False)
#
#     # Dummy progress bar to simulate the context manager.
#     class DummyProgress:
#         def __init__(self):
#             self.updated = 0
#
#         def update(self, n):
#             self.updated += n
#
#         def __enter__(self):
#             return self
#
#         def __exit__(self, exc_type, exc_val, exc_tb):
#             pass
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
#         patch("ai_essay_evaluator.evaluator.processor.normalize_response_text", side_effect=lambda df: df),
#         patch("ai_essay_evaluator.evaluator.processor.read_text_files", return_value={}),
#         patch(
#             "ai_essay_evaluator.evaluator.processor.process_with_openai",
#             new_callable=AsyncMock,
#             return_value=(processed_df, usage_list),
#         ) as mock_process,
#         patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
#         patch(
#             "ai_essay_evaluator.evaluator.processor.typer.progressbar", return_value=DummyProgress()
#         ) as mock_progress,
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#     ):
#         start_time = time.time()
#         await process_csv(
#             input_file=str(dummy_csv),
#             export_folder=export_folder,
#             file_name="output",
#             scoring_format="numeric",
#             openai_project="test-project",
#             api_key="test-key",
#             ai_model="gpt-4",
#             log=False,
#             cost_analysis=False,
#             passes=1,
#             merge_results=False,
#             story_folder=None,
#             rubric_folder=None,
#             question_file=None,
#             start_time=start_time,
#             show_progress=True,
#             calculate_totals=True,
#         )
#         # Validate that the progress bar was created.
#         mock_progress.assert_called_once()
#         assert mock_save.call_count == 1
#         assert mock_process.call_count == 1
#         assert dummy_async_logger.closed


# # Test processing with passes taken from the CSV file.
# @pytest.mark.asyncio
# async def test_process_csv_with_passes_from_csv(dummy_csv_with_passes, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#     processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
#     usage_list = []
#     dummy_async_logger = DummyAsyncLogger(enabled=True)
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
#         patch("ai_essay_evaluator.evaluator.processor.normalize_response_text", side_effect=lambda df: df),
#         patch("ai_essay_evaluator.evaluator.processor.read_text_files", return_value={}),
#         patch(
#             "ai_essay_evaluator.evaluator.processor.process_with_openai",
#             new_callable=AsyncMock,
#             return_value=(processed_df, usage_list),
#         ) as mock_process,
#         patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#     ):
#         start_time = time.time()
#         # Passes is None so the function uses the CSV column.
#         await process_csv(
#             input_file=str(dummy_csv_with_passes),
#             export_folder=export_folder,
#             file_name="output",
#             scoring_format="numeric",
#             openai_project="test-project",
#             api_key="test-key",
#             ai_model="gpt-4",
#             log=True,
#             cost_analysis=False,
#             passes=None,
#             merge_results=False,
#             story_folder=None,
#             rubric_folder=None,
#             question_file=None,
#             start_time=start_time,
#             show_progress=False,
#             calculate_totals=True,
#         )
#         # CSV has passes=2 so process_with_openai should be called twice.
#         assert mock_process.call_count == 2
#         assert dummy_async_logger.closed


# # Test failure when passes is None and CSV does not contain a "Passes" column.
# @pytest.mark.asyncio
# async def test_process_csv_missing_passes(dummy_csv, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#     dummy_async_logger = DummyAsyncLogger(enabled=True)
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#     ):
#         start_time = time.time()
#         with pytest.raises(Exception):
#             await process_csv(
#                 input_file=str(dummy_csv),
#                 export_folder=export_folder,
#                 file_name="output",
#                 scoring_format="numeric",
#                 openai_project="test-project",
#                 api_key="test-key",
#                 ai_model="gpt-4",
#                 log=True,
#                 cost_analysis=False,
#                 passes=None,
#                 merge_results=False,
#                 story_folder=None,
#                 rubric_folder=None,
#                 question_file=None,
#                 start_time=start_time,
#                 show_progress=False,
#                 calculate_totals=True,
#             )
#         # Check that an error log was recorded.
#         assert any("Error no \\'Passes\\' column" in msg for _, msg in dummy_async_logger.log_calls)
#         assert dummy_async_logger.closed


# # Test processing with additional files: story folder, rubric folder and question file.
# @pytest.mark.asyncio
# async def test_process_csv_with_additional_files(dummy_csv, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#
#     # Create additional files and folders.
#     story_folder = tmp_path / "stories"
#     story_folder.mkdir()
#     (story_folder / "story.txt").write_text("Story content")
#
#     rubric_folder = tmp_path / "rubrics"
#     rubric_folder.mkdir()
#     (rubric_folder / "rubric.txt").write_text("Rubric content")
#
#     question_file = tmp_path / "question.txt"
#     question_file.write_text("Question content")
#
#     processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
#     usage_list = []
#     dummy_async_logger = DummyAsyncLogger(enabled=True)
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
#         patch("ai_essay_evaluator.evaluator.processor.normalize_response_text", side_effect=lambda df: df),
#         patch("ai_essay_evaluator.evaluator.processor.read_text_files",
#         return_value={"dummy": "content"}) as mock_read,
#         patch(
#             "ai_essay_evaluator.evaluator.processor.process_with_openai",
#             new_callable=AsyncMock,
#             return_value=(processed_df, usage_list),
#         ) as mock_process,
#         patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#     ):
#         start_time = time.time()
#         await process_csv(
#             input_file=str(dummy_csv),
#             export_folder=export_folder,
#             file_name="output",
#             scoring_format="numeric",
#             openai_project="test-project",
#             api_key="test-key",
#             ai_model="gpt-4",
#             log=True,
#             cost_analysis=False,
#             passes=1,
#             merge_results=False,
#             story_folder=story_folder,
#             rubric_folder=rubric_folder,
#             question_file=question_file,
#             start_time=start_time,
#             show_progress=False,
#             calculate_totals=True,
#         )
#         # read_text_files should be called twice (once for each folder).
#         assert mock_read.call_count == 2
#         assert dummy_async_logger.closed


# # Test processing with cost analysis enabled.
# @pytest.mark.asyncio
# async def test_process_csv_cost_analysis(dummy_csv, tmp_path: Path):
#     export_folder = tmp_path / "export"
#     export_folder.mkdir()
#     processed_df = pd.DataFrame({"student_id": ["001", "002", "003"], "score": [85, 90, 75]})
#     usage_list = [{"token": 100}]
#     dummy_async_logger = DummyAsyncLogger(enabled=True)
#     dummy_cost = {
#         "total_cached_tokens": 50,
#         "total_uncached_tokens": 50,
#         "total_cost": 0.1234,
#     }
#
#     with (
#         patch("ai_essay_evaluator.evaluator.processor.validate_csv"),
#         patch("ai_essay_evaluator.evaluator.processor.normalize_response_text", side_effect=lambda df: df),
#         patch("ai_essay_evaluator.evaluator.processor.read_text_files", return_value={}),
#         patch(
#             "ai_essay_evaluator.evaluator.processor.process_with_openai",
#             new_callable=AsyncMock,
#             return_value=(processed_df, usage_list),
#         ) as mock_process,
#         patch("ai_essay_evaluator.evaluator.processor.save_results") as mock_save,
#         patch("ai_essay_evaluator.evaluator.processor.analyze_cost", return_value=dummy_cost) as mock_cost,
#         patch("ai_essay_evaluator.evaluator.processor.AsyncLogger", return_value=dummy_async_logger),
#         patch("ai_essay_evaluator.evaluator.processor.typer.echo") as mock_echo,
#     ):
#         start_time = time.time()
#         await process_csv(
#             input_file=str(dummy_csv),
#             export_folder=export_folder,
#             file_name="output",
#             scoring_format="numeric",
#             openai_project="test-project",
#             api_key="test-key",
#             ai_model="gpt-4",
#             log=True,
#             cost_analysis=True,
#             passes=1,
#             merge_results=False,
#             story_folder=None,
#             rubric_folder=None,
#             question_file=None,
#             start_time=start_time,
#             show_progress=False,
#             calculate_totals=True,
#         )
#         # Verify cost analysis function was invoked and cost information echoed.
#         assert mock_cost.call_count == 1
#         assert dummy_async_logger.closed
