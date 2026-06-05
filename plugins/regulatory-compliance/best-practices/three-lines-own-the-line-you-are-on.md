# Own the Line You Are On — Three Lines Is a Structure, Not a Slogan

**Status:** Absolute rule
**Domain:** Risk and controls / governance
**Applies to:** `regulatory-compliance`

---

## Why this exists

The three-lines model fails in practice when the lines merge: a business-unit manager who "does compliance" for their own team, or a second-line compliance function that operates the controls it is supposed to oversee. When the first and second lines conflate, ownership evaporates — nobody is accountable for designing the control, and nobody is independently checking it. Examiners specifically probe for this; a control narrative that lists the "compliance team" as both the operating entity and the independent reviewer is a finding waiting to happen. The structure exists because independence is what gives the three-lines opinion its value.

## How to apply

For every control in the risk-and-controls framework, state which line owns it, which line oversees it, and which line provides assurance — and verify the ownership is real, not nominal.

```
Three-Lines Ownership Check — Per Control
────────────────────────────────────────────
Control name:             <e.g., Customer risk-rating review at onboarding>

1st Line (Operate):       Named business-unit role (not "compliance")
  Owner name / title:     <e.g., Relationship Manager or Onboarding Team Lead>
  What they do:           <Assign risk rating, complete KYC checklist, submit for approval>

2nd Line (Oversee):       Compliance or risk function — independent of 1st line
  Owner name / title:     <e.g., MLRO or Compliance Manager>
  What they do:           <Periodic QA review of a sample of completed onboarding files;
                           does NOT complete the onboarding — reviews it>

3rd Line (Assure):        Internal audit — independent of both 1st and 2nd
  Owner name / title:     <e.g., Head of Internal Audit>
  What they do:           <Annual or thematic testing of design + operating effectiveness>

Independence test:
  □ 1st line owner ≠ 2nd line reviewer (no self-review)
  □ 2nd line cannot sign off on their own work
  □ 3rd line is not accountable to the CCO or CFO for their findings
```

**Do:**
- Document the three-lines ownership in every control narrative — not just in the risk register.
- Re-test independence annually: team restructurings, budget pressures, and "acting" arrangements frequently erode the line separation without anyone noticing.
- When a small firm cannot staff all three lines independently, document the compensating control (e.g., "board audit committee acts as third line") and disclose it in the control narrative.

**Don't:**
- Let "compliance" appear as the owner on the 1st-line column of the controls matrix — compliance owns 2nd-line oversight of business-unit controls, not the controls themselves (except for controls inherent to the compliance function).
- Accept "the CCO reviews all compliance matters" as a substitute for a genuine second-line review of first-line controls.
- Conflate the 2nd-line compliance testing with the 3rd-line internal-audit assurance — they use different scopes, methodologies, and reporting lines.

## Edge cases / when the rule does NOT apply

- **Single-function controls unique to the compliance team** (e.g., the MLRO's own SAR-filing decision) — the MLRO is both first and second line for the SAR decision itself; document this explicitly and ensure the board or audit committee provides the assurance layer.
- **Regulated entities too small to maintain all three lines independently** — FATF guidance and most regulator codes acknowledge proportionality; document the alternative governance structure and the explicit compensating controls.

## See also

- [`../agents/risk-and-controls-specialist.md`](../agents/risk-and-controls-specialist.md) — owns the three-lines framework and risk register design.
- [`./controls-one-control-one-requirement-traceable.md`](./controls-one-control-one-requirement-traceable.md) — a control must be mapped to its regulatory requirement before the three-lines ownership can be correctly assigned.

## Provenance

Codifies the risk-and-controls-specialist's three-lines discipline from CLAUDE.md §3 #3 ("Three lines of defense are not a slogan") and the `risk-register-build` skill. The independence test criteria reflect the IIA's 2020 Three Lines Model and standard FATF/Basel Committee governance expectations.

---

_Last reviewed: 2026-06-05 by `claude`_
