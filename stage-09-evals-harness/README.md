# Stage 9 — Evals, observability, and harnesses

Four things to run. This stage covers harness engineering, formally named as a discipline in March 2026, and confirmed as the reason most agent projects never reach production: not the model, the runtime built around it.

## What's actually in here

**topic_1_golden_dataset** — fully offline. A versioned eval set built from three modeled production incidents, not invented easy questions, growing one real failure at a time.

**topic_2_llm_judge_calibration** — the model used as a judge against four responses with known human labels, grounding a real, documented 28% false negative rate directly instead of just citing it.

**topic_3_ci_eval_gate** — fully offline. A real property-check suite that returns an actual process exit code. Confirmed by checking the shell's own exit status after the script runs, not just trusting printed output.

**topic_4_checkpoint_recovery** — fully offline. Stage 8's ReAct loop, extended with checkpointing. A simulated crash partway through, and a second run that resumes from the last good step instead of starting over.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- A free Groq API key. Only topic 2 needs it.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Running each topic

```bash
python src/topic_1_golden_dataset/main.py
python src/topic_2_llm_judge_calibration/main.py
python src/topic_3_ci_eval_gate/main.py
python src/topic_4_checkpoint_recovery/main.py
```

Topics 1, 3, and 4 work immediately with no key at all. Try `echo $?` after running topic 3 to see its real exit code yourself.

## Tests

```bash
pytest tests/
```

12 tests, covering topics 1, 3, and 4 in full, since all three are fully offline.

## A note on how this was built

Topic 4's crash simulation had a real bug during development: the first version made the agent hit the identical simulated crash twice in a row, since nothing distinguished a first attempt from a retry. Fixed by marking the crash as a one-time event, the same way a real transient failure (a dropped connection, a momentary resource spike) isn't guaranteed to recur on retry. Topic 2 calls a live model and was not live-tested against the real Groq API, since this was built with no internet access.

## What you should be able to explain once you're done

- Why a golden dataset built from invented easy questions proves little, and what building one from real incidents actually looks like
- The real, documented limitation of LLM-as-judge, and why current practice says never to rely on it alone
- The literal mechanism, an exit code, that separates an eval that blocks a merge from one that's decoration
- Why a checkpoint is the structural fix for the kind of incident where a runaway agent loops for days unnoticed

## Next

Stage 10 moves into fine-tuning and data curation: when SFT, DPO, or RLHF each actually apply, and why fine-tuning is a later-stage skill in 2026, not the first tool most teams should reach for.
