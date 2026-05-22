#!/usr/bin/env python3
"""
apply-comfort-posture.py — translate .ravenclaude/comfort-posture.yaml
into .claude/settings.json permission rules.

Read by the /set-posture slash command. Can also be invoked directly:

    python3 plugins/ravenclaude-core/scripts/apply-comfort-posture.py
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py --dry-run

What it does:
  1. Read .ravenclaude/comfort-posture.yaml from the consumer's project root.
  2. For each (category, level) pair, emit a list of permission rules using
     the EMISSIONS table below.
  3. Read .claude/settings.json. Remove rules that the previous /set-posture
     run emitted (tracked in .claude/_comfort-posture-snapshot.json).
  4. Add the new emission. Preserve any hand-added rules.
  5. Write back .claude/settings.json + update the snapshot.
  6. Print a summary of what changed plus a warning about session-mode
     interactions (auto-mode silently drops broad rules).

Design constraints (v0.1.0):
  - **Narrow rules only.** Emit `Bash(git push:*)`, NOT `Bash(*)`. Auto-mode
    silently drops the broad shapes; narrow rules survive.
  - **Snapshot-based removal.** Hand-added rules in settings.json survive
    re-application because the script only removes rules it previously
    emitted (tracked by snapshot).
  - **Five levels collapse to three buckets** in v0.1.0:
      deny         -> deny
      always-ask, mostly-ask     -> ask
      mostly-allow, autopilot    -> allow
    v0.2.0 will split each Bash category into safe/risky shapes so
    always-ask vs mostly-ask and mostly-allow vs autopilot become
    meaningfully different (the architect's "split for risky shapes"
    pattern from proposal 002 §5).

Dependencies: PyYAML if present (graceful fallback to a small built-in
parser if not, since the YAML shape is tiny and constrained).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT_ENV = "CLAUDE_PROJECT_DIR"


def find_project_root(start: Path) -> Path:
    """Find the consumer's project root by walking up to find .claude/ or .git/."""
    p = start.resolve()
    while p != p.parent:
        if (p / ".claude").is_dir() or (p / ".git").is_dir():
            return p
        p = p.parent
    return start.resolve()


# ── EMISSIONS table — category -> list of permission rule patterns ──
# Each pattern is emitted under exactly one bucket (deny / ask / allow)
# based on the category's level in the posture YAML. Patterns are NARROW
# by design — broad shapes like Bash(*) get silently dropped under
# auto-mode (verified in plugins/ravenclaude-core/knowledge/
# claude-code-permissions.md "Permission modes — the six modes" section).

