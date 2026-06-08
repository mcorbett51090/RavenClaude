# Every cost has an owner — showback changes behavior

**Status:** Pattern
**Domain:** Cloud cost ownership and cultural change
**Applies to:** `finops-cloud-cost`

---

## Why this exists

Anonymous cost is unmanaged cost. When no individual or team sees their cloud spend, there is no
feedback loop connecting engineering decisions to their financial consequences. An engineer who
deploys a dev environment and forgets to tear it down has no signal that it is costing $800/month.
A product team that adds a new AI feature has no visibility into the inference spend it generates.

Showback — even read-only, even without chargeback — changes this. When engineers see their
team's spend in a weekly digest, three things happen: (1) they become aware of the cost
consequences of their decisions, (2) they take ownership of the items they recognize as theirs,
and (3) they bring cost into their engineering discussions without being told to. This behavioral
change is the primary value of showback, not the dashboard itself.

Chargeback operationalizes accountability by making it financial, but it requires showback first
as a foundation of trust and understanding.

## How to apply

- Design showback before chargeback. Show engineers their team's spend for 2–3 months before
  booking it to their GL cost centre.
- Make showback actionable, not just informational. Include: week-over-week delta, top cost
  drivers (service + resource type), and a link to investigate anomalies.
- Deliver showback to the person who can act on it — the engineering lead, the on-call engineer,
  the product team — not just to Finance.
- Measure behavior change, not just dashboard views. The signal is: are engineers reducing waste,
  rightsizing, and tagging after they see the report?
- Advance to chargeback only when showback has been running for >2 months, tagging coverage is
  >80%, and there is a documented allocation methodology for shared costs.

**Do:**

- Deliver the showback digest where engineers already work (Slack, email, or an embedded dashboard
  in their toolchain).
- Include a "top 3 things you could do to reduce this" alongside the spend view.
- Celebrate cost reductions publicly — cost ownership is a cultural achievement, not a punishment.
- Define unit economics (cost per customer, cost per request) so engineers see cost relative to
  the value it delivers.

**Don't:**

- Send a monthly report that lands in email and goes unread. Weekly cadence, in the right channel.
- Use showback as a blame mechanism — "your team overspent again." Frame it as empowerment, not
  accusation.
- Implement chargeback before showback. A charge without a prior period of visibility creates
  resentment, disputes, and distrust.
- Make showback reports accessible only to Finance or the FinOps team — the engineers who can
  act must be the primary audience.

## Edge cases / when the rule does NOT apply

Some cost items are genuinely shared and cannot be attributed to a specific engineering team
(e.g., shared networking, security tooling, support contracts). For these, showback using a
proportional allocation is still better than no visibility. The fallback allocation method should
be documented and consistent, even if imperfect. Showing "your team's share of shared services is
$X, allocated by CPU consumption ratio" is far preferable to hiding the cost entirely.

## See also

- [`./tag-at-birth-or-you-cant-allocate.md`](./tag-at-birth-or-you-cant-allocate.md)
- [`../templates/showback-chargeback-model.md`](../templates/showback-chargeback-model.md)
- [`../skills/cost-allocation-and-tagging/SKILL.md`](../skills/cost-allocation-and-tagging/SKILL.md)

## Provenance

Reflects the FinOps Foundation inform-phase cultural outcomes research and the consistent field
finding that engineer-visible spend reports produce cost reductions without chargeback, and that
chargeback without showback produces disputes rather than savings.

---

_Last reviewed: 2026-06-08 by `claude`._
