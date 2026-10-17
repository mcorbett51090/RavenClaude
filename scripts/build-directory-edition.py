#!/usr/bin/env python3
"""build-directory-edition.py - build the Anthropic-Directory edition of a plugin from the source plugin.

WHY
    ravenclaude-core cannot be submitted to the Directory as it is: 1,871 files (limit is 512 before a
    reviewer hold), an 11 MB dashboard (hard block at 5 MiB), 57 registered hooks several of which are
    always on, `bin/` that edits shell rc files, and an `experimental` key that must not declare
    components. This builds a SMALLER, REVIEWABLE edition from the same source - one source of truth,
    not a fork - by copying files UNMODIFIED and applying a short, fixed transform list.

    The set of files that ships is a human-reviewed manifest (docs/directory-edition/<name>/manifest.json):
    every agent, skill, command and hook is allow-listed with a REASON. Everything those reference is
    pulled in by closure; anything they reference that the manifest denies is a build failure, not a
    silent dangling reference.

TRANSFORMS (the whole list)
    plugin.json          rebuilt from the source one: `experimental` dropped, homepage/repository set,
                         description replaced, version kept equal to the source (the single source of truth)
    hooks/hooks.json     filtered to the allow-listed hooks, each wrapped in hooks/posture-gate.sh
    commands overrides   a command the manifest overrides is replaced by the override file
    allowed-tools        removed from every shipped command and skill (see strip_frontmatter_keys): the
                         field pre-approves tools while the component runs, and these components read
                         untrusted repositories and web pages
    plugin paths         `plugins/<plugin>/` in shipped markdown becomes ${CLAUDE_PLUGIN_ROOT}/ (Claude Code
                         substitutes it inline in skill/command/agent content; the Bash tool's environment
                         does NOT carry it, so a project-relative path would run the PROJECT's file)
    README / PRIVACY / LICENSE / .claude-plugin/marketplace.json   generated from templates
    hooks/posture-gate.sh, scripts/edition-trust.sh                generated (the on/off switch and its helper)

USAGE
    build-directory-edition.py --out DIR            build the edition into DIR (must not exist or be empty)
    build-directory-edition.py --check              build twice -> identical; file list matches the committed list
    build-directory-edition.py --report             print limits, closure and network report for a fresh build
    build-directory-edition.py --write-file-list    refresh the committed file list
    build-directory-edition.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "docs" / "directory-edition" / "ravenclaude-core" / "manifest.json"

TEXT_EXT = {
    ".md",
    ".sh",
    ".py",
    ".json",
    ".js",
    ".mjs",
    ".yaml",
    ".yml",
    ".txt",
    ".html",
    ".css",
    ".toml",
}
EXEC_EXT = {".sh", ".py", ".js", ".mjs"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}
REF_DIRS = (
    "hooks",
    "scripts",
    "knowledge",
    "templates",
    "rules",
    "skills",
    "agents",
    "commands",
    "schemas",
    "scenarios",
    "best-practices",
    # directories the edition denies: a reference INTO one of these must be seen, not missed
    "bin",
    "monitors",
    "dashboard-assets",
    "copilot",
    "codex",
    "vscode-extension",
)
_REF_DIR = re.compile(
    r"(?<![\w.-])((?:\.\./)*(?:" + "|".join(REF_DIRS) + r")/[\w.@+-]+(?:/[\w.@+-]+)*)"
)
_REF_SIB = re.compile(r"/([\w-]+\.(?:sh|py|js|mjs|json))\b")
_NEVER_COPY = ("__pycache__", ".DS_Store", "node_modules", ".pytest_cache")

GATE_PATH = "hooks/posture-gate.sh"
GATE_PREFIX = 'bash "${CLAUDE_PLUGIN_ROOT}/hooks/posture-gate.sh" '
TRUST_PATH = "scripts/edition-trust.sh"
TRUST_FILE = "~/.ravenclaude/edition-trusted-projects"

# The edition's single on/off switch. Every shipped hook except the one-line setup prompt is invoked
# THROUGH this file, so "does nothing until you opt in" is true by construction: the wrapped hook never
# starts. A posture file alone is NOT an opt-in - a repository you clone can ship one - so the hooks also
# need YOUR entry in a file under your home directory, which no repository can write, bound to the CONTENT of
# the project files the hooks read, so an update that changes them switches the hooks off until you look again.
# Kept short on purpose - a reviewer should be able to read all of it.
POSTURE_GATE_SH = """#!/usr/bin/env bash
# posture-gate.sh - the on/off switch for this plugin's hooks.
#
# hooks.json invokes every hook as:  bash posture-gate.sh <the hook command...>
# The wrapped hook runs ONLY when all of these are true:
#   1. the project has .ravenclaude/comfort-posture.yaml (a regular file), AND
#   2. nothing under .ravenclaude/ is a symbolic link, at any depth, and every directory there can be
#      read: a repository can ship a link, and the hooks write there, so a link could send a write outside
#      the project. runaway-brake.sh writes .ravenclaude/runs/thing/runaway/<session_id> and a .lock beside
#      it. find counts .ravenclaude as depth 0, so that file is depth 4 and a bound of 3 never sees it.
#      find reports every link and does not stop at a depth bound. A directory the check cannot list
#      could be hiding one, and find's own errors refuse too (fail closed). AND
#   3. YOU trusted the project AS IT NOW IS: ~/.ravenclaude/edition-trusted-projects holds the line
#      "<real project path><TAB><sha256>" and the digest still matches the three files the hooks read from the
#      project (the posture, .repo-layout.json, .ravenclaude/task-scope.json; each at most 1 MiB). Change one
#      and the hooks go off again until you trust the project again.
# Condition 3 exists because 1 and 2 are only files, and a repository you clone or update can ship any file.
# Otherwise this exits 0 at once: no output, no files written, no network, the hook never starts.
#
#   posture-gate.sh --status [detail]   prints one word, exits 0:  no-posture | untrusted | changed | active
#   posture-gate.sh --line              prints this project's trust line (exit 1 and a reason on stderr if none)
#
# It reads no VALUE from the posture file and fails toward doing nothing.
tab="$(printf '\\t')"
nl="$(printf '\\n_')"; nl="${nl%_}"
rc_sha() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 | cut -d' ' -f1
  fi
}
rc_line() {
  why=""; real=""; digest=""
  proj="${CLAUDE_PROJECT_DIR:-$PWD}"
  [ -f "$proj/.ravenclaude/comfort-posture.yaml" ] || { why=no-posture; return 1; }
  real="$(CDPATH= cd -P -- "$proj" 2>/dev/null && pwd -P)" || { why=path; return 1; }
  case "$real" in ""|*"$nl"*|*"$tab"*) why=path; return 1 ;; esac
  if [ "${1:-}" = quick ]; then
    # a project nobody trusted costs one grep, not a hash of its files
    if [ -z "${HOME:-}" ] || ! grep -Fq -- "$real$tab" "$HOME/.ravenclaude/edition-trusted-projects" 2>/dev/null; then
      why=untrusted; return 1
    fi
  fi
  links="$(find "$proj/.ravenclaude" -type l -print 2>&1)"; found=$?
  if [ -L "$proj/.ravenclaude" ] || [ "$found" -ne 0 ] || [ -n "$links" ]; then
    why=symlink; return 1
  fi
  listing=""
  for f in .ravenclaude/comfort-posture.yaml .repo-layout.json .ravenclaude/task-scope.json; do
    if [ -f "$proj/$f" ]; then
      sz="$(wc -c < "$proj/$f" 2>/dev/null | tr -d ' ')"
      case "$sz" in ""|*[!0-9]*) why=size; return 1 ;; esac
      [ "$sz" -le 1048576 ] || { why=size; return 1; }
      h="$(rc_sha < "$proj/$f")"
    else
      h=absent
    fi
    [ -n "$h" ] || { why=nosha; return 1; }
    listing="$listing$f $h$nl"
  done
  digest="$(printf '%s' "$listing" | rc_sha)"
  [ "${#digest}" -eq 64 ] || { why=nosha; return 1; }
  return 0
}
rc_state() {
  rc_line quick || { if [ "$why" = no-posture ]; then echo no-posture; else echo untrusted; fi; return; }
  [ -n "${HOME:-}" ] || { echo untrusted; return; }
  tf="$HOME/.ravenclaude/edition-trusted-projects"
  if grep -Fxq -- "$real$tab$digest" "$tf" 2>/dev/null; then echo active; return; fi
  if [ "${1:-}" = detail ] && REAL="$real" awk -F'\\t' '$1 == ENVIRON["REAL"] { f = 1 } END { exit !f }' "$tf" 2>/dev/null; then
    echo changed; return
  fi
  echo untrusted
}
case "${1:-}" in
  "") exit 0 ;;
  --status) rc_state "${2:-}"; exit 0 ;;
  --line)
    if rc_line; then printf '%s\\t%s\\n' "$real" "$digest"; exit 0; fi
    echo "$why" >&2; exit 1 ;;
esac
[ "$(rc_state)" = active ] || exit 0
exec "$@"
"""

# The helper that records your trust. It writes ONE file, ~/.ravenclaude/edition-trusted-projects, and
# nothing else; it refuses a project the gate would refuse, so trust is never granted to nothing.
EDITION_TRUST_SH = """#!/usr/bin/env bash
# edition-trust.sh - trust (or stop trusting) a project for this plugin's hooks.
#
#   edition-trust.sh add    [DIR]   trust DIR as it is now (default: the current directory)
#   edition-trust.sh remove [DIR]   stop trusting DIR
#   edition-trust.sh status [DIR]   print: trusted | changed | not-trusted | no-posture
#   edition-trust.sh list           print every trusted project
#
# The ONLY file this writes is ~/.ravenclaude/edition-trusted-projects, one line per project:
# "<real path><TAB><sha256 of the posture, .repo-layout.json and .ravenclaude/task-scope.json>". The line comes
# from hooks/posture-gate.sh itself (--line), so the helper and the gate cannot disagree about it. After you
# review a change to those files, run `add` again. `add` refuses a project with no regular
# .ravenclaude/comfort-posture.yaml, with a symbolic link (or an unreadable directory) under .ravenclaude/,
# with a newline or tab in its path, or with one of those files over 1 MiB. Pass the project root explicitly:
# the default, the current directory, may be a subdirectory. No network, no other writes.
set -eu
usage() { echo "usage: edition-trust.sh add|remove|status [DIR] | list" >&2; exit 2; }
cmd="${1:-}"
[ -n "$cmd" ] || usage
shift || true
[ -n "${HOME:-}" ] || { echo "edition-trust: HOME is not set" >&2; exit 2; }
file="$HOME/.ravenclaude/edition-trusted-projects"
if [ "$cmd" = list ]; then
  [ -f "$file" ] && cat "$file"
  exit 0
