#!/usr/bin/env bash
# test-worktree-clean-lifecycle.sh — Gate 308 fixture.
#
# Proves the unified worktree + branch lifecycle (scripts/worktree-clean.sh +
# scripts/worktree-cleanup-report.sh) against REAL scratch git repos — never
# this box's own /workspace worktrees (the task's own HARD STOP). Every fixture
# repo lives under a fresh `mktemp -d`.
#
#   P1  fresh repo (only the main worktree) -> --status reports SELF only,
#       nothing actionable; the SessionEnd report hook writes NOTHING
#   P2  clean worktree -> state "clean"; --no-network note present
#   P3  dirty worktree -> state DIRTY; refused without --force; --force removes
#       it AND retires its branch (unified lifecycle: remove -> prune ->
#       cleanup-branches.sh), via <slug> addressing under .claude/worktrees/
#   P4  ignored-only worktree (an untracked .env, with .gitignore committed on
#       the branch POINT so the worktree's own HEAD sees it) -> state IGNORED;
#       refused without --force
#   P5  detached-unreachable worktree -> state DETACHED-unreachable; rescue
#       command printed; refused without --force
#   P6  UNKNOWN worktree (corrupted .git pointer) -> state UNKNOWN-rc; refused
#       EVEN WITH --force
#   P7  stale worktree (commit backdated past the threshold) -> state STALE;
#       refused without --force (flag only, per the brief)
#   P8  open-PR worktree (a stub `gh` on PATH reports 2 open PRs for its
#       branch) -> state OPEN-PR; refused EVEN WITH --force
#   P9  locked worktree -> state LOCKED; refused EVEN WITH --force; unlocking
#       then makes it removable
#   P10 prunable worktree (directory deleted out-of-band, admin metadata
#       intact) -> state PRUNABLE; dispatch runs `git worktree prune`, never
#       `git worktree remove`
#   P11 porcelain discovery of a SIBLING ad-hoc worktree OUTSIDE
#       .claude/worktrees/ -> appears in --status; removable via --target
#       (anchored to porcelain membership, not WT_ROOT); NOT addressable via
#       <slug> (it was never under .claude/worktrees/)
#   P12 dry-run default: `--all` with NO --execute changes NOTHING on disk,
#       even though it prints what it WOULD do
#   P13 `--all --execute`: removes ONLY "clean" entries; dirty/ignored/
#       detached/unknown/stale/open-pr/locked all survive untouched
#   P14 the shipped PLUGIN script resolves cleanup-branches.sh correctly when
#       copied to an installed-user layout (sibling scripts/, no repo-root
#       context at all) — not just when run from this marketplace checkout
#   P15 the SessionEnd report hook: with worktrees beyond the main one, it
#       WRITES .ravenclaude/runs/worktree-cleanup/report.md and mutates
#       NOTHING (no worktree removed, no branch deleted); RC_WORKTREE_CLEANUP_REPORT=off
#       silences it
#   P16 root shim resolves to the plugin script and behaves identically
#   P17 AppSec F3: --all --execute SKIPS a 'clean' worktree another LIVE
#       session has registered via worktree-guard.sh's own SessionStart
#       registry (BUSY); a control proves the same shape with NO
#       registration planted IS removed normally
#   P18 AppSec F1: open-PR status UNKNOWN (--no-network, or gh absent from
#       PATH) classifies PR-UNKNOWN, never clean -- refuses single-target
#       removal EVEN WITH --force and is SKIPPED under --all --execute; a
#       control proves a KNOWN-clean worktree (gh confirms 0 open PRs) is
#       still removable normally
#   P19 AppSec F2: the SessionEnd report hook refuses a symlink anywhere on
#       its write path -- report.md itself, its parent worktree-cleanup/
#       dir, or .ravenclaude itself -- and leaves a victim file/dir outside
#       the repo untouched in every case; a control proves a legitimate
#       (non-symlinked) tree still gets a real report written
#
#   T1  teeth: remove the DIRTY --force gate -> a dirty worktree is removed
#       WITHOUT --force, proving P3's refusal was real
#   T2  teeth: remove the --execute gate in cmd_all -> `--all` with no
#       --execute now mutates, proving P12's dry-run-by-default has teeth
#   T3  teeth: remove the OPEN-PR refusal -> an open-PR worktree is removed,
#       proving P8's "never, even with --force" was real
#   T4  teeth (F3): remove the BUSY check in execute_all()'s 'clean' branch
#       -> a planted-busy worktree IS removed, proving P17's skip was real
#   T5  teeth (F1): remove the PR-UNKNOWN refusal in dispatch_removal() ->
#       an unknown-PR-status worktree IS removed, proving P18 was real
#   T6  teeth (F2): reproduce the ORIGINAL pre-fix write shape (bare
#       mkdir -p + a single `>` redirection) against the same planted
#       symlink as P19a -> the victim IS clobbered, proving the
#       vulnerability class F2 closes was real
#
# Run directly: bash plugins/ravenclaude-core/hooks/tests/test-worktree-clean-lifecycle.sh
# Run via gate:  bash scripts/audit-gates.sh --check 308
#
# Portability: bash (not sh) is required — matches worktree-clean.sh itself.

set -uo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]:-$0}")" rev-parse --show-toplevel 2>/dev/null)"
[ -n "$REPO_ROOT" ] || REPO_ROOT="$(pwd)"
WTC="$REPO_ROOT/plugins/ravenclaude-core/scripts/worktree-clean.sh"
REPORT_HOOK="$REPO_ROOT/plugins/ravenclaude-core/scripts/worktree-cleanup-report.sh"
CLEANUP_BRANCHES="$REPO_ROOT/plugins/ravenclaude-core/scripts/cleanup-branches.sh"

PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

