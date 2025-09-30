import json

import pytest

from ai_essay_evaluator.trainer.merge import merge_jsonl_files


class TestMergeJsonlFiles:
    """Test cases for merging JSONL files."""

    def test_merge_jsonl_files_multiple(self, tmp_path):
        """Test merging multiple JSONL files."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create first JSONL file
        file1 = input_dir / "file1.jsonl"
        data1 = {"messages": [{"role": "user", "content": "test1"}]}
        with open(file1, "w", encoding="utf-8") as f:
            f.write(json.dumps(data1) + "\n")

        # Create second JSONL file
        file2 = input_dir / "file2.jsonl"
        data2 = {"messages": [{"role": "user", "content": "test2"}]}
        with open(file2, "w", encoding="utf-8") as f:
            f.write(json.dumps(data2) + "\n")

        output_file = tmp_path / "merged.jsonl"

        result = merge_jsonl_files(str(input_dir), str(output_file))

        assert result == str(output_file)
        assert output_file.exists()

        # Verify merged content
        with open(output_file, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 2

    def test_merge_jsonl_files_single(self, tmp_path):
        """Test merging a single JSONL file."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.jsonl"
        data1 = {"messages": [{"role": "user", "content": "test"}]}
        with open(file1, "w", encoding="utf-8") as f:
            f.write(json.dumps(data1) + "\n")

        output_file = tmp_path / "merged.jsonl"

        result = merge_jsonl_files(str(input_dir), str(output_file))

        assert result == str(output_file)
        assert output_file.exists()

    def test_merge_jsonl_files_multiple_lines_per_file(self, tmp_path):
        """Test merging JSONL files with multiple lines each."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.jsonl"
        with open(file1, "w", encoding="utf-8") as f:
            f.write(json.dumps({"data": "line1"}) + "\n")
            f.write(json.dumps({"data": "line2"}) + "\n")

        file2 = input_dir / "file2.jsonl"
        with open(file2, "w", encoding="utf-8") as f:
            f.write(json.dumps({"data": "line3"}) + "\n")

        output_file = tmp_path / "merged.jsonl"

        merge_jsonl_files(str(input_dir), str(output_file))

        # Verify all lines are included
        with open(output_file, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 3

    def test_merge_jsonl_files_no_jsonl_files(self, tmp_path):
        """Test merging with no JSONL files in directory exits."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create a non-JSONL file
        (input_dir / "file.txt").write_text("not jsonl")

        output_file = tmp_path / "merged.jsonl"

        with pytest.raises(SystemExit) as exc_info:
            merge_jsonl_files(str(input_dir), str(output_file))
        assert exc_info.value.code == 1

    def test_merge_jsonl_files_invalid_json(self, tmp_path):
        """Test merging with invalid JSON in file raises error."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.jsonl"
        with open(file1, "w", encoding="utf-8") as f:
            f.write("not valid json\n")

        output_file = tmp_path / "merged.jsonl"

        with pytest.raises(json.JSONDecodeError):
            merge_jsonl_files(str(input_dir), str(output_file))

    def test_merge_jsonl_files_preserves_encoding(self, tmp_path):
        """Test merging preserves UTF-8 encoding."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.jsonl"
        data = {"content": "Español: ñ, á, é"}
        with open(file1, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

        output_file = tmp_path / "merged.jsonl"

        merge_jsonl_files(str(input_dir), str(output_file))

        # Verify encoding is preserved
        with open(output_file, encoding="utf-8") as f:
            line = f.readline()
            data_out = json.loads(line)
            assert "ñ" in data_out["content"]
            assert "á" in data_out["content"]

    def test_merge_jsonl_files_output_path_types(self, tmp_path):
        """Test merge works with Path and str types."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.jsonl"
        with open(file1, "w", encoding="utf-8") as f:
            f.write(json.dumps({"test": "data"}) + "\n")

        output_file = tmp_path / "merged.jsonl"

        # Test with Path objects
        result = merge_jsonl_files(input_dir, output_file)
        assert result == str(output_file)
