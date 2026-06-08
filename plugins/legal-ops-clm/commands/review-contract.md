---
description: "Redline a contract draft against standard/fallback positions, flag the material deviations by risk tier, extract key terms, and route approval — operational support, not legal advice."
argument-hint: "[the draft or contract type + the standard/fallback positions (or ask to build them) + value/risk]"
---

You are running `/legal-ops-clm:review-contract`. Use `contract-review-specialist` + the `contract-review-and-redline` skill.

> Operational/process support only — not legal advice. A lawyer sets the standard/fallback positions and signs off on any deviation. This command flags, structures, and routes — it does not adjudicate. State this in the output.

## Steps
1. If no clause library exists, build one: for each key clause (LoL, indemnity, IP, term/termination, confidentiality) a standard, a fallback, and a walk-away line — flagging that a lawyer must set/confirm them.
2. Compare the counterparty draft to standard/fallback; surface only the **material** deviations (the ones that change risk), noting the rest without escalating.
3. Tier each deviation (within fallback / beyond fallback / walk-away) and name the approver it routes to.
4. Extract the key terms into a structured schema (parties, value, dates, liability cap, indemnity scope, IP, termination, governing law, renewal mechanics) for the repository.
5. Route the playbook wiring → legal-ops-lead; the obligations/dates the terms create → obligations-and-renewals-analyst; privacy/DPA clauses → data-governance-privacy; security terms → security-reviewer; any legal opinion or deviation sign-off → a human lawyer.
6. Emit the redline review + key-term extraction + the Structured Output block (with `Not legal advice:` and `Handoff:`).
