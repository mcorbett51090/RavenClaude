#!/usr/bin/env bash
# Gate 186 — the premise ledger's BLAST RADIUS, and the escape a subagent can reach.
#
# ── WHAT WENT WRONG ─────────────────────────────────────────────────────────
# The ledger was keyed on (project, session_id). Neither component varies per
# agent, so a parallel run collapsed every sibling agent onto ONE ledger.
#
# control: enumerated ~/.claude/projects/<proj>/<session>.jsonl for a real
#          6-agent run -> 14,322 events under ONE session_id spanning 49 distinct
#          `cwd` values and 15+ git worktrees, and the matching ledger held 2,825
#          entries with 50 unresolved negative families. The same probe on a
#          single-agent session returned 3 cwd values and 12 entries, so it was
#          capable of returning "they do not collide" and did not.
#
# Consequence: a negative recorded by the agent in worktree A denied an unrelated
# new module in worktree B. Three agents hit it. One lost finished work rather
# than tunnel; one routed around the hook by writing through Bash heredocs.
#
# ── THE TWO HALVES, AND WHY BOTH ────────────────────────────────────────────
# Sections 2 and 3 are a matched pair and neither is meaningful alone:
#   2  a negative in A must NOT block an unrelated write in B  (the fix)
#   3  a negative in A must STILL block the unjustified write in A, and a
#      negative in B must block in B  (proof the fix is not a weakening)
# Delete section 3 and "scoping" is indistinguishable from switching the gate off.
#
# ── THE ESCAPE ──────────────────────────────────────────────────────────────
# RC_PREMISE_CONTROL / RC_PREMISE_OVERRIDE are ENVIRONMENT variables, and a
# variable exported inside a Bash tool call never reaches this hook process — so a
# subagent that genuinely ran the control had no sanctioned exit. Sections 5-7
# pin the file-based control: it clears, it is RECORDED, an incomplete file
# clears NOTHING, and a control written in A does not clear B.
#
# Real git worktrees are used, not simulated ones: the detector keys on a linked
# worktree carrying its own `.git` FILE, and a hand-made stand-in would test the
# stand-in. The project root deliberately sits ABOVE the git repo so that writes
# under `<repo>/.claude/worktrees/**` are not swallowed by the hook`s own
# project-relative `.claude/` prefix exemption — which would make every assertion
# below pass vacuously.
set -uo pipefail
H="$(cd "$(dirname "$0")/.." && pwd)"

command -v git >/dev/null 2>&1 || { echo "  SKIP git absent — cannot build worktrees"; exit 0; }

P=$(mktemp -d)                       # CLAUDE_PROJECT_DIR — deliberately NOT the git root
R="$P/repo"                          # the primary checkout
mkdir -p "$P/plugins/ravenclaude-core/hooks" "$R"
cp "$H/log-probe.sh" "$P/plugins/ravenclaude-core/hooks/"   # recorder "installed"
export CLAUDE_PROJECT_DIR="$P"

(
  cd "$R" || exit 1
  git init -q .
  git config user.email t@t.test; git config user.name t
  git config commit.gpgsign false
  mkdir -p src; echo seed > src/seed.txt
  git add -A; git commit -qm seed
  git worktree add -q -b wt-a .claude/worktrees/A
  git worktree add -q -b wt-b .claude/worktrees/B
) || { echo "  SKIP could not build git worktrees"; exit 0; }

A="$R/.claude/worktrees/A"
B="$R/.claude/worktrees/B"
[ -e "$A/.git" ] && [ -e "$B/.git" ] || { echo "  FAIL worktrees not created"; exit 1; }
mkdir -p "$A/src" "$B/src"

pass=0; fail=0
chk(){ if [ "$2" = "$3" ]; then echo "  OK   $1"; pass=$((pass+1));
       else echo "  FAIL $1 (expected exit $2, got $3)"; fail=$((fail+1)); fi; }
ok(){ if [ "$2" = "yes" ]; then echo "  OK   $1"; pass=$((pass+1));
      else echo "  FAIL $1"; fail=$((fail+1)); fi; }

# `cwd` is the per-agent field; the recorder scopes on it, the gate agrees.
probe(){ # $1 cwd  $2 url  $3 stdout
  bash "$H/log-probe.sh" <<<"{\"session_id\":\"shared\",\"cwd\":\"$1\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"fetch $2\"},\"tool_response\":{\"stdout\":\"$3\",\"stderr\":\"\"}}"
}
write(){ # $1 cwd  $2 abs path            -> exit code
  bash "$H/guard-premise.sh" <<<"{\"session_id\":\"shared\",\"cwd\":\"$1\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$2\"}}" >/dev/null 2>&1
  echo $?
}
ctrlpath(){ # the control.md path the DENY prints — parsed, never recomputed, so
            # this also proves the gate hands the agent a usable path.
  bash "$H/guard-premise.sh" <<<"{\"session_id\":\"shared\",\"cwd\":\"$1\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$2\"}}" 2>&1 >/dev/null \
    | grep -oE "[^[:space:]]*/control\.md" | head -1
}
mkctrl(){ mkdir -p "$(dirname "$1")"; printf '%s\n' "$2" > "$1"; }

echo "-- 1. A records a negative (its own worktree) --"
probe "$A" "https://x.test/gone" "404" >/dev/null 2>&1
ok "A ledger written under its own scope" \
   "$([ "$(find "$P/.ravenclaude/runs/premise/shared/scopes" -name probe-ledger.jsonl 2>/dev/null | wc -l | tr -d ' ')" = "1" ] && echo yes || echo no)"

