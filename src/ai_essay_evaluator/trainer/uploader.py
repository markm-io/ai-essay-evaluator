import os
from typing import Optional

from openai import OpenAI


def upload_jsonl(jsonl_path: str, api_key: Optional[str] = None) -> str:
    """
    Upload JSONL file to OpenAI for fine-tuning.

    Args:
        jsonl_path: Path to the JSONL file to upload
        api_key: OpenAI API key

    Returns:
        str: The file ID of the uploaded file

    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") if api_key is None else api_key)

    try:
        if api_key is None and not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OpenAI API key is missing. Oh No!!!")
            exit(1)

        with open(jsonl_path, "rb") as f:
            response = client.files.create(file=f, purpose="fine-tune")
            file_id = response.id
            print(f"✅ File uploaded successfully! File ID: {file_id}")
            return file_id
    except Exception as e:
        print(f"❌ Error uploading JSONL file: {e}")
        exit(1)
