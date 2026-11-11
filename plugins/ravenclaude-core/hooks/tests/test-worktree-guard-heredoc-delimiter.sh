#!/usr/bin/env bash
# test-worktree-guard-heredoc-delimiter.sh — AppSec R1 (SHIPCHECK on
# RavenClaude#1424, NO-SHIP at 991a54a6): the linear scanner must parse the
# full bash word as the heredoc delimiter (not a leading \w+ run) and must
# never drop unscanned text when a terminator is missing. 0.361.1 and 0.361.2
# denied out-of-tree rm/cp/mv/sed -i/tee/interpreter writes after delimiters
# such as EOF-X, E.O.F, EOF.1, END-MSG, 'EOF'X, "A"B and 'E O F'; 0.361.3
# allowed them.
#
# Door 5: no here-doc-shaped <<TAG span is nested in $( ). The two-character
# sequence "<<" is produced by Python via chr(60)*2, never written as source
# text inside a command substitution.
#
# Run: bash plugins/ravenclaude-core/hooks/tests/test-worktree-guard-heredoc-delimiter.sh

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$HOOKS_DIR/worktree-guard-bash.py"
HOOK="$HOOKS_DIR/worktree-guard.sh"

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

PASS=0
FAIL=0

# Build every payload with Python (no << in this bash source).
python3 - "$T" <<'PY'
import os, sys
td = sys.argv[1]
hd = chr(60) * 2  # "<<"
# (name, text after <<, terminator line)
DELIMS = [
    ("EOF-X", "EOF-X", "EOF-X"),
    ("E.O.F", "E.O.F", "E.O.F"),
    ("EOF.1", "EOF.1", "EOF.1"),
    ("END-MSG", "END-MSG", "END-MSG"),
    ("qEOF-X", "'EOF'X", "EOFX"),
    ("qAB", '"A"B', "AB"),
    ("qE-O-F", "'E O F'", "E O F"),
]
# bash -c uses an interpreter -c write the helper can see (plain
# bash -c "rm -rf …" is also allowed on 0.361.2 — the helper does not
# scan into bash -c for WRITERS). The form below is denied on 0.361.2.
WRITERS = [
    ("rm", "rm -rf /workspace/sibling-wt"),
    ("cp", "cp a /workspace/sibling-wt/"),
    ("mv", "mv a.txt /workspace/escape.txt"),
    ("sed", "sed -i s/a/b/ /workspace/sibling-wt/f"),
    ("tee", "echo x | tee /workspace/sibling-wt/f"),
    ("bash-c", "bash -c \"python3 -c \\\"open('/workspace/sibling-wt/x','w')\\\"\""),
    ("interp", "python3 - " + hd + "'PY'\nopen('/workspace/sibling-wt/x','w').write('x')\nPY"),
]
os.makedirs(os.path.join(td, "helper"), exist_ok=True)
manifest = []
for dname, opener, term in DELIMS:
    for wname, writer in WRITERS:
        body = "cat " + hd + opener + "\nhi\n" + term + "\n" + writer
        key = dname + "__" + wname
        path = os.path.join(td, "helper", key)
        open(path, "w").write(body)
        manifest.append(key)
open(os.path.join(td, "manifest"), "w").write("\n".join(manifest) + "\n")
# AppSec-reproduced allow cases at 0.361.3, used as the teeth set.
teeth = [
    "EOF-X__rm",
    "qEOF-X__mv",
    "EOF.1__sed",
    "END-MSG__cp",
    "qEOF-X__interp",
    "qAB__bash-c",
    "E.O.F__rm",
]
open(os.path.join(td, "teeth"), "w").write("\n".join(teeth) + "\n")
PY

echo
echo "── AppSec R1 — helper: full-word delimiters, following writes must deny (exit 3) ──"
ROOT="$T/worktree"
mkdir -p "$ROOT"
while IFS= read -r key; do
  [ -n "$key" ] || continue
  python3 "$PY" "$ROOT" "$ROOT" <"$T/helper/$key" >"$T/out" 2>"$T/err"
  got=$?
  if [ "$got" = "3" ]; then
    PASS=$((PASS + 1))
    printf '  \033[32m✓\033[0m helper-%s (rc=3)\n' "$key"
  else
    FAIL=$((FAIL + 1))
    printf '  \033[31m✗\033[0m helper-%s want=3 got=%s: %s\n' "$key" "$got" "$(head -c200 "$T/out")$(head -c200 "$T/err")"
  fi
done <"$T/manifest"

echo
echo "── AppSec R1 — hook: the same payloads must deny through worktree-guard.sh (exit 2) ──"
git init -q "$T/wt" && printf '%s\n' ".ravenclaude/" >"$T/wt/.gitignore" \
  && git -C "$T/wt" add .gitignore \
  && git -C "$T/wt" -c user.name=t -c user.email=t@t commit -q -m init
