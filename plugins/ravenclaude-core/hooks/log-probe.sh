#!/usr/bin/env bash
# log-probe.sh — PostToolUse(Bash|WebFetch). Records NEGATIVE-RESULT PROBES.
#
# ── WHY THIS EXISTS ─────────────────────────────────────────────────────────
# 2026-08-07/08, RavenPower-Website. A `curl` of a Cloudflare email-obfuscation
# href returned 404. From that single negative result an agent concluded "the
# decoder is broken, every visitor is affected", then built an 85-line component,
# converted 10 call sites, wrapped 15 addresses, added an owner go-live checklist
# item, and gave two turns of architectural advice.
#
# All of it was wrong. That URL is a PLACEHOLDER that nothing fetches — it is
# SUPPOSED to 404. One control probe (`/cdn-cgi/trace` → 200) would have killed
# the whole thing in ten seconds. Cost asymmetry: ~10s to disconfirm, hours to
# construct, 16 files changed, on a defect no user ever experienced.
#
# ⛔ THE POINT IS NOT THAT THE HYPOTHESIS WAS WRONG. Wrong hypotheses are cheap
# and normal. The damage came from the hypothesis being silently promoted to a
# premise by being written down, with nothing ever returning to test it.
#
# So: this hook records every negative result, and `guard-premise.sh` refuses to
# let a NEW SOURCE MODULE be created while one is still unresolved. A negative
# result is not a diagnosis until a positive control on the same subject shows
# the probe was capable of returning something else.
#
# ── WHY PostToolUse AND NOT THE TRANSCRIPT ──────────────────────────────────
# The transcript also carries tool results, and reading it needs no new matcher.
# It was rejected: code.claude.com/docs/en/hooks (2026-08-08) states the
# transcript "is written asynchronously and may lag the in-memory conversation."
# The probe→build sequence usually happens WITHIN one turn, so a lagging
# transcript would leave the guard reading a file that lacks the very evidence it
# needs — reporting "clean" because it could not see. That is indistinguishable
# from "clean because nothing was there", it fails OPEN, and its canary would
# still pass. Owner decision 2026-08-08: take the friction, never the silence.
#
# `tool_response` is written synchronously at tool completion, so there is no
# staleness window. VERIFIED BY MEASUREMENT, not by reading the docs — three doc
# fetches were inconclusive; a scratch project with a stdin-dumping hook driven by
# `claude -p` settled it (Claude Code 2.1.226, macOS):
#
#     tool_response = {stdout: "404", stderr: "", interrupted: false, ...}
#
# ── PRIVACY: DERIVED LABELS ONLY ────────────────────────────────────────────
# The ledger stores a SUBJECT (host/path or search term) and a VERDICT. It never
# stores the raw command or raw output — those carry tokens, keys and payloads.
#
# Fail-safe: always exits 0. A PostToolUse hook must never break the session; if
# this cannot record, `guard-premise.sh` detects the blindness and fails closed
# on its own side. That split is deliberate — the recorder degrades, the gate does not.

set -uo pipefail

_input="$(cat 2>/dev/null || true)"
[ -z "$_input" ] && exit 0

_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

# The JSON arrives on stdin, so the interpreter is fed with -c and the payload is
# piped in — a heredoc would occupy stdin and the script would read the SCRIPT as
# its input. (Caught by running it; the first draft here did exactly that.)
printf '%s' "$_input" | python3 -c '
import hashlib, json, os, re, sys, time

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

proj = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
tool = d.get("tool_name", "")
ti   = d.get("tool_input", {}) or {}
tr   = d.get("tool_response", {}) or {}
sid  = d.get("session_id", "nosession")

if not isinstance(tr, dict):
    tr = {"stdout": str(tr)}
out = (str(tr.get("stdout", "")) + "\n" + str(tr.get("stderr", "")))[:20000]

# ── SUBJECT: what was probed. Derived, never the raw command. ───────────────
cmd = str(ti.get("command", "") or ti.get("url", ""))
subject = None
m = re.search(r"https?://([^/\s\"\x27]+)(/[^\s\"\x27]*)?", cmd)
if m:
    path = (m.group(2) or "/").split("?")[0]
    subject = m.group(1) + path[:60]
else:
    m = re.search(r"\b(?:grep|rg|find|ls|cat|test -[ef])\b[^|;]*?([\w./*-]{3,60})\s*$", cmd)
    if m:
        subject = "fs:" + m.group(1)
if not subject:
    subject = "cmd:" + re.sub(r"\s+", " ", cmd.strip())[:40]

