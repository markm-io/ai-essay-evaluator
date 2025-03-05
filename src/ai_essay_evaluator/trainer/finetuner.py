import os
from typing import Optional

from openai import OpenAI


def create_fine_tuning_job(file_id: str, api_key: Optional[str] = None, model: str = "gpt-4o-mini-2024-07-18") -> str:
    """Creates a fine-tuning job with OpenAI using the uploaded JSONL file."""
    try:
        if api_key is None and not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OpenAI API key is missing.")
            exit(1)

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") if api_key is None else api_key)
        response = client.fine_tuning.jobs.create(training_file=file_id, model=model)
        job_id = response.id
        print(f"🚀 Fine-tuning job started! Job ID: {job_id}")
        return job_id
    except Exception as e:
        print(f"❌ Error creating fine-tuning job: {e}")
        exit(1)
