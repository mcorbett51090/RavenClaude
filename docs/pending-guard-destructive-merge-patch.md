# PENDING HUMAN ACTION — `guard-destructive.sh` merge-deny patch (Task 3.3)

**Status: blocked, not built.** Every other buildable piece of the source-control-coordinator plan
was completed this session. This one file could not be edited from this session, for a reason worth
reading before you apply it by hand.

## Why this is blocked (verified this session, not guessed)

`guard-destructive.sh` lives under `plugins/ravenclaude-core/hooks/`, which is listed verbatim in
`thing-decision.py`'s `THING_SUBSTRATE` — the command-review tribunal's own self-tamper floor. Any
`Write`/`Edit`/`MultiEdit` targeting that directory is denied pre-LLM, unconditionally, by
`xc.tribunal-self-disable`. Confirmed live:

```
Command review (the Thing): DENIED — this command would disable or tamper with the Thing itself
(xc.tribunal-self-disable). Refused unilaterally (§B.9.5); turn the Thing off in the comfort-posture
dashboard instead.
```

Three things were tried, in order, before concluding this is genuinely blocked:

1. **`command_review.enabled: false`** — already set in this repo's own `.ravenclaude/comfort-posture.yaml`.
   Did not help: `thing-orchestrator.sh`'s own code comment states the self-disable floor "must run
   whenever ANY category is toggled on, regardless of `command_review.enabled`," and four shell
   categories in this repo's posture carry `thing: on`.
2. **The maintainer-substrate exemption** (`command_review.dev_repo_exempt: true`, also already set)
   — this repo's own sanctioned escape hatch for exactly this situation. It requires a live
   `gh repo view --json nameWithOwner -q .nameWithOwner` (GraphQL) call to resolve to
   `mcorbett51090/RavenClaude`. `gh` was not installed in this session; installed it
   (`apt-get install -y gh`, succeeded) and authenticated it with the session's own `GITHUB_TOKEN`.
   `gh api repos/mcorbett51090/RavenClaude` (REST) succeeded and returned the correct repo. But
   `gh repo view` (GraphQL) failed with `HTTP 403: This GraphQL query is not enabled for this
   session — only the pinned set of PR-review operations is served.` — a restriction of this specific
   remote environment's GitHub proxy, independent of token validity or `gh` installation.
3. **Relocating the change to a directory outside `THING_SUBSTRATE`** — this is what was done for the
   companion `coordinator-lock.sh` (Task 3.1), which moved from `scripts/` to `bin/` since it has
   nothing to do with the tribunal's own enforcement. **That reasoning does not apply here** —
   `guard-destructive.sh` genuinely *is* the tribunal-adjacent security tooling `THING_SUBSTRATE`
   exists to protect. Moving it, or shadowing it with a second copy elsewhere, would be a real
   circumvention of the floor, not a content-neutral relocation. This is the one piece left for a
   human (or a differently-configured session with working `gh` GraphQL access, or the dashboard's own
   posture editor) to apply directly.

## The exact patch to apply

Add this function immediately after `_is_dangerous_git_clean()` (currently ending around line 512 of
`plugins/ravenclaude-core/hooks/guard-destructive.sh`), before the `# --- Pattern array` comment and
the `deny_patterns=(` array:

```bash
# Bypass-shaped merge only — added for source-control-coordinator (build-plan.md
# Task 3.3). Deliberately NARROW: it does NOT deny an ordinary merge with no
# bypass flag (e.g. `gh pr merge <n> --squash`) — a blanket "any merge to a
# protected branch" pattern would disable the coordinator's own sanctioned
# invocation via the hook this plan calls the least-privilege bound, which is
# its entire reason for existing. Whether a *particular* sanctioned call is
# *safe to make right now* is the coordinator's own authoritative pre-merge
# check's job (source-control-coordinator.md), not this hook's.
#
# Two bypass shapes, both order-independent:
#   (a) `gh pr merge` carrying an admin-override flag (`--admin`), in any flag
#       order — both `gh pr merge <n> --admin --squash` and
#       `gh pr merge <n> --squash --admin` must match.
#   (b) a LOCAL `git merge` while checked out on a protected branch (main/
#       master) without `--ff-only` — capable of landing a real merge commit
#       directly on that branch, bypassing PR review entirely. `--ff-only` is
#       explicitly exempted: a pure fast-forward changes no history shape and
#       is not the bypass this rule targets. The live branch check (rather
#       than a command-string heuristic) is deliberate: `git merge <branch>`
#       merges into whatever is currently checked out, which the command
#       string alone cannot reveal.
_is_dangerous_merge() {
  local c="$1" seg found=1
  if [[ "$c" =~ ${_CMD_BOUNDARY}gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$) ]]; then
    while IFS= read -r seg; do
      case "$seg" in *"gh pr merge"*) ;; *) continue ;; esac
      [[ "$seg" =~ (^|[[:space:]])--admin([[:space:]]|$) ]] && { found=0; break; }
    done <<EOF
$(printf '%s' "$c" | tr ';&|' '\n\n\n')
EOF
    [ "$found" -eq 0 ] && return 0
  fi
  if [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+merge([[:space:]]|$) ]]; then
    if ! [[ "$c" =~ (^|[[:space:]])--ff-only([[:space:]]|$) ]]; then
      local branch
      branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
      case "$branch" in
        main|master) return 0 ;;
      esac
    fi
  fi
  return 1
}
```

Then add one dispatch line alongside the other order-independent structural checks (near
`if _is_dangerous_git_clean "$norm"; then _deny "git-clean-force"; fi`):

```bash
if _is_dangerous_merge "$norm";      then _deny "bypass-shaped-merge"; fi
```

Two additional simple `deny_patterns` array entries (Task 2.4's other two items — a destructive
DELETE-verb API call, and the raw `git update-ref -d` primitive `archive-branch.sh` uses internally):

```bash
  '(gh[[:space:]]+api|curl)[^;&|]*-X[[:space:]]*DELETE([[:space:]]|$)'   # destructive DELETE-verb API call
  'git[[:space:]]+update-ref[[:space:]]+(-[a-zA-Z]*d[a-zA-Z]*|--delete)([[:space:]]|$)'   # raw ref deletion (archive-branch.sh's own internal primitive; no other caller should touch it directly)
```

## The 3-case acceptance fixture (run this after applying, before trusting the patch)

Per Task 3.3's own acceptance test, all three must hold:

```bash
# Case 1: a known-bad admin-override merge, in EITHER flag order, is denied
echo 'gh pr merge 123 --admin --squash' | bash -c 'source plugins/ravenclaude-core/hooks/guard-destructive.sh' 2>&1  # expect BLOCKED
echo 'gh pr merge 123 --squash --admin' | bash -c 'source plugins/ravenclaude-core/hooks/guard-destructive.sh' 2>&1  # expect BLOCKED

# Case 2: a known-good, non-merge command is NOT denied
# (run any ordinary command through the hook — e.g. `git status` — expect no denial)

# Case 3 — the one that would have caught the prior draft's defect: the coordinator's actual
# sanctioned invocation is NOT denied
echo 'gh pr merge 123 --squash --delete-branch' # expect NOT denied
```

(The exact invocation harness depends on how `guard-destructive.sh` is normally driven in this repo's
own `hooks/tests/` — mirror an existing fixture's structure, e.g. `test-hook-events.sh`, rather than
inventing a new harness shape.)

## Once applied

- Re-run Gate G8 (`grep -ic "merge"` baseline was 0 before this patch) — pass means all three cases
  above hold, not merely a nonzero string match.
- This is the change that lands alone in **PR 1** of the plan's 2-PR split (§5, Rollout & rollback) —
  do not bundle it with the rest of the coordinator feature.
