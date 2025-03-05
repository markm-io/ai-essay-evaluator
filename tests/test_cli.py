import pytest
from typer.testing import CliRunner

from ai_essay_evaluator.cli import app
from ai_essay_evaluator.evaluator.cli import evaluator_app
from ai_essay_evaluator.trainer.cli import trainer_app


@pytest.fixture
def runner():
    return CliRunner()


def test_app_has_subcommands():
    """Test that the main app has the evaluator and trainer subcommands."""
    # Verify the subcommands are properly registered
    subcommands = {cmd.name: cmd for cmd in app.registered_groups}

    # Check if the grader and trainer subcommands exist
    assert "evaluator" in subcommands
    assert "trainer" in subcommands

    # Verify they are the correct app instances
    assert subcommands["evaluator"].typer_instance == evaluator_app
    assert subcommands["trainer"].typer_instance == trainer_app


def test_help_output(runner):
    """Test that the CLI shows help with expected subcommands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "evaluator" in result.stdout
    assert "trainer" in result.stdout
