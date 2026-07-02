# Higher-Education Administration — 2026 Reference

> Dated reference for the `higher-education-administration` team: the concepts that distinguish higher-ed operations and the benchmarks and metric definitions agents reach for. The durable reasoning lives in [`higher-ed-decision-trees.md`](higher-ed-decision-trees.md); this file is the freshness-anchored "what the numbers and definitions are."
>
> **Advisory, not legal / financial-aid-compliance / academic-policy advice.** Every funnel benchmark, discount-rate norm, aid rule, and retention/persistence/completion metric definition below is **volatile and institution-/system-/accreditor-specific**. Each row carries a **source placeholder + retrieval date + `[verify-at-use]`** — re-confirm against the institution's own IR definitions, the aid office, and the accreditor before it drives a target, a budget line, or an intervention. FERPA-aware: no student PII.
>
> _Last reviewed: 2026-07-02 by `claude`. Treat every specific as `[verify-at-use]` unless re-confirmed this session._

---

## 1. The enrollment funnel — stages and definitions

| Stage / rate | Definition (attach the institution's own) | Source / retrieved | Flag |
|---|---|---|---|
| Inquiry -> apply rate | Applications ÷ inquiries | _<source placeholder — institutional IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Apply -> admit rate | Admits ÷ applications | _<source placeholder — IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Admit -> yield | Deposits ÷ admits | _<source placeholder — IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Melt | (Deposits − census enrollments) ÷ deposits | _<source placeholder — IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Census enrollment | Enrolled headcount at the official count date | _<source placeholder — registrar calendar>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **Durable rule:** a target class = inquiries × apply rate × admit rate × yield × (1 − melt). Every rate above is defined by the institution's IR office — quote the definition with the number.

---

## 2. Funnel & yield benchmarks `[ESTIMATE]`

| Metric | Reference behavior `[ESTIMATE]` | Source / retrieved | Flag |
|---|---|---|---|
| Admit yield | Varies widely by institution type, selectivity, and market; a same-institution year-over-year comparison is far more meaningful than a cross-institution "benchmark" | _<source placeholder — sector benchmark>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Summer melt | A non-trivial share of deposits can melt before census; higher where competition and aid gaps are larger | _<source placeholder — sector research>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Apply rate off inquiries | Highly channel-dependent; purchased-name inquiries convert far lower than self-initiated ones | _<source placeholder>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> These are planning anchors, not quotable facts. Confirm the current benchmark and the institution's own baseline before setting a target with an owner.

---

## 3. Tuition discount rate & net tuition revenue

| Concept | Definition / behavior | Source / retrieved | Flag |
|---|---|---|---|
| Tuition discount rate | Institutional grant aid ÷ gross tuition & fee revenue | _<source placeholder — NACUBO-style methodology>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Sector discount-rate trend | The average institutional discount rate for first-time students has trended upward over recent years at many private nonprofits; the exact figure moves annually | _<source placeholder — sector survey>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |
| Net tuition revenue | Gross tuition − institutional aid | _<source placeholder — IR / budget office>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Aid yield response | Enrollment lift per discount dollar, by admit segment | _<source placeholder — institution's own regression>_ — retrieved 2026-07-02 | `[ESTIMATE]` `[verify-at-use]` |

> **Durable rule:** model net tuition revenue, not gross headcount. A rising discount rate with no net-revenue model behind it is a budget decision no one decided.

---

## 4. Retention / persistence / completion — metric definitions

| Term | Common definition variants (name yours) | Source / retrieved | Flag |
|---|---|---|---|
| Retention rate | Fall-to-fall vs term-to-term; first-time-full-time cohort vs all-entering | _<source placeholder — IPEDS / IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Persistence | Continued enrollment *anywhere* (system) vs *at this institution* | _<source placeholder — NSC / IR>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| Completion / graduation rate | 100% / 150% / 200% of normal time; which entering cohort | _<source placeholder — IPEDS / accreditor>_ — retrieved 2026-07-02 | `[verify-at-use]` |
| DFW rate | Share of a course's students earning D / F / Withdraw | _<source placeholder — registrar>_ — retrieved 2026-07-02 | `[verify-at-use]` |

> **Durable rule:** a retention or completion number is meaningless without its cohort, term, and source. IPEDS, the accreditor, and IR often define the "same" metric differently — always attach the definition before comparing.

---

## 5. How to use this file

1. Find the concept / benchmark / metric definition you need.
2. Read its retrieval date — if stale or unconfirmed this session, **re-verify** against the cited source type before quoting.
3. Quote it with its flag (`[ESTIMATE]` / `[verify-at-use]`) and its **definition** intact when it informs a decision or a client-facing number.
4. For anything that drives a target, a budget line, or an intervention: confirm against the institution's IR definitions, the aid office, or the accreditor first.

---

## See also

- [`higher-ed-decision-trees.md`](higher-ed-decision-trees.md) — the durable yield/melt, discount-rate, at-risk-triage, and enrollment-vs-retention trees.
- Skills: [`../skills/enrollment-funnel-and-yield/SKILL.md`](../skills/enrollment-funnel-and-yield/SKILL.md), [`../skills/financial-aid-and-discount-rate/SKILL.md`](../skills/financial-aid-and-discount-rate/SKILL.md), [`../skills/retention-and-student-success/SKILL.md`](../skills/retention-and-student-success/SKILL.md).
