# FORGE reference — per-phase regen discipline (G8 DoD)

> Loaded by [`../SKILL.md`](../SKILL.md) **at G8 only, and only when a phase adds/removes a skill,
> agent, or other artifact whose count is encoded in marketplace prose**. A pure design/analysis plan
> never reaches this file.

**Lesson from the 2026-06-03 hotfix chain, PRs #244-#247.** When a phase changes a counted artifact,
`plan.md` must explicitly list these acceptance criteria in that phase's DoD — otherwise CI breaks on
merge and a 3-PR hotfix chain follows.

1. **Quote `description:` in any SKILL.md / agent .md YAML frontmatter** that contains `:` / `{` /
   `}` (the strict-YAML check via `scripts/check-frontmatter.py` parses unquoted scalars). The
   common trip: a backtick-wrapped `enabled: false` etc. in the description.
2. **Bump skill/agent count strings** in `.claude-plugin/marketplace.json` (top metadata.description
   + the plugin's entry description) AND `plugins/<plugin>/.claude-plugin/plugin.json` description.
   Gate 12 (`marketplace-claims`) compares these to the actual filesystem count.
3. **Regenerate `dashboard.html`** via `python3 scripts/generate-dashboards.py` (Gate 13).
4. **Regenerate the portal** via `python3 scripts/generate-index-dashboard.py` — `index.html` folds
   the dashboard + catalog in natively, and its `--check` freshness gate runs in `audit-gates.sh`.
5. **Regenerate the Copilot package** via `python3 scripts/generate-copilot-plugin.py` (Gate "copilot
   package freshness").
6. **Update `scripts/audit-gates.sh`** fixture literals that hardcode the old skill count (look for
   `s.replace('<N> skills', '20 skills', 1)` — the must_fail fixture mutates this literal; it must
   point at the current real count or it becomes a no-op and the gate's bad-input test silently
   passes where it should fail).
7. **Strip session-bound mutations** (`.ravenclaude/comfort-posture.yaml` posture changes a hook
   wrote while the session ran) before committing — only commit the substantive edits.

`plugin-release-checklist` covers most of this for full releases; FORGE's per-phase plans MUST
restate the relevant subset inline so the Phase-1 build agent doesn't repeat the hotfix chain.

> **Staleness note — this list rots.** It was written against the 2026-06-03 gate harness; item 4
> previously told agents to run `scripts/generate-repo-guide.py`, which **v0.124.0 deleted** along with
> `repo-guide.html` (Gate 11 is retired — see the comment at `scripts/audit-gates.sh:761`), so the
> instruction had been dead for months. It now names the live portal generator instead `[verified this
> session: generate-repo-guide.py absent; generate-index-dashboard.py --check present at
> audit-gates.sh:148 and :3584]`. **Re-derive the live set from `scripts/audit-gates.sh` before pasting
> these into a phase DoD** — the gate harness is the source of truth, this file is a cached copy.
