---
description: "Prepare for a goals-of-care 'hospice conversation' — a values-first talk-track or an objection-handling response (giving up / too soon / my doctor didn't mention it / I want to keep fighting), with the hospice-vs-palliative framing. Empathy and accuracy; never a scripted guarantee or a pressure tactic."
argument-hint: "[situation or objection, e.g. 'family of an end-stage dementia patient says it feels like giving up']"
---

# Coach the hospice conversation

You are running `/hospice-referral-sales:coach-hospice-conversation`. Prepare for the conversation/objection the user described (`$ARGUMENTS`), using this plugin's `goals-of-care-conversation-coach` discipline and the `goals-of-care-conversations` skill.

## The line

Coach **framing**, not promises. Never a guarantee of outcome/coverage/eligibility, never a pressure tactic, never substitute for the patient's clinician. Values-first — the patient's goals lead.

## Steps

1. **Identify the situation** — a full talk-track, a specific objection, a clinician-framing brief, or a hospice-vs-palliative distinction.
2. **Open with values** — what matters most to the patient now, before any service is mentioned.
3. **Frame accurately** — the hospice-vs-palliative distinction where relevant; name the **revocability** (electing hospice is not a one-way door) to defuse "too soon" honestly. Clinical accuracy from `hospice-eligibility-educator`.
4. **Handle the objection** — the empathy-first reframe (said once, never pushed), the accurate information, and the next step.
5. **Add the listen-fors** — the goals, the fears, the unspoken question, and when to slow down.
6. Emit in the Output Contract format + the Structured Output JSON block.

## Guardrails

- No scripted promise, no manufactured urgency, no competitor disparagement.
- Sometimes the honest answer is palliative care, not hospice — say so; it builds trust.
- The clinician leads the medical conversation; the liaison supports.
- No patient-identifying data.