# ── WAS THIS EVEN AN HTTP PROBE? ────────────────────────────────────────────
# ⛔ MEASURED 2026-08-18 across every probe-ledger on disk (7 scopes, 3,070
# entries): of the 204 recorded NEGATIVES, 54 carried an `http-NNN` label, and
# 54 of those 54 came from a Bash command with NO network client anywhere in it.
#
#     wc -l schemas/design-schema.schema.json  ->  http-454   (a line count)
#     ls -la /Users/.../RavenClaude            ->  http-448   (a block count)
#     git diff origin/main --stat              ->  http-447   (an insertion count)
#     git show 5a985b95 --stat | head -60      ->  http-403   (a diffstat number)
#
# `http-447`, `http-448`, `http-454`, `http-459` and `http-482` are not status
# codes at all. The positive control on the same filter returned ZERO genuine
# ones, so the class was 100% noise — and it was not harmless noise: THREE of
# the seven real scopes on disk carried unresolved negative families made
# entirely of these, which is the gate refusing to let a new source module be
# created because `wc -l` printed 454. A guard that fires on `wc -l` is a guard
# that gets switched off.
#
# So: a BARE three-digit number is a status code only when the probe was an HTTP
# probe. Everything below is TEXTUAL (`command not found`, `No such file`) and
# stays ungated — those say what they mean in any context.
#
# ⛔ THE GATING IS SYMMETRIC ON PURPOSE. Gating only the negative half would
# leave a bare `200` in `wc -l` output still RESOLVING a family — trading a
# false deny for a false clear, which is the same defect pointed the other way.
# If you ever narrow one of these three lists, narrow all three.
_HTTP_CLIENT = re.compile(
    r"(?:^|[\s;|&(=])(?:curl|wget|httpie|xh|aria2c|lynx|w3m)(?:[\s;|&)]|$)"
    r"|\bgh\s+api\b"
    r"|\brequests\.(?:get|post|put|head|delete)\b"
    r"|\bhttpx\b|\burllib\b|\bfetch\(",
    re.I,
)
is_http = (
    tool == "WebFetch"
    or bool(re.search(r"https?://", cmd))
    or bool(_HTTP_CLIENT.search(cmd))
)

# ── VERDICT: negative | positive | indeterminate | neutral ──────────────────
# A NEGATIVE is a result that invites the inference "X is broken/absent".
_NEG_STATUS = [
    (r"(?:^|\s|\b)([45]\d\d)(?:\s|$)", "http-{0}"),
]
_NEG_TEXT = [
    (r"\bcommand not found\b", "command-not-found"),
    (r"\bNo such file or directory\b", "no-such-file"),
    (r"\bnot found\b", "not-found"),
    (r"\bdoes not exist\b", "does-not-exist"),
    (r"\bPermission denied\b", "permission-denied"),
    (r"\b(?:0 hits|no matches found|0 results)\b", "zero-match"),
]
NEG = (_NEG_STATUS + _NEG_TEXT) if is_http else _NEG_TEXT

# ── INDETERMINATE, CHECKED FIRST — a NON-result, not a negative result. ─────
# The probe never reached the question: rate-limited, the server errored, the
# connection failed, it timed out. Recording these as `negative` states the
# opposite of what happened — "X is absent" instead of "I could not ask" — and
# an absence-claim the probe never earned is exactly the false premise this
# whole mechanism exists to stop. It also cannot be cleared: re-running a
# rate-limited probe returns the same 429, so a permanent block is the one
# outcome guaranteed to train override-reflex, which costs more safety than it
# buys. 429 is carved OUT of the 4xx pattern for this reason.
#
# The bare-code halves are gated on `is_http` for the reason above — `wc -l`
# printing 503 is a line count, not a server error. The word forms are not.
_INDET_STATUS = [
    (r"(?:^|\s|\b)429(?:\s|$)", "rate-limited"),
    (r"(?:^|\s|\b)5\d\d(?:\s|$)", "server-error"),
]
_INDET_TEXT = [
    (r"\b(?:rate.?limit(?:ed|ing)?|too many requests)\b", "rate-limited"),
    (r"\b(?:timed out|timeout|Operation timed out)\b", "timeout"),
    (r"\b(?:Connection refused|Connection reset|Could not resolve host"
     r"|Temporary failure in name resolution|Network is unreachable)\b", "unreachable"),
]
INDET = (_INDET_STATUS + _INDET_TEXT) if is_http else _INDET_TEXT

verdict, label = "neutral", ""
for pat, lab in INDET:
    mm = re.search(pat, out, re.I | re.M)
    if mm:
        verdict, label = "indeterminate", lab
        break

