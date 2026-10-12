# Stage 2 — The math Stage 1 deliberately left out

Four things to run, all of them pure math. No API key needed anywhere in this stage, no network call at all. Everything here runs fully on your own machine.

Stage 1's own README made a promise: "Stage 2 picks up the math this stage deliberately left out: the real attention formula, RoPE, and the loss functions behind fine-tuning." This is that stage.

## What's actually in here

**topic_1_attention_formula** — the real formula Stage 1's toy "rough shape" demo was standing in for: `Attention(Q, K, V) = softmax(QKᵀ / √d_k)V`. Worked on hand-picked numbers small enough to read, with a clear winner at the end instead of a vague blend.

**topic_2_rope_positional_encoding** — why attention alone has no sense of word order, and how RoPE fixes that by rotating each token's vectors by an angle tied to position. The real proof: two tokens 3 positions apart produce the exact same result whether that gap happens near the start of a sequence or 100 tokens in.

**topic_3_gradient_descent_cross_entropy** — the actual training loop. One weight, trained across six steps, loss falling from 1.10 to 0.30 while the probability on the correct answer climbs from 33% to 74%. This exact loop, scaled to billions of weights, is how every model's parameters got their final values.

**topic_4_dpo_loss** — the loss function behind one of the two fine-tuning approaches named in this project's main roadmap (DPO and GRPO). Worked on one preference pair, showing the loss fall as a simulated policy learns to prefer the better response, and where DPO's job ends and GRPO's begins.

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
python src/topic_1_attention_formula/main.py
python src/topic_2_rope_positional_encoding/main.py
python src/topic_3_gradient_descent_cross_entropy/main.py
python src/topic_4_dpo_loss/main.py
```

All four will work immediately, every time, with no setup beyond the packages above.

## Tests

```bash
pytest tests/
```

All nine tests are real and automated, unlike Stage 1 where only the offline topic had test coverage. Every topic in this stage is pure math with no live API call, so every one of them gets proper test coverage.

## What you should be able to explain once you're done

- The actual attention formula, not just its rough shape, including why the division by √d_k matters
- Why attention has no sense of word order on its own, and specifically how RoPE's rotation fixes that
- What a gradient actually is and why gradient descent reliably reduces loss
- What the DPO loss optimizes for, and when DPO is the right tool versus when GRPO is

## Next

Stage 3 moves from understanding the mechanism to building with it: real API calls, structured output, and the practical engineering layer on top of everything covered so far.
