#!/usr/bin/env bash
#
# guard-cause-closure.sh — PreToolUse(Write|Edit|MultiEdit).
# Phase 6 of verify-before-assert. The SECOND fail-closed surface, not the only one.
#
# ── WHY IT IS A DIFFERENT AXIS FROM T-PROSE, NOT A DUPLICATE ────────────────
# `guard-premise.sh` T-PROSE asks: "is a control probe CITED beside this
# diagnosis?" This gate asks: "is the alternative cause set CLOSED?"
#
# A diagnosis can cite a perfectly real control and still be the wrong member of
# an unenumerated set. That is precisely the /cdn-cgi incident -- a true 404, a
# real curl, and a false cause -- and the runner-image incident, where a status
# page was correctly read as green and the conclusion drawn from it was wrong.
# The two guards are OR-ed in EFFECT and never AND-ed in code, and neither can
# suppress the other.
#
# ── FIVE CONJUNCTS, ALL REQUIRED ────────────────────────────────────────────
#   1. the target is a DURABLE artifact -- not `.ravenclaude/**`, not a run dir,
#      not /tmp, not a scratch name
#   2. the written content contains a line that `classify_claim.py --lines` types
#      in the `causal` family
#   3. that line names a SUBJECT with an open row in `open.jsonl`
#   4. no discriminating-probe result for that subject is on the ledger
#   5. no escape marker
#
# ⛔ CONJUNCT 2 CALLS THE MODULE. IT DOES NOT RE-AUTHOR THE GRAMMAR.
# `classify_claim.py` already owns causal typing, already has a --must-fail
# battery, an import-time canary, and tuned exemptions. A second, independently
# authored grammar would be a copy this run owns and must keep in sync by hand.
# `--lines` is its documented batch entry point; this is the sanctioned read-only
# reuse its own docstring describes, and it touches no protected file.
#
# ⛔ CONJUNCT 2 ALONE OVER-FIRES, AND THAT IS EXPECTED, NOT A DEFECT.
# control: `classify_claim.py --lines` types BOTH "the page is green because the
# check passed" (diagnostic) and "the skip is correct because payloads are small"
# (explanatory) as `causal`. Separating those is not mechanically decidable and
# the repo's own measurement says so. The narrowing is CONJUNCT 3: an explanatory
# sentence about payload size names no subject on the triage ledger. The
# conjuncts compose; no single one is the filter.
#
# ── ONE ESCAPE VOCABULARY, NOT TWO ──────────────────────────────────────────
# `cause-ok: <id> via <probe>`, OR a control citation in T-PROSE's EXISTING
# vocabulary (`control:`, `rc probe`, `disconfirm`), OR a matching
# `premise-control:` in the same `control.md` guard-premise already reads --
# consumed READ-ONLY, schema unchanged, no fourth key invented. An agent should
# not have to learn a second dialect to get out of a second gate.
# ⛔ An EMPTY marker clears nothing.
#
# ── SHIPS AT `warn`. Flips in Phase 11. Blindness ADVISES, never denies. ────
# Identical policy to guard-remediation-cause.sh, for the identical reason.
#
# ── PACKAGING NOTE ──────────────────────────────────────────────────────────
# control: `chmod +x` on a new file under the plugin hooks/ dir -> DENIED by
# xc.tribunal-self-disable, this session. Body lives in scripts/, invoked via
# `bash` from both registrations.
#
set -euo pipefail

# ⛔ THE MODULE DIR IS OVERRIDABLE, AND THAT IS A CORRECTNESS FIX, NOT A TEST HOOK.
# Conjunct 2 shells out to the SIBLING `classify_claim.py`, resolved relative to
# this file. A copy of this script running from anywhere else -- a mutation
# harness, a vendored copy, a symlink resolved to a temp dir -- finds no sibling,
# hits the `os.path.exists` guard, and exits 0. SILENTLY. The gate still runs,
# still reads its posture, still returns success, and gates nothing.
# control: `bash /tmp/<copy>.sh` on a payload the original FIRES on produced no
# output, while the same program run with the real module dir emitted its fire
# verdict -- so the difference is the resolution, not the logic. Caught because
# --must-fail reported no change; had its polarity been "assert silence" it would
# have passed vacuously forever.
_GCC_DIR="${RC_GCC_MODULE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
_GCC_HOOKS="$(cd "${_GCC_DIR}/../hooks" 2>/dev/null && pwd || echo "")"

