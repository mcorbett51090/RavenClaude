---
scenario_id: 2026-06-08-clean-scan-was-not-conformance
contributed_at: 2026-06-08
plugin: accessibility-engineering
product: audit
product_version: "n/a"
scope: likely-general
tags: [conformance, automated-tools, manual-testing, screen-reader]
confidence: medium
reviewed: false
---

## Problem

A team ran axe across the product, got near-zero violations, and told procurement they were 'WCAG 2.1 AA conformant.' The risk: automated tools detect only a fraction of WCAG issues and none of the human-judgment criteria, so a clean scan bounds the floor of how bad things are — it is never a conformance claim (§3 #2).

## Context

- Surface: a transactional web app; AA was the contractual floor.
- Constraint: conformance is per-success-criterion at the target level, and many criteria (focus order, alt-text meaning, name/role/value) cannot be machine-judged (§3 #1 #2).
- The team reasoned from the tool's summary number.

## Attempts

- Tried: **manual keyboard pass + screen-reader session** before trusting the scan. Outcome: the primary form had an illogical focus order and a custom dropdown announced nothing to the screen reader — both invisible to the scanner (§3 #2 #3).
- Tried: **checked the human-judgment criteria by hand** (alt text, name/role/value). Outcome: decorative images carried meaningless alt text and an icon button had no accessible name — Level-A failures.
- Tried: **re-scored against the named target** via `accessibility_calc.py conformance`. Outcome: Level-A blockers present, so not shippable as conformant regardless of the AA pass count (§3 #1).

## Resolution

The fix was to **retract the conformance claim, fix the Level-A blockers, and re-audit with manual + AT testing** against WCAG 2.1 AA — not to ship the scan number. The output was a criterion-level audit, the blocker list, and a weighted score against the target.

**Action for the next consultant hitting this pattern:** **a clean automated scan is a floor, not a conformance claim.** Pair every scan with a manual keyboard pass and a screen-reader session for the criteria tools cannot judge, and surface Level-A blockers separately from the score. See Tree 1 and the `accessibility_calc.py` `conformance` mode.

Benchmark figures are segment-/region-/date-dependent — treat as `[unverified — training knowledge]` and validate against the client's own data before any deliverable (§3 #8).
