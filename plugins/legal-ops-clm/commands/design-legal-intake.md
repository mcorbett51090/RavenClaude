---
description: "Design structured legal intake and triage, the request-to-resolution workflow, a contract playbook (self-serve vs. escalate), and the legal-ops metrics — operational support, not legal advice."
argument-hint: "[current intake pain + request types + team + risk/value thresholds]"
---

You are running `/legal-ops-clm:design-legal-intake`. Use `legal-ops-lead` + the `legal-intake-and-playbooks` skill.

> Operational/process support only — not legal advice. A qualified lawyer owns every legal-judgement call and sets the playbook's bounds. State this in the output.

## Steps
1. Map how legal work enters today; design one structured intake form (request type, risk, value, counterparty, deadline). If intake is already structured, say so and skip ahead.
2. Define the triage rubric (route by risk and value, not arrival order) and an SLA per request class.
3. Build the contract playbook: which request types are self-serve vs. escalate, the pre-approved standard template, the guardrails, and the **bright-line escalation triggers** (value threshold / beyond-fallback deviation / regulated-data touch).
4. Define the matter model (owner, type, status, value, deadline, closure) and the request-to-resolution workflow.
5. Define the legal-ops metrics (cycle time by class, backlog, self-serve rate, escalation/risk mix) — each paired with a decision; flag any vanity count.
6. Route clause-level fallbacks → contract-review-specialist; obligation/renewal tracking → obligations-and-renewals-analyst; any legal opinion → a human lawyer.
7. Emit the intake/triage design + playbook + the Structured Output block (with `Not legal advice:` and `Handoff:`).
