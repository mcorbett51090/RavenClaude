---
description: "Sequence post as a dependency chain keyed off picture lock, so the delivery date rests on the critical path. Reach for this on a post plan."
argument-hint: "[the situation, e.g. the metric/segment in question]"
---

# Sequence the post pipeline

You are running `/film-video-production:sequence-the-post-pipeline` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map the dependencies — Editorial → VFX → color → sound → conform → deliver (§3 #3).
2. Protect picture lock — Set the lock as the gate finishing waits on (§3 #5).
3. Find the critical path — Identify what sets the delivery date.
4. Schedule to deliver — Sequence finishing to the delivery spec and date (§3 #6).

## Output
A post-pipeline dependency map, a protected lock, the critical path, and a delivery schedule. See [`../skills/sequence-the-post-pipeline/SKILL.md`](../skills/sequence-the-post-pipeline/SKILL.md).

## Guardrails
- Apply the §3 house opinions before any method.
- No client PII; cite or mark every external figure.
