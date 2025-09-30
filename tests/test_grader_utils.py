import tempfile
from pathlib import Path

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.utils import normalize_response_text, normalize_text, read_text_files, validate_csv


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


class TestNormalizeText:
    def test_normalize_text_basic(self):
        """Test normalize_text with basic text."""
        result = normalize_text("Hello world")
        assert result == "Hello world"

    def test_normalize_text_with_smart_apostrophe(self):
        """Test normalize_text with smart apostrophe sequence."""
        result = normalize_text("That\u201a\u00c4\u00f4s great")
        assert "'" in result

    def test_normalize_text_with_quotation_marks(self):
        """Test normalize_text with various quotation marks."""
        result = normalize_text("He said \u2018hello\u2019")
        assert "'" in result

    def test_normalize_text_with_non_string(self):
        """Test normalize_text with non-string input."""
        result = normalize_text(123)
        assert result == 123


class TestNormalizeResponseText:
    def test_normalize_response_text_basic(self):
        """Test normalizing text in DataFrame."""
        df = pd.DataFrame({"Student Constructed Response": ["Hello world", "Test"]})
        result = normalize_response_text(df)
        assert len(result) == 2
        assert "Student Constructed Response" in result.columns

    def test_normalize_response_text_with_nan(self):
        """Test normalizing DataFrame with NaN values."""
        df = pd.DataFrame({"Student Constructed Response": ["Hello", None, "World"]})
        result = normalize_response_text(df)
        assert result["Student Constructed Response"].iloc[1] is None

    def test_normalize_response_text_preserves_other_columns(self):
        """Test that normalization preserves other columns."""
        df = pd.DataFrame({"Student Constructed Response": ["Text"], "ID": [123], "Grade": [5]})
        result = normalize_response_text(df)
        assert "ID" in result.columns
        assert result["ID"].iloc[0] == 123
