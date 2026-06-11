---
name: developer-community-funnel-design
description: "Design a developer community as a funnel — size and instrument lurker → asker → answerer → contributor → champion, find the stuck stage, install the matching intervention (response SLAs, recognition loops, good-first-issues), and read unanswered questions as a docs-gap signal."
---

# Developer Community Funnel Design

**Purpose:** grow a community that converts and answers itself, by treating it as a funnel with stage
conversions rather than a member count to broadcast at.

---

## Steps

### 1. Size and instrument the funnel

```
lurker → asker → answerer → contributor → champion
```

For each stage, measure the population and the conversion to the next. Use
[`../../scripts/devrel_calc.py`](../../scripts/devrel_calc.py) `community_health` (active ratio,
answer rate, contributor conversion). A member count with no stage breakdown hides the health story.

### 2. Find the stuck stage

| Stuck transition | Usual cause | Intervention |
|---|---|---|
| lurker → asker | unclear where/how to ask, low safety | seed questions, set norms, visible "ask here" |
| asker → answerer | no recognition for answering | recognition loop, surfaced answerer status |
| answerer → contributor | no on-ramp to contribute | good-first-issues, contribution guide |
| contributor → champion | no growth/access path | ambassador tier with a real value exchange |

### 3. Install response coverage

Define a first-response SLA and triage roles so questions don't rot. An unanswered question is both a
lost asker and a missed signal. Track answer rate and time-to-first-response weekly.

### 4. Read unanswered questions as docs gaps

A recurring question is a missing quickstart section. Route the top recurring questions to
[`docs-and-dx-engineer`](../../agents/docs-and-dx-engineer.md) — answering once and documenting beats
answering the same thing forever
(see [`answer-once-then-document-it`](../../best-practices/answer-once-then-document-it.md)).

### 5. Build the answerer and contributor flywheel

Recognition compounds. Surface and reward people who answer and contribute; a community that
celebrates its answerers grows its own capacity, which is the only way community scales past staff.

---

## Output

A community-funnel model (each stage's population + conversion), the stuck stage, and the
intervention. Use the [`community-health-scorecard`](../../templates/community-health-scorecard.md)
template; deepen with the
[`community-and-ecosystem-reference`](../../knowledge/community-and-ecosystem-reference.md).
