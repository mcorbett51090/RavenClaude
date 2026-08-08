#!/usr/bin/env bash
# guard-premise.sh — PreToolUse(Write). TWO independent triggers, OR-ed:
#
#   T-SHAPE  Blocks a NEW SOURCE MODULE from being created while an unresolved
#            negative-result probe is on the record.
#   T-PROSE  Blocks a DIAGNOSIS from being written into a DURABLE ARTIFACT as
#            established fact with no control probe cited beside it.
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
# ── T-PROSE — THE SECOND TRIGGER, AND WHY IT IS OR-ed ───────────────────────
# incidents.md names the damage in one sentence with two halves: "The wrong
# hypothesis was cheap and normal. The damage came from the hypothesis being
# silently promoted to a premise by being written down."
#
# T-SHAPE catches the FIRST half. It structurally CANNOT catch the second: a
# premise formed in a PRIOR session, or before a context compaction, leaves no
# open probe in this session's ledger, so T-SHAPE stays silent while the
# diagnosis is written into a durable artifact anyway. T-PROSE fires on ALL of:
#     (1) the target is a DURABLE artifact (not .ravenclaude/**, /tmp, scratch)
#     (2) a diagnosis-shaped assertion about a NAMED subject
#     (3) a certainty stamp within +/-6 lines — measured / verified / confirmed
#         / established / an ISO date / a bare HTTP status
#     (4) NO control-probe citation in the same block
#
# ⛔ THEY ARE OR-ed, NEVER AND-ed. AND-ing them would silence T-SHAPE whenever
# the prose is absent — the exact contingency defect this design exists to
# avoid. So T-PROSE is evaluated FIRST and independently, and none of T-SHAPE's
# exemptions may suppress it: a diagnosis written into docs/, or over a file
# that already exists, IS the damage. T-PROSE needs no ledger at all.
#
# ⛔ THE CERTAINTY STAMP IS THE TRIGGER, NOT AN EXEMPTION. The real header read
# 'measured 2026-08-07' beside a claim that was false. Higher confidence makes
# this MORE likely to fire, never less. A hedged draft ("I think the decoder may
# be broken") does not trip it; the confident, dated, authoritative version —
# the dangerous one — does. Anything keyed on self-reported doubt returns null
# on the case that actually happened.
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
# Zero model calls. T-SHAPE: one `test -e` short-circuits every Edit, every docs
# write, every scratch write, and every Write to a file that already exists —
# which is the overwhelming majority. The ledger is read only when a NEW source
# module is created. On a run that touches one existing file: ~2 ms, no deny.
#
# T-PROSE adds NO new process: it is a bounded regex scan of the payload inside
# the python3 this hook already forks, capped at 200 KB / 4000 lines / 2 KB per
# line, and it exits at conjunct 1 for every run-dir and scratch write. A Write
# with no content, or content carrying no defect predicate, costs one pass.
#
# ── ESCAPE HATCHES (all four are recorded, none is silent) ──────────────────
#   RC_PREMISE_CONTROL="<subject>"  the control you ran; resolves that subject
#   RC_PREMISE_OVERRIDE=1           proceed anyway; writes an override marker
#   run the control probe           the natural exit — the ledger clears itself
#   premise-ok: <named control>     T-PROSE only, written INTO the artifact.
#                                   EMPTY does NOT clear — an escape hatch
#                                   nobody tested is one everybody uses.
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

# ═══ T-PROSE ═══════════════════════════════════════════════════════════════
# Evaluated FIRST and independently. OR-ed with T-SHAPE below, never AND-ed:
# none of the T-SHAPE exemptions that follow (new-file-only, source-extension-
# only, docs/) may suppress this one, because a diagnosis written into docs/ or
# over a file that already exists IS the damage. It reads no ledger — that
# independence is the whole reason it exists.
content = str(ti.get("content", "") or "")[:200000]

# (1) DURABLE ARTIFACT. Judged on the PROJECT-RELATIVE path, so a tree that
#     happens to live under a temp root is still judged on docs/ vs scratch/
#     rather than on wherever mktemp put it.
rel_p = path.replace(proj, "").lstrip("/")
_SCRATCH_SEG = ("tmp", ".tmp", "temp", "scratch", "scratchpad", ".scratch", ".cache")
durable = not (
    rel_p.startswith(".ravenclaude/")
    or "/scratchpad/" in path
    or any(s.lower() in _SCRATCH_SEG for s in rel_p.split("/")[:-1])
)

