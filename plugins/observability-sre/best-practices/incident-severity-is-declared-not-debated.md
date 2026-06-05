# Declare incident severity immediately — debate it in the retrospective

**Status:** Absolute rule
**Domain:** Incident response
**Applies to:** `observability-sre`

---

## Why this exists

When engineers spend the first ten minutes of an incident discussing whether it's a SEV-2 or a SEV-3, those are ten minutes not spent mitigating the user impact. The severity classification exists to trigger the right escalation path and communication cadence, not to be an accurate assessment of blame or impact (which is only possible in retrospect). A quick "declare SEV-2, adjust later" keeps the response moving; a prolonged classification debate is a cognitive distraction during the highest-stress window.

## How to apply

Define severity levels with clear, observable thresholds so the on-call engineer can classify in under 30 seconds. Err toward higher severity (lower number) if uncertain — it's always easier to downgrade than to recover from an under-resourced response.

| Severity | Observable trigger | Response SLA | Communications |
|---|---|---|---|
| SEV-1 | Core service down or data loss — all or many users impacted | Immediate; wake anyone | Customer status page, exec notification |
| SEV-2 | Major feature degraded or partial outage — significant user impact | Response in < 15 min | Status page, team notification |
| SEV-3 | Minor feature degraded or slow — limited user impact | Response in < 1 hour | Internal ticket, no customer comms |
| SEV-4 | Cosmetic / no user impact | Next business day | JIRA ticket |

```markdown
# Incident declaration template (post in #incidents immediately)
**INCIDENT DECLARED**
- **Severity:** SEV-[X] (provisional — adjust within 30 min if wrong)
- **Impact:** <one line: what users can't do>
- **IC:** @[your handle]
- **Bridge:** [Zoom/Meet link]
- **Status page:** [link] — set to [Investigating / Degraded Performance / Major Outage]
- **Slack thread:** all updates here ↓
```

**Do:**
- Declare and post the classification within the first 5 minutes, even if the impact is still unclear.
- Use the word "provisional" if you're unsure — it removes pressure to be right.
- Downgrade severity promptly once impact is confirmed to be smaller than initially assessed.
- Train new on-call engineers on the classification rubric during non-incident times.

**Don't:**
- Wait for complete information before declaring — severity gates the response, not the diagnosis.
- Upgrade severity retroactively after the incident to affect blame or metrics (this destroys the trust in the classification).
- Have different teams use different severity scales — one scale, one set of response SLAs.

## Edge cases / when the rule does NOT apply

Automated incident detection systems that auto-classify and auto-page based on SLO burn rate are better than manual classification — let the SLO burn-rate be the trigger and severity be derived from the burn rate window. This rule applies to the human decision point when automation hasn't already made the call.

## See also

- [`../agents/incident-commander.md`](../agents/incident-commander.md) — owns the incident response framework, severity definitions, and the IC role.
- [`./postmortems-are-blameless.md`](./postmortems-are-blameless.md) — severity is finalized and analyzed in the blameless postmortem.

## Provenance

Codifies the incident severity classification practice from PagerDuty's Incident Response Guide and Google SRE Book Chapter 14 ("Managing Incidents"), specifically the principle of over-escalating and downgrading rather than under-escalating.

---

_Last reviewed: 2026-06-05 by `claude`_
