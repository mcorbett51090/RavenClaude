---
description: "Compose a Quarterly Business Review that opens with the partner's stated outcomes (not product features), proves each headline with a baseline-anchored chart, and ends with named, dated, owned commitments captured in the partner's words."
argument-hint: "[the partner and quarter, e.g. 'Q3 QBR for a mid-sized district']"
---

# Compose a QBR

You are running `/edtech-partner-success:compose-qbr`. Build the QBR the user described (`$ARGUMENTS`) as a Value-Realization narrative, not a usage report — the work the `qbr-composer` and `partner-success-manager` agents own. A usage report dressed as a QBR loses the room.

## When to use this

You are preparing a quarterly business review for an education partner. NOT for an ad-hoc check-in or a save play (that is `/edtech-partner-success:run-save-play`).

## Steps

1. **Open with the partner's stated outcomes, not your KPIs** (`qbr-open-with-partner-outcomes-not-product-features.md`): structure the arc from the partner's named business outcomes (the gains the product was supposed to move) outward — pull their goals verbatim from the durable profile, not PSM-internal renewal/expansion telemetry.
2. **Prove every headline with the chart and a named baseline** (`analytics-normalize-to-partner-size-and-state-the-comparison-baseline.md`): normalize engagement to partner size (per-capita, not raw totals — "12,000 logins" hides a per-capita collapse in a large district) and attach a named baseline to every percentage (vs last quarter / vs cohort / vs the onboarding target). Carry the source query and date range.
3. **Ground the readout in leading signals where you can** (`health-design-leading-not-lagging-signals.md`): frame trajectory with leading signals (depth-of-adoption trend, champion engagement) that give the partner runway, not just lagging totals.
4. **Verify any rostering-dependent claim before presenting it** (`check-rostering-before-calling-a-partner-red.md`, `rostering-sync-succeeded-is-not-the-same-claim-as-data-is-correct.md`): a sync that "succeeded" is not the same claim as "the data is correct" — don't present an adoption story built on unverified rostering.
5. **Screen any cohort-level or parent-facing slide for FERPA** (`screen-parent-comms-for-the-cohort-residual.md`): a small-cohort residual ("the 3 students who chose option B") can identify individuals — route anything student-level through `ferpa-comms-translator` before it goes on a slide. Use generic placeholders (`<district>`) in any example.
6. **End with named, dated, owned commitments in the partner's words** (`qbr-end-every-qbr-with-dated-owned-commitments.md`): make the penultimate slide a real commitment table, populate it live, and capture commitments verbatim — "we'll explore that" is never written down as "Partner committed to X." Shape it per the plugin's QBR template.

## Guardrails

- A QBR with no commitments is a status meeting — action items without dates and owners are findings waiting to be re-raised.
- Raw absolute counts mislead across partner sizes, and a percentage with no baseline gets you asked the question you can't answer — normalize and baseline every number.
- Never present student-level or small-cohort data without the FERPA cohort-residual screen; keep all examples generic, no real student data.
