# Changelog — frontend-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.4.0] — 2026-06-09

Version bump previously unlogged here (rolls up `0.3.0` → `0.4.0`); the change that set `0.4.0`:

- feat: visual-feedback-loop — render→see→iterate for web + reporting agents (#378)

## [0.3.0] — 2026-06-05

Value-add build-out — adding the net-new gap left after PR #315 (which added the consolidated decision-tree knowledge, best-practices, and templates): the scenarios bank and the technical-runtime tier. Every value-add menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §9 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `hydration-mismatch-locale-date` (a hydration mismatch is a correctness bug — pin the non-deterministic input, don't `suppressHydrationWarning`), `cls-lcp-perf-budget-regression` (diagnose CWV by metric + cause; fix LCP discovery before size; gate the budget in CI), `server-state-in-redux-refactor` (server state is not client state — migrate to a server-cache lib, don't add store discipline), `accessibility-audit-modal-focus` (accessibility is implementation, not attributes — use a vetted dialog primitive). Matches the existing `scenarios/README.md` index and the 9-field schema.
- **Decision-tree knowledge.** `knowledge/styling-and-bundle-decision-trees.md` — two Mermaid trees: styling-approach selection (RSC-aware, zero-runtime default) and bundle-size-regression triage, plus a dated capability map. Chosen to **complement** #315's `frontend-engineering-decision-trees.md` (rendering/state/component/fetch/optimistic/store/slow-render/form), not duplicate it.
- **Runnable tooling.** `scripts/perf_budget.py` (stdlib only, Python 3.8+) — `bundle` (per-route JS size vs. KB budget, CI-gateable exit code) and `vitals` (75th-pct LCP/INP/CLS vs. Google's "good" thresholds). A checker, not a measurement tool.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP servers), §8 (runnable tooling), §9 (value-add disposition table), §10 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** The two real, first-party frontend MCP servers — Microsoft's `@playwright/mcp` and Google's `chrome-devtools-mcp` — each launch and drive a live browser (side-effecting subprocess) and are first-party-from-the-vendor, which the bundling doctrine routes to **recommend, don't bundle** (with a `security-reviewer` gate for the browser-automation tools). Documented the recommended `claude mcp add …` paths instead. No invented servers.
- **`.lsp.json` kept as-is.** The pre-existing config (typescript-language-server / vscode-eslint-language-server / vscode-css-language-server, wired via `plugin.json` `lspServers`) already covers the stack; documented the install path (`typescript-language-server` + `vscode-langservers-extracted`) in CLAUDE.md §6. No change to the config.
- **No `bin/`, output-styles, monitors, themes, or 5th skill** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or `web-design`'s visual lane" bar.

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the `vscode-langservers-extracted` package providing the ESLint + CSS servers (community-maintained, active forks — vet at adoption); Core Web Vitals "good" thresholds (LCP < 2.5s / INP < 200ms / CLS < 0.1 at the 75th pct); `@playwright/mcp` and `chrome-devtools-mcp` package names, tool surfaces, versions (`chrome-devtools-mcp` ~v0.21.0 Apr 2026), and `chrome-devtools-mcp`'s telemetry-on-by-default. All version-volatile — re-confirm against the vendor before quoting. One unofficial source claimed Google tightened LCP to 2.0s in a March-2026 update; treated as `[unverified]` and the established 2.5s bar used.

## [0.2.2] — earlier

4-agent frontend-engineering team (frontend-architect, react-implementation-engineer, frontend-state-and-data-engineer, frontend-performance-engineer): 5 skills, a decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook, `.lsp.json` (TS/ESLint/CSS). Seams to web-design, auth-identity, api-engineering, mobile-engineering, qa-test-automation. PR #315 added the consolidated decision-tree knowledge, best-practices, and templates.
