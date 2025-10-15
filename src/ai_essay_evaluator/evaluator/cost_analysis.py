# cost_analysis.py

from dataclasses import dataclass


@dataclass
class ModelPricing:
    """Pricing structure for OpenAI models per 1M tokens."""

    input_price: float  # Price per 1M input tokens (uncached)
    cached_input_price: float  # Price per 1M cached input tokens
    output_price: float  # Price per 1M output tokens


# Pricing registry for different OpenAI models
# Prices are per 1,000,000 tokens
MODEL_PRICING = {
    "gpt-4o": ModelPricing(input_price=2.50, cached_input_price=1.25, output_price=10.00),
    "gpt-4o-2024-11-20": ModelPricing(input_price=2.50, cached_input_price=1.25, output_price=10.00),
    "gpt-4o-2024-08-06": ModelPricing(input_price=2.50, cached_input_price=1.25, output_price=10.00),
    "gpt-4o-2024-05-13": ModelPricing(input_price=5.00, cached_input_price=2.50, output_price=15.00),
    "gpt-4o-mini": ModelPricing(input_price=0.150, cached_input_price=0.075, output_price=0.600),
    "gpt-4o-mini-2024-07-18": ModelPricing(input_price=0.150, cached_input_price=0.075, output_price=0.600),
    "o1-preview": ModelPricing(input_price=15.00, cached_input_price=7.50, output_price=60.00),
    "o1-preview-2024-09-12": ModelPricing(input_price=15.00, cached_input_price=7.50, output_price=60.00),
    "o1-mini": ModelPricing(input_price=3.00, cached_input_price=1.50, output_price=12.00),
    "o1-mini-2024-09-12": ModelPricing(input_price=3.00, cached_input_price=1.50, output_price=12.00),
}


def get_model_pricing(model: str) -> ModelPricing:
    """
    Get pricing for a specific model.

    Args:
        model: The model name (e.g., "gpt-4o", "gpt-4o-mini")

    Returns:
        ModelPricing object with pricing information

    Raises:
        ValueError: If model is not found in the pricing registry
    """
    if model not in MODEL_PRICING:
        raise ValueError(
            f"Model '{model}' not found in pricing registry. Available models: {', '.join(MODEL_PRICING.keys())}"
        )
    return MODEL_PRICING[model]


def analyze_cost(usage_list, model: str = "gpt-4o-mini"):
    """
    Analyze and compute the total cost based on cumulative usage details.

    Each usage object is expected to have:
      - "prompt_tokens": total prompt tokens used,
      - "completion_tokens": total output tokens,
      - "prompt_tokens_details": an object containing "cached_tokens".

    Args:
        usage_list: List of usage objects from OpenAI API responses
        model: The OpenAI model name for pricing lookup (default: "gpt-4o-mini")

    Returns:
        Dictionary with token counts and computed costs including:
        - total_cached_tokens: Total cached prompt tokens
        - total_prompt_tokens: Total prompt tokens (cached + uncached)
        - total_output_tokens: Total completion/output tokens
        - total_uncached_tokens: Total uncached prompt tokens
        - cost_uncached: Cost of uncached tokens
        - cost_cached: Cost of cached tokens
        - cost_output: Cost of output tokens
        - total_cost: Total estimated cost
        - model: Model name used for pricing
    """
    # Get pricing for the specified model
    pricing = get_model_pricing(model)

    total_cached_tokens = 0
    total_prompt_tokens = 0
    total_output_tokens = 0
    total_uncached_tokens = 0

    for usage in usage_list:
        total_prompt_tokens += usage.prompt_tokens
        total_output_tokens += usage.completion_tokens

        if hasattr(usage, "prompt_tokens_details") and hasattr(usage.prompt_tokens_details, "cached_tokens"):
            cached_tokens = usage.prompt_tokens_details.cached_tokens
            if isinstance(cached_tokens, int):
                total_cached_tokens += cached_tokens
            else:
                total_cached_tokens += 0
        else:
            cached_tokens = 0

        total_uncached_tokens += usage.prompt_tokens - cached_tokens

    # Calculate costs using model-specific pricing
    cost_uncached = (total_uncached_tokens / 1_000_000) * pricing.input_price
    cost_cached = (total_cached_tokens / 1_000_000) * pricing.cached_input_price
    cost_output = (total_output_tokens / 1_000_000) * pricing.output_price

    total_cost = cost_uncached + cost_cached + cost_output

    print(f"Estimated Cost: ${total_cost:.4f}")

    return {
        "total_cached_tokens": total_cached_tokens,
        "total_prompt_tokens": total_prompt_tokens,
        "total_output_tokens": total_output_tokens,
        "total_uncached_tokens": total_uncached_tokens,
        "cost_uncached": cost_uncached,
        "cost_cached": cost_cached,
        "cost_output": cost_output,
        "total_cost": total_cost,
        "model": model,
    }
