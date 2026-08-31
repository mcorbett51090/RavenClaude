#!/usr/bin/env bash
# enforce-portability.sh — in-loop macOS-portability lint (PreToolUse Write|Edit|MultiEdit).
#
# Stock macOS ships bash 3.2 and BSD userland. The costly failure mode is not a
# crash — it is a SILENT no-op: an invalid shopt exits 1, an absent command exits
# 127, and the harness treats a hook exit other than 2 as a NON-blocking error, so
# the guard simply never runs and nothing is reported. Eighteen separate commits
# have closed one of these doors. This hook moves the catch from "a CI runner on
# some later PR" to "the moment the line is written".
#
# ⛔ SINGLE SOURCE OF TRUTH. The banned-token set lives in
# knowledge/portability-tokens.json and is read by BOTH this hook and the CI
# backstop (scripts/check-portability-lint.py). Neither hard-codes a pattern, so
# the two surfaces cannot drift — the parity is structural, not asserted. Do NOT
# inline a pattern here.
#
# KNOB: macos_portability_lint: off | warn | block  (.ravenclaude/comfort-posture.yaml)
#   absent posture file -> NO-OP entirely (opt-in by presence, like the git-protocol hook)
#   posture present, key absent -> warn
#   warn  -> stderr notice, exit 0, nothing blocked   [the default]
#   block -> deny (exit 2) with the shim to use instead
# Mirrors the shipped git_protocol warn/block precedent rather than inventing a
# second dialect. Default warn because a lint that hard-blocks on day one over a
# repo-wide token set gets switched off, and a switched-off guard protects nothing.
#
# FAIL-OPEN: any error — missing python3, unreadable table, malformed payload,
# absent posture — exits 0. A portability lint that hard-fails a consumer who has
# no shell surface at all is worse than the gap it closes.
#
# SNR: this file is itself in the CI linter's scope and is NOT exempt. It stays
# clean by delegating every match to python3 — there is no banned token in this
# script to begin with, which is the self-test the design asks for.
set -uo pipefail

# ── Payload ─────────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || exit 0
payload="$(cat 2>/dev/null || true)"
[ -n "$payload" ] || exit 0

proj="${CLAUDE_PROJECT_DIR:-$PWD}"
posture="$proj/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0   # opt-in by presence of a posture

# Minimal scalar read — same sed idiom worktree-guard.sh uses for its own knob;
# no PyYAML dependency in a consumer environment.
mode="$(sed -n 's/^macos_portability_lint:[[:space:]]*\([A-Za-z]*\).*$/\1/p' "$posture" 2>/dev/null | head -n 1)"
[ -n "$mode" ] || mode="warn"
[ "$mode" = "off" ] && exit 0

# Resolve the token table: plugin root first, then relative to this script so a
# dev-mirror invocation from the working tree also resolves.
table="${CLAUDE_PLUGIN_ROOT:-}/knowledge/portability-tokens.json"
if [ ! -f "$table" ]; then
  table="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/knowledge/portability-tokens.json"
fi
[ -f "$table" ] || exit 0

findings="$(printf '%s' "$payload" | python3 -c '
import json, os, re, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = d.get("tool_name")
if tool not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)

ti = d.get("tool_input") or {}
path = str(ti.get("file_path", "") or "")
if not path:
    sys.exit(0)

# Per-tool content field. Reading only "content" would leave Edit/MultiEdit
# screened-but-blind — a screen that runs and sees nothing.
if tool == "Write":
    text = str(ti.get("content", "") or "")
elif tool == "Edit":
    text = str(ti.get("new_string", "") or "")
else:
    text = "\n".join(str((e or {}).get("new_string", "") or "") for e in (ti.get("edits") or []))
if not text:
    sys.exit(0)

# ── Scope. Deliberately reaches past hooks/: the two most recent real breaks
# were in an extension-less installer and a monitors script.
base = os.path.basename(path)
p = path.replace(os.sep, "/")
in_scope = (
    p.endswith(".sh")
    or "/bin/" in p
    or base in ("ravenclaude", "rc", "rcwt")
    or text.lstrip().startswith("#!") and "sh" in text.splitlines()[0]
)
if not in_scope:
    sys.exit(0)

# Sanctioned exemptions: each of these must CONTAIN the banned tokens to do its
# job, so linting them would be the self-non-recursion failure.
if base in ("_portable.sh", "check-macos-portability.sh", "check-portability-lint.py"):
    sys.exit(0)
if any(seg in "/" + p for seg in ("/tests/", "/test/", "/fixtures/")):
    sys.exit(0)

try:
    tokens = json.load(open(sys.argv[1], encoding="utf-8")).get("tokens") or []
except Exception:
    sys.exit(0)
if not tokens:
    sys.exit(0)

SQ = re.compile(r"\x27[^\x27\n]*\x27")
DQ = re.compile(r"\"[^\"\n]*\"")
SENTINEL = re.compile(r"#\s*noport\b")


def blank(m):
    return " " * len(m.group(0))


def prep(line, mode):
    # Quotes first so a "#" inside a string is not read as a comment start.
    out = SQ.sub(blank, line)
    if mode == "command":
        out = DQ.sub(blank, out)
    h = out.find("#")
    return out if h == -1 else out[:h] + " " * (len(out) - h)


hits = []
lines = text.splitlines()
for i, raw in enumerate(lines, start=1):
    if SENTINEL.search(raw):
        continue
    for t in tokens:
        try:
            rx = re.compile(t["pattern"])
        except Exception:
            continue
        if not rx.search(prep(raw, t.get("mode", "command"))):
            continue
        pair = t.get("portable_pair")
        if pair:
            try:
                lo, hi = max(0, i - 3), min(len(lines), i + 2)
                if re.search(pair, "\n".join(lines[lo:hi])):
                    continue
            except Exception:
                pass
        hits.append("line %d [%s] %s -> use instead: %s"
                    % (i, t.get("id", "?"), t.get("why", ""), t.get("shim", "")))
print("\n".join(hits))
' "$table" 2>/dev/null || true)"

[ -n "$findings" ] || exit 0

if [ "$mode" = "block" ]; then
  if command -v jq >/dev/null 2>&1; then
    reason="This write introduces a construct that breaks on a stock macOS toolchain, usually SILENTLY. $(printf '%s' "$findings" | head -n 3 | tr '\n' ' ') — route it through plugins/ravenclaude-core/hooks/_portable.sh, or mark a deliberate occurrence with a trailing '# noport' comment."
    jq -n --arg r "$reason" \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  fi
  {
    echo "[enforce-portability] BLOCKED — breaks on a stock macOS toolchain:"
    printf '%s\n' "$findings" | sed 's/^/  /'
    echo "  Route through hooks/_portable.sh, or add a trailing '# noport' to a deliberate occurrence."
    echo "  Set macos_portability_lint: warn (or off) in .ravenclaude/comfort-posture.yaml to relax."
  } >&2
  exit 2
fi

{
  echo "[enforce-portability] portability notice (warn — nothing blocked):"
  printf '%s\n' "$findings" | sed 's/^/  /'
  echo "  Route through hooks/_portable.sh, or add a trailing '# noport' if deliberate."
} >&2
exit 0