export RC_WORKTREE_GUARD_HOME="$T/gh" RC_WG_ERROR_LOG="$T/errors.log" RC_WG_STALE_LOG="$T/stale.log" CLAUDE_PROJECT_DIR="$T/wt"
# Payload builder: JSON on disk, no << in this script's $( ).
while IFS= read -r key; do
  [ -n "$key" ] || continue
  cmd="$(cat "$T/helper/$key")"
  jq -cn --arg c "$cmd" --arg w "$T/wt" \
    '{tool_name:"Bash",session_id:"s1",cwd:$w,tool_input:{command:$c}}' >"$T/payload.json"
  (cd "$T/wt" && bash "$HOOK" check <"$T/payload.json") >"$T/hook-out" 2>"$T/hook-err"
  got=$?
  if [ "$got" = "2" ]; then
    PASS=$((PASS + 1))
    printf '  \033[32m✓\033[0m hook-%s (rc=2)\n' "$key"
  else
    FAIL=$((FAIL + 1))
    printf '  \033[31m✗\033[0m hook-%s want=2 got=%s: %s\n' "$key" "$got" "$(head -c200 "$T/hook-err")"
  fi
done <"$T/manifest"

echo
echo "── AppSec R1 — teeth: the 0.361.3 scanner allows the reproduced cases ──"
# Mutate a copy back to the 0.361.3 delimiter / drop-on-unterminated behaviour
# (leading \\w+ only, word-boundary terminator, blank without a newline, drop
# the rest when a terminator is not found). The AppSec-reproduced cases must
# then return exit 0, proving this fixture would go red on the buggy helper.
python3 - "$PY" "$T/mutant.py" <<'PY'
import sys
src = open(sys.argv[1]).read()
# Swap the full-word parser for a leading-\\w+ opener (the 0.361.3 bug).
anchor = "def _parse_heredoc_opener(text, idx):"
assert anchor in src, "anchor _parse_heredoc_opener not found"
# Replace _parse_shell_word-based body by prefixing a buggy function of the
# same name later? Cleaner: overwrite _parse_heredoc_opener to the old shape
# and ignore _parse_shell_word. Insert a stub immediately after the def
# that the real function would... no, replace from def through return word.
old_start = src.find(anchor)
old_end = src.find("def _parse_shell_word(")
assert old_start >= 0 and old_end > old_start
src = src[:old_start] + '''def _parse_heredoc_opener(text, idx):
    if not text.startswith("<<", idx):
        return None
    if idx + 2 < len(text) and text[idx + 2] == "<":
        return None
    j = idx + 2
    strip_tabs = False
    if j < len(text) and text[j] == "-":
        strip_tabs = True
        j += 1
    while j < len(text) and text[j] in " \\t":
        j += 1
    quote = None
    if j < len(text) and text[j] in ("'", '"', "\\\\"):
        quote = text[j]
        j += 1
    tag_start = j
    while j < len(text) and (text[j].isalnum() or text[j] == "_"):
        j += 1
    if j == tag_start:
        return None
    tag = text[tag_start:j]
    if quote in ("'", '"') and j < len(text) and text[j] == quote:
        j += 1
    return tag, strip_tabs, j


''' + src[old_end:]
# Word-boundary terminator (0.361.3).
src = src.replace(
    "    return check == tag\n",
    '''    if check == tag:
        return True
    if check.startswith(tag) and len(check) > len(tag):
        nxt = check[len(tag)]
        if not (nxt.isalnum() or nxt == "_"):
            return True
    return False
''',
    1,
)
# Drop-on-unterminated + no-newline blank (the rest of the 0.361.3 bug).
src = src.replace(
    'blank="<<HEREDOC\\n"',
    'blank="<<HEREDOC"',
    1,
)
# Restore the drop-on-unterminated else branch.
old_else_keep = '''        else:
            if nl < 0:
                # Unterminated (no body line): keep the rest, including any
                # later commands on this or following lines.
                out.append(text[pos:])
                break
'''
new_else_drop = '''        else:
            out.append(text[pos:idx] + blank)
            if nl < 0:
                break
'''
assert old_else_keep in src, "keep-rest else-branch not found for mutation"
src = src.replace(old_else_keep, new_else_drop, 1)
# The "if not found: keep rest" must also drop.
src = src.replace(
    '''            if not found:
                # Unterminated: keep opener, body, and everything after.
                out.append(text[pos:])
                break
''',
    '''            if not found:
                break
''',
    1,
)
open(sys.argv[2], "w").write(src)
PY

teeth_fail=0
while IFS= read -r key; do
  [ -n "$key" ] || continue
  python3 "$T/mutant.py" "$ROOT" "$ROOT" <"$T/helper/$key" >"$T/mout" 2>"$T/merr"
  got=$?
  if [ "$got" = "0" ]; then
    PASS=$((PASS + 1))
    printf '  \033[32m✓\033[0m mutant-allows-%s (rc=0) — test is sensitive\n' "$key"
  else
    FAIL=$((FAIL + 1))
    teeth_fail=$((teeth_fail + 1))
    printf '  \033[31m✗\033[0m mutant-allows-%s want=0 got=%s: test cannot distinguish fixed from unfixed: %s\n' \
      "$key" "$got" "$(head -c200 "$T/mout")"
  fi
done <"$T/teeth"

echo
printf '  %d pass, %d fail\n' "$PASS" "$FAIL"
echo "RESULT pass=$PASS fail=$FAIL"
[ "$FAIL" -eq 0 ]
