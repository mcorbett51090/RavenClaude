# A fix without a control plan didn't happen — every improvement ships with a control plan and an owner or the gain silently regresses

**Status:** Absolute rule — an improvement without a control plan is a temporary deviation from the old process. Regression is the default; sustainment requires a system.

**Domain:** DMAIC Control phase / process sustainment

**Applies to:** `process-improvement`

---

## Why this exists

Process gains revert. This is not a sign of weak willpower or bad culture — it is the default behavior of any complex system when the sustaining mechanism is absent. Three forces drive regression:

1. **Turnover and onboarding** — new team members learn from whoever trains them, and trainers default to "how we used to do it" when no standard work exists.
2. **Pressure and shortcuts** — under load, people revert to the fastest path they know, which is often the pre-improvement path.
3. **System inertia** — the surrounding systems (tools, templates, approval workflows, reports) were built for the old process; without deliberate change, they pull behavior back.

The evidence: in many DMAIC programs, 40–70% of process improvements show meaningful regression within 12–18 months when no control system is installed. The improvement team solved the problem; the organization restored it.

A control plan changes the default. It is not optimism about behavior — it is a system that makes the improved method the path of least resistance and makes drift visible before it becomes a new baseline.

## What a control plan must contain

A control plan without all four elements is incomplete. Each element is non-negotiable:

| Element | What it does | Why it's required |
|---|---|---|
| **Control chart + alert** | Detects drift before it becomes a trend | Without this, regression is invisible until the problem is already serious |
| **Standard work at point of use** | Makes the improved method the default, easiest path | Without this, muscle memory and informal training restore the old method |
| **Reaction plan** | Tells the owner exactly what to do when a signal fires | Without this, the chart rings and no one knows what action to take; the alert becomes noise |
| **Named Process Owner** | A specific person accepts accountability for the process going forward | Without this, "the team" owns it, which means no one owns it |

## How to apply

At the close of the Improve phase, before any project is declared complete:

1. **Complete the control plan table** — one row per improved CTQ; every column filled. See `control-plan.md` template. No TBDs.

2. **Calculate new control limits from post-improvement data** — ≥ 20 data points after the change. Do not carry pre-improvement limits into the monitoring period.

3. **Write the reaction plan as a decision tree, not a narrative** — the first responder should be able to find the right action in under 1 minute under pressure.

4. **Put standard work at the point of use** — not in a SharePoint folder. Pinned in the workflow tool, linked in the ticket template, printed at the workstation. Where the work happens, not where it could be looked up.

5. **Name the Process Owner before the tollgate** — the Process Owner should be engaged from the charter (Define phase), not introduced at the Control phase. The Control phase is the transfer of accountability, not the introduction.

6. **Get the Process Owner's signature on the control plan** — this is the handoff contract. Without it, the improvement team is still responsible for the process.

7. **Run the Control-phase tollgate with the sponsor** — confirm the gain is real (≥ 20 post-improvement points showing stable process at the new level) and the control plan is complete.

```
The minimum viable control plan:
  CTQ: Hiring time-to-fill
  Chart: I-MR on weekly average time-to-fill; UCL = 42 days; LCL = 18 days
  Ruleset: Western Electric Rules 1–4
  Alert: Automated weekly report to hiring@company.com; UCL breach triggers Slack notification
  Standard work: Requisition-to-offer checklist pinned in ATS; required on every req
  Reaction plan: If Rule 1 breach → check for open reqs > 30 days; identify step where req stalled
                 If Rule 4 (sustained high) → review comp approval queue with HR VP within 5 days
  Owner: Head of Recruiting (signed 2026-03-15)
```

**Do:**
- Build the control plan in parallel with the Improve-phase pilot, not after project close
- Treat the control plan as incomplete if any row has "TBD" or "team" as owner
- Include a scheduled control-plan review date (typically 3 and 12 months post-close)

**Don't:**
- Close the DMAIC project before the control plan is signed
- Substitute a "we'll monitor it" commitment for a written plan with named owners
- Design a control chart with no reaction plan — the alarm rings, nobody knows what to do, the team learns to ignore it
- Accept a reaction plan that says only "investigate" — state what to investigate, in what order, with what expected outcome

## Edge cases

- **Quick wins (non-DMAIC)** — a Kaizen or just-do-it improvement still needs a control plan, even if informal. At minimum: who is responsible for the process, how will regression be detected, what is the response. A handshake with no documentation is not a control plan.
- **The Process Owner won't sign** — this is a sponsor escalation, not a paperwork issue. A Process Owner who won't accept the process owns it by default and has no commitment to the improvement. Surface this to the sponsor; do not close the project without resolution.
- **The process is automated** — automated processes still need monitoring (a control chart on error rates / execution times), an alert owner, and a rollback plan. The control plan applies to automated processes; the implementation lives in the monitoring infrastructure (route to `data-platform` for the alerting pipeline if the process produces digital data).

## See also

- Template: [`../templates/control-plan.md`](../templates/control-plan.md) — the artifact that operationalizes this rule
- Skill: [`../skills/control-plan-and-sustain/SKILL.md`](../skills/control-plan-and-sustain/SKILL.md) — step-by-step for building the control plan, standard work, and poka-yoke
- Skill: [`../skills/process-capability-and-spc/SKILL.md`](../skills/process-capability-and-spc/SKILL.md) — the SPC mechanics for the monitoring layer of the control plan
- Best-practice: [`./separate-common-cause-from-special-cause.md`](./separate-common-cause-from-special-cause.md) — how to read the control chart in the control plan correctly
- Best-practice: [`./measure-the-baseline-before-you-change-anything.md`](./measure-the-baseline-before-you-change-anything.md) — without a baseline, the control plan has no "before" to compare against

## Provenance

Distilled from `CLAUDE.md` §3 house opinion #6 ("Sustain-the-gain matters as much as the fix — a control plan or it didn't happen") and §4 anti-pattern ("A fix with no control plan — no control chart, no reaction plan, no standard work, no owner; the gain will revert"). The regression-rate claim (40–70% in 12–18 months) is a frequently cited practitioner finding; `[unverified — training knowledge]` — verify against a primary source (e.g., ASQ Quality Progress) before quoting to a client. The four-element control plan definition (chart, standard work, reaction plan, named owner) is standard DMAIC Control-phase practice.

---

_Last reviewed: 2026-06-03 by `claude`_
