---
description: Apply the comfort-posture YAML to .claude/settings.json permission rules.
allowed-tools: Bash, Read
---

# /set-posture

Translate `.ravenclaude/comfort-posture.yaml` (edited via this plugin's dashboard) into `.claude/settings.json` allow/ask/deny permission rules so Claude Code actually applies the posture.

## What this does

1. Reads `.ravenclaude/comfort-posture.yaml` from the project root.
2. For each `(category, level)` pair, emits a list of narrow permission rules per the translation table in `plugins/ravenclaude-core/skills/set-posture.md`.
3. Merges into `.claude/settings.json`:
   - Removes any rules emitted by the previous `/set-posture` run (tracked in `.claude/_comfort-posture-snapshot.json`)
   - Adds the new emission
   - Preserves any hand-added rules
4. Writes back; prints a per-bucket count + diff summary.
5. Warns about session-mode interactions (auto-mode silently drops broad rules; the emitted rules are narrow so most survive).

## How to invoke

Run the translator. The exact path depends on where the plugin is installed; the env var `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's install location:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py"
```

Add `--dry-run` to preview without writing:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py" --dry-run
```

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
- Translation table: `plugins/ravenclaude-core/skills/set-posture.md` (the design rationale)
- Schema: `plugins/ravenclaude-core/dashboard-schema.json` (the YAML shape)
- Permission model: `plugins/ravenclaude-core/knowledge/claude-code-permissions.md` (how Claude Code's engine consumes the rules this command writes)
