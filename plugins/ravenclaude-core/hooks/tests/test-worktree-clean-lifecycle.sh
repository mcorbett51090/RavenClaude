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
#
#   T1  teeth: remove the DIRTY --force gate -> a dirty worktree is removed
#       WITHOUT --force, proving P3's refusal was real
#   T2  teeth: remove the --execute gate in cmd_all -> `--all` with no
#       --execute now mutates, proving P12's dry-run-by-default has teeth
#   T3  teeth: remove the OPEN-PR refusal -> an open-PR worktree is removed,
#       proving P8's "never, even with --force" was real
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
exec_out="$(cd "$REPO2" && env PATH="$TMP/bin:$PATH" bash "$WTC" --all --execute --no-network 2>&1)"
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
(cd "$REPO3" && env PATH="$TMP/bin:$PATH" bash "$INSTALLED/worktree-clean.sh" --target "$TMP/installed-clean" --no-network >/dev/null 2>&1)
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
  (cd "$REPO7" && env PATH="$TMP/bin:$PATH" bash "$TMP/mut-all.sh" --all --no-network >/dev/null 2>&1)
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

echo "worktree-clean-lifecycle: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
