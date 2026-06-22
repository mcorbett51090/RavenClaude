# trust-and-safety

> The **Trust & Safety team** for Claude Code — turns "this content is bad" into a defensible system: a policy taxonomy, a proportional enforcement ladder, a human-review operation, the detection stack behind it, and the metrics that prove it works without trampling due process.

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## What it does

| You ask | It returns |
|---|---|
| "Design a moderation policy for this surface." | A policy taxonomy (categories + severity tiers) + a proportional remove/limit/warn/ban ladder + an appeal path |
| "Rules or an ML classifier to catch this abuse?" | A signal inventory + a rules-vs-ML (or hybrid) decision + a signal → score → threshold → queue pipeline |
| "Where do I set the classifier threshold?" | An operating point chosen from the false-positive vs. false-negative cost, with the precision/recall it buys |
| "How do we prioritize the review queue?" | Severity × prevalence × virality prioritization + escalation tiers + reviewer-wellness guardrails |
| "Is our appeals process fair? / What should we measure?" | A due-process appeal path; a metric frame — prevalence, enforcement precision/recall, time-to-action SLA, overturn rate |

**Three rules it never breaks:** *enforcement is proportional*, *appeals are due process (not optional)*, and *measure prevalence, not just volume*.

## What's inside

- **2 agents** — `trust-safety-policy-lead` (policy taxonomy, enforcement ladder, review operations, measurement) and `abuse-detection-engineer` (signals, rules-vs-ML, thresholds, reviewer-queue routing).
- **3 skills** — `design-moderation-policy`, `build-abuse-detection-pipeline`, `measure-enforcement-quality`.
- **2 knowledge files** — an enforcement decision tree (Mermaid: report/signal → severity triage → ladder → appeal) and the T&S metrics catalogue (prevalence, precision/recall, SLA, overturn rate, with formulas).
- **2 templates** — a content-policy doc and a moderation runbook.
- **3 best-practice rules** — proportionality, appeals-as-due-process, prevalence-over-volume.
- **1 advisory hook** — `flag-ts-smells.sh` (an enforcement action with no appeal path; a threshold with no precision/recall noted).

## When to use it

Reach for this plugin when you're standing up or reviewing a content-moderation program, designing an abuse/fraud/spam detector, running the human-review operation, or deciding what to measure. It is **advisory and design-facing** — the live moderation system runs on your data outside the repo, so the agents design the policy, the pipeline, and the metric definitions and emit runnable snippets you wire up locally.

## Seams (where it hands off)

```
trust-and-safety        →  policy, enforcement ladder, review ops, the detector, the metric definitions
applied-statistics      →  "is this classifier eval statistically valid?" (precision/recall CI, sample size)
data-governance-privacy →  PII / data-retention / lawful basis for moderation data
security-engineering    →  account-takeover, coordinated inauthentic behavior, security signals
claude-app-engineering  →  building an LLM-based classifier
```

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install trust-and-safety@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