EMISSIONS: dict[str, list[str]] = {
    # ── File categories ──────────────────────────────────────────
    "file_read_project": [
        "Read(**)",
    ],
    "file_edit_project": [
        "Edit(**)",
        "Write(**)",
        "MultiEdit(**)",
    ],
    "file_read_global": [
        "Read(~/**)",
        "Read(//**)",
    ],
    "file_edit_global": [
        "Edit(~/**)",
        "Write(~/**)",
        "Edit(//**)",
        "Write(//**)",
    ],
    # ── Shell categories ────────────────────────────────────────
    "shell_readonly": [
        "Bash(ls:*)",
        "Bash(cat:*)",
        "Bash(head:*)",
        "Bash(tail:*)",
        "Bash(wc:*)",
        "Bash(file:*)",
        "Bash(stat:*)",
        "Bash(which:*)",
        "Bash(type:*)",
        "Bash(grep:*)",
        "Bash(rg:*)",
        "Bash(find:*)",
        "Bash(tree:*)",
        "Bash(echo:*)",
        "Bash(pwd)",
        "Bash(git status:*)",
        "Bash(git log:*)",
        "Bash(git diff:*)",
        "Bash(git show:*)",
        "Bash(git branch:*)",
        "Bash(git ls-files:*)",
        "Bash(git remote:*)",
        "Bash(git blame:*)",
        "Bash(git stash list)",
        "Bash(gh pr view:*)",
        "Bash(gh pr list:*)",
        "Bash(gh pr diff:*)",
        "Bash(gh pr checks:*)",
        "Bash(gh issue view:*)",
        "Bash(gh issue list:*)",
        "Bash(gh run view:*)",
        "Bash(gh run list:*)",
    ],
    "shell_local_mutate": [
        "Bash(mkdir:*)",
        "Bash(touch:*)",
        "Bash(cp:*)",
        "Bash(mv:*)",
        "Bash(ln:*)",
        "Bash(chmod:*)",
        "Bash(rm:*)",
        "Bash(git add:*)",
        "Bash(git commit:*)",
        "Bash(git checkout:*)",
        "Bash(git switch:*)",
        "Bash(git stash:*)",
        "Bash(git restore:*)",
        "Bash(git reset:*)",
        "Bash(git merge:*)",
        "Bash(git rebase:*)",
        "Bash(git tag:*)",
    ],
    "shell_remote_mutate": [
        "Bash(git push:*)",
        "Bash(git fetch:*)",
        "Bash(git pull:*)",
        "Bash(gh pr create:*)",
        "Bash(gh pr edit:*)",
        "Bash(gh pr comment:*)",
        "Bash(gh pr merge:*)",
        "Bash(gh pr close:*)",
        "Bash(gh issue create:*)",
        "Bash(gh issue edit:*)",
        "Bash(gh issue close:*)",
        "Bash(gh issue comment:*)",
        "Bash(npm publish:*)",
        "Bash(pnpm publish:*)",
        "Bash(yarn publish:*)",
    ],
    "shell_code_exec": [
        "Bash(python:*)",
        "Bash(python3:*)",
        "Bash(node:*)",
        "Bash(deno:*)",
        "Bash(bash -c:*)",
        "Bash(sh -c:*)",
        "Bash(eval:*)",
        "Bash(ruby:*)",
        "Bash(perl:*)",
    ],
    "shell_package_install": [
        "Bash(npm install:*)",
        "Bash(npm i:*)",
        "Bash(pnpm install:*)",
        "Bash(pnpm add:*)",
        "Bash(yarn add:*)",
        "Bash(yarn install:*)",
        "Bash(pip install:*)",
        "Bash(pip3 install:*)",
        "Bash(uv add:*)",
        "Bash(uv pip install:*)",
        "Bash(brew install:*)",
        "Bash(apt install:*)",
        "Bash(apt-get install:*)",
        "Bash(cargo install:*)",
        "Bash(go install:*)",
    ],
    # ── Network categories ──────────────────────────────────────
    "network_read": [
        "WebFetch",
        "Bash(curl:*)",
        "Bash(wget:*)",
    ],
    "network_write": [
        "Bash(curl -X POST:*)",
        "Bash(curl -X PUT:*)",
        "Bash(curl -X DELETE:*)",
        "Bash(curl -X PATCH:*)",
        "Bash(curl --request POST:*)",
        "Bash(curl --request PUT:*)",
        "Bash(curl --request DELETE:*)",
        "Bash(gh api PATCH:*)",
        "Bash(gh api POST:*)",
        "Bash(gh api DELETE:*)",
        "Bash(gh api PUT:*)",
    ],
    # MCP tools — per-server trust is configured in Claude Code's user
    # settings (~/.claude/settings.json). The comfort-posture mcp_tools
    # category serves as the GLOBAL default; per-server overrides win.
    # Emit no rules for v0.1.0; document the gap in the skill.
    "mcp_tools": [],
}


def level_to_bucket(level: str) -> str:
    """Map a comfort-posture level to a permission-rule bucket.

    v0.1.0: 5 levels collapse to 3 buckets.
    v0.2.0: split each Bash category into safe/risky shapes so always-ask
    vs mostly-ask and mostly-allow vs autopilot become meaningfully different.
    """
    if level == "deny":
        return "deny"
    if level in ("always-ask", "mostly-ask"):
        return "ask"
    if level in ("mostly-allow", "autopilot"):
        return "allow"
    raise ValueError(f"Unknown level: {level!r}")


def parse_yaml(text: str) -> dict:
    """Parse the small, constrained comfort-posture YAML.

    Falls back to a minimal hand-rolled parser if PyYAML isn't installed.
    The YAML shape is: top-level keys, one nested 'categories:' block,
    no lists, no anchors, no flow style. Easy to parse without a library.
    """
    try:
        import yaml as pyyaml  # type: ignore
        return pyyaml.safe_load(text)
    except ImportError:
        return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text: str) -> dict:
    """Hand-rolled parser for the constrained comfort-posture shape only."""
    result: dict = {}
    current_section: dict | None = None
    section_indent = 0
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 0:
            if stripped.endswith(":"):
                key = stripped[:-1].strip()
                result[key] = {}
                current_section = result[key]
                section_indent = -1
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                result[k.strip()] = _coerce(v.strip())
                current_section = None
        else:
            if current_section is None:
                continue
            if section_indent == -1:
                section_indent = indent
            if indent != section_indent:
                continue
            if ":" in stripped:
                k, v = stripped.split(":", 1)
                current_section[k.strip()] = _coerce(v.strip())
    return result


