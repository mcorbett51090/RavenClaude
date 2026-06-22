# The CMDB is only as good as its maintenance discipline

**Status:** Absolute rule. **Constitution:** §2 #6.

## Use when
Any ITSM deliverable where this question is in play — read, applied, and cited whole.

## The rule
An unmaintained CMDB is worse than none — it gives confident wrong answers. Automate discovery, define what's a CI and why, and audit drift, or don't claim to have one.

## Why it matters
This is a house opinion distilled into a citable rule. IT teams and users live with these decisions daily; a service-management process that ignores this rule doesn't fail loudly — it erodes trust ticket by ticket, breach by breach. The rule is cheap to apply and expensive to skip.

## How to apply
- Apply this **before** reaching for a practice — it sets the framing, not the conclusion.
- Scope CIs to what serves a decision (impact analysis, change, incident); drop CI types that serve nothing.
- Feed the CMDB from automated discovery; manual entry rots.
- Define the drift-audit cadence and owner before declaring the CMDB authoritative.
- Cite a source + date for any benchmark, SLA target, or tool capability, or mark it `[unverified — training knowledge]` / `[ESTIMATE]`.
- When this rule and another both apply, route to [`service-management-lead`](../agents/service-management-lead.md) to sequence them.

## The anti-pattern this prevents
A CMDB built once in a big project, never maintained, that now misleads every impact analysis with stale relationships. The plugin's advisory hook flags a deliverable that reads as if this rule were ignored.

## See also
- [`../CLAUDE.md`](../CLAUDE.md) §2 #6 — the house opinion this rule encodes.
- [`../skills/build-the-cmdb/SKILL.md`](../skills/build-the-cmdb/SKILL.md) — the method that applies it.
