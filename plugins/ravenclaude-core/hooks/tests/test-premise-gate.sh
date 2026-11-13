#!/usr/bin/env bash
# Gate 177 — the premise gate (log-probe.sh + guard-premise.sh).
#
# A gate that cannot FAIL proves nothing, so every must_pass here is paired with a
# planted defect. Both neuterings were OBSERVED red, not assumed (2026-08-08):
#
#   guard-premise.sh -> `exit 0` (whole gate)   18/18 becomes 12 passed / 6 failed
#   T-PROSE conjunct gate -> `if False:`        18/18 becomes 15 passed / 3 failed
#
# The second number is the one that matters structurally: with T-PROSE dead, all
# NINE T-SHAPE assertions still pass and only the three T-PROSE denies go red. The
# triggers are therefore genuinely OR-ed — neither is carrying the other.
#
# Test 1 IS Incident 1, replayed: probe -> 404 -> create Email.astro.
# Section 6 is the same incident replayed on an EMPTY ledger, where T-SHAPE is
# structurally blind (a prior session, or a context compaction) and only the
# written-down premise remains to catch.
#
# NOTE: the hooks are fed with a here-string, NOT `printf ... | bash`. The pipe form
# put a fetch command and `| bash` in one payload and the command-review tribunal
# denied the write on sce.curl-pipe-shell — a false positive, but the here-string is
# equivalent and unambiguous, so it is the right adjustment rather than an exemption.
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"
T=$(mktemp -d)
mkdir -p "$T/plugins/ravenclaude-core/hooks" "$T/src"
cp "$H/log-probe.sh" "$T/plugins/ravenclaude-core/hooks/"    # recorder "installed"
export CLAUDE_PROJECT_DIR="$T"
pass=0; fail=0
chk(){ if [ "$2" = "$3" ]; then echo "  OK   $1"; pass=$((pass+1));
       else echo "  FAIL $1 (expected exit $2, got $3)"; fail=$((fail+1)); fi; }

post(){ bash "$H/log-probe.sh" <<<"$1"; }
pre(){ bash "$H/guard-premise.sh" <<<"$1" >/dev/null 2>&1; echo $?; }

NEG='{"session_id":"teeth","tool_name":"Bash","tool_input":{"command":"fetch https://www.ravenpower.net/cdn-cgi/l/email-protection"},"tool_response":{"stdout":"404","stderr":""}}'
CTL='{"session_id":"teeth","tool_name":"Bash","tool_input":{"command":"fetch https://www.ravenpower.net/cdn-cgi/trace"},"tool_response":{"stdout":"200","stderr":""}}'
NEWSRC='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/src/Email.astro"}}'
EXISTING='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/src/Existing.astro"}}'
DOCS='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/docs/notes.md"}}'
TESTF='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$T"'/plugins/x/hooks/tests/t.sh"}}'

echo "-- 1. THE REPLAY: Incident 1, step for step --"
post "$NEG"
chk "new source module after a 404 is DENIED" 2 "$(pre "$NEWSRC")"

echo "-- 2. The control probe resolves it (the ten-second fix) --"
post "$CTL"
chk "same module ALLOWED once a control passes" 0 "$(pre "$NEWSRC")"

echo "-- 3. Friction budget: what must NOT be touched --"
rm -rf "$T/.ravenclaude"; post "$NEG"
touch "$T/src/Existing.astro"
chk "editing an EXISTING file is allowed"     0 "$(pre "$EXISTING")"
mkdir -p "$T/docs"
chk "writing docs/ is allowed"                0 "$(pre "$DOCS")"
mkdir -p "$T/plugins/x/hooks/tests"
chk "a nested tests/ path is allowed"         0 "$(pre "$TESTF")"

echo "-- 4. FAIL CLOSED: a blind gate must never say clean --"
B=$(mktemp -d); mkdir -p "$B/src"            # recorder NOT installed
export CLAUDE_PROJECT_DIR="$B"
BLIND='{"session_id":"teeth","tool_name":"Write","tool_input":{"file_path":"'"$B"'/src/New.astro"}}'
chk "recorder absent -> DENIED (blind, not clean)" 2 "$(pre "$BLIND")"

echo "-- 5. Escape hatches work and are recorded --"
export CLAUDE_PROJECT_DIR="$T"
chk "RC_PREMISE_OVERRIDE=1 allows"            0 "$(RC_PREMISE_OVERRIDE=1 pre "$NEWSRC")"
[ -s "$T/.ravenclaude/runs/premise/overrides.log" ] \
  && { echo "  OK   override left a trace"; pass=$((pass+1)); } \
  || { echo "  FAIL override was SILENT"; fail=$((fail+1)); }
chk "RC_PREMISE_CONTROL resolves the subject"  0 "$(RC_PREMISE_CONTROL=www.ravenpower.net pre "$NEWSRC")"