fi
here="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
gate="$here/../hooks/posture-gate.sh"
[ -f "$gate" ] || { echo "edition-trust: cannot find $gate" >&2; exit 2; }
dir="${1:-$PWD}"
real="$(CDPATH= cd -P -- "$dir" 2>/dev/null && pwd -P)" || { echo "edition-trust: not a directory: $dir" >&2; exit 2; }
listed() { [ -f "$file" ] && REAL="$real" awk -F'\\t' '$1 == ENVIRON["REAL"] { f = 1 } END { exit !f }' "$file"; }
case "$cmd" in
  status)
    case "$(CLAUDE_PROJECT_DIR="$real" bash "$gate" --status detail 2>/dev/null || true)" in
      active) echo trusted ;;
      changed) echo changed ;;
      no-posture) echo no-posture ;;
      *) echo not-trusted ;;
    esac
    ;;
  add)
    line="$(CLAUDE_PROJECT_DIR="$real" bash "$gate" --line 2>/dev/null)" || {
      why="$(CLAUDE_PROJECT_DIR="$real" bash "$gate" --line 2>&1 >/dev/null || true)"
      case "$why" in
        no-posture) msg="has no regular .ravenclaude/comfort-posture.yaml - save a posture first (/dashboard)" ;;
        symlink) msg="has a symbolic link, or a directory it cannot read, under .ravenclaude/ - fix that first" ;;
        size) msg="has a posture, .repo-layout.json or task-scope.json file over 1 MiB" ;;
        path) msg="has a newline or tab in its path" ;;
        *) msg="could not be fingerprinted (it needs sha256sum or shasum)" ;;
      esac
      echo "edition-trust: $real $msg" >&2
      exit 2
    }
    if [ -f "$file" ] && grep -Fxq -- "$line" "$file"; then echo "already trusted: $real"; exit 0; fi
    mkdir -p "$HOME/.ravenclaude"
    tmp="$(mktemp "$file.XXXXXX")"
    if [ -f "$file" ]; then REAL="$real" awk -F'\\t' '$1 != ENVIRON["REAL"]' "$file" > "$tmp" || true; fi
    printf '%s\\n' "$line" >> "$tmp"
    mv "$tmp" "$file"
    echo "trusted: $real  (recorded in $file with a fingerprint of the files the hooks read; run this again after you change them)"
    ;;
  remove)
    if ! listed; then echo "not trusted: $real"; exit 0; fi
    tmp="$(mktemp "$file.XXXXXX")"
    REAL="$real" awk -F'\\t' '$1 != ENVIRON["REAL"]' "$file" > "$tmp" || true
    mv "$tmp" "$file"
    echo "no longer trusted: $real"
    ;;
  *) usage ;;
esac
"""

# A hook command may take exactly one of two shapes (optionally followed by the injected file path). Anything
# else - a `;`, a `&&`, a pipe, a variable in the program position - is a build failure, because the gate
# wraps the command string verbatim and only a command this simple is certain to run entirely inside it.
HOOK_CMD_FORM = re.compile(
    r'^(?:bash )?"\$\{CLAUDE_PLUGIN_ROOT\}/(?!\S*\.\.)[A-Za-z0-9_./-]+"(?: "\$CLAUDE_TOOL_FILE_PATH")?$'
)
# Only these hooks may skip the gate, whatever a manifest says: they print one fixed line and do nothing else.
UNGATED_ALLOWED = frozenset({"dashboard-prompt.sh"})
# Frontmatter keys removed from shipped commands and skills (see strip_frontmatter_keys).
STRIPPED_KEYS = ("allowed-tools", "allowed_tools", "allowedTools")
# Frontmatter keys removed from shipped AGENTS. `memory: project` loads .claude/agent-memory/<agent>/MEMORY.md
# from the PROJECT into the agent's system prompt and gives it Write/Edit to maintain it - a repository can
# ship that file, so an agent would read a stranger's text as its own standing instructions.
AGENT_STRIPPED_KEYS = ("memory",)


class BuildError(Exception):
    """A build precondition failed. Always carries an actionable message."""


# ── glob helpers ─────────────────────────────────────────────────────────────


def _glob_re(pattern: str) -> re.Pattern[str]:
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out += r"(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += r".*"
            i += 2
        elif c == "*":
            out += r"[^/]*"
            i += 1
        elif c == "?":
            out += r"[^/]"
            i += 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile("^" + out + "$")


def glob_match(path: str, pattern: str) -> bool:
    return _glob_re(pattern).match(path) is not None


# ── manifest ────────────────────────────────────────────────────────────────


def load_manifest(path: Path) -> dict:
    m = json.loads(path.read_text())
    m["_dir"] = str(path.resolve().parent)  # templates/ and overrides/ are relative to the manifest
    problems = validate_manifest(m)
    if problems:
        raise BuildError("manifest invalid:\n  - " + "\n  - ".join(problems))
    return m


def validate_manifest(m: dict) -> list[str]:
    p: list[str] = []
    for k in (
        "schema_version",
        "plugin",
        "source_plugin_dir",
        "target",
        "plugin_json",
        "limits",
        "components",
        "deny_globs",
    ):
        if k not in m:
            p.append(f"missing key: {k}")
    comps = m.get("components", {})
    for kind in ("agents", "skills", "commands", "hooks"):
        if kind not in comps:
            p.append(f"components.{kind} missing")
            continue
        seen = set()
        for i, e in enumerate(comps[kind]):
            key = e.get("id") if kind == "hooks" else e.get("name")
            if not key:
                p.append(f"components.{kind}[{i}] has no {'id' if kind == 'hooks' else 'name'}")
                continue
            if key in seen:
                p.append(f"components.{kind}: duplicate {key}")
            seen.add(key)
            if not str(e.get("reason", "")).strip():
                p.append(
                    f"components.{kind}.{key}: a REASON is required (the manifest is the review record)"
                )
            if kind == "hooks" and not str(e.get("summary", "")).strip():
                p.append(f"components.hooks.{key}: a README summary is required")
            if (
                kind == "hooks"
                and e.get("ungated")
                and not str(e.get("ungated_reason", "")).strip()
            ):
                p.append(f"components.hooks.{key}: ungated needs an ungated_reason")
            if kind == "hooks" and e.get("ungated") and key not in UNGATED_ALLOWED:
                p.append(
                    f"components.hooks.{key}: only {sorted(UNGATED_ALLOWED)} may be ungated - "
                    "that list is in the builder, not the manifest, so a manifest edit cannot widen it"
                )
    for i, e in enumerate(m.get("extra_roots", [])):
        if not e.get("glob") or not str(e.get("reason", "")).strip():
            p.append(f"extra_roots[{i}] needs glob and reason")
    for i, e in enumerate(m.get("text_edits", [])):
        for k in ("file", "find", "replace", "reason"):
            if k not in e or (k != "replace" and not str(e[k]).strip()):
                p.append(f"text_edits[{i}] needs {k}")
    for key in ("python_isolation_allow", "runnable_path_allow"):
        for i, e in enumerate(m.get(key, [])):
            if not e.get("file") or not str(e.get("reason", "")).strip():
                p.append(f"{key}[{i}] needs file and reason")
    for i, d in enumerate(m.get("deny_globs", [])):
        if not d.get("glob") or not str(d.get("reason", "")).strip():
            p.append(f"deny_globs[{i}] needs glob and reason")
    return p


# ── source scanning ─────────────────────────────────────────────────────────


def list_source(src: Path) -> list[str]:
    out = []
    for dirpath, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in _NEVER_COPY)
        for f in sorted(files):
            if f in _NEVER_COPY or f.endswith(".pyc"):
                continue
            out.append(os.path.relpath(os.path.join(dirpath, f), src).replace(os.sep, "/"))
    return out


def denied_by(path: str, deny: list[dict], roots: frozenset[str] = frozenset()) -> dict | None:
    """First deny entry that matches. A manifest ROOT is an explicit decision and is never denied by a glob;
    an entry may carry `except` globs for the files a broad deny deliberately lets through."""
    if path in roots:
        return None
    for d in deny:
        if glob_match(path, d["glob"]) and not any(
            glob_match(path, e) for e in d.get("except", [])
        ):
            return d
    return None


def _scannable(text: str, rel: str) -> str:
    """Executable files: drop whole-line comments, which are the dominant source of false references."""
    suffix = Path(rel).suffix
    if suffix in (".sh", ".py"):
        return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    if suffix in (".js", ".mjs"):
        return "\n".join(
            l for l in text.splitlines() if not l.lstrip().startswith(("//", "*", "/*"))
        )
    return text


def references(rel: str, text: str, plugin_name: str, exists) -> tuple[set[str], set[str]]:
    """Return (resolved plugin-relative file refs, unresolved-but-denial-checkable refs)."""
    body = _scannable(text, rel)
    here = str(Path(rel).parent).replace("\\", "/")
    here = "" if here == "." else here
    found: set[str] = set()
    cands: list[str] = []
    for m in _REF_DIR.finditer(body):
        cands.append(m.group(1).rstrip(".,;:)"))
    is_exec = Path(rel).suffix in EXEC_EXT or rel.endswith("hooks.json")
    if is_exec:
        for m in _REF_SIB.finditer(body):
            name = m.group(1)
            for base in (here, "hooks", "scripts", "knowledge", "templates"):
                cands.append(f"{base}/{name}" if base else name)
    for c in cands:
        options = []
        if c.startswith("../"):
            options.append(os.path.normpath(os.path.join(here, c)).replace(os.sep, "/"))
        else:
            options.append(c)
            if here:
                options.append(os.path.normpath(os.path.join(here, c)).replace(os.sep, "/"))
            prefix = f"plugins/{plugin_name}/"
            if c.startswith(prefix):
                options.append(c[len(prefix) :])
        for o in options:
            if not o.startswith("..") and exists(o):
                found.add(o)
                break
    return found, set()


def hook_script_paths(command: str) -> list[str]:
    return list(re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([\w./-]+)", command))


def registrations(hooks_json: dict) -> list[tuple[str, str | None, dict]]:
    rows = []
    for event, groups in hooks_json.get("hooks", hooks_json).items():
        for g in groups:
            for h in g.get("hooks", []):
                rows.append((event, g.get("matcher"), h))
    return rows


def hook_id(command: str) -> str:
    """Script basename plus its trailing args (same rule as directory-edition-hook-audit.py), ignoring the
    posture-gate prefix and the injected file-path argument."""
    paths = [
        m
        for m in re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([\w./-]+)", command)
        if m != "hooks/posture-gate.sh"
    ]
    if not paths:
        return command.strip()
    script = paths[0]
    tail = command.split(script, 1)[1]
    args = [a for a in re.findall(r"[^\s\"']+", tail) if "CLAUDE_TOOL_FILE_PATH" not in a]
    return Path(script).name + ((" " + " ".join(args)) if args else "")


# ── the build ───────────────────────────────────────────────────────────────


class Plan:
    """Everything decided before a byte is written, so --report and the gate share one truth."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}  # dist path -> "copy:<src rel>" | "gen:<name>"
        self.closure_breaks: list[tuple[str, str, str]] = []  # (from, to, why)  executable surface
        self.prose_denied: list[tuple[str, str, str]] = []  # informational
        self.generated: dict[str, str] = {}  # dist path -> text
        self.hook_rows: list[dict] = []
        self.via: dict[str, str] = {}  # file -> first referrer (why it is in the closure)


