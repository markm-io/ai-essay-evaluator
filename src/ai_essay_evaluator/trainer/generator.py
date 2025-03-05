import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ValidationError


class BaseGradingResponse(BaseModel):
    """Base class for grading responses to enable dynamic response models."""

    @classmethod
    def create_model(cls, output_format: str) -> type:
        """
        Returns the appropriate Pydantic model based on the output format.

        Args:
            output_format (str): The format type (e.g., "item-specific", "short", "extended").

        Returns:
            Type[BaseModel]: A dynamically selected Pydantic model.

        """
        if output_format in ["item-specific", "short"]:
            return type(
                "GradingResponseBasic",
                (BaseModel,),
                {
                    "__annotations__": {
                        "Score": int,
                        "Feedback": str,
                    }
                },
            )

        elif output_format == "extended":
            return type(
                "GradingResponseExtended",
                (BaseModel,),
                {
                    "__annotations__": {
                        "Idea_Development_Score": int,
                        "Idea_Development_Feedback": str,
                        "Language_Conventions_Score": int,
                        "Language_Conventions_Feedback": str,
                    }
                },
            )

        else:
            raise ValueError(f"❌ Error: Unsupported output format '{output_format}'.")


def validate_response(response_content: str, output_format: str) -> BaseModel | None:
    """
    Validates and parses a JSON response string into the correct grading model.

    Args:
        response_content (str): JSON string containing grading response.
        output_format (str): Determines which grading model to use.

    Returns:
        BaseModel | None: Validated response model if successful, None if validation fails.

    """
    try:
        response_dict = json.loads(response_content)
        GradingModel = BaseGradingResponse.create_model(output_format)
        return GradingModel(**response_dict)
    except ValidationError as e:
        print(f"❌ Validation Error: {e.json()}")
        return None


