import json
import os
from pathlib import Path


def merge_jsonl_files(input_folder: str | Path, output_file: str | Path) -> str:
    """
    Merges all JSONL files in a folder into one JSONL file.

    Args:
        input_folder: Directory containing JSONL files to merge
        output_file: Path where the merged JSONL file will be saved

    Returns:
        str: Path to the merged output file

    """
    jsonl_files = [f for f in os.listdir(input_folder) if f.endswith(".jsonl")]

    if not jsonl_files:
        print(f"❌ No JSONL files found in '{input_folder}'.")
        exit(1)

    print(f"🔍 Merging {len(jsonl_files)} JSONL files...")

    with open(output_file, "w", encoding="utf-8") as outfile:
        for jsonl_file in jsonl_files:
            file_path = os.path.join(input_folder, jsonl_file)
            with open(file_path, encoding="utf-8") as infile:
                for line in infile:
                    json.loads(line.strip())  # Validate JSON
                    outfile.write(line)

    print(f"✅ Merged JSONL saved to: {output_file}")
    return str(output_file)
