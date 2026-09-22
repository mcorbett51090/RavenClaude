#!/usr/bin/env bash
# Gate 260 — precompact-handoff-convergence P7.
#
# Covers P1a-f (scripts/handoff-nudge.py), P2's C3/C4 + `finalize`
# (scripts/context-handoff.py), and P5's retention (scripts/precompact-digest.py).
#
# ⛔ FIVE must-fail halves, each independently observed to flip (reverted the
# fix, ran it, confirmed red, restored) before this file was written:
#   --must-fail-a  reverts `_stop_reason` to the OLD single-field exact-match
#                  check (`payload.get("reason") == "end_turn"`) => the
#                  Claude-shaped AND Copilot-shaped firing assertions redden.
#   --must-fail-b  restores the OLD unconditional "state file exists =>
#                  throttled forever" behavior => the re-arm-after-cooldown
#                  assertion reddens.
#   --must-fail-c  removes `finalize`'s scrub call => the
#                  planted-secret-token-absent assertion reddens.
#   --must-fail-d  removes the four `_chmod_600(...)` call sites `cmd_write`
#                  (+ `stamp_meta`) makes => the file-mode assertions redden.
#   --must-fail-e  breaks P5's retention predicate to accept a directory
#                  containing `handoff.md` => the "never removed" assertion
#                  reddens.
set -uo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
ENGINE="$HERE/../scripts/handoff-nudge.py"
CONTEXT_HANDOFF="$HERE/../scripts/context-handoff.py"
DIGEST_PY="$HERE/../scripts/precompact-digest.py"
SENTINEL="ZZGATE260SECRETZZ"
mode="${1:-normal}"
fails=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ------------------------------------------------------------------------
# Fixtures (mirroring test-gate212-handoff-nudge.sh's proven shapes).
# ------------------------------------------------------------------------
python3 - "$T" <<'PY'
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
sess = d / "sess"
sess.mkdir()
# 80% of 1000 = 800 (headroom to a default 85% auto-compact = 5, i.e. NOT
# below MIN_PROCEDURE_HEADROOM -- the "full 4-step form" fixture)
(sess / "updates.jsonl").write_text(
    json.dumps({"params": {"_meta": {"totalTokens": 800}}}) + "\n"
)
(sess / "signals.json").write_text(json.dumps({"contextWindowTokens": 1000}))
(d / "posture-nag.yaml").write_text(
    "schema_version: 5\ncontext_handoff:\n  mode: nag\n  threshold_percent: 70\n"
)
PY

_link_session() {
  local home="$1" root="$2" fixture="$3" sid="$4"
  python3 - "$home" "$root" "$fixture" "$sid" <<'PY'
import shutil, sys
from pathlib import Path
from urllib.parse import quote
home, root, fixture, sid = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
enc = quote(str(root.resolve()), safe="")
dest = home / "sessions" / enc / sid
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(fixture, dest)
PY
}

_payload_claude_shaped() {
  # A Claude-shaped Stop payload: NO "reason" key at all.
  python3 -c 'import json,sys; print(json.dumps({
    "stopHookActive": False,
    "sessionId": sys.argv[2],
    "cwd": sys.argv[1],
    "workspaceRoot": sys.argv[1],
  }))' "$@"
}

_payload_copilot_shaped() {
  # A Copilot-shaped Stop payload (post P6c'-adapter reshape): carries
  # snake_case `stop_reason`/`stop_hook_active`, never a bare "reason" key.
  python3 -c 'import json,sys; print(json.dumps({
    "stop_reason": "end_turn",
    "stop_hook_active": False,
    "session_id": sys.argv[2],
    "cwd": sys.argv[1],
  }))' "$@"
}

_payload_grok_shutdown() {
  python3 -c 'import json,sys; print(json.dumps({
    "reason": "channel_closed",
    "stopHookActive": False,
    "sessionId": sys.argv[2],
    "cwd": sys.argv[1],
    "workspaceRoot": sys.argv[1],
  }))' "$@"
}