def plan_build(manifest: dict, repo: Path = REPO, overrides_root: Path | None = None) -> Plan:
    src = repo / manifest["source_plugin_dir"]
    name = manifest["plugin"]
    deny = manifest["deny_globs"]
    comps = manifest["components"]
    allow_break = manifest.get("closure_allow", [])
    prose_depth = int(manifest.get("closure", {}).get("prose_depth", 1))
    overrides = {k: (Path(manifest["_dir"]) / v) for k, v in manifest.get("overrides", {}).items()}
    all_src = set(list_source(src))
    plan = Plan()

    def exists(p: str) -> bool:
        return p in all_src or p in overrides

    def read(p: str) -> str:
        if p in overrides:
            return overrides[p].read_text()
        return (src / p).read_text(errors="replace")

    roots: list[str] = []
    for a in comps["agents"]:
        roots.append(f"agents/{a['name']}.md")
    for c in comps["commands"]:
        roots.append(f"commands/{c['name']}.md")
    for s in comps["skills"]:
        prefix = f"skills/{s['name']}/"
        got = [p for p in all_src if p.startswith(prefix)]
        if not got:
            raise BuildError(f"skill {s['name']}: no files under {prefix}")
        roots += sorted(got)
    for er in manifest.get("extra_roots", []):
        got = sorted(p for p in all_src if glob_match(p, er["glob"]))
        if not got:
            raise BuildError(f"extra_roots {er['glob']} matches no source file")
        roots += got
    hooks_json = json.loads((src / "hooks" / "hooks.json").read_text())
    want = {h["id"] for h in comps["hooks"]}
    seen_ids = set()
    kept = []
    for event, matcher, h in registrations(hooks_json):
        hid = hook_id(h["command"])
        if hid in want:
            if not HOOK_CMD_FORM.match(h["command"]):
                raise BuildError(
                    f"{event}: hook {hid} has a command the gate cannot be certain to contain: "
                    f'{h["command"]!r}. Allowed forms: [bash ]"${{CLAUDE_PLUGIN_ROOT}}/<path>" '
                    'optionally followed by "$CLAUDE_TOOL_FILE_PATH" (no `;`, `&&`, pipes or variables).'
                )
            seen_ids.add(hid)
            kept.append((event, matcher, h))
            roots += hook_script_paths(h["command"])
            plan.hook_rows.append({"id": hid, "event": event, "matcher": matcher or "*"})
    missing = want - seen_ids
    if missing:
        raise BuildError(
            "manifest hooks not registered in the source hooks.json: " + ", ".join(sorted(missing))
        )

    root_set = frozenset(roots)
    # BFS closure. budget: exec surfaces propagate fully; prose surfaces stop after prose_depth hops.
    included: dict[str, int] = {}
    queue: list[tuple[str, int, str]] = [(r, prose_depth, "<root>") for r in roots]
    while queue:
        rel, budget, frm = queue.pop(0)
        if rel in included and included[rel] >= budget:
            continue
        d = denied_by(rel, deny, root_set)
        if d is None and rel not in root_set:
            # A skill, agent or command ships ONLY through the manifest, never because some prose mentions it.
            parts = rel.split("/")
            if parts[0] in ("skills", "agents", "commands") and len(parts) > 1:
                d = {
                    "glob": f"{parts[0]}/** (not allow-listed)",
                    "reason": f"{parts[0]} ship only through the manifest allow-list",
                }
        if d:
            is_exec_src = frm != "<root>" and (
                Path(frm).suffix in EXEC_EXT or frm.endswith("hooks.json")
            )
            if frm == "<root>":
                raise BuildError(
                    f"{rel} is a manifest root but is denied by {d['glob']} ({d['reason']})"
                )
            allowed = any(
                glob_match(frm, a["from"]) and glob_match(rel, a["to"]) for a in allow_break
            )
            if is_exec_src and not allowed:
                plan.closure_breaks.append((frm, rel, d["reason"]))
            elif not is_exec_src:
                plan.prose_denied.append((frm, rel, d["reason"]))
            continue
        if not exists(rel):
            raise BuildError(f"{rel} (from {frm}) does not exist in the source plugin")
        included[rel] = max(included.get(rel, -1), budget)
        plan.via.setdefault(rel, frm)
        if Path(rel).suffix not in TEXT_EXT:
            continue
        is_exec = Path(rel).suffix in EXEC_EXT
        if not is_exec and budget <= 0 and frm != "<root>":
            continue
        refs, _ = references(rel, read(rel), name, exists)
        nb = prose_depth if is_exec else budget - 1
        for r in sorted(refs):
            if r != rel:
                queue.append((r, nb if is_exec else max(nb, 0) if budget > 0 else -1, rel))
    for rel in sorted(included):
        plan.files[rel] = "override:" + rel if rel in overrides else "copy:" + rel

    # generated files
    sp = json.loads((src / ".claude-plugin" / "plugin.json").read_text())
    pj = {
        "name": sp["name"],
        "displayName": manifest["plugin_json"].get(
            "displayName", sp.get("displayName", sp["name"])
        ),
        "description": manifest["plugin_json"]["description"],
        "version": sp["version"],
        "author": sp.get("author", {}),
        "homepage": manifest["target"]["homepage"],
        "repository": manifest["target"]["repository"],
        "license": sp.get("license", "MIT"),
        "keywords": manifest["plugin_json"].get("keywords", sp.get("keywords", [])),
    }
    plan.generated[".claude-plugin/plugin.json"] = (
        json.dumps(pj, indent=2, ensure_ascii=False) + "\n"
    )
    mk = {
        "name": manifest["target"]["marketplace_name"],
        "description": pj["description"],  # `claude plugin validate --strict` warns without one
        "owner": sp.get("author", {}),
        "plugins": [
            {
                "name": sp["name"],
                "source": "./",
                "description": pj["description"],
                "version": sp["version"],
            }
        ],
    }
    plan.generated[".claude-plugin/marketplace.json"] = (
        json.dumps(mk, indent=2, ensure_ascii=False) + "\n"
    )
    filtered: dict = {k: v for k, v in hooks_json.items() if k != "hooks"}
    filtered["hooks"] = {}
    ungated = {h["id"]: bool(h.get("ungated")) for h in comps["hooks"]}
    for event, groups in hooks_json["hooks"].items():
        ngroups = []
        for g in groups:
            hs = []
            for h in g.get("hooks", []):
                hid = hook_id(h["command"])
                if hid not in want:
                    continue
                h2 = dict(h)
                if not ungated[hid]:
                    h2["command"] = GATE_PREFIX + h["command"]
                hs.append(h2)
            if hs:
                ng = dict(g)
                ng["hooks"] = hs
                ngroups.append(ng)
        if ngroups:
            filtered["hooks"][event] = ngroups
    plan.generated["hooks/hooks.json"] = json.dumps(filtered, indent=2, ensure_ascii=False) + "\n"
    plan.generated[GATE_PATH] = POSTURE_GATE_SH
    plan.generated[TRUST_PATH] = EDITION_TRUST_SH
    plan.files.pop("hooks/hooks.json", None)
    for gp in plan.generated:
        plan.files[gp] = "gen:" + gp
    return plan


def render_templates(manifest: dict, plan: Plan, repo: Path = REPO) -> dict[str, str]:
    """README / PRIVACY / LICENSE from templates; tables are generated so parity is by construction."""
    tdir = Path(manifest["_dir"]) / "templates"
    version = json.loads(plan.generated[".claude-plugin/plugin.json"])["version"]
    comps = manifest["components"]
    hook_rows = []
    by_id: dict[str, list[dict]] = {}
    for r in plan.hook_rows:
        by_id.setdefault(r["id"], []).append(r)
    for h in comps["hooks"]:
        evs = "<br>".join(
            f"`{r['event']}`" + (f" `{r['matcher']}`" if r["matcher"] != "*" else "")
            for r in by_id.get(h["id"], [])
        )
        hook_rows.append(f"| `{h['id']}` | {evs} | {h['summary']} |")
    hook_table = (
        "| Hook | Fires on | What it does (only once a posture file exists and you have trusted the project, unless stated) |\n|---|---|---|\n"
        + "\n".join(hook_rows)
    )
    lists = {
        "AGENT_LIST": "\n".join(f"- `{a['name']}` - {a['reason']}" for a in comps["agents"]),
        "SKILL_LIST": "\n".join(f"- `{s['name']}` - {s['reason']}" for s in comps["skills"]),
        "COMMAND_LIST": "\n".join(f"- `/{c['name']}` - {c['reason']}" for c in comps["commands"]),
        "HOOK_TABLE": hook_table,
        "VERSION": version,
        "EXEC_LIST": ", ".join(
            f"`{x}`" for x in sorted(manifest.get("hook_audit", {}).get("allowed_execs", []))
        ),
        "N_AGENTS": str(len(comps["agents"])),
        "N_SKILLS": str(len(comps["skills"])),
        "N_COMMANDS": str(len(comps["commands"])),
        "N_HOOKS": str(len(comps["hooks"])),
        "N_GATED_HOOKS": str(sum(1 for h in comps["hooks"] if not h.get("ungated"))),
        "N_FILES": str(len(set(plan.files) | {"README.md", "PRIVACY.md", "LICENSE"})),
        "REPO": manifest["target"]["repository"],
        "HOMEPAGE": manifest["target"]["homepage"],
        "PORTAL": manifest["target"]["portal_url"],
        "SUPPORT": manifest["target"]["support"],
    }
    out = {}
    for fname in ("README.md", "PRIVACY.md", "LICENSE"):
        t = (repo / "LICENSE").read_text() if fname == "LICENSE" else (tdir / fname).read_text()
        for k, v in lists.items():
            t = t.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{[A-Z_]+\}\}", t)
        if left:
            raise BuildError(f"{fname}: unresolved placeholders {sorted(set(left))}")
        out[fname] = t
    return out


def fill_placeholders(text: str, manifest: dict) -> str:
    """The few manifest values an override file may use."""
    tgt = manifest["target"]
    for k, v in (
        ("PORTAL", tgt["portal_url"]),
        ("REPO", tgt["repository"]),
        ("SUPPORT", tgt["support"]),
    ):
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        raise BuildError(f"override has unresolved placeholders {sorted(set(left))}")
    return text


# ── text transforms (the whole list; see the module docstring) ──────────────

# Markdown the transforms touch: instructions Claude reads and may act on. templates/ is excluded on purpose -
# those files are scaffolds for the USER's repo, where `scripts/...` means the user's own scripts.
_TRANSFORM_DIRS = ("commands/", "skills/", "agents/", "rules/", "knowledge/")
# An interpreter run on a plugin-relative script: `python3 scripts/x.py`, `bash ./hooks/y.sh`.
RUN_REL = re.compile(
    r"(?P<pre>\b(?:python3?|bash|sh|node)[ \t]+(?:-[A-Za-z]+[ \t]+)*)(?P<path>(?:\./)?(?:scripts|hooks|bin)/[A-Za-z0-9_./-]+)"
)


def _plugin_path_rx(plugin_name: str) -> re.Pattern[str]:
    return re.compile(r"(?:(?:\.\./)+|\./)?plugins/" + re.escape(plugin_name) + r"/")