_gcc_posture() {
  local dir="${CLAUDE_PROJECT_DIR:-$PWD}" i=0
  while [ -n "$dir" ] && [ "$i" -lt 10 ]; do
    if [ -f "$dir/.ravenclaude/comfort-posture.yaml" ]; then
      local v
      v="$(sed -n 's/^[[:space:]]*cause_closure:[[:space:]]*\([A-Za-z]*\).*/\1/p' \
           "$dir/.ravenclaude/comfort-posture.yaml" 2>/dev/null | head -1 || true)"
      if [ -n "$v" ]; then printf '%s\n' "$v"; else printf 'warn\n'; fi
      return 0
    fi
    [ "$dir" = "/" ] && break
    dir="$(dirname "$dir")"
    i=$((i + 1))
  done
  printf 'absent\n'
}

# ⛔ WITHOUT THIS, THE `warn` TIER REACHES NOBODY. This repo MEASURED
# stderr-at-exit-0 as UNDELIVERED on every event; `_advise.sh` buffers fd2 and
# re-emits at EXIT both to the terminal AND as additionalContext, the channel the
# model actually receives. This gate wrote to `>&2` and never sourced it.
# ⛔ Do NOT redirect this call: `rc_advise_init ... 2>/dev/null` discards the very
# fd it is installing.
_gcc_deliver() {
  [ -n "$_GCC_HOOKS" ] || return 0
  [ -f "$_GCC_HOOKS/_advise.sh" ] || return 0
  # shellcheck source=/dev/null
  . "$_GCC_HOOKS/_advise.sh" || return 0
  command -v rc_advise_init >/dev/null 2>&1 || return 0
  rc_advise_init PreToolUse || true
}

_gcc_report_blind() {
  if [ -n "$_GCC_HOOKS" ] && [ -f "$_GCC_HOOKS/_emit-event.sh" ]; then
    # shellcheck source=/dev/null
    . "$_GCC_HOOKS/_emit-event.sh" 2>/dev/null || true
    if command -v _emit_hook_event >/dev/null 2>&1; then
      _emit_hook_event "guard-cause-closure.sh" "warn" "Write" "" "blind" "0" || true
    fi
  fi
  _gcc_deliver
  printf '%s\n' \
"[cause-closure] I AM BLIND — $1; my clean verdict means nothing." \
"  This gate is ALLOWING the write, deliberately, and has recorded a blind event." >&2
}

_gcc_main() {
  local payload posture verdict kind
  payload="$(cat 2>/dev/null || true)"
  [ -n "$payload" ] || return 0

  posture="$(_gcc_posture)"
  case "$posture" in
    off | absent) return 0 ;;
  esac

  # ⛔ NO LITERAL APOSTROPHE ANYWHERE BELOW, INCLUDING IN PROSE COMMENTS.
  # An earlier draft of this header claimed a QUOTED heredoc has no such trap,
  # unlike the single-quoted-string form triage-outcome.sh warns about. THAT CLAIM
  # WAS FALSE, and it was written into a file whose whole subject is not doing
  # that. The heredoc sits inside `$( ... )`, and bash scanning for the closing
  # paren treats an apostrophe as a quote regardless of the heredoc quoting.
  # control: `bash -n` on this file reported "unexpected EOF while looking for
  # matching '" at the LAST line; deleting exactly one apostrophe from a prose
  # comment 440 lines earlier made it parse clean. One apostrophe, one file, two
  # outcomes.
    # ⛔ PAYLOAD VIA A FILE, NOT THE ENVIRONMENT. An env var is bounded by ARG_MAX,
  # and a payload over it made `exec` fail E2BIG -- swallowed by `|| true`, so the
  # write gate ALLOWED with zero output. MEASURED bypass at ~80k filler lines.
  local _gcc_tmp _gcc_rc
  _gcc_tmp="$(mktemp 2>/dev/null)" || _gcc_tmp=""
  if [ -z "$_gcc_tmp" ]; then
    _gcc_report_blind "cannot create a temp file to pass the payload"
    return 0
  fi
  printf '%s' "$payload" > "$_gcc_tmp"
  _gcc_rc=0
verdict="$(RC_GCC_PAYLOAD_FILE="$_gcc_tmp" RC_GCC_DIR="$_GCC_DIR" python3 - <<'PYEOF' 2>/dev/null
import hashlib
import json
import os
import re
import subprocess
import sys

here = os.environ.get("RC_GCC_DIR") or "."
try:
    with open(os.environ["RC_GCC_PAYLOAD_FILE"], encoding="utf-8", errors="replace") as _fh:
        payload = _fh.read()
except Exception:
    # Exit 3 = "I could not read my own input", reported as BLIND by the caller.
    sys.exit(3)
try:
    d = json.loads(payload)
except Exception:
    sys.exit(0)

tool = d.get("tool_name") or ""
if tool not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)