echo "-- 6. T-PROSE: a diagnosis written down as established fact --"
# A FRESH project with an EMPTY probe ledger. That is deliberate and load-bearing:
# T-SHAPE has nothing to fire on here, so every deny below is T-PROSE ALONE. This
# is what proves the two triggers are OR-ed and not AND-ed — the contingency
# defect the design exists to avoid.
P=$(mktemp -d)
mkdir -p "$P/plugins/ravenclaude-core/hooks" "$P/docs" "$P/scratch" "$P/.ravenclaude/runs/x" "$P/src"
cp "$H/log-probe.sh" "$P/plugins/ravenclaude-core/hooks/"   # recorder installed, never ran
export CLAUDE_PROJECT_DIR="$P"

# Content-bearing Write payloads. `printf %s` does NOT expand escapes in its
# ARGUMENTS, so the \n below survive into the JSON string as real JSON escapes.
mkw(){ printf '{"session_id":"prose","tool_name":"Write","tool_input":{"file_path":"%s","content":"%s"}}' "$1" "$2"; }

# The verbatim Incident-1 header. ⛔ The certainty stamp is the TRIGGER, not an
# exemption: the author was CONFIDENT, with a real tool call behind them.
INC='/* the decoder is broken - measured 2026-08-07 */'
DIAG='The decoder is broken.\nEvery visitor sees a mangled address.\nmeasured 2026-08-07'

chk "empty ledger + plain content -> T-SHAPE silent" 0 "$(pre "$(mkw "$P/src/Email.astro" '// TODO: wire this up')")"
chk "verbatim incident header DENIED on an EMPTY ledger (OR, not AND)" \
                                                    2 "$(pre "$(mkw "$P/src/Email.astro" "$INC")")"
chk "durable docs/: diagnosis + stamp + no control -> DENIED" \
                                                    2 "$(pre "$(mkw "$P/docs/finding.md" "$DIAG")")"
chk "same content WITH a control-probe citation -> allowed" \
     0 "$(pre "$(mkw "$P/docs/finding.md" "$DIAG\ncontrol: GET /cdn-cgi/trace -> 200 (edge healthy)")")"
chk "same content under .ravenclaude/runs/ -> allowed" \
                                                    0 "$(pre "$(mkw "$P/.ravenclaude/runs/x/notes.md" "$DIAG")")"
chk "same content under a scratch/ path -> allowed"  0 "$(pre "$(mkw "$P/scratch/notes.md" "$DIAG")")"
chk "diagnosis with NO certainty stamp -> allowed"   0 "$(pre "$(mkw "$P/docs/finding.md" 'The decoder is broken.\nEvery visitor sees a mangled address.')")"
# An escape hatch nobody tested is one everybody uses.
chk "premise-ok: with nothing after it -> DENIED"    2 "$(pre "$(mkw "$P/docs/finding.md" "$DIAG\npremise-ok:")")"
chk "premise-ok: <named control> -> allowed"         0 "$(pre "$(mkw "$P/docs/finding.md" "$DIAG\npremise-ok: browser render check, run 2026-08-08")")"

# (5) A CONDITIONAL CLAUSE IS NOT AN ASSERTION. These three differ ONLY in what
# precedes the identical <subject>+<predicate> span, which is the whole discriminator.
# The first is the boilerplate section header carried by ALL 35 best-practice files —
# it tripped the gate on the file's OWN structure, which no author chose.
COND='## Edge cases / when the rule does NOT apply\n\nSome body text.\nmeasured 2026-08-12'
ASSERT='The rule does not apply.\nmeasured 2026-08-12'
PREAMBLE='When we checked, the decoder is broken.\nmeasured 2026-08-12'
chk "conditional clause (the boilerplate BP heading) -> allowed" \
                                                     0 "$(pre "$(mkw "$P/docs/finding.md" "$COND")")"
chk "same subject+predicate as a bare ASSERTION -> still DENIED" \
                                                     2 "$(pre "$(mkw "$P/docs/finding.md" "$ASSERT")")"
chk "temporal preamble is not a conditional -> still DENIED" \
                                                     2 "$(pre "$(mkw "$P/docs/finding.md" "$PREAMBLE")")"

echo "-- 7. A project root that LIVES UNDER /tmp (the Linux mktemp shape) --"
# ⛔ REGRESSION GUARD, and it is platform-independent ON PURPOSE. macOS `mktemp -d`
# yields /var/folders/...; Linux yields /tmp/tmp.XXXX. The scratch exemption was once
# a bare `"/tmp/" in path`, so on Linux the PROJECT ROOT ITSELF matched it and every
# deny assertion above passed VACUOUSLY — 18/18 green on macOS, and green for the
# wrong reason in CI. Every case above uses mktemp, so on macOS none of them can
# reach this path. This one pins the root under /tmp explicitly, so the guard is
# exercised on BOTH platforms.
L="/tmp/pg-linuxshape-$$"
mkdir -p "$L/src" "$L/plugins/ravenclaude-core/hooks"
cp "$H/log-probe.sh" "$L/plugins/ravenclaude-core/hooks/"
export CLAUDE_PROJECT_DIR="$L"
post '{"session_id":"linuxshape","tool_name":"Bash","tool_input":{"command":"fetch https://x.test/a"},"tool_response":{"stdout":"404","stderr":""}}'
chk "project root under /tmp: new module after a 404 still DENIED" \
    2 "$(pre '{"session_id":"linuxshape","tool_name":"Write","tool_input":{"file_path":"'"$L"'/src/New.astro"}}')"
