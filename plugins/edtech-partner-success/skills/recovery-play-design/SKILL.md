---
name: recovery-play-design
description: Design red-flag intervention sequences — root-cause diagnostic before remedy (4 parallel hypotheses), time-bound recovery plan with measurable 30/60/90-day signal targets, escalation criteria (PSM → success leadership → exec sponsor → counsel → churn-prep), the "is this recoverable?" rule, churn-prep workflow when not, and the post-recovery learning capture. Reach for this skill when a partner trips red on the health score, when a renewal is at clear risk, or when a partner has signaled dissatisfaction. Used by `success-playbook-designer` (primary) + `partner-success-manager`.
---

# Skill: recovery-play-design

> **Invoked by:** `success-playbook-designer` (primary — when authoring or refreshing the firm's recovery plays), `partner-success-manager` (when executing recovery on a specific partner).
>
> **When to invoke:** when a partner trips red on the composite health score OR fires an independent red-flag trigger; when a renewal is at clear risk; when a partner has signaled dissatisfaction (explicit complaint, vendor-comparison signal, escalation); when designing the firm's recovery playbook.
>
> **Output:** a time-bound, measurable recovery plan with named escalation criteria, OR a churn-prep workflow if the situation isn't recoverable, AND a post-recovery learning capture for the play library.

## The core opinion this skill encodes

**Diagnose before treat.** The most common recovery-play failure mode is offering a remedy (price relief, executive escalation, success-team intensification) *before* understanding which of the four parallel hypotheses is actually driving the red flag. The wrong remedy on the right diagnosis is bad; any remedy on a misdiagnosis is worse — it consumes goodwill, signals desperation, and doesn't fix the actual cause.

Second core opinion: **time-bound or it's not a plan.** "We'll improve engagement" is not a recovery plan. "Active-user count returns to 60% by Day 30, 80% by Day 60" is. Without measurable signal targets and dates, recovery becomes vibes — and vibes can't be reviewed.

Third: **some partners aren't recoverable.** Pretending otherwise burns the PSM, burns budget, and produces a worse churn than a graceful exit would.

## The red-flag taxonomy

A red flag fires recovery — but *which* flag determines which diagnostic branch matters most.

| Red flag | Leading-indicator strength | Most-likely root cause |
|---|---|---|
| **Usage collapse** (>30% WoW drop) | Strong, fast | Implementation health, calendar artifact, or product friction |
| **Sponsor change / departure** | Strong, slow-burn | Sponsorship gap; renewal at risk |
| **Rostering / data crisis** | Strong, fast | Implementation health; often masquerades as product complaint |
| **Escalated support ticket** (esp. to leadership) | Strong | Product fit OR implementation health |
| **Vendor-comparison signal** ("we're looking at X") | Strong, leading | External pressure; can be defensive or genuine |
| **Mid-contract financial pressure** on the partner | Medium | External pressure; ESSER cliff, L&D budget squeeze |
| **Leadership skepticism** signal (new exec questions value) | Strong, slow-burn | Sponsorship; value-evidence gap |
| **21+ days of zero meaningful touchpoints** (active season) | Medium, leading | PSM-side gap, not partner-side — handle internally first |

The same red flag can fire from different root causes; the diagnostic decides the remedy.

## The 4-hypothesis diagnostic (run in parallel)

Before any remedy ships, the PSM runs four hypotheses *in parallel* — not sequentially. Sequential diagnosis takes weeks; parallel diagnosis takes days.

### Hypothesis A — Product fit

Is the product actually doing what the partner needs it to do?

- Re-read the success plan; have the *partner-stated* goals shifted?
- Has the product surface changed in a way that removed something the partner depended on?
- Has a competing product appeared that solves the same problem with a better fit for the partner's segment?

### Hypothesis B — Implementation health

Is the product working but the partner can't use it properly?

- Rostering / SSO / SIS-LMS sync issue (see [`rostering-data-quality.md`](../rostering-data-quality/SKILL.md))
- Train-the-trainer cascade collapse (the trained champions left; their replacements weren't trained)
- Calendar artifact (a state-testing window suppressing the signal — see [`adoption-sequencing-k12.md`](../adoption-sequencing-k12/SKILL.md))
- Feature-tier mismatch (partner is on the wrong tier for what they're trying to do)

### Hypothesis C — Sponsorship

Has the buying committee changed in a way that we missed?

- Named sponsor lost (left org, demoted, sidelined) — see [`executive-sponsor-mapping.md`](../executive-sponsor-mapping/SKILL.md)
- Champion lost — single-thread failure
- New skeptic-in-position arrived with authority
- Ghost-sponsor pattern (named sponsor never engaged; we only discovered it now)

### Hypothesis D — External pressure

What's happening *to* the partner organization that has nothing to do with us?

- District / school / department budget cut (ESSER cliff, enrollment decline, L&D-cuts pattern)
- Org-wide tool consolidation initiative ("we're cutting 30% of our tools")
- New executive with an agenda that includes vendor review
- Regulatory / compliance change forcing a vendor-comparison exercise

**The diagnostic output** is a written hypothesis ranking — which of the four is most likely, what evidence supports it, what would falsify it. Default to written (team constitution §3 #9).

## The time-bound recovery plan

The plan has 30 / 60 / 90 day signal targets. Each target is:

- **Measurable** — the signal itself, the source query, the comparison baseline
- **Time-bound** — a specific date, not "Q3"
- **Owned** — a named person on each side
- **Conditional-on** — what the partner has to do AND what we have to do for the target to materialize

### Day 30 — recoverable signal

The earliest point at which a measurable signal can show whether the recovery is taking hold. Examples by red-flag type:

- Usage collapse → active-user count back to 60% of baseline
- Rostering crisis → sync running clean for 14 consecutive days
- Sponsor change → new sponsor confirmed engaged in at least 2 touchpoints
- Escalated ticket → resolution accepted by the partner, in writing
- Vendor-comparison signal → joint conversation with the named decision-maker confirming we're still in consideration

### Day 60 — sustained signal

The signal is not a one-time spike. It's holding.

- Usage at 75-80% of baseline, sustained 30 days
- Sync clean 45 days
- New sponsor has attended a real working session (not a courtesy intro)
- No second escalation
- DPA / DPA-renewal or RFP positioning has progressed

### Day 90 — value-restoration signal

The original success-plan outcomes are back on track (or a replan has been mutually accepted).

- Usage at 90%+ of baseline
- A new outcome metric is materializing
- The renewal conversation is back on a normal play (not a recovery sub-play)
- OR (legitimate alternative) — the partner and PSM jointly agree the original success plan needs revision, and the new plan is written

If Day 30 or Day 60 misses, the plan branches — either to a deeper recovery (escalation, harder remedy) or to a churn-prep workflow.

## Escalation criteria

The PSM doesn't own the entire recovery alone. Escalation is *part of the play*, not failure of it.

| Trigger | Escalate to |
|---|---|
| Diagnostic hypothesis confirms product-fit gap that requires roadmap visibility | Product leadership |
| Sponsor change requires re-onboarding of an exec | Success leadership + the vendor exec sponsor |
| Day 30 signal target missed | Success leadership review |
| Day 60 signal target missed | Vendor exec sponsor engaged with partner exec sponsor |
| Vendor-comparison signal becomes "we've issued an RFP" | Vendor exec sponsor + AE if applicable; defense play activates |
| Legal-relevant dispute (DPA breach, FERPA / state-privacy claim, contract dispute) | Counsel — mandatory; PSM does NOT freelance the response |
| Partner explicitly signals intent to non-renew | Churn-prep workflow activates (see below) |
| Recovery plan has missed 2+ targets in a row | "Is this recoverable?" rule (see below) |

**Anti-pattern:** the PSM running a 6-month recovery alone because escalation feels like failure. Escalation is the play. Not escalating turns a 90-day recovery into a 9-month one.

## The "is this recoverable?" rule

After Day 60 (or earlier if multiple targets miss), the PSM runs this check honestly:

| Condition | Implication |
|---|---|
| Sponsor lost AND no replacement willing to engage | **Leading indicator of unrecoverable.** Move toward churn-prep. |
| Product-fit gap AND no roadmap visibility AND partner has named a competitor | **Unrecoverable in current form.** Negotiate graceful exit or major restructure. |
| External pressure (budget cut) AND no scoped-down option fits partner's remaining budget | **Unrecoverable at current scope.** Offer scope-down or graceful exit. |
| Implementation health AND partner-side champion has the will to fix | **Recoverable.** Continue the play. |
| Sponsorship gap AND new sponsor identified AND willing to re-engage | **Recoverable.** Pivot to re-onboarding. |
| Two consecutive Day-X signal misses with no honest explanation | **Possibly unrecoverable.** Escalate; run the rule again at next checkpoint. |

The rule is a forcing function for honesty, not a gate that has to be passed. The point is to surface the choice between "more recovery" and "graceful exit" at the right time — not at T-7.

## Churn-prep workflow (when not recoverable)

When the answer is "not recoverable," the play *doesn't end*. The PSM's job is now graceful exit + reference protection + learning capture.

1. **Confirm internally first** — success leadership + AE (if applicable) + vendor exec sponsor agree the partner is unrecoverable. **Don't telegraph to the partner before this.**
2. **Graceful exit conversation** — partner-facing, owned by the senior on the vendor side (often the exec sponsor, not the PSM). Acknowledges reality; doesn't gaslight the partner with false-positive framing.
3. **Off-boarding migration support** — data export, transition timeline, end-of-license technical steps. Coordinated with the [`partner-profile-curator`](../../agents/partner-profile-curator.md) so the durable record is closed cleanly.
4. **Reference protection** — even an exiting partner's word-of-mouth matters in their segment. Generous off-boarding earns "they were professional when we left," which preserves the brand. Stingy off-boarding earns the opposite.
5. **No surprise commercial actions** — no last-minute fees, no auto-renew traps, no contractual gotchas. The cheap-feeling moves at exit get remembered for years.
6. **Learning capture** — see below.

**Anti-pattern:** the PSM treating churn-prep as the AE's problem. The PSM owns the *quality of the exit*; the AE owns the *commercial close*.

## The post-recovery learning capture

Every recovery — successful, partial, or churn — feeds the play library. Without this step, the play library never gets smarter.

Capture, in writing, to the partner profile and to a shared lessons file:

- **What fired the red flag** — which signal, which date, what was its leading-indicator strength
- **What the diagnostic concluded** — which of the four hypotheses, on what evidence
- **What worked** — which remedy moved which signal, with timing
- **What nearly worked** — what was almost-enough but missed
- **Did the play library predict this** — was there a play that should have been written and wasn't
- **What does the play library need** — new red-flag trigger; new remedy; new escalation criterion; refined "is this recoverable?" rule

Surface the learnings at the next play-library review (quarterly default). The `/wrap` slash command in this marketplace is the lightweight path to push a generalized version to the shared scenarios bank.

## Anti-patterns this skill flags

- **Offering price relief without diagnosis.** Discount-as-default removes a lever you may need later, signals desperation, and rarely fixes the actual cause.
- **Generic "let me know how we can help" comms in a red account.** Boilerplate is a smell (team constitution §3 #11) and in a red account it reads as evasion.
- **Recovery plans without time bounds.** "We'll work on it" is not a plan.
- **No escalation criteria.** PSM running a 6-month recovery alone is a PSM-as-hero anti-pattern; success leadership exists for this.
- **Sequential diagnosis** (test hypothesis A for two weeks, then B, then C) — by the time you've finished, the partner has churned.
- **Treating churn-prep as failure.** A graceful exit is a successful execution of recovery's last branch. Stinginess at exit is the failure.
- **Skipping the learning capture.** The play library never improves.
- **Pretending the partner is recoverable past Day 60 when two targets have missed and the sponsor is gone.** Hope is not a play.
- **Telegraphing churn-prep to the partner before internal alignment.** Confusing for the partner; weakens the eventual conversation.

## Hygiene checklist

Before declaring a recovery play "executing":

- [ ] 4-hypothesis diagnostic completed in writing
- [ ] Hypothesis ranking with evidence and falsification criteria
- [ ] Day 30 / 60 / 90 signal targets named, measurable, owned, time-bound
- [ ] Named escalation criteria for each milestone
- [ ] "Is this recoverable?" check scheduled for Day 60
- [ ] Touchpoint cadence intensified (default: weekly during recovery; calendar-blocked, not aspirational)
- [ ] Partner profile updated with current sponsor / champion status (per [`executive-sponsor-mapping.md`](../executive-sponsor-mapping/SKILL.md))
- [ ] Learning-capture template opened at the start (don't try to reconstruct at the end)

Before declaring a recovery play "complete":

- [ ] Day 90 signal target met OR honestly missed
- [ ] Learning capture written
- [ ] Play library updated (or routed to the play-library refresh queue)
- [ ] Partner profile reflects the final state
- [ ] If churn-prep: off-boarding completed, reference-protection delivered

## When NOT to invoke

- The signal is broken — not the partner. Run [`rostering-data-quality.md`](../rostering-data-quality/SKILL.md) before declaring a red flag.
- The signal is a calendar artifact — see [`adoption-sequencing-k12.md`](../adoption-sequencing-k12/SKILL.md) (e.g., a December engagement drop in K-12 may be school break, not partner pain).
- The partner is in a normal renewal window with no actual red flag — use [`renewal-play-design.md`](../renewal-play-design/SKILL.md) instead.
- A red flag fired but the diagnostic shows the root cause is internal-to-vendor (PSM coverage gap, support response time) — the recovery is *internal*, not partner-facing. Don't run the recovery play; fix the internal gap.

## Refresh triggers

- A pattern of recoveries succeeding at Day 30 but failing at Day 90 — the sustained-signal target isn't being designed deep enough
- A pattern of misdiagnosis — one of the four hypotheses is being missed systematically
- A new red-flag pattern emerges that the taxonomy doesn't cover
- An exit that *should have been* recoverable but wasn't — learning-capture surfaces the gap
- Escalation criteria firing too early or too late — leadership review tunes the thresholds

## References

- [`partner-health-scoring.md`](../partner-health-scoring/SKILL.md) — the signals and triggers that fire recovery
- [`executive-sponsor-mapping.md`](../executive-sponsor-mapping/SKILL.md) — sponsorship-hypothesis diagnostic input
- [`rostering-data-quality.md`](../rostering-data-quality/SKILL.md) — implementation-health-hypothesis input; also the "is the signal broken?" check
- [`adoption-sequencing-k12.md`](../adoption-sequencing-k12/SKILL.md) — calendar-artifact discrimination
- [`renewal-play-design.md`](../renewal-play-design/SKILL.md) — when recovery is also the renewal motion
- [`success-plan-authoring.md`](../success-plan-authoring/SKILL.md) — the original success plan as the diagnostic basis
- [`qbr-composition.md`](../qbr-composition/SKILL.md) — recovery-QBR variant (different cadence, different framing)
- [`../knowledge/district-implementation-failure-modes.md`](../../knowledge/district-implementation-failure-modes.md) — pattern library for implementation-health hypothesis
- [`../knowledge/partner-health-score-drift.md`](../../knowledge/partner-health-score-drift.md) — when the score-vs-reality gap is the issue
- [`../templates/escalation-memo.md`](../../templates/escalation-memo.md) — the escalation artifact