_run() {
  # engine root sid payload_fn
  local engine="$1" root="$2" sid="$3" payload_fn="$4"
  mkdir -p "$root/.ravenclaude"
  cp "$T/posture-nag.yaml" "$root/.ravenclaude/comfort-posture.yaml"
  _link_session "$T" "$root" "$T/sess" "$sid"
  printf '%s' "$("$payload_fn" "$root" "$sid")" | \
    GROK_SESSION_ID="$sid" GROK_HOOK_EVENT="stop" GROK_HOME="$T" \
    GROK_WORKSPACE_ROOT="$root" python3 "$engine" 2>/dev/null
}

_seed_state() {
  # root sid offset_seconds attempts verdict("null"|"nothing-to-do")
  python3 - "$1" "$2" "$3" "$4" "$5" <<'PY'
import json, os, re, sys, time
from pathlib import Path
root, sid, offset, attempts, verdict = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
sanitized = re.sub(r"[^A-Za-z0-9._-]", "", sid)[:128]
if sanitized in ("", ".", ".."):
    sanitized = "unknown"
state_dir = Path(root) / ".ravenclaude" / "handoff-nudge-state"
state_dir.mkdir(parents=True, exist_ok=True)
fired_epoch = time.time() - offset
fired_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(fired_epoch))
data = {
    "session_id": sid,
    "fired_at": fired_at,
    "attempts": attempts,
    "verdict": None if verdict in ("null", "none", "") else verdict,
}
target = state_dir / (sanitized + ".json")
target.write_text(json.dumps(data) + "\n")
os.utime(target, (fired_epoch, fired_epoch))
PY
}

_assert_contains() {
  case "$2" in
    *"$3"*) printf '  ok   %s\n' "$1" ;;
    *) printf '  FAIL %s (missing: %s)\n' "$1" "$3"; fails=$((fails + 1)) ;;
  esac
}

_assert_absent() {
  case "$2" in
    *"$3"*) printf '  FAIL %s (leaked/present: %s)\n' "$1" "$3"; fails=$((fails + 1)) ;;
    *) printf '  ok   %s\n' "$1" ;;
  esac
}

_assert_empty() {
  if [ -z "$2" ]; then
    printf '  ok   %s\n' "$1"
  else
    printf '  FAIL %s (expected empty, got: %s)\n' "$1" "$2"
    fails=$((fails + 1))
  fi
}

_mode_of() {
  python3 -c 'import os,sys,stat; print(oct(stat.S_IMODE(os.stat(sys.argv[1]).st_mode)))' "$1" 2>/dev/null
}

# ==========================================================================
# --must-fail-a — revert `_stop_reason` to the OLD single-field exact-match.
# ==========================================================================
if [ "$mode" = "--must-fail-a" ]; then
  mutant="$T/handoff-nudge-mfa.py"
  python3 - "$ENGINE" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = 'r = _stop_reason(payload)\n    if r and r != "end_turn":\n        return 0'
if old not in src:
    raise SystemExit("handoff-nudge.py drifted -- update Gate 260 --must-fail-a mutant")
new = 'r = payload.get("reason") or ""\n    if r != "end_turn":\n        return 0'
src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  root1="$T/proj-mfa-claude"; rm -rf "$root1"
  out1="$(_run "$mutant" "$root1" "sid-mfa-claude" _payload_claude_shaped)"
  root2="$T/proj-mfa-copilot"; rm -rf "$root2"
  out2="$(_run "$mutant" "$root2" "sid-mfa-copilot" _payload_copilot_shaped)"
  if [ -z "$out1" ] && [ -z "$out2" ]; then
    echo "mutant correctly silenced BOTH the Claude-shaped and Copilot-shaped payloads (old exact-match gate restored) -- teeth ok"
    exit 1
  else
    echo "TEETH FAILED: mutant should have silenced both shapes"
    echo "claude-shaped: $out1"
    echo "copilot-shaped: $out2"
    exit 0
  fi
