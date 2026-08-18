#!/usr/bin/env bash
#
# rc-state-key: cwd-anchored ledger dir + a scope digest derived from the path's
#               .ravenclaude/ segment (see rc_rel) — varies per worktree
# rc-state-scope: worktree
# rc-state-rationale: the decision is about SOURCE FILES IN ONE WORKING TREE. Keyed
#   on (project, session_id) it was measurably wrong: one session_id carried 14,322
#   events across 49 cwd values and 15+ worktrees into a single 2,825-entry ledger,
#   so a negative recorded in worktree A denied an unrelated new module in B.
# rc-state-escape: a premise control.md file under the run dir — file-based on
#   purpose, because RC_PREMISE_CONTROL as an env var never reached this process
#   from a dispatched subagent's Bash call, and an unreachable exit gets tunnelled.
#
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
# ── ESCAPE HATCHES (all five are recorded, none is silent) ──────────────────
#   run the control probe           the natural exit — the ledger clears itself
#   premise-ok: <named control>     T-PROSE only, written INTO the artifact.
#                                   EMPTY does NOT clear — an escape hatch
#                                   nobody tested is one everybody uses.
#   RC_PREMISE_CONTROL="<subject>"  the control you ran; resolves that subject
#   RC_PREMISE_OVERRIDE=1           proceed anyway; writes an override marker
#   .../scopes/<scope>/control.md   the FILE-BASED control — the only one of
#                                   these a dispatched SUBAGENT can reach, since
#                                   a variable exported inside a Bash call never
#                                   reaches this hook process. Requires
#                                   premise-control: / who: / subject: / control:
#                                   and appends to overrides.log on every use.
#
# Deny mechanism matches enforce-layout.sh: hookSpecificOutput JSON on stdout
# (Claude Code issue #40580) AND exit 2 for older clients.

set -uo pipefail

_input="$(cat 2>/dev/null || true)"
[ -z "$_input" ] && exit 0

_dir="${CLAUDE_PROJECT_DIR:-$PWD}"

_verdict="$(printf '%s' "$_input" | python3 -c '
import hashlib, json, os, re, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)                      # malformed input -> allow (never break a session)

# Screened tools. Write was the only one until 2026-08-13, which meant an Edit or
# MultiEdit carrying the identical diagnosis prose evaded the screen entirely —
# both a false-negative and the exact surface a session tunnels through when the
# guard denies a Write. The correct response to a false positive is the sanctioned
# escape below (an in-block `premise-ok:` / `control:` marker, RC_PREMISE_CONTROL,
# or the durable control.md), never a tool switch.
_TOOL = d.get("tool_name")
if _TOOL not in ("Write", "Edit", "MultiEdit"):
    sys.exit(0)

proj = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
ti   = d.get("tool_input", {}) or {}
path = str(ti.get("file_path", ""))
sid  = d.get("session_id", "nosession")

if not path:
    sys.exit(0)


def rc_rel(p, root):
    """Project-relative path, correct when `root` is not a literal prefix of `p`.

    The old idiom was `p.replace(root, "").lstrip("/")`. That is a SUBSTRING
    operation, not a path operation, so it silently produced the full absolute
    path whenever the two disagreed textually — a nested worktree, a symlinked
    root (macOS /tmp vs /private/tmp), a trailing slash. An absolute string never
    startswith(".ravenclaude/"), so the exemptions keyed on it evaporated and the
    guard denied legitimate run-artifact writes. Both call sites below use this.
    """
    # A run artifact is a run artifact wherever it lives. In a NESTED worktree the
    # tree sits at <proj>/.claude/worktrees/<wt>/, so even a correct relpath yields
    # `.claude/worktrees/<wt>/.ravenclaude/runs/...` — which does not startswith
    # ".ravenclaude/" either. Anchoring on the LAST `.ravenclaude/` segment is what
    # makes the exemption hold in a worktree, which is where the parallel agents
    # that hit this actually run.
    marker = os.sep + ".ravenclaude" + os.sep
    if marker in p:
        return ".ravenclaude/" + p.rsplit(marker, 1)[1]
    try:
        rp, rr = os.path.realpath(p), os.path.realpath(root)
        rel = os.path.relpath(rp, rr)
        if not rel.startswith(".." + os.sep) and rel != "..":
            return rel
    except Exception:
        pass
    return p.replace(root, "").lstrip("/")

