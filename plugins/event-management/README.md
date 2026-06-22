# event-management

A RavenClaude plugin: an **event-management** specialist team for planning and running conferences, webinars, and field/community events — in-person, virtual, or hybrid — so they hit the goal you set, run smoothly on the day, and pay off.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

## What it's for

Standing up an event and wanting it done right: the goal and KPIs, the format and budget, the sponsorship money, a minute-by-minute show that doesn't fall over, a registration funnel that fills the room, and an honest post-event ROI. This is the **event craft** — distinct from the generic project around it; schedule, RAID, and stakeholder management live in [`project-management`](../project-management/).

## Agents

| Agent | Use for |
|---|---|
| **event-strategist** | Goals/KPIs, format (in-person/virtual/hybrid), audience, budget/break-even, sponsorship strategy, the go/no-go gate |
| **event-operations-lead** | Run-of-show/show-flow, venue/vendor/AV logistics, registration ops, contingency, day-of execution |
| **event-marketing-revenue** | Promotion, the ticketing/registration funnel, sponsorship sales + fulfillment, attendee acquisition, post-event ROI |

## What's inside

- **5 skills** — design-event-plan-and-budget, build-run-of-show, sponsorship-and-revenue, registration-and-attendee-ops, post-event-measurement.
- **Knowledge bank** — [`event-management-decision-trees.md`](knowledge/event-management-decision-trees.md) (4 Mermaid trees: format, break-even, sponsorship-tier, go/no-go) + [`event-management-reference-2026.md`](knowledge/event-management-reference-2026.md) (dated tooling/benchmark map).
- **8 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — event plan & budget, run-of-show, post-event report.
- **3 commands** — `/plan-event`, `/build-run-of-show`, `/event-debrief`.
- **1 advisory hook** — `check-event-anti-patterns.sh` (budget with no contingency line, run-of-show with no owner column, plan with no go/no-go or success metric). `EVENT_STRICT=1` to block.

## Seams

The cross-functional project schedule, RAID log, and stakeholder management → [`project-management`](../project-management/) · security/privacy verdicts (attendee PII, sponsor lead lists) → [`ravenclaude-core/security-reviewer`](../ravenclaude-core/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install event-management@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for routing rules, house opinions, and the output contract.
