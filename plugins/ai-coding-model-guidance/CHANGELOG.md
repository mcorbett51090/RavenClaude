# Changelog — ai-coding-model-guidance

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.9] — 2026-07-01

Research-sweep **correction** (Tier-A weekly news sweep) — **Fable 5 / Mythos 5 export controls LIFTED 2026-06-30; access restoring from 2026-07-01** (the fan-out sibling of `claude-app-engineering` 0.9.6). `knowledge/cross-tool-model-lineup-2026.md` carried the suspension as current status; updated the live assertions (header `Last reviewed`, the coding-agent table row, the Fable 5 Copilot bullet, the free-window parenthetical) to "controls lifted / access restoring — confirm Fable 5 is selectable on your Copilot tenant before relying on it; interim, Opus 4.8 stays the top Copilot Claude option," and added a **2026-07-01 sweep note** that supersedes the older dated "remains suspended" notes (kept as the historical record). Restored access bills usage credits (free promo ended 2026-06-22). `[verify-at-use — restoration in progress]`. Panels: usefulness → USEFUL; detailed review → APPROVE. **Migration:** none — knowledge-file content only.

## [0.3.8] — 2026-06-23

Version bump previously unlogged here; the change that set `0.3.8`:

- chore(ai-coding,claude-app): 2026-06-23 lineup freshness sweep — Fable 5 free window elapsed + suspension re-verified

## [0.3.7] — 2026-06-21

Research-sweep refresh (re-dated 2026-06-21) — two non-Claude churns folded into `knowledge/cross-tool-model-lineup-2026.md` on top of the 2026-06-17 Grok Build addition and the 2026-06-13 Fable 5 suspension (both unchanged): (1) **OpenAI GPT-5.3-Codex and GPT-5.2/5.2-Codex deprecated** — new API requests end 2026-06-30, full shutdown 2026-12-31; flagged in the Codex table like the `grok-code-fast-1` retirement, GPT-5.5 the migration target; decision-tree leaf updated. (2) **MAI-Code-1-Flash** (Microsoft small coding model) broadly available across Copilot surfaces 2026-06-18 — added to the cheapest-fast tier. Routed through two expert panels (usefulness → both USEFUL; detailed review → APPROVE with refinements applied); panels concurred. No migration — knowledge-file content only.

## [0.3.6] — 2026-06-17

Freshness-anchor refresh — **xAI Grok Build CLI + `grok-build-0.1` verified and added**. The prior review's Grok Build line was a flagged `[unverified — confirm at docs.x.ai]` placeholder; this sweep verified it across the xAI primary ([x.ai/news/grok-build-cli](https://x.ai/news/grok-build-cli), [x.ai/cli](https://x.ai/cli)) plus 10 secondaries (incl. OpenRouter / Vercel AI Gateway / Requesty, which list `grok-build-0.1` as a deployable model). The vendor doc pages 403 automated `WebFetch`, so values were read via `WebSearch` per the file's 403 route ladder. (Originally cut as 0.3.5; renumbered to 0.3.6 on merge after the 2026-06-13 Fable 5 suspension sweep independently took 0.3.5 on main.)

### Changed

- **`knowledge/cross-tool-model-lineup-2026.md`** — (1) added a **`grok-build-0.1`** row to the Grok table as a **distinct coding-agent SKU** (256K context · $1 in / $2 out · cached $0.20; text+image, tool-calling, structured output, **always-on/non-dialable reasoning**), framed explicitly as sub-flagship-by-design (cheaper + smaller window than Grok 4.3) so the row doesn't read as a transcription error, and noting house opinion #6's reasoning-dial lever does not apply to an always-on model; the row carries retrieval date **2026-06-17** + `[verify-at-use]` on the row itself (satisfies `check-lineup-citations.py`). (2) Replaced the `[unverified]` **Grok Build CLI** bullet with a verified, dated, cited description (beta launched 2026-05-14, expanded 2026-05-25; up to **8 parallel sub-agents in isolated Git worktrees**, native MCP, plan mode, **ACP** support) — `[verify-at-use — beta]` preserved. (3) Updated the AGENT decision-tree leaf to map the coding-agent tier to grok-build-0.1 (with a 1M+-context caveat to the flagship). (4) Re-dated `Last reviewed` → **2026-06-17** (preserving the 2026-06-13 Fable 5 suspension reference from 0.3.5), added the Grok Build sources to the header, and added a 2026-06-17 sweep note.
- Version **0.3.5 → 0.3.6** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift).

## [0.3.5] — 2026-06-13

