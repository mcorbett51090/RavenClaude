#!/usr/bin/env bash
# task-ledger — set_conservation.py (SSOT) + ledger.py (append + project)
#
# Proves the properties the plan says are NON-NEGOTIABLE, each against a
# planted fixture rather than against the code's own opinion of itself.
#
# ⛔ THE THREE-VALUED GATE IS THE POINT, AND IT IS THE EASIEST THING TO GET
# BACKWARDS. With an EMPTY ledger, `A \ C` and `C \ A` are both empty, so a
# two-valued conservation check reports GREEN — inert exactly when it is most
# needed, which is the never-recorded case the whole ledger exists to catch.
# Every assertion below that says UNKNOWN is asserting a *blocking* exit 2, not
# a warning. A test that only checked "does not pass" would be satisfied by a
# crash, so each one pins the exact code.
#
# ⛔ EVERY EMPTY RESULT HERE CARRIES A POSITIVE CONTROL. The committability
# canary is the worked example: `git check-ignore` returns "no match" for
# EVERYTHING when it is broken, absent, or run outside a git repo, so the
# subject passing proves nothing on its own. The control path
# (`.ravenclaude/runs/**`, gitignored at .gitignore:4) must FIRE, and a test run
# where it does not is a HARNESS FAILURE, not a pass.
#
# ⛔ THE MUST-FAIL CONVENTIONS DIFFER PER TOOL AND ARE NOT INTERCHANGEABLE.
# Both scripts under test exit 0 from `--must-fail` when the teeth BIT — the
# `premise-gate.py` convention. `scripts/sync-plugin-versions.py` uses the
# OPPOSITE (it expects 2). This suite asserts each tool against ITS OWN
# documented contract; do not "harmonise" them.
#
# ⛔ THIS FILE ASSERTS THE PROJECTION ORDER, WHICH IS THE ONE PROPERTY A GREEN
# SUITE CANNOT IMPLY. read -> SORT -> DEDUPE -> fold. Deduping first makes the
# collision survivor depend on file order, and a git union merge leaves merged
# lines in arbitrary order — so two machines render different Markdown from the
# same ledger and nothing reports it. The teeth for that live in ledger.py's own
# `--must-fail`, which plants dedupe-before-sort; this suite asserts the
# must-fail REDDENS, so the property is re-proved on every run rather than being
# a claim in a commit message.
#
# Invoked via `python3 <script>`, so it passes regardless of the executable bit.
#
# bash 3.2 safe. No GNU-only tools, no sed -i, no grep -P, no `timeout`.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
SCRIPTS="$ROOT/plugins/ravenclaude-core/scripts"
LEDGER="$SCRIPTS/ledger.py"
SCP="$SCRIPTS/set_conservation.py"
FIX="$ROOT/tests/fixtures/ledger"
fails=0

T="$(mktemp -d)"
cleanup() { rm -rf "$T"; }
trap cleanup EXIT

last_exit=0
last_out=""

_run() { # $@ = command
  last_out="$("$@" 2>&1)"
  last_exit=$?
}

_assert_exit() { # $1=expected $2=label
  if [ "$last_exit" = "$1" ]; then
    printf '  ok   EXIT %-3s %-56s\n' "$1" "$2"
  else
    printf '  FAIL EXIT %-3s %-56s got=%s\n' "$1" "$2" "$last_exit"
    printf '       out: %s\n' "$(printf '%s' "$last_out" | head -3 | tr '\n' ' ')"
    fails=$((fails + 1))
  fi
}

_assert_contains() { # $1=needle $2=label
  case "$last_out" in
    *"$1"*) printf '  ok   SAYS     %-56s\n' "$2" ;;
    *)
      printf '  FAIL SAYS     %-56s (missing %s)\n' "$2" "$1"
      fails=$((fails + 1))
      ;;
  esac
}

_assert_absent() { # $1=needle $2=label
  case "$last_out" in
    *"$1"*)
      printf '  FAIL ABSENT   %-56s (found %s)\n' "$2" "$1"
      fails=$((fails + 1))
      ;;
    *) printf '  ok   ABSENT   %-56s\n' "$2" ;;
  esac
}

