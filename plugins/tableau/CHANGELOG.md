# Changelog — tableau

All notable changes to the `tableau` plugin. Versioning is semver; the authoritative version is
the `version` field in `.claude-plugin/plugin.json` (mirrored in `marketplace.json`).

## 0.4.0 — 2026-06-09

Version bump previously unlogged here (rolls up `0.3.0` → `0.4.0`); the change that set `0.4.0`:

- feat: visual-feedback-loop — render→see→iterate for web + reporting agents (#378)

## 0.3.0 — 2026-06-05 — value-add completeness build-out

Pilot build-out completing the plugin against the marketplace value-add menu. **No breaking
changes** — all additions are new components; existing agents, knowledge, and best-practices are
unchanged.

### Added

- **`scenarios/`** — the unverified field-note bank (4 dated scenarios + README): FIXED-LOD vs
  dimension-filter order-of-operations, embedding JWT scope + RLS mismatch (401 + leak),
  Server→Cloud extract-refresh dead-end, and a Performance-Recorder slow-dashboard diagnosis.
- **`skills/`** — 2 step-by-step procedures: `workbook-performance-audit` (evidence-first
  Performance Recorder ladder) and `embedding-connected-apps-jwt` (Connected App / Direct Trust
  JWT + Embedding API v3 setup, security-gated).
- **`hooks/`** — `flag-tableau-anti-patterns.sh` (advisory `PreToolUse(Write|Edit)` on `.twb`/
  `.tds`) flagging 6 grep-able anti-patterns (trusted tickets, embedded creds, unjustified live
  connections, blend-vs-relationship, default table-calc addressing, user-filter-as-RLS) + a
  `hooks.json` registering it with `${CLAUDE_PLUGIN_ROOT}` paths. Advisory, never blocking.
- **`templates/`** — 4 fill-in templates: workbook-performance-audit, governance-rls-plan,
  embedding-design-spec, dashboard-design-spec.
- **`knowledge/data-freshness-pipeline-decision-trees.md`** — 3 new grounded, cited Mermaid
  decision trees (refresh path Bridge vs Cloud-native, refresh scope full vs incremental,
  stale-dashboard diagnosis).

### Notes

- **MCP server:** the official `tableau/tableau-mcp` (Apache-2.0) is **recommended, not bundled**
  — it is per-tenant + authenticated (PAT secrets), so it cannot ship a hardcoded `mcpServers`
  entry. See `CLAUDE.md` § "Value-add completeness" for the disposition.
- **Migration:** none. New top-level dirs (`scenarios/`, `skills/`, `hooks/`, `templates/`) need
  `.repo-layout.json` globs — these already exist marketplace-wide (`plugins/*/skills/**`, etc.).

## 0.2.1 and earlier

Initial roster (3 agents: viz-engineer, data-architect, admin), citation-grounded `knowledge/`
decision trees, `best-practices/` library (28 rules), and `commands/`. See git history.