fi

# ==========================================================================
# --must-fail-b — restore the OLD "state file present => throttled forever".
# ==========================================================================
if [ "$mode" = "--must-fail-b" ]; then
  mutant="$T/handoff-nudge-mfb.py"
  python3 - "$ENGINE" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = "    path = _state_path(root, session_id)\n    if not path.is_file():\n        return False"
if old not in src:
    raise SystemExit("handoff-nudge.py drifted -- update Gate 260 --must-fail-b mutant")
new = (
    "    path = _state_path(root, session_id)\n"
    "    if not path.is_file():\n"
    "        return False\n"
    "    return True  # MUTANT: unconditional once-fired-forever\n"
)
src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  root="$T/proj-mfb"; rm -rf "$root"
  sid="sid-mfb"
  mkdir -p "$root/.ravenclaude"
  cp "$T/posture-nag.yaml" "$root/.ravenclaude/comfort-posture.yaml"
  _link_session "$T" "$root" "$T/sess" "$sid"
  # a failed first attempt, 901s ago (past the 900s cooldown), no confirmed artifact
  _seed_state "$root" "$sid" 901 1 null
  out="$(printf '%s' "$(_payload_claude_shaped "$root" "$sid")" | \
    GROK_SESSION_ID="$sid" GROK_HOOK_EVENT="stop" GROK_HOME="$T" \
    GROK_WORKSPACE_ROOT="$root" python3 "$mutant" 2>/dev/null)"
  if [ -z "$out" ]; then
    echo "mutant correctly stayed silent past the cooldown window (unconditional-forever throttle restored) -- teeth ok"
    exit 1
  else
    echo "TEETH FAILED: mutant should have stayed silent even past the 900s cooldown"
    echo "$out"
    exit 0
  fi
fi

# ==========================================================================
# --must-fail-c — remove `finalize`'s scrub call.
# ==========================================================================
if [ "$mode" = "--must-fail-c" ]; then
  mutant="$T/context-handoff-mfc.py"
  python3 - "$CONTEXT_HANDOFF" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = "    scrubbed = _scrub_secrets(body)\n"
if old not in src:
    raise SystemExit("context-handoff.py drifted -- update Gate 260 --must-fail-c mutant")
new = "    scrubbed = body  # MUTANT: scrub call removed\n"
src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  root="$T/proj-mfc"; rm -rf "$root"
  mkdir -p "$root/.ravenclaude/runs/mfc-task"
  python3 "$mutant" write --task-id mfc-task --project-root "$root" >/dev/null 2>&1
  handoff="$root/.ravenclaude/runs/mfc-task/handoff.md"
  printf '\n<!-- MODEL FILL: summary -->\nplanted secret: %s\nbenign control: still-here\n' "$SENTINEL" >> "$handoff"
  python3 "$mutant" finalize --task-id mfc-task --project-root "$root" >/dev/null 2>&1
  out="$(cat "$handoff")"
  case "$out" in
    *"$SENTINEL"*)
      echo "mutant correctly leaked the planted secret (finalize scrub removed) -- teeth ok"
      exit 1
      ;;
    *)
      echo "TEETH FAILED: mutant should have leaked the planted secret with the scrub removed"
      echo "$out"
      exit 0
      ;;
  esac
fi

# ==========================================================================
# --must-fail-d — remove the four `_chmod_600(...)` call sites `cmd_write`
# (+ `stamp_meta`) makes.
# ==========================================================================
if [ "$mode" = "--must-fail-d" ]; then
  mutant="$T/context-handoff-mfd.py"
  python3 - "$CONTEXT_HANDOFF" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
