"""Make the CLI runnable using python -m ai_essay_grader."""

from typer import Typer

from .evaluator.cli import evaluator_app
from .trainer.cli import trainer_app

app = Typer()

app.add_typer(evaluator_app, name="evaluator")
app.add_typer(trainer_app, name="trainer")
