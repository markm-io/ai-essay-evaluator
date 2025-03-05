import typer

from . import create_fine_tuning_job, generate_jsonl, merge_jsonl_files, upload_jsonl, validate_jsonl

trainer_app = typer.Typer(help="Generate, validate, merge, upload, and fine-tune JSONL files.")


@trainer_app.command(name="generate")
def generate(
    story_folder: str = typer.Option(..., help="Path to the folder to the story.txt file"),
    question: str = typer.Option(..., help="Path to the question.txt file"),
    rubric: str = typer.Option(..., help="Path to the rubric.txt file"),
    csv: str = typer.Option(..., help="Path to the model_testing.csv file"),
    output: str = typer.Option("fine_tuning.jsonl", help="Output JSONL file name"),
    scoring_format: str = typer.Option(..., help="Output format: extended, item-specific, or short."),
) -> None:
    """Generate JSONL file from input files."""
    if scoring_format not in ["extended", "item-specific", "short"]:
        raise typer.BadParameter("Format must be 'extended', 'item-specific', or 'short'")
    jsonl_file = generate_jsonl(story_folder, question, rubric, csv, output, scoring_format)
    typer.echo(f"✅ JSONL file generated: {jsonl_file}")


@trainer_app.command(name="validate")
def validate(
    file: str = typer.Option(..., help="Path to the JSONL file to validate"),
    scoring_format: str = typer.Option("extended", help="Scoring format: extended, item-specific, or short."),
) -> None:
    """Validate a JSONL file."""
    if validate_jsonl(file, scoring_format):
        typer.echo("✅ JSONL file is valid!")


@trainer_app.command(name="merge")
def merge(
    folder: str = typer.Option(..., help="Path to the folder containing JSONL files"),
    output: str = typer.Option("merged_fine_tuning.jsonl", help="Output merged JSONL file name"),
) -> None:
    """Merge all JSONL files in a folder into one."""
    merged_file = merge_jsonl_files(folder, output)
    typer.echo(f"✅ Merged JSONL file created: {merged_file}")


@trainer_app.command(name="upload")
def upload(
    file: str = typer.Option(..., help="Path to the JSONL file to upload"),
    api_key: str | None = typer.Option(None, help="OpenAI API key"),
) -> None:
    """Upload a validated JSONL file to OpenAI."""
    file_id = upload_jsonl(file, api_key)
    typer.echo(f"✅ JSONL file uploaded! File ID: {file_id}")


@trainer_app.command(name="fine-tune")
def fine_tune(
    file: str | None = typer.Option(None, help="Path to a validated JSONL file for uploading & fine-tuning"),
    file_id: str | None = typer.Option(None, help="Existing file ID to use for fine-tuning"),
    api_key: str | None = typer.Option(None, help="OpenAI API key"),
    scoring_format: str = typer.Option(None, help="Scoring format: extended, item-specific, or short."),
) -> None:
    """Start a fine-tuning job using OpenAI."""
    if file:
        if validate_jsonl(file, scoring_format):
            file_id = upload_jsonl(file, api_key)
            create_fine_tuning_job(file_id, api_key)
    elif file_id:
        create_fine_tuning_job(file_id, api_key)
    else:
        typer.echo("❌ You must provide either --file or --file-id", err=True)
