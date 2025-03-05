import subprocess
import sys
from pathlib import Path


def test_main_module_execution():
    """Test that the __main__.py module executes correctly with the expected program name."""
    # Get the path to the package
    package_dir = Path(__file__).parent.parent / "src"

    # Run the module as a script with --help to see output
    # This avoids having to mock sys.argv
    result = subprocess.run(
        [sys.executable, "-m", "ai_essay_evaluator", "--help"],
        cwd=package_dir.parent,  # Run from parent of src directory
        capture_output=True,
        text=True,
    )

    # Verify the command executed successfully
    assert result.returncode == 0

    # Verify the program name is correctly set
    assert "Usage: ai-essay-grader" in result.stdout

    # Verify subcommands are present (as we know from other tests they should exist)
    assert "grader" in result.stdout
    assert "trainer" in result.stdout
