import os

import pandas as pd
import pytest

from ai_essay_evaluator.evaluator.file_handler import merge_csv_files, save_results


@pytest.fixture
def temp_dir(tmpdir):
    """Create a temporary directory for test files."""
    return tmpdir


def test_save_results(temp_dir):
    """Test saving DataFrame to CSV."""
    # Create a sample DataFrame
    data = {"essay_id": [1, 2, 3], "score": [85, 92, 78], "feedback": ["Good", "Excellent", "Average"]}
    df = pd.DataFrame(data)

    # Define output path
    output_path = os.path.join(temp_dir, "results.csv")

    # Save the DataFrame
    save_results(df, output_path)

    # Verify the file exists
    assert os.path.exists(output_path)

    # Verify the content
    loaded_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(df, loaded_df)


def test_merge_csv_files(temp_dir):
    """Test merging multiple CSV files."""
    # Create sample DataFrames
    data1 = {"essay_id": [1, 2], "score": [85, 92], "feedback": ["Good", "Excellent"]}
    data2 = {"essay_id": [3, 4], "score": [78, 88], "feedback": ["Average", "Good"]}
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    # Define file paths
    file1_path = os.path.join(temp_dir, "file1.csv")
    file2_path = os.path.join(temp_dir, "file2.csv")
    output_path = os.path.join(temp_dir, "merged.csv")

    # Save the individual files
    df1.to_csv(file1_path, index=False)
    df2.to_csv(file2_path, index=False)

    # Merge the files
    merge_csv_files([file1_path, file2_path], output_path)

    # Verify the output file exists
    assert os.path.exists(output_path)

    # Expected merged DataFrame
    expected_df = pd.concat([df1, df2], ignore_index=True)

    # Load and verify the merged file
    merged_df = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(expected_df, merged_df)


def test_merge_csv_files_empty(temp_dir):
    """Test merging with empty file list."""
    output_path = os.path.join(temp_dir, "merged_empty.csv")

    # Call with empty list should create empty DataFrame
    with pytest.raises(ValueError):
        merge_csv_files([], output_path)
