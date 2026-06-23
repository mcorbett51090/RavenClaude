# Optometry / Eye-Care Practice — 2026 Reference

> Dated reference for the `optometry-eyecare-practice` team: the concepts that distinguish eye-care operations and the benchmarks agents reach for. The durable reasoning lives in [`eyecare-practice-decision-trees.md`](eyecare-practice-decision-trees.md); this file is the freshness-anchored "what the numbers and rules are."
>
> **Advisory, not medical/legal/coding/billing advice.** Every payor rule, CPT/coding specific, benefit structure, and clinical interval below is **volatile and payor- or protocol-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the payor, clearinghouse, or clinical protocol before it drives a claim, a quote, or a schedule. No PII/PHI.
>
> _Last reviewed: 2026-06-22 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. Vision plan vs medical insurance — the core distinction

| Concept | Vision plan | Medical insurance | Source / retrieved | Flag |
|---|---|---|---|---|
| What it is | A routine eye-wellness + materials benefit | Major-medical coverage of eye *conditions* | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Typical trigger | Routine refraction, well-vision exam, glasses/contacts | Medical chief complaint or diagnosis | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Covers | Routine exam, refraction, materials allowance | Evaluation/management of the eye condition | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Example managed-vision-care plans | Multiple national vision-plan carriers exist; named plans, allowances, and formularies change | n/a | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Coding family | Often a routine/well-vision exam code + refraction | E/M or ophthalmological exam code to the diagnosis | _<source placeholder — CPT/coding authority>_ — retrieved 2026-06-22 | `[verify-at-use]` |

> **Routing rule (durable):** decide on the chief complaint and what the visit addressed — see the routing decision tree. Specific codes and benefit rules: `[verify-at-use]`.

---

## 2. Capture-rate benchmarks `[ESTIMATE]`

| Metric | Reference range `[ESTIMATE]` | Source / retrieved | Flag |
|---|---|---|---|
| Optical capture rate (exams -> Rx filled in your optical) | A common stretch target is a clear majority of exam patients; underperformers sit well below — exact ranges vary by practice model | _<source placeholder — industry benchmark>_ — retrieved 2026-06-22 | `[ESTIMATE]` `[verify-at-use]` |
| Second-pair / upgrade capture | Materially below first-pair capture; a known growth lever | _<source placeholder>_ — retrieved 2026-06-22 | `[ESTIMATE]` `[verify-at-use]` |
| Frames inventory turns | Practices target multiple turns per year; dead stock drags it down | _<source placeholder>_ — retrieved 2026-06-22 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors, not quotable facts. Confirm the current benchmark and the practice's own baseline before setting a target with an owner.

---

## 3. Recall / recare intervals

| Exam type | Interval (concept) | Source / retrieved | Flag |
|---|---|---|---|
| Routine refraction, healthy adult | A routine periodic interval set by clinical protocol | _<source placeholder — clinical guideline>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Contact-lens wearer | Periodic CL recheck + annual evaluation | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Medical follow-up (diabetic, glaucoma, dry eye mgmt) | Shorter, condition-driven interval per protocol | _<source placeholder — clinical guideline>_ — retrieved 2026-06-22 | `[verify-at-use]` |
| Pediatric / at-risk | Protocol-driven pediatric interval | _<source placeholder>_ — retrieved 2026-06-22 | `[verify-at-use]` |

> Recall intervals are **clinical-protocol decisions**, not operations choices. The operations job is to *act on* the protocol-set interval (build the recall list), not to set the medical interval. `[verify-at-use]` against current protocol.

---

## 4. How to use this file

1. Find the concept/benchmark/interval you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) intact when it informs a client-facing number.
4. For anything that drives a claim, a patient quote, or a clinical schedule: confirm against the payor/clearinghouse/clinical protocol first.

---

## See also

- [`eyecare-practice-decision-trees.md`](eyecare-practice-decision-trees.md) — the durable routing/cadence/capture/denial trees.
- The shared medical revenue-cycle rails: [`../../medical-revenue-cycle/CLAUDE.md`](../../medical-revenue-cycle/CLAUDE.md).