# A POSITIVE-CAPABLE CONTROL: same subject family, demonstrably able to succeed.
# ⛔ Gated on `is_http` for the SAME reason the negative half is — see above.
# An ungated 2xx/3xx would let `wc -l` printing 200 silently RESOLVE a family
# nobody probed, which is the false-clear twin of the false-deny. A non-HTTP
# Bash call that produced output still records `positive/ok` through the
# fallback below, so nothing that used to clear stops clearing.
_pos = bool(is_http and re.search(r"(?:^|\s|\b)(2\d\d|3\d\d)(?:\s|$)", out, re.M))

if verdict == "neutral":
    _neg = None
    for pat, lab in NEG:
        mm = re.search(pat, out, re.I | re.M)
        if mm:
            _neg = lab.format(*mm.groups()) if "{0}" in lab else lab
            break

    # ⛔ BOTH present => this IS the control probe, and it is POSITIVE.
    # NOTE: no apostrophes in this block — the whole interpreter body is a
    # single-quoted shell string, so one would end it (use \x27 if ever needed).
    # In the words of the gate itself: "a negative result is not a diagnosis
    # until a positive control on the same subject shows the probe was CAPABLE
    # of returning something else." One command showing a 2xx AND a 4xx has
    # demonstrated exactly that capability — it is the disconfirming probe the
    # gate demands. Checking NEG first recorded it as `negative`, so running
    # the prescribed control ADDED an unresolved negative instead of clearing
    # one, and the more thorough the probe the more stuck the author became.
    # The remedy the gate prints was unreachable by following the gate.
    if _pos and _neg:
        verdict, label = "positive", "control-bidirectional"
    elif _neg:
        verdict, label = "negative", _neg
    elif _pos or (out.strip() and tool == "Bash"):
        verdict, label = "positive", "ok"

# A zero-match search with EMPTY output is still a negative result.
if verdict == "neutral" and not out.strip() and re.search(r"\b(grep|rg|find)\b", cmd):
    verdict, label = "negative", "empty-search"

# ── SCOPE: the git WORKTREE this probe belongs to ───────────────────────────
# ⛔ KEEP THIS BLOCK IN SYNC WITH ITS TWIN IN guard-premise.sh. The recorder and
# the gate must derive the SAME key, or the gate reads a ledger nobody writes and
# reports clean forever — the failure this whole mechanism exists to refuse.
#
# WHY (measured 2026-08-12, a real 6-agent parallel run in a consumer repo, NOT
# inferred): ONE session_id carried 14,322 transcript events spanning 49 distinct
# `cwd` values across 15+ git worktrees, and the resulting ledger held 2,825
# entries with 50 UNRESOLVED negative families. The ledger was keyed on
# (project, session_id) alone, and neither varies per agent — so every sibling
# agent appended to one file, and a negative recorded by the agent in worktree A
# denied an unrelated new module in worktree B. Three agents hit it; one routed
# around the hook entirely.
#
# `cwd` is the one payload field that DOES vary per agent (49 values in that one
# session), so the scope is the git worktree root containing it. A LINKED worktree
# carries its own `.git` FILE, so walking up from `cwd` stops at the worktree and
# not at the primary checkout — which is exactly the boundary being scoped.
#
# ⛔ This narrows WHO a negative blocks, never WHAT counts as a negative. A probe
# and the module built on it happen in the same working context, so the incident
# this gate was built from still trips it.
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

sess  = os.path.join(proj, ".ravenclaude", "runs", "premise", sid)
scope = rc_scope_key(str(d.get("cwd", "") or "") or proj, proj)
run   = os.path.join(sess, "scopes", scope)
try:
    os.makedirs(run, exist_ok=True)
    with open(os.path.join(run, "probe-ledger.jsonl"), "a") as f:
        f.write(json.dumps({
            "ts": int(time.time()),
            "tool": tool,
            "subject": subject,
            "verdict": verdict,
            "label": label,
            "scope": scope,
            "tool_use_id": d.get("tool_use_id", ""),
        }) + "\n")
    # Health beacon: proves the recorder RAN. Its absence is what lets
    # guard-premise.sh distinguish "no probes happened" from "I am blind".
    # ⛔ SESSION-level on purpose, NOT per-scope. Per-scope would make a
    # never-probed worktree indistinguishable from an unwired recorder, and the
    # gate fails CLOSED on that — so the first write in every fresh worktree would
    # be denied as blind. Blindness is a property of the recorder, not of a scope.
    open(os.path.join(sess, "recorder-alive"), "w").write(str(int(time.time())))
except Exception:
    pass
' "$_dir"

exit 0
