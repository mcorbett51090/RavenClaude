# Changelog — qa-test-automation

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out on top of PR #315 (which shipped the consolidated knowledge decision-trees, best-practices/, and templates/). Every value-add menu item is dispositioned — built or recorded N-A with reason; see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (now 4 field notes + index).** `ice-cream-cone-slow-suite` (pyramid inversion — push logic checks out of the browser, don't re-platform a cone), `contract-test-drift` (verify the contract in the *provider's* CI, not a fatter mock), `coverage-gaming-no-assertions` (mutation testing exposes high-line-coverage / no-assertion tests) join the existing `flaky-test-quarantine-graveyard`. Added `scenarios/README.md` with the 9-field schema and the index table.
- **New decision-tree knowledge.** `knowledge/qa-selector-and-test-data-decision-trees.md` — two Mermaid trees complementing #315's existing trees: **selector resilience** (role/text/test-id over CSS/positional-XPath; the E2E-brittleness signature) and **test-data strategy** (factory vs shared-fixture vs ephemeral-DB vs namespaced), each with a rationale-per-leaf and a tradeoffs table.
- **Runnable analyzer.** `scripts/qa_suite_metrics.py` — `flake_rate` (per-test flake rate from a JSONL run log; pass-on-retry = a flake event, not a pass) and `pyramid_ratio` (unit:integration:e2e shape from counts or an auto-counted directory; flags an inverted ice-cream cone). Stdlib-only (Python 3.9+), `ruff check` clean, executable. Operationalizes the "measure first" lesson of two scenarios.
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring typescript-language-server (TS/JS — Playwright/Cypress) and Pyright (Python — pytest). Ships the config, not the binary; binaries install separately (loud-but-non-fatal if missing). Verified against the Claude Code plugins reference (2026-06-05).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP — Playwright MCP), §8 (scenarios + tooling), the value-add completeness table, and a milestones section.

### Decisions (recorded, not built)

- **No bundled MCP server.** Playwright MCP (`@playwright/mcp`, first-party Microsoft, Apache-2.0) is the one verified broadly-relevant QA server, but it launches a real browser (headed by default), fetches arbitrary URLs as untrusted input, and upstream states it is "not a security boundary" — the doctrine's evaluate-first / `security-reviewer`-gated row. Documented the recommended `claude mcp add` path (pinned + headless + gated) instead of an `mcpServers` entry. No server invented.
- **No `bin/`, monitors, output-styles, settings tuning, or themes** — covered by the single analyzer + advisory hook; no compiled binary, watcher, or vertical-specific permission/styling surface beyond `ravenclaude-core`.
- **Skills/commands/templates/hooks coverage held sufficient** — 5 skills, 4 commands, 4 templates, 1 advisory hook already cover the surface; the new trees + analyzer extend reach without a 5th agent. No `NOTICE.md` (nothing third-party is bundled).

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the `@playwright/mcp` exact version (`0.0.x` as of 2026-06 — pin, don't float `@latest`) and the "not a security boundary" upstream statement. All version-volatile — re-confirm against the vendor before quoting or adopting.

## [0.2.x] — earlier

3-agent QA team (test-strategy-architect, e2e-automation-engineer, test-infrastructure-engineer): 5 skills, the consolidated decision-tree knowledge bank + best-practices + templates (PR #315), 4 commands, 1 advisory hook, 1 seed scenario. Deepens `ravenclaude-core/tester-qa`. Seams to api-engineering (contract tests), devops-cicd (CI gating), frontend-engineering (UI under test).
