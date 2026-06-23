# Plugin best-practices audit — 2026-06-23

Audit of all **117** RavenClaude plugins against (a) the repo's own documented conventions
(AGENTS.md house rules + per-plugin CLAUDE.md) and (b) **official** Claude Code plugin-authoring
docs (code.claude.com, retrieved 2026-06-23). Run via `/forge` (depth `standard`).

## Headline result
The repo is **already in strong conformance**. The ~100+ CI gates (`audit-gates.sh`,
`check-frontmatter`, `check-marketplace-claims`, `check-layout`, `check-md-links`, …) mean any
gate-enforced convention *cannot* currently be violated. The audit targeted **drift the gates do
NOT catch** — and found exactly one real class.

## Confirmed gaps (fixed in this PR)
| Gap | Count | Standard | Action |
|---|---|---|---|
| CHANGELOG top entry behind `plugin.json` version | **31** | AGENTS.md: "if a plugin HAS a CHANGELOG.md, keep its top entry current on every version bump" — **not CI-gated** | Added a factual entry per plugin, dated by and citing the actual version-setting commit (`git log` of `plugin.json`), style-matched to each file |

## Candidate gaps investigated and DISMISSED (false positives)
| Candidate | Verdict |
|---|---|
| 104 plugins with "undeclared" dirs (`scenarios`/`best-practices`/`scripts`/`bi-report`) | **False positive** — all already in `.repo-layout.json` `allowed_globs`; repo-standard aux dirs, not novel purpose-dirs |
| Agents declaring `hooks`/`mcpServers`/`permissionMode` (official: silently ignored for plugin agents) | **0 violations** |
| Component dirs misplaced inside `.claude-plugin/` (official: must be at plugin root) | **0** |
| kebab-case "violations" (96 hits) | **Mostly false positive** — `NOTICE.md` (conventional), snake_case `*.py` (PEP 8 / importability), `_private.sh` (intentional) |
| Missing `plugin.json` fields vs official schema | **None** — all 117 carry name/version/description/author/homepage/license/keywords; official requires only `name` |
| `marketplace.json` required fields | **Clean** — top-level name/owner/plugins present; all 117 entries have name+source |
| Skill `description`+`when_to_use` > 1536 chars (official truncation) | **None** |
| `commands/` flat-file skills | **Not a defect** — official docs: legacy-but-supported |

## Verified official-vs-convention clarifications (code.claude.com 2026-06-23)
- `plugin.json` requires **only `name`**; everything else is recommended/optional.
- The repo's **300-char agent-description cap is a self-imposed convention** (orchestrator ~15K budget), **not** an official limit. The only documented length limit is the **skill** listing truncation at **1536 chars**.
- Plugin-shipped agents **ignore** `hooks`/`mcpServers`/`permissionMode` (security) — worth a future gate, though currently 0 violations.

## Suggested follow-up (NOT in this PR)
- Add a CI gate to `audit-gates.sh` that flags a stale CHANGELOG top entry (top `## [x.y.z]` ≠ `plugin.json` version) so this drift can't recur silently.
- Optionally add an agent-frontmatter gate rejecting `hooks`/`mcpServers`/`permissionMode` (defends the official trap proactively).
