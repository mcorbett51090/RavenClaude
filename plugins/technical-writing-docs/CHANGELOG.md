# Changelog — technical-writing-docs

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.0] — 2026-06-05

Value-add build-out against the full value-add menu — every menu item dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §9 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `api-docs-drift-from-code` (collapse competing sources to one spec, gate spec-freshness + examples in CI), `no-information-architecture` (fix the IA before the search; card-sort against the four Diátaxis kinds), `tutorial-reference-confusion` (split the mixed-kind "Getting Started" page), `docs-review-bottleneck` (split mechanical vs. judgment; automate prose lint in CI + editor LSP). Matches the existing `scenarios/README.md` index and the 9-field schema — the README listed them; the files were the net-new gap.
- **Decision-tree knowledge (2 new Mermaid trees).** `knowledge/diataxis-content-type-selection-decision-tree.md` (four-kind selector deepened with the mixed-kind split, resolved against the 2D needs grid) and `knowledge/lint-in-ci-vs-manual-review-decision-tree.md` (automate-in-CI/editor vs. keep-it-human). Complement the 8 trees consolidated into the bank file. Authored with `## The tree` headings (not `## Decision Tree:`) so they render inline without triggering the SVG pre-render gate.
- **Prose-linter LSP tier.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring **Vale-LS** (`vale-ls`, prose/style diagnostics) and **Marksman** (`marksman server`, markdown structure). Ships the config, not the binary; binaries install separately (loud-but-non-fatal if missing) — the editor half of the lint decision tree.
- **Runnable script.** `scripts/docs_check.py` — stdlib-only, ruff-clean: Flesch Reading Ease + Flesch-Kincaid Grade Level readability (markdown-stripped) and a prose-hygiene linter (non-descriptive links, placeholders, weasel words, banned/inconsistent terminology). Complements (does not replace) Vale; needs nothing installed.
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP), §8 (runnable script), §9 (value-add table), §10 (milestones).

### Decisions (recorded, not built)

- **No bundled MCP server.** No docs-MCP clears the doctrine's zero-config + read-only bar: the MIT first-party filesystem/git reference servers need a consumer-specific path and are write-capable; a docs-vendor MCP is per-tenant + secret-handling. Documented the recommended `claude mcp add …` paths instead. No invented servers. Vale's value reaches the agent via the LSP, not an MCP.
- **No `bin/`, output-styles, monitors, settings, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate the Output Contract / advisory hook / runnable script" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — no 5th skill added; the new trees + script + LSP extend reach without a new agent (team-growth-as-knowledge house rule).

### Verify-at-use

- **Vale-LS** v0.4.0 (2025-03-14, MIT) and the `cargo install vale-ls` / bare-`vale-ls`-stdio invocation; **Marksman** `marksman server` stdio invocation; the docs-tooling landscape (notably **Material for MkDocs entered maintenance mode 2025-11-05**, 9.7.0 the last feature release, team moved to "Zensical"). All version-volatile — re-confirm against the vendor before quoting.

## [0.2.x] — earlier

3-agent technical-writing-docs team (docs-architect, api-reference-writer, docs-site-engineer). PR #315 consolidated the decision-tree knowledge bank (8 trees + a dated 2026 map), `best-practices/` (12 rules), and `templates/` (4). 5 skills, 4 commands, 1 advisory hook. Seams to api-engineering, web-design, devops-cicd, and ravenclaude-core/documentarian.
