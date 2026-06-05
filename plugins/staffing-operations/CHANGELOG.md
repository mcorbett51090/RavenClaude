# Changelog — staffing-operations

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.2.0] — 2026-06-05

Value-add build-out for a **pure non-code (healthcare + education staffing) vertical** — adds the scenarios bank, two new Mermaid decision-tree sections, and a runnable staffing-analytics calculator; honestly dispositions the code-runtime tier as N-A. Builds on PR #315 (which added the consolidated decision-trees file, best-practices set, and templates).

- **Scenarios bank** (`scenarios/`) — **4** dated, scope-tagged, unverified engagement scenarios authored to the pre-existing `scenarios/README.md` index (mirrors the marketplace 9-field schema, `product_version: "n/a"` for a non-code vertical):
  - `2026-06-05-fill-rate-up-time-to-fill-losing.md` — a "healthy fill rate" division losing on speed; pair fill with time-to-fill (§3 #2), localize the latency.
  - `2026-06-05-travel-margin-compression-in-the-burden-stack.md` — margin slide misread as a pricing problem; the leak was the housing/stipend burden line (§3 #3).
  - `2026-06-05-credentialing-clock-hidden-in-time-to-fill.md` — a fast accept hiding a slow time-to-start + accept→start fall-off; measure the whole clock (§3 #7).
  - `2026-06-05-iep-fill-gap-redeployment-and-teletherapy.md` — a calendar-quarter seasonality artifact stacked on a real IEP-mandate gap; cycle-align the fill (§3 #5), close the gap with teletherapy + redeployment (§3 #16).
  - Each carries an "Action for the next consultant" lesson and cited sources / knowledge-bank pointers; no candidate/client PII (§3 #10).
- **2 new Mermaid decision-tree sections** appended to `knowledge/staffing-decision-trees.md` (which already had 3 trees from PR #315):
  - **Fill Strategy by Requisition Type** — how to work an order (push-back-to-intake / redeploy / teletherapy / source + parallel credentialing / standard sourcing / raise pay), the per-req routing upstream of the capacity question. Per-leaf rationale + tradeoffs table.
  - **Placement Model — Contract vs. Contract-to-Hire vs. Direct** — the commercial-model choice by demand shape and margin/cash profile (markup spread vs. conversion fee vs. perm fee), with the bench/redeployment guard. Per-leaf rationale + tradeoffs table.
- **Runnable calculator** `scripts/staffing_calc.py` (stdlib only, Python 3.8+, ruff-clean) — three modes: `margin` (bill − pay − burden decomposition naming the spread-driving burden line, §3 #3), `fill-rate` (received-vs-workable denominator comparison exposing a dead-order pileup, §3 #1/#6), `funnel-leak` (worst-converting stage across the recruiting funnel incl. accept→start credentialing, §3 #7). Decision-support, not advice (§2); no PII in or out (§3 #10). **Complements** the existing static `bi-report/` scorecard (which *displays* these numbers) by *computing* the decomposition parametrically — the parametric-calculator gap was genuinely net-new.

### Honestly N-A for a non-code vertical (documented, not forced)
The code-runtime tier (code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, `settings.json`) is genuinely not applicable to a staffing-operations advisory vertical. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". ATS/VMS systems are per-tenant / authenticated / PII-&-PHI-bearing, so a bundled MCP is out of scope and the plugin stays ATS/VMS-neutral (§2). The one runtime item with real non-code value — a runnable calculator — **was** built.

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**` and `plugins/*/scripts/**` (both present; no new glob needed — confirmed).
- `.claude-plugin/marketplace.json` `version` bump `0.1.2` → `0.2.0` to mirror `plugin.json` (CI fails on drift).

## [0.1.0] — initial release

6 agents (`staffing-engagement-lead`, `staffing-operations-analyst`, `recruiting-funnel-strategist`, `healthcare-staffing-specialist`, `education-staffing-specialist`, `workforce-market-analyst`), 10 skills, 10 templates, 5 commands, 1 advisory hook, a 7-rule best-practices set, and an 8-file research-grounded knowledge bank. A consulting kit for a healthcare + education staffing engagement (Soliant Health shape).