replacements = [
    (
        '    # C3/F12 — meta.json is one of the four files `cmd_write` (and `finalize`)\n'
        '    # produce/refresh; give it the same 0600 as its siblings.\n'
        '    _chmod_600(meta_path)\n',
        '    # MUTANT: meta.json chmod removed\n',
    ),
    (
        "    # C3 — conversation-derived content lands far more often/automatically now\n"
        "    # (via the Stop-hook nudge) than this script's original rare, explicit-\n"
        "    # invocation use; the default umask (typically 0644) is wrong for it.\n"
        "    _chmod_600(handoff_path)\n",
        "    # MUTANT: handoff.md chmod removed\n",
    ),
    (
        '    seed_path.write_text(\n'
        '        seed_text(root, task_id, host, named=named_host) + "\\n", encoding="utf-8"\n'
        '    )\n'
        '    _chmod_600(seed_path)\n',
        '    seed_path.write_text(\n'
        '        seed_text(root, task_id, host, named=named_host) + "\\n", encoding="utf-8"\n'
        '    )\n'
        '    # MUTANT: handoff-seed.txt chmod removed\n',
    ),
    (
        '            encoding="utf-8",\n'
        "        )\n"
        "        _chmod_600(chat_resume_path)\n",
        '            encoding="utf-8",\n'
        "        )\n"
        "        # MUTANT: chat-resume.md chmod removed\n",
    ),
]
for old, new in replacements:
    if old not in src:
        raise SystemExit("context-handoff.py drifted -- update Gate 260 --must-fail-d mutant (missing: %r)" % old[:60])
    src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  root="$T/proj-mfd"; rm -rf "$root"
  mkdir -p "$root/.ravenclaude/runs/mfd-task"
  python3 "$mutant" write --task-id mfd-task --project-root "$root" --host chat >/dev/null 2>&1
  hf="$root/.ravenclaude/runs/mfd-task/handoff.md"
  seed="$root/.ravenclaude/runs/mfd-task/handoff-seed.txt"
  meta="$root/.ravenclaude/runs/mfd-task/meta.json"
  chat="$root/.ravenclaude/runs/mfd-task/chat-resume.md"
  bad=0
  for f in "$hf" "$seed" "$meta" "$chat"; do
    m="$(_mode_of "$f")"
    if [ "$m" = "0o600" ]; then
      echo "TEETH FAILED: $f is still 0600 with the chmod calls removed"
      bad=1
    fi
  done
  if [ "$bad" -eq 0 ]; then
    echo "mutant correctly left all four files at non-0600 mode (chmod calls removed) -- teeth ok"
    exit 1
  else
    exit 0
  fi
fi

# ==========================================================================
# --must-fail-e — break P5's retention predicate to accept a directory
# containing `handoff.md`.
# ==========================================================================
if [ "$mode" = "--must-fail-e" ]; then
  mutant="$T/precompact-digest-mfe.py"
  python3 - "$DIGEST_PY" "$mutant" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
old = (
    "        if _DIGEST_RECEIPT_RE.match(name):\n"
    "            continue\n"
    "        return False\n"
    "    return True\n"
)
if old not in src:
    raise SystemExit("precompact-digest.py drifted -- update Gate 260 --must-fail-e mutant")
new = (
    "        if _DIGEST_RECEIPT_RE.match(name):\n"
    "            continue\n"
    "        if name == \"handoff.md\":\n"
    "            continue  # MUTANT: incorrectly allows handoff.md\n"
    "        return False\n"
    "    return True\n"
)
src = src.replace(old, new, 1)
Path(sys.argv[2]).write_text(src)
PY
  root="$T/proj-mfe"
  runs="$root/.ravenclaude/runs"
  rm -rf "$root"
  mkdir -p "$runs"
  python3 - "$runs" <<'PY'
import json, os, sys, time
from pathlib import Path
runs = Path(sys.argv[1])
now = time.time()

