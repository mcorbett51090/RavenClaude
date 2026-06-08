---
description: "Shape a security-compliance program: pick the framework, scope the audit boundary, crosswalk controls across frameworks, and produce the Statement of Applicability."
argument-hint: "[org size + customer/contract demand + existing controls + target frameworks]"
---

You are running `/cybersecurity-grc:scope-compliance-program`. Use `grc-architect` + the `framework-selection-and-control-mapping` skill.

## Steps
1. Establish demand + risk: who is asking for what attestation, org size, and what controls already exist? Right-size the framework (SOC 2 / ISO 27001 / NIST CSF / 800-53) — don't cargo-cult a heavyweight framework.
2. Scope the audit boundary (systems, locations, people, data, third parties) to what can be attested honestly this cycle; defend the carve-outs against the risk register.
3. If multiple frameworks are in play, pick one primary and crosswalk the rest to it (map once, attest many); produce the single primary control set.
4. Author the Statement of Applicability — per control: applicability, justification, status, crosswalk reference; every exclusion justified.
5. Route the builds: control implementation + evidence → control-and-evidence-engineer; audit + vendor risk → audit-and-third-party-risk-lead; technical config → security-engineering / data-governance-privacy / the cloud plugins.
6. Emit the framework + scope recommendation, the crosswalk, and the SoA + the Structured Output block (with `Control state:` and `Handoff to technical teams:`; mark recalled framework specifics `[verify-at-build]`).
