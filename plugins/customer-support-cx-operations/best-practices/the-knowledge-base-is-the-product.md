# The knowledge base is the product

**Status:** Pattern
**Domain:** Knowledge management and self-service strategy
**Applies to:** `customer-support-cx-operations`

---

## Why this exists

A knowledge base that has no owner, no review cadence, and no systematic process for identifying
gaps is a liability, not an asset. Articles go stale when products change. Gaps accumulate as new
contact categories emerge. Agents stop trusting the KB and either escalate or improvise. Self-service
deflection degrades. The knowledge base becomes a museum.

Treating the KB as a product — with a backlog prioritized by ticket volume, an ownership model
per article, and a review cadence triggered by traffic and age — changes the economics. Each KB
article is an investment that deflects contacts at a fraction of the per-contact cost of a live
agent. A content roadmap driven by ticket-volume demand signals is the highest-ROI investment a
support team can make for its deflection rate.

## How to apply

- **Ownership model:** every KB article has a named owner (a support agent, a product manager,
  or a subject-matter expert). Unowned articles are automatically flagged for review.
- **Review cadence:** high-traffic articles (>X views/month): reviewed quarterly minimum.
  Low-traffic articles (stale for >90 days + <Y views/month): flag for archive or refresh.
- **Content backlog from ticket data:** weekly: pull the top contact categories with no matching
  KB article or with a matching article that doesn't deflect the contact (agent notes that it
  didn't resolve). That is the new-article backlog. Prioritize by `volume × deflectability score`.
- **KB as the deflection layer, not a supplement:** route every new contact category through
  "does the KB resolve this?" before staffing to it. If the answer is yes and the article doesn't
  exist, the content gap is the primary lever.
- **Article brief template:** for each new article: title (matching the customer's question phrasing,
  not the internal product name), intent (what question does this answer?), resolution steps,
  scope (what does this article NOT cover?), owner, and review date.

**Do:**

- Build a content backlog from ticket data, not from agent requests or editorial intuition.
- Assign every article an owner and a review date.
- Measure KB health by deflection quality: articles that resolve contacts, not just articles
  that exist.
- Treat article staleness (age × traffic without review) as a risk metric.

**Don't:**

- Create a KB that anyone can edit without a review/approval step — unreviewed edits introduce
  inaccuracy at scale.
- Measure KB quality by article count — 1,000 stale articles are worse than 100 accurate ones.
- Build a KB with internal product names as article titles — customers search using their
  own language, not yours.
- Let "contact support" be the resolution step in a KB article for a self-serviceable issue.

## Edge cases / when the rule does NOT apply

For a very early-stage team (<3 agents, <100 contacts/month), a formal KB ownership model may
be premature. In that case, maintain a shared FAQ document and establish the ownership convention
before the team grows. The principle that content gaps drive contacts still applies at any scale;
formalize the process when you have the volume to justify it (typically: >200 contacts/month or
when the same question appears more than 3 times).

## See also

- [`./deflect-with-answers-not-walls.md`](./deflect-with-answers-not-walls.md)
- [`../skills/deflection-and-knowledge-strategy/SKILL.md`](../skills/deflection-and-knowledge-strategy/SKILL.md)
- [`../scripts/cx_calc.py`](../scripts/cx_calc.py) for deflection ROI calculation.

## Provenance

Reflects the KB-as-product framing from ICMI best practices, the Help Scout / Zendesk content
strategy literature, and the broader product-management-applied-to-support-ops movement. The
ticket-driven content backlog approach is aligned with the "voice of the customer through ticket
taxonomy" methodology common in enterprise CX programs.

---

_Last reviewed: 2026-06-08 by `claude`._
