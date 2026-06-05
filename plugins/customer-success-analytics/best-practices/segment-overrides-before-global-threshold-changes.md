# Apply segment overrides before loosening global thresholds

**Status:** Pattern
**Domain:** CS analytics — tier tuning
**Applies to:** `customer-success-analytics`

---

## Why this exists

When the Red list is dominated by a single account segment that keeps renewing (e.g., SMB accounts all show high support-ticket volume because SMB is self-serve by design), the instinct is to loosen the global threshold. Loosening globally reduces false-Red rates for the SMB segment but simultaneously reduces sensitivity for enterprise accounts where the same threshold was correctly calibrated. The tier is tuned twice and ends up accurate for neither. A segment override — a different threshold for the over-flagging segment — is the targeted fix.

## How to apply

When the false-Red rate is above 25% and the over-flagged accounts are concentrated in one segment:

```
1. Confirm segment concentration:
   → What % of false Reds are in segment X vs. the rest of the book?
   → If segment X accounts for > 50% of false Reds: segment override is the right fix

2. Diagnose why the segment over-flags:
   → Structural difference (SMB is self-serve → higher support volume is normal)
   → Lifecycle difference (new accounts always have low usage initially)
   → Vertical difference (academic calendars create seasonal usage dips that aren't churn risk)

3. Design the segment-specific threshold:
   → Keep the global threshold for all other segments
   → Set a higher threshold for the over-flagging segment, documented and versioned
   → Run a parallel back-test on the segment-specific threshold before deploying

4. Document the override:
   → Why this segment needs a different threshold
   → What back-test result justified the override value
   → Review date (segment behavior can change — revisit annually or after a major product change)
```

**Do:**
- Keep a written record of every segment override — an undocumented override is a configuration debt item.
- Run a parallel test on both the old global threshold and the new segment override before deploying.

**Don't:**
- Apply a segment override before confirming the concentration is in that specific segment — a diffuse false-Red problem needs a global threshold loosening, not an override.
- Create overlapping or contradictory segment overrides — one override per segment maximum.

## Edge cases / when the rule does NOT apply

- False-Red accounts are evenly distributed across all segments (no concentration) — the problem is global threshold over-sensitivity; loosen the global threshold with a parallel test, do not create segment overrides.

## See also

- [`../knowledge/customer-success-decision-trees.md`](../knowledge/customer-success-decision-trees.md) — the retune-or-rebuild tree that routes to this rule
- [`../agents/churn-signal-analyst.md`](../agents/churn-signal-analyst.md) — the agent that diagnoses tier misfires and recommends overrides

## Provenance

Codifies the "Add Segment Override" leaf in the health-tier-retune decision tree (`customer-success-decision-trees.md` §2). A global loosening in response to a segment-specific problem is a predictable mis-application of the retune procedure.

---

_Last reviewed: 2026-06-05 by `claude`_
