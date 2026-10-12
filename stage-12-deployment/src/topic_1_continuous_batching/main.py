"""
Confirmed as table stakes for any serious 2026 inference stack:
continuous batching (also called in-flight batching), the second of
vLLM's two foundational techniques alongside PagedAttention. The
documented real-world effect: switching from static batching to
continuous batching typically lifts GPU utilization from a 30-40%
range up to 75-90%, roughly 2 to 4x more output tokens per GPU-hour on
the same hardware. This simulates why, with real arithmetic on request
timing, not a live serving engine.
"""


def simulate_static_batching(requests: list, batch_size: int) -> dict:
    """
    Static batching: wait until a full batch of requests has arrived,
    process them together, wait for every request in the batch to
    finish before starting the next batch. A short request sitting in
    the same batch as a long one has to wait for the long one anyway.
    """
    total_time = 0
    gpu_busy_time = 0
    i = 0
    while i < len(requests):
        batch = requests[i:i + batch_size]
        batch_duration = max(batch)  # the batch can't finish until its slowest request does
        total_time += batch_duration
        gpu_busy_time += sum(batch)  # work actually done, even though it took batch_duration wall-clock time
        i += batch_size
    utilization = gpu_busy_time / (total_time * batch_size) if total_time else 0
    return {"total_time": total_time, "gpu_busy_time": gpu_busy_time, "utilization": utilization}


def simulate_continuous_batching(requests: list, batch_size: int) -> dict:
    """
    Continuous batching: the instant one request in the batch finishes,
    a new request from the queue takes its slot immediately, no waiting
    for the whole batch to drain. This is a simplified event-driven
    simulation, not a real scheduler, but the core mechanic, slots
    refilling independently instead of in lockstep, is the same one
    that produces the real documented utilization gain.
    """
    slots = [0.0] * batch_size  # time remaining for whatever is currently in each slot
    queue = list(requests)
    gpu_busy_time = sum(requests)
    clock = 0.0

    for i in range(min(batch_size, len(queue))):
        slots[i] = queue.pop(0)

    while any(s > 0 for s in slots) or queue:
        # advance to whichever slot finishes next
        active = [s for s in slots if s > 0]
        if not active:
            break
        step = min(active)
        clock += step
        for i in range(batch_size):
            if slots[i] > 0:
                slots[i] -= step
                if slots[i] <= 1e-9:
                    slots[i] = queue.pop(0) if queue else 0.0

    utilization = gpu_busy_time / (clock * batch_size) if clock else 0
    return {"total_time": clock, "gpu_busy_time": gpu_busy_time, "utilization": utilization}


def main() -> None:
    # A realistic mixed workload: most requests are short, a few are
    # much longer, exactly the pattern that makes static batching's
    # wait-for-the-slowest problem visible.
    requests = [2, 3, 2, 15, 2, 3, 2, 2, 14, 3, 2, 2, 3, 13, 2, 2]
    batch_size = 4

    static = simulate_static_batching(requests, batch_size)
    continuous = simulate_continuous_batching(requests, batch_size)

    print(f"{len(requests)} requests, batch size {batch_size}, durations: {requests}\n")

    print(f"Static batching:")
    print(f"  Total wall-clock time: {static['total_time']:.1f}")
    print(f"  GPU utilization: {static['utilization']*100:.0f}%")

    print(f"\nContinuous batching:")
    print(f"  Total wall-clock time: {continuous['total_time']:.1f}")
    print(f"  GPU utilization: {continuous['utilization']*100:.0f}%")

    speedup = static['total_time'] / continuous['total_time']
    print(f"\nSpeedup: {speedup:.2f}x faster wall-clock time for identical work")
    print(
        f"\nThe same three long requests (15, 14, 13) are what punish static "
        f"batching specifically: every short request sharing a batch slot "
        f"with one of them has to wait for it to finish before that slot "
        f"can start a new request. Continuous batching refills each slot "
        f"the instant it's free, independent of what else is still running."
    )
    print(
        "\nConfirmed as the real documented range: production teams report "
        "GPU utilization climbing from 30-40% under static batching to "
        "75-90% under continuous batching, translating to roughly 2 to 4x "
        "more output tokens per GPU-hour on identical hardware. This "
        "simulation's own speedup, on a small illustrative workload, "
        "lands in that same real range."
    )


if __name__ == "__main__":
    main()
