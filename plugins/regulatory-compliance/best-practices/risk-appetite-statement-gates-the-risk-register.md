# The Risk Appetite Statement Gates the Risk Register

**Status:** Absolute rule
**Domain:** Risk management / governance
**Applies to:** `regulatory-compliance`

---

## Why this exists

A risk register built without a risk appetite statement is a list of concerns with no calibration device. Without the appetite, the residual-risk ratings in the register have no anchor: "medium residual" is meaningless unless the firm has stated whether medium risk is within appetite, at its boundary, or above it. The result is a register that supports management discussions but cannot answer the one question it exists to answer: where is the firm over- or under-controlled relative to what the board has approved? Regulators specifically check that the risk appetite is board-approved, that it flows to the risk register, and that the register's red items have escalation paths.

## How to apply

Before building or refreshing a risk register, confirm that a board-approved Risk Appetite Statement (RAS) exists and that the register's rating scale maps to it.

```
Risk Appetite Statement — Minimum Components (for RAS or RAS check)
─────────────────────────────────────────────────────────────────────
1. BOARD APPROVAL REFERENCE
   Board minute or resolution: <date> — "Board approved RAS v<X.Y>"

2. APPETITE CATEGORIES (one per principal risk class)
   Risk class | Appetite level | Threshold metric
   e.g., "AML/Sanctions | Zero tolerance | Any confirmed SAR or SDN hit triggers board notification"
   e.g., "Operational risk | Low | < $X loss per quarter outside insurance recovery"
   e.g., "Strategic/business risk | Moderate | Combined ratio within X% of target"

3. RISK REGISTER LINKAGE
   Rating scale used in the register: 1–5 × 1–5 (or equivalent)
   RAG map:
     Green = within appetite (residual ≤ appetite level)
     Amber = at boundary — requires action plan within 30 days
     Red = above appetite — requires immediate escalation to board/audit committee

4. ESCALATION PATH
   Amber items: CCO quarterly review
   Red items: Board or audit committee — next scheduled meeting or sooner
```

**Do:**
- Update the RAS when the board's risk appetite changes — a RAS last approved 3 years ago during a different rate environment may not reflect the current strategic intent.
- Map every risk register "red" item to an escalation entry in board or committee minutes — the trail from register to board action is the evidence an examiner expects.
- For regulated entities, check whether the regulator prescribes minimum appetite thresholds (e.g., the BMA or PRA requires explicit statements for certain risk classes) — cite those in the RAS.

**Don't:**
- Write a risk register in which all items are "within appetite" without asking whether the RAS is stringent enough — an all-green register on a high-risk business is a calibration failure, not a success.
- Allow the CCO to set the RAS without board approval — appetite is a governance instrument.
- Use "we have a low appetite for compliance risk" as the entirety of the appetite statement; appetite is meaningful only when paired with a threshold that makes it testable.

## Edge cases / when the rule does NOT apply

- **Pre-formation entities** building the RAS for the first time — the register can be built in parallel with the RAS draft, but the RAS must be board-approved before the register is used to drive control investment decisions.
- **Narrow-scope risk registers** (e.g., a single-product operational risk assessment, not the enterprise register) — the enterprise RAS still applies; the scope is a subset, not a separate appetite.

## See also

- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — owns risk appetite statement design and risk register build.
- [`./controls-inherent-residual-target-are-three-ratings.md`](./controls-inherent-residual-target-are-three-ratings.md) — the three-ratings rule is meaningless without the RAS to calibrate what "target" means for a given risk class.

## Provenance

Codifies the risk-and-controls-specialist's RAS discipline from CLAUDE.md §3 #4 ("risk appetite drives controls, not the other way around") and the `risk-register-build` skill. The board-approval and escalation-path requirements reflect standard IAIS, PRA, and Basel Pillar-2 governance expectations.

---

_Last reviewed: 2026-06-05 by `claude`_