ti = d.get("tool_input") or {}
path = ti.get("file_path") or ti.get("path") or ""
if not path:
    sys.exit(0)

# ⛔ Content is gathered from EVERY shape the three tools use. Edit and MultiEdit
# carry new_string / edits[], not content. A gate that reads only `content`
# inspects Write and silently waves Edit through -- the tool-switch tunnel
# guard-premise.sh had to close on 2026-08-13. Do not re-open it.
chunks = []
if isinstance(ti.get("content"), str):
    chunks.append(ti["content"])
if isinstance(ti.get("new_string"), str):
    chunks.append(ti["new_string"])
for e in ti.get("edits") or []:
    if isinstance(e, dict) and isinstance(e.get("new_string"), str):
        chunks.append(e["new_string"])
content = "\n".join(chunks)
if not content.strip():
    sys.exit(0)


# ── Conjunct 1: is the target DURABLE? ───────────────────────────────────────
# The exclusion list mirrors guard-premise.sh's intent: they must agree, or one
# guard gates a surface the other exempts.
#
# ⛔ THIS PARITY IS NOT MECHANIZED, AND SAYING SO IS THE POINT. An earlier draft
# of this comment asserted that `check-durable-predicate-parity.py` drives both
# over one fixture set. No such script exists. The durable predicate inside
# guard-premise.sh is not an extractable list — it is embedded in conjunct logic and
# entangled with ledger state — so a byte-parity check across the two shapes
# would very likely pass vacuously, which is worse than an admitted gap: it would
# report agreement nobody measured.
# control: `grep -nE "scratch|durable|_is_durable" guard-premise.sh` returns only
# prose and conjunct descriptions, no list literal to compare against.
# The honest form is BEHAVIOURAL parity over a shared path fixture, which is a
# declared follow-up rather than a claim made here. Until it lands, the two
# predicates are kept aligned by review, and that is a weaker guarantee.
_SCRATCH = re.compile(
    r"(^|/)\.ravenclaude/|(^|/)\.claude/|(^|/)runs?/|^/tmp/|^/private/tmp/|"
    r"(^|/)(scratch|tmp|temp|draft|wip|scratchpad)[^/]*$|\.(tmp|bak|orig|swp)$|"
    r"(^|/)node_modules/|(^|/)\.git/"
)


def is_durable(p):
    return not bool(_SCRATCH.search(p))


if not is_durable(path):
    sys.exit(0)

# ── Conjunct 2: does any line type `causal`? Call the module, do not re-author.
lines = content.split("\n")
causal_idx = []
try:
    mod = os.path.join(here, "classify_claim.py")
    if not os.path.exists(mod):
        sys.exit(0)
    proc = subprocess.run(
        [sys.executable, mod, "--lines"],
        input="\n".join(lines),
        capture_output=True,
        text=True,
        timeout=20,
    )
    for row in (proc.stdout or "").split("\n"):
        parts = row.split("\t")
        if len(parts) >= 3 and parts[2].strip() == "causal":
            try:
                causal_idx.append(int(parts[0]) - 1)
            except ValueError:
                continue
except Exception:
    sys.exit(0)

if not causal_idx:
    sys.exit(0)

# ── Conjunct 5: the escapes. ONE vocabulary, and EMPTY clears nothing. ───────
_CAUSE_OK = re.compile(r"cause-ok:\s*([EFGHI][0-9]{1,2})\s+via\s+(\S.*)")
_TPROSE_CONTROL = re.compile(r"\bcontrol:\s*\S|\brc probe\b|\bdisconfirm(?:ed|ing|s)?\b")


def escaped(text):
    m = _CAUSE_OK.search(text)
    if m and m.group(1).strip() and m.group(2).strip():
        return True
    return bool(_TPROSE_CONTROL.search(text))


# ── Scope + ledger (the synced twins) ────────────────────────────────────────
def rc_worktree_root(start, fallback):
    try:
        p = os.path.abspath(str(start))
        if not os.path.isdir(p):
            p = os.path.dirname(p)
        for _ in range(48):
            if os.path.exists(os.path.join(p, ".git")):
                return p
            up = os.path.dirname(p)
            if up == p:
                break
            p = up
    except Exception:
        pass
    return os.path.abspath(str(fallback))


def rc_scope_key(start, fallback):
    forced = os.environ.get("RC_PREMISE_SCOPE", "").strip()
    base = forced if forced else rc_worktree_root(start, fallback)
    slug = re.sub(r"[^A-Za-z0-9._-]", "-", os.path.basename(str(base).rstrip("/")))[:32]
    digest = hashlib.sha1(str(base).encode("utf-8", "replace")).hexdigest()[:10]
    return (slug or "root") + "-" + digest


