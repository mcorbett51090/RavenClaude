---
description: Apply the comfort-posture YAML to .claude/settings.json permission rules.
allowed-tools: Bash, Read
---

# /set-posture

Translate `.ravenclaude/comfort-posture.yaml` (edited via this plugin's dashboard) into `.claude/settings.json` allow/ask/deny permission rules so Claude Code actually applies the posture.

## What this does

1. Reads `.ravenclaude/comfort-posture.yaml` from the project root.
2. For each `(category, level)` pair, emits a list of narrow permission rules per the translation table in `plugins/ravenclaude-core/skills/set-posture/SKILL.md`.
3. **Overwrites** `permissions.{allow,ask,deny}` in the target settings file with the emission (since v0.17.0 — the YAML is the single source of truth; hand-edits to those buckets are replaced, so keep personal extras in `.claude/settings.local.json`, which Claude Code merges on top).
4. Writes back; prints a per-bucket count + diff summary.
5. Warns about session-mode interactions (auto-mode silently drops broad rules; the emitted rules are narrow so most survive).

## Schema v5 — per-layer (multi-layer posture)

A v5 posture sets each category independently at the **user** / **local** / **project** layer (`allow` / `ask` / `deny` / `inherit`). `/set-posture` then writes one settings file per active layer:

| Layer | File | Shared? |
|---|---|---|
| user | `~/.claude/settings.json` | no — all your projects on this machine |
| local | `.claude/settings.local.json` | no — gitignored, this project only |
| project | `.claude/settings.json` | **yes — committed**; also carries the `security_deny` floor |

Claude Code merges all three at runtime as **deny > ask > allow** — the strictest layer wins, so a personal `allow` cannot loosen a team `ask`/`deny`. v3/v4 single-layer postures still work unchanged (they write only the project file).

## How to invoke

Run the translator. `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install location:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py"
```

Useful flags:

```bash
# Preview without writing
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py" --dry-run

# (v5) Write only one layer instead of all active layers
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py" --scope local

# (v5) Show the merged effective posture across all three layers
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py" --preview-merge
```

The dashboard's **"Save & apply all layers"** button performs the save + apply in one step (via `scripts/serve-dashboards.py`), so manual invocation is mostly for CI or headless use.

## When the posture file doesn't exist

If `.ravenclaude/comfort-posture.yaml` doesn't exist yet, the script prints:

> ERROR: <path> does not exist. Open the dashboard and click 'Save to repo' to create one.

Point the user at `plugins/ravenclaude-core/dashboard.html` — the Settings tab is where they pick their levels. Save to repo writes the YAML; then `/set-posture` translates it.

## Session-mode interactions

After applying, the user should keep their session mode at **default** for the posture to be fully effective:

- **Plan mode** — composes cleanly (no writes regardless of posture)
- **Accept edits** — overrides `shell_local_mutate` ask-rules for the session
- **Auto-mode** — silently drops broad allow rules by design; some categories partially fail
- **bypassPermissions** — bypasses these rules entirely

The script's footer reminds the user of this on every run.

## Related artifacts

- Dashboard: `plugins/ravenclaude-core/dashboard.html` (the input UI)
- Translation table: `plugins/ravenclaude-core/skills/set-posture/SKILL.md` (the design rationale)
- Schema: `plugins/ravenclaude-core/dashboard-schema.json` (the YAML shape)
- Permission model: `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` (how Claude Code's engine consumes the rules this command writes)
