import json


def validate_jsonl(jsonl_path: str, scoring_format: str) -> bool:
    """
    Validate JSONL file format for OpenAI fine-tuning.

    Args:
        jsonl_path: Path to the JSONL file to validate
        scoring_format: Scoring format for the JSONL file

    Returns:
        bool: True if file is valid, exits with code 1 otherwise

    """
    try:
        with open(jsonl_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading JSONL file: {e}")
        exit(1)

    for i, line in enumerate(lines):
        try:
            entry = json.loads(line.strip())

            # Ensure required fields exist
            if "messages" not in entry:
                raise ValueError("Missing 'messages' key")

            if not isinstance(entry["messages"], list):
                raise ValueError("'messages' should be a list")

            # Check role structure
            expected_roles = ["system", "user", "assistant"]
            roles = [msg.get("role") for msg in entry["messages"]]

            if roles != expected_roles:
                raise ValueError(f"Incorrect roles sequence in entry {i + 1}: {roles}")
            if scoring_format == "extended":
                required_fields = ["Idea_Development_Score", "Language_Conventions_Score"]
            else:  # short or item-specific
                required_fields = ["Score"]

            # Check assistant's response format
            assistant_msg = entry["messages"][-1]["content"]

            if not all(key in assistant_msg for key in required_fields):
                raise ValueError(f"Missing expected score fields for {scoring_format} format in assistant response")

        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON format on line {i + 1}")
            exit(1)
        except ValueError as ve:
            print(f"❌ Error: {ve} (line {i + 1})")
            exit(1)

    print(f"✅ JSONL file '{jsonl_path}' is valid for fine-tuning!")
    return True
