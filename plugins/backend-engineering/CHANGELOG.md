# Changelog — backend-engineering

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.3.6] — 2026-10-19

### Fixed

- **N+1 and dual-write checks never fired** (repo-review 2026-10-19, domainplugins-1). Both were `grep -E "...[\\s\\S]{0,N}..."`: POSIX ERE reads `[\s\S]` as the set {backslash, s, S} and grep is line-oriented, so neither could match. Both are perl (multi-line) now, tightened first: N+1 is a loop line followed, on the same line or one of the next four body lines, by `.query(` / `.execute(` / a filter-object `.find({` / an ORM finder (`findOne`, `findById`, ...) / upper-case `SELECT`; a bare `.get(` or a string `.find(` no longer counts. Dual-write is a commit/save call followed within four lines by a publish/emit call.

Fixtures that drive the hook exactly as `hooks.json` registers it (fires on the anti-pattern, silent on clean code) are in `scripts/check-domain-hook-teeth.py` (control: the same fixtures run against the pre-fix hook fail, the anti-pattern case printing nothing).

**Migration:** none. The hook is advisory; expect these checks to fire where they never did.

## [0.3.5] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.3.2] — 2026-06-22

Version bump previously unlogged here (rolls up `0.3.0` → `0.3.2`); the change that set `0.3.2`:

- Repo review autonomous fixes + B1–B6 deferred items + dead-regex CI guard (#449)

## [0.3.0] — 2026-06-05

Pilot value-add build-out — proving the repeatable plugin-enrichment recipe against the full value-add menu. Every menu item was dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (pilot build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `idempotent-payments-endpoint` (unique-index dedup beats check-then-act), `n-plus-one-and-pool-exhaustion` (diagnose the N+1 before resizing the pool), `zero-downtime-schema-migration` (expand/contract across rolling deploys), `async-job-queue-poison-message` (DLQ + idempotent consumer are both non-negotiable under at-least-once). Matches the existing `scenarios/README.md` index and the 9-field schema.
- **Decision-tree knowledge.** `knowledge/data-store-and-api-paradigm-decision-trees.md` — two Mermaid trees: relational-vs-NoSQL store selection, and REST-vs-GraphQL-vs-gRPC paradigm selection, plus a dated capability map. Fills the gaps left by the existing tree file (monolith/cache/sync-async/extract).
- **LSP code-intelligence config.** `.lsp.json` (referenced from `plugin.json` `lspServers`) configuring Pyright (Python), typescript-language-server (TS/JS), and gopls (Go) — the plugin's example languages. Ships the config, not the binary; binaries install separately (loud-but-non-fatal if missing). Verified against the Claude Code plugins reference (2026-06-05).
- **CLAUDE.md** §5 (knowledge & scenario banks), §6 (LSP tier), §7 (recommended-not-bundled MCP servers), and the value-add completeness disposition table.

### Decisions (recorded, not built)

- **No bundled MCP server.** No backend-useful server clears the doctrine's zero-config + read-only bar: the MIT first-party filesystem/git reference servers need a consumer-specific path and are write-capable; a Postgres server is per-tenant + secret-handling; the Anthropic `@modelcontextprotocol/server-postgres` reference is archived/deprecated. Documented the recommended `claude mcp add …` paths (with a `security-reviewer` gate for the DB path) instead of shipping an `mcpServers` entry. No invented servers.
- **No `bin/`, output-styles, monitors, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface or a neighbouring plugin" bar.
- **Skills/commands/templates/hooks coverage held sufficient** — no 5th skill added (idempotency is already covered across a template + best-practice + the `backend-implementation` skill).

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the `gopls` install path (`go install golang.org/x/tools/gopls@latest`); the MCP reference-server set + the postgres-reference deprecation; the MCP Toolbox for Databases version. All version-volatile — re-confirm against the vendor before quoting.

## [0.2.0] — earlier

4-agent backend-engineering team (backend-architect, service-implementation-engineer, backend-data-access-engineer, backend-reliability-engineer): 4 skills, a decision-tree knowledge bank, 12 best-practices, 4 templates, 4 commands, 1 advisory hook. Seams to api-engineering, database-engineering, devops-cicd, observability-sre, auth-identity.
