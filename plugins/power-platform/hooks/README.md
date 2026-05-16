# power-platform hooks

This directory ships hook scripts that enforce the Power Platform team constitution
([`../CLAUDE.md`](../CLAUDE.md)) on real edits. Hooks are **advisory by default** —
they print warnings to stderr (which both Claude and the user see) but don't block
the edit. Each script documents how to flip it to blocking if you want enforcement.

## Available hooks

| Script | When it fires | What it catches |
|---|---|---|
| [`check-house-opinions.sh`](./check-house-opinions.sh) | PostToolUse on Edit / Write / MultiEdit, for files under `CanvasApps/Src/`, `Solutions/`, or with extensions `.fx.yaml` / `.pa.yaml` / `solution.xml` / `customizations.xml` / `.cdsproj` / `.msapp` | (1) GUIDs hard-coded in Power Fx canvas YAML, (2) default publisher prefix (`cr_`, `crXXX_`, `new_`) in solution XML, (3) hard-coded SharePoint / Dynamics tenant URLs in any source file |

## Wiring in a consumer project's `.claude/settings.json`

Plugin hooks don't auto-wire — Claude Code reads hooks from the consumer project's
`.claude/settings.json`. Add this entry:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-house-opinions.sh \"$CLAUDE_TOOL_FILE_PATH\"",
            "comment": "Advisory: Power Platform house-opinion violations (GUIDs in Power Fx, default publisher prefix, hard-coded tenant URLs)."
          }
        ]
      }
    ]
  }
}
```

If `$CLAUDE_PLUGIN_ROOT` is not set in your environment, replace it with the
absolute path to `plugins/power-platform` (e.g. `~/.claude/plugins/power-platform`
for a marketplace install, or your local checkout path).

## To make a hook blocking instead of advisory

Open the script and change the final `exit 0` to `exit 1`. The edit will then
be rejected when a violation is detected. Recommended only after you've shaken
out false positives in your codebase.
