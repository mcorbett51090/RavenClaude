#!/usr/bin/env bash
#
# triage-outcome.sh — PostToolUse(Bash). POST-FAILURE TRIAGE. Advisory only.
#
# rc-state-key: .ravenclaude/runs/cause-triage/<session>/scopes/<scope>/open.jsonl
# rc-state-scope: git worktree root containing the payload cwd (the log-probe.sh key)
# rc-state-rationale: a triage row is opened here and DISCRIMINATED later, possibly
#   by a different turn, so the row has to outlive the invocation that wrote it.
# rc-state-escape: comfort-posture — `cause_triage: off` silences it. An ABSENT
#   posture file is a no-op (opt-in, like the other advisory hooks).
#
# ─────────────────────────────────────────────────────────────────────────────
# WHAT IT DOES
# ─────────────────────────────────────────────────────────────────────────────
# A Bash command comes back angry or empty. This hook enumerates the CANDIDATE
# CAUSES from scripts/cause_taxonomy.py and emits, for each of the top three, the
# DISCRIMINATING PROBE — the cheapest command whose two outcomes split that cause
# from its siblings. It never states a cause. It states what would tell them apart.
#
# The failure it exists to interrupt is not "the hypothesis was wrong". Wrong
# hypotheses are cheap and normal. It is the hypothesis being promoted to a
# premise by being written down, with nothing ever returning to test it.
# control: log-probe.sh records the precedent — a placeholder URL that is
# SUPPOSED to 404 was read as a broken decoder, and one positive control on the
# same host would have disconfirmed the whole build in ten seconds.
#
# ─────────────────────────────────────────────────────────────────────────────
# ⛔ MEASURED CONSTRAINT 1 — THE PAYLOAD CARRIES NO EXIT STATUS
# ─────────────────────────────────────────────────────────────────────────────
# A failing Bash `tool_response` carries exactly:
#
#     {interrupted, isImage, noOutputExpected, stderr, stdout}
#
# and no exit-status field under any name. This was dumped from a real failing
# call, not read from docs.
# control: the same run carried a SessionStart sentinel that arrived and was
# reported back, so the dump is a fact about the payload and not about a blind
# harness. Recorded in docs/plans/2026-08-19-verify-before-assert/
# phase0-delivery-matrix.md, G0.4.
#
# CONSEQUENCE, stated here rather than papered over: every trigger arm degrades
# to a STDOUT/STDERR-LABEL arm. This hook passes `exit_code: null` to the
# taxonomy, which treats None as a first-class legal value. Any future edit that
# reintroduces an exit-status conjunct would be keying on a field the payload
# never carries, and would read as a permanent no-op.
#
# One further caveat, carried honestly: in that same dump the `ls` error text
# arrived in **stdout** with stderr empty. [unverified — one observation, and the
# command had `; echo` appended, so stream-merging is not established.] The label
# matcher therefore scans BOTH streams, while `stdout_empty` is computed from
# stdout alone.
#
# ─────────────────────────────────────────────────────────────────────────────
# ⛔ MEASURED CONSTRAINT 2 — STDERR AT EXIT 0 DOES NOT REACH THE MODEL
# ─────────────────────────────────────────────────────────────────────────────
# Matched trials on PostToolUse, PreToolUse and Stop all returned NOT-SEEN for
# stderr-at-exit-0, while `additionalContext` returned SEEN on the same runs.
# control: a SessionStart additionalContext sentinel arrived in every trial, so
# each negative measures the channel rather than a deaf harness.
#
# So delivery goes through `_advise.sh`, which is already on main and already
# does this correctly: it buffers fd2 and, at exit, emits the buffer BOTH to the
# real stderr (the terminal notice is unchanged) AND as `additionalContext`. Two
# emitters on one event are CONCATENATED, not last-writer-wins, so this hook
# needs no spool and no disjoint matcher against sanitize-webfetch-output.
#
# The self-identifying banner `_advise.sh` prepends is NOT decoration and must
# not be stripped: in the same bake-off an unlabelled advisory was described by
# the model as "something wrapping or post-processing bash output" and discounted.
# An advisory that cannot be told from an attack buys nothing.
#
# ⛔ EXIT POSTURE. Exit 0, always. That is an OUTPUT of the measurement above and
# not a generalisation from PreToolUse: at PostToolUse there is nothing left to
# block, delivery no longer depends on the exit code, and a non-zero exit here
# can only break a session. Every internal error path fails OPEN.
#
# ─────────────────────────────────────────────────────────────────────────────
# ⛔ WHAT THE ADVISORY MAY CONTAIN — AND WHAT IT MAY NOT
# ─────────────────────────────────────────────────────────────────────────────
# ZERO BYTES of the command output are ever echoed. stdout and stderr are reduced
# to DERIVED LABEL CODES from a closed vocabulary before they cross into the
# taxonomy, and the taxonomy is typed to accept nothing else. Probe placeholders
# are filled from `tool_input` only — text the model authored and already holds —
# and only through a restrictive whitelist charset with a length bound.
#
# The ledger likewise stores a derived `subject` label and never the raw command.
# ⛔ `subject`, not a digest: Phases 5/6 have to JOIN this row against a subject
# named in prose, and a one-way digest cannot support that join, which would
# leave those gates inert while still looking wired.
#
# ─────────────────────────────────────────────────────────────────────────────
# ⛔ FALSE POSITIVES — the argument, not a hand-wave
# ─────────────────────────────────────────────────────────────────────────────
# The risk here is VOLUME, not correctness. An advisory on every search that
# legitimately matched nothing is how a channel gets tuned out.
# control: this repo already rejected a candidate rule measured at an 85%
# false-positive rate over 17,410 real commands, on exactly that reasoning — a
# channel that is wrong most of the time teaches an agent to stop reading it.
#
# Three brakes, all live in this file:
#   1. the empty-output arm fires only on an EVIDENCE-BEARING command, so mkdir,
#      cd, touch, export, package installs and writes never trigger it;
#   2. a clean, non-empty, unangry result produces NO advisory and NO ledger row
#      (the negative control — a nudge on every green command trains the ignore
#      reflex a cry-wolf gate always trains);
#   3. repeat suppression: the same (subject, candidate ids) in one session emits
#      the full advisory ONCE, then a one-line pointer. Suppression lives in the
#      DISPLAY, never in the ledger.
#
# ⛔ WIRED 2026-08-19, ON A MEASUREMENT — not on a decision to stop waiting.
# This hook shipped UNWIRED first, because the plan gates wiring on a measured fire
# rate of 3% or less over a replay corpus, and no corpus existed. The corpus was
# then built: 46,557 real Bash envelopes paired from 1,107 local transcripts.
#
#   first measurement   3.740%   OVER the gate -> NOT wired
#   after two fixes     2.588%   under the gate -> wired
#
# ⛔ THE GATE WAS NEVER MOVED. The trigger got more specific; 3% stayed 3%. The two
# fixes were the anticipated-failure brake (see the TRIGGER block) and gating the
# URL subject on the http family (see the SUBJECT block). Both are objective
# command shape. Same corpus, same sample seed, so the two numbers compare directly.
#
# Controls, run before believing either number, because a 0% rate and an inert hook
# are indistinguishable: an unhandled failing command FIRES; `mkdir -p` is SILENT;
# and — the pair that shows the brake removes noise and not signal — the SAME
# failure is silent when the author wrote a `||` fallback and still fires without one.
#
# ⛔ HONEST LIMIT ON THAT NUMBER. Transcripts store a RENDERED result string, so the
# corpus envelopes were reconstructed with everything in stdout and stderr always
# empty. That is not byte-identical to a live payload and could bias the rate in
# either direction. Re-measure against live payloads once the Phase 1 harness can
# capture them; 2.588% is the best available figure, not a perfect one.
#
# Portability: bash 3.2 / BSD-safe. No declare -A, no mapfile, no GNU timeout.
# ⛔ NO APOSTROPHES inside the embedded python: it sits in a single-quoted bash
# block, and one apostrophe in even a comment closes the string and the hook dies.
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# ⛔ ARM THE FAIL-SAFE FIRST, before any line that could abort. Flagged by
# check-verdict-default-nonpermissive.py on this file first run: the trap sat
# below the directory-resolution line, so an abort in between would exit
# non-zero with no trap, and the harness reads a non-zero PostToolUse exit as an
# error rather than as this hook contract.
# control: with the trap moved above, the same checker returns clean, and it was
# returning a finding on this exact file before the move — so the pass measures
# the fix and not a checker that stopped looking.
trap 'exit 0' EXIT