[ -f "$WTC" ] || { fail "P0 $WTC missing"; echo "worktree-clean-lifecycle: $PASS passed, $FAIL failed"; exit 1; }
[ -f "$REPORT_HOOK" ] || { fail "P0 $REPORT_HOOK missing"; echo "worktree-clean-lifecycle: $PASS passed, $FAIL failed"; exit 1; }
[ -f "$CLEANUP_BRANCHES" ] || { fail "P0 $CLEANUP_BRANCHES missing"; echo "worktree-clean-lifecycle: $PASS passed, $FAIL failed"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git required"; exit 1; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t wtc)"
trap 'rm -rf "$TMP"' EXIT

# ── fixture builder ──────────────────────────────────────────────────────────
# One shared repo with every non-mutating fixture state, so classification can
# be proven once via --status, plus the mutating ones re-built per-test so a
# removal in one test never contaminates another.
REPO="$TMP/repo"
mkdir -p "$REPO"
(
  cd "$REPO" || exit 1
  git init -q .
  git config user.email t@t.local
  git config user.name tester
  echo hi > f.txt
  git add f.txt
  git commit -q -m "init"
  git branch -M main
) >/dev/null 2>&1

wt_add() { # $1=name $2=branch -> worktree at $TMP/$1 off main
  git -C "$REPO" worktree add -q -b "$2" "$TMP/$1" main >/dev/null 2>&1
}

# P2: clean
wt_add wt-clean wt-clean

# P4: ignored-only. The .gitignore must be committed BEFORE branching this
# worktree off — otherwise the worktree's own HEAD predates .gitignore and the
# untracked .env reads as a plain untracked (DIRTY) file, not an ignored one.
(
  cd "$REPO" || exit 1
  echo ".env" > .gitignore
  git add .gitignore
  git commit -q -m "gitignore"
) >/dev/null 2>&1
wt_add wt-ignored wt-ignored
echo "secret" > "$TMP/wt-ignored/.env"

# P3: dirty
wt_add wt-dirty wt-dirty
echo "uncommitted" >> "$TMP/wt-dirty/f.txt"

# P5: detached, unreachable. Branch, commit, detach a NEW worktree at that
# sha, then delete the branch (not checked out anywhere) so the commit is
# reachable from no ref.
(
  cd "$REPO" || exit 1
  git branch temp-detach main >/dev/null 2>&1
  git -C "$REPO" worktree add -q -b temp-detach-src "$TMP/temp-detach-src" temp-detach >/dev/null 2>&1
  (cd "$TMP/temp-detach-src" && echo x >> f.txt && git add f.txt && git commit -q -m "orphan")
  ORPHAN_SHA="$(git -C "$TMP/temp-detach-src" rev-parse HEAD)"
  git -C "$REPO" worktree remove --force "$TMP/temp-detach-src" >/dev/null 2>&1
  git -C "$REPO" branch -D temp-detach-src >/dev/null 2>&1
  git -C "$REPO" branch -D temp-detach >/dev/null 2>&1
  git -C "$REPO" worktree add -q --detach "$TMP/wt-detached" "$ORPHAN_SHA" >/dev/null 2>&1
) >/dev/null 2>&1

# P6: UNKNOWN (corrupted .git pointer file)
wt_add wt-unknown wt-unknown
printf 'gitdir: /nonexistent/path/that/does/not/exist\n' > "$TMP/wt-unknown/.git"

# P7: stale (backdated commit)
wt_add wt-stale wt-stale
(
  cd "$TMP/wt-stale" || exit 1
  OLD="$(date -u -d '40 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-40d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)"
  if [ -n "$OLD" ]; then
    echo "stale-commit" >> f.txt
    GIT_AUTHOR_DATE="$OLD" GIT_COMMITTER_DATE="$OLD" git commit -q -am "old"
  fi
) >/dev/null 2>&1

# P8: open-PR (stub `gh` on PATH; branch name is distinctive so the stub can
# match it unambiguously)
wt_add wt-openpr wt-has-open-pr
mkdir -p "$TMP/bin"
cat > "$TMP/bin/gh" <<'STUBGH'
#!/usr/bin/env bash
case "$*" in
  *"wt-has-open-pr"*) echo "2" ;;
  *) echo "0" ;;
esac
STUBGH
chmod +x "$TMP/bin/gh"

# P9: locked
wt_add wt-locked wt-locked
git -C "$REPO" worktree lock "$TMP/wt-locked" --reason "testing" >/dev/null 2>&1

# P10: prunable (directory removed out-of-band)
wt_add wt-prunable wt-prunable
rm -rf "$TMP/wt-prunable"

# P11: sibling ad-hoc worktree, deliberately OUTSIDE .claude/worktrees/ — all
# of the above already are (this fixture never uses .claude/worktrees/ at
# all), but name one explicitly for the --target tests.
SIBLING="$TMP/ad-hoc-sibling"
wt_add ad-hoc-sibling ad-hoc-sibling-branch

run_status() { # [extra env] -> stdout of --status
  # ⛔ The `cd` here is load-bearing, not cosmetic: worktree-clean.sh resolves
  # its own REPO_ROOT via `git rev-parse --show-toplevel` from the CALLER's
  # cwd. Forgetting this `cd` once during development made the very first
  # run of this file enumerate THIS SESSION'S OWN real worktree instead of
  # the fixture — read-only (--status --no-network), so nothing was mutated
  # and nothing was printed (a separate slicing bug happened to blank the
  # debug output), but it is exactly the HARD STOP this file exists to
  # respect. Every invocation of $WTC in this file must be wrapped in a
  # subshell `(cd "$SOME_FIXTURE_REPO" && ...)` — never run bare.
  #
  # Deliberately NOT --no-network here: the stub `gh` on $TMP/bin answers "2"
  # for the open-PR branch and "0" for everything else, so leaving the real
  # (stubbed) network path active is what lets P8's OPEN-PR classification
  # exercise for real, while every other fixture's "0" answer leaves its own
  # classification (age-driven for STALE, status-driven for DIRTY/IGNORED/
  # etc.) unaffected either way.
  (cd "$REPO" && env "$@" bash "$WTC" --status) 2>&1
}

