import tempfile
from pathlib import Path

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.utils import read_text_files, validate_csv


class TestValidateCSV:
    def test_validate_csv_with_valid_data(self):
        """Test validate_csv with data containing all required columns."""
        data = {
            "Local Student ID": [1, 2, 3],
            "Enrolled Grade Level": ["K", "1", "2"],
            "Tested Language": ["English", "Spanish", "English"],
        }
        df = pd.DataFrame(data)

        # Should not raise an exception
        validate_csv(df)

    def test_validate_csv_with_missing_columns(self):
        """Test validate_csv with data missing required columns."""
        data = {
            "Local Student ID": [1, 2, 3],
            "Enrolled Grade Level": ["K", "1", "2"],
            # Missing "Tested Language"
        }
        df = pd.DataFrame(data)

        with pytest.raises(ValueError) as excinfo:
            validate_csv(df)
        assert "Missing required columns" in str(excinfo.value)

    def test_validate_csv_with_empty_dataframe(self):
        """Test validate_csv with an empty DataFrame."""
        df = pd.DataFrame()

        with pytest.raises(ValueError) as excinfo:
            validate_csv(df)
        assert "Missing required columns" in str(excinfo.value)


class TestReadTextFiles:
    def test_read_text_files_with_valid_folder(self):
        """Test read_text_files with a folder containing text files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            # Create test files
            file1 = folder / "test1.txt"
            file2 = folder / "test2.txt"

            file1.write_text("Test content 1")
            file2.write_text("Test content 2\nwith multiple lines")

            # Create a non-txt file to verify it's ignored
            (folder / "ignored.csv").write_text("should be ignored")

            result = read_text_files(folder)

            assert len(result) == 2
            assert result["test1.txt"] == "Test content 1"
            assert result["test2.txt"] == "Test content 2\nwith multiple lines"

    def test_read_text_files_with_empty_folder(self):
        """Test read_text_files with an empty folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            result = read_text_files(folder)
            assert result == {}

    def test_read_text_files_with_special_characters(self):
        """Test read_text_files with text containing special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            file = folder / "special.txt"
            file.write_text("Text with\u00a0non-breaking space")

            result = read_text_files(folder)

            assert result["special.txt"] == "Text with non-breaking space"
