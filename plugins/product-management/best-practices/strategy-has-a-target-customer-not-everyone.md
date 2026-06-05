# A Product Strategy Names Its Target Customer — Not "Everyone"

**Status:** Absolute rule
**Domain:** Product strategy
**Applies to:** `product-management`

---

## Why this exists

A product strategy that targets "everyone" actually targets no one. "Everyone" produces requirements that are simultaneously too broad to design against and too shallow to delight any specific segment. The classic result is a product that is average for everyone and exceptional for no one, priced and positioned to compete with products designed for focused audiences that out-execute on the specific job the customer actually needs done. A named, specific target customer — a segment with a describable characteristic, situation, and job to be done — is the constraint that makes every subsequent product decision tractable. Without it, the roadmap is a political negotiation between stakeholders, not a strategy.

## How to apply

Every product strategy document must name its target customer in a form that is specific enough to test and specific enough to say no.

```
Target Customer — Minimum Specification (strategy doc)
──────────────────────────────────────────────────────
1. WHO THEY ARE (describable, not demographic)
   Role, situation, or context: e.g., "a solo financial advisor managing < 50 clients
   who builds their own reporting in spreadsheets"
   NOT: "financial professionals"

2. WHAT JOB THEY'RE HIRING THE PRODUCT TO DO
   The core JTBD in their language:
   e.g., "to look credible and informed to clients without hiring a junior analyst"
   NOT: "to improve productivity"

3. WHAT MAKES THEM UNDERSERVED
   Why existing solutions don't fully serve them:
   e.g., "enterprise tools are too expensive and require IT; spreadsheets are too
   manual and error-prone at their scale"

4. EXPLICIT NON-TARGETS (equally important)
   Name at least one adjacent customer the strategy explicitly does not serve
   in this cycle: e.g., "not a 500-person RIA firm with dedicated operations staff"
   The non-target is the decision the strategy makes; the target is only
   meaningful if the non-target is also named.
```

**Do:**
- Test the target customer definition against the question: "If two product managers read this, would they make the same feature decision?" If the answer is no, the definition is too vague.
- Update the target customer when the market moves, the competitive set changes, or data shows the actual user is different from the intended one.
- Communicate the non-targets explicitly to the sales, marketing, and CS teams — they are the ones who will be asked to serve non-target customers, and they need the strategic rationale.

**Don't:**
- Define the target customer by demographics alone (age range, company size) without the job-to-be-done; two people in the same demographic may have entirely different jobs.
- Expand the target to avoid saying no to an internal stakeholder; a wider target is a weaker strategy, not a more inclusive one.
- Confuse "we can serve this customer" with "we have chosen to prioritize this customer" — capability and strategy are different.

## Edge cases / when the rule does NOT apply

- **Platform products** (e.g., an API, a marketplace, a data infrastructure layer) — the target customer is a developer or a set of ecosystem participants; the JTBD framing still applies, but the "everyone as end customer" argument has more legitimacy for platforms designed to be open. Even platforms benefit from naming a primary use case they optimize for.
- **Early pre-product-market-fit stage** — it is legitimate to hold the target customer loosely while signals from early users identify who the product is actually for; document it as "working hypothesis: target is X" and treat it as an assumption to validate.

## See also

- [`../agents/product-strategist.md`](../agents/product-strategist.md) — owns the product strategy and the positioning stack.
- [`./roadmap-in-bets-with-confidence.md`](./roadmap-in-bets-with-confidence.md) — the target customer is the frame within which the roadmap bets are evaluated; a bet that doesn't serve the target customer is a bet outside the strategy.

## Provenance

Codifies the product-strategist's positioning and strategy discipline from the product-management plugin's CLAUDE.md §1 ("what's our product strategy?", "how should we position this?") and §2 #1 (fall in love with the problem, not the solution). The target customer / non-target specification pattern reflects April Dunford's positioning framework and standard STP (segmentation / targeting / positioning) strategy practice.

---

_Last reviewed: 2026-06-05 by `claude`_
