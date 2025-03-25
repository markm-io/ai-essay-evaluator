import asyncio
import time
from pathlib import Path

import typer

from .processor import process_csv

evaluator_app = typer.Typer(help="CLI for grading student responses.")


@evaluator_app.command()
def grader(
    project_folder: Path = typer.Option(None, help="Path to project folder containing all required files"),
    input_file: Path = typer.Option(None, help="Path to input CSV"),
    export_folder: Path = typer.Option(None, help="Folder to export results"),
    export_file_name: str = typer.Option(None, help="Base file name for output"),
    scoring_format: str = typer.Option(..., help="Scoring format: extended, item-specific, short"),
    story_folder: Path = typer.Option(None, help="Folder containing story text files"),
    rubric_folder: Path = typer.Option(None, help="Folder containing rubric text files"),
    question_file: Path = typer.Option(None, help="Path to question text file"),
    api_key: str = typer.Option(..., help="OpenAI API Key"),
    openai_project: str = typer.Option(None, help="OpenAI project ID"),
    ai_model: str = typer.Option(None, help="Custom AI model to use"),
    log: bool = typer.Option(True, help="Enable logging"),
    cost_analysis: bool = typer.Option(True, help="Perform cost analysis"),
    passes: int = typer.Option(None, help="Number of times to process the CSV"),
    merge_results: bool = typer.Option(True, help="Merge results if multiple passes"),
    show_progress: bool = typer.Option(True, help="Display progress during processing"),
    calculate_totals: bool = typer.Option(True, help="Calculate scoring totals for each student"),
):
    start_time = time.time()

    # If project folder is provided, validate and extract paths
    if project_folder:
        # Validate project structure
        if not project_folder.is_dir():
            typer.secho(f"Error: Project folder '{project_folder}' not found", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Setup rubric folder
        rubric_folder = project_folder / "rubric"
        if not rubric_folder.is_dir() or not any(rubric_folder.glob("*.txt")):
            typer.secho("Error: Rubric folder not found or contains no txt files", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Setup story folder
        story_folder = project_folder / "story"
        if not story_folder.is_dir() or not any(story_folder.glob("*.txt")):
            typer.secho("Error: Story folder not found or contains no txt files", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Setup question file
        question_file = project_folder / "question.txt"
        if not question_file.exists():
            typer.secho("Error: question.txt not found in project folder", fg=typer.colors.RED)
            raise typer.Exit(1)

        # Setup input file if not explicitly provided
        if input_file is None:
            csv_files = list(project_folder.glob("*.csv"))
            if csv_files:
                input_file = csv_files[0]
                typer.echo(f"Using input file: {input_file}")
            else:
                typer.secho("Error: No CSV input file found in project folder", fg=typer.colors.RED)
                raise typer.Exit(1)

        # Set default export folder if not provided
        if export_folder is None:
            export_folder = project_folder / "output"
            export_folder.mkdir(exist_ok=True)

        # Set default export filename if not provided
        if export_file_name is None:
            export_file_name = f"results_{time.strftime('%Y%m%d_%H%M%S')}"

    else:
        # Validate required parameters when not using project folder
        if not input_file:
            typer.secho("Error: --input-file is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not export_folder:
            typer.secho("Error: --export-folder is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not export_file_name:
            typer.secho("Error: --export-file-name is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not story_folder:
            typer.secho("Error: --story-folder is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not rubric_folder:
            typer.secho("Error: --rubric-folder is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)
        if not question_file:
            typer.secho("Error: --question-file is required when not using --project-folder", fg=typer.colors.RED)
            raise typer.Exit(1)

    # Determine the AI model if not provided
    if ai_model is None:
        model_mapping = {
            "extended": "ft:gpt-4o-mini-2024-07-18:securehst::B6YDFKyO",
            "item-specific": "ft:gpt-4o-mini-2024-07-18:securehst::B72LJHWZ",
            "short": "ft:gpt-4o-mini-2024-07-18:securehst::B79Kzt5H",
        }
        ai_model = model_mapping.get(scoring_format)

    typer.echo(f"Starting essay evaluation with {scoring_format} format...")

    asyncio.run(
        process_csv(
            input_file,
            export_folder,
            export_file_name,
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
            show_progress,
            calculate_totals,
        )
    )

    duration = time.time() - start_time
    typer.echo(f"Processing completed in {duration:.2f} seconds.")
