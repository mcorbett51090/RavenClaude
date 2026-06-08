# One definition of pipeline

**Status:** Absolute rule
**Domain:** GTM analytics and reporting
**Applies to:** `revenue-operations`

---

## Why this exists

"We have $12M in pipeline" means nothing if the AE, the sales manager, the CRO, and the CFO are
each counting something different. The AE counts every deal they've touched. The manager counts
Stage 3+. The CRO counts Stage 3+ with a close date this quarter. The CFO counts the weighted
forecast from Stage 4+. All four are talking about "the pipeline" in a Monday-morning review, and
none of them are having the same conversation.

Parallel definitions of pipeline destroy three things at once: forecast accuracy (different
denominators), alignment between go-to-market and finance (quota-to-pipeline coverage cannot be
calculated if the denominator changes between teams), and trust in the CRM (if the CEO knows
the number is interpreted differently in every meeting, the number loses meaning).

RevOps's job is to own the canonical definition and hold the line on it.

## How to apply

1. **Write the canonical definition.** At minimum, define: what stages are included, what date
   range qualifies (close date this quarter, this half, rolling 12 months), what minimum deal
   size is included, and whether it is ACV/ARR or TCV.
2. **Publish and circulate the definition.** It lives in the CRM as a saved report or view, in
   the RevOps wiki, and in the quarterly business review template. Every leader who uses the word
   "pipeline" in a recurring meeting should have the definition in front of them.
3. **Create one canonical CRM view.** The pipeline view that feeds the forecast is the view.
   Not a manager's custom filter. Not a spreadsheet export. The CRM view.
4. **Challenge shadow pipelines immediately.** When a team starts maintaining a "real" pipeline
   outside the CRM (spreadsheet, board, Slack thread), ask why — the answer is usually a data
   quality problem in the CRM, not a deficiency in the definition.

**Do:**

- Define pipeline once, in writing, with the specific criteria (stage range, close-date range,
  ACV floor, excluded deal types).
- Use one CRM saved report or view as the canonical source.
- Review the definition at least annually; update it formally when the sales process changes.
- When two stakeholders cite different pipeline numbers, diagnose the definition gap first — do
  not average the numbers.

**Don't:**

- Allow individual managers to maintain their own pipeline definitions for their "real" view.
- Let the pipeline definition drift informally over time without a formal update.
- Treat different pipeline numbers as "both valid from different perspectives" — pick one and
  enforce it.
- Allow the CFO to use a different pipeline number than the CRO in the same planning process.

## Edge cases / when the rule does NOT apply

Multiple pipeline views are appropriate when they are named and layered — for example, "total
pipeline (all stages)" vs. "qualified pipeline (Stage 3+)" vs. "forecast pipeline (Commit category)"
are distinct, named views that serve different purposes. The rule is: each name maps to exactly
one definition, and the definitions are not competing — they are explicitly nested. The problem is
not multiple views; it is unlabeled, competing definitions of the same term.

## See also

- [`./stages-are-exit-criteria-not-vibes.md`](./stages-are-exit-criteria-not-vibes.md)
- [`./a-forecast-is-a-commitment-not-a-hope.md`](./a-forecast-is-a-commitment-not-a-hope.md)
- [`../agents/revops-lead.md`](../agents/revops-lead.md)

## Provenance

Codifies the RevOps community consensus on system-of-record discipline and definitional alignment.
Consistent with the "single source of truth" principle in Sirius Decisions (now Forrester) GTM
frameworks and standard RevOps practitioner guidance.

---

_Last reviewed: 2026-06-08 by `claude`._
