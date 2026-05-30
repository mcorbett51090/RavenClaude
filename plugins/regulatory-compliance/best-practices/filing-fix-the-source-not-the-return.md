# Fix the source, not the return — never apply a hidden adjustment inside a filing

**Status:** Absolute rule
**Domain:** Regulatory reporting — data integrity
**Applies to:** `regulatory-compliance`

---

## Why this exists

When source data is wrong, the tempting shortcut is to "fix" the number in the return — an override in the workbook cell, a plug to make the schedule tie. That is the one move that turns a data-quality problem into an integrity problem. A hidden adjustment breaks the lineage (the return cell no longer reconciles to the system of record), it hides the underlying defect (so the source stays broken and re-breaks next period), and it is exactly what an examiner finds when they trace a cell back and the source doesn't support it. The discipline is the opposite: if the source is wrong, fix the source, document the impact, and let the corrected source flow through. Where the source genuinely can't be corrected in time, the limitation is *disclosed*, not papered over. Known source-data issues are raised to the controller before filing, never absorbed quietly into the return.

## How to apply

When the lineage reveals bad source data, route it to one of three honest outcomes — never an in-return plug:

```
Source is wrong?
   -> FIX THE SOURCE      correct the system of record; document the impact on the return; re-run the cell
   -> CAN'T FIX IN TIME   disclose the limitation in the filing + raise to the controller pre-submission
   -> ALREADY FILED WRONG  follow the regulator's formal AMENDMENT/restatement process — don't quietly resubmit
NEVER                     apply an undisclosed adjustment inside the return to make it tie
```

A restatement is a separate filing event with its own disclosure of what changed and why — not a silent re-upload.

**Do:**
- Correct the system of record and let the fix flow through; document the impact at the line level.
- Raise known source-data quality issues to the controller before filing (don't carry them silently).
- Treat a discovered prior-period error as a formal amendment with disclosure of what changed and why.

**Don't:**
- Plug or override a cell in the return to make a schedule tie — that severs the lineage.
- "Fix it in the next filing" without a formal amendment process for the prior period.
- Quietly resubmit a corrected return — restatement follows the regulator's amendment process and discloses the change.

## Edge cases / when the rule does NOT apply

- **Legitimate documented adjustments** (statutory-vs-GAAP, admitted-vs-non-admitted, consolidation eliminations) are *part of the methodology*, not hidden plugs — they belong in the transform step of the lineage with their basis recorded.
- **Materiality of the error** governs whether amendment vs next-period correction is required `[verify-at-build — amendment thresholds and statutes of limitation are regulator-specific]`; route the threshold call with the regime's own materiality definition (house opinion #7, #12).
- **Legal-opinion gate** — whether a restatement triggers a disclosure obligation or penalty exposure routes to counsel; the operational correction and impact documentation continue.

## See also

- [`./filing-source-trace-every-load-bearing-cell.md`](./filing-source-trace-every-load-bearing-cell.md) — the lineage that surfaces the bad source.
- [`./filing-explain-the-variance-before-you-submit.md`](./filing-explain-the-variance-before-you-submit.md) — a variance is the signal that a source may be wrong.
- [`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md) — "Don't fix data in the return"; "Restatement is a separate filing event."

## Provenance

Codifies the `regulatory-reporting-analyst` opinions "Don't fix data in the return. If the source data is wrong, fix the source (and document the impact)" and "Restatement is a separate filing event," and the anti-patterns "'adjustment' applied inside the return without a corresponding fix at the source," "'we'll fix it in the next filing' without a formal amendment process," and "source-data quality issues known but not raised to the controller before filing" ([`../agents/regulatory-reporting-analyst.md`](../agents/regulatory-reporting-analyst.md)).

---

_Last reviewed: 2026-05-30 by `claude`_
