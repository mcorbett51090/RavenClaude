# optometry-eyecare-practice

A RavenClaude plugin: an **optometry / eye-care practice operations** specialist team for the three engines of an eye-care practice — the clinical exam flow, the optical dispensary, and the front-office / billing split that makes optometry distinct.

> Inherits the domain-neutral team constitution and protocols from [`ravenclaude-core`](../ravenclaude-core/). Requires `ravenclaude-core@>=0.7.0`.

> **Advisory domain operations knowledge — not medical, legal, coding, or billing advice.** Payor rules, CPT/coding specifics, vision-plan benefits, and clinical recall intervals are volatile and payor-/protocol-specific: each carries a retrieval date + `[verify-at-use]` and must be confirmed before it drives a claim, a quote, or a schedule. The agents store no PII/PHI.

## What it's for

Running an eye-care practice well: a full schedule fed by recall, an exam lane that protects the doctor's chair time, an optical that captures the exam into a well-margined sale, and a front desk that routes each visit to the right payor with the right code and clean eligibility.

## Agents

| Agent | Use for |
|---|---|
| **practice-operations-lead** | Scheduling, pretesting workflow, exam-room/lane flow, recall/recare cadence, clinical capacity |
| **optical-dispensary-manager** | Frames & lens inventory, optical capture rate & sales, lab orders, managed-vision-care formularies |
| **front-office-billing** | Medical-vs-vision billing split, eligibility, CPT/coding for eye exams, payor mix, claims/denials |

## What's inside

- **5 skills** — schedule-and-recall-management, exam-flow-and-pretesting, optical-capture-and-dispensary, medical-vs-vision-billing, eligibility-and-claims.
- **Knowledge bank** — [`eyecare-practice-decision-trees.md`](knowledge/eyecare-practice-decision-trees.md) (4 Mermaid trees: medical-vs-vision routing, recall cadence by exam type, optical capture improvement, denial triage) + [`eyecare-practice-reference-2026.md`](knowledge/eyecare-practice-reference-2026.md) (dated reference, verify-at-use).
- **8 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **3 templates** — practice KPI dashboard, recall campaign plan, billing-route decision.
- **3 commands** — `/route-claim`, `/plan-recall`, `/review-optical-capture`.
- **1 advisory hook** — `check-eyecare-billing-smells.sh` (refraction note with no medical-vs-vision route, recall plan with no interval, payor reference with no date/verify-at-use). `EYECARE_STRICT=1` to block.

## Seams

General medical revenue-cycle mechanics → [`medical-revenue-cycle`](../medical-revenue-cycle/) · comparable (distinct) service-practice models → [`dental-practice`](../dental-practice/), [`veterinary-practice`](../veterinary-practice/).

## Install

```shell
/plugin marketplace add ./        # from a separate Claude Code project, pointed at this repo
/plugin install optometry-eyecare-practice@ravenclaude
```

See the team constitution in [`CLAUDE.md`](CLAUDE.md) for the advisory scope, routing rules, house opinions, and the output contract.