# ── P1 is tested against a SEPARATE, solo repo (no linked worktrees at all) ──
SOLO="$TMP/solo"
mkdir -p "$SOLO"
(cd "$SOLO" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init) >/dev/null 2>&1
out_solo="$(cd "$SOLO" && bash "$WTC" --status --no-network 2>&1)"
case "$out_solo" in *"state: SELF"*) pass "P1a solo repo: --status reports the main/self worktree" ;; *) fail "P1a solo repo status missing SELF ($out_solo)" ;; esac
case "$out_solo" in *"state: clean"*|*"state: DIRTY"*|*"state: STALE"*) fail "P1b solo repo reported an entry beyond the main worktree" ;; *) pass "P1b solo repo: nothing beyond the main worktree" ;; esac
out_hook_solo="$(cd "$SOLO" && CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" 2>&1)"
rc_hook_solo=$?
[ -f "$SOLO/.ravenclaude/runs/worktree-cleanup/report.md" ] && fail "P1c SessionEnd hook wrote a report for a solo repo (nothing to report)" || pass "P1c SessionEnd hook wrote nothing for a solo repo"
[ "$rc_hook_solo" -eq 0 ] && [ -z "$out_hook_solo" ] && pass "P1d SessionEnd hook exits 0, silent stdout" || fail "P1d SessionEnd hook rc=$rc_hook_solo out=${out_hook_solo:0:80}"

# ── P2..P11: classification, via one shared --status over the multi-fixture repo ─
STATUS_OUT="$(run_status PATH="$TMP/bin:$PATH")"

check_state() { # label path expected_token
  case "$STATUS_OUT" in
    *"$1"*"state: $2"*) pass "$3 '$1' classified $2" ;;
    *) fail "$3 '$1' NOT classified $2 (status head: $(printf '%s' "$STATUS_OUT" | head -c 200))" ;;
  esac
}
check_state "$TMP/wt-clean" "clean" "P2"
check_state "$TMP/wt-dirty" "DIRTY" "P3a"
check_state "$TMP/wt-ignored" "IGNORED" "P4"
check_state "$TMP/wt-detached" "DETACHED-unreachable" "P5"
check_state "$TMP/wt-unknown" "UNKNOWN" "P6"
check_state "$TMP/wt-stale" "STALE" "P7"
check_state "$TMP/wt-openpr" "OPEN-PR" "P8"
check_state "$TMP/wt-locked" "LOCKED" "P9"
check_state "$TMP/wt-prunable" "PRUNABLE" "P10"
check_state "$SIBLING" "clean" "P11a"

case "$STATUS_OUT" in *"rescue: git"*) pass "P5b detached-unreachable prints a rescue command" ;; *) fail "P5b no rescue command printed"; esac

# ── P10b: PRUNABLE is pruned, never passed to `git worktree remove` ─────────
# ⛔ MUST run before ANY other removal in this $REPO: every real removal's
# unified lifecycle calls `git worktree prune` GLOBALLY (remove_and_cleanup),
# which would sweep wt-prunable away as a side effect of an unrelated
# removal, making a later "before vs after" comparison measure nothing.
before_admin="$(git -C "$REPO" worktree list --porcelain | grep -c '^worktree ')"
(cd "$REPO" && bash "$WTC" --target "$TMP/wt-prunable" >/dev/null 2>&1)
after_admin="$(git -C "$REPO" worktree list --porcelain | grep -c '^worktree ')"
[ "$after_admin" -lt "$before_admin" ] && pass "P10b prunable entry is gone from \`worktree list\` after prune" || fail "P10b prunable entry still listed"

# ── P12: dry run is the DEFAULT for --all — nothing on disk changes ─────────
before="$(git -C "$REPO" worktree list --porcelain | md5sum 2>/dev/null || git -C "$REPO" worktree list --porcelain | cksum)"
dryrun_out="$(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --all --no-network 2>&1)"
after="$(git -C "$REPO" worktree list --porcelain | md5sum 2>/dev/null || git -C "$REPO" worktree list --porcelain | cksum)"
[ "$before" = "$after" ] && pass "P12a \`--all\` with no --execute changes NOTHING on disk" || fail "P12a worktree list changed under dry-run --all"
case "$dryrun_out" in *"DRY RUN"*) pass "P12b dry-run output says DRY RUN" ;; *) fail "P12b dry-run output missing the DRY RUN label" ;; esac
[ -d "$TMP/wt-clean" ] && pass "P12c the clean worktree still exists after a dry-run --all" || fail "P12c the clean worktree vanished under dry-run --all"

# ── P11b: --target removes the sibling (porcelain-anchored, not WT_ROOT) ────
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$SIBLING" >/dev/null 2>&1)
[ ! -d "$SIBLING" ] && pass "P11b --target removed the sibling ad-hoc worktree" || fail "P11b sibling worktree still present after --target removal"
git -C "$REPO" show-ref --verify --quiet refs/heads/ad-hoc-sibling-branch \
  && fail "P11c sibling's branch survived (cleanup-branches.sh should have retired a trivially-ancestor branch)" \
  || pass "P11c sibling's branch was retired by cleanup-branches.sh as part of the unified lifecycle"
# <slug> addressing must NOT reach a path that was never under .claude/worktrees/
(cd "$REPO" && bash "$WTC" "ad-hoc-sibling" >/dev/null 2>&1) && fail "P11d a bare slug reached a non-WT_ROOT path" || pass "P11d a bare slug correctly refuses a path outside .claude/worktrees/"

# ── P9b: locked refuses even with --force; unlock then removes ─────────────
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-locked" --force >/dev/null 2>&1) \
  && fail "P9b LOCKED was removed with --force (should never be)" \
  || pass "P9b LOCKED refuses removal even with --force"
git -C "$REPO" worktree unlock "$TMP/wt-locked" >/dev/null 2>&1
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-locked" --force >/dev/null 2>&1)
[ ! -d "$TMP/wt-locked" ] && pass "P9c after unlocking, the worktree is removable" || fail "P9c worktree still present after unlock + --force"

# ── P8b: open-PR refuses even with --force ──────────────────────────────────
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-openpr" --force >/dev/null 2>&1) \
  && fail "P8b OPEN-PR was removed with --force (should never be)" \
  || pass "P8b OPEN-PR refuses removal even with --force"

# ── P6b: UNKNOWN refuses even with --force ──────────────────────────────────
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-unknown" --force >/dev/null 2>&1) \
  && fail "P6b UNKNOWN was removed with --force (should never be)" \
  || pass "P6b UNKNOWN refuses removal even with --force"
[ -d "$TMP/wt-unknown" ] && pass "P6c UNKNOWN worktree directory still present" || fail "P6c UNKNOWN worktree vanished"

