# Research routine — two-cadence redesign (2026-06-11)

**Status:** active · **Supersedes:** the implicit "research news for *each* active plugin every week" framing.

## The problem this fixes

The research routine was framed as "research recent news/updates for **each** active plugin." That framing is mismatched to the marketplace's actual shape, and a 2026-06-11 broad sweep proved it:

- The marketplace has ~100 plugins. Only ~25 are **anchored to a fast-moving third-party product/API** whose dated facts (a price, a GA/preview status, a version, a model SKU, an API shape) go stale **weekly-to-monthly**. For those, a weekly news sweep is exactly right — the same sweep that caught the Fabric "Spark 4.0 → 4.1" error, OneLake "preview → GA", OpenTofu "1.8 → 1.12", and the M365 Federated-Connectors stale `[verify-at-build]` marker.
- The other ~75 are **domain-craft verticals** (dental-practice, freight-forwarding, hospice-referral-sales, …) whose value is durable methodology / regulation that changes **slowly and episodically**. Running a "weekly news" pass over them mostly produces noise — or, worse, **fabrication pressure**: an agent asked to "find this week's news for veterinary-practice" will tend to manufacture a finding rather than honestly return "nothing changed." That is the exact failure mode the marketplace's accuracy discipline exists to prevent.

A routine that implies weekly coverage it cannot honestly deliver is a routine that erodes trust in its own output. The fix is to make the cadence **honest by construction**.

## The two cadences

| | **Tier A — news cadence** | **Tier B — methodology cadence** |
|---|---|---|
| **Who** | ~25 vendor-API-anchored plugins (AI/Claude tooling, Microsoft stack, cloud/infra, data/BI, security) | ~75 domain-craft verticals + regulatory verticals |
| **Trigger** | The **weekly** `researcher-reminder.yml` deep sweep | A **quarterly** methodology review; **event-driven** for `regulatory_watch` plugins when a relevant rule/standard ships |
| **What it looks for** | Stale dated facts: versions, GA/preview flips, price/SKU changes, API shape, deprecations | Drift in durable craft: superseded best practice, a new regulation, a structural methodology gap |
| **Honest null result** | Common and expected — most Tier-A plugins have **0 net-new** in any given week; report it, don't pad | The default — methodology rarely changes week-to-week |

The membership manifest is [`.ravenclaude/plugins/sweep-tiers.yaml`](../.ravenclaude/plugins/sweep-tiers.yaml). **Rule of record:** a plugin is Tier A **iff** it appears in that file's `tier_a_news` list; every other plugin in `plugins/` defaults to Tier B. A newly-added vertical therefore lands in the methodology cadence automatically — it must be *explicitly promoted* to earn weekly news attention.

## How a weekly news-sweep run should behave

1. **Scope to Tier A.** Read `tier_a_news` from the manifest. Do **not** sweep Tier-B plugins for "news."
2. **Per Tier-A plugin:** read its knowledge files' `Last reviewed:` stamps; for each dated/volatile claim, re-verify against the **primary** source (vendor docs, Microsoft-Learn MCP for MS, GitHub releases, the Claude/Codex/Grok primaries). A `WebFetch` 403 is a re-route signal — `WebSearch` the page, then the domain MCP, then a non-blocked host (the webfetch-hardening route ladder).
3. **Triage, don't dump.** Classify each finding as a **correction** (the repo currently states something now-false — highest priority, actively misleads) or an **addition** (a new capability not yet documented). Ship corrections first; queue additions.
4. **Verify before writing.** Anything written into a claim-grounded knowledge file must be re-verified by the editor against a primary source, carry an ISO date + citation + `[verify-at-use]` marker, and pass the relevant gate (`check-lineup-citations.py`, etc.).
5. **Honest null is a result.** "0 net-new for plugin X this week" is logged, not padded.
6. **Tribunal gate before the PR is final** (added 2026-09-11). Once the gate suite is green, run the diff through the [`routine-review-tribunal`](../plugins/ravenclaude-core/skills/routine-review-tribunal/SKILL.md) skill — the same two-panel, cross-model review `/forge-pipeline` gives a plan before code exists, applied here to the knowledge-file diff this routine just produced. `approved` → open the PR; `needs_revision` → apply the tribunal's required edits and resubmit (bounded to 2 rounds); `escalate` → open a flagged draft PR and notify rather than merging unreviewed corrections into a claim-grounded knowledge file. This is the routine's second opinion in place of the human reviewer it doesn't have, running unattended.

## The feedback loop (keeps the tiering honest)

The manifest's `review_candidates` list holds borderline plugins. Each sweep should note:

- A **Tier-B** plugin that keeps surfacing real weekly deltas → **promote** to `tier_a_news`.
- A **Tier-A** plugin that never does → **demote** to Tier B (stop paying weekly attention that buys no freshness).

This is why the tiering is a manifest, not hard-coded: it is meant to drift with evidence, re-reviewed on the same cadence it governs.

## Relationship to existing machinery

- [`.github/workflows/researcher-reminder.yml`](../.github/workflows/researcher-reminder.yml) — the weekly-deep issue now scopes itself to Tier A via the manifest, and the monthly skill-gap audit remains the structural-gap pass.
- [`knowledge-file-staleness-sweep`](../plugins/ravenclaude-core/skills/knowledge-file-staleness-sweep/SKILL.md) — the staleness-tier concept (Tier-4 fast-churn) is the per-file complement to this per-plugin cadence; the two agree (a Tier-4 file lives in a Tier-A plugin).
- The PR/no-PR boundary is unchanged (AGENTS.md): knowledge-file edits ship via PR + version bump; this spec doc is docs-only.
- [`routine-review-tribunal`](../plugins/ravenclaude-core/skills/routine-review-tribunal/SKILL.md) — the tribunal gate this routine now runs before a correction/addition PR is opened (§ "How a weekly news-sweep run should behave," step 6). Shared with the plugin-discovery routine's own gate ([`docs/plugin-discovery-routine-policy.md`](plugin-discovery-routine-policy.md) § "Tribunal gate") so both PR-producing scheduled routines use the same reviewed-and-approved (or revised-and-reapproved) mechanism.

## Learn-tab improvement output (added 2026-06-12)

The Tier A sweep for `web-design` and `frontend-engineering` has a **third output** beyond corrections and additions to plugin knowledge files: a **Learn-tab improvement pass** that checks whether new documentation, web-design, or interactivity best practices warrant a new concept card in `plugins/ravenclaude-core/knowledge/concepts/` (the source for the portal's Learn section). Full protocol in [`plugins/ravenclaude-core/skills/researcher/SKILL.md`](../plugins/ravenclaude-core/skills/researcher/SKILL.md) § "Learn-tab improvement pass." The honest null result applies here too: "0 net-new concept candidates this week" is a valid output.
