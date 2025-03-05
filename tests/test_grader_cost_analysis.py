import sys
from io import StringIO

import pandas as pd

from ai_essay_evaluator.evaluator.cost_analysis import analyze_cost


class CaptureOutput:
    def __init__(self):
        self.old_stdout = None
        self.captured_output = None

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        return self.captured_output

    def __exit__(self, *args):
        sys.stdout = self.old_stdout


def test_analyze_cost():
    # Create a sample DataFrame
    df = pd.DataFrame({"essay_id": [1, 2, 3, 4, 5], "content": ["text1", "text2", "text3", "text4", "text5"]})

    # Set number of passes
    passes = 2

    # Calculate expected costs manually
    input_tokens = len(df) * passes * 100
    uncached_cost = (input_tokens / 1_000_000) * 0.30
    cached_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (len(df) * passes * 50 / 1_000_000) * 1.2
    expected_total = uncached_cost + cached_cost + output_cost
    expected_output = f"Estimated Cost: ${expected_total:.4f}"

    # Capture the printed output
    with CaptureOutput() as output:
        analyze_cost(df, passes)

    # Assert the captured output matches the expected output
    assert output.getvalue().strip() == expected_output


def test_analyze_cost_zero_data():
    # Test with empty DataFrame
    df = pd.DataFrame()
    passes = 5

    # Calculate expected cost (should be zero)
    expected_output = "Estimated Cost: $0.0000"

    # Capture the printed output
    with CaptureOutput() as output:
        analyze_cost(df, passes)

    # Assert the captured output matches the expected output
    assert output.getvalue().strip() == expected_output


def test_analyze_cost_different_parameters():
    # Test with different parameters
    df = pd.DataFrame({"essay_id": [1, 2, 3]})
    passes = 10

    # Calculate expected costs manually
    input_tokens = len(df) * passes * 100
    uncached_cost = (input_tokens / 1_000_000) * 0.30
    cached_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (len(df) * passes * 50 / 1_000_000) * 1.2
    expected_total = uncached_cost + cached_cost + output_cost
    expected_output = f"Estimated Cost: ${expected_total:.4f}"

    # Capture the printed output
    with CaptureOutput() as output:
        analyze_cost(df, passes)

    # Assert the captured output matches the expected output
    assert output.getvalue().strip() == expected_output
