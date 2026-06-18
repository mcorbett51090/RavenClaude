# Knowledge — DevRel tooling (2026, tiered, with retrieval dates)

> **Last reviewed:** 2026-06-18 · **Confidence:** Medium — tooling, pricing, and feature sets are
> **volatile**. Every category below is a *capability* recommendation; the named products are
> illustrative examples as of the review date, **not** an endorsement and **not** a current-price
> claim. Re-verify the specific product, tier, and price at use (claim-grounding discipline).

The agents recommend the **capability** first and a product second, defaulting to the lowest-coupling
tool that does the job. Don't over-tool a small program.

---

## How to read this

- **Tier 1** = reach for this first; broadly used, low lock-in, covers most needs.
- **Tier 2** = reach with a reason; more specialized or higher-commitment.
- Anything with a number (reach, price, limits) is **`[verify-at-use]`** — the agent fetches live
  before quoting it to a client.

---

## By category

| Need | Tier 1 (default) | Tier 2 (with a reason) | Notes |
|---|---|---|---|
| **Funnel / product analytics** (instrument TTFS, activation) | Your existing product-analytics stack (PostHog / Amplitude / a warehouse + dbt) | A dedicated DevRel analytics layer | Don't buy a second analytics tool before instrumenting the one you have. Seam: `data-platform` / `analytics-engineering`. |
| **Docs / golden-path hosting** | Owned by `technical-writing-docs` (Docusaurus / Mintlify / MkDocs) | — | This plugin does not pick the docs system; it audits the path *in* it. |
| **Sample/demo hosting** | GitHub repo + a deployable preview | An interactive sandbox (StackBlitz / CodeSandbox / Replit embeds) | A runnable repo beats a fancy sandbox that drifts. Maintenance owner required. |
| **Community** | Sponsor an existing channel (Stack Overflow tag, subreddit, an established Discord) | Owned Discord / Discourse forum | Only own one you can staff (Tree 2). Health = response time + resolution. |
| **CFP / talk tracking** | A shared sheet + the conference's own CFP portal (Sessionize is common) | A dedicated speaker-CRM | A spreadsheet covers most teams; don't buy a tool for 6 talks a year. |
| **Content calendar** | The template in this plugin + your existing planning tool | A marketing content platform | Seam: `marketing-operations` owns the broader content ops. |
| **Developer newsletter** | Your existing ESP | A developer-newsletter-specific platform | Seam: deliverability/auth is the future `email-engineering-deliverability` plugin's domain. |

---

## House guidance

- **Instrument before you buy.** Most "we need a DevRel tool" requests are "we never instrumented
  time-to-first-success." Fix the measurement gap before adding a vendor.
- **Lowest coupling that works.** A repo + a sheet beats a platform you'll abandon. Match tool weight
  to program size.
- **The docs system is not this plugin's choice** — that's `technical-writing-docs`. Avoid
  recommending a second docs tool.
- **Every reach/price/limit number carries a retrieval date** and is re-verified before it reaches a
  client deliverable.

---

## Provenance

Capability tiers reflect developer-relations CLAUDE.md §3 house opinion #10 (volatile claims carry
retrieval dates) and the marketplace's bundled-MCP/lowest-coupling default
([`../../../docs/best-practices/bundled-mcp-servers.md`](../../../docs/best-practices/bundled-mcp-servers.md)).
Product names are illustrative as of 2026-06-18; none is bundled or endorsed, and no current price is
asserted here.

---

_Last reviewed: 2026-06-18 by `claude`_