# ── ADVISORY DELIVERY. rc_advise_init installs its OWN EXIT trap, REPLACING the
# one armed above; the forced 0 reproduces this hook always-exit-0 fail-safe
# contract exactly, and the trap above keeps that contract if the helper is absent.
_rc_hd="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || printf '.')"
if [ -f "$_rc_hd/_advise.sh" ]; then
  . "$_rc_hd/_advise.sh"
  rc_advise_init PostToolUse 0
fi

# ── hook-event substrate (fail-safe: stub if absent) ────────────────────────
# ⛔ Wired BEFORE ship, not after. guard-premise.sh shipped with 463 events from
# six hooks and zero from itself, and "I have no events" was indistinguishable
# from "I never fire" until somebody went looking.
# control: the same log carried rows from six SIBLING hooks on the same run, so
# the empty slice was a fact about that one hook rather than about a dead log.
# shellcheck source=/dev/null
[ -f "$_rc_hd/_emit-event.sh" ] && . "$_rc_hd/_emit-event.sh" 2>/dev/null || true
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

_input=""
[ ! -t 0 ] && _input="$(cat 2>/dev/null || printf '')"
[ -n "$_input" ] || exit 0

command -v python3 >/dev/null 2>&1 || exit 0 # no interpreter on this host -> fail open

