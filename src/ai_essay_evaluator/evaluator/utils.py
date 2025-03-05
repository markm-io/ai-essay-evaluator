from pathlib import Path

import pandas as pd


def validate_csv(df: pd.DataFrame) -> None:
    required_columns = {"Local Student ID", "Enrolled Grade Level", "Tested Language"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")


def read_text_files(folder: Path) -> dict[str, str]:
    return {file.name: file.read_text(encoding="utf-8").strip().replace("\u00a0", " ") for file in folder.glob("*.txt")}
