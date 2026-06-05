# Express Every Risk as Cause → Event → Consequence

**Status:** Absolute rule
**Domain:** Project Management — Risk / RAID
**Applies to:** `project-management`

---

## Why this exists

A risk entered as a bare noun — "key-person dependency", "regulatory change", "vendor delivery" — carries no information about what could go wrong, how likely it is, or what the impact would be. It cannot be scored, cannot be responded to, and cannot be owned by anyone. The cause → event → consequence structure forces the registrar to articulate a specific triggering condition, the risk event that would follow, and the project-measurable impact. Without this structure, a "High" risk rating is unauditable and the register becomes a list of worries rather than a decision instrument.

## How to apply

**Risk statement template:**

```
CAUSE:      Because [uncertain condition or event in the environment]
EVENT:      there is a risk that [the risk event — what could happen to the project]
CONSEQUENCE: resulting in [impact on scope / schedule / cost / quality — quantified if possible]
```

**Example (before and after):**

| Before | After |
|---|---|
| "Key-person dependency" | Because the API integration is owned by a single engineer with no backup, there is a risk that their unplanned absence causes the integration milestone to slip, resulting in a 2-week schedule delay and a potential breach of the delivery SLA. |

**Required fields per risk register entry:**

| Field | Content |
|---|---|
| Risk ID | Sequential + sprint/phase label |
| Cause → Event → Consequence | Full statement |
| Probability | Score 1–5 against the stated rubric (not a bare "High/Med/Low") |
| Impact | Score 1–5 per dimension (scope/schedule/cost/quality) |
| Risk Score | P × I or P × max(I) |
| Response | Avoid / Transfer / Mitigate / Accept + the specific action |
| Response owner | Named person + due date |
| Trigger | Observable event that signals the risk is materializing |

**Do:**
- Agree the probability and impact rubric before scoring begins — scores without a rubric are not comparable.
- Quantify the consequence where possible ("2-week slip", "€30K overage estimate") so the score maps to a real impact.
- Review the register at each sprint review / stage gate; closed risks are not deleted, they are marked closed with an outcome note.

**Don't:**
- List risks as bare nouns or headlines.
- Score risks without a stated rubric.
- Enter a risk with no response and no owner ("Accept" is a valid response — but it must be a deliberate choice, not an oversight).

## Edge cases / when the rule does NOT apply

- **RAID assumptions and dependencies**: the C→E→C structure adapts — "Because we have assumed X, if X proves false, there is a risk that…". Assumptions and dependencies are a distinct RAID category, but the same expression discipline applies.
- **Issues** (risks that have materialized): an issue still needs the same root structure, stated in past tense, plus an action plan and owner.

## See also

- [`../agents/risk-and-raid-analyst.md`](../agents/risk-and-raid-analyst.md) — the agent that writes and scores the risk register
- [`./commitments-have-one-owner-and-one-date.md`](./commitments-have-one-owner-and-one-date.md) — the owner + date rule applied to risk responses

## Provenance

Codifies house opinion #5 ("Risk is cause→event→consequence") from `CLAUDE.md` §3. Risk statement structure from PMBOK 6th/7th edition (PMI) and APM Body of Knowledge. _Last verified: 2026-06-05._

---

_Last reviewed: 2026-06-05 by `claude`_
