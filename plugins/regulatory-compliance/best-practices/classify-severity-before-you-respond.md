# Classify a regulator finding's severity before you pick a response playbook

**Status:** Primary diagnostic
**Domain:** Examination / supervisory response
**Applies to:** `regulatory-compliance`

---

## Why this exists

When a regulator delivers a finding, the most expensive mistake is misreading **severity** before deciding how to respond. The vocabulary — MRA, MRIA, consent order, self-identified issue — looks interchangeable from outside formal supervision, but the response window, board-paper requirements, remediation funding, counsel involvement, and public-disclosure consequences differ sharply. The dominant failure mode is **misclassifying _down_**: treating an MRIA (immediate action, 30–60 day window, mandatory board reporting) as an MRA (90–180 day plan), which produces a non-urgent posture for an urgent item. Reading the document's *title* instead of its *language* is how that happens.

## How to apply

Traverse [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) `## Decision Tree` top-to-bottom on the actual text of the document, not its heading:

```
Is the regulator the BMA/Bermuda?        -> route to bermuda-insurance-specialist (different vocabulary)
Is it a formal enforcement order?        -> CONSENT ORDER: counsel-led, board approval, disclosure analysis
Does it say "immediate" / cite a repeat? -> MRIA: 30-60 day plan, interim controls in days, board reporting
Examiner-issued (not self-identified)?   -> MRA: timely corrective action, 90-180 day plan typical
Otherwise                                -> Self-Identified Issue: internal plan; notification may still be required
```

**Do:**
- Read the finding for the cues — "immediate", repeat-finding escalation, enforcement-instrument language — not the document title.
- When a branch could go either way, **default to the higher severity**; escalate down only when the higher tier is demonstrably ruled out by the document's language and the examiner's stated intent.
- State the resolved tier and its jurisdiction/regime explicitly in the response (Output Contract `Jurisdiction:` line).

**Don't:**
- Assume a BMA supervisory letter automatically maps to a US MRA — route to `bermuda-insurance-specialist` for the terminology mapping first.
- Treat a consent order or C&D as a compliance-only workflow — counsel leads, the `Legal-advice gate:` line flips to counsel-required.
- Run an internal-audit or second-line control-test finding through this tree — it is for **regulator-written** findings only.

## Edge cases / when the rule does NOT apply

- **Internal-audit, second-line control-test, and firm self-identified issues** use separate workflows — this tree is scoped to regulator-issued findings.
- **Jurisdiction outside US federal banking / Bermuda** — the tree's tiers are anchored to the Federal Reserve SR 13-13 and OCC frameworks (and the BMA carve-out). Another regime needs its own severity ladder; map before applying these timelines.
- **A repeat MRA** — even if not formally re-classified, treat it as escalation-eligible: SR 13-13 names repeat criticisms as MRIA-qualifying, so the board/risk-committee escalation fires regardless.

## See also

- [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) — the decision tree, tradeoffs table, and BMA carve-out this codifies.
- [`../agents/examination-prep-specialist.md`](../agents/examination-prep-specialist.md) — owns MRA/MRIA response drafting; traverses this tree first.
- [`../agents/bermuda-insurance-specialist.md`](../agents/bermuda-insurance-specialist.md) — the mapping when the regulator is the BMA.

## Provenance

Codifies the severity-triage decision tree in [`../knowledge/regulator-finding-severity-triage.md`](../knowledge/regulator-finding-severity-triage.md) (last reviewed 2026-05-22; sourced from Federal Reserve SR 13-13/CA 13-10, OCC News Release 2014-150, with OCC Bulletin 2025-29 flagged as NPR-only / not finalized), and house opinions #11 (provenance on every regulatory claim) and #12 (jurisdiction matters) in [`../CLAUDE.md`](../CLAUDE.md) §3.

---

_Last reviewed: 2026-05-30 by `claude`_
