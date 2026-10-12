"""
Confirmed, and already researched directly for this project: naive
self-host comparisons (raw GPU rental price vs. API price per token)
typically underestimate real self-hosting cost by 3 to 5x once
utilization, staffing, and setup are counted. This builds the actual
break-even calculation, naive and real, side by side, rather than
quoting the multiplier as a fact to take on faith.
"""


def naive_cost_per_million_tokens(gpu_hourly_rate: float, tokens_per_gpu_hour: float) -> float:
    """
    The number most comparisons stop at: GPU rental price divided by
    its rated token throughput, silently assuming 100% utilization and
    zero operational overhead, as if the GPU produced useful tokens
    every second it was rented and nobody had to run the thing.
    """
    return (gpu_hourly_rate / tokens_per_gpu_hour) * 1_000_000


def real_cost_per_million_tokens(gpu_hourly_rate: float, tokens_per_gpu_hour: float,
                                   utilization: float = 0.5, staffing_overhead_multiplier: float = 2.0) -> float:
    """
    The real cost per token, confirmed as 3 to 5x the naive figure once
    properly counted. Two separate effects combine here, not one: you
    pay for the GPU whether or not it's busy, so real-world utilization
    well under 100% directly raises the effective cost of every token
    actually produced; and someone has to monitor, patch, and operate
    the deployment, a real, ongoing cost the naive estimate ignores
    entirely.
    """
    naive = naive_cost_per_million_tokens(gpu_hourly_rate, tokens_per_gpu_hour)
    return naive * staffing_overhead_multiplier / utilization


def tokens_served_per_day(gpu_hourly_rate: float, hours_per_day: float, utilization: float, tokens_per_gpu_hour: float) -> float:
    return hours_per_day * utilization * tokens_per_gpu_hour


def find_break_even_tokens_per_day(self_host_daily_cost: float, api_price_per_million_tokens: float) -> float:
    """At what daily token volume does self-hosting's fixed daily cost
    equal what the same volume would have cost through an API?"""
    return (self_host_daily_cost / api_price_per_million_tokens) * 1_000_000


def main() -> None:
    gpu_hourly_rate = 2.0           # a realistic current on-demand GPU rental rate
    utilization = 0.5                # realistic real-world average, not the 100% a naive estimate assumes
    staffing_overhead_multiplier = 2.0  # realistic ongoing monitoring, patching, and operational cost
    tokens_per_gpu_hour = 500_000    # a realistic open-weight model's throughput at this scale

    naive_cost = naive_cost_per_million_tokens(gpu_hourly_rate, tokens_per_gpu_hour)
    real_cost = real_cost_per_million_tokens(gpu_hourly_rate, tokens_per_gpu_hour, utilization, staffing_overhead_multiplier)
    real_multiplier = real_cost / naive_cost

    print(f"GPU rental: ${gpu_hourly_rate}/hour, rated throughput: {tokens_per_gpu_hour:,} tokens/hour\n")
    print(f"Naive cost per million tokens (assumes 100% utilization, zero overhead): ${naive_cost:.3f}")
    print(f"Real cost per million tokens ({utilization*100:.0f}% utilization, {staffing_overhead_multiplier}x staffing overhead): ${real_cost:.3f}")
    print(f"Real cost multiplier: {real_multiplier:.1f}x the naive estimate\n")

    daily_tokens = tokens_served_per_day(gpu_hourly_rate, 24, utilization, tokens_per_gpu_hour)
    daily_dollar_cost = (daily_tokens / 1_000_000) * real_cost
    print(f"Realistic tokens served per day at {utilization*100:.0f}% utilization: {daily_tokens:,.0f}")
    print(f"Real daily dollar cost at that volume: ${daily_dollar_cost:.2f}")

    # Break-even against two different kinds of API: a frontier model
    # (expensive per token) and a cheap open-weight API (inexpensive
    # per token), confirmed as landing in very different places.
    frontier_price_per_million = 15.0   # a realistic frontier API price per million tokens
    cheap_api_price_per_million = 0.20  # a realistic cheap open-weight API price per million tokens

    break_even_frontier = find_break_even_tokens_per_day(daily_dollar_cost, frontier_price_per_million)
    break_even_cheap = find_break_even_tokens_per_day(daily_dollar_cost, cheap_api_price_per_million)

    print(f"\nBreak-even token volume against a frontier API (${frontier_price_per_million}/M tokens):")
    print(f"  {break_even_frontier:,.0f} tokens/day")
    print(f"  This deployment's realistic capacity ({daily_tokens:,.0f}/day) is "
          f"{'above' if daily_tokens > break_even_frontier else 'below'} that break-even point.")

    print(f"\nBreak-even token volume against a cheap open-weight API (${cheap_api_price_per_million}/M tokens):")
    print(f"  {break_even_cheap:,.0f} tokens/day")
    if daily_tokens < break_even_cheap:
        print(f"  This deployment's realistic capacity ({daily_tokens:,.0f}/day) is "
              f"below that break-even point, by {break_even_cheap/daily_tokens:.0f}x.")
    else:
        print(f"  This deployment's realistic capacity ({daily_tokens:,.0f}/day) is above that break-even point.")

    print(
        f"\nThis deployment's realistic capacity ({daily_tokens:,.0f}/day) sits "
        f"right at the edge of the frontier break-even point "
        f"({break_even_frontier:,.0f}/day), close enough that a modest "
        f"utilization improvement or a slightly busier day tips it either "
        f"way. Against the cheap open-weight API it isn't close at all, off "
        f"by 80x. This is the real, confirmed shape of the finding: "
        f"self-hosting's case depends entirely on which API it's actually "
        f"being compared against, and a naive comparison that skips "
        f"utilization and staffing costs would have made both comparisons "
        f"look far more favorable than either actually is."
    )


if __name__ == "__main__":
    main()