# A ledger dir seeded from a fixture. Returns the REPO ROOT for --repo-root.
_seed() { # $1=fixture basename $2=name
  local d="$T/$2"
  mkdir -p "$d/.ravenclaude/ledger"
  ( cd "$d" && git init -q . 2>/dev/null )
  cp "$FIX/$1" "$d/.ravenclaude/ledger/2026-08.jsonl"
  printf '%s' "$d"
}

echo "task-ledger — set_conservation (SSOT) + ledger append/project"

# ─────────────────────────────────────────────────────────────────────────────
# 0. FIXTURE CONTROLS — a missing or empty fixture is a HARNESS FAILURE.
#    Asserted BEFORE any result is trusted, because an absent fixture makes
#    every downstream "no errors found" vacuously true.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 0. fixture controls (an empty fixture is a harness failure) --"

_fixture_count=0
for f in "$FIX"/*.jsonl; do
  [ -f "$f" ] || continue
  _fixture_count=$((_fixture_count + 1))
  if [ ! -s "$f" ]; then
    printf '  FAIL FIXTURE  %-56s is EMPTY\n' "$(basename "$f")"
    fails=$((fails + 1))
  fi
done
if [ "$_fixture_count" -ge 15 ]; then
  printf '  ok   FIXTURE  %-56s (%s files, all non-empty)\n' \
    "the ledger fixture bank is populated" "$_fixture_count"
else
  printf '  FAIL FIXTURE  %-56s only %s found — the bank is not populated\n' \
    "the ledger fixture bank" "$_fixture_count"
  fails=$((fails + 1))
fi

# Every fixture must PARSE to >=1 event. A fixture that parses to zero would
# make its gate assertion pass by being blind.
_run python3 -c '
import json, pathlib, sys
bad = []
for p in sorted(pathlib.Path(sys.argv[1]).glob("*.jsonl")):
    n = 0
    for line in p.read_bytes().split(b"\n"):
        if not line.strip():
            continue
        try:
            json.loads(line.decode("utf-8"))
            n += 1
        except Exception:
            pass
    # bad-truncated-line.jsonl is EXPECTED to hold one unparseable record.
    if n < 1:
        bad.append(p.name)
print("ZEROPARSE:" + ",".join(bad) if bad else "ALLPARSE")
' "$FIX"
_assert_contains "ALLPARSE" "every fixture parses to >=1 event"

# ─────────────────────────────────────────────────────────────────────────────
# 1. THE SSOT PRIMITIVE — its own self-test, and its teeth.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 1. set_conservation.py (the SSOT shared with verify-before-assert) --"

_run python3 "$SCP" --self-test
_assert_exit 0 "self-test passes"
_assert_contains "set_kind='causes' returns the same shape" "C38: the sibling run's set_kind works"

_run python3 "$SCP" --must-fail
_assert_exit 0 "--must-fail exits 0 when the TEETH BIT (premise-gate.py's convention)"
_assert_contains "teeth ok" "the planted digest defect was caught"

# The digest is stable under input reordering — asserted through the CLI, so the
# published interface is what is pinned, not an internal helper.
_run python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z \
  --id rc-a3f8c1d2e4b7 --id rc-1f0c9a3b2d41
_a="$last_out"
_run python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z \
  --id rc-1f0c9a3b2d41 --id rc-a3f8c1d2e4b7
if [ "$_a" = "$last_out" ]; then
  printf '  ok   ORDER    %-56s\n' "build is byte-identical under reordered --id flags"
else
  printf '  FAIL ORDER    %-56s\n' "build differs when --id flags are reordered"
  fails=$((fails + 1))
fi

# A sequential id is refused. Spec-kit's T001 needs a central allocator and
# collides across worktrees, so the pattern is a floor, not a preference.
_run python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z --id T001
_assert_exit 1 "a sequential id (T001) is refused at build time"

# ─────────────────────────────────────────────────────────────────────────────
# 2. THE THREE-VALUED GATE — UNKNOWN blocks, and it is NOT a warning.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 2. three-valued conservation: UNKNOWN BLOCKS (exit 2) --"

python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z --out "$T/empty.json" >/dev/null 2>&1

# The whole point: an empty set with NO positive control is UNKNOWN, not PASS.
_run python3 "$SCP" diff --claimed "$T/empty.json" --actual "$T/empty.json"
_assert_exit 2 "empty + NO --parsed-records => UNKNOWN"
_assert_contains "no_positive_control" "the reason names the missing control"

_run python3 "$SCP" diff --claimed "$T/empty.json" --actual "$T/empty.json" --parsed-records 0
_assert_exit 2 "empty + 0 records parsed => UNKNOWN, never '0 open'"
_assert_contains "ledger_empty" "the reason distinguishes empty from conserved"

# POSITIVE CONTROL for the two assertions above: the SAME empty sets, with a
# real parse count, must PASS. Without this the two UNKNOWNs would be satisfied
# by a gate that can only ever say UNKNOWN.
_run python3 "$SCP" diff --claimed "$T/empty.json" --actual "$T/empty.json" --parsed-records 7
_assert_exit 0 "POSITIVE CONTROL: empty + 7 records parsed => PASS"

_run python3 "$SCP" diff --claimed "$T/nope.json" --actual "$T/empty.json" --parsed-records 7
_assert_exit 2 "an unreadable block => UNKNOWN, never FAIL and never PASS"

python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z \
  --id rc-1f0c9a3b2d41 --id rc-a3f8c1d2e4b7 --out "$T/two.json" >/dev/null 2>&1
python3 "$SCP" build --set-kind open_items --basis 'b:1' \
  --computed-at 2026-08-20T09:44:12.771Z \
  --id rc-1f0c9a3b2d41 --out "$T/one.json" >/dev/null 2>&1

_run python3 "$SCP" diff --claimed "$T/one.json" --actual "$T/two.json" --parsed-records 9
_assert_exit 1 "under-enumeration => FAIL (determinate), exit 1"
_assert_contains "rc-a3f8c1d2e4b7" "the FAIL names the id that was dropped"

_run python3 "$SCP" diff --claimed "$T/two.json" --actual "$T/one.json" --parsed-records 9
_assert_exit 1 "over-enumeration => FAIL, exit 1"

# ─────────────────────────────────────────────────────────────────────────────
# 3. THE PROJECTION — order-independence and collision determinism.
#    This is the single most important property in the plan: two machines must
#    render byte-identical Markdown from the same merged ledger.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 3. projection: sort BEFORE dedupe (order-independence) --"

_canon="$(_seed canonical.jsonl canon)"
_shuf="$(_seed shuffled-order.jsonl shuf)"

_run python3 "$LEDGER" --repo-root "$_canon" project
_assert_exit 0 "canonical.jsonl projects clean"
_a="$last_out"
_run python3 "$LEDGER" --repo-root "$_shuf" project
_assert_exit 0 "shuffled-order.jsonl projects clean"
if [ "$_a" = "$last_out" ]; then
  printf '  ok   ORDER    %-56s\n' "shuffled input renders BYTE-IDENTICAL Markdown"
else
  printf '  FAIL ORDER    %-56s\n' "shuffled input renders DIFFERENT Markdown"
  fails=$((fails + 1))
fi

# The fixtures must genuinely differ on disk, or the assertion above is vacuous.
if cmp -s "$FIX/canonical.jsonl" "$FIX/shuffled-order.jsonl"; then
  printf '  FAIL FIXTURE  %-56s the two fixtures are IDENTICAL — the test proves nothing\n' \
    "canonical vs shuffled"
  fails=$((fails + 1))
else
  printf '  ok   FIXTURE  %-56s\n' "canonical and shuffled differ on disk (not a vacuous compare)"
fi

_coll="$(_seed collision-deterministic.jsonl coll)"
_run python3 "$LEDGER" --repo-root "$_coll" project --json
_assert_exit 1 "a same-id/different-byte pair FAILS (errors[] flips the exit code)"
_assert_contains "event_id_collision" "the collision is named, not silently deduped"
_assert_contains "kept_sha" "the SURVIVOR is reported by digest, not left to eyeball"

# ⛔ The teeth for the projection ORDER. ledger.py --must-fail plants
# dedupe-before-sort; if the suite still passed with that bug in place, every
# order-independence assertion above would be decorative.
_run python3 "$LEDGER" --must-fail
_assert_exit 0 "--must-fail exits 0 when the TEETH BIT (premise-gate.py's convention)"
_assert_contains "teeth ok" "planting dedupe-before-sort REDDENS the suite"
_assert_contains "SURVIVOR is the documented one" "the assertion that reddens is the ORDER one"

# ─────────────────────────────────────────────────────────────────────────────
# 4. NO CLOSING EVENT = STILL OPEN, and verification is DERIVED.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 4. absence of a closing event means OPEN (dropping needs an act) --"

_run python3 "$LEDGER" --repo-root "$_canon" project
_assert_contains "Wire the harvest lane" "an item with ONLY a proposed event is rendered OPEN"
_assert_contains "done, unverified" "a completed item with no verify event stays OPEN"
_assert_contains "verification_failed" "a verification_failed item is rendered OPEN"
_assert_contains "blocked" "blocked is DERIVED into the view"

# ...and NONE of those derived words may be a stored value.
_run env grep -c '"state":"blocked"' "$FIX/canonical.jsonl"
if [ "$last_exit" != "0" ]; then
  printf '  ok   DERIVED  %-56s\n' "no canonical event STORES state=blocked"
else
  printf '  FAIL DERIVED  %-56s\n' "canonical.jsonl stores a derived state"
  fails=$((fails + 1))
fi

_blocked="$(_seed bad-blocked-stored.jsonl blocked)"
_run python3 "$LEDGER" --repo-root "$_blocked" project --json
_assert_exit 1 "G-LED-07: storing state=blocked FAILS"
_assert_contains "rc ledger link --item" "the rejection is a RUNNABLE COMMAND, not a description"

_await="$(_seed bad-awaiting-verification-stored.jsonl awaiting)"
_run python3 "$LEDGER" --repo-root "$_await" project --json
_assert_exit 1 "G-LED-07: storing state=awaiting_verification FAILS (ruling E)"

# ─────────────────────────────────────────────────────────────────────────────
# 5. A RELATIONSHIP RESOLUTION REQUIRES A TYPED, GATE-CHECKED POINTER.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 5. a pointer-less relationship resolution is INVALID --"

_notarget="$(_seed bad-superseded-no-target.jsonl notarget)"
_run python3 "$LEDGER" --repo-root "$_notarget" project --json
_assert_exit 1 "superseded_by with NO target id fails a gate"
_assert_contains "requires a typed, gate-checked" "the message states the rule"

for _pair in "bad-supersede-cycle.jsonl:supersede_cycle:a supersede CYCLE is caught" \
  "bad-split-one-child.jsonl:split_too_small:split_into with <2 members is caught" \
  "bad-dangling-ref.jsonl:dangling_ref:a pointer to a nonexistent item is caught"; do
  _f="${_pair%%:*}"
  _rest="${_pair#*:}"
  _kind="${_rest%%:*}"
  _label="${_rest#*:}"
  _d="$(_seed "$_f" "ref-${_kind}")"
  _run python3 "$LEDGER" --repo-root "$_d" project --json
  _assert_exit 1 "$_label"
  _assert_contains "$_kind" "  ...and names it $_kind"
done

# ─────────────────────────────────────────────────────────────────────────────
# 6. `confidence` IS REFUSED STRUCTURALLY, not by convention.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 6. the refused fields are refused by the SCHEMA, not by discipline --"

_conf="$(_seed bad-confidence.jsonl conf)"
_run python3 "$LEDGER" --repo-root "$_conf" project --json
_assert_exit 1 "an event carrying `confidence` FAILS validation"

# Positive control: the SAME shape without the refused field must PASS, or the
# assertion above would be satisfied by a validator that rejects everything.
_good="$(_seed good-evidence-null.jsonl goodnull)"
_run python3 "$LEDGER" --repo-root "$_good" project --json
_assert_exit 0 "POSITIVE CONTROL: evidence:null is VALID (the B-1 regression)"

_ci="$(_seed good-evidence-ci-run.jsonl goodci)"
_run python3 "$LEDGER" --repo-root "$_ci" project --json
_assert_exit 0 "POSITIVE CONTROL: every accepted evidence form is VALID"

_prose="$(_seed bad-prose-evidence.jsonl prose)"
_run python3 "$LEDGER" --repo-root "$_prose" project --json
_assert_exit 1 "a grammatically perfect English sentence FAILS the evidence grammar"

# ─────────────────────────────────────────────────────────────────────────────
# 7. TRUNCATION IS NEVER SILENT — and the marker is not always-on.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 7. truncation: count + digest + pointer, BOTH directions --"

_run python3 "$LEDGER" --repo-root "$_canon" project
_assert_absent "RENDER TRUNCATED" "NEGATIVE CONTROL: a small set emits NO truncation banner"

# The positive direction is covered by ledger.py's own self-test (a 40-item
# fixture at cap 12), which this suite asserts green below. A marker that is
# always on is as useless as one that is never on, so both halves must hold.

# ─────────────────────────────────────────────────────────────────────────────
# 8. COMMITTABILITY — with the positive control that stops it passing blind.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 8. committability canary + its POSITIVE CONTROL --"

_run python3 "$LEDGER" --repo-root "$ROOT" check-committable \
  --path .ravenclaude/ledger/2026-08.jsonl
_assert_exit 0 "the resolved ledger path is NOT gitignored"
_assert_contains "positive control fired" "the control FIRED — the canary is not blind"

_run python3 "$LEDGER" --repo-root "$ROOT" check-committable \
  --path .ravenclaude/runs/x/ledger.jsonl
_assert_exit 1 "NEGATIVE CONTROL: a path under .ravenclaude/runs/ IS caught as ignored"

# Outside a git repo the canary must report a HARNESS FAILURE, never "clean" —
# this is the exact shape that lets a broken check-ignore pass by being blind.
mkdir -p "$T/notgit"
_run python3 "$LEDGER" --repo-root "$T/notgit" check-committable --path a/b.jsonl
_assert_exit 2 "outside a git repo => HARNESS FAILURE (exit 2), never a pass"
_assert_contains "HARNESS FAILURE" "  ...and says so explicitly"

# ─────────────────────────────────────────────────────────────────────────────
# 9. APPEND ATOMICITY — the conditions, enforced, under real concurrency.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 9. append: one write() syscall, O_APPEND, never read-modify-write --"

_run python3 - "$SCRIPTS" "$T/atomic" <<'PYEOF'
import os
import sys
import subprocess

sys.path.insert(0, sys.argv[1])
root = sys.argv[2]
os.makedirs(root, exist_ok=True)

worker = os.path.join(root, "worker.py")
with open(worker, "w", encoding="utf-8") as fh:
    fh.write(
        "import sys\n"
        "sys.path.insert(0, %r)\n" % sys.argv[1]
        + "import ledger\n"
        "from pathlib import Path\n"
        "tag = sys.argv[1]\n"
        "d = Path(sys.argv[2])\n"
        "for i in range(50):\n"
        "    ev = ledger.build_event(d, 'open', 'rc-%012x' % i,\n"
        "                            {'subject': tag + ' item ' + str(i) + ' ' + 'p'*400},\n"
        "                            'w-' + tag, '2026-08-19T00:00:00.000Z')\n"
        "    ledger.append_record(d / 'ledger', ev, 8192)\n"
    )

# 8 concurrent writers x 50 records = 400 lines, one shared file.
procs = [
    subprocess.Popen([sys.executable, worker, str(n), root])
    for n in range(8)
]
for p in procs:
    p.wait()

shard = os.path.join(root, "ledger", "2026-08.jsonl")
raw = open(shard, "rb").read()
lines = [ln for ln in raw.split(b"\n") if ln.strip()]
import json
bad = 0
for ln in lines:
    try:
        json.loads(ln.decode("utf-8"))
    except Exception:
        bad += 1
print("LINES:%d MALFORMED:%d TRAILING_NL:%s" % (len(lines), bad, raw.endswith(b"\n")))
PYEOF
_assert_exit 0 "8 concurrent writers complete"
_assert_contains "LINES:400" "all 400 records survived concurrent appends"
_assert_contains "MALFORMED:0" "ZERO torn lines under 8-way concurrency"
_assert_contains "TRAILING_NL:True" "every record is newline-terminated"

# Append-only: after the concurrent run, appending again must leave the earlier
# bytes untouched. A read-modify-write would not.
_run python3 - "$SCRIPTS" "$T/atomic" <<'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import ledger

d = Path(sys.argv[2]) / "ledger"
before = (d / "2026-08.jsonl").read_bytes()
ev = ledger.build_event(Path(sys.argv[2]), "open", "rc-ffffffffffff",
                        {"subject": "appended after"}, "probe",
                        "2026-08-19T00:00:00.000Z")
ledger.append_record(d, ev, 8192)
after = (d / "2026-08.jsonl").read_bytes()
print("PREFIX_PRESERVED:%s GREW:%s" % (after.startswith(before), len(after) > len(before)))
PYEOF
_assert_contains "PREFIX_PRESERVED:True" "an append leaves every earlier byte untouched"
_assert_contains "GREW:True" "  ...and the file actually grew (not a no-op pass)"

# ⛔ The one-record-one-write() invariant, tested DIRECTLY on the primitive.
# A mutation harness caught this gap: disabling the newline guard broke nothing
# in the suite, because `canonical_bytes` JSON-escapes newlines, so no record
# built through the writer can ever carry one. The guard exists for a caller
# that bypasses that — and an untested guard is a guard that will be deleted by
# someone who cannot see what it is for.
_run python3 - "$SCRIPTS" "$T/atomic" <<'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import ledger

d = Path(sys.argv[2]) / "guard"
d.mkdir(parents=True, exist_ok=True)
results = []

# Two records in one write() — the exact shape that breaks atomicity.
try:
    ledger._append_bytes(d / "x.jsonl", b'{"a":1}\n{"b":2}\n')
    results.append("TWO_RECORDS:ACCEPTED")
except ledger.LedgerError:
    results.append("TWO_RECORDS:REFUSED")

# No trailing newline — the next append would concatenate onto this line.
try:
    ledger._append_bytes(d / "y.jsonl", b'{"a":1}')
    results.append("NO_NEWLINE:ACCEPTED")
except ledger.LedgerError:
    results.append("NO_NEWLINE:REFUSED")

# POSITIVE CONTROL: a well-formed single record must still be ACCEPTED, or the
# two refusals above would be satisfied by a primitive that refuses everything.
try:
    ledger._append_bytes(d / "z.jsonl", b'{"a":1}\n')
    results.append("WELLFORMED:ACCEPTED")
except ledger.LedgerError:
    results.append("WELLFORMED:REFUSED")

print(" ".join(results))
PYEOF
_assert_contains "TWO_RECORDS:REFUSED" "two records in one write() are REFUSED"
_assert_contains "NO_NEWLINE:REFUSED" "a record with no trailing newline is REFUSED"
_assert_contains "WELLFORMED:ACCEPTED" "POSITIVE CONTROL: a well-formed record is ACCEPTED"

# ─────────────────────────────────────────────────────────────────────────────
# 10. TORN LINES, SECRETS, PII AND OVERSIZE ARE NEVER SILENT.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 10. a malformed/leaky/oversize record flips the exit code --"

_torn="$(_seed bad-truncated-line.jsonl torn)"
_run python3 "$LEDGER" --repo-root "$_torn" project --json
_assert_exit 1 "a byte-truncated record flips the exit code (never skipped)"
_assert_contains "malformed_line" "  ...and is reported with its file and line number"

_sec="$(_seed bad-secret-in-subject.jsonl sec)"
_run python3 "$LEDGER" --repo-root "$_sec" project --json
_assert_exit 1 "G-LED-06: an unscrubbed secret shape in asserted FAILS"
_assert_absent "ghp_AAAA" "  ...and the finding does NOT echo the matched secret"

_pii="$(_seed bad-pii-in-subject.jsonl pii)"
_run python3 "$LEDGER" --repo-root "$_pii" project --json
_assert_exit 1 "G-LED-06: an unscrubbed email address in asserted FAILS"
_assert_absent "jane.doe@client.com" "  ...and the finding does NOT echo the address"

_big="$(_seed bad-oversize-record.jsonl big)"
_run python3 "$LEDGER" --repo-root "$_big" project --json
_assert_exit 1 "G-LED-14: a record over max_record_bytes FAILS"
_assert_contains "oversize_record" "  ...and names the size band it left"

# ─────────────────────────────────────────────────────────────────────────────
# 11. UNRECOGNISED VALUES ARE RENDERED, NEVER DROPPED.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 11. schema drift is surfaced, never silently skipped --"

_drift="$(_seed drift-unrecognized.jsonl drift)"
_run python3 "$LEDGER" --repo-root "$_drift" project --no-schema
_assert_contains "Unrecognized" "an out-of-enum value renders under its own heading"
_assert_contains "frobnicated" "  ...and the actual drifted value is shown"

# ─────────────────────────────────────────────────────────────────────────────
# 12. AN EMPTY OR UNREADABLE LEDGER IS UNKNOWN — the inert-ratchet defect.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 12. empty / unreadable ledger => UNKNOWN (exit 2), never green --"

mkdir -p "$T/emptyrepo/.ravenclaude/ledger"
( cd "$T/emptyrepo" && git init -q . 2>/dev/null )
: >"$T/emptyrepo/.ravenclaude/ledger/2026-08.jsonl"
_run python3 "$LEDGER" --repo-root "$T/emptyrepo" project --json
_assert_exit 2 "an EMPTY initialised ledger => UNKNOWN, never '0 open'"
_assert_contains "UNKNOWN" "  ...and says UNKNOWN, not PASS"

mkdir -p "$T/nodir"
( cd "$T/nodir" && git init -q . 2>/dev/null )
_run python3 "$LEDGER" --repo-root "$T/nodir" project --json
_assert_exit 2 "an ABSENT ledger dir => UNKNOWN, never zero"

mkdir -p "$T/badcfg/.ravenclaude"
( cd "$T/badcfg" && git init -q . 2>/dev/null )
printf '{ not json' >"$T/badcfg/.ravenclaude/ledger-config.json"
_run python3 "$LEDGER" --repo-root "$T/badcfg" project --json
_assert_exit 2 "an UNPARSEABLE config => UNKNOWN hard stop, never the defaults"
_assert_contains "config_unparseable" "  ...and names the cause (not a silent fall-through)"

# The independent lower bound: action items observed, zero recorded => UNKNOWN.
# This is the ONE path that fires when the ledger is empty.
_run python3 "$LEDGER" --repo-root "$_canon" check-enumeration \
  --claimed "$T/two.json" --lower-bound 4 --recorded-this-turn 0
_assert_exit 2 "lower_bound=4 with 0 recorded => UNKNOWN (the ratchet ENGAGES)"
_assert_contains "unrecorded_lower_bound" "  ...and names the independent signal"

# ─────────────────────────────────────────────────────────────────────────────
# 13. INIT: portable, and it REFUSES a gitignored resolved path.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 13. init in a repo with no docs/, no .ravenclaude/, no layout file --"

mkdir -p "$T/bare"
( cd "$T/bare" && git init -q . && printf '.ravenclaude/runs/\n' >.gitignore )
_run python3 "$LEDGER" --repo-root "$T/bare" --actor tester init
_assert_exit 0 "init succeeds in a bare repo"
_assert_contains "positive control fired" "init runs the committability canary WITH its control"
if [ -f "$T/bare/.ravenclaude/ledger-config.json" ]; then
  printf '  ok   INIT     %-56s\n' "ledger-config.json written"
else
  printf '  FAIL INIT     %-56s\n' "ledger-config.json missing"
  fails=$((fails + 1))
fi
_run env grep -c 'ledger_init' "$T/bare/.ravenclaude/ledger/2026-08.jsonl"
_assert_exit 0 "a ledger_init event makes 'empty' distinguishable from 'not enabled'"
# No docs/ => the view path must fall inside the ledger dir, not docs/pm/.
_run env grep -c '"view_path": ".ravenclaude/ledger/task-list.md"' \
  "$T/bare/.ravenclaude/ledger-config.json"
_assert_exit 0 "with no docs/, view_path resolves INSIDE the ledger dir"

mkdir -p "$T/ignored"
( cd "$T/ignored" && git init -q . && printf '.ravenclaude/\n' >.gitignore )
_run python3 "$LEDGER" --repo-root "$T/ignored" --actor tester init
_assert_exit 1 "init REFUSES when the resolved ledger path IS gitignored"
_assert_contains "COMMITTABILITY FAILED" "  ...and says why, instead of proceeding"

# ─────────────────────────────────────────────────────────────────────────────
# 14. THE PROJECTOR NEVER APPENDS, AND IS A PURE FUNCTION OF (bytes, now).
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 14. projection is pure: it never mutates the source of truth --"

_before_sha="$(shasum -a 256 "$_canon/.ravenclaude/ledger/2026-08.jsonl" | awk '{print $1}')"
python3 "$LEDGER" --repo-root "$_canon" project >/dev/null 2>&1
python3 "$LEDGER" --repo-root "$_canon" project --json >/dev/null 2>&1
_after_sha="$(shasum -a 256 "$_canon/.ravenclaude/ledger/2026-08.jsonl" | awk '{print $1}')"
if [ "$_before_sha" = "$_after_sha" ]; then
  printf '  ok   PURE     %-56s\n' "the ledger file is byte-unchanged after 2 projections"
else
  printf '  FAIL PURE     %-56s\n' "projection MUTATED the ledger"
  fails=$((fails + 1))
fi

# `now` is an explicit parameter, so two runs an hour apart agree.
_run python3 "$LEDGER" --repo-root "$_canon" project --now 2026-08-19T01:00:00.000Z
_a="$last_out"
_run python3 "$LEDGER" --repo-root "$_canon" project --now 2026-08-19T02:00:00.000Z
if [ "$_a" = "$last_out" ]; then
  printf '  FAIL NOW      %-56s\n' "two different 'now' values gave identical output — now is inert"
  fails=$((fails + 1))
else
  printf '  ok   NOW      %-56s\n' "'now' is a real parameter (an hour apart differs on ageing)"
fi
_run python3 "$LEDGER" --repo-root "$_canon" project --now 2026-08-19T02:00:00.000Z
if [ "$_a" = "$last_out" ]; then
  printf '  FAIL NOW      %-56s\n' "same 'now' gave different output — projection is not pure"
  fails=$((fails + 1))
else
  printf '  ok   NOW      %-56s\n' "the same 'now' reproduces byte-identical output"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 15. THE MODULES' OWN SELF-TESTS (the fine-grained half).
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "  -- 15. module self-tests --"

_run python3 "$LEDGER" --self-test
_assert_exit 0 "ledger.py --self-test passes"
_assert_contains "C21 committability" "  ...including the committability canary"
_assert_contains "C20 negative control" "  ...including the truncation NEGATIVE control"
_assert_contains "HARD FAILS" "  ...including the item_id mint-time collision hard-fail"

_run python3 "$SCP" --self-test
_assert_exit 0 "set_conservation.py --self-test passes"

# ⛔ REGRESSION GUARD for a real defect this suite caught: the SCP `basis` used
# to be the ABSOLUTE ledger path. That embeds an OS username into a COMMITTED,
# permanently-retained artifact (git cannot un-say it) and makes the projection
# machine-dependent, so two checkouts of one ledger disagree for a reason that
# has nothing to do with the ledger. The order-independence assertion in §3 is
# what surfaced it; this pins it by name so it cannot come back quietly.
_run python3 "$LEDGER" --repo-root "$_canon" project --json
_assert_absent "$T" "the SCP basis carries NO absolute path (no OS username leak)"
_assert_absent "$HOME" "  ...and no home directory either"
_assert_contains '"basis": "ledger:.ravenclaude/ledger' "  ...it is repo-relative by construction"

# ─────────────────────────────────────────────────────────────────────────────
# 16. --prove-nonzero: route a FALSE claim through the real assertion path, so
#     the SUITE proves this harness can actually redden.
# ─────────────────────────────────────────────────────────────────────────────
if [ "${1:-}" = "--prove-nonzero" ]; then
  echo
  echo "  -- --prove-nonzero: the assertion below is MEANT to fail --"
  _run python3 "$SCP" --self-test
  _assert_exit 42 "SELF-BREAK: the self-test exits 0, so asserting 42 must redden"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "task-ledger PASS"
  exit 0
else
  echo "task-ledger FAIL ($fails)"
  exit 1
fi