def strip_frontmatter_keys(text: str, keys: tuple[str, ...] = STRIPPED_KEYS) -> str:
    """Remove the named keys (inline value, or an indented continuation / list) from a leading YAML
    frontmatter block. Text with no frontmatter, or with the closing fence missing, is returned unchanged.

    Why `allowed-tools` goes: it pre-approves those tools while the command or skill is active. /repo-review
    reads every file of a repository that may be hostile, with a bare `Bash` pre-approved, is exactly the
    shape a prompt injection wants. Without the field, each call goes through the user's own permissions."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    head, rest = text[4:end], text[end:]
    out: list[str] = []
    skipping = False
    for line in head.split("\n"):
        m = re.match(r"^([A-Za-z0-9_-]+)[ \t]*:", line)
        if m:
            skipping = m.group(1) in keys
        elif skipping and line.strip() and not line.startswith((" ", "\t", "-")):
            skipping = False
        if not skipping:
            out.append(line)
    return "---\n" + "\n".join(out) + rest


def transform_text(rel: str, text: str, plugin_name: str, shipped: set[str]) -> str:
    """The deterministic text edits applied to a shipped markdown file (everything else is byte-identical)."""
    if not rel.endswith(".md") or not rel.startswith(_TRANSFORM_DIRS):
        return text
    if rel.startswith(("commands/", "skills/")):
        text = strip_frontmatter_keys(text)
    elif rel.startswith("agents/"):
        text = strip_frontmatter_keys(text, AGENT_STRIPPED_KEYS)
    text = _plugin_path_rx(plugin_name).sub("${CLAUDE_PLUGIN_ROOT}/", text)

    def _abs(m: re.Match[str]) -> str:
        path = m.group("path")
        bare = path[2:] if path.startswith("./") else path
        return m.group("pre") + ("${CLAUDE_PLUGIN_ROOT}/" + bare if bare in shipped else path)

    return RUN_REL.sub(_abs, text)


def apply_text_edits(rel: str, text: str, edits: list[dict]) -> str:
    """Manifest `text_edits`: {file, find, replace, count?, reason}. An edit whose `find` is not present the
    expected number of times is a BUILD ERROR - the source moved under the edit and the edition would
    otherwise ship text nobody reviewed. These exist for the few sentences that are true in the source
    repository and false in the edition (a script that lives in the marketplace repo, not the plugin)."""
    for e in edits:
        want = int(e.get("count", 1))
        got = text.count(e["find"])
        if got != want:
            raise BuildError(
                f"text_edits: {rel}: expected {want} occurrence(s) of the text to replace, found {got} "
                f"({e['find'][:50]!r}...) - the source changed; re-review this edit"
            )
        text = text.replace(e["find"], e["replace"])
    return text


def write_dist(manifest: dict, plan: Plan, out: Path, repo: Path = REPO) -> None:
    src = repo / manifest["source_plugin_dir"]
    overrides = {k: (Path(manifest["_dir"]) / v) for k, v in manifest.get("overrides", {}).items()}
    if out.exists() and any(out.iterdir()):
        raise BuildError(f"{out} exists and is not empty")
    out.mkdir(parents=True, exist_ok=True)
    gen = dict(plan.generated)
    gen.update(render_templates(manifest, plan, repo))
    shipped = set(plan.files)
    name = manifest["plugin"]
    edits: dict[str, list[dict]] = {}
    for e in manifest.get("text_edits", []):
        edits.setdefault(e["file"], []).append(e)
    for f in sorted(set(edits) - shipped):
        raise BuildError(f"text_edits names {f}, which does not ship (stale entry)")
    for dist_path, how in sorted(plan.files.items()):
        dest = out / dist_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if how.startswith("gen:"):
            dest.write_text(gen[dist_path])
            if (dist_path.startswith("hooks/") and dist_path.endswith(".sh")) or dist_path == TRUST_PATH:
                os.chmod(dest, 0o755)
        elif how.startswith("override:"):
            text = fill_placeholders(overrides[dist_path].read_text(), manifest)
            text = apply_text_edits(dist_path, text, edits.get(dist_path, []))
            dest.write_text(transform_text(dist_path, text, name, shipped))
            os.chmod(dest, 0o644)
        else:
            srcfile = src / dist_path
            if srcfile.is_symlink():
                # copyfile follows a symlink, so the output-tree symlink check could never see one.
                raise BuildError(f"{dist_path} is a symlink in the source plugin; refusing to follow it")
            if dist_path in edits or (
                dist_path.endswith(".md") and dist_path.startswith(_TRANSFORM_DIRS)
            ):
                raw = apply_text_edits(dist_path, srcfile.read_text(), edits.get(dist_path, []))
                dest.write_text(transform_text(dist_path, raw, name, shipped))
                shutil.copymode(srcfile, dest)
            else:
                shutil.copyfile(srcfile, dest)
                shutil.copymode(srcfile, dest)
    for gname, text in gen.items():
        if gname in plan.files:
            continue
        dest = out / gname
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)


def all_dist_paths(plan: Plan, manifest: dict, repo: Path = REPO) -> list[str]:
    extra = set(render_templates(manifest, plan, repo))
    return sorted(set(plan.files) | extra)


# ── analyses of a built tree ────────────────────────────────────────────────


def tree_files(root: Path) -> list[str]:
    out = []
    for dirpath, dirs, files in os.walk(root):
        dirs.sort()
        for f in sorted(files):
            out.append(os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/"))
    return out


def limits_report(root: Path, limits: dict) -> dict:
    files = tree_files(root)
    big_nonimage, huge, symlinks, binaries, total = [], [], [], [], 0
    for rel in files:
        p = root / rel
        if p.is_symlink():
            symlinks.append(rel)
            continue
        size = p.stat().st_size
        total += size
        if size > limits["max_file_bytes"]:
            huge.append((rel, size))
        if Path(rel).suffix.lower() not in IMAGE_EXT and size > limits["max_file_bytes_nonimage"]:
            big_nonimage.append((rel, size))
        if Path(rel).suffix.lower() not in IMAGE_EXT:
            try:
                head = p.read_bytes()[:4096]
            except OSError:
                head = b""
            if b"\x00" in head:
                binaries.append(rel)
    violations = []
    if len(files) > limits["max_files"]:
        violations.append(
            f"{len(files)} files > max_files {limits['max_files']} (reviewer hold on every version)"
        )
    for rel, s in huge:
        violations.append(f"{rel}: {s} bytes > {limits['max_file_bytes']} (blocks)")
    for rel, s in big_nonimage:
        violations.append(
            f"{rel}: {s} bytes > {limits['max_file_bytes_nonimage']} non-image (reviewer hold)"
        )
    for rel in symlinks:
        violations.append(f"{rel}: symlink")
    for rel in binaries:
        violations.append(f"{rel}: binary/NUL content that is not an image")
    if total > limits.get("max_total_bytes", 1 << 60):
        violations.append(f"total {total} bytes > max_total_bytes")
    largest = sorted(
        (((root / r).stat().st_size, r) for r in files if not (root / r).is_symlink()), reverse=True
    )[:5]
    return {"files": len(files), "total_bytes": total, "largest": largest, "violations": violations}


_NET_PRIM = re.compile(
    r"\b(curl|wget|urllib|http\.client|requests\.|aiohttp|socket\.|fetch\(|nc |ncat|ssh |scp )"
)
_URL = re.compile(r"https?://([\w.-]+)")


def network_scan(root: Path) -> dict[str, dict]:
    """Executable files that contain a network primitive or a URL host (comments excluded)."""
    hits: dict[str, dict] = {}
    for rel in tree_files(root):
        if Path(rel).suffix not in EXEC_EXT:
            continue
        text = _scannable((root / rel).read_text(errors="replace"), rel)
        prims = sorted({m.group(1).strip() for m in _NET_PRIM.finditer(text)})
        hosts = sorted({m.group(1) for m in _URL.finditer(text)})
        if prims or hosts:
            hits[rel] = {"primitives": prims, "hosts": hosts}
    return hits


def network_findings(root: Path, manifest: dict) -> list[str]:
    classified = manifest.get("network_classification", {})
    problems = []
    for rel, h in network_scan(root).items():
        c = classified.get(rel)
        if (
            not c
            or not str(c.get("reason", "")).strip()
            or c.get("kind")
            not in (
                "none-runtime",
                "user-configured",
                "local-loopback",
                "user-session",
                "text-only",
            )
        ):
            problems.append(
                f"{rel}: network primitive/URL ({', '.join(h['primitives'] + h['hosts'])[:90]}) "
                "has no network_classification entry with a kind and a reason"
            )
        elif c.get("primitives") is None or c.get("hosts") is None:
            problems.append(
                f"{rel}: the classification must pin what it reviewed: "
                f"\"primitives\": {h['primitives']}, \"hosts\": {h['hosts']}"
            )
        elif sorted(c["primitives"]) != h["primitives"] or sorted(c["hosts"]) != h["hosts"]:
            problems.append(
                f"{rel}: network primitives/hosts changed since this classification was reviewed "
                f"(pinned {sorted(c['primitives'])}/{sorted(c['hosts'])}, now {h['primitives']}/{h['hosts']}) - "
                "re-review the file and update the pin"
            )
    for rel in classified:
        if rel not in set(tree_files(root)):
            problems.append(
                f"network_classification names {rel}, which does not ship (stale entry)"
            )
    return problems


def readme_parity(root: Path, manifest: dict) -> list[str]:
    """README must list exactly the shipped hooks (by id), and nothing else that looks like a hook."""
    readme = (root / "README.md").read_text()
    shipped = {h["id"] for h in manifest["components"]["hooks"]}
    hooks_dir = {
        p
        for p in tree_files(root)
        if p.startswith("hooks/") and p.endswith(".sh") and "/_" not in "/" + p[6:]
    }
    problems = []
    for hid in sorted(shipped):
        if f"`{hid}`" not in readme:
            problems.append(f"README does not list shipped hook `{hid}`")
    for rel in sorted(hooks_dir):
        base = Path(rel).name
        if rel == GATE_PATH:
            continue
        if not any(h.split()[0] == base for h in shipped):
            problems.append(
                f"{rel} ships but is not a manifest hook (unregistered script in hooks/)"
            )
    return problems


def structure_findings(root: Path, manifest: dict) -> list[str]:
    problems = []
    pj = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    if "experimental" in pj:
        problems.append("plugin.json declares `experimental` (must not declare components)")
    if pj.get("name") != manifest["plugin"]:
        problems.append(f"plugin.json name {pj.get('name')} != {manifest['plugin']}")
    for forbidden in (
        "bin",
        "monitors",
        "CLAUDE.md",
        "dashboard.html",
        "copilot",
        "codex",
        "vscode-extension",
    ):
        if (root / forbidden).exists():
            problems.append(f"{forbidden} must not ship in the directory edition")
    hj = json.loads((root / "hooks" / "hooks.json").read_text())
    for _event, _matcher, h in registrations(hj):
        for sp in hook_script_paths(h["command"]):
            if not (root / sp).is_file():
                problems.append(f"hooks.json registers {sp}, which does not ship")
    ungated = {h["id"] for h in manifest["components"]["hooks"] if h.get("ungated")}
    if not (root / GATE_PATH).is_file():
        problems.append(f"{GATE_PATH} is missing")
    elif (root / GATE_PATH).read_text() != POSTURE_GATE_SH:
        problems.append(f"{GATE_PATH} differs from the reviewed shim")
    if not (root / TRUST_PATH).is_file():
        problems.append(f"{TRUST_PATH} is missing")
    elif (root / TRUST_PATH).read_text() != EDITION_TRUST_SH:
        problems.append(f"{TRUST_PATH} differs from the reviewed helper")
    elif not os.access(root / TRUST_PATH, os.X_OK):
        problems.append(f"{TRUST_PATH} is not executable")
    for bad in sorted(ungated - UNGATED_ALLOWED):
        problems.append(f"{bad} is ungated but is not in the builder's UNGATED_ALLOWED list")
    for event, _matcher, h in registrations(hj):
        gated = h["command"].startswith(GATE_PREFIX)
        hid = hook_id(h["command"])
        inner = h["command"][len(GATE_PREFIX) :] if gated else h["command"]
        if not HOOK_CMD_FORM.match(inner):
            problems.append(f"{event}: {hid} has a command outside the allowed forms: {inner!r}")
        if hid in ungated and gated:
            problems.append(f"{hid} is declared ungated but is wrapped in the gate")
        if hid not in ungated and not gated:
            problems.append(
                f"{event}: {hid} is not wrapped in {GATE_PATH} (it would run with no posture file)"
            )
    for rel in tree_files(root):
        if rel.startswith("hooks/") and rel.endswith(".sh") and not os.access(root / rel, os.X_OK):
            problems.append(f"{rel} is not executable")
    return problems


# ── hygiene: things a stranger's repository could turn against the person who installed this ──

# An interpreter in command position: start of the line, or after | & ; ( ` or $(.
# Optional NAME=value assignments (quoted values included) may precede it. The path may be
# ./ ../ or absolute, including /usr/bin/env python3. A bare docs/python3 is not a command.
_PY_INVOKE = re.compile(
    r"(?:^|(?<=[|&;(`])|(?<=\$\())"
    r"[ \t]*"
    r"(?:[A-Za-z_][A-Za-z0-9_]*=(?:"
    r'"[^"]*"|'
    r"'[^']*'|"
    r"[^\s|&;()`]+"
    r")[ \t]+)*"
    r"(?:(?:\.\./)+(?:[\w.@+-]+/)*|\./(?:[\w.@+-]+/)*|/(?:[\w.@+-]+/)*)?"
    r"(?:python3?(?:\.\d+)?(?![\w.-])|env(?![\w.-])[ \t]+python3?(?:\.\d+)?(?![\w.-]))"
)
_CLAUDE_CL = "cla" + "ude"
_SPAWN_PIECES = (
    r"(^|[|&;(`]|\$\()\s*([A-Za-z_]+=\S+\s+)*" + _CLAUDE_CL + r"\s+(-|auth|plugin|mcp|config)",
    r"\[\s*['\"]" + _CLAUDE_CL + r"['\"]",
    r"which\(['\"]" + _CLAUDE_CL,
    r"command -v " + _CLAUDE_CL,
    _CLAUDE_CL + r" -p\b",
)
_SPAWN = re.compile("|".join(_SPAWN_PIECES))
# A non-empty default for the plugin root (`${CLAUDE_PLUGIN_ROOT:-plugins/x}`, `:=`, or no colon). Claude Code
# substitutes only the bare token, so the shell expands the default, which is a path inside the PROJECT.
# The empty default `${CLAUDE_PLUGIN_ROOT:-}` (a set-or-unset test inside a hook) is fine and not matched.
_ROOT_FALLBACK = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT:?[-=][^}]")


def _line_continues(line: str) -> bool:
    """A trailing unescaped backslash continues the shell line (backslash-newline)."""
    n = 0
    for ch in reversed(line):
        if ch != "\\":
            break
        n += 1
    return n % 2 == 1


def _join_continuations(text: str) -> str:
    """Join backslash-newline continuations so the interpreter and its flags are one line."""
    out: list[str] = []
    buf = ""
    pending = False
    for line in text.splitlines():
        buf = buf + line if pending else line
        if _line_continues(line):
            buf = buf[:-1]
            pending = True
            continue
        out.append(buf)
        buf = ""
        pending = False
    if pending:
        out.append(buf)
    return "\n".join(out)


def _logical_lines(text: str) -> list[str]:
    joined = _join_continuations(text)
    return joined.splitlines()


def _read_word(s: str, i: int) -> tuple[str, int]:
    n = len(s)
    if i >= n:
        return "", i
    if s[i] in "\"'":
        q = s[i]
        j = i + 1
        while j < n and s[j] != q and s[j] != "\n":
            j += 1
        if j < n and s[j] == q:
            j += 1
        return s[i:j], j
    j = i
    while j < n and s[j] not in " \t\n|&;)#<>":
        if s[j] in "\"'":
            q = s[j]
            j += 1
            while j < n and s[j] != q and s[j] != "\n":
                j += 1
            if j < n and s[j] == q:
                j += 1
            continue
        j += 1
    return s[i:j], j


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t":
        i += 1
    return i


def _consume_word(s: str, i: int) -> int:
    i = _skip_ws(s, i)
    if i >= len(s) or s[i] in "|&;\n#)<>":
        return i
    _word, i = _read_word(s, i)
    return i


def _invocation_sensitive(tail: str, before: str) -> bool | None:
    """Whether the argv after an interpreter token imports the current directory and is not isolated.

    None means this match is a case-pattern arm (`python3|python)`), not a command.
    `-I` counts only as a flag (alone or in a cluster). A script path is not sensitive.
    No script and no -c/-m means the interpreter reads stdin (a pipe, a bare name, `python3 -`,
    or a heredoc). `--version` / `--help` / `-V` / `-h` do not run user code.
    """
    if before == "|" and tail.startswith(")"):
        return None
    if re.match(r"(?:\|[A-Za-z0-9._-]*)+\)", tail):
        return None
    i = 0
    n = len(tail)
    isolated = False
    c_or_m = False
    dash_stdin = False
    heredoc = False
    stdin_redirect = False
    script = False
    version = False
    while True:
        i = _skip_ws(tail, i)
        if i >= n or tail[i] in "|&;\n#)":
            break
        if tail.startswith("<<", i):
            heredoc = True
            break
        if tail[i] == "<":
            stdin_redirect = True
            break
        if tail[i] == ">":
            break
        if tail[i].isdigit():
            j = i
            while j < n and tail[j].isdigit():
                j += 1
            if j < n and tail[j] == ">":
                break
        word, i = _read_word(tail, i)
        if not word:
            break
        if word == "-":
            dash_stdin = True
            break
        if word == "--":
            i = _skip_ws(tail, i)
            if i < n and tail[i] not in "|&;\n#)<>":
                script = True
            break
        if word.startswith("--"):
            name, _eq, _attached = word.partition("=")
            if name in ("--version", "--help"):
                version = True
                continue
            if name == "--check-hash-based-pycs" and "=" not in word:
                i = _consume_word(tail, i)
            continue
        if word.startswith("-") and len(word) > 1:
            cluster = word[1:]
            k = 0
            while k < len(cluster):
                ch = cluster[k]
                k += 1
                if not (("a" <= ch <= "z") or ("A" <= ch <= "Z") or ch == "?"):
                    break
                if ch == "I":
                    isolated = True
                    continue
                if ch in "Vh?":
                    version = True
                    continue
                if ch in "cm":
                    c_or_m = True
                    if cluster[k:] == "":
                        i = _consume_word(tail, i)
                    break
                if ch in "WXQ":
                    if cluster[k:] == "":
                        i = _consume_word(tail, i)
                    break
            if c_or_m:
                break
            continue
        script = True
        break
    if c_or_m or dash_stdin or heredoc or (stdin_redirect and not script):
        return not isolated
    if script or version:
        return False
    return not isolated


def python_cwd_sensitive(line: str) -> bool:
    """True when `line` runs python in a form that puts the CURRENT DIRECTORY on sys.path and does not
    isolate it. `python3 -c` (with or without a space, including `-Bc`/`-uc`), `python3 -m`, `python3 -`,
    `python3 <<`, a pipe into a bare interpreter, and a bare `python3` all do. A path
    (`/usr/bin/python3`, `./python3`, `/usr/bin/env python3`) is the same command. Options may precede
    `-c`/`-m`/`-`, including ones that take an argument (`-W ignore`, `-X dev`). A backslash-newline
    between the interpreter and its flags still counts. `python3 script.py` puts the SCRIPT's directory
    on sys.path instead, so it is allowed. `-I` (isolated mode, Python 3.4+, also inside a cluster such
    as `-Ic`) removes the current directory, PYTHON* variables and the user site."""
    for logical in _logical_lines(line):
        if re.match(r"^[ \t]*[A-Za-z0-9._|*-]+\)[ \t]*$", logical):
            continue
        for m in _PY_INVOKE.finditer(logical):
            before = logical[m.start() - 1] if m.start() else ""
            decided = _invocation_sensitive(logical[m.end() :], before)
            if decided:
                return True
    return False


_INLINE_PY = re.compile(
    r"^(?:(?:\.\./)+(?:[\w.@+-]+/)*|\./(?:[\w.@+-]+/)*|/(?:[\w.@+-]+/)*)?"
    r"(?:python3?(?:\.\d+)?|env[ \t]+python3?(?:\.\d+)?)\b"
)


def _md_code_lines(text: str):
    """(lineno, code) for fenced-block lines and inline code spans that START with an interpreter.

    Backslash-newline continuations inside a fence are joined first. An inline span is scanned when
    it starts with python, a ./ ../ or absolute path to python, or env python — not when python is
    merely mentioned later in the span.
    """
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith("```"):
            i += 1
            block: list[tuple[int, str]] = []
            while i < n and not lines[i].lstrip().startswith("```"):
                block.append((i + 1, lines[i]))
                i += 1
            buf = ""
            start = 0
            pending = False
            for no, bl in block:
                if not pending:
                    buf = bl
                    start = no
                else:
                    buf += bl
                if _line_continues(bl):
                    buf = buf[:-1]
                    pending = True
                    continue
                yield start, buf
                pending = False
            if pending and buf:
                yield start, buf
            if i < n and lines[i].lstrip().startswith("```"):
                i += 1
            continue
        for sp in re.finditer(r"`([^`\n]+)`", lines[i]):
            code = sp.group(1).strip()
            if code.startswith("$ "):
                code = code[2:]
            if _INLINE_PY.match(code):
                yield i + 1, code
        i += 1


def hygiene_findings(root: Path, manifest: dict) -> list[str]:
    """Checks that the shipped files cannot be steered by a repository the person opened.

    1. python: no cwd-sensitive interpreter call without `-I` (a project-root json.py/shlex.py would run).
    2. allowed-tools: no shipped command or skill pre-approves a tool, and no agent loads repository memory (`memory:`).
    3. paths: no `plugins/<name>/` left in instructions, and no interpreter run on a plugin-relative script
       that does not ship (it would resolve inside the PROJECT).
    4. no shipped executable starts the `claude` CLI (a nested model session is a disclosed-or-absent thing).
    5. no shipped text file (markdown, script, workflow) falls back to a path inside the project when the plugin
       root is unset: `${CLAUDE_PLUGIN_ROOT:-plugins/x}` would run a hostile repository's own copy.
    """
    problems: list[str] = []
    name = manifest["plugin"]
    py_allow = {a["file"]: a for a in manifest.get("python_isolation_allow", [])}
    run_allow = {a["file"]: a for a in manifest.get("runnable_path_allow", [])}
    py_seen: set[str] = set()
    run_seen: set[str] = set()
    for a in list(py_allow.values()) + list(run_allow.values()):
        if not str(a.get("reason", "")).strip():
            problems.append(f"hygiene allow entry for {a.get('file')} needs a reason")
    for rel in tree_files(root):
        suffix = Path(rel).suffix
        text = (root / rel).read_text(errors="replace")
        if suffix in TEXT_EXT:
            for i, line in enumerate(text.splitlines(), 1):
                if _ROOT_FALLBACK.search(line):
                    problems.append(
                        f"{rel}:{i}: falls back to a path inside the project when the plugin root is unset "
                        f"({line.strip()[:70]!r}); Claude Code substitutes only the bare token"
                    )
        if suffix in EXEC_EXT:
            for line in _logical_lines(_scannable(text, rel)):
                if python_cwd_sensitive(line):
                    py_seen.add(rel)
                    if rel not in py_allow:
                        problems.append(
                            f"{rel}: python run without -I ({line.strip()[:70]!r}) - a json.py in the "
                            "project root would be imported"
                        )
                if _SPAWN.search(line):
                    problems.append(f"{rel}: starts the claude CLI ({line.strip()[:70]!r})")
        if suffix == ".md" and rel.startswith(_TRANSFORM_DIRS):
            for i, code in _md_code_lines(text):
                if python_cwd_sensitive(code):
                    py_seen.add(rel)
                    if rel not in py_allow:
                        problems.append(
                            f"{rel}:{i}: instruction runs python without -I ({code[:70]!r})"
                        )
            if f"plugins/{name}/" in text:
                problems.append(f"{rel}: still names plugins/{name}/ (should be ${{CLAUDE_PLUGIN_ROOT}}/)")
            for i, line in enumerate(text.splitlines(), 1):
                for m in RUN_REL.finditer(line):
                    run_seen.add(rel)
                    if rel not in run_allow:
                        problems.append(
                            f"{rel}:{i}: runs plugin-relative {m.group('path')!r}, which does not ship "
                            "(it would resolve inside the project)"
                        )
            if rel.startswith(("commands/", "skills/", "agents/")):
                fm = text.split("\n---", 1)[0] if text.startswith("---\n") else ""
                keys = AGENT_STRIPPED_KEYS if rel.startswith("agents/") else STRIPPED_KEYS
                for key in keys:
                    if re.search(rf"^{re.escape(key)}[ \t]*:", fm, re.M):
                        problems.append(f"{rel}: frontmatter still carries {key}")
    for f in sorted(set(py_allow) - py_seen):
        problems.append(f"python_isolation_allow names {f}, which has no finding (stale entry)")
    for f in sorted(set(run_allow) - run_seen):
        problems.append(f"runnable_path_allow names {f}, which has no finding (stale entry)")
    return problems


def claude_validate(root: Path) -> tuple[str, str]:
    """`claude plugin validate --strict` on BOTH manifests: the marketplace one at the root (what a directory
    reviewer's tooling reads first) and the plugin one. A pass needs both; a fail names which one."""
    exe = shutil.which("claude")
    if not exe:
        return "unavailable", "claude CLI not on PATH"
    out: list[str] = []
    status = "pass"
    for target in (root, root / ".claude-plugin" / "plugin.json"):
        try:
            cp = subprocess.run(
                [exe, "plugin", "validate", "--strict", str(target)],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception as e:  # noqa: BLE001
            return "unavailable", f"could not run: {e}"
        label = "marketplace manifest" if target == root else "plugin manifest"
        out.append(f"[{label}] " + (cp.stdout + cp.stderr).strip()[-700:])
        if cp.returncode != 0:
            status = "fail"
    return status, "\n".join(out)[-1500:]


def file_list_text(paths: list[str]) -> str:
    return "\n".join(paths) + "\n"


def file_list_path(manifest: dict, repo: Path = REPO) -> Path:
    return Path(manifest["_dir"]) / "file-list.txt"


def digest_tree(root: Path) -> str:
    h = hashlib.sha256()
    for rel in tree_files(root):
        h.update(rel.encode())
        h.update(b"\0")
        h.update((root / rel).read_bytes())
        h.update(b"\0")
        h.update(str(oct((root / rel).stat().st_mode & 0o111)).encode())
    return h.hexdigest()


def full_build(manifest: dict, out: Path, repo: Path = REPO) -> Plan:
    plan = plan_build(manifest, repo)
    if plan.closure_breaks:
        lines = [f"  {a} -> {b}  ({why})" for a, b, why in plan.closure_breaks]
        raise BuildError(
            "closure broken: an executable file references a denied file. Add the file to the "
            "manifest, change the source, or allow-list the pair in closure_allow with a reason:\n"
            + "\n".join(lines)
        )
    write_dist(manifest, plan, out, repo)
    return plan


# ── commands ────────────────────────────────────────────────────────────────


SECRET_RULES = {
    "aws-access-key": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "github-token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
    "github-fine-grained": r"\bgithub_pat_[A-Za-z0-9_]{50,}\b",
    "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    "stripe-live": r"\b[sr]k_live_[A-Za-z0-9]{16,}\b",
    "google-api-key": r"\bAIza[0-9A-Za-z_-]{35}\b",
    "npm-token": r"\bnpm_[A-Za-z0-9]{36}\b",
    "hf-token": r"\bhf_[A-Za-z0-9]{30,}\b",
    "private-key-block": r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}\b",
    "url-with-credentials": r"[a-z][a-z0-9+.-]*://[^\s/:@'\"]{3,}:[^\s/@'\"]{3,}@[A-Za-z0-9.-]+",
    "anthropic-key": r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    "openai-key": r"\bsk-[A-Za-z0-9]{32,}\b",
    "assigned-secret": r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*[\"'][A-Za-z0-9/+_=-]{16,}[\"']",
}
_SECRET_RX = {k: re.compile(v) for k, v in SECRET_RULES.items()}


def secret_findings(root: Path, allow: list[dict] | None = None) -> list[str]:
    """Secret-shaped strings in the built tree. Two independent passes: a gitleaks-style regex set, and the
    plugin's own hooks/_scrub.sh (a file is flagged when scrubbing would change it). Findings are reported as
    file:line:rule, never the matched text. An `allow` entry (file + reason) explains a finding that is the
    scrubber's own pattern literal; an allow entry that matches nothing is itself a problem (stale)."""
    allow = allow or []
    scrub = root / "hooks" / "_scrub.sh"
    found: dict[str, list[str]] = {}
    for rel in tree_files(root):
        p = root / rel
        data = p.read_bytes()
        if b"\x00" in data[:4096]:
            continue
        hits = []
        for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
            for name, rx in _SECRET_RX.items():
                if rx.search(line):
                    hits.append(f"{i}:{name}")
        if scrub.is_file():
            cp = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; a="$(cat "$2")"; b="$(_scrub_reason "$a")"; [ "$a" = "$b" ]',
                    "_",
                    str(scrub),
                    str(p),
                ],
                capture_output=True,
                text=True,
            )
            if cp.returncode != 0:
                hits.append("0:repo-scrub.sh-would-redact")
        if hits:
            found[rel] = hits
    problems = []
    allowed = {a["file"] for a in allow if str(a.get("reason", "")).strip()}
    for a in allow:
        if not str(a.get("reason", "")).strip():
            problems.append(f"secret_scan_allow {a.get('file')}: a reason is required")
        elif a["file"] not in found:
            problems.append(
                f"secret_scan_allow names {a['file']}, which has no finding (stale entry)"
            )
    for rel, hits in sorted(found.items()):
        if rel not in allowed:
            problems.append(f"secret-shaped string in {rel}: " + ", ".join(hits[:4]))
    return problems


