# cost_analysis.py


def analyze_cost(usage_list):
    """
    Analyze and compute the total cost based on cumulative usage details.

    Each usage dictionary is expected to have:
      - "prompt_tokens": total prompt tokens used,
      - "completion_tokens": total output tokens,
      - "prompt_tokens_details": a dict containing "cached_tokens".

    Cost calculations:
      - Uncached tokens: prompt_tokens - cached_tokens, at $0.30 per 1,000,000 tokens.
      - Cached tokens: cached_tokens, at $0.15 per 1,000,000 tokens.
      - Output tokens: completion_tokens, at $1.20 per 1,000,000 tokens.

    Returns a dictionary with token counts and computed costs.
    """
    total_cached_tokens = 0
    total_prompt_tokens = 0
    total_output_tokens = 0

    for usage in usage_list:
        # Access attributes directly from the pydantic model
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens

        # For nested attributes like cached_tokens, check if the attribute exists
        cached_tokens = 0
        if hasattr(usage, "prompt_tokens_details") and usage.prompt_tokens_details:
            cached_tokens = getattr(usage.prompt_tokens_details, "cached_tokens", 0)

        total_cached_tokens += cached_tokens
        total_prompt_tokens += prompt_tokens
        total_output_tokens += completion_tokens

    total_uncached_tokens = total_prompt_tokens - total_cached_tokens

    cost_uncached = (total_uncached_tokens / 1_000_000) * 0.30
    cost_cached = (total_cached_tokens / 1_000_000) * 0.15
    cost_output = (total_output_tokens / 1_000_000) * 1.20

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
    }
