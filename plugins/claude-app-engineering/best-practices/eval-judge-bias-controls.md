# Control LLM-judge bias with order randomization and a calibration set

**Status:** Absolute rule
**Domain:** Evals / LLM-as-judge
**Applies to:** `claude-app-engineering`

---

## Why this exists

An LLM judge has well-documented systematic biases: it favors the response it sees first (position bias), favors longer responses regardless of quality (verbosity bias), and favors responses that match its own generation style (self-similarity bias). A judge score that is not corrected for these biases is an unreliable regression signal — it can report an improvement where none exists, and miss a real regression. The investment in an eval pipeline is wasted if the judge's verdicts are noise.

## How to apply

Apply three controls before trusting any LLM-judge eval run.

**1. Randomize presentation order for every pair comparison.**

```python
import random

def judge_pair(judge_client, prompt, response_a, response_b):
    """Return the winner; compensate for position bias with order swap."""
    if random.random() > 0.5:
        order = (response_a, response_b)
        mapping = {"first": "A", "second": "B"}
    else:
        order = (response_b, response_a)
        mapping = {"first": "B", "second": "A"}

    verdict = judge_client.compare(prompt, first=order[0], second=order[1])
    return mapping[verdict]  # map "first/second" back to A/B
```

**2. Run each comparison twice (flipped order) and only count agreements.**

```python
def stable_judge_pair(judge_client, prompt, a, b):
    v1 = judge_client.compare(prompt, first=a, second=b)   # a=first
    v2 = judge_client.compare(prompt, first=b, second=a)   # b=first
    # Agreement: both say the same response wins
    if v1 == "first" and v2 == "second":
        return "A"
    if v1 == "second" and v2 == "first":
        return "B"
    return "tie"  # disagreement = position bias dominated; count as inconclusive
```

**3. Maintain a calibration set with known labels (human-verified) and check the judge's accuracy on it each release.**

```python
CALIBRATION_SET = [
    {"prompt": "...", "better": "A", "reason": "more accurate"},
    ...
]

def validate_judge(judge_fn):
    correct = sum(1 for item in CALIBRATION_SET if judge_fn(item) == item["better"])
    accuracy = correct / len(CALIBRATION_SET)
    assert accuracy >= 0.80, f"Judge accuracy on calibration set: {accuracy:.0%} — too low"
```

**Do:**
- Use Haiku via Batch for judging: cheap, fast, and position-bias-controlled the same way as any other judge.
- Pin the judge model version — a judge model update is itself an eval event.
- Log every `(prompt, response_a, response_b, verdict, order)` tuple for post-hoc audit.

**Don't:**
- Use a single-pass comparison with a fixed order as the sole signal.
- Use the same model (or a closely related variant) as both the subject and the judge.
- Trust a judge's calibration score from three months ago without re-running on the current model.

## Edge cases / when the rule does NOT apply

Absolute/rubric-style grading (score 1–5 against a rubric, not a head-to-head comparison) reduces position bias but not verbosity bias — still validate on a calibration set. Order randomization doesn't apply to rubric grading.

## See also

- [`../agents/eval-engineer.md`](../agents/eval-engineer.md) — the agent that owns the eval pipeline and judge design
- [`./evals-before-vibes.md`](./evals-before-vibes.md) — the foundational rule that an eval gate must exist

## Provenance

Codifies `claude-app-engineering/CLAUDE.md` §3 opinion #4 (judge on Haiku via Batch, randomize order against position bias). Position/verbosity bias controls are established LLM-eval practice (Stanford HELM, Chatbot Arena methodology, Anthropic eval guidance).

---

_Last reviewed: 2026-06-05 by `claude`_
