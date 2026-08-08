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
import json, os, re, sys, time

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

# ── VERDICT: negative | positive | neutral ──────────────────────────────────
# A NEGATIVE is a result that invites the inference "X is broken/absent".
NEG = [
    (r"(?:^|\s|\b)([45]\d\d)(?:\s|$)", "http-{0}"),
    (r"\bcommand not found\b", "command-not-found"),
    (r"\bNo such file or directory\b", "no-such-file"),
    (r"\bnot found\b", "not-found"),
    (r"\bdoes not exist\b", "does-not-exist"),
    (r"\bPermission denied\b", "permission-denied"),
    (r"\b(?:0 hits|no matches found|0 results)\b", "zero-match"),
]
verdict, label = "neutral", ""
for pat, lab in NEG:
    mm = re.search(pat, out, re.I | re.M)
    if mm:
        verdict = "negative"
        label = lab.format(*mm.groups()) if "{0}" in lab else lab
        break

# A POSITIVE-CAPABLE CONTROL: same subject family, demonstrably able to succeed.
if verdict == "neutral":
    if re.search(r"(?:^|\s|\b)(2\d\d|3\d\d)(?:\s|$)", out, re.M) or (out.strip() and tool == "Bash"):
        verdict = "positive"
        label = "ok"

# A zero-match search with EMPTY output is still a negative result.
if verdict == "neutral" and not out.strip() and re.search(r"\b(grep|rg|find)\b", cmd):
    verdict, label = "negative", "empty-search"

run = os.path.join(proj, ".ravenclaude", "runs", "premise", sid)
try:
    os.makedirs(run, exist_ok=True)
    with open(os.path.join(run, "probe-ledger.jsonl"), "a") as f:
        f.write(json.dumps({
            "ts": int(time.time()),
            "tool": tool,
            "subject": subject,
            "verdict": verdict,
            "label": label,
            "tool_use_id": d.get("tool_use_id", ""),
        }) + "\n")
    # Health beacon: proves the recorder RAN. Its absence is what lets
    # guard-premise.sh distinguish "no probes happened" from "I am blind".
    open(os.path.join(run, "recorder-alive"), "w").write(str(int(time.time())))
except Exception:
    pass
' "$_dir"

exit 0