# ── P3b/P4b/P7b: refused WITHOUT --force, removed WITH --force (DIRTY/IGNORED/STALE) ─
for pair in "wt-dirty DIRTY" "wt-ignored IGNORED" "wt-stale STALE"; do
  name="${pair%% *}"
  (cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/$name" >/dev/null 2>&1) \
    && fail "P3/4/7 '$name' removed WITHOUT --force" \
    || pass "P3/4/7 '$name' refuses without --force"
  (cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/$name" --force >/dev/null 2>&1)
  [ ! -d "$TMP/$name" ] && pass "P3/4/7 '$name' removed WITH --force" || fail "P3/4/7 '$name' still present after --force"
done

# ── P5c: detached-unreachable refuses without --force, removable with it ───
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-detached" >/dev/null 2>&1) \
  && fail "P5c detached-unreachable removed WITHOUT --force" \
  || pass "P5c detached-unreachable refuses without --force"
(cd "$REPO" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/wt-detached" --force >/dev/null 2>&1)
[ ! -d "$TMP/wt-detached" ] && pass "P5d detached-unreachable removed WITH --force" || fail "P5d still present after --force"

# ── P13: --all --execute removes only 'clean'; builds a FRESH tiny repo so the
#    "clean" branch is a trivial ancestor of main and cleanup-branches.sh can
#    retire it for real, proving the remove -> prune -> cleanup-branches order ──
REPO2="$TMP/repo2"
mkdir -p "$REPO2"
(cd "$REPO2" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO2" worktree add -q -b exec-clean "$TMP/exec-clean" main >/dev/null 2>&1
git -C "$REPO2" worktree add -q -b exec-dirty "$TMP/exec-dirty" main >/dev/null 2>&1
echo dirty >> "$TMP/exec-dirty/f.txt"
# ⛔ NOT --no-network: a known PR status (via the stub `gh` on PATH, which
# answers "0" for anything that isn't the open-PR branch) is what lets
# exec-clean classify "clean" rather than PR-UNKNOWN (F1) — this test is
# proving the unified remove->prune->cleanup-branches lifecycle, not F1's
# refusal, so it must not collide with the unrelated PR-UNKNOWN class.
exec_out="$(cd "$REPO2" && env PATH="$TMP/bin:$PATH" bash "$WTC" --all --execute 2>&1)"
[ ! -d "$TMP/exec-clean" ] && pass "P13a --all --execute removed the clean worktree" || fail "P13a clean worktree survived --execute"
[ -d "$TMP/exec-dirty" ] && pass "P13b --all --execute left the dirty worktree alone" || fail "P13b dirty worktree was removed by --execute"
git -C "$REPO2" show-ref --verify --quiet refs/heads/exec-clean \
  && fail "P13c exec-clean's branch survived (should have been retired — remove -> prune -> cleanup-branches)" \
  || pass "P13c exec-clean's branch was retired (unified lifecycle: remove -> prune -> cleanup-branches.sh)"
case "$exec_out" in *"removed:"*) pass "P13d --execute output reports the removal" ;; *) fail "P13d no removal reported in --execute output" ;; esac

# ── P14: plugin-shipped script path resolves cleanup-branches.sh correctly
#    when copied to an INSTALLED-USER layout (no repo-root context at all) ──
INSTALLED="$TMP/installed-scripts"
mkdir -p "$INSTALLED"
cp "$WTC" "$INSTALLED/worktree-clean.sh"
cp "$CLEANUP_BRANCHES" "$INSTALLED/cleanup-branches.sh"
REPO3="$TMP/repo3"
mkdir -p "$REPO3"
(cd "$REPO3" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO3" worktree add -q -b installed-clean "$TMP/installed-clean" main >/dev/null 2>&1
# ⛔ NOT --no-network: a known PR status (via the stub `gh` on PATH) is what
# lets installed-clean classify "clean" rather than PR-UNKNOWN (F1) — this
# test is proving the installed-layout path resolution, not F1's refusal.
(cd "$REPO3" && env PATH="$TMP/bin:$PATH" bash "$INSTALLED/worktree-clean.sh" --target "$TMP/installed-clean" >/dev/null 2>&1)
[ ! -d "$TMP/installed-clean" ] && pass "P14a installed-layout copy removes the worktree" || fail "P14a installed-layout copy failed to remove"
git -C "$REPO3" show-ref --verify --quiet refs/heads/installed-clean \
  && fail "P14b installed-layout copy did not retire the branch (cleanup-branches.sh sibling resolution failed)" \
  || pass "P14b installed-layout copy correctly resolved + ran the sibling cleanup-branches.sh"

# ── P15: the SessionEnd report hook writes a report and mutates nothing ────
REPO4="$TMP/repo4"
mkdir -p "$REPO4"
(cd "$REPO4" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO4" worktree add -q -b hook-wt "$TMP/hook-wt" main >/dev/null 2>&1
before_hook="$(git -C "$REPO4" worktree list --porcelain | cksum)"
(cd "$REPO4" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" >/dev/null 2>&1)
after_hook="$(git -C "$REPO4" worktree list --porcelain | cksum)"
[ "$before_hook" = "$after_hook" ] && pass "P15a SessionEnd hook changed nothing in git worktree state" || fail "P15a git worktree state changed after the hook ran"
[ -d "$TMP/hook-wt" ] && pass "P15b SessionEnd hook did not remove the worktree" || fail "P15b worktree vanished after the hook ran"
[ -f "$REPO4/.ravenclaude/runs/worktree-cleanup/report.md" ] && pass "P15c SessionEnd hook wrote the dry-run report" || fail "P15c no report file written"
if [ -f "$REPO4/.ravenclaude/runs/worktree-cleanup/report.md" ]; then
  grep -q "DRY RUN ONLY" "$REPO4/.ravenclaude/runs/worktree-cleanup/report.md" \
    && pass "P15d the written report states it is dry-run only" \
    || fail "P15d the written report does not say dry-run only"
fi
rm -f "$REPO4/.ravenclaude/runs/worktree-cleanup/report.md"
(cd "$REPO4" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" RC_WORKTREE_CLEANUP_REPORT=off bash "$REPORT_HOOK" >/dev/null 2>&1)
[ -f "$REPO4/.ravenclaude/runs/worktree-cleanup/report.md" ] && fail "P15e RC_WORKTREE_CLEANUP_REPORT=off did not silence the hook" || pass "P15e RC_WORKTREE_CLEANUP_REPORT=off silences the hook"

# ── P16: root shim resolves to the plugin script ────────────────────────────
# The shim's own `exec` line resolves `plugins/ravenclaude-core/scripts/
# worktree-clean.sh` RELATIVE TO `git rev-parse --show-toplevel` from the
# CALLER's cwd — it only makes sense run from inside a checkout that actually
# has that relative layout. Exercising the real shim safely (never this
# session's own real worktree) means building a MINIATURE fake marketplace
# with the same relative layout, out of the real files, in scratch space.
ROOT_SHIM="$REPO_ROOT/scripts/worktree-clean.sh"
if [ -f "$ROOT_SHIM" ]; then
  FAKEMKT="$TMP/fake-marketplace"
  mkdir -p "$FAKEMKT/plugins/ravenclaude-core/scripts" "$FAKEMKT/scripts"
  cp "$WTC" "$FAKEMKT/plugins/ravenclaude-core/scripts/worktree-clean.sh"
  cp "$CLEANUP_BRANCHES" "$FAKEMKT/plugins/ravenclaude-core/scripts/cleanup-branches.sh"
  cp "$ROOT_SHIM" "$FAKEMKT/scripts/worktree-clean.sh"
  (cd "$FAKEMKT" && git init -q . && git config user.email t@t.local && git config user.name tester \
    && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
  out_shim="$(cd "$FAKEMKT" && bash scripts/worktree-clean.sh --status --no-network 2>&1)"
  case "$out_shim" in *"state: SELF"*) pass "P16 root shim resolves and runs the plugin script" ;; *) fail "P16 root shim did not behave like the plugin script (out=$(printf '%s' "$out_shim" | head -c 160))" ;; esac
else
  fail "P16 root shim $ROOT_SHIM missing"
fi

# ── T1: teeth — remove the force gate shared by DIRTY/IGNORED/DETACHED-
#    unreachable/STALE (one identical `if [ "$force" != "--force" ]; then`
#    line per class). Targets STALE, deliberately NOT dirty: a dirty target
#    has a SECOND, independent backstop — `git worktree remove` itself
#    refuses a dirty tree without --force — so neutering only OUR gate and
#    pointing it at a dirty worktree still correctly fails (git's own native
#    check catches it), which would make this teeth test pass for the wrong
#    reason. A STALE worktree is, by git's own measure, perfectly CLEAN —
#    there is no git-native concept of "too old" — so our shell-level gate
#    is the ONLY thing standing between it and removal, and is the class
#    this mutation can actually prove depends on real code.
REPO6="$TMP/repo6"
mkdir -p "$REPO6"
(cd "$REPO6" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO6" worktree add -q -b teeth-stale "$TMP/teeth-stale" main >/dev/null 2>&1
(
  cd "$TMP/teeth-stale" || exit 1
  OLD="$(date -u -d '40 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-40d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)"
  [ -n "$OLD" ] && { echo old >> f.txt; GIT_AUTHOR_DATE="$OLD" GIT_COMMITTER_DATE="$OLD" git commit -q -am old; }
) >/dev/null 2>&1
sed 's/if \[ "\$force" != "--force" \]; then/if false; then/' "$WTC" > "$TMP/mut-dirty.sh"
if ! cmp -s "$TMP/mut-dirty.sh" "$WTC" && bash -n "$TMP/mut-dirty.sh" 2>/dev/null; then
  (cd "$REPO6" && bash "$TMP/mut-dirty.sh" --target "$TMP/teeth-stale" --no-network >/dev/null 2>&1)
  [ ! -d "$TMP/teeth-stale" ] && pass "T1 teeth: with the force gate neutered, STALE is removed WITHOUT --force (P7 depends on the gate, not on a git-native backstop)" || fail "T1 teeth: mutant did not remove — P7's refusal may be vacuous, or the mutation missed its target"
else
  fail "T1 setup: could not produce a syntactically-valid mutant (force-gate line not found as expected, or the mutant is broken)"
fi

# ── T2: teeth — remove the --execute gate in cmd_all ────────────────────────
sed 's/if \[ "\$1" = "1" \]; then/if true; then/' "$WTC" > "$TMP/mut-all.sh"
if ! cmp -s "$TMP/mut-all.sh" "$WTC"; then
  REPO7="$TMP/repo7"
  mkdir -p "$REPO7"
  (cd "$REPO7" && git init -q . && git config user.email t@t.local && git config user.name tester \
    && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
  git -C "$REPO7" worktree add -q -b teeth-clean "$TMP/teeth-clean" main >/dev/null 2>&1
  # ⛔ NOT --no-network here: a known PR status (via the stub `gh` on PATH,
  # which answers "0" for anything that isn't the open-PR branch) is what
  # lets "teeth-clean" classify "clean" rather than PR-UNKNOWN (F1) — this
  # test is proving the --execute gate's teeth, not F1's, so it must not
  # accidentally collide with the unrelated PR-UNKNOWN refusal.
  (cd "$REPO7" && env PATH="$TMP/bin:$PATH" bash "$TMP/mut-all.sh" --all >/dev/null 2>&1)
  [ ! -d "$TMP/teeth-clean" ] && pass "T2 teeth: with the --execute gate neutered, \`--all\` (no --execute) mutates — proving P12's dry-run-by-default depends on that gate" || fail "T2 teeth: mutant still left --all as a dry run — P12 may be vacuous"
else
  fail "T2 setup: could not locate the --execute gate to neuter"
fi

# ── T3: teeth — remove the OPEN-PR refusal ──────────────────────────────────
awk '
  /^    OPEN-PR\)$/ { print; print "      : ;;"; getline; while ($0 !~ /;;$/) { getline }; next }
  { print }
' "$WTC" > "$TMP/mut-openpr.sh"
if ! cmp -s "$TMP/mut-openpr.sh" "$WTC"; then
  REPO8="$TMP/repo8"
  mkdir -p "$REPO8"
  (cd "$REPO8" && git init -q . && git config user.email t@t.local && git config user.name tester \
    && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
  git -C "$REPO8" worktree add -q -b wt-has-open-pr "$TMP/teeth-openpr" main >/dev/null 2>&1
  bash -n "$TMP/mut-openpr.sh" 2>/dev/null
  if [ $? -eq 0 ]; then
    (cd "$REPO8" && env PATH="$TMP/bin:$PATH" bash "$TMP/mut-openpr.sh" --target "$TMP/teeth-openpr" >/dev/null 2>&1)
    [ ! -d "$TMP/teeth-openpr" ] && pass "T3 teeth: with the OPEN-PR refusal neutered, it removes an open-PR worktree — proving P8 was real" || fail "T3 teeth: mutant did not remove — P8's refusal may be vacuous"
  else
    fail "T3 setup: mutant has a syntax error — mutation shape did not fit"
  fi
else
  fail "T3 setup: could not locate the OPEN-PR block to neuter"
fi

# ── P17: --all --execute SKIPS a 'clean' worktree another LIVE session is
#    using as its cwd (BUSY) — F3. Reuses the EXISTING worktree-guard.sh
#    SessionStart registry (PATH_KEY=sha256(realpath) + pid/mtime liveness),
#    never a second heuristic — this plants a record the same shape that
#    registry already writes.
REPO9="$TMP/repo9"
mkdir -p "$REPO9"
(cd "$REPO9" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO9" worktree add -q -b busy-clean "$TMP/busy-clean" main >/dev/null 2>&1
BUSY_REAL="$(cd "$TMP/busy-clean" && pwd -P)"
BUSY_KEY=""
if command -v sha256sum >/dev/null 2>&1; then
  BUSY_KEY="$(printf '%s' "$BUSY_REAL" | sha256sum | cut -d' ' -f1)"
elif command -v shasum >/dev/null 2>&1; then
  BUSY_KEY="$(printf '%s' "$BUSY_REAL" | shasum -a 256 | cut -d' ' -f1)"
fi
GUARD_HOME_TEST="$TMP/guard-home"
mkdir -p "$GUARD_HOME_TEST/sessions/$BUSY_KEY"
# pid=$$ (this test's own process) -- guaranteed alive for the test's duration.
printf '{"session_id":"planted","pid":%s,"ppid":0,"host":"test","branch":"busy-clean","started_at":0}\n' "$$" \
  > "$GUARD_HOME_TEST/sessions/$BUSY_KEY/planted.json"
# ⛔ NOT --no-network: a known PR status (via the stub `gh` on PATH) is what
# lets busy-clean classify "clean" rather than PR-UNKNOWN (F1) BEFORE the
# BUSY check (F3) ever gets a say — otherwise this test would "pass" for
# the wrong reason (skipped as PR-UNKNOWN, not as BUSY), which is exactly
# what P17b's "names the BUSY skip" assertion below exists to catch.
busy_out="$(cd "$REPO9" && env PATH="$TMP/bin:$PATH" RC_WORKTREE_GUARD_HOME="$GUARD_HOME_TEST" bash "$WTC" --all --execute 2>&1)"
[ -d "$TMP/busy-clean" ] && pass "P17a --all --execute skipped a BUSY clean worktree (another live session registered)" || fail "P17a BUSY worktree was removed despite a live session registration"
case "$busy_out" in *"BUSY"*) pass "P17b --all --execute output names the BUSY skip" ;; *) fail "P17b no BUSY mention in output ($busy_out)" ;; esac
git -C "$REPO9" show-ref --verify --quiet refs/heads/busy-clean \
  && pass "P17c busy-clean's branch survives (the worktree was never removed, so no retirement happened)" \
  || fail "P17c busy-clean's branch is gone though the worktree should not have been touched"

# control: the SAME shape, in a fresh repo, with NO registration planted --
# proves the skip is keyed on the registry, not on the branch/worktree name
# or some other coincidence.
REPO9B="$TMP/repo9b"
mkdir -p "$REPO9B"
(cd "$REPO9B" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO9B" worktree add -q -b busy-control "$TMP/busy-control" main >/dev/null 2>&1
(cd "$REPO9B" && env PATH="$TMP/bin:$PATH" RC_WORKTREE_GUARD_HOME="$TMP/guard-home-empty" bash "$WTC" --all --execute >/dev/null 2>&1)
[ ! -d "$TMP/busy-control" ] && pass "P17d control: with NO registration planted, the same-shaped clean worktree IS removed" || fail "P17d control worktree survived though nothing was registered"

# ── P18: open-PR status UNKNOWN fails CLOSED, never clean, including
#    --force (F1).
REPO10="$TMP/repo10"
mkdir -p "$REPO10"
(cd "$REPO10" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO10" worktree add -q -b pr-unknown-recent "$TMP/pr-unknown" main >/dev/null 2>&1
out_prunk="$(cd "$REPO10" && bash "$WTC" --status --no-network 2>&1)"
case "$out_prunk" in *"$TMP/pr-unknown"*) case "$out_prunk" in *"state: PR-UNKNOWN"*) pass "P18a --no-network + recent commit classifies PR-UNKNOWN, not clean" ;; *) fail "P18a did not classify PR-UNKNOWN under --no-network" ;; esac ;; *) fail "P18a pr-unknown worktree missing from --status output" ;; esac
(cd "$REPO10" && bash "$WTC" --target "$TMP/pr-unknown" --no-network >/dev/null 2>&1) \
  && fail "P18b PR-UNKNOWN removed WITHOUT --force" \
  || pass "P18b PR-UNKNOWN refuses single-target removal without --force"
(cd "$REPO10" && bash "$WTC" --target "$TMP/pr-unknown" --no-network --force >/dev/null 2>&1) \
  && fail "P18c PR-UNKNOWN removed WITH --force (unknown PR status must never be a removal path, even forced)" \
  || pass "P18c PR-UNKNOWN refuses single-target removal EVEN WITH --force"
[ -d "$TMP/pr-unknown" ] && pass "P18d PR-UNKNOWN worktree directory still present after the forced attempt" || fail "P18d PR-UNKNOWN worktree vanished"

# (b) gh ABSENT from PATH entirely -- same unknown-status fail-closed path,
#     not just the --no-network flag.
REPO10B="$TMP/repo10b"
mkdir -p "$REPO10B"
(cd "$REPO10B" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO10B" worktree add -q -b pr-unknown-nogh "$TMP/pr-unknown-nogh" main >/dev/null 2>&1
MINPATH="$(dirname "$(command -v git)")"
(cd "$REPO10B" && env PATH="$MINPATH" bash "$WTC" --target "$TMP/pr-unknown-nogh" --force >/dev/null 2>&1) \
  && fail "P18e PR-UNKNOWN (gh absent from PATH) removed WITH --force" \
  || pass "P18e PR-UNKNOWN (gh absent from PATH) refuses removal EVEN WITH --force"
[ -d "$TMP/pr-unknown-nogh" ] && pass "P18f gh-absent worktree still present after the forced attempt" || fail "P18f gh-absent worktree vanished"

# (c) --all --execute must SKIP a PR-UNKNOWN entry, never remove it in bulk.
REPO10C="$TMP/repo10c"
mkdir -p "$REPO10C"
(cd "$REPO10C" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO10C" worktree add -q -b pr-unknown-bulk "$TMP/pr-unknown-bulk" main >/dev/null 2>&1
(cd "$REPO10C" && bash "$WTC" --all --execute --no-network >/dev/null 2>&1)
[ -d "$TMP/pr-unknown-bulk" ] && pass "P18g --all --execute skips a PR-UNKNOWN entry (never removed in bulk)" || fail "P18g PR-UNKNOWN entry was removed under --all --execute"

# (d) control: a KNOWN-clean worktree (the stub gh reports 0 open PRs for
#     anything that isn't the open-PR branch) is still removable normally --
#     proves F1's fix narrows exactly the unknown case, nothing wider.
REPO10D="$TMP/repo10d"
mkdir -p "$REPO10D"
(cd "$REPO10D" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO10D" worktree add -q -b pr-known-clean "$TMP/pr-known-clean" main >/dev/null 2>&1
(cd "$REPO10D" && env PATH="$TMP/bin:$PATH" bash "$WTC" --target "$TMP/pr-known-clean" >/dev/null 2>&1)
[ ! -d "$TMP/pr-known-clean" ] && pass "P18h control: a KNOWN-clean worktree (gh confirms 0 open PRs) is still removable without --force" || fail "P18h known-clean control worktree was NOT removed (regression)"

# ── P19: the SessionEnd report hook refuses a symlinked report path or a
#    symlinked ancestor under .ravenclaude, and leaves the outside victim
#    untouched (F2).
# (a) report.md itself is a symlink to a victim file OUTSIDE the repo.
REPO12="$TMP/repo12"
mkdir -p "$REPO12"
(cd "$REPO12" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO12" worktree add -q -b report-wt "$TMP/report-wt" main >/dev/null 2>&1
VICTIM="$TMP/victim-outside-repo.txt"
printf 'untouched\n' > "$VICTIM"
mkdir -p "$REPO12/.ravenclaude/runs/worktree-cleanup"
ln -s "$VICTIM" "$REPO12/.ravenclaude/runs/worktree-cleanup/report.md"
(cd "$REPO12" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" >/dev/null 2>&1)
[ "$(cat "$VICTIM")" = "untouched" ] && pass "P19a report.md-is-a-symlink: the victim file outside the repo is unchanged" || fail "P19a victim file was clobbered through a symlinked report.md"
[ -L "$REPO12/.ravenclaude/runs/worktree-cleanup/report.md" ] && pass "P19b the planted symlink itself was not replaced (the hook refused rather than following it)" || fail "P19b the symlink at report.md is gone -- did the hook remove and replace it?"

# (b) the worktree-cleanup DIRECTORY itself is a symlink to an outside dir.
REPO13="$TMP/repo13"
mkdir -p "$REPO13"
(cd "$REPO13" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO13" worktree add -q -b report-wt2 "$TMP/report-wt2" main >/dev/null 2>&1
VICTIM_DIR="$TMP/victim-dir-outside"
mkdir -p "$VICTIM_DIR"
mkdir -p "$REPO13/.ravenclaude/runs"
ln -s "$VICTIM_DIR" "$REPO13/.ravenclaude/runs/worktree-cleanup"
(cd "$REPO13" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" >/dev/null 2>&1)
[ ! -e "$VICTIM_DIR/report.md" ] && pass "P19c worktree-cleanup-dir-is-a-symlink: nothing was written into the outside victim directory" || fail "P19c a report was written into the victim directory through a symlinked parent"
[ -L "$REPO13/.ravenclaude/runs/worktree-cleanup" ] && pass "P19d the planted directory symlink itself was not replaced" || fail "P19d the symlink at worktree-cleanup is gone"

# (c) .ravenclaude ITSELF is a symlink to an outside dir (ancestor-level attack).
REPO14="$TMP/repo14"
mkdir -p "$REPO14"
(cd "$REPO14" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO14" worktree add -q -b report-wt3 "$TMP/report-wt3" main >/dev/null 2>&1
VICTIM_DIR2="$TMP/victim-dir-outside2"
mkdir -p "$VICTIM_DIR2"
ln -s "$VICTIM_DIR2" "$REPO14/.ravenclaude"
(cd "$REPO14" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" >/dev/null 2>&1)
[ ! -e "$VICTIM_DIR2/runs" ] && pass "P19e .ravenclaude-itself-is-a-symlink: nothing was created inside the outside victim via the ancestor link" || fail "P19e content was written through a symlinked .ravenclaude ancestor"
[ -L "$REPO14/.ravenclaude" ] && pass "P19f the planted .ravenclaude symlink itself was not replaced" || fail "P19f the symlink at .ravenclaude is gone"

# (d) control: a legitimate (non-symlinked) report still writes normally,
#     proving the refusals above aren't simply refusing everything.
REPO15="$TMP/repo15"
mkdir -p "$REPO15"
(cd "$REPO15" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO15" worktree add -q -b report-wt4 "$TMP/report-wt4" main >/dev/null 2>&1
(cd "$REPO15" && env PATH="$TMP/bin:$PATH" CLAUDE_PLUGIN_ROOT="$REPO_ROOT/plugins/ravenclaude-core" bash "$REPORT_HOOK" >/dev/null 2>&1)
[ -f "$REPO15/.ravenclaude/runs/worktree-cleanup/report.md" ] && [ ! -L "$REPO15/.ravenclaude/runs/worktree-cleanup/report.md" ] \
  && pass "P19g control: a legitimate (non-symlinked) tree still gets a real report file written" \
  || fail "P19g legitimate report write regressed"

# ── T4: teeth -- remove the BUSY check from execute_all()'s 'clean' branch;
#    a planted-busy worktree is then removed, proving P17 was real (F3).
REPO9C="$TMP/repo9c"
mkdir -p "$REPO9C"
(cd "$REPO9C" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO9C" worktree add -q -b busy-teeth "$TMP/busy-teeth" main >/dev/null 2>&1
BUSY_TEETH_REAL="$(cd "$TMP/busy-teeth" && pwd -P)"
BUSY_TEETH_KEY=""
if command -v sha256sum >/dev/null 2>&1; then
  BUSY_TEETH_KEY="$(printf '%s' "$BUSY_TEETH_REAL" | sha256sum | cut -d' ' -f1)"
elif command -v shasum >/dev/null 2>&1; then
  BUSY_TEETH_KEY="$(printf '%s' "$BUSY_TEETH_REAL" | shasum -a 256 | cut -d' ' -f1)"
fi
mkdir -p "$GUARD_HOME_TEST/sessions/$BUSY_TEETH_KEY"
printf '{"session_id":"planted2","pid":%s,"ppid":0,"host":"test","branch":"busy-teeth","started_at":0}\n' "$$" \
  > "$GUARD_HOME_TEST/sessions/$BUSY_TEETH_KEY/planted2.json"
sed 's/if is_worktree_busy "\$path"; then/if false; then/' "$WTC" > "$TMP/mut-busy.sh"
if ! cmp -s "$TMP/mut-busy.sh" "$WTC" && bash -n "$TMP/mut-busy.sh" 2>/dev/null; then
  # ⛔ NOT --no-network: same reason as P17 above -- busy-teeth must
  # classify "clean" (via the stub `gh` on PATH) so the BUSY check is the
  # thing actually under test, not an incidental PR-UNKNOWN skip.
  (cd "$REPO9C" && env PATH="$TMP/bin:$PATH" RC_WORKTREE_GUARD_HOME="$GUARD_HOME_TEST" bash "$TMP/mut-busy.sh" --all --execute >/dev/null 2>&1)
  [ ! -d "$TMP/busy-teeth" ] && pass "T4 teeth: with the BUSY check neutered, a planted-busy worktree IS removed -- proving P17's skip depends on that check" || fail "T4 teeth: mutant still skipped it -- P17 may be vacuous"
else
  fail "T4 setup: could not produce a syntactically-valid mutant (BUSY check line not found as expected)"
fi

# ── T5: teeth -- remove the PR-UNKNOWN refusal in dispatch_removal(); an
#    unknown-PR-status worktree is then removed, proving P18 was real (F1).
REPO11="$TMP/repo11"
mkdir -p "$REPO11"
(cd "$REPO11" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO11" worktree add -q -b pr-unknown-teeth "$TMP/pr-unknown-teeth" main >/dev/null 2>&1
awk '
  /^    PR-UNKNOWN\)$/ { print; print "      : ;;"; getline; while ($0 !~ /;;$/) { getline }; next }
  { print }
' "$WTC" > "$TMP/mut-prunknown.sh"
if ! cmp -s "$TMP/mut-prunknown.sh" "$WTC" && bash -n "$TMP/mut-prunknown.sh" 2>/dev/null; then
  (cd "$REPO11" && bash "$TMP/mut-prunknown.sh" --target "$TMP/pr-unknown-teeth" --no-network --force >/dev/null 2>&1)
  [ ! -d "$TMP/pr-unknown-teeth" ] && pass "T5 teeth: with the PR-UNKNOWN refusal neutered, it is removed -- proving P18 was real" || fail "T5 teeth: mutant did not remove -- P18's refusal may be vacuous"
else
  fail "T5 setup: could not locate the PR-UNKNOWN block to neuter"
fi

# ── T6: teeth -- reproduce the ORIGINAL (pre-fix) report-write shape
#    verbatim (bare mkdir -p + a single `>` redirection, no symlink checks,
#    no mktemp+mv) against the SAME planted-symlink fixture as P19a, and
#    show it DOES clobber the victim -- proving the vulnerability class F2
#    fixes is real, not hypothetical. This reproduces the reported shape
#    directly (not a sed-mutant of the live hook) because the fix is two
#    independent layers (the symlink checks, and mv's non-dereferencing
#    rename) and either alone already defeats the report.md-is-a-symlink
#    case -- a true single-point mutant of the live file would not
#    demonstrate anything here. P19b/d/f already prove the live hook's
#    actual refusal path has an effect (the symlink survives, unreplaced).
REPO16="$TMP/repo16"
mkdir -p "$REPO16"
(cd "$REPO16" && git init -q . && git config user.email t@t.local && git config user.name tester \
  && echo hi > f.txt && git add f.txt && git commit -q -m init && git branch -M main) >/dev/null 2>&1
git -C "$REPO16" worktree add -q -b report-teeth "$TMP/report-teeth" main >/dev/null 2>&1
VICTIM2="$TMP/victim-teeth.txt"
printf 'untouched\n' > "$VICTIM2"
mkdir -p "$REPO16/.ravenclaude/runs/worktree-cleanup"
ln -s "$VICTIM2" "$REPO16/.ravenclaude/runs/worktree-cleanup/report.md"
( cd "$REPO16" || exit 1
  RUN_DIR_PRE="$REPO16/.ravenclaude/runs/worktree-cleanup"
  mkdir -p "$RUN_DIR_PRE" 2>/dev/null
  { printf 'CLOBBERED\n'; } > "$RUN_DIR_PRE/report.md" 2>/dev/null
) >/dev/null 2>&1
[ "$(cat "$VICTIM2")" = "CLOBBERED" ] && pass "T6 teeth: the pre-fix write shape (bare mkdir -p + single redirection) DOES follow the symlink and clobber the victim -- proving the vulnerability F2 closes was real" || fail "T6 setup: could not reproduce the pre-fix vulnerability shape to prove against"

echo "worktree-clean-lifecycle: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