# ═══ SCOPE — WHOSE LEDGER IS THIS? ═════════════════════════════════════════
# ⛔ KEEP THIS BLOCK IN SYNC WITH ITS TWIN IN log-probe.sh. The recorder and the
# gate must derive the SAME key, or the gate reads a ledger nobody writes and
# reports clean forever.
#
# The ledger used to be keyed on (project, session_id). MEASURED 2026-08-12 on a
# real 6-agent parallel run: ONE session_id carried 14,322 transcript events
# spanning 49 distinct `cwd` values across 15+ git worktrees, and its single
# ledger held 2,825 entries with 50 UNRESOLVED negative families. Neither key
# component varies per agent, so every sibling agent shared one ledger and a
# negative recorded in worktree A denied an unrelated new module in worktree B.
#
# `cwd` is the one payload field that DOES vary per agent, so the scope is the git
# worktree root containing it (a LINKED worktree carries its own `.git` FILE, so
# the walk stops at the worktree, not the primary checkout). When the payload
# carries no `cwd`, the WRITE TARGET stands in — it is the other thing that is
# always present and always agent-specific.
#
# ⛔ This narrows WHO a negative blocks. It does not narrow WHAT counts as one:
# a probe and the module built on it share a working context, so the incident
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

sess_dir  = os.path.join(proj, ".ravenclaude", "runs", "premise", sid)
scope     = rc_scope_key(str(d.get("cwd", "") or "") or path, proj)
run       = os.path.join(sess_dir, "scopes", scope)
ctrl_path = os.path.join(run, "control.md")

# ═══ THE FILE-BASED CONTROL — the escape a SUBAGENT can actually reach ═════
# ⛔ RC_PREMISE_CONTROL and RC_PREMISE_OVERRIDE are ENVIRONMENT VARIABLES, and a
# variable exported inside a Bash tool call does not reach this hook process. So
# a dispatched subagent that has genuinely run the control work had NO sanctioned
# way to say so. Measured consequence (2026-08-12): one agent lost a finished
# harness rather than tunnel, and one agent routed around the hook by writing via
# Bash heredocs instead of the Write tool. A guardrail whose only exit is
# unreachable does not get respected — it gets tunnelled.
#
# The file is reachable with the Write tool (it lives under `.ravenclaude/`, which
# both triggers already exempt), it is scoped to ONE session and ONE worktree so
# it cannot clear anybody else, and it is INERT unless it names who ran the
# control, what subject it covers, and what the control was.
#
# ⛔ An escape hatch nobody tested is one everybody uses: a file missing any of
# who: / subject: / control: (or with an EMPTY value after the colon) clears
# NOTHING, and the deny says so by name rather than failing silently.
_CTRL_CACHE = {}

def rc_load_control():
    if _CTRL_CACHE:
        return _CTRL_CACHE
    fc = {"exists": False, "valid": False, "subjects": [],
          "who": "", "subject": "", "control": "", "sig": ""}
    try:
        with open(ctrl_path) as fh:
            txt = fh.read(65536)
        fc["exists"] = True
    except Exception:
        txt = ""
    if txt:
        def kv(key):
            m = re.search(r"(?im)^[ \t>*-]*" + key + r"[ \t]*:[ \t]*(\S.*)$", txt)
            return m.group(1).strip() if m else ""
        fc["who"] = kv("who")
        fc["subject"] = kv("subject")
        fc["control"] = kv("control")
        fc["subjects"] = [s.strip() for s in re.findall(
            r"(?im)^[ \t>*-]*premise-control[ \t]*:[ \t]*(\S.*)$", txt) if s.strip()]
        fc["sig"] = hashlib.sha1(txt.encode("utf-8", "replace")).hexdigest()[:16]
        fc["valid"] = bool(fc["who"] and fc["subject"] and fc["control"] and fc["subjects"])
    _CTRL_CACHE.update(fc)
    return _CTRL_CACHE

