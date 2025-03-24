import logging
import os
import time
from datetime import datetime

import pandas as pd
import typer

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
    start_time,
    show_progress=True,
    calculate_totals=True,
):
    if log:
        # Configure logging to file with timestamp
        log_directory = "logs"
        os.makedirs(log_directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_directory, f"ai_evaluator_{timestamp}.log")

        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
            ],
        )

        # Set httpx logger to WARNING level to suppress INFO messages
        logging.getLogger("httpx").setLevel(logging.WARNING)
        # Set OpenAI logger to INFO to capture relevant OpenAI errors
        logging.getLogger("openai").setLevel(logging.INFO)

    # Get logger for this module
    logger = logging.getLogger(__name__)

    export_folder.mkdir(parents=True, exist_ok=True)

    # Read and validate CSV
    df = pd.read_csv(input_file)
    validate_csv(df)
    total_rows = len(df)

    # Read additional data
    stories = read_text_files(story_folder) if story_folder else {}
    rubrics = read_text_files(rubric_folder) if rubric_folder else {}
    question = question_file.read_text() if question_file else None

    cumulative_usage = []  # To accumulate usage details across passes
    results = []

    for i in range(1, passes + 1):
        if passes > 1:
            typer.echo(f"\nProcessing pass {i} of {passes}...")

        output_path = export_folder / f"{file_name}_pass_{i}.csv"

        try:
            # Create a progress bar if show_progress is True
            if show_progress:
                with typer.progressbar(length=total_rows, label="Evaluating essays") as progress:
                    # Define a callback for updating progress
                    processed_count = 0

                    async def progress_callback():
                        nonlocal processed_count
                        processed_count += 1
                        progress.update(1)
                        if log and processed_count % 10 == 0:  # Log every 10 essays
                            logger.info(f"Processed {processed_count}/{total_rows} essays")

                    # Process with OpenAI with progress tracking
                    processed_df, usage_list = await process_with_openai(
                        df,
                        ai_model,
                        api_key,
                        stories,
                        rubrics,
                        question,
                        scoring_format,
                        openai_project,
                        progress_callback,
                    )
            else:
                # Process without progress tracking
                processed_df, usage_list = await process_with_openai(
                    df, ai_model, api_key, stories, rubrics, question, scoring_format, openai_project
                )
        except Exception as e:
            logger.error(f"Error processing with OpenAI: {e!s}", exc_info=True)
            raise

        save_results(processed_df, output_path, calculate_totals)
        results.append(output_path)
        cumulative_usage.extend(usage_list)

    # Merge results if required
    if passes > 1 and merge_results:
        merged_path = export_folder / f"{file_name}_merged.csv"
        merge_csv_files(results, merged_path, scoring_format, calculate_totals)
        if log:
            logger.info(f"Results merged into {merged_path}")

    if cost_analysis:
        duration = time.time() - start_time
        cost_data = analyze_cost(cumulative_usage)
        # Add duration to cost_data dictionary
        cost_data["duration_seconds"] = duration

        # Save usage information to CSV if log is True
        if log:
            cost_df = pd.DataFrame([cost_data])
            cost_file_path = export_folder / f"{file_name}_cost_analysis.csv"
            cost_df.to_csv(cost_file_path, index=False)
            logger.info(f"Cost analysis saved to {cost_file_path}")

            # Display cost summary
            typer.echo(f"\nProcessed {total_rows} essays in {duration:.2f} seconds")
            typer.echo(
                f"Total tokens: {cost_data.get('total_cached_tokens', 0) + cost_data.get('total_uncached_tokens', 0):,}"
            )
            typer.echo(f"Estimated cost: ${cost_data.get('total_cost', 0):.4f}")
