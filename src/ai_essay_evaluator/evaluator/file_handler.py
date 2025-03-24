import unicodedata

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


def save_results(df, output_path, calculate_totals=True):
    if calculate_totals:
        # Determine which columns to use for score calculation based on column names
        if "idea_development_score" in df.columns and "language_conventions_score" in df.columns:
            # Extended format
            score_columns = ["idea_development_score", "language_conventions_score"]
            # Convert columns to numeric and fill NaN with 0
            for col in score_columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            # Calculate total score
            df["total_score"] = df[score_columns].sum(axis=1)
        elif "score" in df.columns:
            # Item-specific or short format
            df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
            df["total_score"] = df["score"]

    # Fix encoding for text columns before saving
    text_columns = ["feedback", "idea_development_feedback", "language_conventions_feedback"]
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # For all other string columns, also normalize text
    for col in df.columns:
        if df[col].dtype == "object" and col not in text_columns:
            df[col] = df[col].apply(normalize_text)

    # Explicitly set encoding to utf-8 when writing to CSV
    df.to_csv(output_path, index=False, encoding="utf-8")


def merge_csv_files(file_paths, output_path, scoring_format, calculate_totals=True):
    """
    Merge multiple CSV files from different passes while preserving pass information.
    Uses the total_score from each pass and calculates a new merged total.

    Args:
        file_paths: List of Paths to CSV files to merge
        output_path: Path to save the merged output
        scoring_format: The scoring format (extended, item-specific, short)
        calculate_totals: Whether to calculate total scores
    """
    # Determine which columns to extract based on scoring format
    if scoring_format == "extended":
        score_columns = [
            "idea_development_score",
            "idea_development_feedback",
            "language_conventions_score",
            "language_conventions_feedback",
        ]
    else:  # For item-specific or short
        score_columns = ["score", "feedback"]

    # Function to read CSV with proper handling of encodings
    def read_csv_with_encoding(file_path_):
        try:
            # Try UTF-8 first
            df = pd.read_csv(file_path_, encoding="utf-8")
        except UnicodeDecodeError:
            # If that fails, try with ISO-8859-1 (Latin-1)
            df = pd.read_csv(file_path_, encoding="iso-8859-1")

        # Apply text normalization to all string columns
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(normalize_text)

        return df

    # Base dataframe - use the first file to get all common columns
    base_df = read_csv_with_encoding(file_paths[0])

    # Track total score columns for calculation (but won't be kept in final output)
    pass_total_scores = []

    # Extract pass number from filename
    for file_path in file_paths:
        file_name = file_path.name
        # Extract pass number (assumes format with "_pass_N.csv")
        if "_pass_" in file_name:
            pass_num = file_name.split("_pass_")[1].split(".")[0]

            # Read the file with proper encoding
            pass_df = read_csv_with_encoding(file_path)

            # Process as before...
            if file_path != file_paths[0]:
                merge_cols = ["testentryid", "TeacherName"]
                temp_cols = merge_cols + [col for col in score_columns if col in pass_df.columns]
                temp_df = pass_df[temp_cols].copy()

                rename_dict = {}
                for col in score_columns:
                    if col in pass_df.columns:
                        rename_dict[col] = f"{col}_pass{pass_num}"

                temp_df = temp_df.rename(columns=rename_dict)
                base_df = pd.merge(base_df, temp_df, on=merge_cols, how="left")

                if "total_score" in pass_df.columns:
                    pass_total_scores.append(pd.to_numeric(pass_df["total_score"], errors="coerce").fillna(0))
            else:
                rename_dict = {}
                for col in score_columns:
                    if col in pass_df.columns:
                        rename_dict[col] = f"{col}_pass{pass_num}"

                base_df = base_df.rename(columns=rename_dict)

                if "total_score" in pass_df.columns:
                    pass_total_scores.append(pd.to_numeric(pass_df["total_score"], errors="coerce").fillna(0))

    # Calculate merged total score based on individual pass total scores
    if calculate_totals and pass_total_scores:
        total_scores_df = pd.DataFrame(index=base_df.index)

        for i, scores in enumerate(pass_total_scores):
            if len(scores) == len(base_df):
                total_scores_df[f"pass_{i + 1}"] = scores.values

        base_df["total_score"] = total_scores_df.sum(axis=1)

    # Normalize all text columns before saving
    for col in base_df.columns:
        if base_df[col].dtype == "object":
            base_df[col] = base_df[col].apply(normalize_text)

    # Save the merged dataframe with explicit utf-8 encoding
    base_df.to_csv(output_path, index=False, encoding="utf-8")

    return base_df
