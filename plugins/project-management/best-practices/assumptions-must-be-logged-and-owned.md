# Log every planning assumption with an owner and a validation date

**Status:** Absolute rule
**Domain:** RAID management — assumptions
**Applies to:** `project-management`

---

## Why this exists

Assumptions are the quiet killers of project baselines. They are made at charter time ("we assume the data migration team will be available from sprint 3"), recorded nowhere, and discovered to be false at the worst possible moment — usually when the dependency is needed. Unlike risks (something that might happen), an assumption is something the team is counting on being true. If it turns out to be false, it is an issue immediately. An assumption that is not logged cannot be validated, cannot be assigned an owner, and cannot be converted to a risk entry when evidence emerges that it may not hold. The RAID register exists precisely to surface these: assumptions belong in the A column, with an owner who validates each one by a named date.

## How to apply

**Assumption register entry (minimum fields):**

| Field | Guidance |
|---|---|
| ID | Sequential reference (A-001, A-002 …) |
| Assumption statement | A single declarative sentence: "We assume that [X] will be true" |
| Impact if false | What happens to scope/schedule/cost/quality if this assumption is invalid |
| Impact severity | HIGH / MEDIUM / LOW |
| Owner | The person responsible for validating the assumption |
| Validation method | How will we know if it is true? (confirmation from stakeholder, signed contract, test result) |
| Validation date | When must we know — what is the last date we can act if it is false? |
| Status | Open / Validated / Invalidated (now a risk or issue) |

**The critical discipline — convert invalid assumptions immediately:**

```
Assumption validated → Mark as VALIDATED; remove from active monitoring
Assumption invalidated → IMMEDIATELY raise a risk (if still possible) or an issue (if already impacting)
Assumption status uncertain and validation date approaching → Escalate to PM; open a risk entry proactively
```

**Common assumption categories in technology and delivery projects:**

- Resource availability: "We assume that [person/team/skill] will be available from [date]."
- Dependency delivery: "We assume that [upstream system/data/environment] will be ready by [date]."
- Stakeholder engagement: "We assume that [stakeholder group] will provide decisions within [X days] of each request."
- Technology stability: "We assume that the [platform/API/data source] will not undergo breaking changes during delivery."
- Regulatory: "We assume that [approval/licence/compliance confirmation] will be obtained before [phase gate]."

**Do:**
- Log assumptions at project initiation and at every new phase — planning surfaces new assumptions.
- Set calendar reminders for each validation date so assumptions are not left to sit until invalidated by events.
- Review the assumption register at every risk/RAID review — open assumptions with past validation dates are either invalidated or forgotten.

**Don't:**
- Write assumptions as aspirations ("we hope that budget will be confirmed") — they must be stated as factual claims the plan depends on.
- Leave an assumption without an owner; an ownerless assumption will never be validated.
- Conflate an assumption with a risk; once you know the assumption may not hold, it is a risk — register it in the risk column.

## Edge cases / when the rule does NOT apply

On very short projects (< 4 weeks) where the assumption register would have only 2–3 entries, it may be folded into the project charter assumptions section rather than a standalone register — the fields and owner/date discipline still apply. Agile projects carry assumptions in the product backlog's refined acceptance criteria and in the sprint risk log; the structure differs but the discipline — state it, own it, validate it — does not change.

## See also
- [`../agents/risk-and-raid-analyst.md`](../agents/risk-and-raid-analyst.md) — RAID register methodology
- [`../skills/raid-facilitation/SKILL.md`](../skills/raid-facilitation/SKILL.md) — RAID facilitation playbook (assumptions column)

## Provenance

Codifies `risk-and-raid-analyst`'s assumptions discipline. The RAID register (Risks, Assumptions, Issues, Dependencies) is a standard UK/EU programme management artefact; the assumption-to-risk conversion is documented in PRINCE2, MSP, and the APM Body of Knowledge.

---

_Last reviewed: 2026-06-05 by `claude`_
