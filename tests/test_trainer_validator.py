import json

import pytest

from ai_essay_evaluator.trainer.validator import validate_jsonl


class TestValidateJsonl:
    """Test cases for JSONL validation."""

    def test_validate_jsonl_extended_valid(self, tmp_path):
        """Test validating a valid extended format JSONL file."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "Idea_Development_Score": "4",
                            "Idea_Development_Feedback": "Great",
                            "Language_Conventions_Score": "3",
                            "Language_Conventions_Feedback": "Good",
                        }
                    ),
                },
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        result = validate_jsonl(str(jsonl_file), "extended")
        assert result is True

    def test_validate_jsonl_short_valid(self, tmp_path):
        """Test validating a valid short format JSONL file."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {"role": "assistant", "content": json.dumps({"Score": "3", "Feedback": "Good"})},
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        result = validate_jsonl(str(jsonl_file), "short")
        assert result is True

    def test_validate_jsonl_item_specific_valid(self, tmp_path):
        """Test validating a valid item-specific format JSONL file."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {"role": "assistant", "content": json.dumps({"Score": "4", "Feedback": "Excellent"})},
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        result = validate_jsonl(str(jsonl_file), "item-specific")
        assert result is True

    def test_validate_jsonl_missing_messages_key(self, tmp_path):
        """Test validating JSONL with missing 'messages' key exits."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {"data": "no messages key"}

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_messages_not_list(self, tmp_path):
        """Test validating JSONL where messages is not a list exits."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {"messages": "not a list"}

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_incorrect_roles(self, tmp_path):
        """Test validating JSONL with incorrect role sequence exits."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "user", "content": "Wrong order"},
                {"role": "system", "content": "Should be first"},
                {"role": "assistant", "content": "{}"},
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_missing_score_fields_extended(self, tmp_path):
        """Test validating extended format JSONL with missing score fields exits."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {
                    "role": "assistant",
                    "content": json.dumps({"Score": "3"}),  # Missing extended fields
                },
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_missing_score_fields_short(self, tmp_path):
        """Test validating short format JSONL with missing score fields exits."""
        jsonl_file = tmp_path / "test.jsonl"

        data = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {
                    "role": "assistant",
                    "content": json.dumps({"Feedback": "Good"}),  # Missing Score
                },
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "short")
        assert exc_info.value.code == 1

    def test_validate_jsonl_invalid_json(self, tmp_path):
        """Test validating JSONL with invalid JSON exits."""
        jsonl_file = tmp_path / "test.jsonl"

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write("not valid json\n")

        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl(str(jsonl_file), "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_file_not_found(self):
        """Test validating non-existent file exits."""
        with pytest.raises(SystemExit) as exc_info:
            validate_jsonl("/nonexistent/file.jsonl", "extended")
        assert exc_info.value.code == 1

    def test_validate_jsonl_multiple_entries(self, tmp_path):
        """Test validating JSONL with multiple valid entries."""
        jsonl_file = tmp_path / "test.jsonl"

        data1 = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade this"},
                {"role": "assistant", "content": json.dumps({"Score": "3", "Feedback": "Good"})},
            ]
        }

        data2 = {
            "messages": [
                {"role": "system", "content": "AI Grader"},
                {"role": "user", "content": "Grade that"},
                {"role": "assistant", "content": json.dumps({"Score": "4", "Feedback": "Great"})},
            ]
        }

        with open(jsonl_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(data1) + "\n")
            f.write(json.dumps(data2) + "\n")

        result = validate_jsonl(str(jsonl_file), "short")
        assert result is True
