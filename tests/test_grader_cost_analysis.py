from unittest.mock import Mock

import pytest

from ai_essay_evaluator.evaluator.cost_analysis import analyze_cost


class TestCostAnalysis:
    def test_analyze_cost_basic_calculation(self):
        # Create mock usage objects with the expected attributes
        usage1 = Mock(prompt_tokens=1000, completion_tokens=500, prompt_tokens_details=Mock(cached_tokens=200))

        usage2 = Mock(prompt_tokens=2000, completion_tokens=1000, prompt_tokens_details=Mock(cached_tokens=500))

        result = analyze_cost([usage1, usage2])

        # Assert the token counts are calculated correctly
        assert result["total_cached_tokens"] == 700
        assert result["total_prompt_tokens"] == 3000
        assert result["total_output_tokens"] == 1500
        assert result["total_uncached_tokens"] == 2300

        # Assert costs are calculated correctly
        assert pytest.approx(result["cost_uncached"]) == (2300 / 1_000_000) * 0.30
        assert pytest.approx(result["cost_cached"]) == (700 / 1_000_000) * 0.15
        assert pytest.approx(result["cost_output"]) == (1500 / 1_000_000) * 1.20
        assert (
            pytest.approx(result["total_cost"])
            == result["cost_uncached"] + result["cost_cached"] + result["cost_output"]
        )

    def test_analyze_cost_empty_input(self):
        result = analyze_cost([])

        assert result["total_cached_tokens"] == 0
        assert result["total_prompt_tokens"] == 0
        assert result["total_output_tokens"] == 0
        assert result["total_uncached_tokens"] == 0
        assert result["total_cost"] == 0

    def test_analyze_cost_real_example(self, capsys):
        # Test with values similar to those in the log file
        usage = Mock(prompt_tokens=3309, completion_tokens=2000, prompt_tokens_details=Mock(cached_tokens=3072))

        result = analyze_cost([usage])

        assert result["total_cached_tokens"] == 3072
        assert result["total_prompt_tokens"] == 3309
        assert result["total_output_tokens"] == 2000
        assert result["total_uncached_tokens"] == 237

        # Check that the function prints the expected cost
        captured = capsys.readouterr()
        expected_cost = (237 / 1_000_000) * 0.30 + (3072 / 1_000_000) * 0.15 + (2000 / 1_000_000) * 1.20
        assert f"Estimated Cost: ${expected_cost:.4f}" in captured.out
