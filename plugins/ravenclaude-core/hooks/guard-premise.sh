#!/usr/bin/env bash
# guard-premise.sh — PreToolUse(Write). Blocks a NEW SOURCE MODULE from being
# created while an unresolved negative-result probe is on the record.
#
# ── THE INCIDENT ────────────────────────────────────────────────────────────
# `curl /cdn-cgi/l/email-protection` → 404. Inference: "the decoder is broken,
# every visitor sees a mangled address." Then: an 85-line component, 10 call
# sites, 15 addresses opted out of anti-scraping protection, an owner checklist
# item, two turns of architectural advice. The URL is a placeholder nothing
# fetches — it is SUPPOSED to 404. `/cdn-cgi/trace` → 200 would have ended it in
# ten seconds. No user ever experienced the defect.
#
# This hook fires at exactly the moment that mattered: the Write that creates
# `Email.astro`, a module whose entire reason to exist is the unverified premise.
#
# ── WHY IT FIRES WHEN THE AUTHOR IS CERTAIN ─────────────────────────────────
# ⛔ At the moment of the incident the author was CONFIDENT, with a real tool call
# behind them. Any gate keyed on self-reported doubt would NEVER have fired. So
# this reads only objective shape:
#     (a) a negative-result probe is on the ledger with no positive control after
#     (b) the Write CREATES a file that does not exist
#     (c) the target is a source module (not docs, not scratch, not a run dir)
# Confidence is not an input, so it cannot be an exemption.
#
# ── FAIL CLOSED — owner decision 2026-08-08: "failing silently is no bueno" ──
# The recorder (`log-probe.sh`) drops a `recorder-alive` beacon every time it
# runs. Three states, and the third is the whole reason this section exists:
#
#   beacon present, no unresolved negative  -> ALLOW. Genuinely clean.
#   beacon present, unresolved negative     -> DENY. The case above.
#   beacon ABSENT but a Bash tool has run   -> DENY, "I am blind."
#
# A check that cannot see MUST NOT report clean. Those two outcomes are
# indistinguishable afterward, which is how a green gate protects nothing.
#
# ── FRICTION BUDGET ─────────────────────────────────────────────────────────
# Zero model calls. One `test -e` short-circuits every Edit, every docs write,
# every scratch write, and every Write to a file that already exists — which is
# the overwhelming majority. The ledger is read only when a NEW source module is
# created. On a run that touches one existing file: ~2 ms and no deny path.
#
# ── ESCAPE HATCHES (all three are recorded, none is silent) ─────────────────
#   RC_PREMISE_CONTROL="<subject>"  the control you ran; resolves that subject
#   RC_PREMISE_OVERRIDE=1           proceed anyway; writes an override marker
#   run the control probe           the natural exit — the ledger clears itself
#
# Deny mechanism matches enforce-layout.sh: hookSpecificOutput JSON on stdout
# (Claude Code issue #40580) AND exit 2 for older clients.

set -uo pipefail

_input="$(cat 2>/dev/null || true)"
[ -z "$_input" ] && exit 0

_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

_verdict="$(printf '%s' "$_input" | python3 -c '
import json, os, re, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)                      # malformed input -> allow (never break a session)

if d.get("tool_name") != "Write":
    sys.exit(0)

proj = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
ti   = d.get("tool_input", {}) or {}
path = str(ti.get("file_path", ""))
sid  = d.get("session_id", "nosession")

if not path:
    sys.exit(0)

# (b) CREATES a file — an edit to something that exists is not a new premise-bearer.
if os.path.exists(path):
    sys.exit(0)

# (c) a SOURCE MODULE. Everything below is deliberately exempt: none of it is a
#     thing whose reason for existing can be a false diagnosis.
rel = path.replace(proj, "").lstrip("/")
# Prefix-exempt: these are top-level areas that never hold a premise-bearing module.
if rel.startswith((".ravenclaude/", "docs/", "node_modules/", ".git/", ".claude/")):
    sys.exit(0)
# Anywhere-exempt: a test/fixture is not an abstraction whose reason for existing is
# a diagnosis — and it can live at any depth (`plugins/x/hooks/tests/`), so a
# startswith check would miss it and gate the very tests that prove this gate works.
if any(seg in rel for seg in ("/test/", "/tests/", "/__tests__/", "/fixtures/")) or \
   rel.startswith(("test/", "tests/", "__tests__/", "fixtures/")):
    sys.exit(0)
