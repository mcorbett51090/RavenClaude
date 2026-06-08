---
name: structured-hiring
description: "Run a structured, bias-resistant hiring process end-to-end: design the interview loop, write competency-anchored scorecards, brief interviewers, facilitate the debrief, and close with a defensible hire/no-hire decision."
---

# Structured Hiring

**Purpose:** replace impression-based hiring with a repeatable, evidence-grounded process where
every stage has a defined competency, every interviewer has a structured question set and a
scoring rubric, and the debrief produces a hire/no-hire from evidence — not consensus or
seniority.

## The operating loop

### 1. Define the role competencies (before writing the JD)

Identify 4–7 competencies that are genuinely predictive of success in this role. Distinguish:

- **Must-haves** — absence is a no-hire (e.g., production on-call experience for a Staff SRE).
- **Nice-to-haves** — gap is coachable; absence alone doesn't disqualify.
- **Role-specific technical competencies** — e.g., distributed-systems design, SQL proficiency.
- **Cross-cutting behavioral competencies** — e.g., cross-functional communication, handling
  ambiguity, bias for action.

Avoid "culture fit" as a competency unless it maps to a specific, observable behavior. "Culture
fit" as a gestalt feeling is a bias amplifier.

### 2. Write the job description with a bias audit

- Use experience-based requirements, not credential proxies (degree requirements unless legally
  required or directly relevant).
- Audit for gendered language (tools like Textio, Gender Decoder — apply the same logic manually
  if tools are unavailable): avoid "aggressive", "dominant", "ninja/rockstar/guru", "young",
  "energetic" as coded descriptors.
- Include the compensation band. Hiding comp creates mismatched pipelines and signals
  pay-opacity.
- Lead with "what you'll do", then "what we need" — not a credential list followed by optional
  job duties.

### 3. Design the interview loop

Map each competency to exactly one stage and one primary interviewer. No competency goes
uncovered; no competency is covered by more than two interviewers.

| Stage | Owner | Competency(ies) | Format |
|-------|-------|-----------------|--------|
| Recruiter screen | Recruiter | Logistics, motivation, baseline requirements | 30 min phone/video |
| Hiring manager screen | HM | Role scope alignment, career narrative | 45 min video |
| Technical assessment | Tech interviewer | Role-specific technical competency | 60–90 min |
| Behavioral panel | Panel (2) | Cross-cutting behavioral competencies | 60 min, split ownership |
| Executive/skip-level | Executive | Company values, org fit at level | 30 min |
| Reference check | Recruiter/HM | Confirmation of behavioral competencies | 30 min, structured |

Aim for ≤5 live stages, ≤8 interviewers total. Every additional interview increases candidate
drop-off and interviewer-hour cost.

### 4. Write the scorecard

For each competency:

1. **Definition** — one sentence, behavioral and observable.
2. **Rubric anchors** — example behaviors at each level (1 = Strong No Hire … 4 = Strong Hire,
   or 1–5 with explicit midpoint definition).
3. **Sample STAR questions** (2–3 per competency) — "Tell me about a time when…" with probes.
4. **Red flags** — specific answer patterns that signal a low score.

Overall recommendation: Strong Hire / Hire / No Hire / Strong No Hire — **not** "maybe" or
"leaning". Force the interviewer to a position.

Template: [`../../templates/interview-scorecard.md`](../../templates/interview-scorecard.md).

### 5. Brief every interviewer before they go in

Send each interviewer:
- The competency they own (one, named explicitly).
- The question set and rubric.
- A reminder: complete the scorecard independently before the debrief; do not discuss with
  other interviewers.

### 6. Run the structured debrief

1. **Scorecards first.** Collect all scorecards before the meeting begins.
2. **Go in reverse seniority.** Junior interviewers speak first to avoid anchoring on the most
   senior voice.
3. **Evidence, not impressions.** "She handled the distributed-locking question by proposing X
   and acknowledged the Y tradeoff" beats "she seemed sharp."
4. **Unanimous Strong Hire → proceed.** Split panel (any No Hire + any Hire) → re-examine
   the evidence; if still split, a Strong No Hire on a must-have competency is disqualifying.
5. **Document the rationale.** The debrief outcome is a written record, not a verbal call.

### 7. Close ethically

- Reject candidates with a specific, honest reason where possible (and legally permissible).
- Protect comp negotiation: make the offer based on the band, not the candidate's stated
  history.
- Collect candidate-experience NPS at close (both accepts and declines).

## Anti-patterns

- Unstructured "get to know you" interviews with no scorecard.
- Debriefs where the HM speaks first and the panel converges.
- A "culture fit" vote at the end that can override all structured scores.
- Offer letters issued before the comp band for the role is established.
- No feedback loop: candidates never get a reason for a decline.

## Output

A complete hiring kit per role: job description with bias audit, a stage-by-stage loop with
competency mapping, a scorecard per stage (template filled in), interviewer briefing notes, a
debrief facilitation guide, and a close/offer checklist. Use
[`../../templates/interview-scorecard.md`](../../templates/interview-scorecard.md) for scorecard
artifacts.
