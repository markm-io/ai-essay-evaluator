from unittest.mock import Mock

import pytest

from ai_essay_evaluator.evaluator.cost_analysis import MODEL_PRICING, ModelPricing, analyze_cost, get_model_pricing


class TestCostAnalysis:
    def test_analyze_cost_basic_calculation_gpt4o_mini(self):
        # Create mock usage objects with the expected attributes
        usage1 = Mock(prompt_tokens=1000, completion_tokens=500, prompt_tokens_details=Mock(cached_tokens=200))

        usage2 = Mock(prompt_tokens=2000, completion_tokens=1000, prompt_tokens_details=Mock(cached_tokens=500))

        result = analyze_cost([usage1, usage2], model="gpt-4o-mini")

        # Assert the token counts are calculated correctly
        assert result["total_cached_tokens"] == 700
        assert result["total_prompt_tokens"] == 3000
        assert result["total_output_tokens"] == 1500
        assert result["total_uncached_tokens"] == 2300
        assert result["model"] == "gpt-4o-mini"

        # gpt-4o-mini pricing: $0.150/1M input, $0.075/1M cached, $0.600/1M output
        assert pytest.approx(result["cost_uncached"]) == (2300 / 1_000_000) * 0.150
        assert pytest.approx(result["cost_cached"]) == (700 / 1_000_000) * 0.075
        assert pytest.approx(result["cost_output"]) == (1500 / 1_000_000) * 0.600
        assert (
            pytest.approx(result["total_cost"])
            == result["cost_uncached"] + result["cost_cached"] + result["cost_output"]
        )

    def test_analyze_cost_basic_calculation_gpt4o(self):
        # Create mock usage objects for gpt-4o
        usage1 = Mock(prompt_tokens=1000, completion_tokens=500, prompt_tokens_details=Mock(cached_tokens=200))

        usage2 = Mock(prompt_tokens=2000, completion_tokens=1000, prompt_tokens_details=Mock(cached_tokens=500))

        result = analyze_cost([usage1, usage2], model="gpt-4o")

        # Assert the token counts are calculated correctly
        assert result["total_cached_tokens"] == 700
        assert result["total_prompt_tokens"] == 3000
        assert result["total_output_tokens"] == 1500
        assert result["total_uncached_tokens"] == 2300
        assert result["model"] == "gpt-4o"

        # gpt-4o pricing: $2.50/1M input, $1.25/1M cached, $10.00/1M output
        assert pytest.approx(result["cost_uncached"]) == (2300 / 1_000_000) * 2.50
        assert pytest.approx(result["cost_cached"]) == (700 / 1_000_000) * 1.25
        assert pytest.approx(result["cost_output"]) == (1500 / 1_000_000) * 10.00
        assert (
            pytest.approx(result["total_cost"])
            == result["cost_uncached"] + result["cost_cached"] + result["cost_output"]
        )

    def test_analyze_cost_empty_input(self):
        result = analyze_cost([], model="gpt-4o-mini")

        assert result["total_cached_tokens"] == 0
        assert result["total_prompt_tokens"] == 0
        assert result["total_output_tokens"] == 0
        assert result["total_uncached_tokens"] == 0
        assert result["total_cost"] == 0
        assert result["model"] == "gpt-4o-mini"

    def test_analyze_cost_real_example_gpt4o_mini(self, capsys):
        # Test with values similar to those in the log file
        usage = Mock(prompt_tokens=3309, completion_tokens=2000, prompt_tokens_details=Mock(cached_tokens=3072))

        result = analyze_cost([usage], model="gpt-4o-mini")

        assert result["total_cached_tokens"] == 3072
        assert result["total_prompt_tokens"] == 3309
        assert result["total_output_tokens"] == 2000
        assert result["total_uncached_tokens"] == 237
        assert result["model"] == "gpt-4o-mini"

        # Check that the function prints the expected cost
        captured = capsys.readouterr()
        # gpt-4o-mini pricing: $0.150/1M input, $0.075/1M cached, $0.600/1M output
        expected_cost = (237 / 1_000_000) * 0.150 + (3072 / 1_000_000) * 0.075 + (2000 / 1_000_000) * 0.600
        assert f"Estimated Cost: ${expected_cost:.4f}" in captured.out

    def test_analyze_cost_default_model(self):
        # Test that default model is gpt-4o-mini
        usage = Mock(prompt_tokens=1000, completion_tokens=500, prompt_tokens_details=Mock(cached_tokens=200))

        result = analyze_cost([usage])

        assert result["model"] == "gpt-4o-mini"

    def test_analyze_cost_no_cached_tokens(self):
        # Test handling of usage without cached tokens
        usage = Mock(prompt_tokens=1000, completion_tokens=500)
        usage.prompt_tokens_details = Mock(spec=[])  # No cached_tokens attribute

        result = analyze_cost([usage], model="gpt-4o-mini")

        assert result["total_cached_tokens"] == 0
        assert result["total_uncached_tokens"] == 1000

    def test_get_model_pricing(self):
        # Test getting pricing for known models
        gpt4o_pricing = get_model_pricing("gpt-4o")
        assert isinstance(gpt4o_pricing, ModelPricing)
        assert gpt4o_pricing.input_price == 2.50
        assert gpt4o_pricing.cached_input_price == 1.25
        assert gpt4o_pricing.output_price == 10.00

        gpt4o_mini_pricing = get_model_pricing("gpt-4o-mini")
        assert gpt4o_mini_pricing.input_price == 0.150
        assert gpt4o_mini_pricing.cached_input_price == 0.075
        assert gpt4o_mini_pricing.output_price == 0.600

    def test_get_model_pricing_unknown_model(self):
        # Test that unknown model raises ValueError
        with pytest.raises(ValueError, match="Model 'unknown-model' not found"):
            get_model_pricing("unknown-model")

    def test_model_pricing_registry(self):
        # Verify all expected models are in registry
        expected_models = [
            "gpt-4o",
            "gpt-4o-2024-11-20",
            "gpt-4o-2024-08-06",
            "gpt-4o-2024-05-13",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            "o1-preview",
            "o1-preview-2024-09-12",
            "o1-mini",
            "o1-mini-2024-09-12",
        ]

        for model in expected_models:
            assert model in MODEL_PRICING
            pricing = MODEL_PRICING[model]
            assert isinstance(pricing, ModelPricing)
            assert pricing.input_price > 0
            assert pricing.cached_input_price > 0
            assert pricing.output_price > 0

    def test_analyze_cost_invalid_model(self):
        # Test that analyze_cost raises error for invalid model
        usage = Mock(prompt_tokens=1000, completion_tokens=500, prompt_tokens_details=Mock(cached_tokens=200))

        with pytest.raises(ValueError, match="not found in pricing registry"):
            analyze_cost([usage], model="invalid-model")