_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
_taxonomy="$(cd "$_rc_hd/../scripts" 2>/dev/null && pwd || printf '.')"

# The JSON arrives on stdin, so the interpreter is fed with -c and the payload is
# piped in. A heredoc would occupy stdin and the script would read ITSELF.
_advisory="$(printf '%s' "$_input" | python3 -c '
import hashlib, json, os, re, sys, time

sys.path.insert(0, sys.argv[2])
try:
    from cause_taxonomy import CmdShape, enumerate_causes
except Exception:
    # FAIL OPEN. A taxonomy that fails to import must not break a Bash call.
    sys.exit(0)

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(d, dict):
    sys.exit(0)

proj = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
if d.get("tool_name") != "Bash":
    sys.exit(0)

ti = d.get("tool_input") or {}
tr = d.get("tool_response") or {}
if not isinstance(ti, dict):
    ti = {}
if not isinstance(tr, dict):
    tr = {"stdout": str(tr)}

cmd = str(ti.get("command", "") or "")
if not cmd.strip():
    sys.exit(0)
out = str(tr.get("stdout", "") or "")
err = str(tr.get("stderr", "") or "")
both = (err + "\n" + out)[:20000]
stdout_empty = not out.strip()
stderr_nonempty = bool(err.strip())

# ── POSTURE KNOB: off | warn. An ABSENT posture file means no opinion. ──────
cwd = str(d.get("cwd", "") or "") or proj
mode = "warn"
try:
    ppath = os.path.join(cwd, ".ravenclaude", "comfort-posture.yaml")
    if not os.path.isfile(ppath):
        sys.exit(0)
    with open(ppath, "r", errors="replace") as fh:
        m = re.search(r"^[ \t]*cause_triage:[ \t]*([A-Za-z]+)", fh.read(), re.M)
    if m:
        mode = m.group(1).lower()