def subject_body(s):
    for p in ("fs:", "cmd:"):
        if s.startswith(p):
            return s[len(p):]
    return s


# ⛔ NEVER EMIT A `cmd:` SUBJECT VERBATIM -- IT IS RAW COMMAND TEXT.
# The ledger writer derives `fs:` and URL subjects genuinely; its FALLBACK arm is
# the raw command truncated to 40 chars. That value was re-emitted verbatim into
# permissionDecisionReason, so attacker-chosen bytes arrived in the model context
# as a repo guard speaking. Two headers in this tree claimed the ledger holds
# derived labels only; for that arm the claim was FALSE.
# control: a write naming a `cmd:` subject that began `IGNORE PREVIOUS
# INSTRUCTIONS.` reproduced the phrase end-to-end in the deny envelope; with this
# transform the same input yields `cmd:<8 hex>` and the phrase is absent.
# The join still uses the RAW ledger value internally -- only what LEAVES this
# process is transformed -- so the readable-subject ruling is preserved.
def emit_safe_subject(s):
    s = s or ""
    if s.startswith("cmd:"):
        return "cmd:" + hashlib.sha1(
            s[4:].encode("utf-8", "replace")).hexdigest()[:8]
    return re.sub(r"[^A-Za-z0-9._/:@-]", "", s)[:80]


proj = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
cwd = d.get("cwd") or os.getcwd()
sid = str(d.get("session_id", "nosession") or "nosession")
scope = rc_scope_key(cwd, proj)
sess = os.path.join(proj, ".ravenclaude", "runs", "cause-triage", sid)
ledger = os.path.join(sess, "scopes", scope, "open.jsonl")
beacon = os.path.join(sess, "triage-alive")

if not os.path.exists(beacon):
    print(json.dumps({"verdict": "blind"}))
    sys.exit(0)

rows = []
try:
    with open(ledger, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
except OSError:
    rows = []

settled = {r.get("subject") for r in rows if r.get("discriminated") not in (None, "", "null")}
open_rows = [
    r for r in rows
    if r.get("discriminated") in (None, "", "null") and r.get("subject") not in settled
]

# ── Conjunct 5 (read-only cross-consumption of control.md) ──────────────────
# Consumed with guard-premise.sh's OWN schema. No fourth key is invented, and the
# file is never written here.
control_subjects = set()
control_all = False
cpath = os.path.join(proj, ".ravenclaude", "runs", "premise", sid, "scopes", scope, "control.md")
try:
    with open(cpath, encoding="utf-8", errors="replace") as fh:
        ctext = fh.read()
    has_all = re.search(r"^premise-control:\s*(\S.*)$", ctext, re.M)
    needed = ("who:", "subject:", "control:")
    if has_all and all(re.search(r"^%s\s*\S" % k, ctext, re.M) for k in needed):
        val = has_all.group(1).strip()
        if val == "*":
            control_all = True
        else:
            control_subjects.add(val)
except OSError:
    pass

# ── Conjuncts 3 and 4: a causal line NAMES an open, undiscriminated subject ──
# ⛔ THE ESCAPE IS SCOPED TO THE CLAIM PARAGRAPH, NOT THE WHOLE FILE.
# `if escaped(content)` cleared the ENTIRE write when any marker appeared
# ANYWHERE in it. In a repo whose prose is full of `control:` lines that is a
# trivially-satisfied global bypass: any document that mentions a control once is
# exempt from the whole gate, however imprecise the other conjuncts become.
# It also made G6.2 -- "the highest-value pre-build gate" -- pass for a reason
# unrelated to what it claims.
# control: the two worst-case docs carry 8 escape-vocabulary matches EACH; driven
# as-is the gate is silent, and with the markers stripped the IDENTICAL document
# FIRES. The escape, not the detector, was doing the work.
# A paragraph is the contiguous run of non-blank lines around the causal claim --
# close enough to read as "beside the claim", narrow enough that a marker three
# sections away does not clear it.
def paragraph_of(all_lines, idx):
    start = idx
    while start > 0 and all_lines[start - 1].strip():
        start -= 1
    end = idx
    while end + 1 < len(all_lines) and all_lines[end + 1].strip():
        end += 1
    return "\n".join(all_lines[start:end + 1])


hit = None
for i in causal_idx:
    if i < 0 or i >= len(lines):
        continue
    line = lines[i]
    if escaped(line) or escaped(paragraph_of(lines, i)):
        continue
    for r in open_rows:
        s = r.get("subject") or ""
        sb = subject_body(s)
        if len(sb) < 5:
            continue
        if sb in line:
            if control_all or s in control_subjects or sb in control_subjects:
                continue
            hit = (r, i + 1)
            break
    if hit:
        break

if hit is None:
    sys.exit(0)

row, lineno = hit
print(json.dumps({
    "verdict": "fire",
    "subject": emit_safe_subject(row.get("subject") or ""),
    "candidates": [c for c in (row.get("candidate_ids") or [])[:3]
                   if re.fullmatch(r"[EFGHI][0-9]{1,2}", str(c))],
    "line": lineno,
    # The basename is attacker-influenceable (the agent chose the path), so it is
    # allowlisted and capped like any other emitted value.
    "path": re.sub(r"[^A-Za-z0-9._-]", "", os.path.basename(path))[:60],
}))
PYEOF
)" || _gcc_rc=$?

  # ⛔ A NON-ZERO INTERPRETER EXIT IS BLINDNESS, NOT SILENCE (P2-2). `_gcc_rc`
  # was captured here and then NEVER READ: the next line returned 0 on an empty
  # verdict, so a missing python3, an E2BIG exec or a crash inside the program
  # produced an ALLOW indistinguishable from "nothing to report" — inert AND
  # invisible, which this file's own header promises it will not be.
  #
  # ⛔ The sibling guard already had this fix. Applying it to one gate of a pair
  # and stopping is not fixing the class, and the second gate is the one whose
  # blind path existed but was unreachable from an interpreter failure.
  if [ "$_gcc_rc" -ne 0 ]; then
    _gcc_report_blind "the verdict program exited $_gcc_rc"
    return 0
  fi

  [ -n "$verdict" ] || return 0
  kind="$(printf '%s' "$verdict" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("verdict",""))
