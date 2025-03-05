import logging

import pandas as pd

from .cost_analysis import analyze_cost
from .file_handler import merge_csv_files, save_results
from .openai_client import process_with_openai
from .utils import read_text_files, validate_csv


async def process_csv(
    input_file,
    export_folder,
    file_name,
    scoring_format,
    openai_project,
    api_key,
    ai_model,
    log,
    cost_analysis,
    passes,
    merge_results,
    story_folder,
    rubric_folder,
    question_file,
):
    if log:
        logging.basicConfig(level=logging.INFO)

    export_folder.mkdir(parents=True, exist_ok=True)

    # Read and validate CSV
    df = pd.read_csv(input_file)
    validate_csv(df)

    # Read additional data
    stories = read_text_files(story_folder) if story_folder else {}
    rubrics = read_text_files(rubric_folder) if rubric_folder else {}
    question = question_file.read_text() if question_file else None

    cumulative_usage = []  # To accumulate usage details across passes
    results = []
    for i in range(1, passes + 1):
        output_path = export_folder / f"{file_name}_pass_{i}.csv"
        # process_with_openai now returns a tuple: (processed DataFrame, usage_list)
        processed_df, usage_list = await process_with_openai(
            df, ai_model, api_key, stories, rubrics, question, scoring_format, openai_project
        )
        save_results(processed_df, output_path)
        results.append(output_path)
        cumulative_usage.extend(usage_list)

    # Merge results if required
    if passes > 1 and merge_results:
        merged_path = export_folder / f"{file_name}_merged.csv"
        merge_csv_files(results, merged_path)

    if cost_analysis:
        cost_data = analyze_cost(cumulative_usage)

        # Save usage information to CSV if log is True
        if log:
            cost_df = pd.DataFrame([cost_data])
            cost_file_path = export_folder / f"{file_name}_cost_analysis.csv"
            cost_df.to_csv(cost_file_path, index=False)
            logging.info(f"Cost analysis saved to {cost_file_path}")
