---
scenario_id: 2026-06-05-delivery-method-selection-cmar
contributed_at: 2026-06-05
plugin: architecture-aec
product: project-delivery
product_version: "n/a"
scope: likely-general
tags: [delivery-method, cmar, design-build, gmp, estimate-class]
confidence: medium
reviewed: false
---

## Problem

An owner with a complex, schedule-sensitive project defaulted to "design-build, because it's the fast and cheap one," and was about to commit. They were also treating a concept-stage cost number as a hard budget for board approval. Two conflated errors: (1) picking a delivery method on a slogan rather than on the project's actual risk-allocation priorities, and (2) presenting an early, wide-confidence estimate as a firm commitment. The architect was asked to advise before the owner locked either in.

## Context

- Segment: institutional, complex/risky scope, owner valued **both** early cost certainty **and** keeping the architect under direct contract (not folded under a design-builder).
- Constraint: the cost number driving the board ask was built on a **concept/feasibility-level design (~10-15% complete)** — an AACE Class 5/4 screening range, not a control estimate [verify-at-use]. The owner's "design-build is cheaper" belief was a half-truth: industry comparisons show design-build compresses *schedule* (~-4.2% vs. DBB's ~+4.8% growth) but can carry *higher cost growth* (~7.2% vs. DBB ~3.6%) [verify-at-use].
- The two wants — early cost certainty + a retained architect — are exactly the CMAR profile, but nobody had named the trade explicitly.

## Attempts

- Tried: ran the delivery-method decision tree against the owner's stated priorities instead of the slogan. Speed mattered but wasn't the *sole* driver; complexity/risk and wanting builder input during design were equally weighted; and the owner explicitly wanted to keep the architect directly contracted. That combination routes to **CMAR** (CM at-risk joins early, holds a GMP, designer retained), not design-build (single-entity, designer folded in, less owner design control). Outcome: named the method that actually fit, with the trade-off explicit.
- Tried: gated the budget number on its estimate class before it reached the board. A ~10-15%-design number is a Class 5/4 *screening range* with wide accuracy and heavy contingency — it cannot carry a board commitment without disclosing the range and sizing contingency to the class (Class 1 control estimates commonly carry ~3-7% contingency; early classes materially more) [verify-at-use]. Outcome: stopped a concept number from being presented as a control budget.
- Tried: framed the cost/schedule deltas as *industry averages, not project predictions* — the +4.8% / -4.2% / 1-3% low-bid-premium figures frame the conversation; they do not size *this* project's budget (§3 #8).

## Resolution

The owner moved from a slogan-driven design-build default to a **CMAR selection that matched their real priorities** (early GMP cost certainty + retained architect + builder input on a complex scope), and the board ask was reframed with the estimate's confidence range and class-sized contingency disclosed — a defensible budget, not a concept number wearing a commitment's clothes.

**Action for the next consultant hitting this pattern:** **select the delivery method from the owner's risk-allocation priorities, not a slogan**, and **gate every budget number on its AACE estimate class before it drives a decision.** "Design-build is fast and cheap" is half-true (faster schedule, but often higher cost growth than low-bid DBB) [verify-at-use]; when an owner wants early cost certainty *and* a directly-retained architect on a complex job, that is the CMAR profile. Never present an early-class (concept) number as a late-class commitment; size contingency to the class and disclose the range. Route procurement-law/public-bid constraints to counsel and the professional of record (§3 #7). See [`../knowledge/aec-delivery-and-estimate-decision-tree.md`](../knowledge/aec-delivery-and-estimate-decision-tree.md) and the [`../skills/phase-load-the-fee/SKILL.md`](../skills/phase-load-the-fee/SKILL.md) / [`../skills/read-firm-economics/SKILL.md`](../skills/read-firm-economics/SKILL.md) playbooks.

**Sources (retrieved 2026-06-05):**
- Mastt — *Comparing CMAR vs Design-Build vs Design-Bid-Build*: https://www.mastt.com/blogs/cmar-vs-design-build
- UNLV thesis — *Performance Comparison of DBB, DB and CMAR* (cost/schedule growth figures): https://oasis.library.unlv.edu/cgi/viewcontent.cgi?article=5920&context=thesesdissertations
- AACE International 18R-97 — *Cost Estimate Classification System* (class definitions, accuracy, contingency): https://web.aacei.org/docs/default-source/toc/toc_18r-97.pdf

Cost/schedule deltas and AACE ranges are industry averages and class rules-of-thumb, not project predictions — treat as `[verify-at-use]` and validate against a project-specific risk analysis before any deliverable (§3 #8). Delivery-method procurability is constrained by public-bid/procurement law — route to counsel (§3 #7).