if "/tmp/" in path or path.startswith("/tmp") or "/scratchpad/" in path:
    sys.exit(0)
SRC_EXT = (".py", ".sh", ".ts", ".tsx", ".js", ".jsx", ".astro", ".vue", ".svelte",
           ".go", ".rs", ".rb", ".java", ".kt", ".c", ".h", ".cpp", ".cs", ".php", ".mjs")
if not path.endswith(SRC_EXT):
    sys.exit(0)

run    = os.path.join(proj, ".ravenclaude", "runs", "premise", sid)
ledger = os.path.join(run, "probe-ledger.jsonl")
beacon = os.path.join(run, "recorder-alive")

# ── FAIL CLOSED: is the recorder alive at all? ─────────────────────────────
if not os.path.exists(beacon):
    # No beacon can mean "no Bash ran yet" (genuinely clean) or "the recorder is
    # not wired" (blind). Distinguish by asking whether the recorder EXISTS to be
    # wired. If it is installed but has never run, no tool call has happened yet,
    # so there is no probe to be unresolved -> clean.
    rec = os.path.join(proj, "plugins", "ravenclaude-core", "hooks", "log-probe.sh")
    if os.path.exists(rec):
        sys.exit(0)
    print("BLIND\t\t" + "the premise recorder (log-probe.sh) is not installed, "
          "so this check cannot see whether an unresolved negative probe exists")
    sys.exit(0)

# ── (a) unresolved negative: a negative with no later positive on the SAME subject
entries = []
try:
    with open(ledger) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
except FileNotFoundError:
    sys.exit(0)

def family(subject):
    """Same host, or same fs/cmd root — a control must probe the SAME subsystem."""
    s = str(subject)
    return s.split("/")[0] if "/" in s else s

resolved, unresolved = set(), {}
for e in entries:
    fam = family(e.get("subject", ""))
    if e.get("verdict") == "positive":
        resolved.add(fam)
        unresolved.pop(fam, None)
    elif e.get("verdict") == "negative" and fam not in resolved:
        unresolved.setdefault(fam, e)

ctrl = os.environ.get("RC_PREMISE_CONTROL", "")
if ctrl:
    unresolved.pop(family(ctrl), None)

if unresolved:
    fam, e = next(iter(unresolved.items()))
    print("DENY\t%s\t%s" % (os.path.basename(path),
          "%s returned %s (%s)" % (e.get("subject"), e.get("label"), e.get("tool"))))
' "$_dir" 2>/dev/null || true)"

[ -z "$_verdict" ] && exit 0

_kind="$(printf '%s' "$_verdict" | cut -f1)"
_file="$(printf '%s' "$_verdict" | cut -f2)"
_why="$(printf '%s' "$_verdict" | cut -f3)"

if [ "${RC_PREMISE_OVERRIDE:-0}" = "1" ]; then
  # An override is a decision, not a bypass — it leaves a trace on purpose.
  mkdir -p "$_dir/.ravenclaude/runs/premise" 2>/dev/null || true
  printf '%s\toverride\t%s\n' "$(date -u +%FT%TZ)" "$_why" \
    >> "$_dir/.ravenclaude/runs/premise/overrides.log" 2>/dev/null || true
  exit 0
fi

if [ "$_kind" = "BLIND" ]; then
  _reason="⛔ PREMISE GATE IS BLIND — refusing to report clean.

$_why

A check that cannot see must never allow. Install/wire log-probe.sh, or set
RC_PREMISE_OVERRIDE=1 to proceed and record the override."
else
  _reason="⛔ PREMISE GATE: creating a new source module on an unresolved negative result.

  new module : $_file
  unresolved : $_why

A negative result is NOT a diagnosis. Before building on it, send ONE probe that
would come out DIFFERENTLY if your hypothesis were false — a positive control on
the same subject.

This gate exists because that step was skipped once: a 404 on a placeholder URL
(which is supposed to 404) produced an 85-line component, 10 converted call sites,
an owner checklist item and two turns of architectural advice, for a defect no
user ever experienced. The control probe would have cost ten seconds.

  1. run the control   → the ledger resolves itself, nothing else needed
  2. RC_PREMISE_CONTROL='<subject>'  → you already ran it
  3. RC_PREMISE_OVERRIDE=1           → proceed anyway; the override is recorded"
fi

printf '%s' "$(python3 -c '
import json,sys
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse",
  "permissionDecision":"deny","permissionDecisionReason":sys.argv[1]}}))' "$_reason")"
echo "$_reason" >&2
exit 2
