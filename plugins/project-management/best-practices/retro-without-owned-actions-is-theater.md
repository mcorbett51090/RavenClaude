# A Retrospective Without Owned Actions Is Theater

**Status:** Absolute rule
**Domain:** Project Management — Agile / continuous improvement
**Applies to:** `project-management`

---

## Why this exists

The retrospective is the primary empirical improvement mechanism in Scrum. A retro that surfaces problems, generates discussion, and closes with no specific owned actions — or with actions assigned to "the team" or "everyone" with no date — produces no improvement. Teams that run retros this way train themselves to treat the ceremony as a venting session rather than a change instrument. Within two or three repetitions, attendance drops, engagement falls, and the retro becomes the ceremony most likely to be canceled under schedule pressure.

## How to apply

**Retro output contract (non-negotiable):**

Every retrospective closes with a **Retro Action Register** containing at least one entry:

| Action | Owner (named person) | Due date | Success metric |
|---|---|---|---|
| [Specific change to make] | [First Last] | [YYYY-MM-DD] | [How we'll know it worked] |

**Facilitation rules:**
1. **Time-box the discussion** so the last 15 minutes is reserved for action-item drafting.
2. **Limit actions to 1–3 per sprint**: more than 3 rarely get done; prioritize ruthlessly.
3. **The action must be within the team's control** to complete in the next sprint — no actions that require external approval, unless the *ask for approval* is itself the action with an owner and date.
4. **Review last sprint's actions first**: open the retro by reading out the previous actions and their outcomes. Recurring open actions are a signal that the action was too large or not genuinely owned.
5. **Success metric**: each action has an observable outcome so the *following* retro can assess whether it worked.

**Do:**
- Write the action register on the visible board before closing the ceremony.
- Rotate the scribe and action-owner role so a single person doesn't carry all improvement work.
- Track retro action completion rate as a team health metric — a rate below 60% signals that actions are not being set at the right scope.

**Don't:**
- Close a retro with only "items to think about" or "topics for the next PI."
- Accept "the team" or "everyone" as an action owner.
- Carry the same action item into a third sprint without either completing it or explicitly deprioritizing it with a documented reason.

## Edge cases / when the rule does NOT apply

- **First retro of a brand-new team**: the purpose may be norms-setting rather than improvement actions; a single "working agreement" entry with a team sign-off is the equivalent output.
- **Crisis sprint retro** (e.g., post-incident review): the retro may generate an incident action register instead of a sprint improvement register — the ownership and date discipline is identical.

## See also

- [`../agents/scrum-master.md`](../agents/scrum-master.md) — facilitates the retro and enforces the action register
- [`./commitments-have-one-owner-and-one-date.md`](./commitments-have-one-owner-and-one-date.md) — the parent rule that every commitment has one owner and one date

## Provenance

Codifies house opinion #8 ("Empiricism over theater — a retro with no owned actions is theater") from `CLAUDE.md` §3. Retrospective discipline from the Scrum Guide 2020 and Esther Derby & Diana Larsen, "Agile Retrospectives." _Last reviewed: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