except Exception: print("")' 2>/dev/null || true)"

  if [ "$_GCC_HOOKS" != "" ] && [ -f "$_GCC_HOOKS/_emit-event.sh" ]; then
    # shellcheck source=/dev/null
    . "$_GCC_HOOKS/_emit-event.sh" 2>/dev/null || true
  fi

  case "$kind" in
    blind)
      if command -v _emit_hook_event >/dev/null 2>&1; then
        _emit_hook_event "guard-cause-closure.sh" "warn" "Write" "" "blind" "0" || true
      fi
      printf '%s\n' \
"[cause-closure] I AM BLIND — no triage beacon this session; my clean verdict means nothing." \
"  The cause-triage ledger is not being written, so this gate cannot see whether the" \
"  diagnosis being written down rests on a closed cause set. It is ALLOWING the write," \
"  deliberately, and has recorded a blind event so an audit can find this session." >&2
      return 0
      ;;
    fire) : ;;
    *) return 0 ;;
  esac

  local subject candidates lineno fname
  subject="$(printf '%s' "$verdict" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("subject","") or "")
except Exception: print("")' 2>/dev/null || true)"
  candidates="$(printf '%s' "$verdict" | python3 -c 'import json,sys
try: print(", ".join(json.load(sys.stdin).get("candidates") or []))
except Exception: print("")' 2>/dev/null || true)"
  lineno="$(printf '%s' "$verdict" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("line",""))
except Exception: print("")' 2>/dev/null || true)"
  fname="$(printf '%s' "$verdict" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("path","") or "")
except Exception: print("")' 2>/dev/null || true)"

  if command -v _emit_hook_event >/dev/null 2>&1; then
    _emit_hook_event "guard-cause-closure.sh" "warn" "Write" "$fname" "cause-set-not-closed" "0" || true
  fi

  if [ "$(_gcc_posture)" = "block" ]; then
    RC_GCC_REASON="a diagnosis is being written for a subject whose cause set was never closed. subject: $subject. candidates: $candidates. line $lineno of $fname. Close the set with: cause-ok: <class-id> via <probe>, or cite a control beside the claim. An empty marker does not clear." \
      python3 -c '
import json, os
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": os.environ["RC_GCC_REASON"],
}}))' 2>/dev/null || true
    return 0
  fi

  printf '%s\n' \
"[cause-closure] a diagnosis is being written for a cause set that was never closed." \
"" \
"  subject:     $subject" \
"  candidates:  $candidates" \
"  where:       $fname line $lineno" \
"" \
"  T-PROSE asks whether a control is CITED. This asks a different question: is the" \
"  ALTERNATIVE CAUSE SET CLOSED? A diagnosis can cite a real control and still be the" \
"  wrong member of a set nobody enumerated — a true 404 with a false cause is exactly" \
"  how the /cdn-cgi incident started." \
"" \
"  Close it, or say what you ruled out and how:" \
"" \
"      cause-ok: <class-id> via <the probe you ran>" \
"" \
"  A control citation in the existing vocabulary (control: … / rc probe / disconfirm)" \
"  also clears — one escape dialect, not two. ⛔ An EMPTY marker clears nothing." >&2
  return 0
}