def check_problems(manifest: dict, repo: Path = REPO) -> tuple[list[str], list[str], Path | None]:
    """Everything the gate checks that needs no hook execution. Returns (problems, dist file list, None).
    The built tree is deleted on return; callers that need it (the hook audit) call full_build themselves."""
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
        a, b = Path(td) / "a", Path(td) / "b"
        full_build(manifest, a, repo)
        full_build(manifest, b, repo)
        if digest_tree(a) != digest_tree(b):
            problems.append("two builds from the same source differ (non-deterministic)")
        problems += limits_report(a, manifest["limits"])["violations"]
        problems += structure_findings(a, manifest)
        problems += hygiene_findings(a, manifest)
        problems += readme_parity(a, manifest)
        problems += network_findings(a, manifest)
        problems += secret_findings(a, manifest.get("secret_scan_allow", []))
        paths = tree_files(a)
        want = file_list_text(paths)
        lp = file_list_path(manifest, repo)
        have = lp.read_text() if lp.exists() else ""
        if want != have:
            ws, hs = set(want.split()), set(have.split())
            problems.append(
                f"file list is stale ({len(ws - hs)} added, {len(hs - ws)} removed): "
                "run build-directory-edition.py --write-file-list"
            )
    return problems, paths, None


def cmd_check(manifest: dict, repo: Path = REPO) -> int:
    problems, paths, _ = check_problems(manifest, repo)
    for p in problems:
        print("  FAIL", p)
    print("directory-edition build check:", "FAILED" if problems else f"OK ({len(paths)} files)")
    return 1 if problems else 0


