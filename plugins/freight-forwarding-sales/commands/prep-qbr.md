---
description: "Prepare a Quarterly Business Review for a freight key account — a deck outline led by the CUSTOMER's outcomes (value delivered, honest assessment, next-quarter goals, joint action plan), not the forwarder's activity."
argument-hint: "[account + data, e.g. 'Acme Corp, Q2: 340 TEU, 96% on-time, 2 claims resolved']"
---

# Prep a QBR

You are running `/freight-forwarding-sales:prep-qbr`. Build a QBR for the account/data the user gave (`$ARGUMENTS`), using this plugin's `key-account-manager` discipline and the `qbr-account-planning` skill.

## Steps
1. **Gather the inputs** — period, lanes/volumes, service KPIs (on-time %, claims/exceptions, cost saved), open issues, the customer's stated goals. Flag which numbers are the customer's real data vs placeholders to fill.
2. **Build the 5-part deck outline:**
   - Partnership recap (factual, one slide).
   - **Value delivered** — tied to the customer's KPIs (lead with their results).
   - Honest assessment — what was hard, owned plainly (credibility).
   - Next-quarter goals — the **customer's** objectives and how you support them.
   - Joint action plan — actions with **named owners + dates**, both sides.
3. **Surface whitespace** — modes/lanes/services they buy elsewhere, as a growth thread for the goals section (pull from `key-account-manager` / `pipeline-forecast-coach`).
4. **Flag any service-recovery item** to address head-on (don't bury it).
5. Emit the deck outline in the Output Contract format + the Structured Output JSON block.

## Guardrails
- Lead with the customer's outcomes, never the forwarder's shipment count.
- A QBR without a joint action plan (owners + dates) is just a status meeting — don't ship one.
- Bring data; flag real-vs-placeholder numbers explicitly.
- Address what went wrong candidly — a too-perfect QBR isn't believed.
