import unicodedata
from pathlib import Path

import ftfy
import pandas as pd


def normalize_text(text):
    """
    Normalize text to handle encoding issues with special characters.
    """
    if not isinstance(text, str):
        return text

    # Replace specific problematic character sequences
    # Replace specific problematic character sequences
    replacements = [
        ("\u201a\u00c4\u00f4", "'"),  # Smart apostrophe sequence
        ("\u2019", "'"),  # Right single quotation mark
        ("\u2018", "'"),  # Left single quotation mark
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Normalize other Unicode characters to their closest ASCII equivalent
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    return text


def normalize_response_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize text columns in a DataFrame.
    """
    df = df.map(lambda x: ftfy.fix_text(x) if isinstance(x, str) else x)
    return df


def validate_csv(df: pd.DataFrame) -> None:
    required_columns = {"Local Student ID", "Enrolled Grade Level", "Tested Language"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")


def read_text_files(folder: Path) -> dict[str, str]:
    return {
        file.name: normalize_text(file.read_text(encoding="utf-8").strip().replace("\u00a0", " "))
        for file in folder.glob("*.txt")
    }