def load_text_file(file_path: str | Path) -> str:
    """
    Load and normalize text file contents.

    Args:
        file_path: Path to the text file to load, as string or Path object

    Returns:
        str: File contents with normalized spaces

    Raises:
        FileNotFoundError: If the specified file does not exist

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read().strip()
        return text.replace("\u00a0", " ")  # Normalize spaces
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        exit(1)


def load_rubric_files(rubric_folder: str | Path, output_format: str) -> dict[str, Any]:
    """
    Loads multiple rubric files from a folder and organizes them into a dictionary.

    - If `output_format == "extended"`, the rubric is **structured by categories**.
    - Otherwise, the rubric is **flattened** to only contain `score_3`, `score_2`, etc.

    Returns:
        dict: A structured or flattened rubric dictionary.

    """
    rubric_dict: dict[str, Any] = {}

    rubric_folder = Path(rubric_folder)

    if not rubric_folder.exists() or not rubric_folder.is_dir():
        print(f"❌ Error: Rubric folder '{rubric_folder}' not found or not a directory.")
        exit(1)

    for rubric_file in rubric_folder.glob("*.txt"):
        category_name = rubric_file.stem.replace("_", " ")

        try:
            with open(rubric_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if " - " in line:
                        key, value = line.split(" - ", 1)
                        key = key.strip()
                        value = value.strip()

                        if output_format == "extended":
                            if category_name not in rubric_dict:
                                rubric_dict[category_name] = {}
                            rubric_dict[category_name][key] = value
                        else:
                            rubric_dict[key] = value

        except Exception as e:
            print(f"❌ Error reading '{rubric_file}': {e}")
            exit(1)

    return rubric_dict


def load_story_files(story_folder: str | Path) -> dict[str, str]:
    """
    Loads multiple story files from a folder and organizes them into a dictionary.

    Returns:
        dict: A dictionary mapping "Story 1", "Story 2", etc., to story content.

    """
    story_dict: dict[str, str] = {}

    story_folder = Path(story_folder)

    if not story_folder.exists() or not story_folder.is_dir():
        print(f"❌ Error: Story folder '{story_folder}' not found or not a directory.")
        exit(1)

    story_files = sorted(story_folder.glob("*.txt"))  # Sort for consistent ordering

    for idx, story_file in enumerate(story_files, start=1):
        try:
            with open(story_file, encoding="utf-8") as f:
                story_text = f.read().strip()
            story_dict[f"Story {idx}"] = story_text.replace("\u00a0", " ")  # Normalize spaces
        except Exception as e:
            print(f"❌ Error reading '{story_file}': {e}")
            exit(1)

    return story_dict


def generate_jsonl(
    story_folder: str | Path,
    question_path: str | Path,
    rubric_folder: str | Path,
    csv_path: str | Path,
    output_path: str | Path,
    output_format: str,
) -> str | Path:
    """
    Generates a JSONL file for fine-tuning based on multiple stories, a question file, and a rubric.

    - Supports multiple stories by dynamically reading all `.txt` files from `story_folder`.
    - Includes detailed scoring feedback or simplified feedback based on `output_format`.
    - Considers **grade level** to ensure appropriate expectations for student responses.
    - Adapts feedback to the **tested language** (English or Spanish).

    Returns:
        str: Path to the generated JSONL file.

    """
    # Load multiple stories dynamically
    story_dict = load_story_files(story_folder)
    question_text = load_text_file(question_path)
    rubric_dict = load_rubric_files(rubric_folder, output_format)  # Load rubric dynamically

    # Load CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        exit(1)

    # Convert dataset into chat-based format
    chat_jsonl_data = []

    for _, row in df.iterrows():
        system_message = {"role": "system", "content": "AI Grader: Evaluate student responses based on rubric."}

        # Extract additional context
        grade_level = row["Enrolled Grade Level"]  # Ensure this exists in the CSV
        tested_language = row["Tested Language"].strip().lower()  # Normalize language format

        # Language settings (English or Spanish)
        if tested_language == "spanish":
            language_instruction = (
                "El estudiante ha realizado la prueba en español. "
                "Proporcione la retroalimentación y la evaluación en español."
            )
        else:
            language_instruction = (
                "The student has taken the test in English. Provide feedback and evaluation in English."
            )

        # Structured prompt with grade-level and language context
        user_prompt = {
            "grade_level": f"Grade {grade_level}",
            "language": tested_language.capitalize(),
            "stories": story_dict,  # Dictionary of multiple stories
            "question": question_text,
            "rubric": rubric_dict,
            "student_response": row["Student Constructed Response"],
            "evaluation_guidance": (
                f"Analyze the student's response in a grade-appropriate manner. "
                f"Ensure feedback aligns with expectations for Grade {grade_level}. "
                f"{language_instruction}"
            ),
        }

        user_message = {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}

        # Format assistant response based on output_format
        if output_format == "extended":
            response_obj = {
                "Idea_Development_Score": str(row["Idea Development Score"]),
                "Idea_Development_Feedback": row["Idea Development Feedback"],
                "Language_Conventions_Score": str(row["Language Conventions Score"]),
                "Language_Conventions_Feedback": row["Language Conventions Feedback"],
            }
        elif output_format in ["item-specific", "short"]:
            response_obj = {
                "Score": str(row["Score"]),
                "Feedback": row["Feedback"],
            }
        else:
            print(f"❌ Error: Invalid output format '{output_format}'.")
            exit(1)

        # Modify the assistant response validation in generate_jsonl()
        validated_response = validate_response(json.dumps(response_obj), output_format)

        if not validated_response:
            print("⚠️ Skipping malformed response.")
            continue

        # Convert response to JSON string and append stop sequence
        assistant_response = {
            "role": "assistant",
            "content": json.dumps(validated_response.model_dump(), ensure_ascii=False) + " ###",
        }

        chat_jsonl_data.append({"messages": [system_message, user_message, assistant_response]})

    # Save JSONL file with proper encoding
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in chat_jsonl_data:
                clean_entry = json.dumps(entry, ensure_ascii=False).replace("\u00a0", " ")
                f.write(clean_entry + "\n")
        print(f"✅ JSONL file successfully generated: {output_path}")
    except Exception as e:
        print(f"❌ Error writing JSONL file: {e}")
        exit(1)

    return output_path
