# Changelog — microsoft-graph

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.4.0] — 2026-06-05

Value-add build-out completing the menu on top of PR #315 (which added the consolidated decision-trees, `best-practices/`, skills, templates, and the `scenarios/README.md` index). Every menu item dispositioned; see [`CLAUDE.md`](CLAUDE.md) § "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** The four scenarios the existing `scenarios/README.md` index referenced but that were never created: `throttling-429-retry-after-cascade` (a `Retry-After`-ignoring retry *is* the cascade; `$batch` + delta complete the fix), `app-only-consent-failure` (delegated-vs-application **type** + admin **consent** are distinct — re-granting the wrong type fixes nothing), `delta-query-410-resync` (`410 Gone` is a resync instruction, not a failure; follow `Location`, full-enumerate, reconcile), `subscription-silent-expiry` (expiry is silent — green monitoring ≠ alive; renew + `lifecycleNotificationUrl` + delta resync). 9-field schema, Microsoft-Learn-cited, dated, no secrets/tenant IDs.
- **Runtime error-disposition decision trees.** `knowledge/api-error-disposition-decision-trees.md` — two new Mermaid trees complementing #315's *design-time* trees: (1) disposition a non-2xx response (which HTTP status → the **non-interchangeable** fix: 401 re-auth-and-retry vs 403 fix-permission vs 429 wait-`Retry-After` vs 410 resync vs 409/412 reconcile vs 5xx backoff), (2) silent-vs-hard failure ("is green actually healthy?" — subscription expiry, `$batch` 200-envelope sub-failures, delta-token aging, dropped webhooks). Dispositions all 4 new scenarios.
- **Permission-matrix template.** `templates/graph-permission-matrix.md` — a fillable capability→permission decision matrix (type/consent/narrower-alternative/runtime-disposition) that feeds the existing `graph-app-registration` worksheet; distinct from the `permission-least-privilege-review` audit skill.
- **Scope analyzer script.** `scripts/graph_scope_analyzer.py` — stdlib-only (no network/no tenant contact) analyzer for a permission list or a JWT's `scp`/`roles` claims (claims-only, no signature verification); flags over-privilege per CLAUDE.md §3 #1 / §4, suggests narrower alternatives, exits `1` on mandatory `security-reviewer` escalation (CI-usable). Ruff-clean.
- **Bundled MCP server `microsoft-learn`.** Declared in `plugin.json` (`type: http`, `url: https://learn.microsoft.com/api/mcp`) with top-level `x-mcpAttribution` + `NOTICE.md`. Remote HTTP, no auth, read-only, MIT tooling — clears the zero-config-read-only bundling bar (`docs/best-practices/bundled-mcp-servers.md`). Mirrors the `microsoft-365-copilot` precedent. Gives agents a tool to verify volatile Graph facts against current Learn docs (§3 #9 / §5).
- **CLAUDE.md** §7 (scenarios + script pointers), §7a (bundled-MCP doctrine + Lokka recommend-not-bundle), the value-add completeness table, and a milestones note. **NOTICE.md** added (required once a third-party server is bundled).

### Decisions (recorded, not built)

- **Credentialed Graph MCPs are recommend-not-bundle.** Lokka (`@merill/lokka`, MIT) is per-tenant Entra-authenticated and write-capable (`POST`/`PUT`/`PATCH`/`DELETE`) → documented setup + secret-as-a-reference + a `security-reviewer` gate, never an `mcpServers` entry. No invented servers.
- **No LSP** — not a single-source-language authoring domain (agents emit .NET/JS/Python/PowerShell/HTTP snippets); no one language server fits.
- **No `bin/`, monitors, output-styles, settings, or themes** — none cleared the "groundable + broadly valuable, doesn't duplicate the advisory hook / the new script / the §6 Output Contract" bar.
- **No 5th skill** — post-#315 the plugin has 5 skills + 4 templates with strong coverage; the genuine gap was a decision *artifact* (the permission-matrix template), not another playbook.

### Verify-at-use

- Microsoft Graph throttle limits, delta-token durations (directory ~7 days), and subscription max-expiration per resource (chatMessage ~60 min; message/event/contact ~7 days non-rich, ~1 day rich; driveItem/list ~30 days; user/group ~29 days) — version-volatile; re-verify against Microsoft Learn before quoting (sources cited inline in each file).
- Lokka package version `0.1.7`, its auth env-var names, and tool surface; the Learn MCP endpoint + Claude Code `claude mcp add --transport http` flags — all version-volatile.

## [0.3.2] — earlier (#315 and prior)

3-agent Microsoft Graph team (graph-api-engineer, graph-identity-engineer, graph-workloads-engineer): 5 skills, 4 templates, 5 commands, 1 advisory hook, 3-file decision-tree knowledge bank, a best-practices library, and the scenarios README + index.
