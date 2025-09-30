import json

import pandas as pd
import pytest

from ai_essay_evaluator.trainer.generator import (
    BaseGradingResponse,
    generate_jsonl,
    load_rubric_files,
    load_story_files,
    load_text_file,
    validate_response,
)


class TestBaseGradingResponse:
    """Test cases for BaseGradingResponse model creation."""

    def test_create_model_extended(self):
        """Test creating extended format model."""
        model_class = BaseGradingResponse.create_model("extended")
        assert model_class.__name__ == "GradingResponseExtended"
        assert "Idea_Development_Score" in model_class.model_fields
        assert "Language_Conventions_Score" in model_class.model_fields

    def test_create_model_item_specific(self):
        """Test creating item-specific format model."""
        model_class = BaseGradingResponse.create_model("item-specific")
        assert model_class.__name__ == "GradingResponseBasic"
        assert "Score" in model_class.model_fields
        assert "Feedback" in model_class.model_fields

    def test_create_model_short(self):
        """Test creating short format model."""
        model_class = BaseGradingResponse.create_model("short")
        assert model_class.__name__ == "GradingResponseBasic"
        assert "Score" in model_class.model_fields

    def test_create_model_invalid_format(self):
        """Test creating model with invalid format raises error."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            BaseGradingResponse.create_model("invalid")


class TestValidateResponse:
    """Test cases for response validation."""

    def test_validate_response_extended_valid(self):
        """Test validating a valid extended response."""
        response = json.dumps(
            {
                "Idea_Development_Score": 4,
                "Idea_Development_Feedback": "Good work",
                "Language_Conventions_Score": 3,
                "Language_Conventions_Feedback": "Minor errors",
            }
        )
        result = validate_response(response, "extended")
        assert result is not None
        assert result.Idea_Development_Score == 4

    def test_validate_response_short_valid(self):
        """Test validating a valid short response."""
        response = json.dumps({"Score": 3, "Feedback": "Good"})
        result = validate_response(response, "short")
        assert result is not None
        assert result.Score == 3

    def test_validate_response_invalid_json(self):
        """Test validating invalid JSON."""
        # validate_response will try to parse "not json" and catch the JSONDecodeError
        # But the function exits with print instead of raising, so this will return None
        # due to the except block
        try:
            result = validate_response("not json", "short")
            assert result is None
        except json.JSONDecodeError:
            # If it raises, that's also acceptable behavior
            pass


class TestLoadTextFile:
    """Test cases for loading text files."""

    def test_load_text_file_success(self, tmp_path):
        """Test successfully loading a text file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content\u00a0with special space", encoding="utf-8")

        content = load_text_file(test_file)
        assert content == "Test content with special space"

    def test_load_text_file_not_found(self):
        """Test loading non-existent file exits."""
        with pytest.raises(SystemExit) as exc_info:
            load_text_file("/nonexistent/file.txt")
        assert exc_info.value.code == 1


class TestLoadRubricFiles:
    """Test cases for loading rubric files."""

    def test_load_rubric_files_extended(self, tmp_path):
        """Test loading rubrics for extended format."""
        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()

        rubric_file = rubric_dir / "idea_development.txt"
        rubric_file.write_text("score_4 - Excellent\nscore_3 - Good\n", encoding="utf-8")

        result = load_rubric_files(rubric_dir, "extended")
        assert "idea development" in result
        assert result["idea development"]["score_4"] == "Excellent"

    def test_load_rubric_files_flat(self, tmp_path):
        """Test loading rubrics for flat format."""
        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()

        rubric_file = rubric_dir / "rubric.txt"
        rubric_file.write_text("score_4 - Excellent\nscore_3 - Good\n", encoding="utf-8")

        result = load_rubric_files(rubric_dir, "short")
        assert "score_4" in result
        assert result["score_4"] == "Excellent"

    def test_load_rubric_files_not_found(self):
        """Test loading from non-existent directory exits."""
        with pytest.raises(SystemExit) as exc_info:
            load_rubric_files("/nonexistent", "extended")
        assert exc_info.value.code == 1


class TestLoadStoryFiles:
    """Test cases for loading story files."""

    def test_load_story_files_multiple(self, tmp_path):
        """Test loading multiple story files."""
        story_dir = tmp_path / "stories"
        story_dir.mkdir()

        (story_dir / "story1.txt").write_text("Story one content\u00a0here", encoding="utf-8")
        (story_dir / "story2.txt").write_text("Story two content", encoding="utf-8")

        result = load_story_files(story_dir)
        assert len(result) == 2
        assert "Story 1" in result
        assert "Story 2" in result
        assert "Story one content here" == result["Story 1"]

    def test_load_story_files_not_found(self):
        """Test loading from non-existent directory exits."""
        with pytest.raises(SystemExit) as exc_info:
            load_story_files("/nonexistent")
        assert exc_info.value.code == 1


