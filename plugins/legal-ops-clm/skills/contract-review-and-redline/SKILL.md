---
name: contract-review-and-redline
description: "Build a clause library with standard / fallback / walk-away positions, run a redline review that flags only the material deviations by risk tier, extract key terms into a structured schema, and route approval by the highest-tier deviation — operational support, not legal advice."
---

# Contract Review & Redline

> Operational/process support only — not legal advice. A lawyer sets the standard/fallback positions and signs off on any deviation; this skill flags, structures, and routes — it does not adjudicate.

## Build the clause library: standard / fallback / walk-away
For each key clause — limitation of liability, indemnity, IP ownership, term/termination, confidentiality — encode the **standard** (preferred) position, the **fallback** (acceptable) position, and the **walk-away** (never-acceptable) line. Set by a lawyer once, applied consistently. The fallback is what lets a non-lawyer negotiate within bounds.

## Redline against the standard — flag what's material
Compare the counterparty draft to standard/fallback. Surface the deviations that change risk; note the rest without escalating. Escalating every comma drowns the signal. Concentrate on the key clauses where exposure concentrates.

## Tier every flag and route approval
Each deviation gets a risk tier — within fallback (self-serve), beyond fallback (escalate to the tier's approver), or walk-away (stop). The tier is the contract between business speed and legal control; it drives who must approve. A flag with no tier and no named approver is just a highlight.

## Extract key terms to a schema
Pull parties, value, effective/term dates, liability cap, indemnity scope, IP ownership, termination rights, governing law, and renewal mechanics into named fields — not prose — so the repository, the obligations tracker, and reporting can consume them.

## Output
A clause library (standard/fallback/walk-away + tier + approver per clause), a structured redline review (material deviations flagged + tiered + routed), and/or a key-term extraction. Hand the playbook wiring to `legal-ops-lead`; the obligations/dates the terms create to `obligations-and-renewals-analyst`; any legal opinion or deviation sign-off to a human lawyer.
