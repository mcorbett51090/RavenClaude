# Enforce mutual exclusion between experiments that share a surface

**Status:** Absolute rule
**Domain:** Experimentation / assignment integrity
**Applies to:** `experimentation-growth-engineering`

---

## Why this exists

Two experiments running concurrently on the same UI surface, funnel step, or
pricing page interact. A user assigned to experiment A's treatment and
experiment B's treatment at the same time produces a metric reading that is an
uninterpretable mix of both effects. The naive fix is "we'll check if the results
look similar across groups" — but interaction effects are precisely what that
can't detect. Mutual exclusion (disjoint assignment) or full factorial design
(deliberate cross-assignment with interaction terms) are the two sound approaches.
Running overlapping experiments without either is broken by design.

## How to apply

**Option 1 — Mutual exclusion (default):** Partition the eligible population into
disjoint traffic buckets before assigning to experiments. Each user can be in at
most one experiment on a given surface at a time.

```python
# Hash-based layer assignment
def assign_layer(user_id: str, layers: list[str]) -> str:
    """Returns which experiment layer this user belongs to."""
    bucket = int(hashlib.md5(f"layer:{user_id}".encode()).hexdigest(), 16) % 100
    cumulative = 0
    for layer, pct in layers:
        cumulative += pct
        if bucket < cumulative:
            return layer
    return "holdout"  # unassigned to any experiment

layers = [
    ("checkout-flow-experiment", 20),   # 20% of users
    ("pricing-display-experiment", 20), # next 20% — no overlap
]
```

**Option 2 — Full factorial (deliberate overlap):** Allow users into multiple
experiments and include the interaction term in the analysis model. Only use
when the two experiments are hypothesised to be independent AND you have
sufficient power to detect the interaction.

**Escalate the statistical design choice** (which option, power for factorial)
to `applied-statistics`.

**Do:**
- Default to mutual exclusion; use full factorial only with a documented
  rationale and applied-statistics sign-off.
- Document which experiments share a layer and which are independent layers.
- Re-verify mutual exclusion after any experiment topology change.

**Don't:**
- Run overlapping experiments on the same surface without an explicit decision
  between mutual exclusion and full factorial.
- Assume "the effects are probably independent" without statistical backing.
- Mix assignment layers without updating the assignment layer documentation.

## Edge cases / when the rule does NOT apply

- Experiments on entirely separate, non-interacting surfaces (e.g. email subject
  line vs onboarding flow): they are naturally mutually exclusive and can share
  the same population without bucketing.

## See also

- [`../agents/experimentation-architect.md`](../agents/experimentation-architect.md) — owns the experiment assignment design
- [`./deterministic-assignment-server-side.md`](./deterministic-assignment-server-side.md) — assignment must be deterministic for mutual exclusion to hold

## Provenance

Codifies the concurrent-experiment interaction threat from standard A/B testing
infrastructure practice. The mutual-exclusion layer model is the dominant
approach in production experimentation systems (Evan Miller, "How Not to Run an
A/B Test" and related literature). Statistical design (full factorial) routes to
`applied-statistics`.

---

_Last reviewed: 2026-06-05 by `claude`_
