---
name: regulatory-mapping
description: Map internal controls / policies / procedures to specific regulatory citations (regulator + section + paragraph). Gap-analysis output format. Used by `risk-and-controls-specialist` + `policy-and-procedure-writer`.
---

# Skill: regulatory-mapping

**Purpose:** Map internal controls / policies / procedures to specific regulatory citations. Used by `risk-and-controls-specialist` and `policy-and-procedure-writer`.

## When to use

- New regulation issued — gap analysis vs existing controls / policies
- Pre-exam — examiner will want the control-to-rule mapping
- Building a regulatory inventory for a new licence or jurisdiction
- Refreshing controls after a regulatory amendment
- Multi-jurisdiction coordination — same control, multiple regulatory bases

## The output: a regulatory map

A clean mapping looks like this:

| Regulator | Regime | Citation | Requirement (1-line) | Internal control | Control owner | Evidence type | Last tested |
|---|---|---|---|---|---|---|---|
| BMA | Insurance Act 1978 | §6A(1) | Maintain prescribed capital | BSCR submission process | Group CRO | BMA-submitted CSR | YYYY-MM-DD |
| BMA | AMLR 2008 | Reg 11(1) | CDD on customers | KYC onboarding workflow | MLRO | KYC file sample | YYYY-MM-DD |
| OFAC | 31 CFR 501 | §501.601 | Maintain records 5 yrs | Recordkeeping policy + system retention | Compliance Officer | Audit log | YYYY-MM-DD |

## Building the map

### Step 1 — Inventory the regulation

Read the regulator's actual published rule. Don't trust a vendor summary. Extract:

- Citation (regulator + regime + section + paragraph)
- 1-line requirement (in plain English, not regulator-speak)
- Frequency (one-time, periodic, on-event)
- Penalty (informational — informs prioritization)

### Step 2 — Inventory existing controls

From the firm's control library or risk register. Extract:

- Control ID
- Control statement (1-line)
- Owner (named, not functional)
- Frequency (manual / automated; daily / weekly / monthly / etc.)
- Evidence type (system log / report / signed memo / etc.)

### Step 3 — Map (and find the gaps)

For each regulatory requirement, identify the control(s) that address it.

Four states emerge:

- **Covered** — one or more controls address the requirement, owners aligned, evidence available
- **Under-controlled** — control exists but doesn't fully satisfy the requirement (gap)
- **Over-controlled** — multiple controls testing the same requirement (rationalization opportunity)
- **Uncovered** — no control addresses the requirement (priority gap)

### Step 4 — Output

| Status | Citation | Requirement | Existing controls | Gap | Owner | Target date |
|---|---|---|---|---|---|---|

Plus:
- **P0 gaps** — uncovered requirements with regulator visibility
- **P1 gaps** — under-controlled requirements
- **Rationalization candidates** — over-controlled areas

## Common pitfalls

- **Mapping to the wrong source.** Vendor "guides" to regulation are starting points, not authorities. Cite the regulator's actual publication.
- **One-to-one mapping where the actual relationship is one-to-many or many-to-one.** A single requirement might need several controls; a single control might satisfy several requirements.
- **Skipping the frequency check.** A monthly control can't satisfy a real-time requirement.
- **Skipping the evidence check.** A control with no documented evidence is effectively no control.
- **Treating the map as a one-time artifact.** Maps are living — regulation changes, controls change, ownership changes.

## Multi-jurisdiction notes

When the same firm is regulated under multiple regimes:

- Build separate columns per regulator on the same control row
- A control might satisfy multiple regulators with different cited bases
- Where regulators conflict (e.g., data-retention period), document the firm's policy + which regulator's standard it follows + rationale

## See also

- Template: [`../../templates/control-narrative.md`](../../templates/control-narrative.md)
- Template: [`../../templates/risk-register.md`](../../templates/risk-register.md)
- Agent: [`../../agents/risk-and-controls-specialist.md`](../../agents/risk-and-controls-specialist.md)
- Agent: [`../../agents/policy-and-procedure-writer.md`](../../agents/policy-and-procedure-writer.md)
