# Every commitment has one named owner and one date

**Status:** Absolute rule — a task, risk, action, or deliverable with no single named owner and no date is a wish, not a managed commitment. This holds on **both** the predictive and agile tracks.

**Domain:** Project management

**Applies to:** `project-management`

---

## Why this exists

The single most common way projects rot is shared ownership: a RAID item owned by "the team," a sprint task owned by "we," a remediation "in progress" with no date. Shared ownership is no ownership — at the next review nobody is accountable and the item is silently re-raised. This rule is the discipline `ravenclaude-core`'s project-manager already applies to the RAID log, made a citable standard for every artifact this plugin's specialists produce.

## How to apply

- **One named person per item.** Never "the team," "we," "TBD," or a role with no name behind it. If the owner genuinely isn't decided, the *decision of who owns it* is itself an action with an owner and a date.
- **One date per item.** A target/due date (predictive) or a sprint/iteration (agile). "Ongoing" is not a date; "next sprint" is acceptable only if the sprint has a boundary.
- **Applies across tracks:** WBS work packages, change requests, risk responses, issue triage, sprint-backlog items, retro actions, and every escalation's "decision needed by." Acceptance criteria + owner are set *before* a sprint item is committed, not argued at review.
- **Surface the gap rather than fill it with mush.** If an owner or date can't be set, say so explicitly and name what's blocking it — don't paper it with "team / ongoing."

**Do:** assign one named owner + one date to every task/risk/action/deliverable; treat an undecided owner as an action with its own owner+date.

**Don't:** accept "we"/"the team"/"TBD"/"ongoing"; commit a sprint item without acceptance criteria + owner; let a remediation sit with no date.

## Edge cases / when the rule does NOT apply

A genuinely shared *informational* note (not a commitment) needs no owner. A backlog item that is **not yet committed** to a sprint may sit un-owned in the backlog — the rule binds at commitment time, not at idea time. A pairing/mob arrangement still names one accountable owner even when several people do the work.

## See also

- [`../knowledge/pm-decision-trees.md`](../knowledge/pm-decision-trees.md) — applies on every leaf of the delivery-approach tree.
- [`../../ravenclaude-core/agents/project-manager.md`](../../ravenclaude-core/agents/project-manager.md) — the hygiene agent that enforces this on the RAID log.
- PMBOK 7 (accountability) + the Scrum Guide (Developers own the Sprint Backlog) — domain-standard framings.

## Provenance

Authored with the `project-management` plugin (2026-06-01). Extends the single-ownership discipline already enforced by `ravenclaude-core/project-manager` into a citable, cross-track standard for the plugin's specialists.

---

_Last reviewed: 2026-06-01 by `claude`_
