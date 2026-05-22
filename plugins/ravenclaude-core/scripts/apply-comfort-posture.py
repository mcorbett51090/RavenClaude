#!/usr/bin/env python3
"""
apply-comfort-posture.py — translate .ravenclaude/comfort-posture.yaml
into .claude/settings.json permission rules.

Read by the /set-posture slash command. Can also be invoked directly:

    python3 plugins/ravenclaude-core/scripts/apply-comfort-posture.py
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/apply-comfort-posture.py --dry-run

What it does (v0.17.0 — overwrite mode):
  1. Read .ravenclaude/comfort-posture.yaml from the consumer's project root.
  2. For each pattern in the EMISSIONS table, resolve its level using
     (per-pattern override > category default > global_default), then place
     the pattern in the deny/ask/allow bucket per level_to_bucket().
  3. Union the posture's `security_deny` list into the deny bucket.
  4. OVERWRITE permissions.allow/ask/deny in .claude/settings.json with the
     resolved emission. Non-posture fields ($schema, model, env, hooks) are
     left untouched.
  5. Delete any stale snapshot file from v0.16.0 (no longer used).
  6. Print a per-bucket count + the session-mode warning footer.

Design constraints:
  - **Narrow rules only.** Emit `Bash(git push:*)`, NOT `Bash(*)`. Auto-mode
    silently drops the broad shapes; narrow rules survive.
  - **Overwrite, not merge.** The posture YAML is the single source of truth
    for permissions.{allow,ask,deny}. Hand-edits to those buckets in
    settings.json are wiped on next /set-posture. Persist non-posture rules
    in .claude/settings.local.json instead — Claude Code merges that on top.
  - **Five levels collapse to three buckets** in v0.1.0:
      deny                        -> deny
      always-ask, mostly-ask      -> ask
      mostly-allow, autopilot     -> allow
    v0.2.0 will split each Bash category into safe/risky shapes so
    always-ask vs mostly-ask and mostly-allow vs autopilot become
    meaningfully different (the architect's "split for risky shapes"
    pattern from proposal 002 §5).
  - **Per-pattern overrides** (v0.17.0) let any single pattern in any
    category be set to a different level than its category default.
    See dashboard-schema.json `_category_value_shape` for the YAML shape.

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
# Each pattern is placed into deny/ask/allow based on the level resolved
# from (per-pattern override > category default > global_default).
# Patterns are NARROW by design — broad shapes like Bash(*) get silently
# dropped under auto-mode (verified in knowledge/claude-code-permissions.md
# "Permission modes" section).

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


# Baseline security deny rules used when posture lacks an explicit
# `security_deny` list (i.e., v3-shaped YAML reading into v4 script).
DEFAULT_SECURITY_DENY: list[str] = [
    "Bash(rm -rf:*)",
    "Bash(git push --force:*)",
    "Bash(git push -f:*)",
    "Bash(git reset --hard:*)",
    "Bash(git clean -fd:*)",
    "Bash(npm publish:*)",
    "Bash(pnpm publish:*)",
    "Bash(yarn publish:*)",
    "Bash(cargo publish:*)",
    "Bash(curl * | sh)",
    "Bash(curl * | bash)",
    "Bash(wget * | sh)",
    "Bash(wget * | bash)",
    "Read(.env)",
    "Read(.env.*)",
    "Read(**/*.pem)",
    "Read(**/*.key)",
    "Read(**/credentials*)",
    "Read(**/secrets*)",
]

VALID_LEVELS = {"deny", "always-ask", "mostly-ask", "mostly-allow", "autopilot"}


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
    """Parse the comfort-posture YAML.

    Falls back to a minimal hand-rolled parser if PyYAML isn't installed.
    """
    try:
        import yaml as pyyaml  # type: ignore
        return pyyaml.safe_load(text)
    except ImportError:
        return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text: str) -> dict:
    """Hand-rolled parser supporting the posture YAML shape.

    Supports:
      - top-level scalar key: value
      - top-level list: `- item` items
      - nested mapping (one level): `categories:` then indented `key: value`
      - nested mapping value as object: `category:` then indented `default:` /
        `overrides:` with further indented overrides keyed by quoted pattern.
    """
    result: dict = {}
    lines = [ln for ln in text.splitlines() if not (ln.strip().startswith("#"))]
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.split("#", 1)[0].rstrip()
        if not stripped.strip():
            i += 1
            continue
        indent = len(stripped) - len(stripped.lstrip())
        content = stripped.lstrip()
        if indent != 0:
            i += 1
            continue
        if content.endswith(":"):
            key = content[:-1].strip()
            block, consumed = _parse_block(lines, i + 1, base_indent=0)
            result[key] = block
            i += 1 + consumed
            continue
        if ":" in content:
            k, v = content.split(":", 1)
            result[k.strip()] = _coerce(v.strip())
            i += 1
            continue
        i += 1
    return result


def _parse_block(lines: list[str], start: int, base_indent: int):
    """Parse a nested block. Returns (parsed_value, lines_consumed).

    Detects whether the block is a list (starts with `- `) or a mapping.
    """
    if start >= len(lines):
        return {}, 0
    first = None
    for j in range(start, len(lines)):
        s = lines[j].split("#", 1)[0].rstrip()
        if not s.strip():
            continue
        first = s
        break
    if first is None:
        return {}, 0
    block_indent = len(first) - len(first.lstrip())
    if block_indent <= base_indent:
        return {}, 0
    if first.lstrip().startswith("- "):
        result_list: list = []
        consumed = 0
        for j in range(start, len(lines)):
            s = lines[j].split("#", 1)[0].rstrip()
            if not s.strip():
                consumed += 1
                continue
            ind = len(s) - len(s.lstrip())
            if ind < block_indent:
                break
            consumed += 1
            content = s.lstrip()
            if content.startswith("- "):
                result_list.append(_coerce(content[2:].strip()))
        return result_list, consumed
    result_map: dict = {}
    consumed = 0
    j = start
    while j < len(lines):
        s = lines[j].split("#", 1)[0].rstrip()
        if not s.strip():
            consumed += 1
            j += 1
            continue
        ind = len(s) - len(s.lstrip())
        if ind < block_indent:
            break
        if ind != block_indent:
            consumed += 1
            j += 1
            continue
        content = s.lstrip()
        if content.endswith(":"):
            key = content[:-1].strip().strip("'\"")
            sub, used = _parse_block(lines, j + 1, base_indent=block_indent)
            result_map[key] = sub
            consumed += 1 + used
            j += 1 + used
            continue
        if ":" in content:
            k, v = content.split(":", 1)
            result_map[k.strip().strip("'\"")] = _coerce(v.strip())
        consumed += 1
        j += 1
    return result_map, consumed


def _coerce(v: str):
    if v == "":
        return None
    if v.isdigit():
        return int(v)
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v.strip("'\"")


def resolve_category(cat_value, global_default: str) -> tuple[str, dict[str, str]]:
    """Return (category_default_level, overrides_map) for a category value.

    Accepts either:
      - a string (the level; no overrides)
      - an object {default: <level>, overrides: {<pattern>: <level>}}
      - None / missing (falls back to global_default)
    """
    if cat_value is None:
        return global_default, {}
    if isinstance(cat_value, str):
        if cat_value not in VALID_LEVELS:
            raise ValueError(f"Invalid level {cat_value!r}")
        return cat_value, {}
    if isinstance(cat_value, dict):
        default = cat_value.get("default", global_default)
        if default not in VALID_LEVELS:
            raise ValueError(f"Invalid category default {default!r}")
        overrides_raw = cat_value.get("overrides") or {}
        if not isinstance(overrides_raw, dict):
            raise ValueError(f"`overrides` must be a mapping, got {type(overrides_raw).__name__}")
        overrides: dict[str, str] = {}
        for pattern, lvl in overrides_raw.items():
            if lvl not in VALID_LEVELS:
                raise ValueError(f"Invalid level {lvl!r} for override {pattern!r}")
            overrides[pattern] = lvl
        return default, overrides
    raise ValueError(f"Category value must be string or object, got {type(cat_value).__name__}")


def compute_emission(posture: dict) -> dict[str, list[str]]:
    """Walk the posture YAML and emit a {bucket: [rules]} dict."""
    out: dict[str, list[str]] = {"allow": [], "ask": [], "deny": []}
    global_default = posture.get("global_default", "mostly-ask")
    categories = posture.get("categories", {}) or {}

    for cat, patterns in EMISSIONS.items():
        cat_default, overrides = resolve_category(categories.get(cat), global_default)
        for pattern in patterns:
            level = overrides.get(pattern, cat_default)
            bucket = level_to_bucket(level)
            out[bucket].append(pattern)

    security_deny = posture.get("security_deny")
    if security_deny is None:
        security_deny = list(DEFAULT_SECURITY_DENY)
    if not isinstance(security_deny, list):
        raise ValueError(f"`security_deny` must be a list, got {type(security_deny).__name__}")
    out["deny"].extend(security_deny)

    # Security-deny wins. A pattern emitted into allow/ask AND listed in
    # security_deny is removed from allow/ask so it appears only in the deny
    # bucket. (Claude Code's precedence is deny > ask > allow, so the rule is
    # functionally identical either way; this keeps settings.json visually clean.)
    deny_set = set(out["deny"])
    out["allow"] = [r for r in out["allow"] if r not in deny_set]
    out["ask"] = [r for r in out["ask"] if r not in deny_set]

    for bucket in out:
        seen: set[str] = set()
        out[bucket] = [r for r in out[bucket] if not (r in seen or seen.add(r))]
    return out


def overwrite_permissions(settings: dict, new_emission: dict[str, list[str]]) -> dict:
    """Replace settings['permissions'].{allow,ask,deny} with the new emission.

    Non-posture fields ($schema, model, env, hooks) are untouched.
    Any 'additionalDirectories' or other permission subkeys are preserved.
    """
    perms = settings.setdefault("permissions", {})
    for bucket in ("allow", "ask", "deny"):
        perms[bucket] = list(new_emission[bucket])
    return settings


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project-root", help="Override project root detection. Default: search upward from CWD for .claude/ or .git/.")
    p.add_argument("--dry-run", action="store_true", help="Print what would change; don't write.")
    args = p.parse_args()

    root = Path(args.project_root) if args.project_root else find_project_root(Path.cwd())
    posture_path = root / ".ravenclaude" / "comfort-posture.yaml"
    settings_path = root / ".claude" / "settings.json"
    stale_snapshot = root / ".claude" / "_comfort-posture-snapshot.json"

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
    if schema_version not in (3, 4):
        print(
            f"WARNING: posture schema_version is {schema_version!r}, expected 3 or 4. "
            "Translation may be incomplete.",
            file=sys.stderr,
        )

    new_emission = compute_emission(posture)

    if settings_path.is_file():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        settings = {"$schema": "https://json.schemastore.org/claude-code-settings.json"}

    prev_perms = settings.get("permissions", {})
    prev_counts = {b: len(prev_perms.get(b, [])) for b in ("allow", "ask", "deny")}

    updated = overwrite_permissions(settings, new_emission)
    new_counts = {b: len(updated["permissions"][b]) for b in ("allow", "ask", "deny")}

    if args.dry_run:
        print("DRY RUN — would overwrite permissions buckets:")
        print(f"  {settings_path}:")
        for bucket in ("allow", "ask", "deny"):
            delta = new_counts[bucket] - prev_counts[bucket]
            sign = "+" if delta > 0 else ""
            print(f"    permissions.{bucket}: {prev_counts[bucket]} -> {new_counts[bucket]} ({sign}{delta})")
        if stale_snapshot.is_file():
            print(f"  Would delete stale snapshot: {stale_snapshot.relative_to(root)}")
    else:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(updated, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if stale_snapshot.is_file():
            stale_snapshot.unlink()
            print(f"Deleted stale snapshot: {stale_snapshot.relative_to(root)}")
        print(f"Applied comfort posture to {settings_path.relative_to(root)}:")
        for bucket in ("allow", "ask", "deny"):
            delta = new_counts[bucket] - prev_counts[bucket]
            sign = "+" if delta > 0 else ""
            print(f"  permissions.{bucket}: {prev_counts[bucket]} -> {new_counts[bucket]} ({sign}{delta})")

    print(
        "\nNote: comfort-posture works best with session mode at 'default'.\n"
        "  - Plan mode and Accept-edits compose fine.\n"
        "  - Auto-mode silently drops broad allow rules by design. The\n"
        "    rules this script emits are narrow, so most categories survive\n"
        "    auto-mode — but expect shell_code_exec and shell_package_install\n"
        "    to be partially overridden when auto-mode is on.\n"
        "  - bypassPermissions bypasses these rules entirely (use sparingly).\n"
        "\nHand-edits to permissions.allow/ask/deny are wiped on next /set-posture.\n"
        "Put personal overrides in .claude/settings.local.json instead — Claude\n"
        "Code merges that on top of this file."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
