# Moves management is a documented record, not a mental model

**Status:** Pattern
**Domain:** Nonprofit major gifts
**Applies to:** `nonprofit-fundraising`

---

## Why this exists

Moves management — the discipline of intentionally moving a major-gift prospect through identification, qualification, cultivation, solicitation, and stewardship — exists on paper in most development shops but lives primarily in the major-gifts officer's head. When that officer leaves, transitions, or is sick the week of a critical cultivation meeting, the relationship history and the planned next move disappear with them. The documentation of each contact's stage, the last meaningful touch, the planned next move, and the ask range is not optional overhead; it is the asset that makes the donor relationship survive personnel changes. A move that is not recorded in the CRM did not happen for the purposes of continuity.

## How to apply

Use a CRM contact record (Salesforce, Bloomerang, Raiser's Edge, or equivalent) as the running log for every major-gift prospect. Every meaningful contact results in a logged entry within 24 hours.

```
CRM contact record minimum fields for moves management:
  Prospect: [name]
  Stage: Identified / Qualifying / Cultivating / Solicitation-ready / Ask-pending / Stewardship
  Ask range: $[min] – $[max] (based on capacity research + relationship depth)
  Last meaningful touch: [date + type + summary — 2–3 sentences]
  Next planned move: [specific action + owner + target date]
  Notes on interests: [2–3 sentences on what the prospect cares about most]

Definition of "meaningful touch":
  — A personal call, meeting, site visit, or handwritten note
  — NOT: a mass email or newsletter
  — NOT: a phone call that went to voicemail with no message left

Log rule: if you had a cultivation conversation and it's not in the CRM by the next morning, you didn't have it for continuity purposes.
```

**Do:**
- Log every meaningful touch within 24 hours of the contact.
- Include the next planned move with a specific date and a named owner in every log entry.
- Review the moves-management log in weekly development meetings so all staff are aware of the pipeline state.

**Don't:**
- Rely on a major-gifts officer's memory as the source of truth for any prospect relationship.
- Log only gift transactions — the cultivation touches are the strategic asset, not just the dollars received.
- Leave a prospect in the same stage for more than 90 days without a documented reason for the pause.

## Edge cases / when the rule does NOT apply

Very small shops (one-person development) with fewer than 20 major-gift prospects may find a spreadsheet adequate as an interim CRM; the documentation discipline applies regardless of the tool. For anonymous donors or prospects who have explicitly requested privacy, modify logging to capture relationship stage and touch types without names in shared systems.

## See also

- [`../agents/major-gifts-strategist.md`](../agents/major-gifts-strategist.md) — owns and executes the moves-management cycle.
- [`./major-gifts-are-a-cultivation-cycle-not-an-ask.md`](./major-gifts-are-a-cultivation-cycle-not-an-ask.md) — the parent rule establishing why the cycle must be managed, not improvised.

## Provenance

Codifies standard major-gifts CRM discipline. The "lives in the officer's head" anti-pattern is the primary cause of major-gift relationship loss during staff transitions; the 24-hour logging rule is the standard corrective.

---

_Last reviewed: 2026-06-05 by `claude`_