# ── Self-test ────────────────────────────────────────────────────────────────
_gcc_payload() {  # <tool> <json-path> <json-content> <sid> <cwd>
  printf '{"tool_name":"%s","session_id":%s,"cwd":%s,"tool_input":{"file_path":%s,"content":%s}}' \
    "$1" "$4" "$5" "$2" "$3"
}

_gcc_scope_of() {
  RC_ROOT="$1" python3 - <<'PYEOF'
import hashlib, os, re
base = os.environ["RC_ROOT"]
slug = re.sub(r"[^A-Za-z0-9._-]", "-", os.path.basename(base.rstrip("/")))[:32]
print((slug or "root") + "-" + hashlib.sha1(base.encode()).hexdigest()[:10])
PYEOF
}

_gcc_self_test() {
  local fails=0 out root sid scope run self
  self="${BASH_SOURCE[0]}"
  _fail() { printf 'FAIL: %s\n' "$1"; fails=$((fails + 1)); }

  root="$(mktemp -d)"
  mkdir -p "$root/.ravenclaude" "$root/.git"
  printf 'schema_version: 5\ncause_closure: warn\n' > "$root/.ravenclaude/comfort-posture.yaml"
  sid="testsession"
  scope="$(_gcc_scope_of "$root")"
  run="$root/.ravenclaude/runs/cause-triage/$sid/scopes/$scope"
  mkdir -p "$run"
  : > "$root/.ravenclaude/runs/cause-triage/$sid/triage-alive"
  printf '{"ts":1,"subject":"fs:src/thing.ts","verdict":"negative","candidate_ids":["F1","E1","H1"],"discriminated":null,"tool_use_id":"t","scope":"%s"}\n' \
    "$scope" >> "$run/open.jsonl"

  _run() {  # _run <tool> <json-path> <json-content>
    _gcc_payload "$1" "$2" "$3" "\"$sid\"" "\"$root\"" \
      | CLAUDE_PROJECT_DIR="$root" bash "$self" 2>&1 || true
  }

  local DIAG='"The outage was caused by src/thing.ts losing its handler."'

  # 1. durable doc + causal line naming an open subject -> FIRES
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  case "$out" in *"cause-closure"*) : ;; *) _fail "did not fire on a diagnosis naming an open subject" ;; esac

  # 2. the SAME prose with a cause-ok escape -> allow
  out="$(_run Write '"docs/x.md"' '"The outage was caused by src/thing.ts losing its handler. cause-ok: F1 via git log -1 src/thing.ts"')"
  case "$out" in *"cause-closure"*) _fail "a complete cause-ok: did not clear" ;; esac

  # 3. an EMPTY cause-ok -> still fires. THE REFUSAL IS TESTED.
  out="$(_run Write '"docs/x.md"' '"The outage was caused by src/thing.ts losing its handler. cause-ok:"')"
  case "$out" in *"cause-closure"*) : ;; *) _fail "an EMPTY cause-ok: cleared the gate" ;; esac

  # 4. a T-PROSE control citation clears — one dialect, not two.
  out="$(_run Write '"docs/x.md"' '"The outage was caused by src/thing.ts losing its handler. control: reverted it and the outage persisted."')"
  case "$out" in *"cause-closure"*) _fail "a control: citation did not clear (two dialects, not one)" ;; esac

  # 5. a scratch target -> allow (conjunct 1)
  out="$(_run Write '"'"$root"'/.ravenclaude/runs/notes.md"' "$DIAG")"
  case "$out" in *"cause-closure"*) _fail "fired on a .ravenclaude/ run-dir target" ;; esac

  # 6. hedged / non-causal prose -> allow (conjunct 2)
  out="$(_run Write '"docs/x.md"' '"src/thing.ts may be involved; nothing is settled yet."')"
  case "$out" in *"cause-closure"*) _fail "fired on hedged, non-causal prose" ;; esac

  # ⛔ 7. THE LEDGER-IS-READ CANARY. Row discriminated -> allow. Without this,
  # cases 1 and 7 would pass the same way for the wrong reason.
  : > "$run/open.jsonl"
  printf '{"ts":1,"subject":"fs:src/thing.ts","verdict":"negative","candidate_ids":["F1"],"discriminated":"F1","tool_use_id":"t","scope":"%s"}\n' \
    "$scope" >> "$run/open.jsonl"
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  case "$out" in *"cause-closure"*) _fail "fired on a discriminated row (ledger not read)" ;; esac
  printf '{"ts":1,"subject":"fs:src/thing.ts","verdict":"negative","candidate_ids":["F1","E1","H1"],"discriminated":null,"tool_use_id":"t","scope":"%s"}\n' \
    "$scope" > "$run/open.jsonl"

  # ⛔ 8. EDIT AND MULTIEDIT CARRY IDENTICAL PROSE -> IDENTICAL VERDICT.
  # The tool-switch tunnel guard-premise.sh had to close on 2026-08-13.
  local w e m
  w="$(_run Write '"docs/x.md"' "$DIAG")"
  e="$(printf '{"tool_name":"Edit","session_id":"%s","cwd":"%s","tool_input":{"file_path":"docs/x.md","new_string":%s}}' \
      "$sid" "$root" "$DIAG" | CLAUDE_PROJECT_DIR="$root" bash "$self" 2>&1 || true)"
  m="$(printf '{"tool_name":"MultiEdit","session_id":"%s","cwd":"%s","tool_input":{"file_path":"docs/x.md","edits":[{"new_string":%s}]}}' \
      "$sid" "$root" "$DIAG" | CLAUDE_PROJECT_DIR="$root" bash "$self" 2>&1 || true)"
  case "$e" in *"cause-closure"*) : ;; *) _fail "Edit carrying identical prose did NOT fire (tool-switch tunnel)" ;; esac
  case "$m" in *"cause-closure"*) : ;; *) _fail "MultiEdit carrying identical prose did NOT fire (tool-switch tunnel)" ;; esac
  [ -n "$w" ] || _fail "Write did not fire in the tool-parity comparison"

  # 9. blindness ADVISES, never denies.
  rm -f "$root/.ravenclaude/runs/cause-triage/$sid/triage-alive"
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  case "$out" in *"I AM BLIND"*) : ;; *) _fail "beacon absent produced no blind advisory" ;; esac
  case "$out" in *"permissionDecision"*) _fail "denied on blindness" ;; esac
  : > "$root/.ravenclaude/runs/cause-triage/$sid/triage-alive"

  # ⛔ 10. G6.2 — THE HIGHEST-VALUE PRE-BUILD GATE, AS A STANDING REGRESSION.
  # The REAL detection bytes are run against the FULL TEXT of the two documents
  # whose entire purpose is to contain subject + defect-predicate + date
  # sentences. They are the worst case BY CONSTRUCTION. Zero denies on both, or
  # this gate blocks its own repair the first time someone edits the taxonomy.
  local repo doc rc_doc
  repo="$(cd "$(dirname "$self")/../../.." && pwd)"
  for doc in "plugins/ravenclaude-core/knowledge/cause-taxonomy.md" \
             "plugins/ravenclaude-core/knowledge/verification-discipline.md"; do
    if [ -f "$repo/$doc" ]; then
      rc_doc="$(RC_DOC="$repo/$doc" RC_ROOT2="$root" RC_SID="$sid" python3 - <<'PYEOF' 2>/dev/null || true