except Exception:
    sys.exit(0)
if mode not in ("off", "warn"):
    mode = "warn"
if mode == "off":
    sys.exit(0)

# ── DERIVED STDERR LABELS. A closed vocabulary, matched by fixed patterns.
# This is the injection boundary. Nothing past this block sees the raw text
# again; the taxonomy is TYPED to refuse anything but these codes.
_LABEL_PATTERNS = (
    ("command-not-found", r"command not found|not found: "),
    ("permission-denied", r"[Pp]ermission denied|EACCES"),
    ("no-such-file", r"No such file or directory|ENOENT"),
    ("is-a-directory", r"[Ii]s a directory|EISDIR"),
    ("ambiguous-argument", r"ambiguous argument|unknown revision or path"),
    ("broken-pipe", r"[Bb]roken pipe|EPIPE"),
    ("timeout", r"[Tt]imed out|ETIMEDOUT"),
    ("rate-limited", r"rate limit|429 |[Tt]oo [Mm]any [Rr]equests"),
    ("server-error", r"Internal Server Error|Bad Gateway|Service Unavailable"),
    ("dns-failure", r"Could not resolve host|Name or service not known|NXDOMAIN"),
    ("conn-refused", r"[Cc]onnection refused|[Cc]onnection reset|ECONNREFUSED"),
    ("auth-denied", r"[Uu]nauthorized|[Bb]ad credentials|[Aa]uthentication failed"),
    ("in-progress", r"in progress|still running|queued"),
    ("not-a-git-repo", r"not a git repository"),
    ("json-parse-error", r"parse error|Invalid JSON|JSONDecodeError|Unexpected token"),
)
labels = set()
for code, pattern in _LABEL_PATTERNS:
    try:
        if re.search(pattern, both):
            labels.add(code)
    except Exception:
        pass
if stderr_nonempty:
    labels.add("stderr-nonempty")

# ── DERIVED COMMAND SHAPE. Booleans only. The raw command never travels. ────
def has(pattern):
    try:
        return bool(re.search(pattern, cmd))
    except Exception:
        return False

_OUTPUT_LIMIT = (
    r"\|\s*(head|tail)\b"
    r"|(^|\s)(head|tail)\s+-"
    r"|(^|\s)--max-count\b"
    r"|(^|\s)-m\s+[0-9]"
    r"|(^|\s)-n\s+[0-9]"
    r"|(^|\s)--limit\b"
    r"|(^|\s)-maxdepth\b"
)
_FAMILY = (
    ("grep", r"(^|[\s/|])(u|e|f|z)?grep\b|(^|[\s/|])rg\b|(^|[\s/|])ag\b"),
    ("find", r"(^|[\s/|])find\b|(^|[\s/|])fd\b"),
    ("git", r"(^|[\s/|])git\b"),
    ("http", r"(^|[\s/|])(curl|wget|http|gh)\b"),
    ("jq", r"(^|[\s/|])jq\b"),
    ("build", r"(^|[\s/|])(make|npm|pnpm|yarn|cargo|go|astro|vite|tsc)\b"),
    ("pkg", r"(^|[\s/|])(brew|pip3?|apt|apk)\b"),
    ("fs", r"(^|[\s/|])(ls|cat|head|tail|stat|wc|file|readlink|realpath)\b"),
)
family = "other"
for name, pattern in _FAMILY:
    if has(pattern):
        family = name
        break

# EVIDENCE-BEARING is the volume brake on the empty-output arm. A command whose
# job is to CHANGE something answers no question, so its silence carries nothing.
_SIDE_EFFECT_ONLY = (
    r"^\s*(mkdir|cd|touch|export|set|unset|rm|cp|mv|ln|chmod|chown|kill|sleep|true|:)\b"
    r"|(^|[\s;&|])git\s+(add|commit|push|checkout|switch|restore|stash|tag)\b"
    r"|(^|[\s;&|])(npm|pnpm|yarn)\s+(install|i|ci|add)\b"
    r"|(^|[\s;&|])printf\b|(^|[\s;&|])echo\b"
)
evidence_bearing = not has(_SIDE_EFFECT_ONLY)