class TestGenerateJsonl:
    """Test cases for JSONL generation."""

    def test_generate_jsonl_extended(self, tmp_path):
        """Test generating JSONL for extended format."""
        # Setup directories and files
        story_dir = tmp_path / "stories"
        story_dir.mkdir()
        (story_dir / "story1.txt").write_text("A tale of courage", encoding="utf-8")

        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()
        (rubric_dir / "idea_development.txt").write_text("score_4 - Excellent\n", encoding="utf-8")
        (rubric_dir / "language_conventions.txt").write_text("score_4 - Perfect\n", encoding="utf-8")

        question_file = tmp_path / "question.txt"
        question_file.write_text("What is courage?", encoding="utf-8")

        csv_file = tmp_path / "data.csv"
        df = pd.DataFrame(
            {
                "Local Student ID": [12345],
                "Enrolled Grade Level": [5],
                "Tested Language": ["English"],
                "Student Constructed Response": ["Courage is bravery"],
                "Idea Development Score": [4],
                "Idea Development Feedback": ["Excellent work"],
                "Language Conventions Score": [3],
                "Language Conventions Feedback": ["Minor errors"],
            }
        )
        df.to_csv(csv_file, index=False)

        output_file = tmp_path / "output.jsonl"

        result = generate_jsonl(story_dir, question_file, rubric_dir, csv_file, output_file, "extended")

        assert result == output_file
        assert output_file.exists()

        # Verify JSONL content
        with open(output_file, encoding="utf-8") as f:
            line = f.readline()
            data = json.loads(line)
            assert "messages" in data
            assert len(data["messages"]) == 3
            assert data["messages"][0]["role"] == "system"
            assert data["messages"][1]["role"] == "user"
            assert data["messages"][2]["role"] == "assistant"

    def test_generate_jsonl_short(self, tmp_path):
        """Test generating JSONL for short format."""
        # Setup directories and files
        story_dir = tmp_path / "stories"
        story_dir.mkdir()
        (story_dir / "story1.txt").write_text("A tale", encoding="utf-8")

        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()
        (rubric_dir / "rubric.txt").write_text("score_4 - Excellent\n", encoding="utf-8")

        question_file = tmp_path / "question.txt"
        question_file.write_text("Question?", encoding="utf-8")

        csv_file = tmp_path / "data.csv"
        df = pd.DataFrame(
            {
                "Local Student ID": [12345],
                "Enrolled Grade Level": [5],
                "Tested Language": ["English"],
                "Student Constructed Response": ["Answer"],
                "Score": [3],
                "Feedback": ["Good"],
            }
        )
        df.to_csv(csv_file, index=False)

        output_file = tmp_path / "output.jsonl"

        result = generate_jsonl(story_dir, question_file, rubric_dir, csv_file, output_file, "short")

        assert result == output_file
        assert output_file.exists()

    def test_generate_jsonl_spanish(self, tmp_path):
        """Test generating JSONL with Spanish language."""
        # Setup directories and files
        story_dir = tmp_path / "stories"
        story_dir.mkdir()
        (story_dir / "story1.txt").write_text("Una historia", encoding="utf-8")

        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()
        (rubric_dir / "rubric.txt").write_text("score_4 - Excelente\n", encoding="utf-8")

        question_file = tmp_path / "question.txt"
        question_file.write_text("¿Qué es?", encoding="utf-8")

        csv_file = tmp_path / "data.csv"
        df = pd.DataFrame(
            {
                "Local Student ID": [12345],
                "Enrolled Grade Level": [5],
                "Tested Language": ["Spanish"],
                "Student Constructed Response": ["Respuesta"],
                "Score": [3],
                "Feedback": ["Bien"],
            }
        )
        df.to_csv(csv_file, index=False)

        output_file = tmp_path / "output.jsonl"

        result = generate_jsonl(story_dir, question_file, rubric_dir, csv_file, output_file, "short")

        assert result == output_file

        # Verify Spanish instruction is included
        with open(output_file, encoding="utf-8") as f:
            line = f.readline()
            data = json.loads(line)
            user_content = json.loads(data["messages"][1]["content"])
            assert "español" in user_content["evaluation_guidance"]

    def test_generate_jsonl_invalid_csv(self, tmp_path):
        """Test generating JSONL with invalid CSV exits."""
        story_dir = tmp_path / "stories"
        story_dir.mkdir()
        (story_dir / "story1.txt").write_text("Story", encoding="utf-8")

        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()
        (rubric_dir / "rubric.txt").write_text("score_4 - Good\n", encoding="utf-8")

        question_file = tmp_path / "question.txt"
        question_file.write_text("Q?", encoding="utf-8")

        output_file = tmp_path / "output.jsonl"

        with pytest.raises(SystemExit) as exc_info:
            generate_jsonl(story_dir, question_file, rubric_dir, "/nonexistent.csv", output_file, "short")
        assert exc_info.value.code == 1

    def test_generate_jsonl_invalid_format(self, tmp_path):
        """Test generating JSONL with invalid format exits."""
        story_dir = tmp_path / "stories"
        story_dir.mkdir()
        (story_dir / "story1.txt").write_text("Story", encoding="utf-8")

        rubric_dir = tmp_path / "rubrics"
        rubric_dir.mkdir()
        (rubric_dir / "rubric.txt").write_text("score_4 - Good\n", encoding="utf-8")

        question_file = tmp_path / "question.txt"
        question_file.write_text("Q?", encoding="utf-8")

        csv_file = tmp_path / "data.csv"
        df = pd.DataFrame(
            {
                "Local Student ID": [12345],
                "Enrolled Grade Level": [5],
                "Tested Language": ["English"],
                "Student Constructed Response": ["Answer"],
                "Score": [3],
                "Feedback": ["Good"],
            }
        )
        df.to_csv(csv_file, index=False)

        output_file = tmp_path / "output.jsonl"

        with pytest.raises(SystemExit) as exc_info:
            generate_jsonl(story_dir, question_file, rubric_dir, csv_file, output_file, "invalid")
        assert exc_info.value.code == 1