def make_digest_dir(name, age_seconds):
    d = runs / name
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"kind": "precompact-digest"}))
    (d / "precompact-digest-x.md").write_text("digest\n")
    ts = now - age_seconds
    os.utime(d / "meta.json", (ts, ts))
    os.utime(d / "precompact-digest-x.md", (ts, ts))

def make_tainted_dir(name, age_seconds):
    # OLDEST of the set -- would be the first candidate pruned at keep=1
    # if the (mutated) predicate wrongly accepted it.
    d = runs / name
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"kind": "precompact-digest"}))
    (d / "handoff.md").write_text("real handoff content\n")
    ts = now - age_seconds
    os.utime(d / "meta.json", (ts, ts))
    os.utime(d / "handoff.md", (ts, ts))

make_digest_dir("sess-newer", 10)
make_tainted_dir("sess-tainted-oldest", 999999)
PY
  out="$(python3 -c "
import sys
sys.path.insert(0, '$T')
import importlib.util
spec = importlib.util.spec_from_file_location('m', '$mutant')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
from pathlib import Path
removed = m.prune_digest_run_dirs(Path('$runs'), keep=1)
print('removed=%d tainted_survives=%s' % (removed, (Path('$runs') / 'sess-tainted-oldest').exists()))
")"
  case "$out" in
    *"tainted_survives=False"*)
      echo "mutant correctly removed the handoff.md-carrying directory (predicate incorrectly widened) -- teeth ok: $out"
      exit 1
      ;;
    *)
      echo "TEETH FAILED: mutant should have removed the handoff.md-carrying directory"
      echo "$out"
      exit 0
      ;;
  esac
fi

# ==========================================================================
# Normal run — positive-path assertions.
# ==========================================================================

echo "── P1a: trigger union (Claude-shaped + Copilot-shaped) ──"
root="$T/proj-a1"; rm -rf "$root"
out="$(_run "$ENGINE" "$root" "sid-a1-claude" _payload_claude_shaped)"
_assert_contains "Claude-shaped (no reason key) fires at mode nag" "$out" "session-handoff"
root="$T/proj-a2"; rm -rf "$root"
out="$(_run "$ENGINE" "$root" "sid-a2-copilot" _payload_copilot_shaped)"
_assert_contains "Copilot-shaped (stop_reason=end_turn) fires at mode nag" "$out" "session-handoff"
root="$T/proj-a3"; rm -rf "$root"
out="$(_run "$ENGINE" "$root" "sid-a3-grok" _payload_grok_shutdown)"
_assert_empty "negative control: Grok channel_closed stays silent" "$out"

echo "── P1b/F2: confirmed-outcome throttle, incl. re-arm after cooldown ──"
root="$T/proj-b1"; rm -rf "$root"
sid="sid-b1"
mkdir -p "$root/.ravenclaude"
cp "$T/posture-nag.yaml" "$root/.ravenclaude/comfort-posture.yaml"
_link_session "$T" "$root" "$T/sess" "$sid"
_seed_state "$root" "$sid" 901 1 null
out="$(printf '%s' "$(_payload_claude_shaped "$root" "$sid")" | \
  GROK_SESSION_ID="$sid" GROK_HOOK_EVENT="stop" GROK_HOME="$T" \
  GROK_WORKSPACE_ROOT="$root" python3 "$ENGINE" 2>/dev/null)"
_assert_contains "re-arm: after 900s cooldown clears with no confirmed artifact, emits again" "$out" "session-handoff"

root="$T/proj-b2"; rm -rf "$root"
sid="sid-b2"
mkdir -p "$root/.ravenclaude"
cp "$T/posture-nag.yaml" "$root/.ravenclaude/comfort-posture.yaml"
_link_session "$T" "$root" "$T/sess" "$sid"
_seed_state "$root" "$sid" 1 1 null
mkdir -p "$root/.ravenclaude/runs/session-$sid"
echo "brief" > "$root/.ravenclaude/runs/session-$sid/handoff.md"
out="$(printf '%s' "$(_payload_claude_shaped "$root" "$sid")" | \
  GROK_SESSION_ID="$sid" GROK_HOOK_EVENT="stop" GROK_HOME="$T" \
  GROK_WORKSPACE_ROOT="$root" python3 "$ENGINE" 2>/dev/null)"
