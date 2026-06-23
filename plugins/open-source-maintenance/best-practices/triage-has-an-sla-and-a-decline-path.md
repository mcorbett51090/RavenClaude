# Triage has an SLA and a graceful decline path

**Status:** Pattern (strong default; deviate only with a written reason)
**Domain:** Issue/PR triage / maintainer sustainability
**Applies to:** `open-source-maintenance`

---

## Why this exists

The dominant cause of maintainer burnout is an unbounded, silent backlog — issues and PRs that get neither a response nor a close. Contributors experience silence as the cruelest outcome; maintainers experience the growing pile as a permanent guilt debt. A triage system with a first-response SLA and an explicit, kind decline path bounds both: every item gets acknowledged within tier, and every item that won't be done gets closed with a reason.

## How to apply

Apply the [`../skills/triage-issues-and-prs/SKILL.md`](../skills/triage-issues-and-prs/SKILL.md) taxonomy: one `type/*` + one `priority/*` label per item, a first-response SLA per priority (not a fix-time promise), a reproduction gate for bugs, and a `wontfix`/`out-of-scope` close *with a comment* for anything declined.

**Do:**
- Make the SLA a first-response promise; acknowledge within tier even if the fix is later.
- Decline fast and warmly: name why, thank the work, point elsewhere if you can.
- Curate `good-first-issue` as the top of the contributor funnel.

**Don't:**
- Let actionable items sit with no response for months.
- Close without a reason, or let a stale-bot auto-close prioritized/ready work.

## Edge cases / when the rule does NOT apply

- **Security reports never get triaged in public** — reroute to the private channel immediately ([`./security-reports-go-private-first.md`](./security-reports-go-private-first.md)).
- **A maintainer on hiatus** should say so (a pinned issue / README banner) rather than leave the SLA silently unmet.

## See also
- [`../skills/triage-issues-and-prs/SKILL.md`](../skills/triage-issues-and-prs/SKILL.md)
- [`./bus-factor-is-a-first-class-risk.md`](./bus-factor-is-a-first-class-risk.md)

## Provenance
Codifies opensource.guide maintainer-sustainability guidance and the `oss-maintainer-strategist` house opinion "decline kindly and fast." Last reviewed 2026-06-23.

---

_Last reviewed: 2026-06-23 by `claude`_
