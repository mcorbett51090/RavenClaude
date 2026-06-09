# Changelog — ai-coding-model-guidance

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.1] — 2026-06-09

Freshness-anchor refresh — **Claude Opus 4.8 is now GA in GitHub Copilot** ([Changelog 2026-05-28](https://github.blog/changelog/2026-05-28-claude-opus-4-8-is-generally-available-for-github-copilot/); retrieved 2026-06-09).

### Changed

- **`knowledge/cross-tool-model-lineup-2026.md`** — added **Opus 4.8 (GA 2026-05-28)** to the Copilot coding-agent + mobile-picker rows; added a Copilot bullet (Pro+/Business/Enterprise; selectable in VS Code all modes + Visual Studio/JetBrains/Xcode/Eclipse/Copilot CLI/GitHub Mobile/Copilot App; launched at a 15× premium-request multiplier that closed when Usage-Based Billing went live 2026-06-01 — re-confirm the current multiplier); re-dated the Copilot row to 2026-06-09 and added the GitHub Changelog citation. Codex/Grok rows unchanged (still within their 2026-05-31 retrieval window). All additions carry a date/citation/`[verify-at-use]` per the `check-lineup-citations.py` gate.



Value-add build-out — completes the scenarios bank, adds two right-sizing-focused Mermaid decision-tree knowledge files (complementing the PR #315 trees), and ships the plugin's first runnable helper: a cost-per-resolved-task calculator with **no baked-in prices**. Honestly dispositions the runtime/MCP/LSP tier as N-A for an advisory knowledge vertical. Every model fact added carries a citation, an ISO retrieval date, or a `[verify-at-use]` marker — and the two new knowledge files pass the `check-lineup-citations.py` gate.

- **Scenarios bank completed** (`scenarios/`) — the README indexed four scenarios but only one file existed; added the three missing dated, scope-tagged engagement scenarios (mirrors the marketplace 9-field schema, `product_version: "n/a"` for an advisory vertical):
  - `2026-06-05-codex-reasoning-level-before-model-upgrade.md` — raise the Codex reasoning dial before a model upgrade for a latency-tolerant hard bug; surfaces the verified-this-date nuance that **on Codex cost is set by the model, not the reasoning level** (higher reasoning costs latency, not dollars).
  - `2026-06-05-grok-code-fast-1-retirement-silent-rebill.md` — the retired `grok-code-fast-1` slug still resolves and silently redirects to Grok 4.3 pricing; the canonical retirement-with-billing-consequence catch.
  - `2026-06-05-hallucinated-model-closed-world-catch.md` — refusing to extrapolate `GPT-5.6` / `Grok 4.5` from version-number cadence; the closed-world rule in action (not in lineup → offer to verify live → re-anchor on a real SKU).
- **2 new Mermaid decision-tree knowledge files** (complement, do not duplicate, the PR #315 trees in `ai-coding-decision-trees.md`):
  - `ai-coding-right-size-cost-decision-tree.md` — the **cost-per-resolved-task** right-sizing tree (the money question the agents asserted but never operationalized), with a tier-relative tradeoff table. Opted into the citation gate.
  - `ai-coding-mode-selection-decision-tree.md` — **interaction-mode** selection (inline completion vs. chat/edit vs. autonomous agent) one step *before* the model question, with a per-vendor surface mapping. Opted into the citation gate.
- **First runnable helper** `scripts/right_size_cost.py` (stdlib only, Python 3.8+, `ruff`-clean) — two modes: `per-task` (rank candidate tiers by cost-per-resolved-task = cost-per-call ÷ resolution-rate) and `mix` (single-pin vs. right-sized-per-shape spend, the "I pinned the top model for everything" anti-pattern made numeric). **No vendor prices are baked in** — every number is user-supplied; the tool does the arithmetic and points back to the dated lineup for figures.

### Honestly N-A for an advisory knowledge vertical (documented, not forced)
Bundled code-aware MCP server, LSP, `bin/`, monitors, output-styles, themes, and `settings.json` tuning are genuinely not applicable to a non-Claude model-selection *advisory* plugin — there is no consumer codebase, runtime, or live model API this plugin operates on. Each is dispositioned with a one-line reason in `CLAUDE.md` § "Value-add completeness (build-out 2026-06-05)". The one runtime item with real advisory value — a calculator — **was** built (`scripts/right_size_cost.py`).

### Shared-file changes required (orchestrator-owned, NOT done here)
- `.repo-layout.json` `allowed_globs` already covers `plugins/*/scenarios/**`, `plugins/*/knowledge/**`, and `plugins/*/scripts/**` — confirmed, no edit needed.
- `.claude-plugin/marketplace.json` `version` must be bumped `0.2.2` → `0.3.0` to match `plugin.json` (CI fails on drift). Not edited here per the build-out's no-marketplace.json-edit constraint — flagged for the orchestrator.

## [0.2.x] — prior releases
3 strategist agents (`copilot-model-strategist`, `codex-model-strategist`, `grok-model-strategist`), 8 skills, 4 templates, a 24-rule best-practices set, and a citation-grounded, dated cross-tool model-lineup knowledge bank with consolidated decision trees (PR #315) — guidance for model selection across GitHub Copilot, OpenAI Codex, and xAI Grok over a single freshness-anchored source of truth.