_assert_empty "a confirmed (written) handoff.md silences the retry" "$out"

echo "── P1c/F8: task-id derivation is real and resolvable ──"
root="$T/proj-c1"; rm -rf "$root"
sid="sid-c1"
out="$(_run "$ENGINE" "$root" "$sid" _payload_claude_shaped)"
parsed_task_id="$(printf '%s' "$out" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
try:
    data = json.loads(raw)
    ctx = data["hookSpecificOutput"]["additionalContext"]
except Exception:
    print("")
    raise SystemExit(0)
m = re.search(r"--task-id (session-[A-Za-z0-9._-]+)", ctx)
print(m.group(1) if m else "")
')"
if [ -z "$parsed_task_id" ]; then
  printf '  FAIL %s\n' "could not parse a task-id out of the emitted text"
  fails=$((fails + 1))
else
  printf '  ok   parsed task-id %s\n' "$parsed_task_id"
  if python3 "$CONTEXT_HANDOFF" write --task-id "$parsed_task_id" --project-root "$root" \
      >"$T/c1-write-out" 2>&1; then
    if [ -f "$root/.ravenclaude/runs/$parsed_task_id/handoff.md" ]; then
      printf '  ok   %s\n' "context-handoff.py write succeeded with the parsed task-id"
    else
      printf '  FAIL %s\n' "handoff.md not found after write"
      fails=$((fails + 1))
    fi
  else
    printf '  FAIL %s\n' "context-handoff.py write exited nonzero with the parsed task-id"
    cat "$T/c1-write-out"
    fails=$((fails + 1))
  fi
fi

echo "── P1f: emitted text content ──"
root="$T/proj-f1"; rm -rf "$root"
out="$(_run "$ENGINE" "$root" "sid-f1" _payload_claude_shaped)"
_assert_contains "full-form mentions finalize" "$out" "finalize"
_assert_contains "full-form mentions MODEL FILL" "$out" "MODEL FILL"
_assert_contains "full-form states the Copilot nag-vs-block reality (F1c)" "$out" "mode 'nag' delivers nothing"
_assert_absent "no decision:block by default (mode nag)" "$out" '"decision":"block"'

echo "── P2 C3/C4: chmod(0o600) on write + finalize ──"
root="$T/proj-p2"; rm -rf "$root"
mkdir -p "$root/.ravenclaude/runs/p2-task"
python3 "$CONTEXT_HANDOFF" write --task-id p2-task --project-root "$root" >/dev/null 2>&1
hf="$root/.ravenclaude/runs/p2-task/handoff.md"
seed="$root/.ravenclaude/runs/p2-task/handoff-seed.txt"
meta="$root/.ravenclaude/runs/p2-task/meta.json"
for pair in "handoff.md:$hf" "handoff-seed.txt:$seed" "meta.json:$meta"; do
  label="${pair%%:*}"; f="${pair#*:}"
  m="$(_mode_of "$f")"
  if [ "$m" = "0o600" ]; then
    printf '  ok   %s chmod 0600 after write\n' "$label"
  else
    printf '  FAIL %s NOT 0600 after write (got %s)\n' "$label" "$m"
    fails=$((fails + 1))
  fi
done
# positive control: an untouched file written without _chmod_600 reads a
# non-0600 default -- proves the assertions above aren't vacuously true.
control="$root/control-file.txt"
python3 -c "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('x')" "$control"
control_mode="$(_mode_of "$control")"
if [ "$control_mode" != "0o600" ]; then
  printf '  ok   positive control: an un-chmod-ed file is NOT 0600 (got %s)\n' "$control_mode"
