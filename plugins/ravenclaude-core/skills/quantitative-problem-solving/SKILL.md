---
name: Quantitative Problem Solving
description: >-
  Use this when something failed or may fail — enumerate failure hypotheses,
  cost each try, update P(cause|history), and pick the next action by expected
  value / EVPI.
---

# Quantitative Problem Solving

Companion to RavenClaude Core. Prefer math over vibes when choosing the next try after failure.

## Stance

1. Failure is information — log it; update beliefs; do not hide it.
2. Retry is not repeat — change hypothesis, method, or observation.
3. Occam as prior — more complex causes get lower prior unless evidence demands them.
4. Score the next poke — rank by expected value (or EV of information), not gut.
5. Stop when EV-negative or wall — escalate with the table, not a novel.

## Workflow 1 — Hypothesis table

Columns: ID, Hypothesis, Prior P0, Complexity (Occam low/med/high), Signature, Ruled out if.

Occam-adjusted prior (simple): unnormalized weight = base_plausibility / (2 ** k), where k = extra-assumptions count. Normalize so priors sum to 1.

Map hypotheses to failure variables: auth, network, permissions, version skew, bad input, wrong target, flake, capacity, logic bug, config drift, and domain-specific ones.

## Workflow 2 — Cost of each try

For each candidate action (probe, fix, rollback, ask human, switch tool), score time, token/money, and blast/risk. Total C(a) = weighted sum; state weights once per session. Irreversible / money / delete get huge risk or require CoS/HITL.

## Workflow 3 — Update from history (Bayes)

After outcome o, set likelihood L(o | Hi) on a coarse scale (0.05, 0.2, 0.5, 0.8, 0.95). Posterior P(Hi | o) proportional to L(o | Hi) * P(Hi); renormalize. Identical blind retries should not move posteriors — design a new observation.

## Workflow 4 — Choose next action

EV(a) = P(solve | a) * U_solve + (1 - P(solve | a)) * U_fail - C(a). Pick the allowed action with max EV. If EV of perfect information exceeds the best probe cost, probe before a heavy fix.

## Deliverable shape

1. Hypothesis table (priors + posteriors)
2. Cost table for candidate tries
3. Chosen action + EV one-liner
4. What would falsify it next
5. Escalation trigger if top actions are blocked

## Anti-patterns

One-and-done abandonment; same failing command on loop; complex conspiracies without Occam penalty; nuclear options without cost; skipping the table when two or more causes remain.

## Credit

Companion to RavenClaude Core — first principles + Occam + Bayesian try-ranking.
