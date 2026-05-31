# Strategic plan — AI-coding model-guidance plugin

> **Status:** v2 — gap-filled after two-panel review; **built**. Authored 2026-05-31 on branch `claude/resumed-session-recovery-OXFkX`.
> Recovered from a stopped session that died at the decision-fork point (no files had been written).

## v2 changes after the gap-analysis panel (what the review changed)

A four-lens panel (architect / security / ops / devil's-advocate) gap-analyzed the v1 plan. Material outcomes, confirmed with Matt:

- **Collapsed three plugins → ONE plugin (`ai-coding-model-guidance`) with three agents** (`copilot-/codex-/grok-model-strategist`). Copilot/Codex/Grok are three vendors but one domain; the house shape is cohesive agents inside one plugin. Resolves the single-source-of-truth, drift, and catalog-bloat P0s. (Matt chose "one plugin, three agents".)
- **One shared knowledge bank** (`knowledge/cross-tool-model-lineup-2026.md`) is the single source of truth — one file refreshes, not three.
- **Volatile-fact discipline strengthened**: verify-now + freshness. Kept model names/tiers; prices/context windows carry retrieval date + verify-at-use rider + a closed-world anti-hallucination rule. (Matt chose "verify-now + freshness discipline".)
- **Wired into existing machinery**: uses the repo's `Last reviewed:`/`Owner:` header convention, tagged Tier-4 for the `knowledge-file-staleness-sweep`, in scope for the weekly `researcher-reminder.yml` sweep.
- **Seams to prior art**: `claude-app-engineering/claude-solution-architect` owns Claude models; this plugin explicitly does not (resolves the "duplicates existing model-selection content" P0).
- Added `requires: ravenclaude-core@>=0.7.0` and a `## Decision Tree` in the knowledge bank (P1 fixes).
- **Primary-source verification corrected two reconstructed facts**: `grok-code-fast-1` was retired 2026-05-15 (redirects to Grok 4.3 pricing); "Gemini removed from Copilot" was a web-chat-surface-only changelog, not a picker-wide removal.

**Deferred (noted, not built this PR):** a `check-lineup-citations.py` CI gate (panel P0 ci-1) to mechanically enforce that every lineup number carries an inline citation — recommended as a follow-up; the discipline is currently enforced in-content + by agent prompts.

---

## (v1 plan below — retained for provenance)

## Purpose

Build **three new Claude Code marketplace plugins** under `plugins/`, one per non-Claude AI-coding ecosystem, each teaching "how the models work" and how to pick the right model for a task — grounded in citations, with a dated lineup that ages gracefully.

This fills a real gap in the marketplace: there is guidance for Claude-native work (`claude-app-engineering`) and Microsoft surfaces, but nothing that helps a developer reason about model selection in **GitHub Copilot, OpenAI Codex, or xAI Grok** — the three ecosystems a polyglot team actually toggles between.

## The three plugins

| Plugin | Agent (frontmatter-gated) | Knowledge bank (verified, dated) |
|---|---|---|
| `github-copilot` | `copilot-model-picker` — picking models across Copilot surfaces (completions / chat / coding agent / cloud agent), org model rules | `knowledge/copilot-model-lineup.md` |
| `openai-codex` | `codex-model-strategist` — Codex CLI model selection (GPT-5.5 / 5.4 / 5.4-mini / 5.3-Codex(-Spark) / 5.2-Codex), reasoning levels, `/model` | `knowledge/codex-model-lineup.md` |
| `xai-grok` | `grok-model-strategist` — Grok model selection (Grok 4 / 4.3 / `grok-code-fast-1`) + the new **Grok Build** CLI | `knowledge/grok-model-lineup.md` |

**One strong agent per plugin** (not three each) — deliberate scope choice to land all three this session, fully verified. Existing plugins use three agents each; this trades roster breadth for landability and re-verifiability.

## Verified current facts (as of 2026-05-31, via web search; to be re-pinned by WebFetch of authoritative docs at build time)

- **GitHub Copilot picker**: OpenAI + Claude models available (Gemini removed from Copilot Chat on web). Coding agents → Claude Sonnet/Opus 4.6/4.5 & Codex GPT-5.2/5.3-Codex + GPT-5.4; cloud-agent fast tier → Claude Haiku 4.5 / GPT-5.4-mini; org **model rules** target models to orgs. *(docs.github.com/en/copilot/reference/ai-models/supported-models + github.blog changelog 2026-05)*
- **OpenAI Codex CLI**: GPT-5.5 (start-here frontier), GPT-5.4 / GPT-5.4-mini, GPT-5.3-Codex / GPT-5.3-Codex-Spark, GPT-5.2-Codex; `/model` switches model + reasoning level. *(developers.openai.com/codex/models + /cli)*
- **xAI Grok**: Grok 4, Grok 4.3 (1M ctx, ~\$1.25 in / \$2.50 out per M tok), `grok-code-fast-1` (agentic coding), and **Grok Build** — a coding-agent CLI competing with Claude Code & Codex (early beta, SuperGrok Heavy). *(docs.x.ai/developers/models + x.ai/news)*

## Per-plugin file set (mirrors existing plugins)

`.claude-plugin/plugin.json` · `README.md` · `CLAUDE.md` · `agents/<agent>.md` (full scenario-authoring schema: `audience`, `works_with`, `scenarios[intent,trigger_phrase,outcome,difficulty]`, `quickstart` — or `check-frontmatter.py` fails CI) · `knowledge/<lineup>.md` (`Last verified:` date + source links + re-verify note).

## Repo wiring

- Append all three to `.claude-plugin/marketplace.json` `plugins[]` (name/source/description/version/author/keywords), version-synced to each `plugin.json`.
- `.repo-layout.json`: **no change needed** — `plugins/*/...` globs already cover these paths (verified against the allow-list).

## Gate-pass checklist before pushing

1. `scripts/check-frontmatter.py` — every agent carries the scenario schema; descriptions quoted (no bare colon-space).
2. `python3 -m json.tool` on all manifests + version-drift check (`plugin.json` ↔ `marketplace.json`).
3. `npx prettier --write . && --check .` (JSON/YAML touched).
4. Layout-violation snippet from AGENTS.md.
5. Commit on `claude/resumed-session-recovery-OXFkX` → push → GitHub MCP draft PR → post-PR decision-review comment.

## Honest caveats

- **Vendor-doc volatility**: even web-verified, these lineups churn weekly. Every fact ships with a source link + `Last verified: 2026-05-31` and an explicit "re-verify before relying" note, per the repo's claim-grounding discipline.
- **Naming**: `github-copilot` / `openai-codex` / `xai-grok` are proposed plugin names.
- **Reconstruction risk**: this plan is reconstructed from a stopped session's partial response, not the original prompt. The one-plugin-per-ecosystem cut is the inferred intent.