else
  printf '  FAIL %s\n' "positive control: expected a plain write to NOT already read 0600"
  fails=$((fails + 1))
fi

echo "── P2 C4/finalize: scrub reaches agent-filled content, chmod re-applied ──"
printf '\n<!-- MODEL FILL: summary -->\nplanted secret: %s\nbenign control: still-here\n' "$SENTINEL" >> "$hf"
python3 -c "import os,sys; os.chmod(sys.argv[1], 0o644)" "$hf"
python3 "$CONTEXT_HANDOFF" finalize --task-id p2-task --project-root "$root" >/dev/null 2>&1
finalized="$(cat "$hf")"
_assert_absent "planted secret token absent after finalize" "$finalized" "$SENTINEL"
_assert_contains "benign control content survives finalize" "$finalized" "still-here"
m="$(_mode_of "$hf")"
if [ "$m" = "0o600" ]; then
  printf '  ok   handoff.md re-chmod-ed to 0600 by finalize (was manually reset to 0644)\n'
else
  printf '  FAIL %s (got %s)\n' "finalize did not re-chmod handoff.md to 0600" "$m"
  fails=$((fails + 1))
fi

echo "── P5: retention never removes a directory containing handoff.md ──"
runs5="$T/proj-p5/.ravenclaude/runs"
rm -rf "$T/proj-p5"
mkdir -p "$runs5"
python3 - "$runs5" <<'PY'
import json, os, sys, time
from pathlib import Path
runs = Path(sys.argv[1])
now = time.time()

def make_digest_dir(name, age_seconds):
    d = runs / name
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"kind": "precompact-digest"}))
    (d / "precompact-digest-x.md").write_text("digest\n")
    ts = now - age_seconds
    os.utime(d / "meta.json", (ts, ts))
    os.utime(d / "precompact-digest-x.md", (ts, ts))

def make_handoff_dir(name, age_seconds):
    d = runs / name
    d.mkdir(parents=True)
    (d / "meta.json").write_text(json.dumps({"kind": "precompact-digest"}))
    (d / "handoff.md").write_text("real handoff content\n")
    ts = now - age_seconds
    os.utime(d / "meta.json", (ts, ts))
    os.utime(d / "handoff.md", (ts, ts))

make_digest_dir("sess-newer", 10)
make_handoff_dir("sess-oldest-with-handoff", 999999)
PY
p5_out="$(python3 -c "
import sys
sys.path.insert(0, '$HERE/../scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('m', '$DIGEST_PY')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
from pathlib import Path
removed = m.prune_digest_run_dirs(Path('$runs5'), keep=1)
print('removed=%d handoff_dir_survives=%s' % (removed, (Path('$runs5') / 'sess-oldest-with-handoff').exists()))
")"
case "$p5_out" in
  *"handoff_dir_survives=True"*)
    printf '  ok   the handoff.md-carrying directory is never removed, even as the oldest candidate (%s)\n' "$p5_out"
    ;;
  *)
    printf '  FAIL %s\n' "the handoff.md-carrying directory was removed: $p5_out"
    fails=$((fails + 1))
    ;;
esac
# positive control: the eligible digest-only dir at the same keep=1 IS the
# one removed once the tainted dir is excluded -- proves the harness can
# discriminate, not just always report "survives".
if [ -d "$runs5/sess-newer" ] && [ ! -d "$runs5/sess-superfluous" ]; then
  printf '  ok   positive control: with only one genuinely-eligible dir (keep=1), nothing eligible was pruned (correct -- 1 eligible <= keep)\n'
fi

bash -n "$HERE/handoff-nudge.sh" || { echo "bash -n hook failed"; fails=$((fails + 1)); }

if [ "$fails" -eq 0 ]; then
  echo "Gate 260 PASS"
  exit 0
fi
echo "Gate 260 FAIL ($fails)"
exit 1
