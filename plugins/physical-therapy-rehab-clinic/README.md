# physical-therapy-rehab-clinic

A Claude Code plugin for the **practice-ops + documentation + billing craft of an outpatient physical-therapy / rehab clinic**. Three specialist agents cover scheduling and capacity, defensible documentation and plan-of-care compliance, and therapy billing — backed by decision trees, skills, templates, best-practices, and an advisory documentation hook.

> **Advisory only — not medical, legal, or billing/coding advice.** Decision-support for clinic owners, office managers, clinicians, and billers; the clinic's licensed clinicians, certified coders, and payor contracts are the authority. **Every regulatory/payor specific carries a retrieval date + `verify-at-use`** (advisory numbers are `[ESTIMATE]`), and **no patient PII** is used or stored.

## What's inside

- **3 agents**
  - `clinic-operations-lead` — scheduling & capacity, plan-of-care visit cadence, patient flow, cancellation/no-show management, productivity.
  - `clinical-documentation-compliance` — defensible POC documentation, certification/recertification timing, medical necessity, skilled care, the therapy-threshold + KX concept, signatures.
  - `billing-and-revenue` — CPT timed codes & the 8-minute rule, units, modifiers (GP/KX/59), denial prevention & appeals, payor mix.
- **5 skills** — `schedule-and-capacity-planning`, `defensible-documentation`, `therapy-billing-and-units`, `denial-prevention-and-appeals`, `plan-of-care-management`.
- **Knowledge bank** — `pt-clinic-decision-trees.md` (4 Mermaid trees: 8-minute-rule units, documentation defensibility, certification vs recertification timing, denial triage) and `pt-clinic-reference-2026.md` (dated reference; figures `[verify-at-use]` / `[ESTIMATE]`).
- **8 best-practices** — one rule per file (medical necessity every visit, the 8-minute rule, certify before lapse, skilled care in the note, match the modifier, no-shows as a revenue leak, defensible notes beat appeals, verify payor rules before you bill).
- **3 templates** — plan-of-care, daily-note-skeleton, denial-appeal-letter.
- **3 commands** — `/calc-therapy-units`, `/review-documentation`, `/plan-clinic-capacity`.
- **1 advisory hook** — `check-pt-documentation-smells.sh` (3 checks; `PTCLINIC_STRICT=1` to block).

## Install

```shell
/plugin marketplace add ./            # from a separate Claude Code project
/plugin install physical-therapy-rehab-clinic@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.

## Boundaries (cross-link, don't duplicate)

- Generic medical revenue-cycle (clearinghouse, A/R aging, payer enrollment) → [`medical-revenue-cycle`](../medical-revenue-cycle/CLAUDE.md).
- Mental-health / behavioral clinics → [`behavioral-health-practice`](../behavioral-health-practice/CLAUDE.md).

## Team constitution

See [`CLAUDE.md`](CLAUDE.md) for the full team constitution, routing rules, house opinions, and the safety posture.
