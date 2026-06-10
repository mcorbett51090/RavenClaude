---
scenario_id: 2026-06-10-security-questionnaire-unverifiable-yes
contributed_at: 2026-06-10
plugin: sales-engineering
product: security-questionnaire
product_version: "n/a"
scope: likely-general
tags: [security-questionnaire, soc2, evidence, clawback, trust-center]
confidence: medium
reviewed: false
---

## Situation

Late in an enterprise deal, the buyer's security team sent a 280-row bespoke security questionnaire with a 48-hour turnaround. Under deadline pressure, an AE started marking "Yes / Compliant" down the column to keep the deal moving.

## Constraints

- Real SOC 2 Type II report existed, but several questionnaire rows asked about controls **not** in the current audit scope (e.g., a specific key-rotation cadence and a customer-managed-keys option still on the roadmap).
- 48-hour clock; the AE wanted to avoid "looking weak."

## What we tried

1. The first pass inflated two roadmap controls to "implemented" to avoid a "No."
2. On review, the SE caught that neither claim mapped to evidence — one was roadmap, one was a compensating control, not the literal control asked about.

## Resolution

The team rebuilt the answers under the evidence-mapping discipline: every "yes" cited a SOC 2 section or an ISO SoA item; the two unbacked rows were answered honestly — one as **roadmap (dated)**, one as a **compensating control** with an explanation — and both were flagged to `security-reviewer` before sending. They also pointed the buyer to the SOC 2 report + a short trust summary, which let them mark ~40 rows as "see attached report" instead of re-answering. The honest answers actually *accelerated* the review — the buyer's security team trusted the package because the caveats were explicit.

## Lesson

A security questionnaire is a legal artifact; an inflated "yes" is a clawback/fraud risk, not a sales win. Map every claim to evidence, state roadmap-vs-implemented plainly, flag the unverifiable for security-reviewer, and lean on the SOC 2 report + trust center to deflect the repetitive rows. Honesty mapped to evidence closed the review faster than a column of unbacked yeses would have.
