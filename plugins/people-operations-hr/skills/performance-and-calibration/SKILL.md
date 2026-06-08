---
name: performance-and-calibration
description: "Design and run a performance cycle that treats feedback as continuous, calibration as mandatory, and ratings as evidence-based summaries — not annual surprises or manager-popularity contests."
---

# Performance and Calibration

**Purpose:** replace the once-a-year surprise review with a system where continuous feedback
is the norm, formal reviews summarize a documented record, and calibration sessions remove
the rater-bias that makes ratings reflect manager advocacy rather than actual performance.

## The operating loop

### 1. Design the performance system architecture

Before writing a review form, make three decisions:

**Decision 1: Rating scale**
- **3-point** (Below / Meets / Exceeds) — simple, forces distinction, limited signal for merit
  differentiation.
- **5-point** (1–5 or equivalent) — more nuance; requires strong calibration to prevent
  everyone clustering at 3.
- **Narrative-only** — removes false precision; requires strong writing quality and is harder
  to attach to merit mechanically.
- Traverse the performance-model selection tree in
  [`../../knowledge/people-ops-decision-trees.md`](../../knowledge/people-ops-decision-trees.md)
  before choosing.

**Decision 2: Review components**
- Self-assessment (the employee's narrative on their impact and growth).
- Manager assessment (competency-by-competency with evidence).
- Peer review (optional; adds signal, adds process load; typically 2–3 peers).
- Upward feedback (manager effectiveness; keep anonymous and aggregate).

**Decision 3: Calibration model**
- Pre-calibration (calibrate before ratings are finalized and communicated — correct approach).
- Post-calibration (calibrate after managers write ratings — poor practice; rationalization mode).
  Always pre-calibrate.

### 2. Design the continuous feedback layer

Formal reviews should summarize documented feedback, not introduce new information. The
continuous feedback layer includes:

- **Weekly/bi-weekly 1:1s** — manager-employee cadence; documented in a shared note.
- **Quarterly check-ins** — structured discussion: what's going well, what needs to change,
  career development. Documented; carries into the formal review.
- **Project retrospectives** — real-time feedback tied to deliverables, not to a calendar
  quarter.
- **Flagging mechanism** — if performance is below expectations, it is raised in the moment,
  with documentation. An annual review is never the first mention of a performance problem.

### 3. Write the review form

A good review form elicits evidence, not adjectives:

- Each competency has a definition and a 2-3 sentence prompt: "Describe a specific instance
  where [name] demonstrated / failed to demonstrate [competency]. What was the impact?"
- Space for overall summary narrative.
- Rating field comes after the narrative, not before — the narrative should drive the rating,
  not the reverse.
- A "coachable moments" or "development focus" section — what does the person need to grow?

### 4. Build the calibration pre-work packet

Before the calibration session, every manager submits:

- Proposed rating per direct report (1 per person, from the scale).
- A 2–3 sentence evidence summary justifying the rating.
- A flag for anyone being considered for promotion.
- A flag for anyone on a formal performance plan (PIP).

Collect all submissions into a calibration deck:
- One slide/row per employee (anonymize if appropriate for the session scope).
- Proposed rating + manager's evidence summary.
- Previous-cycle rating for context.
- Tenure in role.

### 5. Facilitate the calibration session

**Setup:**
- Participants: managers in the calibration group + HR facilitator.
- Time: 60–90 min for groups of 8–15. Scale proportionally.
- Goal: surface inconsistencies, not achieve consensus for its own sake.

**Protocol:**
1. Review the distribution of proposed ratings. Flag obvious outliers (all 3s from one manager,
   all 4s from another).
2. Work through the proposed ratings systematically. For each:
   - Present the evidence summary.
   - Invite the group: "Does anything here feel inconsistent with how we've calibrated this
     level before?"
   - Challenge recency bias explicitly: "Is this based on the full year or the last sprint?"
   - Challenge halo bias: "Are we rating the person or the project they were on?"
3. For split calibrations, surface the evidence on both sides. The facilitator does not cast
   a deciding vote — managers reach a documented consensus or escalate.
4. Promotions are discussed after ratings are calibrated, not before.

**Post-session output:**
- A finalized rating for every employee in scope.
- A promotion list with evidence.
- A PIP-in-progress list to track before the next cycle.
- A written rationale for any significant recalibration (manager-proposed vs calibrated rating
  differs by >1 level).

### 6. Communicate ratings and close the cycle

- Managers deliver ratings in 1:1s — never in writing first, never in a group.
- The rating conversation leads with: "Here's what I observed across the year [evidence]…
  based on that, your rating is [X]."
- Merit cycle follows calibration; never communicate merit at the same time as rating.
  Separate the conversations by at least one week so the rating is heard as performance
  feedback, not as a justification for a pay decision.
- Document the conversation. Both manager and employee should leave knowing what "keep doing" and
  "change this" looks like.

## Anti-patterns

- A formal review that is the first time an employee hears they have a performance problem.
- A calibration session where ratings are finalized before managers present evidence.
- "Calibration" that is just ratification — the most senior manager in the room's ratings
  are accepted without discussion.
- A rating scale with no rubric — "Exceeds expectations" undefined means 10 managers interpret
  it 10 different ways.
- Merit dollars communicated in the same meeting as the performance rating.

## Output

A complete performance system design: review form per cycle, calibration pre-work packet
template, calibration facilitation guide, and a cycle calendar with communication milestones.
Reference: [`../../templates/leveling-matrix.md`](../../templates/leveling-matrix.md) for
leveling context; [`../../skills/comp-bands-and-leveling/SKILL.md`](../comp-bands-and-leveling/SKILL.md)
for the merit-cycle connection.