def rc_control_blanket(fc):
    return "*" in [s.strip() for s in fc.get("subjects", [])]

def rc_control_covers(fc, target):
    if rc_control_blanket(fc):
        return True
    t = str(target).lower()
    for want in fc.get("subjects", []):
        w = str(want).strip().lower()
        if w and (w in t or t in w):
            return True
    return False

def rc_record_control(fc, cleared):
    """Durable, deduped audit line. Recording is the price of the escape."""
    applied = os.path.join(run, "control.applied")
    try:
        prev = open(applied).read().strip()
    except Exception:
        prev = ""
    if prev == fc.get("sig", ""):
        return
    line = ("file-control\tscope=%s\twho=%s\tsubject=%s\tcontrol=%s\tclears=%s"
            % (scope, fc.get("who", ""), fc.get("subject", ""),
               fc.get("control", ""), cleared))
    line = re.sub(r"[\r\n]+", " ", line)[:1000]
    try:
        os.makedirs(os.path.join(proj, ".ravenclaude", "runs", "premise"), exist_ok=True)
        import time as _t
        with open(os.path.join(proj, ".ravenclaude", "runs", "premise",
                               "overrides.log"), "a") as fh:
            fh.write(_t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()) + "\t" + line + "\n")
        os.makedirs(run, exist_ok=True)
        open(applied, "w").write(fc.get("sig", ""))
    except Exception:
        pass

def rc_note():
    """One line naming a control file that exists but clears nothing, and why."""
    fc = rc_load_control()
    if not fc.get("exists") or fc.get("valid"):
        return ""
    missing = [k for k in ("who", "subject", "control") if not fc.get(k)]
    if not fc.get("subjects"):
        missing.append("premise-control")
    return ("a control file EXISTS but is INERT: missing a non-empty "
            + " / ".join(missing) + " line")

def say(kind, fname, why, note=""):
    def flat(s):
        return re.sub(r"[\t\r\n]+", " ", str(s))
    # Field 6 is the TOOL NAME, carried out for the substrate emit below. It is
    # read straight off the payload (a fixed Claude Code enum), so passing it
    # here costs nothing and saves the shell half a second python fork.
    print("%s\t%s\t%s\t%s\t%s\t%s" % (flat(kind), flat(fname), flat(why),
                                      flat(ctrl_path), flat(note), flat(_TOOL)))

# ═══ T-PROSE ═══════════════════════════════════════════════════════════════
# Evaluated FIRST and independently. OR-ed with T-SHAPE below, never AND-ed:
# none of the T-SHAPE exemptions that follow (new-file-only, source-extension-
# only, docs/) may suppress this one, because a diagnosis written into docs/ or
# over a file that already exists IS the damage. It reads no ledger — that
# independence is the whole reason it exists.
# Per-tool content field. Write carries `content`; Edit carries the replacement
# text; MultiEdit carries a list of them. Reading only `content` would have left
# Edit/MultiEdit screened-but-blind — a screen that runs and sees nothing.
if _TOOL == "Write":
    content = str(ti.get("content", "") or "")
elif _TOOL == "Edit":
    content = str(ti.get("new_string", "") or "")
else:
    content = "\n".join(
        str((e or {}).get("new_string", "") or "") for e in (ti.get("edits") or [])
    )
content = content[:200000]