shape = CmdShape(
    has_devnull_stdout=has(r"(^|[^0-9])>>?\s*/dev/null|(^|\s)1>>?\s*/dev/null"),
    has_2devnull=has(r"2>>?\s*/dev/null|&>\s*/dev/null"),
    has_output_limit=has(_OUTPUT_LIMIT),
    is_pipeline="|" in cmd,
    has_stderr_merge=has(r"2>&1"),
    has_glob=has(r"[*?\[]"),
    has_relative_path=has(r"(^|\s)\.{1,2}/"),
    has_paginated_client=has(r"per_page|--paginate|page=|\?page"),
    is_evidence_bearing=evidence_bearing,
    tool_family=family,
)

# ── TRIGGER. Objective shape only. There is no confidence input here and no
# parameter through which one could be added later.
_INDETERMINATE = ("timeout", "rate-limited", "server-error", "dns-failure",
                  "conn-refused", "auth-denied", "in-progress")
indeterminate = any(x in labels for x in _INDETERMINATE)

# ── ANTICIPATED-FAILURE BRAKE (added after a corpus measurement) ────────────
# ⛔ MEASURED over 46,557 real Bash envelopes from 1,107 local transcripts: the
# unbraked trigger fired at 3.740%, over the 3% wiring gate set by the plan. The dominant
# contributor was NOT failed commands — it was SUCCESSFUL COMPOUND commands
# (`a; b; c`, `a && b`) where ONE sub-command emitted error-shaped text into the
# merged output, e.g. `tail -20 /tmp/x.log || echo "(no log)"`.
#
# An error the author ALREADY HANDLED is not an unexplained outcome. A `||`
# fallback or a `2>/dev/null` on the failing part is the author stating in the
# command itself that this failure is expected and covered. Advising on it is the
# 85%-false-positive shape this repo has already rejected once.
#
# ⛔ This is OBJECTIVE COMMAND SHAPE, not a confidence input and not a loosened
# threshold. There is still no parameter here through which self-reported doubt
# could be introduced. The gate stayed at 3%; the trigger got more specific.
#
# ⛔ SCOPED TO THE `angry` (label) ARM ONLY. `indeterminate` — timeout, rate
# limit, auth, DNS, connection-refused — is NOT braked: those are the rare,
# high-value shapes where a fallback hides a real infrastructure problem, and a
# handled rate-limit is still a rate-limit worth naming.
anticipated_failure = has(r"\|\|") or has(r"2>>?\s*/dev/null|&>\s*/dev/null")

angry = bool(labels - set(["stderr-nonempty"])) or stderr_nonempty
if anticipated_failure:
    angry = False
empty_null = stdout_empty and not stderr_nonempty and evidence_bearing

if indeterminate:
    verdict = "indeterminate"
elif angry:
    verdict = "negative"
elif empty_null:
    verdict = "empty-null"
else:
    verdict = "clean"

if verdict == "clean":
    # THE NEGATIVE CONTROL. A clean, non-empty result yields no advisory and no
    # ledger row. This branch is asserted by the gate test and must stay.
    sys.exit(0)

candidates = enumerate_causes(
    shape,
    None,                      # the payload carries no exit status
    stdout_empty,
    frozenset(labels),
    positive_control=False,    # a control is never assumed; H1 stays gated
    limit=3,
)
if not candidates:
    sys.exit(0)

