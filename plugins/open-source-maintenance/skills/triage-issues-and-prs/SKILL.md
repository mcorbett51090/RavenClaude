---
name: triage-issues-and-prs
description: Turn an unbounded issue/PR backlog into a tractable system — a label taxonomy, SLA tiers, a reproduction gate for bugs, a stale policy, and a graceful decline path. Returns a TRIAGE policy, issue/PR templates, and label definitions. Prevents the silent-backlog burnout the project exists to avoid. Used by `oss-maintainer-strategist` (primary).
---

# Skill: triage-issues-and-prs

> **Invoked by:** `oss-maintainer-strategist` (primary).
>
> **When to invoke:** "the backlog is out of control"; "set up triage"; "how do I handle drive-by issues/PRs?".
>
> **Output:** a TRIAGE policy + a label taxonomy + issue/PR templates + a stale/decline policy.

## The triage decision (per incoming item)

1. **Is it actionable as written?** No reproduction / no version / a question → apply `needs-info` (bug) or `question` and ask once; close after the stale window if unanswered. A bug with no reproduction is not yet a bug — that is the **reproduction gate**.
2. **Is it in scope?** Out of scope → `wontfix` / `out-of-scope` with a *kind, specific* decline ("this belongs in a plugin, not core, because…"). Declining fast and warmly beats six months of silence.
3. **What kind, what priority?** Apply exactly one `type/*` (bug/feature/docs/chore) and one `priority/*` label. Map priority to an **SLA tier** (first-response, not fix-time).
4. **Is it a good contributor on-ramp?** Small, well-scoped, low-context → `good-first-issue` / `help-wanted`. This is the top of the contributor funnel — curate it deliberately.
5. **Is it security-sensitive?** A vulnerability reported in a public issue → do **not** discuss it publicly; route to the private channel ([`coordinate-a-security-release`](../coordinate-a-security-release/SKILL.md)) and minimize the public issue.

## Label taxonomy (minimal, orthogonal)

| Group | Labels | Rule |
|---|---|---|
| `type/*` | bug, feature, docs, chore, question | exactly one |
| `priority/*` | p0-critical, p1, p2, p3 | exactly one; maps to first-response SLA |
| `status/*` | needs-info, needs-repro, blocked, ready, in-progress | reflects the gate it's waiting on |
| `area/*` | (project-specific) | optional, for routing |
| on-ramp | good-first-issue, help-wanted | curated, not automatic |
| disposition | wontfix, duplicate, out-of-scope | with a decline comment |

## SLA tiers (first response, not resolution)

| Priority | First response | Meaning |
|---|---|---|
| p0-critical | 24h | data loss / security / build broken on main |
| p1 | 3 business days | major feature broken, no workaround |
| p2 | 2 weeks | normal bug / feature |
| p3 | best-effort | nice-to-have |

## Guardrails
- **Triage SLA is a first-response promise, not a fix promise.** Acknowledging within tier is the commitment; the fix has its own timeline.
- **Every closed-without-merge item gets a reason.** Silence is the failure mode. See [`../../best-practices/triage-has-an-sla-and-a-decline-path.md`](../../best-practices/triage-has-an-sla-and-a-decline-path.md).
- **A stale-bot is a tool, not a policy.** Auto-closing `needs-info` after a window is fine; auto-closing actionable bugs because nobody got to them is hostile — exempt `priority/*` and `ready`.
- **Security never gets triaged in public.** Reroute to the private channel immediately.
