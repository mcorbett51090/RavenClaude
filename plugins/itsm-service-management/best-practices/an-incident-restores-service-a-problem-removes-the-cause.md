# An incident restores service; a problem removes the cause

**Status:** Absolute rule. **Constitution:** §2 #1.

## Use when
Any ITSM deliverable where this question is in play — read, applied, and cited whole.

## The rule
They are two different jobs with two different success metrics (time-to-restore vs. recurrence-eliminated). Conflating them means you firefight the same fire forever.

## Why it matters
This is a house opinion distilled into a citable rule. IT teams and users live with these decisions daily; a service-management process that ignores this rule doesn't fail loudly — it erodes trust ticket by ticket, breach by breach. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a practice — it sets the framing, not the conclusion.
- Open an incident to restore service now (a workaround counts); open a problem to remove the cause.
- For a recurring incident, run BOTH in parallel — restore the incident, open the problem.
- Measure incidents on time-to-restore and problems on recurrence eliminated, never one number for both.
- Cite a source + date for any benchmark, SLA target, or tool capability, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`service-management-lead`](../agents/service-management-lead.md) to sequence them.

## The anti-pattern this prevents
Treating every recurring outage as 'just another incident,' restoring it again and again while the cause is never removed. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #1 — the house opinion this rule encodes.
- [`../skills/triage-incident-vs-problem/SKILL.md`](../skills/triage-incident-vs-problem/SKILL.md) — the method that applies it.