# ── SUBJECT: a derived label. Never the raw command. ────────────────────────
# ⛔ Redirect OPERANDS are stripped first. Caught by running the hook, not by
# reading it: `grep -rn needle src/ 2>/dev/null` derived the subject `fs:/dev/null`
# and then filled the probe template with it, producing the advice
# `command -v /dev/null`. The redirect target is the last path-shaped token on the
# line and it is never what was being asked about.
# control: with the strip in place the same command yields `fs:src/`, and the
# no-redirect variant of the same command yields `fs:src/` too — the two agree,
# which is what shows the strip removed noise rather than signal.
subj_src = re.sub(r"[0-9]?>>?\s*[^\s;|&]+", " ", cmd)
subj_src = re.sub(r"[0-9]?>&[0-9-]", " ", subj_src)
subject = None
# ⛔ The URL subject is gated on the command actually being an HTTP command.
# MEASURED in the corpus run: an export of a PATH plus a quoted user-agent string
# that embedded https://github.com/owner/repo produced the subject
# github.com/owner/repo — a URL lifted out of a
# QUOTED LITERAL that was data, not a target, in a command that fetches nothing.
# Same family as the redirect-operand defect above: a path-shaped token in the
# command text is not automatically the thing being asked about.
# control: with the gate, that export yields a `cmd:` subject; a real
# `curl https://host/path` still yields `host/path` — so the gate removed noise
# without removing signal.
# ⛔ NO literal apostrophe anywhere in this python program — INCLUDING IN PROSE
# COMMENTS. The whole program is one single-quoted bash string, so one apostrophe
# ends it and the hook stops parsing. Cost me two rounds: the giveaway was four
# different control inputs all returning an IDENTICAL 591 bytes, which is never a
# real result, only a shared error.
m = re.search(r"https?://([^/\s\"]+)(/[^\s\"]*)?", subj_src) if family == "http" else None
if m:
    subject = m.group(1) + (m.group(2) or "/").split("?")[0][:60]
else:
    m = re.search(r"\b(?:grep|rg|find|ls|cat|test|jq|wc)\b[^|;]*?([\w./*-]{3,60})\s*$",
                  subj_src.strip())
    if m:
        subject = "fs:" + m.group(1)
if not subject:
    subject = "cmd:" + re.sub(r"\s+", " ", subj_src.strip())[:40]

# ── TARGET for the probe templates. Whitelist charset, bounded length, drawn
# ONLY from tool_input — text the model authored and already holds.
target = "<target>"
for tok in reversed(re.findall(r"[A-Za-z0-9_./*-]{2,60}", subj_src)):
    if not tok.startswith("-"):
        target = tok
        break

# ── SCOPE: the git WORKTREE this triage belongs to. ─────────────────────────
# ⛔ KEEP THIS BLOCK IN SYNC WITH ITS TWIN IN log-probe.sh AND guard-premise.sh.
# A recorder and a gate deriving DIFFERENT keys give a gate that reads a ledger
# nobody writes and reports clean forever.
# control: log-probe.sh header records the measurement that forced this key — one
# session carried 49 distinct cwd values across 15+ worktrees, and a flat key let
# a negative recorded in worktree A deny an unrelated module in worktree B.
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

sid = str(d.get("session_id", "nosession") or "nosession")
sess = os.path.join(proj, ".ravenclaude", "runs", "cause-triage", sid)
scope = rc_scope_key(cwd, proj)
run = os.path.join(sess, "scopes", scope)
ids = [c.id for c in candidates]

