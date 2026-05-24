---
name: qbr-composition
description: Compose a Quarterly Business Review end-to-end — data pull plan, narrative arc, deck outline, talk track, post-QBR commitment tracker. Reach for this skill 1–2 weeks before a QBR is scheduled, OR after a QBR to convert in-meeting promises into a tracked plan.
---

# Skill: QBR Composition

A QBR with no commitments is a status meeting. This skill prevents that.

## Step 1 — Identify the partner's stated goals from the success plan

Pull the success plan (`success-plan-authoring`) and the partner profile. The **opening content slide** of the QBR is the partner's goals, verbatim, with attribution. **Don't paraphrase. Don't substitute internal KPIs.**

If the success plan doesn't have explicit partner-stated goals, **stop**. Loop in `partner-profile-curator` to capture them first. A QBR against goals you assumed is worse than no QBR.

## Step 2 — Data pull plan

For each partner-stated goal, identify the measurable outcomes that prove progress (per the success plan). Then build the data pull:

- **Source** — which database / dashboard / export
- **Query** — the actual query, written down so a successor can re-run it
- **Date range** — usually quarter-over-quarter; sometimes year-over-year for seasonal partners
- **Comparison baseline** — vs prior quarter, vs onboarding baseline, vs same-cohort average. **Pick deliberately, name it on the slide.**
- **Freeze date** — when the data is cut. Don't change it after this date.

If a goal can't be measured with available data, that's a finding — flag it in the data pull plan and route the gap to `learning-analytics-analyst` for instrumentation in the next cycle.

## Step 3 — Narrative arc (the storyline that makes the data make sense)

A QBR is a story. Default structure (15–18 slides):

1. **Opener** — partner's goals, in their words, from the success plan
2. **Where we are** — for each goal, the relevant outcome with chart + date range + baseline
3. **What's working** — 2–3 specific wins, named (specific user, specific feature, specific outcome)
4. **What's at risk** — 1–2 honest concerns (don't bury them; partners notice)
5. **What we recommend next** — 3–5 specific actions; mix of partner-side, our-side, joint
6. **Followups** — named owners, dates, cadence for review

**Anti-pattern:** opening with "Here's how we did this quarter" — that's PSM-internal framing. Open with the partner's reasons for being here.

## Step 4 — Deck outline (one headline per slide)

Each slide:
- One headline (the claim)
- One chart or visual (the evidence)
- One sentence of context (if any; often the headline + chart is enough)
- No body-copy paragraphs

If a slide has two competing claims, it's two slides. If a slide needs an appendix, the appendix is a follow-up doc.

## Step 5 — Talk track (what the PSM says *between* slides)

For each slide, the talk track answers:
- What does the partner already know about this?
- What's the *new* claim being made?
- Where is the partner most likely to push back?
- What's the right response if they do?
- What's the transition to the next slide?

The talk track is for the PSM rehearsing the night before. It is *not* shown to the partner.

## Step 6 — Followups slide (the most important slide)

Default structure:

| Action | Owner | Date | Cadence to review |
|---|---|---|---|
| [Specific action, in the partner's framing] | [Named person, our side OR partner side] | [Real date, not "Q3"] | [Weekly / biweekly / monthly until done] |

**Rules:**
- Every action has all 4 columns. Missing any column = the action isn't tracked.
- Multiple owners on one action = no owner. Pick one.
- "Continue to monitor X" is not an action.
- Capture commitments in the partner's words, not yours, where possible. ("Susan committed to enabling feature X by 2026-07-01" — not "Partner agreed to expand usage.")

## Step 7 — Post-QBR commitment tracking

The followups slide doesn't track itself. After the QBR:

- Convert the followups into a tracked plan (the touchpoint-log template captures this)
- Set the review cadence (default: biweekly during the followup window)
- Block calendar time for each review
- Surface at-risk actions in the next touchpoint, not at the next QBR (3 months later)

A QBR followup that's only re-examined at the next QBR is a churn vector.

## Step 8 — Mock-QBR rehearsal (the easy 30-min win)

Before the real meeting, the PSM runs through the deck out loud — to a colleague, a manager, or a recorded version of themselves. Catches:
- Slides that read fine and present terribly
- Claims that the PSM can't actually back up (revealing the data pull is shakier than the slide implies)
- Talk-track transitions that don't work in spoken form
- Time-bombs (the slide that will spark a 20-minute debate; decide upfront whether to keep, soften, or move to appendix)

## Renewal-QBR variant

When the QBR is ~90 days from a renewal date, add:
- **Decision-maker confirmation** — verify the named decision-maker is still in the role; refresh the partner profile if not
- **Multi-year vs single-year framing** — explicit recommendation with rationale
- **Objection pre-handling** — top 3 likely objections, with the prepared response for each
- **Champion engagement check** — at least one named champion-side stakeholder is in attendance

## What this skill does NOT cover

- Designing the underlying metrics (route to `partner-health-scoring` or `learning-analytics-analyst`)
- Designing the renewal play itself (route to `success-playbook-designer`)
- Parent / school-facing summaries of QBR content (route to `ferpa-comms-translator`)
- Long-form post-QBR executive memo (route to `ravenclaude-core/documentarian`)