# (1) DURABLE ARTIFACT. Judged on the PROJECT-RELATIVE path, so a tree that
#     happens to live under a temp root is still judged on docs/ vs scratch/
#     rather than on wherever mktemp put it.
rel_p = rc_rel(path, proj)
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
    # (5) A CONDITIONAL CLAUSE IS NOT AN ASSERTION. "when the rule does not apply"
    #     states a CASE; "the rule does not apply" states a FACT. Only the second is
    #     a premise, and this gate exists for premises. Measured 2026-08-12: the
    #     boilerplate heading "## Edge cases / when the rule does NOT apply" is in ALL
    #     35 best-practice files and parses as <subject>+<failure predicate>, so it
    #     tripped (2) on any file with a date inside the +/-6-line window of (3) —
    #     4 of 35 on that day — firing on the section header of the file itself,
    #     which no author chose. Scoped to the text BEFORE the match on the SAME
    #     line, so a real assertion later in the file is untouched.
    #
    #     ⛔ NO APOSTROPHES ANYWHERE IN THIS PYTHON BLOCK. It is embedded in a
    #     single-quoted bash $(...), so one apostrophe in a COMMENT closes the
    #     string and the whole hook dies with "bad substitution" -> exit 1, which
    #     Claude Code treats as a NON-BLOCKING error, i.e. the gate fails OPEN and
    #     silently stops gating. That is why the code above writes doesn\x27t.
    #
    #     ⛔ The tempting fixes are both worse. Dropping `apply|applies` from _FAILS
    #     loses a genuine predicate ("the patch does not apply"). Skipping markdown
    #     headings loses MORE: this repo routinely states real diagnoses in headings
    #     ("## macOS door 2 — `timeout` is absent…", "## The gate that never ran"),
    #     which are exactly the confident claims (2) is for.
    #     The window excludes `,` as well as `.!?` on purpose: without the comma,
    #     "When we checked, the decoder is broken" would be skipped, and that is an
    #     ASSERTION with a temporal preamble, not a conditional. Narrower is right —
    #     a missed skip costs one `control:` line; a missed DENY costs a false premise.
    _COND = re.compile(
        r"(?i:\b(?:when|whenever|if|unless|whether|where|in\s+case|cases?\s+where)\b)"
        r"[^.!?,]{0,24}$"
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
        if _COND.search(_ln[:dm.start()]):
            continue                  # (5) conditional clause -> a case, not a premise
        block = "\n".join(lines[max(0, i - 6):i + 7])
        if not _STAMP.search(block):
            continue                  # (3) unstamped -> a hypothesis, not a premise
        if prose_ctrl or _CTRL.search(block):
            continue                  # (4) a control IS cited -> allowed
        claim = re.sub(r"\s+", " ", dm.group(0)).strip()[:120]
        _fc = rc_load_control()
        if _fc.get("valid") and rc_control_covers(_fc, claim):
            rc_record_control(_fc, "prose:" + claim[:60])
            continue                  # a durable, attributed control file covers it
        say("PROSE", os.path.basename(path),
            "line %d writes a diagnosis as established fact: %s" % (i + 1, claim),
            rc_note())
        sys.exit(0)

# (b) CREATES a file — an edit to something that exists is not a new premise-bearer.
if os.path.exists(path):
    sys.exit(0)

# (c) a SOURCE MODULE. Everything below is deliberately exempt: none of it is a
#     thing whose reason for existing can be a false diagnosis.
rel = rc_rel(path, proj)
# Prefix-exempt: these are top-level areas that never hold a premise-bearing module.
if rel.startswith((".ravenclaude/", "docs/", "node_modules/", ".git/", ".claude/")):
    sys.exit(0)
# Anywhere-exempt: a test/fixture is not an abstraction whose reason for existing is
# a diagnosis — and it can live at any depth (`plugins/x/hooks/tests/`), so a
# startswith check would miss it and gate the very tests that prove this gate works.
if any(seg in rel for seg in ("/test/", "/tests/", "/__tests__/", "/fixtures/")) or \
   rel.startswith(("test/", "tests/", "__tests__/", "fixtures/")):
    sys.exit(0)
# Scratch-area exemption — but ONLY for paths OUTSIDE the project.
# ⛔ This was a bare `"/tmp/" in path` check and it was WRONG on Linux. macOS
# `mktemp -d` yields /var/folders/...; Linux yields /tmp/tmp.XXXX. So on Linux the
# project root ITSELF sat under /tmp, every path matched the exemption, and every
# deny assertion passed VACUOUSLY — green locally on macOS, green-for-the-wrong-
# reason in CI. Caught only because CI runs Linux. Anchor on the project-relative
# path, so "is this scratch?" cannot be decided by where the project happens to live.
_abs = os.path.abspath(path)
_proj = os.path.abspath(proj)
_inside = _abs == _proj or _abs.startswith(_proj + os.sep)
if not _inside:
    if _abs.startswith(("/tmp/", "/var/tmp/", "/private/tmp/")) or "/scratchpad/" in _abs:
        sys.exit(0)
if "/scratchpad/" in rel or rel.startswith(("tmp/", "scratch/")):
    sys.exit(0)
SRC_EXT = (".py", ".sh", ".ts", ".tsx", ".js", ".jsx", ".astro", ".vue", ".svelte",
           ".go", ".rs", ".rb", ".java", ".kt", ".c", ".h", ".cpp", ".cs", ".php", ".mjs")
if not path.endswith(SRC_EXT):
    sys.exit(0)

ledger = os.path.join(run, "probe-ledger.jsonl")
# ⛔ The beacon is SESSION-level, not per-scope. A per-scope beacon would make a
# never-probed worktree indistinguishable from an unwired recorder, and this gate
# fails CLOSED on that — so the first write in every fresh worktree would be
# denied as blind. Blindness is a property of the recorder, not of a scope.
beacon = os.path.join(sess_dir, "recorder-alive")

# ── FAIL CLOSED: is the recorder alive at all? ─────────────────────────────
if not os.path.exists(beacon):
    # No beacon can mean "no Bash ran yet" (genuinely clean) or "the recorder is
    # not wired" (blind). Distinguish by asking whether the recorder EXISTS to be
    # wired. If it is installed but has never run, no tool call has happened yet,
    # so there is no probe to be unresolved -> clean.
    rec = os.path.join(proj, "plugins", "ravenclaude-core", "hooks", "log-probe.sh")
    if os.path.exists(rec):
        sys.exit(0)
    # A BLANKET control file is the recorded, attributed equivalent of
    # RC_PREMISE_OVERRIDE=1 — same power, reachable from a subagent, and it names
    # who took the decision. A subject-scoped file does NOT clear blindness:
    # blindness is not a claim about one subject.
    _fcb = rc_load_control()
    if _fcb.get("valid") and rc_control_blanket(_fcb):
        rc_record_control(_fcb, "blind")
        sys.exit(0)
    say("BLIND", "",
        "the premise recorder (log-probe.sh) is not installed, so this check "
        "cannot see whether an unresolved negative probe exists", rc_note())
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

# ⛔ `indeterminate` (rate-limited / server-error / timeout / unreachable) is
# DELIBERATELY neither arm below. It is a NON-result — the probe never reached
# the question — so it is not evidence of absence and must not block, and it
# proves no capability so it must not resolve. Do NOT "complete" this by
# folding it into the negative arm: a rate-limited probe returns the same 429
# on every retry, so it would be an unclearable block whose only exit is
# RC_PREMISE_OVERRIDE — and a gate whose sole remedy is its own override
# teaches the override, which costs more than the case it covers.
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
    _fc = rc_load_control()
    if _fc.get("valid"):
        _cleared = [f for f in list(unresolved) if rc_control_covers(_fc, f)]
        for f in _cleared:
            unresolved.pop(f, None)
        if _cleared:
            rc_record_control(_fc, ",".join(str(c)[:40] for c in _cleared[:5]))

if unresolved:
    fam, e = next(iter(unresolved.items()))
    say("DENY", os.path.basename(path),
        "%s returned %s (%s)" % (e.get("subject"), e.get("label"), e.get("tool")),
        rc_note())
' "$_dir" 2>/dev/null || true)"

[ -z "$_verdict" ] && exit 0

_kind="$(printf '%s' "$_verdict" | cut -f1)"
_file="$(printf '%s' "$_verdict" | cut -f2)"
_why="$(printf '%s' "$_verdict" | cut -f3)"
_ctrl="$(printf '%s' "$_verdict" | cut -f4)"
_note="$(printf '%s' "$_verdict" | cut -f5)"
_tool="$(printf '%s' "$_verdict" | cut -f6)"

# ── SUBSTRATE EMIT — this gate was UNMEASURABLE until 2026-08-18 ────────────
# ⛔ MEASURED: 463 hook events across 4 real sessions on this machine, from SIX
# hooks (enforce-layout 282, thing-orchestrator 88, guard-destructive 67,
# worktree-guard 18, dod-gate 4, enforce-git-protocol 4) — and ZERO from this
# one, because it never called the emitter. Consequences, both real:
#   * Heimdall and Víðarr showed a clean perimeter while this gate was denying.
#   * Its own false-positive rate could not be measured from the substrate at
#     all. "I have no events" and "I never fire" are indistinguishable — which
#     is this repo's own recorded silent-green shape, on the guard whose
#     precision matters most.
# The 463 IS the positive control: the substrate demonstrably records other
# hooks from the same runs dir, so the empty guard-premise result was a real
# absence, not a broken probe.
#
# ⛔ DERIVED VALUES ONLY. The hook name, a fixed rule token, the tool enum and
# the target BASENAME. The unresolved subject and the prose claim are NOT
# emitted: both are attacker-influenceable text and this log is read back into
# the dashboard and the SessionStart banner. Same invariant as
# capability-orientation.sh / watch-run-state.sh / compact-anchor.sh.
#
# Fail-safe: every step degrades to a no-op. A telemetry write must never be
# able to change a guardrail verdict — the deny below runs either way.
_gp_emit() {
  _gp_helper="$(dirname "${BASH_SOURCE[0]:-$0}")/_emit-event.sh"
  [ -f "$_gp_helper" ] || return 0
  # _emit-event.sh resolves the session id from the caller-scope `payload` var.
  payload="$_input"
  # shellcheck source=/dev/null
  . "$_gp_helper" 2>/dev/null || return 0
  command -v _emit_hook_event >/dev/null 2>&1 || return 0
  _emit_hook_event "guard-premise.sh" "deny" "${_tool:-Write}" \
    "${_file:-}" "${1:-premise-deny}" 2 2>/dev/null || true
}

case "$_kind" in
  BLIND) _gp_rule="premise-recorder-blind" ;;
  PROSE) _gp_rule="premise-unverified-diagnosis" ;;
  *)     _gp_rule="premise-unresolved-negative" ;;
