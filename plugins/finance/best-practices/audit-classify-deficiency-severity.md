# Classify a control deficiency by severity — CD, SD, or material weakness

**Status:** Absolute rule — calling every exception a "finding" (or burying a material weakness as a minor one) misstates the control environment; severity is a defined judgment, not a vibe.

**Domain:** Audit / internal controls

**Applies to:** `finance`

---

## Why this exists

When a control test fails, the exception has to be **classified by severity** — control deficiency (CD), significant deficiency (SD), or material weakness (MW) — and that classification drives everything downstream: what gets remediated first, what's disclosed, what management has to certify. The `soc-control-walkthrough` skill mentions CD/SD/MW but no standalone rule made it the citable judgment an auditor/controller reaches for. Without a defined ladder, teams either over-escalate every minor gap (alarm fatigue) or quietly downgrade a real material weakness (the dangerous direction). This rule states the ladder and the two dimensions that set it.

## How to apply

Severity is a function of **likelihood** (could it let a misstatement through?) × **magnitude** (how big could that misstatement be?), assessed against materiality — not the cosmetic size of the control gap:

- **Control deficiency (CD)** — the control doesn't operate, or doesn't operate effectively, but the potential misstatement is **less than significant**. Track and remediate; not individually disclosable.
- **Significant deficiency (SD)** — less severe than a material weakness, but **important enough to merit attention by those charged with governance** (audit committee). A reasonable possibility of a more-than-inconsequential misstatement.
- **Material weakness (MW)** — a **reasonable possibility** that a **material** misstatement would not be prevented or detected timely. This is the disclosable, certification-affecting one.

**Aggregate before you conclude:** several individually-minor CDs over the *same* assertion/account can **combine** into an SD or MW — assess the cluster, not just each in isolation.

**Apply the compensating-control downgrade carefully:** a compensating control can reduce severity **only** if it operates at a level of precision that would catch the misstatement — document why it qualifies, don't assume it.

**Do:** classify on likelihood × magnitude vs materiality; aggregate related deficiencies; document a compensating-control downgrade with its precision rationale; escalate SD/MW to those charged with governance.

**Don't:** label every exception a generic "finding"; downgrade an MW because remediation is inconvenient; treat a compensating control as an automatic downgrade without evidence it's precise enough.

## Edge cases / when the rule does NOT apply

A deficiency in a control over an **immaterial, low-risk** account may genuinely be a CD even if the control fully failed — magnitude caps severity. Fraud-related deficiencies and deficiencies in controls over the financial-reporting *process itself* (period-end close, journal entries) carry heightened scrutiny and bias toward SD/MW regardless of the single-instance magnitude. Specific framework definitions (PCAOB AS, COSO) and any regulator-specific severity vocabulary are framework-/jurisdiction-specific — `[verify-at-build]`.

## See also

- [`./audit-controls-need-an-owner-frequency-and-evidence.md`](./audit-controls-need-an-owner-frequency-and-evidence.md) — the control attributes a deficiency is measured against
- [`../agents/audit-prep-specialist.md`](../agents/audit-prep-specialist.md) — owns deficiency classification
- [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md) — the audit/close decision trees
- PCAOB AS 2201 / COSO Internal Control–Integrated Framework — authoritative (`[verify-at-build]` the current standard)

## Provenance

Surfaced by the two-panel + tiebreak coverage campaign (2026-06-01): the `audit-prep-specialist` owns deficiency work and the SOC walkthrough skill mentions CD/SD/MW, but no standalone citable rule made the severity classification the durable judgment. Grounded in PCAOB/COSO deficiency-severity definitions. Framework specifics are `[verify-at-build]`. (The matching deficiency-severity *tree* ships in [`../knowledge/finance-decision-trees.md`](../knowledge/finance-decision-trees.md).)

---

_Last reviewed: 2026-06-01 by `claude`_
