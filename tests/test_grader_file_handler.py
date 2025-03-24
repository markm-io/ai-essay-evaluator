from pathlib import Path

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.file_handler import merge_csv_files, normalize_text, save_results


@pytest.fixture
def temp_dir(tmpdir):
    """Create a temporary directory for test files."""
    return Path(tmpdir)


def test_normalize_text():
    """Test normalize_text function with various inputs."""
    # Test with normal text
    assert normalize_text("Hello World") == "Hello World"

    # Test with non-string input
    assert normalize_text(123) == 123

    # Test with special characters
    special_text = "Café académique"
    normalized = normalize_text(special_text)
    assert normalized == "Cafe academique"

    # Test with combining characters
    combining_text = "a\u0303"  # ã (a with tilde)
    normalized = normalize_text(combining_text)
    assert normalized == "a"


def test_save_results_basic(temp_dir):
    """Test saving basic DataFrame to CSV."""
    data = {"essay_id": [1, 2, 3], "score": [85, 92, 78], "feedback": ["Good", "Excellent", "Average"]}
    df = pd.DataFrame(data)
    output_path = temp_dir / "results_basic.csv"

    save_results(df, output_path)

    # Verify file exists and content
    assert output_path.exists()
    loaded_df = pd.read_csv(output_path)

    # Check total score was added
    assert "total_score" in loaded_df.columns
    assert all(loaded_df["total_score"] == loaded_df["score"])


def test_save_results_extended(temp_dir):
    """Test saving extended format DataFrame to CSV."""
    data = {
        "essay_id": [1, 2, 3],
        "idea_development_score": [40, 45, 38],
        "language_conventions_score": [45, 47, 40],
        "idea_development_feedback": ["Good", "Excellent", "Average"],
        "language_conventions_feedback": ["Well done", "Great", "Needs work"],
    }
    df = pd.DataFrame(data)
    output_path = temp_dir / "results_extended.csv"

    save_results(df, output_path)

    # Verify file exists and content
    assert output_path.exists()
    loaded_df = pd.read_csv(output_path)

    # Check total score calculation
    assert "total_score" in loaded_df.columns
    expected_totals = df["idea_development_score"] + df["language_conventions_score"]
    assert all(loaded_df["total_score"] == expected_totals)


def test_save_results_without_totals(temp_dir):
    """Test saving DataFrame without calculating totals."""
    data = {"essay_id": [1, 2, 3], "idea_development_score": [40, 45, 38], "language_conventions_score": [45, 47, 40]}
    df = pd.DataFrame(data)
    output_path = temp_dir / "results_no_totals.csv"

    save_results(df, output_path, calculate_totals=False)

    # Verify file exists and content
    assert output_path.exists()
    loaded_df = pd.read_csv(output_path)

    # Check total score was not added
    assert "total_score" not in loaded_df.columns


def test_save_results_with_nan_values(temp_dir):
    """Test saving DataFrame with NaN values."""
    data = {"essay_id": [1, 2, 3], "score": [85, float("nan"), 78], "feedback": ["Good", None, "Average"]}
    df = pd.DataFrame(data)
    output_path = temp_dir / "results_with_nan.csv"

    save_results(df, output_path)

    # Verify file exists and content
    assert output_path.exists()
    loaded_df = pd.read_csv(output_path)

    # Check NaN scores are converted to 0 for total calculation
    assert loaded_df.loc[1, "total_score"] == 0


def test_merge_csv_files_short_format(temp_dir):
    """Test merging CSV files in short format."""
    # Create first pass file
    data1 = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "score": [85, 90],
        "feedback": ["Good work", "Excellent"],
    }
    df1 = pd.DataFrame(data1)
    file1_path = temp_dir / "pass_1_pass_1.csv"
    df1.to_csv(file1_path, index=False)

    # Create second pass file
    data2 = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "score": [82, 92],
        "feedback": ["Good", "Very good"],
    }
    df2 = pd.DataFrame(data2)
    file2_path = temp_dir / "pass_2_pass_2.csv"
    df2.to_csv(file2_path, index=False)

    output_path = temp_dir / "merged_short.csv"

    # Merge files
    merged_df = merge_csv_files([file1_path, file2_path], output_path, "short")

    # Verify file exists
    assert output_path.exists()

    # Verify merged columns exist
    assert "score_pass1" in merged_df.columns
    assert "feedback_pass1" in merged_df.columns
    assert "score_pass2" in merged_df.columns
    assert "feedback_pass2" in merged_df.columns


