---
description: "Extract a contract's obligations as owned tracked items, build the renewal/expiry/auto-renew tracker with tiered notice-window alerts, and model the repository metadata — operational support, not legal advice."
argument-hint: "[the signed contract(s) or contract set + key dates + owners]"
---

You are running `/legal-ops-clm:track-obligations-renewals`. Use `obligations-and-renewals-analyst` + the `obligations-and-renewals` skill.

> Operational/process support only — not legal advice. This command extracts, structures, tracks, and alerts on what the contract says; a lawyer interprets ambiguous language. Flag ambiguity for the lawyer rather than guessing. State this in the output.

## Steps
1. Extract the obligations (deliverables, SLAs, payment terms, notice periods, audit rights) into a register — each a tracked item with a **named owner**, a due date or trigger, and a status.
2. Build the renewal/expiry tracker: per contract, the expiry, the auto-renew flag, and the **notice-window deadline** (track the window, not just the end date).
3. Set tiered alerts (90/60/30 days) to the named owner so the renew/renegotiate/exit decision happens before the window closes.
4. Model the repository metadata schema (counterparty, type, value, dates, auto-renew, owner, status, governing law, obligation links) and the reports it enables (expiring-soon, notice-closing, obligation-due, by-value, by-counterparty).
5. Take key-term seeds from contract-review-specialist; feed obligation/renewal health to legal-ops-lead's metrics; flag any ambiguous obligation for a human lawyer.
6. Emit the obligations register + renewal tracker + metadata schema + the Structured Output block (with `Not legal advice:` and `Handoff:`).
