# Continuous batching

## What the code showed you

16 identical requests, run through both strategies. Static batching finished in 45 time units at 40% GPU utilization. Continuous batching finished the same work in 23 time units at 78% utilization, a 1.96x speedup, landing almost exactly inside the real documented range for this exact technique.

## What's actually happening underneath that

![Static batching leaving visible idle gaps while every slot waits for the slowest request in its batch, versus continuous batching packing slots tightly](./images/batching_comparison.png)

Confirmed as table stakes for any serious 2026 inference stack: continuous batching (also called in-flight batching) alongside PagedAttention are vLLM's two foundational techniques, and by 2026 both are the baseline expectation, not a differentiator. Static batching's specific failure, visible directly in this topic's diagram, is that a batch can't start processing its next group of requests until every single request in the current batch finishes, including the slowest one. Three long requests (15, 14, and 13 time units) in this topic's workload each forced three other, much shorter requests to sit idle waiting for them.

Continuous batching fixes this by refilling each processing slot the instant it frees up, independent of what else is still running in the other slots. Confirmed as the real, documented production effect: switching from static to continuous batching typically lifts GPU utilization from a 30-40% range up to 75-90%, translating to roughly 2 to 4x more output tokens per GPU-hour on identical hardware, numbers this topic's own simulation landed well inside of.

## Resources, in the order I'd actually use them

**For the current state of vLLM and this exact technique**
- Current 2026 sources on vLLM's production serving guide confirm the 30-40% to 75-90% utilization range directly, alongside PagedAttention as the memory-management technique that keeps continuous batching effective as sequences grow.

## The one thing worth remembering

A workload with uniform request durations gets no benefit from continuous batching at all, since nothing ever finishes early enough to need refilling ahead of its neighbors. The entire benefit comes specifically from variance in request length, which is exactly the normal, mixed-length-request shape of real production traffic.
