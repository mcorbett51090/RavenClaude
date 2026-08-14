# Product-analog catalog (evidence samples)

**Last verified:** 2026-08-14  
**N = 13** (harvest cap 30; shortfall 17 is the honest result)  
**Provenance:** `[obs]` = file body or root listing via `gh api` this day. `[inf]` = listing-only inference. `[unverified]` = not used as a row.  
**Gold ≠ everything in their README.** Stars are `[verify-at-use]` metadata, never a rank key.  
**Exclusion-clean:** zero protocol-30, operator-7, `anthropics/claude-plugins-official`, or this repo as rows.

This is **evidence** for the C01–C15 matrix, not a fill backlog and not a tourism table.

## Rubric

**Dims** M/H/G/O/E/I/T/V scored 0/1/2. Weighted `3M+3H+3G+2O+2E+2I+2T+1V` (max 36).

| dim | meaning |
|---|---|
| M | Marketplace catalog + install path |
| H | Multi-host projection from one tree |
| G | Hooks / governance as policy |
| O | Agent ops / routing |
| E | Eval / golden-set of agent failures |
| I | Installer / CLI |
| T | Trust boundary for untrusted tool/web output |
| V | Operator-visible catalog / dashboard |

**Closeness** is recomputed from the weighted score: 0–8 → 1, 9–14 → 2, 15–20 → 3, 21–27 → 4, 28–36 → 5. Checker: `.ravenclaude/runs/forge/analog-repos-gap-fill/survey/check-closeness.py`.

**Quality bar:** ≥1 of M/H/G ≥ 1 **and** ≥3 dims `[obs]`. Fail → `dropped.md`.

## Verified set (ranked by closeness, then weighted)

| # | owner/repo | cat | close | w | M H G O E I T V | capabilities | note |
|---|---|---|---:|---:|---|---|---|
| 1 | [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | marketplace | 4 | 25 | 2 1 2 2 0 2 0 2 | C01 C03 C04 C05 C13 C14 | Catalog + `ccpi` CLI + frontmatter validator |
| 2 | [netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace) | marketplace | 4 | 25 | 2 2 1 1 1 2 0 2 | C01 C02 C03 C09 C14 | Portable Agent Skills; `/plugin` + `npx skills add` |
| 3 | [wshobson/agents](https://github.com/wshobson/agents) | marketplace | 4 | 21 | 2 2 0 2 0 2 0 1 | C01 C02 C03 C04 | One `plugins/` tree → Claude/Codex/Cursor/OpenCode/Gemini/Copilot |
| 4 | [obra/superpowers](https://github.com/obra/superpowers) | skills-framework | 4 | 22 | 1 2 1 2 1 2 0 0 | C02 C03 C04 C05 | Per-host install; methodology, not a catalog |
| 5 | [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) | governance | 3 | 19 | 1 1 2 1 0 1 1 1 | C05 C06 C15 | Policy/identity/sandbox product |
| 6 | [KbWen/agentic-os](https://github.com/KbWen/agentic-os) | governance | 3 | 16 | 0 2 2 1 0 1 0 0 | C05 C08 C11 | Evidence-gated plan/build/review/test/ship |
| 7 | [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | single-plugin | 2 | 13 | 1 2 0 1 0 1 0 0 | C01 C02 C03 | One plugin, several hosts |
| 8 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | skills-pack | 2 | 13 | 1 1 1 1 0 1 0 0 | C03 C05 | Lifecycle skills; `evals/` listing-only |
| 9 | [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) | host-bridge | 2 | 13 | 1 1 1 1 0 1 0 0 | C01 C02 | Codex inside Claude Code |
| 10 | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | templates-cli | 2 | 10 | 0 0 1 1 0 2 0 1 | C03 C14 | npm CLI; no `marketplace.json` |
| 11 | [anthropics/skills](https://github.com/anthropics/skills) | skills-spec | 2 | 10 | 2 0 0 1 0 1 0 0 | C01 C03 | Official skills impl + spec (not the official *marketplace*) |
| 12 | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | marketplace | 2 | 10 | 2 0 0 1 0 1 0 0 | C01 C03 C04 | First-party Cowork/Code catalog |
| 13 | [snarktank/ralph](https://github.com/snarktank/ralph) | agent-loop | 1 | 8 | 0 1 1 1 0 0 0 0 | C05 C11 | Fresh-context PRD loop |

RavenClaude baseline (matrix only, not a catalog row): closeness **5** on HEAD `0.267.0` (F1/F2 merged; C06/C15 still partial on MCP).

## What 13 is not

- Not “30 gold analogs.” The close population is thin at the governance layer and commoditized at the catalog layer.
- Not a reason to add a host, vendor a runtime, or copy a README hook.
- Not the fill generator. Fills start from local known-bads (T3).

Machine-readable rows + dim evidence: `.ravenclaude/runs/forge/analog-repos-gap-fill/survey/verified.jsonl` (gitignored run tier). Dropped / excluded: same dir `dropped.md`. Matrix: [capability-matrix.md](capability-matrix.md).
