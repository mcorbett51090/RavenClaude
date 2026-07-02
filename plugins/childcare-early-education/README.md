# childcare-early-education

A RavenClaude plugin: a **childcare / early-education center operations** specialist team for the three engines of an early-education center — the operations & tuition model, the enrollment & family funnel, and ratio & licensing compliance.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not legal, licensing, or financial advice.** Child:staff ratios, group-size caps, staff-qualification rules, and childcare subsidy programs (CCDF and state variants) are **state-specific and volatile**: each carries a retrieval date + `[verify-at-use, state-specific]` and must be confirmed against your current state licensing regulation and funding agency before it drives a staffing plan, an enrollment cap, or a bill. The agents store **no child or family PII**.

## What it's for

Running an early-education center well: every licensed seat filled with a family that stays, each room staffed to the required ratio at a labor cost the tuition covers, tuition and subsidy collected on the right rail, and every licensing domain kept inspection-ready continuously.

## Agents

| Agent | Use for |
|---|---|
| **childcare-center-lead** | Enrollment/waitlist, capacity vs licensed ratios, tuition model, staffing to ratio, family retention, P&L |
| **enrollment-and-family-manager** | Tour-to-enroll conversion, waitlist, enrollment paperwork, family communication, tuition & CCDF/state subsidy billing |
| **classroom-ratio-compliance-advisor** | Ratio & group-size by age, licensing readiness, staff qualifications, health & safety, incident documentation |

## What's inside

- **4 skills** — enrollment-and-waitlist-management, ratios-and-licensing-compliance, tuition-and-subsidy-billing, staffing-to-ratio-scheduling.
- **Knowledge bank** — [`childcare-decision-trees.md`](knowledge/childcare-decision-trees.md) (4 Mermaid trees: staff a room to ratio, enrollment/waitlist, tuition vs subsidy billing route, licensing-readiness triage) + [`childcare-reference-2026.md`](knowledge/childcare-reference-2026.md) (dated reference: ratio/group-size norms by age, CCDF/subsidy basics, licensing domains — each verify-at-use, state-specific).
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **2 templates** — enrollment funnel tracker, ratio staffing plan.
- **2 commands** — `/plan-staffing-to-ratio`, `/model-enrollment`.

## Seams

Broader early-education partner/programmatic and school-district relationships → the adjacent (distinct) [`edtech-partner-success`](../edtech-partner-success/) plugin · security/privacy verdicts on family-data handling → [`ravenclaude-core`](../ravenclaude-core/)'s `security-reviewer`.

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install childcare-early-education@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
