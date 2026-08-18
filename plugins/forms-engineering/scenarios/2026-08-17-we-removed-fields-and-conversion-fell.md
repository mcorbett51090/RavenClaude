---
scenario_id: 2026-08-17-we-removed-fields-and-conversion-fell
contributed_at: 2026-08-17
plugin: forms-engineering
product: form-intake
product_version: "n/a"
scope: likely-general
tags: [field-count, conversion, denominator, intake, measurement]
confidence: medium
reviewed: false
---

## Problem

A team cut a lead form from a long list of fields to three, on the widely-repeated principle that fewer fields always converts better. Submissions rose. Then the sales team reported that the pipeline had got *worse*, and a follow-up measurement showed the completion rate on the reduced form had **fallen** against the number the team had been quoting.

## Context

- The form fed a human qualification queue. The removed fields were the ones the queue used to route and prioritise.
- The "before" completion rate had been computed against page views. The "after" number was computed against form starts, by a different person, in a different tool.
- Nobody had written down what a submission was worth, so "more submissions" read as success for two weeks.

## Attempts

- Tried: re-running both numbers on one denominator. Outcome: the apparent drop was mostly an artifact — the two figures had never been comparable. This was the first thing to fix and it changed the size of the problem, not its direction.
- Tried: reading the field-count literature for a number to justify the change retroactively. Outcome: dropped. The commonly-quoted per-field penalties are single-company tests presented as benchmarks; this marketplace's own treatment removed them rather than re-cite them, and the counter-evidence is recorded with it. **The claim "fewer fields always converts better" is not supported.** That is a negation of an absolute — it is not a claim that more fields convert better.
- Tried: re-deriving the field list from the routing decision instead of from the form. Outcome: two of the removed fields had no consumer at all and stayed removed; two were what the queue needed to act without a reply and came back — one of them moved later in the flow rather than restored to the first screen.
- Tried (the move that worked): defining the metric as *qualified* submissions rather than submissions, on one written denominator, and re-measuring. Outcome: the number the business cared about was now visible, and the field question became answerable by testing rather than by principle.

## Resolution

Two independent errors compounded. The **measurement** error was quoting two rates from two denominators and comparing them. The **design** error was optimising a proxy — raw submission count — that nobody had connected to value.

The durable fix was not a field count. It was: derive required fields from *what the receiving queue needs to act*, apply the use test to every field, and if conversion is the goal, **test the change** rather than assert it — field count is one of the few things genuinely worth testing, precisely because its effect is not predictable in advance.

**Action for the next person hitting this pattern:** fix the denominator before you interpret any movement — [`../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md`](../best-practices/name-the-denominator-before-you-quote-a-completion-rate.md). Then derive fields from the routing decision using [`../skills/form-intake-and-triage-design/SKILL.md`](../skills/form-intake-and-triage-design/SKILL.md) steps 2–3. Do not re-import a per-field penalty figure from anywhere.

**Sources for facts cited:** the field-count evidence, the counter-evidence, and the retraction of the unsourced benchmark table live in [`../../web-design/skills/conversion-design/SKILL.md`](../../web-design/skills/conversion-design/SKILL.md) §3 — one source, one home. Read 2026-08-17. Figures are illustrative `[ESTIMATE]`.
