# Changelog — ecommerce-dtc

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.1] — 2026-06-12

Version bump previously unlogged here; the change that set `0.2.1`:

- fix: repo-review fixes — gate tool-absence guard + broken antipattern regex (#422)

## [0.2.0] — 2026-06-05

Value-add build-out — completes the scenarios bank the README already indexed, adds two Mermaid decision-tree knowledge files and a runnable unit-economics calculator, and honestly dispositions the code-runtime + bundled-MCP tiers.

- **Scenarios bank** (`scenarios/`) — the README/index pre-existed (PR #315) but its **4** indexed scenario files did not; created to match the index exactly (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical):
  - `2026-06-05-cac-rising-blended-vs-incremental.md` — read CAC by channel + cohort and MER (not last-click) before reallocating; holdout before a cut.
  - `2026-06-05-contribution-margin-negative-after-returns.md` — a high-conversion apparel category that loses money once returns load in; fix the return driver at the PDP.
  - `2026-06-05-checkout-conversion-drop.md` — a falling headline conversion rate diagnosed to a mobile checkout regression, not bad traffic.
  - `2026-06-05-subscription-churn-vs-acquisition.md` — fix churn (voluntary vs. involuntary; dunning; value-layer-past-discount) before scaling acquisition on a subscription.
  - Each carries an "Action for the next consultant" lesson and cited, dated 2025–2026 public benchmarks.
- **2 new Mermaid decision-tree knowledge files** (complementing PR #315's three in-file trees — CAC root-cause, subscription, new-channel):
  - `ecommerce-channel-mix-reallocation-decision-tree.md` — MER-gated reallocation (breakeven MER = 1 ÷ contribution-margin%), re-read on blended/cohort, holdout before a major shift. Northbeam/Eightx/AdLibrary-cited.
  - `ecommerce-platform-vs-headless-decision-tree.md` — themed Shopify vs. headless/build as a capability-need + capacity + 3-year-payback trade (default: stay on a theme). Ask Phill/Conversion-Design/Shopify-cited.
- **Runnable calculator** `scripts/dtc_calc.py` (stdlib only, Python 3.8+, `ruff`-clean) — three modes: `contribution-margin` (per-order margin net of returns + negative/thin flags), `ltv-cac` (master ratio + payback-in-orders + optional churn→lifetime, vs the 3:1 / 2:1 lines), `breakeven-roas` (MER floor = 1 ÷ contribution-margin% + per-order CAC headroom). Decision-support, not advice.

### Honestly N-A / recommend-not-bundle (documented, not forced)
- **Bundled MCP** — Shopify's official commerce MCP is per-tenant/OAuth/PII-bearing → *recommend, don't bundle* (`docs/best-practices/bundled-mcp-servers.md`). The read-only Shopify dev-docs MCP could bundle if a stable zero-auth artifact were confirmed, but that was **not verified this session** — so per the no-invent rule it is `[unverified]` and **not bundled**; no `x-mcpAttribution` / `NOTICE.md` shipped.
- The code-runtime tier (LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely N-A for a growth/ops advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` §9.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/scripts/**`, `plugins/*/knowledge/**`, and `plugins/*/CHANGELOG.md` — **no new globs needed**.
- `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` (mirror of `plugin.json`).

## [0.1.0] — initial release

4 agents (`ecommerce-lead`, `merchandising-specialist`, `performance-marketing-strategist`, `retention-analytics-analyst`), 5 skills, 3 templates, 5 commands, 1 advisory hook, an 8-rule best-practices set, and a 4-file research-grounded knowledge bank. A growth-and-unit-economics team for a DTC brand operator.
