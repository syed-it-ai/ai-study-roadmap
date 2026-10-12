# Stage 10 — Fine-tuning and data curation

Four things to run, all of them pure math. No API key needed anywhere in this stage, same property as Stage 2. This is the second fully-offline stage in the project, which fits: training-time math doesn't need a live model to demonstrate, only to eventually apply.

## What's actually in here

**topic_1_sft_dpo_rlhf_decision** — a real decision function routing 5 realistic scenarios to SFT, DPO, GRPO, or RLHF, based on what signal is actually available, not which method sounds most advanced.

**topic_2_lora_dora_math** — the real low-rank decomposition math. At a realistic 4096x4096 layer, LoRA cuts trainable parameters by 99.2%, not the 50% a smaller illustrative example alone would suggest. DoRA's magnitude/direction split is computed directly and shown to produce a measurably different result from plain LoRA.

**topic_3_grpo_loss** — the actual GRPO loss, group-relative advantage and clipping, built on Stage 2's DPO code. The exact mechanism behind DeepSeek-R1-Zero's documented 15.6% to 77.9% jump on AIME 2024, with zero supervised fine-tuning.

**topic_4_knowledge_distillation** — hard-label versus soft-label training signal, worked on a real teacher distribution, showing exactly what information a one-hot label throws away.

## Before you start

You need:
- Python 3.10 or newer
- VS Code with the Python extension installed
- Nothing else. No API key, no provider account, no internet connection once the packages below are installed.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running each topic

```bash
python src/topic_1_sft_dpo_rlhf_decision/main.py
python src/topic_2_lora_dora_math/main.py
python src/topic_3_grpo_loss/main.py
python src/topic_4_knowledge_distillation/main.py
```

All four work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

16 tests, the most of any stage, covering all four topics in full, since every topic in this stage is pure math.

## A note on how this was built

Topic 2's first version used a 64x64 example that happened to land on exactly 50% parameter reduction, a number that understates LoRA badly since real model layers are far larger and the savings get more dramatic with scale, not less. Fixed by adding a realistic 4096x4096 comparison showing the actual 99.2% figure. Topic 3's clipped objective landed on an unintentional 0.0000 from one specific set of numbers summing to exactly zero, correct but visually indistinguishable from a bug; adjusted one input value so the result is clearly a real, non-coincidental number.

## What you should be able to explain once you're done

- Which of SFT, DPO, GRPO, or RLHF fits a given problem, based on what signal is actually available
- Why LoRA's parameter savings get more dramatic as the target matrix gets larger, and what DoRA specifically fixes about plain LoRA
- The actual GRPO mechanism: no value model, group-relative advantage, and why that's what let DeepSeek-R1-Zero train with pure reinforcement learning
- What a soft label carries that a hard label discards, and why a distilled model can never exceed its teacher

## Next

Stage 11 moves into multimodal, voice, and realtime: vision and document extraction beyond plain OCR, and the latency and turn-taking engineering that realtime voice actually depends on.
