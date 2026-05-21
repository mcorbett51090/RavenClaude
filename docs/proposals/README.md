# Proposals

> Forward-looking ideas, issues, and improvements that need review **before** becoming canonical lessons or best-practices. The pre-decision substrate.

This folder sits between "I had a thought" and "we've codified it." Drop ideas here; review them deliberately; promote to lessons / best-practices / specific-plugin changes when decided.

## What goes here

- **Issues to investigate** — "X feels off, need to think about it before acting"
- **Improvement ideas** — "what if we changed Y"
- **Architectural questions** — "should we do A or B; here's the trade-off"
- **Open design questions** — pre-implementation, when the answer isn't obvious
- **Feature wishlist** — things to consider building, when their time comes

## What does NOT go here

| Other artifact | Where it lives | What it is |
|---|---|---|
| Lessons already learned | [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md) | Post-hoc, dated learnings |
| Promoted best practices | [`../best-practices/`](../best-practices/) | Canonical, reviewed rules |
| Staged contributions awaiting maintainer review | [`../staging/incoming/`](../staging/incoming/) | Consumer-side contributions from `/contribute-finding` |
| Active engagement scenarios | `plugins/<plugin>/scenarios/` | Dated war-story narratives from real engagements (via `/wrap`) |
| Active sprint work | `feat/*` branches + PRs | Decided + implementing |

**The distinction in one line:** proposals are *pre-decision*. Everything else is *post-decision*.

## Filename convention

`YYYY-MM-DD-NNN-short-slug.md` where:

- `YYYY-MM-DD` = the date the proposal was filed
- `NNN` = a 3-digit counter for proposals filed on the same day (001, 002, ...)
- `short-slug` = 3-5 hyphenated keywords from the proposal title

Example: `2026-05-21-001-feedback-loop-discovery-friction.md`

## Lifecycle

| Status | Meaning |
|---|---|
| `proposed` | Filed; awaiting initial review |
| `under-review` | Actively being analyzed (architect, expert agents, deep-researcher, or just Matt thinking) |
| `accepted` | Decision made; will be implemented (link to PR / branch / lesson where the work landed) |
| `rejected` | Decision made; not pursuing — keep the file with the reason so the proposal doesn't get re-raised |
| `implemented` | Work landed; proposal is closed |
| `deferred` | Worth doing later; not now (note the trigger that would un-defer it) |

## Frontmatter schema

```yaml
---
proposal_id: <YYYY-MM-DD-NNN>
proposed_at: <YYYY-MM-DD>
proposed_by: <name or handle>
status: proposed | under-review | accepted | rejected | implemented | deferred
topic: <area — e.g., feedback-loop / docs / plugin-{name} / cross-plugin / infrastructure>
last_updated: <YYYY-MM-DD>
---
```

The body is freeform markdown — favor short prose + concrete examples over checklist-heavy templates. Each proposal should answer:

1. **What's the issue / idea?** (1-3 sentences)
2. **Why does it matter?** (1-2 paragraphs)
3. **What are the options?** (if it's a decision; list 2-3)
4. **What's the recommendation, if any?** (with reasoning)
5. **What would un-block / un-defer it?** (if status ≠ accepted)

## Promotion paths

A proposal that gets accepted typically lands somewhere — and the proposal file gets a link to where:

- → A lesson in [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md) — when the proposal *was about something we now know*
- → A best-practice in [`../best-practices/`](../best-practices/) — when the proposal *generalizes into a rule*
- → A new feature in a plugin — via PR (link from the proposal)
- → A new agent / skill / knowledge file / template — via PR (link from the proposal)
- → A `/wrap` scenario — when the proposal *was about something a real engagement now teaches*

## Anti-patterns this folder discipline avoids

- **"Wiki graveyard"** — proposals decay without status updates. Mitigation: every proposal carries `last_updated`; quarterly pass to age out forgotten ones.
- **"Endless deliberation"** — proposals sit in `under-review` indefinitely. Mitigation: a proposal that's been `under-review` for >60 days should default to `deferred` with a named trigger.
- **"Decision drift"** — accepted proposals don't get linked to where the work landed. Mitigation: when promoting, edit the proposal file to add the link.
- **"Pre-emptive proposals"** — filing every passing thought. Mitigation: prefer the `/wrap` flow for engagement-derived ideas; this folder is for genuinely pre-decision strategic questions.

## When the proposal is sensitive

If a proposal touches sensitive material (client identification, internal financial info, etc.):

- Don't put it here — this folder is public-visible per the repo's distribution
- Use Matt's private memory (`/home/codespace/.claude/projects/-workspaces-RavenClaude/memory/`) for sensitive ideas
- OR scrub the proposal of identifying info before filing here

## References

- [`../memory-bank/lessons-learned.md`](../memory-bank/lessons-learned.md) — the post-hoc-learnings counterpart
- [`../best-practices/`](../best-practices/) — promoted-rules counterpart
- [`../staging/README.md`](../staging/README.md) — consumer-contributions counterpart
- `plugins/ravenclaude-core/commands/wrap.md` — engagement-scenario counterpart
