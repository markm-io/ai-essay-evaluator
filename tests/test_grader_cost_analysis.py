import sys
from io import StringIO
from types import SimpleNamespace

import pytest

from ai_essay_evaluator.evaluator.cost_analysis import analyze_cost


class CaptureOutput:
    """Helper class to capture stdout for testing."""

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


def create_usage_object(prompt_tokens, completion_tokens, cached_tokens=0):
    """Create a mock usage object similar to what the analyze_cost function expects."""
    usage = SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

    if cached_tokens > 0:
        usage.prompt_tokens_details = SimpleNamespace(cached_tokens=cached_tokens)

    return usage


def test_analyze_cost_basic():
    """Test basic cost analysis with multiple usage records."""
    # Create sample usage data
    usages = [create_usage_object(1000, 200, 300), create_usage_object(2000, 400, 600)]

    # Calculate expected values
    total_prompt_tokens = 3000
    total_cached_tokens = 900
    total_output_tokens = 600
    total_uncached_tokens = 2100

    cost_uncached = (total_uncached_tokens / 1_000_000) * 0.30
    cost_cached = (total_cached_tokens / 1_000_000) * 0.15
    cost_output = (total_output_tokens / 1_000_000) * 1.20
    total_cost = cost_uncached + cost_cached + cost_output

    # Capture printed output
    with CaptureOutput() as output:
        result = analyze_cost(usages)

    # Verify printed output
    assert output.getvalue().strip() == f"Estimated Cost: ${total_cost:.4f}"

    # Verify returned dictionary values
    assert result["total_cached_tokens"] == total_cached_tokens
    assert result["total_prompt_tokens"] == total_prompt_tokens
    assert result["total_output_tokens"] == total_output_tokens
    assert result["total_uncached_tokens"] == total_uncached_tokens
    assert result["cost_uncached"] == pytest.approx(cost_uncached)
    assert result["cost_cached"] == pytest.approx(cost_cached)
    assert result["cost_output"] == pytest.approx(cost_output)
    assert result["total_cost"] == pytest.approx(total_cost)


def test_analyze_cost_no_cached_tokens():
    """Test cost analysis when no cached tokens are present."""
    # Create sample usage without cached tokens
    usages = [create_usage_object(1000, 200), create_usage_object(2000, 400)]

    total_prompt_tokens = 3000
    total_output_tokens = 600
    total_uncached_tokens = 3000

    with CaptureOutput():
        result = analyze_cost(usages)

    assert result["total_cached_tokens"] == 0
    assert result["total_uncached_tokens"] == total_prompt_tokens
    assert result["total_cost"] == pytest.approx(
        (total_uncached_tokens / 1_000_000) * 0.30 + (total_output_tokens / 1_000_000) * 1.20
    )


def test_analyze_cost_empty_list():
    """Test cost analysis with an empty list of usages."""
    with CaptureOutput() as output:
        result = analyze_cost([])

    assert output.getvalue().strip() == "Estimated Cost: $0.0000"
    assert result["total_cached_tokens"] == 0
    assert result["total_prompt_tokens"] == 0
    assert result["total_output_tokens"] == 0
    assert result["total_cost"] == 0


def test_analyze_cost_real_example():
    """Test with values matching the example from results_cost_analysis.csv."""
    # From the CSV, we have:
    # total_cached_tokens: 29184, total_prompt_tokens: 47342, total_output_tokens: 5512

    usage = create_usage_object(prompt_tokens=47342, completion_tokens=5512, cached_tokens=29184)

    with CaptureOutput():
        result = analyze_cost([usage])

    # Verify against the CSV values
    assert result["total_cached_tokens"] == 29184
    assert result["total_prompt_tokens"] == 47342
    assert result["total_output_tokens"] == 5512
    assert result["total_uncached_tokens"] == 18158
    assert round(result["total_cost"], 7) == pytest.approx(0.0164394, abs=1e-6)