esac

# The file-based escape, printed VERBATIM in every deny. It is the only exit a
# dispatched subagent can actually take: RC_PREMISE_* are environment variables,
# and a variable exported inside a Bash call never reaches this hook process.
# ⛔ It is scoped to this session AND this worktree, so it cannot clear a sibling
# agent, and it is INERT unless all four keys carry a non-empty value.
_ESCAPE="  FILE-BASED CONTROL (works from a SUBAGENT — the env vars do not).
  Write this file with the Write tool, then retry:

    $_ctrl

    premise-control: <subject this covers, or * for all>
    who: <which agent/session ran the control>
    subject: <the claim that was under test>
    control: <the probe you ran -> the result it returned>

  All four keys are REQUIRED and an empty value clears nothing. Every use is
  appended to .ravenclaude/runs/premise/overrides.log — the escape is recorded,
  not silent."
[ -n "$_note" ] && _ESCAPE="⚠ $_note

$_ESCAPE"

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
RC_PREMISE_OVERRIDE=1 to proceed and record the override.

$_ESCAPE
  (blindness is not a claim about one subject, so only \`premise-control: *\`
   clears it here.)"
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
  4. RC_PREMISE_OVERRIDE=1           proceed anyway; the override is recorded

$_ESCAPE"
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
  3. RC_PREMISE_OVERRIDE=1           → proceed anyway; the override is recorded

⛔ The ledger is scoped to THIS git worktree, so what you see above was recorded
by work in this tree — not by a sibling agent in another one.

$_ESCAPE"
fi

# Emitted immediately before the deny, never on the override path above — an
# override is already recorded in overrides.log and is not a perimeter event.
_gp_emit "$_gp_rule"

printf '%s' "$(python3 -c '
import json,sys
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse",
  "permissionDecision":"deny","permissionDecisionReason":sys.argv[1]}}))' "$_reason")"
echo "$_reason" >&2
exit 2
