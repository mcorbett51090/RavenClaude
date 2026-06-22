---
name: partner-training-program-design
description: Design partner-facing training programs for EdTech — train-the-trainer is the only model that scales in K-12. K-12 PD modality decision rule (live-in-person / live-virtual / hybrid / async-with-followup), PD-credit alignment with state frameworks, teacher-union overlay in unionized states. Used by `ravenclaude-core/documentarian` + `edtech-partner-success-manager` + `success-playbook-designer`.
---

# Skill: partner-training-program-design

> **Invoked by:** `ravenclaude-core/documentarian` (when content-designing training materials), `edtech-partner-success-manager` (when planning a partner's training rollout), `success-playbook-designer` (when authoring an enablement play).
>
> **When to invoke:** any question of the shape "how should this partner's staff be trained on our product?" Includes initial-rollout training, ongoing enablement, certification programs, learning paths, and the train-the-trainer model specifically.
>
> **Output:** a training program (or single curriculum artifact) that respects the partner-segment's PD norms, modality preferences, and certification/PD-credit expectations.

## The core insight

**Direct vendor-to-end-user training doesn't scale in K-12.** A district with 800 teachers cannot be trained by a vendor's PSM running 40 sessions. The only model that works is **train-the-trainer** — equip 2-3 internal champions per district to run the training cascade locally. This skill encodes that model + the K-12-specific PD norms that make it work.

## The flow

1. **Identify the partner segment** — K-12 / higher-ed / corp L&D. PD norms differ materially.
2. **Identify the training motion type:**
   - **Implementation training** — at go-live; covered by [`implementation-90-day-arc.md`](../implementation-90-day-arc/SKILL.md) week 5-6 + [`../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md)
   - **Sustained enablement** — quarterly waves, new-feature rollouts, refreshers
   - **Certification / learning paths** — for partners that want formal completion tracking
   - **Train-the-trainer specifically** — see the dedicated curriculum template
3. **Layer the segment-specific PD norms** from [`../knowledge/k12-pd-norms-and-constraints.md`](../../knowledge/k12-pd-norms-and-constraints.md) — teacher PD hours, in-service days, asynchronous-vs-synchronous norms, district PD-credit policies.
4. **Choose modality** — live-virtual / live-in-person / hybrid / asynchronous-with-followups. Calendar-driven, not preference-driven.
5. **Author the curriculum** using [`../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md) as the starter shape (for train-the-trainer) or adapt for the broader motion.
6. **Build the measurement loop** — how do you know the training landed? Feedback forms, post-training usage signals, champion-cascade tracking.

## K-12 PD modality decision rule

| Modality | Use when | Don't use when |
|---|---|---|
| **Live-in-person** | District has in-service days scheduled + product is hands-on / requires troubleshooting + multi-school district (gather champions geographically) | Distributed champions; no in-service window available within target rollout time |
| **Live-virtual** | Single-school or geographically-distributed champions + product is workflow-oriented + ≤ 90 min sessions | Hands-on troubleshooting required; need-side-by-side device interaction; champion broadband / video conferencing constraints |
| **Hybrid** | Long-form (3+ hour) training where chunks can be async + champions need cohort cohesion | Short sessions (90 min or less); hybrid overhead exceeds value |
| **Asynchronous + live followup** | Self-paced learners; multiple sessions over weeks; reference-able content needed | First-touch training; teachers who need real-time questions answered |

## Higher-ed PD modality (briefly)

Higher-ed PD respects faculty time differently than K-12 — academic-affairs office is the gatekeeper; faculty PD is opt-in not required; "training" framing often lands poorly (frame as "professional development for instruction" or "academic-technology integration"). Asynchronous-with-followup is the default; synchronous reserves for high-stakes or hands-on.

## Corporate L&D PD modality (briefly)

Corporate L&D operates on quarterly business calendar + has dedicated L&D function. Cohort-based, often integrated with LMS-of-record. Certification is more important than in K-12. Mobile-first asynchronous + monthly cohort cohorts is the dominant pattern.

## The certification / learning-path question

When should the program offer formal certification + learning paths?

- **Yes, certify, if:** partner specifically asks; partner segment values formal completion (corporate L&D leans yes); product surface is broad enough to warrant tiered learning; certifications drive sustained adoption.
- **No, don't certify, if:** partner segment doesn't value it (most K-12 districts treat certifications as nice-to-have, not load-bearing); product is narrow (one workflow doesn't need 5-level certification); vendor team doesn't have the bandwidth to maintain a certification program (a stale certification is worse than no certification).

## Anti-patterns this skill flags

- **Direct vendor-to-teacher training at scale.** Vendor PSMs cannot personally train 800 teachers. Train-the-trainer is the only model that scales.
- **Training without measurement.** Sessions happen; feedback never collected; effectiveness unknown. Always include a feedback loop.
- **Synchronous-only.** Some learners need to re-watch; some districts have async-first PD policy; some teachers can't attend live. Always have async reference material even when sync is the primary modality.
- **Generic "PD" framing in higher-ed.** Higher-ed faculty don't see themselves as needing "PD" — frame as professional development for instruction, or academic-technology integration, or pedagogical-tools workshop.
- **Train-the-trainer that's product-only.** Champions need facilitation craft, not just product knowledge. The [`../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md) has both Session 1 (product depth) and Session 2 (facilitation craft) for this reason.
- **Certification without maintenance plan.** Stale certifications signal stale product. If you ship a cert, plan the quarterly refresh.
- **Ignoring district PD-credit conventions.** Some districts award PD credit for vendor training only if the sign-in sheet + learning-objectives align with the state PD framework. Confirm at engagement start.

## When NOT to invoke

- The partner already has a training program operating — defer to their motion + provide content reference material.
- The training need is < 1 hour of content. Use a quickstart guide / video instead.
- The partner is corporate L&D with their own LMS-of-record. Plug into their LMS rather than running a parallel program.

## Refresh triggers

- A state's PD-credit conventions materially change
- A district-level PD modality shift (post-COVID async-first to in-person-first reversion, etc.)
- New product line that opens a new training surface
- Live engagement signal via `/wrap` shows train-the-trainer cascading failing in a way this skill didn't anticipate

## References

- [`../../knowledge/k12-pd-norms-and-constraints.md`](../../knowledge/k12-pd-norms-and-constraints.md) — PD hours, in-service days, async/sync norms, district PD-credit conventions
- [`../../templates/train-the-trainer-curriculum.md`](../../templates/train-the-trainer-curriculum.md) — the train-the-trainer artifact
- [`implementation-90-day-arc.md`](../implementation-90-day-arc/SKILL.md) — where this skill plugs into the implementation arc (weeks 5-6)
- [`../knowledge/edtech-segment-fundamentals.md`](../../knowledge/edtech-segment-fundamentals.md) — segment-by-segment differences
- [`../knowledge/k12-psm-operating-cadence.md`](../../knowledge/k12-psm-operating-cadence.md) — when to schedule training (avoid dead zones)
- [`../knowledge/parent-comms-jurisdictional-bear-traps.md`](../../knowledge/parent-comms-jurisdictional-bear-traps.md) — Module 5 of the train-the-trainer curriculum (FERPA/multilingual content)
