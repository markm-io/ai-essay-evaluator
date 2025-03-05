import pandas as pd


def save_results(df, output_path):
    df.to_csv(output_path, index=False)


def merge_csv_files(file_paths, output_path):
    dfs = [pd.read_csv(file) for file in file_paths]
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_csv(output_path, index=False)