def _coerce(v: str):
    if v.isdigit():
        return int(v)
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v.strip("'\"")


def compute_emission(posture: dict) -> dict[str, list[str]]:
    """Walk the posture YAML and emit a {bucket: [rules]} dict."""
    out: dict[str, list[str]] = {"allow": [], "ask": [], "deny": []}
    global_default = posture.get("global_default", "mostly-ask")
    categories = posture.get("categories", {}) or {}

    for cat, patterns in EMISSIONS.items():
        level = categories.get(cat, global_default)
        bucket = level_to_bucket(level)
        out[bucket].extend(patterns)

    # Dedup while preserving order
    for bucket in out:
        seen: set[str] = set()
        out[bucket] = [r for r in out[bucket] if not (r in seen or seen.add(r))]
    return out


def merge_into_settings(
    settings: dict,
    new_emission: dict[str, list[str]],
    prev_snapshot: dict[str, list[str]] | None,
) -> tuple[dict, dict[str, int]]:
    """Remove previous-snapshot rules from settings; add new emission.

    Returns the updated settings + a stats dict {bucket: net_delta}.
    """
    perms = settings.setdefault("permissions", {})
    stats = {}
    for bucket in ("allow", "ask", "deny"):
        current = list(perms.get(bucket, []))
        prev_rules = (prev_snapshot or {}).get(bucket, [])
        # Remove rules from previous snapshot
        without_prev = [r for r in current if r not in prev_rules]
        # Add new emission (dedup with what's already there)
        existing = set(without_prev)
        merged = without_prev + [r for r in new_emission[bucket] if r not in existing]
        perms[bucket] = merged
        stats[bucket] = len(merged) - len(current)
    return settings, stats


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project-root", help="Override project root detection. Default: search upward from CWD for .claude/ or .git/.")
    p.add_argument("--dry-run", action="store_true", help="Print what would change; don't write.")
    args = p.parse_args()

    root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    settings_path = root / ".claude" / "settings.json"
    snapshot_path = root / ".claude" / "_comfort-posture-snapshot.json"

    if not posture_path.is_file():
        print(f"ERROR: {posture_path} does not exist.", file=sys.stderr)
        print(
            "Open the dashboard (plugins/ravenclaude-core/dashboard.html) "
            "and click 'Save to repo' to create one.",
            file=sys.stderr,
        )
        return 1

    posture = parse_yaml(posture_path.read_text(encoding="utf-8"))
    schema_version = posture.get("schema_version")
    if schema_version != 3:
        print(
            f"WARNING: posture schema_version is {schema_version!r}, expected 3. "
            "Translation may be incomplete.",
            file=sys.stderr,
        )

    new_emission = compute_emission(posture)

    if settings_path.is_file():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        settings = {"$schema": "https://json.schemastore.org/claude-code-settings.json"}

    prev_snapshot = None
    if snapshot_path.is_file():
        try:
            prev_snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            prev_snapshot = None

    updated, stats = merge_into_settings(settings, new_emission, prev_snapshot)

    if args.dry_run:
        print("DRY RUN — would write:")
        print(f"  {settings_path}:")
        for bucket in ("allow", "ask", "deny"):
            count = len(updated.get("permissions", {}).get(bucket, []))
            delta = stats[bucket]
            sign = "+" if delta > 0 else ""
            print(f"    permissions.{bucket}: {count} rules ({sign}{delta})")
        print(f"\n  {snapshot_path}: snapshot of comfort-posture emission")
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        snapshot_path.write_text(
            json.dumps(new_emission, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Applied comfort posture to {settings_path.relative_to(root)}:")
        for bucket in ("allow", "ask", "deny"):
            count = len(updated["permissions"][bucket])
            emitted = len(new_emission[bucket])
            print(f"  permissions.{bucket}: {count} rules total ({emitted} from comfort-posture)")
        print(f"\n  Snapshot written: {snapshot_path.relative_to(root)}")

    # Session-mode warning footer
    print(
        "\nNote: comfort-posture works best with session mode at 'default'.\n"
        "  - Plan mode and Accept-edits compose fine.\n"
        "  - Auto-mode silently drops broad allow rules by design. The\n"
        "    rules this script emits are narrow, so most categories survive\n"
        "    auto-mode — but expect shell_code_exec and shell_package_install\n"
        "    to be partially overridden when auto-mode is on.\n"
        "  - bypassPermissions bypasses these rules entirely (use sparingly)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
