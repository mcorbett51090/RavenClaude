---
name: raid-facilitation
description: Build or refresh a decision-grade RAID register — risks framed cause→event→consequence and scored against a stated rubric (qualitative probability×impact, quantified/EMV where the stakes justify it), each with a response and a single owner; plus issue triage, assumptions, and dependency tracking. Reach for this when a RAID stub needs to become a real register, a risk needs quantifying, or issues need triaging to action. Used by `risk-and-raid-analyst` (primary).
---

# Skill: raid-facilitation

**Purpose:** Turn a RAID stub into a register that actually drives mitigation spend to where the expected loss is. Goes deeper than `ravenclaude-core/project-manager`'s lightweight RAID-log hygiene. Used by `risk-and-raid-analyst`.

## When to use

- Standing up a risk register for a new project.
- Refreshing RAID after a scope change, a missed milestone, or a new dependency.
- Quantifying a high-stakes risk (go/no-go-moving).
- Triaging a backlog of issues to owners + dates.

## The procedure

### Risks
1. **Frame cause → event → consequence.** "Server might fail" is not a risk. "Because the gateway is single-node *(cause)*, it may go down during refresh *(event)*, delaying month-end close *(consequence)*" is.
2. **Score against a stated rubric.** Qualitative probability × impact with the scale written down (don't let "High" float undefined). **Aggregate** related low risks over the same objective — several minors can combine into a major.
3. **Quantify where the stakes justify it.** For high-impact risks: an impact **range** + probability → expected value (EMV) → the **contingency reserve** it justifies. Don't quantify trivia; do quantify the ones that move the decision.
4. **A response per risk:** mitigate / transfer / avoid / accept — each with a single owner and (for *accept*) an explicit, documented decision. A scored risk with no response is half an entry.
5. **A trigger / review date** per risk, so it's re-checked, not filed and forgotten.

### Issues, Assumptions, Dependencies
- **Issues** (already occurred) — triage by severity × urgency, assign owner + due date, escalate the ones breaching threshold with a recommended path.
- **Assumptions** — log them; an unstated assumption is a silent risk.
- **Dependencies** — especially cross-team ones (the most common silent schedule risk). Name the owner on both sides + the needed-by date.

## Anti-patterns this skill prevents

- Risks as bare nouns; "High" with no rubric; a scored risk with no response or owner.
- Quantifying trivia while the go/no-go risk sits as a bare "Medium."
- Contingency reserve set by gut, not by the quantified risk it covers.
- Issues logged but never triaged; cross-team dependencies absent from the register.

## Output

A risk register + issue log (see [`../../templates/risk-register.md`](../../templates/risk-register.md)): cause-event-consequence risks, the scoring rubric, responses + owners + review dates, triaged issues, and tracked assumptions/dependencies. End with the `risk-and-raid-analyst` Output Contract block; route contingency into the baseline via `delivery-lead`.
