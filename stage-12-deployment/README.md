# Stage 12 — Deployment and inference

Four things to run, all of them pure Python. No API key needed anywhere in this stage, the fourth fully-offline stage in the project, since serving infrastructure, gateway logic, quantization math, and cost calculators are all things you can reason about and verify without a live model call.

## What's actually in here

**topic_1_continuous_batching** — a real simulation of static vs. continuous batching on 16 mixed-duration requests. The code's own numbers (40% vs. 78% utilization, 1.96x speedup) land almost exactly inside the real documented range for this exact technique.

**topic_2_llm_gateway_fallback** — a working gateway with real fallback logic, built on the LiteLLM pattern. All three outcomes (success, fallback, total failure) are genuinely exercised with controllable fake providers, not just described.

**topic_3_quantization_math** — the actual scale/zero-point quantization formula, worked on real weight values, then the real memory savings at a 70B-parameter scale: 280 GB down to 35 GB across four precisions.

**topic_4_self_host_vs_api** — the real break-even calculator. Caught and fixed a genuine bug during development: an earlier version computed only a 1.4x real-cost multiplier while the code's own comments claimed the confirmed 3-5x figure. Now lands at exactly 4.0x.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- Nothing else. No API key, no provider account, no internet connection.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running each topic

```bash
python src/topic_1_continuous_batching/main.py
python src/topic_2_llm_gateway_fallback/main.py
python src/topic_3_quantization_math/main.py
python src/topic_4_self_host_vs_api/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

12 tests, covering all four topics in full. `test_real_multiplier_lands_in_confirmed_range` specifically locks in the fix described below, so the bug it caught can't quietly come back.

## A note on how this was built

Topic 4 had a real, substantive bug caught by actually running the code: the first version applied a staffing-overhead multiplier directly to a daily dollar figure while applying utilization only to token output, producing a 1.4x real-cost multiplier that flatly contradicted the confirmed 3-5x figure stated in the code's own comments. Fixed by properly combining both effects into one real cost-per-token calculation, utilization and staffing overhead compounding together rather than applied separately, landing the result at exactly 4.0x. A second pass caught the closing summary claiming the deployment's capacity was comfortably above the frontier break-even point when the actual numbers (6.0M vs. 6.4M) put it just below, fixed to describe the real relationship instead of a convenient-sounding approximation of it.

## What you should be able to explain once you're done

- Why continuous batching's entire benefit comes from variance in request length, and why a uniform workload gets nothing from it
- How an LLM gateway's fallback logic actually works, and why it's only trustworthy once its failure path has been tested, not just described
- The real memory cost of each quantization precision at a realistic model scale, and why the per-weight error is a genuine, permanent tradeoff
- Why self-hosting's case depends entirely on which API it's being compared against, with real numbers showing both a near-even case and an 80x-short case from the identical deployment

## Next

Stage 13 moves into AI coding agents: picking one tool and learning its harness deeply, and the skills (SKILL.md files) pattern that's become a cross-platform standard.