def test_merge_csv_files_extended_format(temp_dir):
    """Test merging CSV files in extended format."""
    # Create first pass file
    data1 = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "idea_development_score": [40, 45],
        "language_conventions_score": [45, 47],
        "idea_development_feedback": ["Good", "Excellent"],
        "language_conventions_feedback": ["Well done", "Great"],
        "total_score": [85, 92],
    }
    df1 = pd.DataFrame(data1)
    file1_path = temp_dir / "pass_1_pass_1.csv"
    df1.to_csv(file1_path, index=False)

    # Create second pass file
    data2 = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "idea_development_score": [38, 44],
        "language_conventions_score": [42, 46],
        "idea_development_feedback": ["Fair", "Good"],
        "language_conventions_feedback": ["Okay", "Nice"],
        "total_score": [80, 90],
    }
    df2 = pd.DataFrame(data2)
    file2_path = temp_dir / "pass_2_pass_2.csv"
    df2.to_csv(file2_path, index=False)

    output_path = temp_dir / "merged_extended.csv"

    # Merge files
    merged_df = merge_csv_files([file1_path, file2_path], output_path, "extended")

    # Verify file exists
    assert output_path.exists()

    # Verify merged columns exist
    assert "idea_development_score_pass1" in merged_df.columns
    assert "language_conventions_score_pass1" in merged_df.columns
    assert "idea_development_score_pass2" in merged_df.columns
    assert "language_conventions_score_pass2" in merged_df.columns

    # Verify total score calculation from all passes
    assert merged_df["total_score"].iloc[0] == 165  # 85 + 80
    assert merged_df["total_score"].iloc[1] == 182  # 92 + 90


def test_merge_csv_files_without_totals(temp_dir):
    """Test merging CSV files without calculating totals."""
    # Create files (without total_score in the input)
    data1 = {"Local Student ID": ["S001", "S002"], "TeacherName": ["Smith", "Jones"], "score": [85, 90]}
    df1 = pd.DataFrame(data1)
    file1_path = temp_dir / "pass_1_pass_1.csv"
    df1.to_csv(file1_path, index=False)

    data2 = {"Local Student ID": ["S001", "S002"], "TeacherName": ["Smith", "Jones"], "score": [82, 92]}
    df2 = pd.DataFrame(data2)
    file2_path = temp_dir / "pass_2_pass_2.csv"
    df2.to_csv(file2_path, index=False)

    output_path = temp_dir / "merged_no_totals.csv"

    # Merge files without totals
    merged_df = merge_csv_files([file1_path, file2_path], output_path, "short", calculate_totals=False)

    # Verify file exists
    assert output_path.exists()

    # Verify total score was not calculated
    assert "total_score" not in merged_df.columns


def test_merge_csv_files_single_file(temp_dir):
    """Test merging a single CSV file."""
    data = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "score": [85, 90],
        "feedback": ["Good", "Excellent"],
    }
    df = pd.DataFrame(data)
    file_path = temp_dir / "pass_1_pass_1.csv"
    df.to_csv(file_path, index=False)

    output_path = temp_dir / "merged_single.csv"

    # Merge single file
    merged_df = merge_csv_files([file_path], output_path, "short")

    # Verify file exists
    assert output_path.exists()

    # Verify columns were renamed properly
    assert "score_pass1" in merged_df.columns
    assert "feedback_pass1" in merged_df.columns


def test_merge_csv_files_with_special_characters(temp_dir):
    """Test merging CSV files with special characters."""
    # Create file with special characters
    data = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Müller", "García"],
        "score": [85, 90],
        "feedback": ["Très bien!", "¡Excelente trabajo!"],
    }
    df = pd.DataFrame(data)
    file_path = temp_dir / "special_chars_pass_1.csv"
    df.to_csv(file_path, index=False, encoding="utf-8")

    output_path = temp_dir / "merged_special.csv"

    # Verify file exists
    assert output_path.exists()

    # Verify special characters were normalized
    loaded_df = pd.read_csv(output_path)
    assert loaded_df["TeacherName"].iloc[0] == "Muller"
    assert "Tres bien!" in loaded_df["feedback_pass1"].iloc[0]
    assert "Excelente trabajo!" in loaded_df["feedback_pass1"].iloc[1]


def test_merge_csv_files_with_encoding_fallback(temp_dir):
    """Test merging CSV files with encoding fallback."""
    # Create file with Latin-1 encoding
    data = {
        "Local Student ID": ["S001", "S002"],
        "TeacherName": ["Smith", "Jones"],
        "score": [85, 90],
        "feedback": ["Good", "Excellent"],
    }
    df = pd.DataFrame(data)
    file_path = temp_dir / "latin1_pass_1.csv"
    df.to_csv(file_path, index=False, encoding="latin1")

    output_path = temp_dir / "merged_latin1.csv"

    # Verify file exists
    assert output_path.exists()

    # Load and check content
    loaded_df = pd.read_csv(output_path)
    assert "score_pass1" in loaded_df.columns
    assert "feedback_pass1" in loaded_df.columns
