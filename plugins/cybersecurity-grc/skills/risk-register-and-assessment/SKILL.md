---
name: risk-register-and-assessment
description: "Build a risk register (assets, threats, likelihood x impact scoring), drive control selection from risk rather than from a framework checklist, choose a treatment per risk (mitigate / accept / transfer / avoid), and track residual risk with a named owner — so every control traces to a risk and every top risk has a control."
---

# Risk Register & Assessment

## Risk drives controls, not the reverse
Start from the assets worth protecting, the threats against them, and the likelihood × impact of each. Then select controls that treat the top risks. A control with no risk behind it is cost without benefit; a top risk with no control is the real exposure. Common methodologies: ISO 27005, NIST 800-30 (mark specifics `[verify-at-build]`).

## Score consistently
Use a documented likelihood × impact scale (e.g. a 5×5 matrix) applied the same way across every risk, so prioritization is comparable. Score inherent risk, apply the treating control, then score residual risk — the delta is what the control bought.

## Choose a treatment per risk
Every risk gets one of four decisions: **mitigate** (add/strengthen a control), **accept** (document and own the residual, with sign-off), **transfer** (insurance/contract), or **avoid** (stop the activity). "Accept" is a legitimate choice when documented and owned; an un-owned accepted risk is just an ignored one.

## Owner and review cadence
Every register row has a named owner and a review date. The register is a living document reviewed at a set cadence (and on material change), not a one-time spreadsheet — it feeds the Statement of Applicability and the control roadmap.

## Output
A scored risk register (assets, threats, likelihood × impact, treating control, treatment decision, owner, residual risk) that drives control selection. Feed it to `grc-architect`'s SoA and crosswalk; hand control implementation + evidence to `control-and-evidence-engineer`.
