# Guardrails and capability evals are different tests

**Rule.** Keep "can it do the task well?" (capability) separate from "does it ever do something
harmful/leaky/off-policy?" (guardrail). Different suites, different pass bars: a capability regression is
a quality bug to weigh; a guardrail failure is a zero-tolerance release blocker.

**Why.** Averaging them hides the thing that matters most — a feature can score 90% on quality while
leaking PII on 1% of inputs, and a blended number makes that 1% disappear.

**Anti-pattern it kills.** A single "eval score" that lets a prompt-injection or PII-leak failure be
outweighed by good average quality.

**In practice.** Capability suite → threshold gate; guardrail/red-team suite → any failure blocks, and
grows every time production surprises you.