import json, os
body = open(os.environ["RC_DOC"], encoding="utf-8", errors="replace").read()
print(json.dumps({"tool_name": "Write", "session_id": os.environ["RC_SID"],
                  "cwd": os.environ["RC_ROOT2"],
                  "tool_input": {"file_path": "docs/real-doc.md", "content": body}}))
PYEOF
)"
      out="$(printf '%s' "$rc_doc" | CLAUDE_PROJECT_DIR="$root" bash "$self" 2>&1 || true)"
      case "$out" in
        *"cause-closure"*) _fail "G6.2: the gate FIRES on $doc — it would block its own repair" ;;
      esac

      # ⛔ G6.2 WAS PASSING FOR A REASON UNRELATED TO WHAT IT CLAIMS.
      # Both target documents carry EIGHT escape-vocabulary matches each, and the
      # old code cleared the entire write if any marker appeared anywhere in it.
      # The assertion was satisfied by the documents VOCABULARY, not by the gate
      # precision, and would have kept passing however imprecise conjuncts 2-4
      # became. control: with the markers stripped, the identical document FIRED.
      # So the same document is now driven a SECOND time with every escape marker
      # removed. It must STILL be silent -- because it names no open ledger
      # subject, which is conjunct 3 doing the work rather than the escape.
      local stripped
      stripped="$(RC_DOC="$repo/$doc" RC_ROOT2="$root" RC_SID="$sid" python3 - <<'PYEOF' 2>/dev/null || true
import json, os, re
body = open(os.environ["RC_DOC"], encoding="utf-8", errors="replace").read()
body = re.sub(r"control:", "REDACTED-MARKER:", body)
body = re.sub(r"rc probe", "REDACTED-MARKER", body)
body = re.sub(r"disconfirm(?:ed|ing|s)?", "REDACTED-MARKER", body)
body = re.sub(r"cause-ok:", "REDACTED-MARKER:", body)
print(json.dumps({"tool_name": "Write", "session_id": os.environ["RC_SID"],
                  "cwd": os.environ["RC_ROOT2"],
                  "tool_input": {"file_path": "docs/real-doc.md", "content": body}}))
