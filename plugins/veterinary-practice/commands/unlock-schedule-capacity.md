---
description: "Find the doctor bottleneck and fix the appointment template so a fully-booked practice can grow throughput. Reach for this when revenue is flat despite full demand."
argument-hint: "[the situation, e.g. the metric / segment / matter in question]"
---

# Unlock schedule capacity

You are running `/veterinary-practice:unlock-schedule-capacity` for `$ARGUMENTS`. Run it the way the team's specialists would — applying the house opinions in [`../CLAUDE.md`](../CLAUDE.md) §3.

## Steps (traverse top-to-bottom; do not skip)
1. Map utilization — Measure schedule utilization and the doctor bottleneck (§3 #3).
2. Redesign the template — Adjust appointment lengths/types and the support hand-off to add doctor throughput.
3. Set the support ratio — Tune the tech-to-doctor ratio so doctors work at the top of their license (§3 #7).
4. Quantify the unlock — State the added capacity and revenue from the change.

## Output
A capacity read, an appointment-template redesign, a support-ratio recommendation, and the revenue unlock. See [`../skills/unlock-schedule-capacity/SKILL.md`](../skills/unlock-schedule-capacity/SKILL.md). Traverse the matching tree in [`../knowledge/vet-decision-trees.md`](../knowledge/vet-decision-trees.md).

## Guardrails
- Apply the §3 house opinions before any method; resist a single-cause story.
- No client PII in the output; cite a source + date for every external figure (or mark it).
- End with owner / date / expected movement on each recommendation.