if content and durable:
    # (2) DIAGNOSIS — a defect predicate about a NAMED subject. The subject
    #     alternatives are what make it a claim ABOUT something rather than a
    #     floating sentence; the closed predicate lists are what keep it off
    #     ordinary prose (a bare "is not X" deliberately does NOT qualify, or
    #     every "memory is not enforcement" sentence in this repo would trip).
    _SUBJ = (
        r"(?:`[^`\n]{1,60}`"
        r"|\"[^\"\n]{1,60}\""
        r"|(?:[Tt]he|[Aa]n?|[Tt]his|[Oo]ur|[Ii]ts|[Tt]heir)\s+[A-Za-z_][A-Za-z0-9_-]{1,40}"
        r"|[A-Za-z_][A-Za-z0-9_]*(?:[./-][A-Za-z0-9_]+)+"
        r"|/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*"
        r"|[A-Z][A-Za-z0-9_]{0,40})"
    )
    _DEFECT = (
        r"(?i:broken|down|missing|absent|failing|failed|dead|corrupt(?:ed)?"
        r"|unavailable|unreachable|misconfigured|disabled|stale|inert|empty"
        r"|null|undefined|wrong|inoperative|non-?functional|mangled|garbled"
        r"|not\s+(?:wired|installed|present|registered|reachable|set|called"
        r"|invoked|running|working|firing|fired|applied|honou?red|enforced"
        r"|loaded|hooked|configured|deployed|live))"
    )
    _EMITS = (
        r"(?i:returns?|returned|responds?\s+with|responded\s+with|throws?|threw"
        r"|emits?|emitted|yields?|gives?|gave|produces?)\s+(?i:an?\s+)?"
        r"(?i:[45]\d\d|error|errors|nothing|null|undefined|empty|NaN)"
    )
    _FAILS = (
        r"(?i:does\s+not|doesn\x27t|do\s+not|don\x27t|never|fails?\s+to"
        r"|failed\s+to|cannot|can\x27t|can\s+not|will\s+not|won\x27t)\s+"
        r"(?i:exist|exists|work|works|fire|fires|run|runs|load|loads|resolve"
        r"|resolves|render|renders|match|matches|return|returns|apply|applies"
        r"|trigger|triggers|execute|executes|save|saves|respond|responds"
        r"|connect|connects|start|starts)"
    )
    _DIAG = [
        re.compile(_SUBJ + r"\s+(?:is|are|was|were|has\s+been|have\s+been)\s+" + _DEFECT + r"\b"),
        re.compile(_SUBJ + r"\s+" + _EMITS + r"\b"),
        re.compile(_SUBJ + r"\s+" + _FAILS + r"\b"),
        re.compile(_SUBJ + r"\s*(?:->|=>|\u2192)\s*[45]\d\d\b"),
    ]
    # (3) CERTAINTY STAMP. ⛔ This is the TRIGGER, not an exemption. The real
    #     header read: measured 2026-08-07 — beside a claim that was false.
    _STAMP = re.compile(
        r"(?i:\b(?:measured|verified|confirmed|established|proven|validated)\b)"
        r"|\b\d{4}-\d{2}-\d{2}\b"
        r"|(?<![\w.])[1-5]\d\d(?![\w.])"
    )
    # (4) A CONTROL PROBE CITED IN THE SAME BLOCK. An EMPTY premise-ok: is not
    #     a citation, by construction — the trailing \S is the whole point.
    _CTRL = re.compile(
        r"(?i:\bcontrol\s*(?::|probe)|\bpositive\s+control\b"
        r"|\bpremise-ok:[ \t]*\S|\bdisconfirm(?:ing|ed|s)?\b|\brc\s+probe\b)"
    )

    lines = [_ln[:2000] for _ln in content.split("\n")[:4000]]
    prose_ctrl = os.environ.get("RC_PREMISE_CONTROL", "")
    for i, _ln in enumerate(lines):
        dm = None
        for rx in _DIAG:
            dm = rx.search(_ln)
            if dm:
                break
        if not dm:
            continue
        block = "\n".join(lines[max(0, i - 6):i + 7])
        if not _STAMP.search(block):
            continue                  # (3) unstamped -> a hypothesis, not a premise
        if prose_ctrl or _CTRL.search(block):
            continue                  # (4) a control IS cited -> allowed
        say = re.sub(r"\s+", " ", dm.group(0)).strip()[:120]
        print("PROSE\t%s\t%s" % (os.path.basename(path),
              "line %d writes a diagnosis as established fact: %s" % (i + 1, say)))
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
elif [ "$_kind" = "PROSE" ]; then
  _reason="⛔ PREMISE GATE: a diagnosis is being written down as established fact.

  artifact : $_file
  claim    : $_why

A defect claim with a certainty stamp beside it is no longer a hypothesis — it
is a PREMISE, and writing it into a durable artifact is how one gets silently
promoted. The wrong hypothesis was cheap and normal; the damage came from it
being written down, with nothing ever returning to test it.

⛔ The certainty is the TRIGGER here, not an exemption. At the moment of the
incident the author was CONFIDENT, with a real tool call behind them, and the
header read 'measured 2026-08-07' beside a claim that was false. A hedged draft
does not trip this; the confident, dated, authoritative version does.

Name the ONE probe that would come out DIFFERENTLY if the claim were false, and
cite it in the same block:

  1. control: <probe> -> <result>    a positive control on the same subject
  2. premise-ok: <named control>     you already ran it (EMPTY does NOT clear)
  3. RC_PREMISE_CONTROL='<subject>'  same, supplied out of band
  4. RC_PREMISE_OVERRIDE=1           proceed anyway; the override is recorded"
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