# SECRET SCRUB BEFORE THE DURABLE WRITE.
# The fs: and URL arms are derived, but the cmd: fallback is the raw command
# truncated to 40 chars, so a credential typed on a failing command line was
# written verbatim into open.jsonl and read back by two downstream gates.
# _emit-event.sh scrubs its own rule and path fields for exactly this reason and
# says so; this writer never did.
# control: a failing command carrying a ghp_-shaped token produced the row
# subject cmd:ghp_BBBB...; with this scrub the same input yields [REDACTED].
# Mirrors the high-confidence shapes in hooks/_scrub.sh. Deliberately a SUBSET:
# these are the prefix-anchored shapes that cannot false-positive on ordinary
# command text.
_SECRET_SHAPES = (
    r"AKIA[0-9A-Z]{12,}",
    r"sk-(?:ant-)?[A-Za-z0-9-]{20,}",
    r"(?:sk|rk)_live_[A-Za-z0-9]{24,}",
    r"ghp_[A-Za-z0-9]{30,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"glpat-[A-Za-z0-9_-]{15,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"AIza[0-9A-Za-z_-]{30,}",
    r"npm_[A-Za-z0-9]{30,}",
    r"hf_[A-Za-z0-9]{30,}",
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}",
)
for _pat in _SECRET_SHAPES:
    subject = re.sub(_pat, "[REDACTED]", subject)

suppressed = False
try:
    os.makedirs(run, exist_ok=True)
    with open(os.path.join(run, "open.jsonl"), "a") as fh:
        fh.write(json.dumps({
            "ts": int(time.time()),
            "subject": subject,
            "verdict": verdict,
            "candidate_ids": ids,
            "discriminated": None,
            "tool_use_id": d.get("tool_use_id", ""),
            "scope": scope,
        }) + "\n")
    # Health beacon at SESSION level, not per scope. Per-scope would make a
    # never-triaged worktree read the same as an unwired recorder.
    with open(os.path.join(sess, "triage-alive"), "w") as fh:
        fh.write(str(int(time.time())))
    # Repeat suppression lives HERE, in the display path, and never in the ledger.
    key = hashlib.sha1(("|".join([subject] + ids)).encode("utf-8", "replace")).hexdigest()[:16]
    seen = os.path.join(sess, "seen-" + key)
    suppressed = os.path.exists(seen)
    if not suppressed:
        with open(seen, "w") as fh:
            fh.write("1")
except Exception:
    pass

if suppressed:
    print("[cause-triage] %s (%s) — same candidates as earlier this session: %s. "
          "The full advisory and its probes were emitted on the first occurrence."
          % (subject, verdict, ", ".join(ids)))
    sys.exit(0)

lines = []
lines.append("[cause-triage] a Bash result came back %s. Before naming a cause, run "
             "the probe that would tell the candidates apart." % verdict)
lines.append("  subject:  %s" % subject)
lines.append("  observed: stdout %s | stderr %s | labels: %s"
             % ("empty" if stdout_empty else "non-empty",
                "non-empty" if stderr_nonempty else "empty",
                ", ".join(sorted(labels)) or "none matched"))
lines.append("  no exit status is available in the payload, so this triage is derived "
             "from stream shape and derived labels only.")
lines.append("")
lines.append("  CANDIDATE CAUSES, ranked by observed shape (never by confidence):")
for i, c in enumerate(candidates, 1):
    lines.append("   %d. %s — %s" % (i, c.id, c.cause))
    lines.append("      probe: %s" % c.probe.replace("{target}", target))
lines.append("")
if verdict == "indeterminate":
    lines.append("  An indeterminate result is evidence about REACHABILITY only, never "
                 "about the subject. It cannot close this row.")
lines.append("  Absence (H1) is unavailable as a conclusion until a POSITIVE CONTROL on "
             "the same subsystem shows this probe can return something else.")
lines.append("  Advisory only — this hook never blocks. Silence it with "
             "`cause_triage: off` in .ravenclaude/comfort-posture.yaml.")
print("\n".join(lines))
' "$_dir" "$_taxonomy" 2>/dev/null || printf '')"

if [ -n "$_advisory" ]; then
  printf '%s\n' "$_advisory" >&2
  _emit_hook_event "triage-outcome.sh" "warn" "Bash" "" "ct.post-failure-triage" "0" 2>/dev/null || true
else
  _emit_hook_event "triage-outcome.sh" "allow" "Bash" "" "ct.no-trigger" "0" 2>/dev/null || true
fi

exit 0
