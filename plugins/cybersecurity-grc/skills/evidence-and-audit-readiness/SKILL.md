---
name: evidence-and-audit-readiness
description: "Set the control-testing cadence, build evidence collection and continuous control monitoring, decide Type I vs Type II readiness, run a gap assessment and manage the auditor PBC list, and own third-party risk — vendor tiering, SIG/CAIQ, shared-responsibility, and ongoing monitoring — so evidence is a system and the audit holds no surprises."
---

# Evidence & Audit Readiness

## Evidence is a system, not a fire drill
Collect evidence automatically at the source (API export, log, config snapshot) on a cadence matched to each control's frequency, then retain it. A pre-audit screenshot scramble means the control isn't reliably operating. One artifact should serve every framework the control maps to.

## Track the three control states for the report type
Type I is a point-in-time design opinion; Type II / certification needs evidence the control *operated* across the observation period without exception. Don't chase a report date past the evidence window — a control with no window becomes an exception.

## Gap assessment before fieldwork
Assess each in-scope control's readiness (designed / implemented / operating-effectively), surface the evidence gaps that would become exceptions, rank remediation by audit risk, and give a fieldwork go/no-go. An honest gap assessment means no surprise findings. Manage the auditor PBC (provided-by-client) list proactively, not reactively during fieldwork.

## Third-party risk, proportional to the tier
Tier vendors by data sensitivity + access + criticality. Assess proportionally — full SIG/CAIQ for the critical few, SIG-Lite or attestation for the tail. Read a vendor's SOC 2 scope, period, exceptions, and the complementary user-entity controls *you* must run. Own the shared-responsibility boundary; set an ongoing-monitoring cadence.

## Output
A control-testing cadence + CCM plan, a Type I/II readiness call, a gap assessment + ranked remediation + PBC list, and a vendor tiering + assessment model with shared-responsibility and monitoring. Route technical remediation to `security-engineering` / the cloud plugins; raise scope/framework gaps to `grc-architect`.
