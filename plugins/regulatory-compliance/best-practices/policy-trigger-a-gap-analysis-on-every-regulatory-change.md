# Trigger a Gap Analysis on Every Material Regulatory Change

**Status:** Absolute rule
**Domain:** Policy / regulatory change management
**Applies to:** `regulatory-compliance`

---

## Why this exists

Firms that copy their prior-year policies and update the date without re-checking against current regulation are the ones regulators find deficient at examination. Regulatory change is continuous — FATF mutual evaluation cycles, annual rule amendments from the BMA, CIMA, JFSC, and GFSC, and periodic Basel implementation milestones all alter the obligation landscape. A policy that accurately cited the law when written can be materially non-compliant within 18 months if no one has read the amending rule. The gap analysis is the mechanism that converts a regulator-published change into a named obligation delta and a documented remediation plan.

## How to apply

When a material regulatory change is identified (new rule, amending rule, guidance paper, enforcement action in the sector), run a structured gap analysis before updating any policy.

```
Regulatory Change Gap Analysis — Steps
────────────────────────────────────────
Step 1 — IDENTIFY THE CHANGE
  Source: regulator primary publication (not a law-firm summary)
  Cite: Act/Rule/Guidance title, section, effective date
  Effective date vs firm's next policy review cycle

Step 2 — MAP TO CURRENT OBLIGATIONS
  List every current policy, procedure, and control that references
  the superseded section or relies on the prior standard.
  Use the controls-to-obligation matrix (see controls-one-control-one-requirement-traceable.md).

Step 3 — IDENTIFY THE DELTA
  For each mapped item: Does the new rule require a change?
  Change type: New obligation | Amended obligation | Removed obligation | No change

Step 4 — PRIORITIZE
  For each delta: Effective date | Risk if not remediated | Complexity of remediation

Step 5 — REMEDIATION PLAN
  Each delta row: Owner | Target date | Interim control (if applicable) | Sign-off gate

Step 6 — SIGN OFF
  Second-line (CCO / MLRO) approves the gap analysis before policy drafts begin.
  Retain the gap analysis as the audit trail for the policy update.
```

**Do:**
- Read the primary regulator source for every gap analysis, not a law-firm summary — the summary may lag or paraphrase.
- Run the gap analysis against the controls matrix, not just the policy text; a policy change that isn't followed by a control update is incomplete.
- Date the gap analysis and attach it to the updated policy as an exhibit.
- Track open remediation items in the risk register with target dates and owners.

**Don't:**
- Run a gap analysis and then archive it without updating the affected policies — the gap analysis is the starting point, not the deliverable.
- Assume a regulatory change that affects a sister jurisdiction doesn't apply; check the cross-border or equivalent-regime question explicitly.
- Allow the gap analysis to be the CCO's solo opinion — second-line sign-off and a named document reviewer are required.

## Edge cases / when the rule does NOT apply

- **Minor technical amendments** (e.g., a fee schedule update, a formatting requirement on a prescribed form) — a brief memo documenting the change and confirming no substantive policy impact suffices; a full five-step analysis is not required.
- **Guidance notes** (non-binding) — run the gap analysis, but tag the delta items as "best practice" rather than "obligation" and document the distinction.

## See also

- [`../agents/policy-and-procedure-writer.md`](../agents/policy-and-procedure-writer.md) — owns policy gap analysis and drafting.
- [`./policy-separate-policy-from-procedure.md`](./policy-separate-policy-from-procedure.md) — the gap analysis will often reveal that a change affects the procedure layer more than the policy layer; the split matters for routing the update.

## Provenance

Codifies the policy-and-procedure-writer's regulatory change management discipline from CLAUDE.md §3 #11 (cite the primary source) and §4 anti-pattern ("a policy refresh that copies last year's text without re-checking against current regulation"). The five-step structure reflects standard second-line compliance change-management practice.

---

_Last reviewed: 2026-06-05 by `claude`_