Research-sweep **correction** (Tier-A weekly news sweep; freshness anchor) — **Claude Fable 5 was suspended on 2026-06-12** across the Anthropic API, AWS Bedrock, and all GitHub Copilot surfaces under a US export-control directive (disputed; Anthropic working to restore). This **supersedes the 2026-06-09 Copilot GA** recorded in this file. Verified this session against the primary [Anthropic statement](https://www.anthropic.com/news/fable-mythos-access) (corroborated by Bloomberg + CNBC). Routed through three expert panels (usefulness → USEFUL/unanimous; detailed review → APPROVE-WITH-FIX, fixes applied).

### Fixed

- **`knowledge/cross-tool-model-lineup-2026.md`** — annotated the Copilot coding-agent table row and the Fable 5 bullet as **SUSPENDED 2026-06-12** (was listed GA + selectable); noted the "free through 2026-06-22" inclusion window is suspended-with-access (expiry date unchanged, resumes only if access returns); re-route to **Opus 4.8** as the top Copilot Claude option until restored; added a 2026-06-13 sweep note. Other Claude models in Copilot (Opus 4.8, Sonnet 4.6, Haiku 4.5) unaffected. Framed as fluid/disputed (`[verify-at-use]`), not a deprecation.
- Version **0.3.4 → 0.3.5** in `.claude-plugin/plugin.json` **and** `marketplace.json` (lockstep).

## [0.3.4] — 2026-06-11

Research-sweep re-verify — re-checked the **Microsoft Foundry Fable 5** sub-claim against the authoritative `learn.microsoft.com` Foundry Claude-model table via the **Microsoft-Learn MCP**. Despite the Azure blog and the `ai.azure.com/catalog/models/claude-fable-5` catalog page announcing GA, the Learn **deployable-model table still does not list `claude-fable-5`** (it lists Opus 4-8/4-7/4-6/4-5/4-1, Sonnet 4-6/4-5, Haiku 4-5 previews + the gated `claude-mythos-preview`).

### Changed

- **`knowledge/cross-tool-model-lineup-2026.md`** — **sharpened** the Foundry Fable 5 caveat in the Copilot bullet: the prior wording ("the Foundry Learn model table still lists only the gated `claude-mythos-preview`") was imprecise (the Opus/Sonnet/Haiku families are listed too); restated as "the Learn table lists Opus/Sonnet/Haiku previews + gated `claude-mythos-preview` but does **not** list `claude-fable-5`," with the authoritative Learn URL and a **2026-06-11 re-verify note** added beside the existing sweep note. Caveat **sharpened, not struck** — a vendor blog/catalog announcement is not a deployable-model-table listing.
- Version **0.3.3 → 0.3.4** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift).

## [0.3.3] — 2026-06-10

Freshness-anchor follow-up — codified the **403 route ladder** in the lineup's "How to keep this current" (the header already noted the vendor doc pages 403 automated fetch; this says what to *do* about it).

### Changed

- **`knowledge/cross-tool-model-lineup-2026.md`** — added a 403 route-ladder sweep note pointing at [`webfetch-hardening`](../ravenclaude-core/skills/webfetch-hardening/SKILL.md): on a 403, `WebSearch` the page (it reads the bot-blocked content the agent's `WebFetch` can't — how the Copilot/Anthropic primaries were read this sweep) → domain MCP → non-blocked host → secondaries last; Wayback + UA-spoofing unavailable.
- **Softened the Fable 5 Microsoft Foundry claim** in the Copilot bullet: Foundry **announced** (Azure blog), but the Foundry Learn model table still lists only the gated `claude-mythos-preview` as of 2026-06-10 — re-verify.
- Version **0.3.2 → 0.3.3** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep.

## [0.3.2] — 2026-06-10

Freshness-anchor refresh — **Claude Fable 5 is GA in GitHub Copilot** ([Changelog 2026-06-09](https://github.blog/changelog/2026-06-09-claude-fable-5-is-generally-available-for-github-copilot/); retrieved 2026-06-10). Anthropic's first public **Mythos-class** model; the Copilot changelog 403s automated fetch, so facts are cross-referenced across the GitHub/Microsoft posts + dev guides (the doc's accepted "primary 403 → cross-reference" pattern).

### Changed

- **`knowledge/cross-tool-model-lineup-2026.md`** — added **Fable 5 (GA 2026-06-09)** to the Copilot coding-agent verified row (also satisfying the closed-world rule so agents may name it) and a Copilot bullet: plans **Pro+/Max/Business/Enterprise**; surfaces VS Code/Visual Studio/JetBrains/Xcode/Eclipse/Copilot CLI/cloud agent/github.com/mobile; **included free through 2026-06-22** then usage-credit (written as an expiring dated caveat); **Business/Enterprise admins must enable the Fable 5 policy, off by default**; also on AWS Bedrock + Microsoft Foundry; API `claude-fable-5` at **$10/$50 per Mtok (2× Opus 4.8)**. Vendor-framing/single-source claims carry `[verify-at-use — single-source]`. Re-dated `Last reviewed` 2026-06-09 → 2026-06-10 and added a sweep note that Fable 5 was a **same-day-of-last-review miss**. All additions carry a date/citation/`[verify-at-use]` per the `check-lineup-citations.py` gate.
- Version **0.3.1 → 0.3.2** bumped in `.claude-plugin/plugin.json` **and** the `marketplace.json` catalog entry in lockstep (CI fails on drift).

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
