def analyze_cost(df, passes):
    input_tokens = len(df) * passes * 100  # Example assumption
    uncached_cost = (input_tokens / 1_000_000) * 0.30
    cached_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (len(df) * passes * 50 / 1_000_000) * 1.2  # Example assumption

    total_cost = uncached_cost + cached_cost + output_cost
    print(f"Estimated Cost: ${total_cost:.4f}")
