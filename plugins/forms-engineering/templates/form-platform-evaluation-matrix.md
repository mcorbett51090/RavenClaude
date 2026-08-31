# Form platform evaluation — `<decision name>`

**Owner:** `<named person>` · **Date:** `<YYYY-MM-DD>` · **Candidates:** `<A>`, `<B>`, `<C>`

Axes defined in [`../knowledge/form-platform-evaluation.md`](../knowledge/form-platform-evaluation.md). Scored by [`../skills/form-intake-and-triage-design/SKILL.md`](../skills/form-intake-and-triage-design/SKILL.md) step 7.

⛔ **No pricing and no feature counts go in this table.** Both go stale within a quarter and a stale comparison reads authoritative long after it stopped being true. Record the axis verdict and the reason; look the numbers up on the day you decide.

⛔ **This is not a weighted sum.** A **blocking** score on any single axis ends the evaluation for that candidate. Weighted sums let three cheap wins outvote one disqualifier.

---

## Scores

Score each cell `blocking` / `costly` / `acceptable`, and put the reason in the cell. A cell with a verdict and no reason is not filled in.

| # | Axis | `<A>` | `<B>` | `<C>` |
| --- | --- | --- | --- | --- |
| 1 | Egress: verifiable signature, replay defence, retry distinguishable | | | |
| 2 | Data residency: where the rows and attachments come to rest | | | |
| 3 | DPA/BAA available on the plan we can actually buy — **legal ruling required** | | | |
| 4 | Limits: submission volume, attachment size and type, retention | | | |
| 5 | Export: both the data **and** the form definition | | | |
| 6 | Accessibility of the vendor's own rendered markup — tested, not claimed | | | |
| 7 | Do we keep our own anti-abuse layer, and can we see what it rejected | | | |

## Disqualifications

| Candidate | Axis | Why it is blocking |
| --- | --- | --- |
| | | |

## Routing

| Question | Goes to |
| --- | --- |
| Is the DPA sufficient for our jurisdiction and data classes? | [`../../data-governance-privacy/CLAUDE.md`](../../data-governance-privacy/CLAUDE.md) **and the owner** — this plugin flags it, it does not rule on it |
| Is the vendor's rendered form accessible? | [`../../web-design/agents/accessibility-auditor.md`](../../web-design/agents/accessibility-auditor.md) |
| How do we verify their outbound call? | [`../../web-commerce/skills/webhook-hardening/SKILL.md`](../../web-commerce/skills/webhook-hardening/SKILL.md) |
| We are building it ourselves — where does the data live? | [`../../data-platform/skills/stack-selection/SKILL.md`](../../data-platform/skills/stack-selection/SKILL.md) |
| Is the attachment path safe? | [`../../ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md) §File handling, verdict to [`../../ravenclaude-core/agents/security-reviewer.md`](../../ravenclaude-core/agents/security-reviewer.md) |

## Decision

| | |
| --- | --- |
| **Chosen** | |
| **The axis that decided it** | |
| **What we accepted** | |
| **What would make us revisit** | |
