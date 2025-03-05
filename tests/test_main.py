import re
import subprocess
import sys
from pathlib import Path


def test_main_module_execution():
    """Test that the __main__.py module executes correctly with the expected program name."""
    # Get the path to the package
    package_dir = Path(__file__).parent.parent / "src"

    # Run the module as a script with --help to see output
    result = subprocess.run(
        [sys.executable, "-m", "ai_essay_evaluator", "--help"],
        cwd=package_dir.parent,  # Run from parent of src directory
        capture_output=True,
        text=True,
    )

    # Verify the command executed successfully
    assert result.returncode == 0

    # Strip ANSI escape codes for text comparison
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_output = ansi_escape.sub("", result.stdout)

    # Verify the program name is correctly set
    assert "Usage: ai-essay-grader" in clean_output

    # Verify subcommands are present
    assert "grader" in clean_output
    assert "trainer" in clean_output