# The exemption must still work for a genuine scratch write OUTSIDE the project.
chk "out-of-project /tmp write is still exempt" \
    0 "$(pre '{"session_id":"linuxshape","tool_name":"Write","tool_input":{"file_path":"/tmp/pg-elsewhere-'"$$"'/x.astro"}}')"
rm -rf "$L"

echo "-- 8. hooks-3: DISPLAYED content is not a probe --"
# A reader/search tool prints FILE CONTENT. A file that merely says "does not
# exist" or "not found" is not a failed probe, and an ordinary read must not
# make the gate deny a new module. Real negatives must still record, including
# when the command merges stderr into stdout (the dangerous false-CLEAR side).
D=$(mktemp -d)
mkdir -p "$D/src" "$D/plugins/ravenclaude-core/hooks"
cp "$H/log-probe.sh" "$D/plugins/ravenclaude-core/hooks/"
export CLAUDE_PROJECT_DIR="$D"
# last ledger verdict for session $1 (the recorder writes one row per call)
verdict(){ cat "$D"/.ravenclaude/runs/premise/"$1"/scopes/*/probe-ledger.jsonl 2>/dev/null \
  | tail -1 | python3 -c 'import json,sys; print(json.loads(sys.stdin.read() or "{}").get("verdict","none"))'; }
vchk(){ if [ "$2" = "$3" ]; then echo "  OK   $1"; pass=$((pass+1));
        else echo "  FAIL $1 (expected verdict $2, got $3)"; fail=$((fail+1)); fi; }
bash_call(){ printf '{"session_id":"%s","tool_name":"Bash","tool_input":{"command":"%s"},"tool_response":{"stdout":"%s","stderr":"%s"}}' "$1" "$2" "$3" "$4"; }
new_mod(){ printf '{"session_id":"%s","tool_name":"Write","tool_input":{"file_path":"%s/src/New%s.py"}}' "$1" "$D" "$1"; }
CONTENT='def load(p):\n    # raise if the file does not exist\n    raise FileNotFoundError(\"not found\")'

post "$(bash_call d1 'cat src/loader.py' "$CONTENT" '')"
vchk "cat of a file whose CONTENT says does-not-exist records positive" positive "$(verdict d1)"
chk  "a new module after that benign cat is ALLOWED" 0 "$(pre "$(new_mod d1)")"

post "$(bash_call d2 'sed -n 1,40p src/loader.py' "$CONTENT" '')"
vchk "sed -n of the same content records positive" positive "$(verdict d2)"

post "$(bash_call d3 'grep -rn not\\ found docs/' 'docs/a.md:3: the key was not found' '')"
vchk "a grep FOR the phrase, with matches, records positive" positive "$(verdict d3)"

post "$(bash_call d4 'cd /repo && sed -n 1,20p x.py' "$CONTENT" '')"
vchk "cd <dir> && sed -n (wrapped display) records positive" positive "$(verdict d4)"

post "$(bash_call d5 'ls /nonexistent' '' 'ls: cannot access /nonexistent: No such file or directory')"
vchk "ls /nonexistent (stderr) still records negative" negative "$(verdict d5)"
chk  "and still DENIES a new module" 2 "$(pre "$(new_mod d5)")"

post "$(bash_call d6 'cat /missing.txt 2>&1' 'cat: /missing.txt: No such file or directory' '')"
vchk "cat of a missing file with 2>&1 (merged, stderr empty) records negative" negative "$(verdict d6)"
chk  "and still DENIES a new module" 2 "$(pre "$(new_mod d6)")"

post "$(bash_call d7 'cat a.py missing.py' "$CONTENT" 'cat: missing.py: No such file or directory')"
vchk "display with a real error on stderr records negative" negative "$(verdict d7)"

post "$(bash_call d8 'curl -s https://x.test/missing' '404 Not Found' '')"
vchk "a fetch-tool 404 body still records negative" negative "$(verdict d8)"

post "$(bash_call d9 'grep -rn https://api.x.test docs/' 'docs/a.md:9: returns 404 when absent' '')"
vchk "a grep whose PATTERN is a URL is not an HTTP probe (no 404 negative)" positive "$(verdict d9)"

post "$(bash_call d10 'grep -rn zzz docs/' '' '')"
vchk "an EMPTY grep is still a negative (empty-search arm kept)" negative "$(verdict d10)"

# Teeth: with the display classification neutered, the benign cat goes negative.
MUT="$D/mut-log-probe.sh"
sed 's/^display = first_word(cmd) in _DISPLAY_TOOLS and bool(stdout_s.strip())$/display = False/' \
  "$H/log-probe.sh" > "$MUT"
if grep -q '^display = False$' "$MUT"; then
  bash "$MUT" <<<"$(bash_call d11 'cat src/loader.py' "$CONTENT" '')"
  vchk "[teeth] display neutered -> the benign cat records negative" negative "$(verdict d11)"
else
  echo "  FAIL [teeth] could not build the display-neutered mutant"; fail=$((fail+1))
fi
rm -rf "$D"

echo
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