def cmd_explain(manifest: dict, repo: Path = REPO) -> int:
    """Every file that is in the build only because something referenced it, with the referrer."""
    plan = plan_build(manifest, repo)
    comps = manifest["components"]
    roots = {f"agents/{a['name']}.md" for a in comps["agents"]} | {
        f"commands/{c['name']}.md" for c in comps["commands"]
    }
    for rel, frm in sorted(plan.via.items()):
        if frm != "<root>" and rel not in roots:
            print(f"{rel}  <-  {frm}")
    return 0


def cmd_report(manifest: dict, repo: Path = REPO) -> int:
    with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
        out = Path(td) / "dist"
        plan = plan_build(manifest, repo)
        print(f"closure breaks (executable -> denied): {len(plan.closure_breaks)}")
        for a, b, why in plan.closure_breaks:
            print(f"  {a} -> {b}  [{why}]")
        print(f"prose references to denied files (informational): {len(plan.prose_denied)}")
        if plan.closure_breaks:
            return 1
        full_build(manifest, out, repo)
        rep = limits_report(out, manifest["limits"])
        print(f"files: {rep['files']}  bytes: {rep['total_bytes']}")
        for s, r in rep["largest"]:
            print(f"  {s:>9}  {r}")
        for v in rep["violations"]:
            print("  VIOLATION", v)
        for v in network_findings(out, manifest):
            print("  NETWORK", v)
        for v in structure_findings(out, manifest) + hygiene_findings(out, manifest) + readme_parity(out, manifest):
            print("  STRUCTURE", v)
        by_top: dict[str, int] = {}
        for r in tree_files(out):
            by_top[r.split("/")[0]] = by_top.get(r.split("/")[0], 0) + 1
        print("by top-level:", dict(sorted(by_top.items())))
    return 0


# ── self-test ───────────────────────────────────────────────────────────────


def _fixture(root: Path) -> dict:
    p = root / "plugins" / "demo"
    (p / ".claude-plugin").mkdir(parents=True)
    (p / "agents").mkdir()
    (p / "skills" / "good").mkdir(parents=True)
    (p / "skills" / "bad").mkdir(parents=True)
    (p / "commands").mkdir()
    (p / "hooks").mkdir()
    (p / "scripts").mkdir()
    (p / "knowledge").mkdir()
    (p / "bin").mkdir()
    (p / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "version": "1.2.3",
                "author": {"name": "T"},
                "license": "MIT",
                "experimental": {"monitors": "./m.json"},
            }
        )
    )
    (p / "agents" / "a.md").write_text("---\nname: a\n---\nSee knowledge/k.md for detail.\n")
    (p / "knowledge" / "k.md").write_text("knowledge\n")
    (p / "skills" / "good" / "SKILL.md").write_text(
        "---\nname: good\n---\nRun scripts/helper.py.\n"
    )
    (p / "skills" / "bad" / "SKILL.md").write_text("---\nname: bad\n---\nbad\n")
    (p / "scripts" / "helper.py").write_text("print('hi')\n")
    (p / "commands" / "c.md").write_text("---\ndescription: c\n---\ncommand\n")
    (p / "hooks" / "keep.sh").write_text(
        '#!/usr/bin/env bash\nsource "$(dirname "$0")/_lib.sh"\nexit 0\n'
    )
    (p / "hooks" / "_lib.sh").write_text("#!/usr/bin/env bash\n:\n")
    (p / "hooks" / "drop.sh").write_text("#!/usr/bin/env bash\nexit 2\n")
    for h in ("keep.sh", "_lib.sh", "drop.sh"):
        (p / "hooks" / h).chmod(0o755)
    (p / "bin" / "tool").write_text("#!/bin/sh\n")
    (p / "hooks" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"',
                                },
                                {
                                    "type": "command",
                                    "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/drop.sh"',
                                },
                            ]
                        }
                    ]
                }
            }
        )
    )
    tdir = root / "docs" / "directory-edition" / "demo" / "templates"
    tdir.mkdir(parents=True)
    (root / "LICENSE").write_text("MIT License\n")
    (tdir / "README.md").write_text(
        "# demo {{VERSION}}\n{{HOOK_TABLE}}\n{{AGENT_LIST}}\n{{SKILL_LIST}}\n{{COMMAND_LIST}}\n{{REPO}} {{HOMEPAGE}} {{PORTAL}} {{SUPPORT}}\n"
    )
    (tdir / "PRIVACY.md").write_text("privacy {{VERSION}} {{SUPPORT}}\n")
    (tdir / "LICENSE").write_text("MIT {{REPO}}\n")
    return {
        "_dir": str(root / "docs" / "directory-edition" / "demo"),
        "schema_version": 1,
        "plugin": "demo",
        "source_plugin_dir": "plugins/demo",
        "target": {
            "repository": "https://example.invalid/demo",
            "homepage": "https://example.invalid/demo",
            "marketplace_name": "demo",
            "portal_url": "https://example.invalid/portal",
            "support": "https://example.invalid/issues",
        },
        "plugin_json": {"description": "Demo.", "displayName": "Demo"},
        "limits": {
            "max_files": 40,
            "max_file_bytes_nonimage": 4096,
            "max_file_bytes": 8192,
            "max_total_bytes": 100000,
        },
        "closure": {"prose_depth": 1},
        "components": {
            "agents": [{"name": "a", "reason": "agent"}],
            "skills": [{"name": "good", "reason": "skill"}],
            "commands": [{"name": "c", "reason": "cmd"}],
            "hooks": [{"id": "keep.sh", "reason": "r", "summary": "does nothing"}],
        },
        "deny_globs": [
            {"glob": "bin/**", "reason": "no bin"},
            {"glob": "hooks/drop.sh", "reason": "always on"},
        ],
        "network_classification": {},
    }