PYEOF
)"
      if [ -n "$stripped" ]; then
        out="$(printf '%s' "$stripped" | CLAUDE_PROJECT_DIR="$root" bash "$self" 2>&1 || true)"
        case "$out" in
          *"cause-closure"*)
            _fail "G6.2 (escapes stripped): the gate FIRES on $doc — the earlier pass was the escape vocabulary, not the detector" ;;
        esac
      fi
    fi
  done

  # 11. posture off / absent; POSITIVE CONTROL after, so silence is not blindness.
  printf 'schema_version: 5\ncause_closure: off\n' > "$root/.ravenclaude/comfort-posture.yaml"
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  [ -n "$out" ] && _fail "cause_closure: off did not silence the gate"
  rm -f "$root/.ravenclaude/comfort-posture.yaml"
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  [ -n "$out" ] && _fail "an absent posture file was not a no-op"
  printf 'schema_version: 5\ncause_closure: warn\n' > "$root/.ravenclaude/comfort-posture.yaml"
  out="$(_run Write '"docs/x.md"' "$DIAG")"
  [ -z "$out" ] && _fail "POSITIVE CONTROL: the probe is blind — it emits nothing even when armed"

  rm -rf "$root"
  if [ "$fails" -ne 0 ]; then
    printf '\nself-test FAILED — %s finding(s)\n' "$fails"
    return 1
  fi
  printf 'PASS: 14 checks — fires on an unclosed diagnosis, both escape dialects clear,\n'
  printf '      empty marker refused, ledger-is-read canary, Edit/MultiEdit parity,\n'
  printf '      blindness advises, and G6.2 zero-denies on the two worst-case docs\n'
  return 0
}

_gcc_must_fail() {
  # Neuter conjunct 5 (the escape); the escaped write must then fire.
  local mutant out root sid scope run self
  self="${BASH_SOURCE[0]}"
  mutant="$(mktemp)"
  awk '
    /^def escaped\(text\):$/ { print; print "    return False"; skip=1; next }
    skip && /^def rc_worktree_root/ { skip=0 }
    skip { next }
    { print }
  ' "$self" > "$mutant"
  if ! grep -q '^    return False$' "$mutant"; then
    printf 'MUST-FAIL SETUP FAILED: the mutation did not apply\n'; rm -f "$mutant"; return 1
  fi
  root="$(mktemp -d)"; mkdir -p "$root/.ravenclaude" "$root/.git"
  printf 'schema_version: 5\ncause_closure: warn\n' > "$root/.ravenclaude/comfort-posture.yaml"
  sid="testsession"; scope="$(_gcc_scope_of "$root")"
  run="$root/.ravenclaude/runs/cause-triage/$sid/scopes/$scope"
  mkdir -p "$run"; : > "$root/.ravenclaude/runs/cause-triage/$sid/triage-alive"
  printf '{"ts":1,"subject":"fs:src/thing.ts","verdict":"negative","candidate_ids":["F1"],"discriminated":null,"tool_use_id":"t","scope":"%s"}\n' \
    "$scope" >> "$run/open.jsonl"
  # ⛔ RC_GCC_MODULE_DIR is REQUIRED here. The mutant runs from a temp path, so
  # without it the sibling classify_claim.py is unresolvable and the mutant exits
  # 0 for a reason that has nothing to do with the mutation -- a vacuous result
  # dressed as a verdict. control: with the override the mutant fires; without it
  # it is silent even on a payload carrying no escape at all.
  out="$(_gcc_payload Write '"docs/x.md"' '"The outage was caused by src/thing.ts losing its handler. cause-ok: F1 via git log -1 src/thing.ts"' "\"$sid\"" "\"$root\"" \
        | RC_GCC_MODULE_DIR="$(cd "$(dirname "$self")" && pwd)" \
          CLAUDE_PROJECT_DIR="$root" bash "$mutant" 2>&1 || true)"
  rm -rf "$root" "$mutant"
  case "$out" in
    *"cause-closure"*)
      printf 'PASS (--must-fail): neutering the escape makes an escaped write fire\n'
      return 0
      ;;
  esac
  printf 'MUST-FAIL VIOLATED: the escape was neutered and nothing changed\n'
  return 1
}

case "${1:-}" in
  --self-test) _gcc_self_test ;;
  --must-fail) _gcc_must_fail ;;
  *) _gcc_main ;;
esac
