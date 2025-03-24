import pandas as pd


def save_results(df, output_path):
    df.to_csv(output_path, index=False)


def merge_csv_files(file_paths, output_path, scoring_format):
    """
    Merge multiple CSV files from different passes while preserving pass information.

    Merges on 'Local Student ID' and 'TeacherName', and preserves scoring columns
    from each pass with appropriate suffixes.

    Args:
        file_paths: List of Paths to CSV files to merge
        output_path: Path to save the merged output
        scoring_format: The scoring format (extended, item-specific, short)
    """
    # Determine which columns to extract based on scoring format
    if scoring_format == "extended":
        score_columns = [
            "Tested Language",
            "idea_development_score",
            "idea_development_feedback",
            "language_conventions_score",
            "language_conventions_feedback",
        ]
    else:  # For item-specific or short
        score_columns = ["Tested Language", "score", "feedback"]

    # If scoring_format is None, try to detect from the first file
    if scoring_format is None:
        first_df = pd.read_csv(file_paths[0])
        if "idea_development_score" in first_df.columns:
            score_columns = [
                "idea_development_score",
                "idea_development_feedback",
                "language_conventions_score",
                "language_conventions_feedback",
            ]
        else:
            score_columns = ["score", "feedback"]

    # Base dataframe - use the first file to get all common columns
    base_df = pd.read_csv(file_paths[0])

    # Extract pass number from filename
    for file_path in file_paths:
        file_name = file_path.name
        # Extract pass number (assumes format with "_pass_N.csv")
        if "_pass_" in file_name:
            pass_num = file_name.split("_pass_")[1].split(".")[0]

            # Read the file
            pass_df = pd.read_csv(file_path)

            # For files after the first one, only merge the score columns
            if file_path != file_paths[0]:
                # Create a temporary dataframe with just the ID and score columns
                # Include both Local Student ID and TeacherName for merging
                merge_cols = ["Local Student ID", "TeacherName"]
                temp_df = pass_df[merge_cols + [col for col in score_columns if col in pass_df.columns]].copy()

                # Rename the score columns to include the pass number
                rename_dict = {col: f"{col}_pass{pass_num}" for col in score_columns if col in pass_df.columns}
                temp_df = temp_df.rename(columns=rename_dict)

                # Merge with the base dataframe on Student ID and TeacherName
                base_df = pd.merge(base_df, temp_df, on=merge_cols, how="left")
            else:
                # For the first file, rename columns to include pass number
                for col in score_columns:
                    if col in pass_df.columns:
                        base_df = base_df.rename(columns={col: f"{col}_pass{pass_num}"})

    # Save the merged dataframe
    base_df.to_csv(output_path, index=False)

    return base_df