def self_test() -> int:
    ok = bad = 0

    def check(label: str, cond: bool) -> None:
        nonlocal ok, bad
        print(("  ok   " if cond else "  FAIL ") + label)
        ok, bad = (ok + 1, bad) if cond else (ok, bad + 1)

    def expect_error(label: str, fn, needle: str) -> None:
        try:
            fn()
        except BuildError as e:
            check(label + f" [{needle}]", needle in str(e))
            return
        check(label + " (no error raised)", False)

    with tempfile.TemporaryDirectory(prefix="rc-edition-self-") as td:
        root = Path(td)
        m = _fixture(root)
        plan = plan_build(m, root)
        shipped = set(plan.files)
        check(
            "agent, command, skill copied",
            {"agents/a.md", "commands/c.md", "skills/good/SKILL.md"} <= shipped,
        )
        check(
            "a skill that is not allow-listed does not ship", "skills/bad/SKILL.md" not in shipped
        )
        check(
            "closure pulls in a referenced knowledge file (prose, one hop)",
            "knowledge/k.md" in shipped,
        )
        check("closure pulls in a referenced script", "scripts/helper.py" in shipped)
        check("closure pulls in a hook's sibling helper", "hooks/_lib.sh" in shipped)
        check("an un-listed hook does not ship", "hooks/drop.sh" not in shipped)
        hj = json.loads(plan.generated["hooks/hooks.json"])
        cmds = [h["command"] for g in hj["hooks"]["Stop"] for h in g["hooks"]]
        check("hooks.json is filtered to the manifest", len(cmds) == 1 and "keep.sh" in cmds[0])
        pj = json.loads(plan.generated[".claude-plugin/plugin.json"])
        check("plugin.json drops `experimental`", "experimental" not in pj)
        check(
            "plugin.json version equals the source (single source of truth)",
            pj["version"] == "1.2.3",
        )

        out1, out2 = root / "o1", root / "o2"
        full_build(m, out1, root)
        full_build(m, out2, root)
        check(
            "two builds are byte-identical (deterministic)", digest_tree(out1) == digest_tree(out2)
        )
        check(
            "hook scripts keep their executable bit", os.access(out1 / "hooks" / "keep.sh", os.X_OK)
        )
        hj1 = json.loads((out1 / "hooks" / "hooks.json").read_text())
        gcmds = [h["command"] for g in hj1["hooks"]["Stop"] for h in g["hooks"]]
        check(
            "gate: a gated hook's command is wrapped in the posture gate",
            gcmds[0].startswith(GATE_PREFIX),
        )
        check(
            "gate: the shim ships, is executable and is the reviewed text",
            (out1 / GATE_PATH).read_text() == POSTURE_GATE_SH
            and os.access(out1 / GATE_PATH, os.X_OK),
        )
        check("README lists exactly the shipped hooks", not readme_parity(out1, m))
        check("structure findings are clean", not structure_findings(out1, m))
        check(
            "limits are clean for a small tree", not limits_report(out1, m["limits"])["violations"]
        )

        # ── must-fail halves: each guard has to be capable of failing ──
        mu = json.loads(json.dumps(m))
        mu["components"]["hooks"][0]["ungated"] = True
        check(
            "manifest: ungated without an ungated_reason is rejected",
            any("ungated_reason" in x for x in validate_manifest(mu)),
        )
        m2 = json.loads(json.dumps(m))
        (root / "plugins" / "demo" / "hooks" / "keep.sh").write_text(
            '#!/usr/bin/env bash\nbash "$CLAUDE_PLUGIN_ROOT/bin/tool"\n'
        )
        p2 = plan_build(m2, root)
        check(
            "closure: an executable file referencing a DENIED file is a build break",
            bool(p2.closure_breaks),
        )
        m2["closure_allow"] = [{"from": "hooks/keep.sh", "to": "bin/tool", "reason": "demo"}]
        check(
            "closure: an explicit allow-list entry clears it",
            not plan_build(m2, root).closure_breaks,
        )
        (root / "plugins" / "demo" / "hooks" / "keep.sh").write_text(
            '#!/usr/bin/env bash\nsource "$(dirname "$0")/_lib.sh"\nexit 0\n'
        )

        (root / "plugins" / "demo" / "knowledge" / "k.md").write_text("see bin/tool\n")
        check(
            "a PROSE reference to a denied file is informational, not a break",
            not plan_build(m, root).closure_breaks,
        )
        (root / "plugins" / "demo" / "knowledge" / "k.md").write_text("knowledge\n")

        m3 = json.loads(json.dumps(m))
        m3["components"]["agents"][0]["reason"] = ""
        check(
            "manifest: an entry without a reason is rejected",
            any("REASON" in x for x in validate_manifest(m3)),
        )
        m4 = json.loads(json.dumps(m))
        m4["components"]["hooks"].append({"id": "ghost.sh", "reason": "r", "summary": "s"})
        expect_error(
            "manifest: a hook that is not registered in the source fails the build",
            lambda: plan_build(m4, root),
            "ghost.sh",
        )

        big = root / "o1" / "knowledge" / "huge.md"
        big.write_text("x" * 5000)
        check(
            "limits: a non-image file over the cap is a violation",
            bool(limits_report(root / "o1", m["limits"])["violations"]),
        )
        big.unlink()
        (root / "o1" / "knowledge" / "link.md").symlink_to("k.md")
        check(
            "limits: a symlink is a violation",
            any("symlink" in v for v in limits_report(root / "o1", m["limits"])["violations"]),
        )
        (root / "o1" / "knowledge" / "link.md").unlink()
        (root / "o1" / "knowledge" / "blob.bin").write_bytes(b"\x00\x01\x02" * 10)
        check(
            "limits: non-image binary content is a violation",
            any("binary" in v for v in limits_report(root / "o1", m["limits"])["violations"]),
        )
        (root / "o1" / "knowledge" / "blob.bin").unlink()

        hjb = json.loads((root / "o1" / "hooks" / "hooks.json").read_text())
        hjb["hooks"]["Stop"][0]["hooks"][0]["command"] = '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"'
        (root / "o1" / "hooks" / "hooks.json").write_text(json.dumps(hjb))
        check(
            "gate: an un-wrapped registration is a structure finding",
            any("not wrapped" in x for x in structure_findings(root / "o1", m)),
        )
        (root / "o1" / "README.md").write_text("# no hook table\n")
        check("README parity: a missing hook row is caught", bool(readme_parity(root / "o1", m)))
        (root / "o1" / "hooks" / "stray.sh").write_text("#!/bin/sh\n")
        (root / "o1" / "hooks" / "stray.sh").chmod(0o755)
        (root / "o1" / "README.md").write_text("`keep.sh`\n")
        check(
            "README parity: an unregistered script in hooks/ is caught",
            any("stray.sh" in x for x in readme_parity(root / "o1", m)),
        )

        (root / "o1" / "scripts" / "helper.py").write_text(
            "import urllib.request\nurllib.request.urlopen('https://example.invalid/x')\n"
        )
        nf = network_findings(root / "o1", m)
        check(
            "network: an unclassified primitive/URL is a finding", any("helper.py" in x for x in nf)
        )
        m["network_classification"] = {
            "scripts/helper.py": {
                "kind": "user-configured",
                "reason": "demo",
                "primitives": ["urllib"],
                "hosts": ["example.invalid"],
            }
        }
        check(
            "network: a classified entry with a reason clears it",
            not network_findings(root / "o1", m),
        )
        m["network_classification"]["scripts/ghost.py"] = {"kind": "text-only", "reason": "x"}
        check(
            "network: a classification for a file that does not ship is stale",
            any("stale" in x for x in network_findings(root / "o1", m)),
        )

        planted = root / "o1" / "knowledge" / "planted.md"
        planted.write_text("token = " + "gh" + "p_" + "0123456789abcdef0123456789abcdef0123" + "\n")
        check(
            "secrets: a planted token is a finding",
            any("planted.md" in x for x in secret_findings(root / "o1")),
        )
        check(
            "secrets: an allow entry with a reason clears it",
            not secret_findings(root / "o1", [{"file": "knowledge/planted.md", "reason": "test"}]),
        )
        check(
            "secrets: an allow entry without a reason does not",
            any(
                "reason is required" in x
                for x in secret_findings(
                    root / "o1", [{"file": "knowledge/planted.md", "reason": ""}]
                )
            ),
        )
        planted.unlink()
        check(
            "secrets: an allow entry that matches nothing is stale",
            any(
                "stale" in x
                for x in secret_findings(
                    root / "o1", [{"file": "knowledge/planted.md", "reason": "test"}]
                )
            ),
        )
        check("secrets: a clean tree has no findings", not secret_findings(root / "o1"))

        (root / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "demo", "version": "9.9.9", "author": {"name": "T"}})
        )
        check(
            "a source version bump flows through with no manifest edit",
            json.loads(
                plan_build(json.loads(json.dumps(m)), root).generated[".claude-plugin/plugin.json"]
            )["version"]
            == "9.9.9",
        )

        # ── review-driven hardening: each guard below has a half that must fail ──
        fm = "---\nname: x\nallowed-tools: Bash, Read\ndescription: d\n---\nbody allowed-tools: Bash\n"
        s = strip_frontmatter_keys(fm)
        check(
            "allowed-tools: removed from frontmatter; other keys and the body are untouched",
            "allowed-tools: Bash, Read" not in s
            and "name: x" in s
            and "description: d" in s
            and s.endswith("body allowed-tools: Bash\n"),
        )
        lst = "---\nname: x\nallowed-tools:\n  - Bash\n  - Read\ndescription: d\n---\nb\n"
        check(
            "allowed-tools: a multi-line list value is removed with its items",
            "Bash" not in strip_frontmatter_keys(lst) and "description: d" in strip_frontmatter_keys(lst),
        )
        check(
            "allowed-tools: no frontmatter, or an unterminated one, is returned unchanged",
            strip_frontmatter_keys("no fm\nallowed-tools: x\n") == "no fm\nallowed-tools: x\n"
            and strip_frontmatter_keys("---\nallowed-tools: x\n") == "---\nallowed-tools: x\n",
        )
        tx = transform_text(
            "skills/good/SKILL.md",
            "---\nallowed-tools: Bash\n---\nsee plugins/demo/scripts/a.py, ./plugins/demo/x and "
            "../../plugins/demo/y\nrun python3 scripts/helper.py and python3 scripts/ghost.py\n",
            "demo",
            {"scripts/helper.py"},
        )
        check(
            "paths: plugins/<name>/ becomes ${CLAUDE_PLUGIN_ROOT}/ in every relative spelling",
            "plugins/demo/" not in tx and tx.count("${CLAUDE_PLUGIN_ROOT}/") >= 4,
        )
        check(
            "paths: a shipped script run by an interpreter gets the plugin root; an unshipped one is left for the lint",
            "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/helper.py" in tx
            and "python3 scripts/ghost.py" in tx,
        )
        _agent = transform_text(
            "agents/a.md", "---\nname: a\nmemory: project\ntools: Read\n---\nbody memory: keep\n", "demo", set()
        )
        check(
            "agents: memory: is removed from the frontmatter and nothing else is touched",
            "memory: project" not in _agent and "tools: Read" in _agent and "body memory: keep" in _agent,
        )
        check(
            "agents: a COMMAND keeps a memory: line (only agents lose it)",
            "memory: project"
            in transform_text("commands/c.md", "---\ndescription: d\nmemory: project\n---\nx\n", "demo", set()),
        )
        check(
            "paths: templates/ is never touched (those scripts belong to the user's repo)",
            transform_text("templates/x.md", "plugins/demo/a python3 scripts/helper.py", "demo", {"scripts/helper.py"})
            == "plugins/demo/a python3 scripts/helper.py",
        )
        table = {
            "python3 -c 'x'": True,
            "python3 -m json.tool f": True,
            "python3 - <<'PY'": True,
            "python3 <<EOF": True,
            "x | python3 -": True,
            "python3 -B -c 'x'": True,
            "python3 -I -c 'x'": False,
            "python3 -Ic 'x'": False,
            "python3 -I -m json.tool": False,
            "python3 script.py": False,
            "echo python3": False,
            "/usr/bin/python3 -c 'x'": True,
            "./python3 -c 'x'": True,
            "/usr/bin/env python3 -c 'x'": True,
            "env python3 -c 'x'": True,
            "python -c 'x'": True,
            "python3 -c'import json'": True,
            'python3 -c"import json"': True,
            "python3 -Bc 'x'": True,
            "python3 -uc 'x'": True,
            "python3 -W ignore -c 'x'": True,
            "python3 -X dev -c 'x'": True,
            "python3 -O -m json.tool": True,
            "cmd | python3": True,
            "python3": True,
            "python3 -": True,
            "python3 \\\n -c 'x'": True,
            "python3.11 -c 'x'": True,
            "python3 -Wignore -c 'x'": True,
            "python3 -c -I": True,
            "python3 < file": True,
            "`python -m spacy download en`": True,
            "pip install spacy && python -m spacy download en": True,
            "python3 -I -c'import json'": False,
            "/usr/bin/python3 -I -c 'x'": False,
            "/usr/bin/env python3 -I -c 'x'": False,
            "python3 -W ignore -I -c 'x'": False,
            "python3 -I -W ignore -c 'x'": False,
            "python3 -BI -c 'x'": False,
            "cmd | python3 -I": False,
            "python3 -I": False,
            "python3 -I <<EOF": False,
            "python3 -O script.py": False,
            "python3 -W ignore script.py": False,
            "cmd | python3 script.py": False,
            "python3 \\\n script.py": False,
            "command -v python3": False,
            "python3|python)": False,
            "python3 -V": False,
            "python3 --version": False,
            "python3 -h": False,
            "python3 --help": False,
            "notpython3 -c 'x'": False,
            "docs/python3 readme": False,
            "python3-config --prefix": False,
            "python3 script.py < file": False,
            "#!/usr/bin/env python3": False,
            'FOO="a b" python3 -I -c \'x\'': False,
            "python3 ${SCRIPTS_DIR}/repo_map.py --out x": False,
        }
        wrong = [k for k, v in table.items() if python_cwd_sensitive(k) != v]
        check("python isolation: truth table " + (f"[wrong: {wrong}]" if wrong else ""), not wrong)
        good_cmds = [
            '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"',
            'bash "${CLAUDE_PLUGIN_ROOT}/scripts/b.sh"',
            '"${CLAUDE_PLUGIN_ROOT}/hooks/c.sh" "$CLAUDE_TOOL_FILE_PATH"',
        ]
        bad_cmds = [
            '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"; rm x',
            '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" && b',
            'bash -c "${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"',
            "${CLAUDE_PLUGIN_ROOT}/hooks/a.sh",
            '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" | tee x',
            'X; bash "${CLAUDE_PLUGIN_ROOT}/hooks/a.sh"',
            '"${CLAUDE_PLUGIN_ROOT}/../a.sh"',
            '"${CLAUDE_PLUGIN_ROOT}/hooks/a.sh" x',
        ]
        check(
            "hook command form: the shapes in hooks.json pass",
            all(HOOK_CMD_FORM.match(c) for c in good_cmds),
        )
        check(
            "hook command form: ;, &&, pipes, bash -c, a bare variable, `..` and stray args are refused",
            not any(HOOK_CMD_FORM.match(c) for c in bad_cmds),
        )
        mf = json.loads(json.dumps(m))
        (root / "plugins" / "demo" / "hooks" / "hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": 'true; bash "${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"',
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
        )
        expect_error(
            "hook command form: a source command the gate cannot contain fails the build",
            lambda: plan_build(mf, root),
            "cannot be certain",
        )
        (root / "plugins" / "demo" / "hooks" / "hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {"type": "command", "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"'}
                                ]
                            }
                        ]
                    }
                }
            )
        )
        mu2 = json.loads(json.dumps(m))
        mu2["components"]["hooks"][0].update({"ungated": True, "ungated_reason": "because"})
        check(
            "ungated: only the builder's own list may skip the gate, whatever the manifest says",
            any("may be ungated" in x for x in validate_manifest(mu2)),
        )

        m5 = json.loads(json.dumps(m))
        m5["text_edits"] = [{"file": "knowledge/k.md", "find": "knowledge", "replace": "EDITED", "reason": "t"}]
        o5 = root / "o5"
        full_build(m5, o5, root)
        check("text_edits: an edit is applied", (o5 / "knowledge" / "k.md").read_text().startswith("EDITED"))
        m5["text_edits"][0]["find"] = "text that is not there"
        expect_error(
            "text_edits: a find that no longer matches fails the build",
            lambda: write_dist(m5, plan_build(m5, root), root / "o5b", root),
            "expected 1",
        )
        m5["text_edits"] = [{"file": "knowledge/ghost.md", "find": "x", "replace": "y", "reason": "t"}]
        expect_error(
            "text_edits: an edit to a file that does not ship is stale",
            lambda: write_dist(m5, plan_build(m5, root), root / "o5c", root),
            "does not ship",
        )

        m6 = json.loads(json.dumps(m))
        m6["extra_roots"] = [{"glob": "knowledge/sym.md", "reason": "t"}]
        (root / "plugins" / "demo" / "knowledge" / "sym.md").symlink_to("k.md")
        expect_error(
            "source symlink: copyfile would follow it, so the build refuses",
            lambda: write_dist(m6, plan_build(m6, root), root / "o6", root),
            "symlink",
        )
        (root / "plugins" / "demo" / "knowledge" / "sym.md").unlink()

        # hygiene lints against a fresh build
        (root / "plugins" / "demo" / "hooks" / "hooks.json").write_text(
            json.dumps(
                {
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {"type": "command", "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/keep.sh"'}
                                ]
                            }
                        ]
                    }
                }
            )
        )
        o7 = root / "o7"
        full_build(m, o7, root)
        check("hygiene: a clean build has no findings", not hygiene_findings(o7, m))
        keep = o7 / "hooks" / "keep.sh"
        keep.write_text('#!/usr/bin/env bash\npython3 -c "import json"\n')
        check(
            "hygiene: python3 -c without -I in a shipped script is a finding",
            any("without -I" in x for x in hygiene_findings(o7, m)),
        )
        keep.write_text('#!/usr/bin/env bash\npython3 -I -c "import json"\n')
        check("hygiene: ... and python3 -I -c is clean", not hygiene_findings(o7, m))
        keep.write_text('#!/usr/bin/env bash\n# python3 -c "import json" is only a comment\nexit 0\n')
        check("hygiene: a comment line is not a finding", not hygiene_findings(o7, m))
        keep.write_text('#!/usr/bin/env bash\nexit 0\n')
        (o7 / "scripts" / "helper.py").write_text('import subprocess\nsubprocess.run(["claude", "-p", "x"])\n')
        check(
            "hygiene: a shipped script that starts the claude CLI is a finding",
            any("claude CLI" in x for x in hygiene_findings(o7, m)),
        )
        (o7 / "scripts" / "helper.py").write_text("print('hi')\n")
        cmd = o7 / "commands" / "c.md"
        cmd.write_text("---\ndescription: c\nallowed-tools: Bash\n---\nx\n")
        check(
            "hygiene: allowed-tools left in a shipped command is a finding",
            any("allowed-tools" in x for x in hygiene_findings(o7, m)),
        )
        cmd.write_text("---\ndescription: c\n---\nx\n")
        kn = o7 / "knowledge" / "k.md"
        kn.write_text("see plugins/demo/scripts/a.py\n")
        check(
            "hygiene: plugins/<name>/ left in an instruction is a finding",
            any("plugins/demo/" in x for x in hygiene_findings(o7, m)),
        )
        kn.write_text("run `python3 scripts/ghost.py` now\n")
        check(
            "hygiene: an interpreter run on an unshipped plugin-relative script is a finding",
            any("does not ship" in x for x in hygiene_findings(o7, m)),
        )
        m7 = json.loads(json.dumps(m))
        m7["runnable_path_allow"] = [{"file": "knowledge/k.md", "reason": "an example"}]
        check("hygiene: an allow entry with a reason clears it", not hygiene_findings(o7, m7))
        kn.write_text("nothing to see\n")
        check(
            "hygiene: ... and a stale allow entry is itself a finding",
            any("stale" in x for x in hygiene_findings(o7, m7)),
        )
        kn.write_text("run `python3 -m json.tool f` now\n")
        check(
            "hygiene: python3 -m in an instruction is a finding",
            any("without -I" in x for x in hygiene_findings(o7, m)),
        )
        kn.write_text("run `python3 ${CLAUDE_PLUGIN_ROOT:-plugins/demo}/skills/x/s.py` now\n")
        check(
            "hygiene: a ${CLAUDE_PLUGIN_ROOT:-default} in an instruction is a finding",
            any("falls back" in x for x in hygiene_findings(o7, m)),
        )
        keep.write_text('#!/usr/bin/env bash\nroot="${CLAUDE_PLUGIN_ROOT:-./plugins/demo}"\nexit 0\n')
        check(
            "hygiene: ... and in a shipped script",
            any("falls back" in x and "hooks/keep.sh" in x for x in hygiene_findings(o7, m)),
        )
        wfjs = o7 / "skills" / "x"
        wfjs.mkdir(parents=True, exist_ok=True)
        (wfjs / "w.js").write_text('const R = "${CLAUDE_PLUGIN_ROOT:-plugins/demo}";\n')
        check(
            "hygiene: ... and in a shipped workflow .js",
            any("falls back" in x and "w.js" in x for x in hygiene_findings(o7, m)),
        )
        (wfjs / "w.js").unlink()
        wfjs.rmdir()
        kn.write_text("knowledge\n")
        keep.write_text('#!/usr/bin/env bash\n[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0\nexit 0\n')
        check("hygiene: the empty default ${CLAUDE_PLUGIN_ROOT:-} is not a finding", not hygiene_findings(o7, m))
        keep.write_text("#!/usr/bin/env bash\nexit 0\n")
        (o7 / "agents").mkdir(exist_ok=True)
        ag = o7 / "agents" / "a.md"
        ag.write_text("---\nname: a\nmemory: project\n---\nbody\n")
        check(
            "hygiene: memory: left in a shipped agent is a finding (repository memory would load into its prompt)",
            any("memory" in x for x in hygiene_findings(o7, m)),
        )
        ag.unlink()
        (o7 / "agents").rmdir()
        kn.write_text("knowledge\n")

        trust = o7 / TRUST_PATH
        trust.write_text(trust.read_text() + "# tampered\n")
        check(
            "structure: a changed trust helper is a finding",
            any("differs from the reviewed helper" in x for x in structure_findings(o7, m)),
        )
        trust.write_text(EDITION_TRUST_SH)
        trust.chmod(0o644)
        check(
            "structure: a non-executable trust helper is a finding",
            any("not executable" in x for x in structure_findings(o7, m)),
        )
        trust.chmod(0o755)
        gate = o7 / GATE_PATH
        gate.write_text(POSTURE_GATE_SH.replace('grep -Fxq', 'grep -Fq'))
        check(
            "structure: a changed gate (even one character) is a finding",
            any("differs from the reviewed shim" in x for x in structure_findings(o7, m)),
        )
        gate.write_text(POSTURE_GATE_SH)

        (o7 / "scripts" / "helper.py").write_text("import urllib.request\n")
        m8 = json.loads(json.dumps(m))
        m8["network_classification"] = {"scripts/helper.py": {"kind": "text-only", "reason": "demo"}}
        check(
            "network: a classification that does not pin primitives/hosts is a finding",
            any("must pin" in x for x in network_findings(o7, m8)),
        )
        m8["network_classification"]["scripts/helper.py"].update({"primitives": ["urllib"], "hosts": []})
        check("network: a matching pin clears it", not network_findings(o7, m8))
        (o7 / "scripts" / "helper.py").write_text("import urllib.request\nimport socket\nsocket.socket()\n")
        check(
            "network: a NEW primitive in an already-classified file is a finding",
            any("changed since" in x for x in network_findings(o7, m8)),
        )

    print(f"build-directory-edition self-test: {ok} passed, {bad} failed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--repo", type=Path, default=REPO, help="repo root holding the source plugin")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument(
        "--explain",
        action="store_true",
        help="list files that ship only via closure, with their referrer",
    )
    ap.add_argument("--write-file-list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        manifest = load_manifest(a.manifest)
        repo = a.repo.resolve()
        if a.check:
            return cmd_check(manifest, repo)
        if a.report:
            return cmd_report(manifest, repo)
        if a.explain:
            return cmd_explain(manifest, repo)
        if a.write_file_list:
            with tempfile.TemporaryDirectory(prefix="rc-edition-") as td:
                full_build(manifest, Path(td) / "d", repo)
                paths = tree_files(Path(td) / "d")
            file_list_path(manifest).write_text(file_list_text(paths))
            print(f"wrote {file_list_path(manifest)} ({len(paths)} files)")
            return 0
        if a.out:
            full_build(manifest, a.out.resolve(), repo)
            print(f"built {len(tree_files(a.out))} files into {a.out}")
            return 0
    except BuildError as e:
        print(f"BUILD ERROR: {e}", file=sys.stderr)
        return 2
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