echo "-- 2. THE FIX: A's unresolved negative must not reach B --"
chk "unrelated new module in worktree B is ALLOWED" 0 "$(write "$B" "$B/src/Unrelated.ts")"
probe "$B" "https://y.test/live" "200" >/dev/null 2>&1
chk "B with its own CLEAN ledger is still ALLOWED"  0 "$(write "$B" "$B/src/Unrelated2.ts")"

echo "-- 3. NOT A WEAKENING: the unjustified write in A is still denied --"
# Each assertion below uses its OWN host, because a family that has ever returned
# a positive is resolved for the rest of the session — reusing y.test here would
# make the deny unreachable and the assertion vacuous.
chk "new module in worktree A is DENIED"            2 "$(write "$A" "$A/src/Built.ts")"
probe "$B" "https://z.test/gone" "404" >/dev/null 2>&1
chk "B is independently gated by ITS OWN negative"  2 "$(write "$B" "$B/src/Built.ts")"
probe "$B" "https://z.test/live" "200" >/dev/null 2>&1
chk "a control in B resolves B (recorder+gate agree on the key)" 0 "$(write "$B" "$B/src/Built.ts")"
chk "...and A is untouched by B's control"          2 "$(write "$A" "$A/src/Built.ts")"

echo "-- 4. The deny hands the agent a usable control path --"
probe "$B" "https://w.test/gone" "404" >/dev/null 2>&1   # kept unresolved for 7-8
CA="$(ctrlpath "$A" "$A/src/Built.ts")"
CB="$(ctrlpath "$B" "$B/src/Built.ts")"
ok "DENY prints a control.md path"                  "$([ -n "$CA" ] && echo yes || echo no)"
ok "A and B are handed DIFFERENT control paths"     "$([ -n "$CB" ] && [ "$CA" != "$CB" ] && echo yes || echo no)"

echo "-- 5. TEETH: an incomplete control file clears NOTHING --"
mkctrl "$CA" "premise-control: *
who: agent-a
subject: the widget is absent"
chk "missing control: -> still DENIED"              2 "$(write "$A" "$A/src/Built.ts")"
mkctrl "$CA" "premise-control: *
who: agent-a
subject: the widget is absent
control:"
chk "EMPTY control: value -> still DENIED"          2 "$(write "$A" "$A/src/Built.ts")"
mkctrl "$CA" "who: agent-a
subject: the widget is absent
control: fetch /live -> 200"
chk "no premise-control: line -> still DENIED"      2 "$(write "$A" "$A/src/Built.ts")"

echo "-- 6. The complete file clears, and the escape is RECORDED --"
mkctrl "$CA" "premise-control: *
who: agent-a (subagent, no env access)
subject: x.test/gone returns 404
control: fetch https://x.test/live -> 200, same host answered"
chk "complete control file -> ALLOWED"              0 "$(write "$A" "$A/src/Built.ts")"
L="$P/.ravenclaude/runs/premise/overrides.log"
ok "overrides.log records who/subject/control" \
   "$(grep -q 'file-control' "$L" 2>/dev/null && grep -q 'who=agent-a' "$L" 2>/dev/null \
      && grep -q 'subject=x.test/gone' "$L" 2>/dev/null && grep -q 'control=fetch' "$L" 2>/dev/null \
      && echo yes || echo no)"
ok "the record is deduped, not one line per write" \
   "$([ "$(write "$A" "$A/src/Built3.ts")" = "0" ] && [ "$(grep -c 'file-control' "$L")" = "1" ] && echo yes || echo no)"

echo "-- 7. The escape is scoped too: A's control must not clear B --"
chk "B still DENIED while only A carries a control" 2 "$(write "$B" "$B/src/Built9.ts")"

echo "-- 8. A subject-scoped control clears only its own subject --"
mkctrl "$CB" "premise-control: nosuchhost.invalid
who: agent-b
subject: an unrelated claim
control: fetch https://nosuchhost.invalid/live -> 200"
chk "non-matching subject -> still DENIED"          2 "$(write "$B" "$B/src/Built9.ts")"
mkctrl "$CB" "premise-control: w.test
who: agent-b
subject: w.test/gone returns 404
control: fetch https://w.test/live -> 200"
chk "matching subject -> ALLOWED"                   0 "$(write "$B" "$B/src/Built9.ts")"

echo "-- 9. BLIND: only a BLANKET control is the recorded override --"
N=$(mktemp -d); mkdir -p "$N/repo/src"              # recorder NOT installed
export CLAUDE_PROJECT_DIR="$N"
NB="{\"session_id\":\"blind\",\"cwd\":\"$N/repo\",\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$N/repo/src/New.ts\"}}"
bexit(){ bash "$H/guard-premise.sh" <<<"$NB" >/dev/null 2>&1; echo $?; }
chk "recorder absent -> DENIED (blind, not clean)"  2 "$(bexit)"
CN="$(bash "$H/guard-premise.sh" <<<"$NB" 2>&1 >/dev/null | grep -oE "[^[:space:]]*/control\.md" | head -1)"
mkctrl "$CN" "premise-control: some.host
who: agent-n
subject: a narrow claim
control: fetch https://some.host/live -> 200"
chk "a SUBJECT-scoped file does not clear blindness" 2 "$(bexit)"
mkctrl "$CN" "premise-control: *
who: agent-n
subject: recorder is unwired in this environment
control: verified log-probe.sh absent AND present elsewhere in the same session"
chk "a BLANKET file clears blindness"               0 "$(bexit)"
ok "blind clearance is recorded" \
   "$(grep -q 'clears=blind' "$N/.ravenclaude/runs/premise/overrides.log" 2>/dev/null && echo yes || echo no)"

git -C "$R" worktree remove --force .claude/worktrees/A >/dev/null 2>&1
git -C "$R" worktree remove --force .claude/worktrees/B >/dev/null 2>&1
rm -rf "$P" "$N"

echo
echo "  $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
