---
description: "Run a gap assessment before fieldwork: control readiness, evidence-cadence check, Type I vs Type II readiness, the auditor PBC list, and third-party risk."
argument-hint: "[target framework + report type + fieldwork date + in-scope controls + vendors]"
---

You are running `/cybersecurity-grc:audit-readiness-review`. Use `audit-and-third-party-risk-lead` + the `evidence-and-audit-readiness` skill.

## Steps
1. Assess each in-scope control's readiness — designed / implemented / operating-effectively — and the evidence behind each claim.
2. Check the evidence cadence: is it collected at the source on a frequency matched to the control, or a pre-audit scramble? Flag controls with no evidence window.
3. Make the Type I vs Type II call against the observation period; identify gaps that would become exceptions and rank remediation by audit risk.
4. Build the PBC (provided-by-client) list and the evidence package; give a fieldwork go/no-go.
5. For vendors: tier by data/access/criticality, set assessment depth (SIG/CAIQ vs SIG-Lite), review critical vendors' SOC 2 exceptions + the CUECs you must run, and own the shared-responsibility boundary.
6. Route technical remediation to security-engineering / the cloud plugins; raise scope/framework gaps to grc-architect.
7. Emit the gap assessment + remediation plan + PBC list + vendor model + the Structured Output block (with `Control state:` and `Handoff to technical teams:`; mark recalled framework specifics `[verify-at-build]`).
