# Build vs. Buy vs. Partner Is a Strategic Decision, Not Just a Technical One

**Status:** Pattern
**Domain:** Product strategy
**Applies to:** `product-management`

---

## Why this exists

Build-vs-buy-vs-partner decisions are routinely made by engineering teams on the basis of technical feasibility and cost, without the product strategy input that makes the decision coherent long-term. Engineering teams optimizing for build quality may build a capability that is differentiating only to the team that built it; buying a commodity capability on the market at a fraction of the build cost liberates engineering time for the things that actually differentiate. Conversely, partnering for a capability that sits in a critical-path user flow means a competitor can match the capability overnight by signing the same partner. The right question is not "can we build this?" but "does owning this capability give us a durable competitive advantage over buying or partnering?"

## How to apply

Run a structured build-vs-buy-vs-partner evaluation for any capability decision above a defined complexity or strategic importance threshold.

```
Build / Buy / Partner Evaluation
──────────────────────────────────────────────────────
1. CAPABILITY DESCRIPTION
   What does it do, and where does it sit in the user flow?
   Is it visible to the user (experience layer) or invisible (infrastructure)?

2. STRATEGIC DIFFERENTIATION TEST
   Will owning this capability vs. buying/partnering it give us a durable
   competitive advantage? (Not just "it would be better" — would users choose
   us over a competitor specifically because of this capability?)
   If YES → bias toward Build (own it)
   If NO → bias toward Buy or Partner (commodity; don't waste engineering on it)

3. BUILD ASSESSMENT (if differentiation test = YES or Buy is unavailable)
   Internal estimate of build cost (person-months + infrastructure)
   Maintenance cost over 2 years
   Time-to-ship vs. competitive urgency

4. BUY ASSESSMENT (if differentiation test = NO)
   Available vendors that can cover the need
   Unit economics at current and 3× current volume
   Data portability and exit cost if vendor changes terms

5. PARTNER ASSESSMENT (if differentiation test = SHARED with a potential partner)
   What does the partner provide and what do we provide?
   Revenue / data / user-flow leverage that changes hands
   Exclusivity / non-compete risk

6. DECISION AND RATIONALE (written)
   Selected option + the specific reason the differentiation test was answered as it was.
```

**Do:**
- Default to buy or partner for capabilities that are not user-visible or that have a mature vendor market (payments, email delivery, maps, storage).
- Apply the differentiation test honestly: "we can build a better one" and "we should build one" are different questions.
- Revisit buy/partner decisions when the vendor changes pricing or terms materially — the economics that justified the original decision may no longer hold.

**Don't:**
- Let "engineers prefer to build it" substitute for a strategic differentiation test.
- Partner for a capability in the core user journey without an exit strategy if the partner pivots.
- Build commodity infrastructure capabilities when the engineering time has a measurable opportunity cost against differentiated features.

## Edge cases / when the rule does NOT apply

- **Security and privacy-critical capabilities** — even if "commodity," there may be regulatory or data-sovereignty reasons to own rather than share with a third party; the differentiation test must be supplemented by a risk/compliance assessment.
- **Very early stage, pre-PMF** — before product-market fit is found, the build-vs-buy-vs-partner framework is premature; bias toward the fastest path to learning, not the most strategically coherent infrastructure choice.

## See also

- [`../agents/product-strategist.md`](../agents/product-strategist.md) — owns the build-vs-buy-vs-partner decision framework and the competitive strategy layer.
- [`./roadmap-in-bets-with-confidence.md`](./roadmap-in-bets-with-confidence.md) — the build-vs-buy-vs-partner decision is a strategic bet; it belongs on the roadmap with explicit confidence and rationale.

## Provenance

Codifies the product-strategist's make-vs-buy discipline from the product-management plugin's CLAUDE.md §1 ("build-vs-buy-vs-partner") and §3 (seams to adjacent capabilities). The differentiation-test framing reflects Helge Tennø's capability strategy practice and standard competitive strategy literature (Porter, "What Is Strategy?").

---

_Last reviewed: 2026-06-05 by `claude`_
