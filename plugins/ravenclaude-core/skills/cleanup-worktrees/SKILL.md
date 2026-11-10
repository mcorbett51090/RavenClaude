---
name: cleanup-worktrees
description: Remove finished agent worktrees, prune their branches, and surface anything still in flight. Run at the end of a multi-agent session and weekly as hygiene.
---

# Skill: cleanup-worktrees

> **Labeling (Sleipnir):** worktrees are "Sleipnir's stables" in user-facing prose (see `ravenclaude-core/CLAUDE.md` → "Sleipnir"); this skill returns Sleipnir to the stable. Labeling only; the mechanics below are unchanged.

## The shipped tool

[`scripts/worktree-clean.sh`](../../scripts/worktree-clean.sh) (canonical home;
the repo-root `scripts/worktree-clean.sh` is a thin shim, same pattern as
`cleanup-branches.sh`) implements everything below as one entry point:

```bash
scripts/worktree-clean.sh --status [--no-network]          # read-only report
scripts/worktree-clean.sh --all [--execute] [--no-network] # bulk; dry-run by default
scripts/worktree-clean.sh <slug> [--force]                 # single, under .claude/worktrees/
scripts/worktree-clean.sh --target <path> [--force]        # single, anywhere (sibling/ad-hoc)
```

**Discovery is porcelain-wide** — `git worktree list --porcelain`, not just
`.claude/worktrees/<role>-<slug>/` — so a sibling worktree, an ad-hoc one a
human made by hand, or anything else `git worktree list` knows about is
covered. Addressing a worktree for *removal* still comes in two shapes:
`<slug>` for the conventional `.claude/worktrees/<slug>` path (unchanged
containment/charset checks), and `--target <path>` for anything else —
anchored to **porcelain membership** (the resolved path must equal one git
itself reported) rather than a directory prefix, so it is at least as safe,
not a looser escape hatch.

**Dry run is the default everywhere a bulk/automated path could mutate
something.** `--status` never mutates. `--all` without `--execute` prints
exactly what it *would* do and changes nothing on disk — pass `--execute` to
actually run the lifecycle. A single `<slug>` or `--target` removal is
already an individually-named, explicit human action; it still honors the
per-class force contract below.

## The trigger

A **SessionEnd** hook ([`scripts/worktree-cleanup-report.sh`](../../scripts/worktree-cleanup-report.sh),
registered in `hooks/hooks.json` alongside — never instead of —
`spectate-emit.sh`) runs `worktree-clean.sh --status --no-network` at the end
of every session and, when there is anything beyond the solo main worktree,
**flushes** the dry-run report to `.ravenclaude/runs/worktree-cleanup/report.md`.
It is a report, never a mutation: a SessionEnd hook's stdout is not injected
into any live context (the session is ending — there is no further turn), so
this mirrors the documented SessionEnd contract ("flush run artifacts, emit a
summary") and the plugin's other SessionEnd hooks, which are file-writers for
the same reason. `--no-network` is there specifically so this hook never
makes a per-worktree `gh pr list` call on every session end — see "Open PR"
below for what that trades away. Opt out with `RC_WORKTREE_CLEANUP_REPORT=off`.

Reading that report (or running `--status` by hand) is the normal way a human
or the Team Lead discovers there is cleanup to do; nothing auto-executes.

## Classification

- **clean** — safe to remove with no flag. Requires a *positive* signal: no
  uncommitted/untracked/ignored content, no open PR on its branch (or, absent
  network/`gh`, no evidence either way **and** a recent commit — see Stale),
  and not detached-unreachable/locked/prunable.
- **DIRTY** — uncommitted changes. Refuses; `--force` removes anyway.
- **UNKNOWN** — the tree could not be inspected (`git status` failed, or
  succeeded against an ancestor, or is unreadable). ⛔ This is **not** a third
  flavour of clean: an un-inspected tree produces empty output, byte-identical
  to a clean one, so treating it as clean deletes work nobody looked at.
  `worktree-clean.sh` refuses it — and refuses it **even with `--force`**,
  because `--force` discards uncommitted work and here we do not know whether
  there is any.

  There are **two causes**, and only one of them involves an error:
  - *`git status` failed* — a stale linked worktree whose admin dir under
    `.git/worktrees/` is gone, a corrupt `.git`, permission denied. Empty
    stdout, non-zero exit.
  - *`git status` **succeeded**, but against an ANCESTOR* — the directory is
    not a worktree, or its `.git` file is missing, so git's discovery walked
    up and reported the parent repo. This also comes back empty — with
    **exit 0**. This is the more common shape, and it is why a successful
    `git status` is not by itself evidence that anything was inspected.

  ⛔ Do **not** reach for `git worktree repair` / `git worktree prune` as a
  reflex. Both were measured to be no-ops on every UNKNOWN shape tested, so
  that advice sends you in a loop — and loop pressure is what makes people
  tunnel to a manual delete. Read the specific cause, fix that, or move the
  tree aside. Never delete it to make the message go away.
- **IGNORED** — nothing tracked is modified and nothing is untracked, but the
  tree still holds **ignored** files (`.env`, `node_modules/`, a local db).
  ⛔ `git status --porcelain` is **silent on ignored files by design**, so this
  tree would otherwise report empty output and classify `clean` — with git
  working perfectly. The `.env` case is the one that hurts: a file is ignored
  *precisely because* it is not in git, so the rule that hides it from the
  probe is the same rule that guarantees no other copy exists.
  `worktree-clean.sh` skips it under `--all` and names what is there. Unlike
  UNKNOWN, it **does** honour `--force` — the difference is knowledge, not
  danger: here we can see exactly what would be destroyed, so `--force` is a
  considered choice rather than a blind one.
- **DETACHED-unreachable** — the tree is clean by every measure above, but its
  HEAD is detached at a commit **no branch or tag contains**. ⛔ This is the
  first state where the work is *committed*: `git status` is rightly silent,
  and removing the worktree makes that commit unreachable. The reflog does
  **not** rescue it — `.git/worktrees/<name>/logs/HEAD` is deleted with the
  admin dir. Recovery is `git fsck --lost-found` until gc prunes.
  `worktree-clean.sh` skips it under `--all`, names the SHA, and prints the
  one-command rescue: `git branch <name> <sha>`. It honours `--force`, like
  IGNORED. **The discriminator is reachability, not detachment** — a worktree
  detached at an existing ref tip is common and harmless, still reads `clean`,
  and is removed normally.
- **STALE** — last commit older than the threshold (default 14 days,
  `WORKTREE_CLEAN_STALE_DAYS` to override), or whose age could not be
  determined at all. **Flag only** — never auto-removed under
  `--all --execute`; a single-target removal needs `--force`, same contract
  as IGNORED/DETACHED-unreachable. ⛔ An *unverifiable* open-PR status
  (`--no-network`, or `gh` simply absent) is deliberately **not, by itself**,
  grounds for STALE — only commit age decides that. A recent commit whose PR
  status could not be checked still classifies `clean` (no negative evidence
  found — the same "fails safe, not closed" precedent `cleanup-branches.sh`
  already applies to an unverifiable PR once another signal clears the
  branch; here the other signal is age); an *old* commit with the same
  unverifiable status is STALE, because age alone already flags it.
- **OPEN-PR** — the worktree's branch has an open PR (checked via `gh`, unless
  `--no-network`). Refuses, **even with `--force`** — unlike IGNORED/STALE,
  this isn't a "we can see the risk and accept it" case; the branch's review
  thread is still live. (The worktree directory itself isn't what closes a
  PR — its *branch* is, and `cleanup-branches.sh`'s own open-PR veto is the
  thing that actually protects that, downstream, in the unified lifecycle
  below — this class exists so the worktree isn't pulled out from under an
  in-review branch either.)
- **LOCKED** — `git worktree lock` (or the admin `locked` file). Refuses
  unconditionally, no `--force` escape. Unlock first: `git worktree unlock
  <path>`.
- **PRUNABLE** — git itself reports the worktree's directory is gone from
  disk. The correct action is `git worktree prune`, never `git worktree
  remove` — handled as its own case, not folded into UNKNOWN.
- **MAIN / SELF** — the primary checkout, and the worktree the process is
  currently running in. Never touched, no force escape, ever.

## The unified lifecycle

Removing a worktree and retiring its branch are **one lifecycle, not two**:
remove → `git worktree prune` → branch cleanup via
[`cleanup-branches.sh`](../../scripts/cleanup-branches.sh), which owns its own
safety checks (merged-PR-tip match, ancestry, the open-PR veto, the
SHA-guarded atomic delete via `git update-ref -d`) — **never** a second,
parallel `git branch -D` path. `worktree-clean.sh` resolves
`cleanup-branches.sh` relative to its own location, so this works whether
you're running it from this marketplace checkout or from an installed-plugin
layout (`~/.claude/plugins/cache/.../scripts/`).

```
worktree removed -> git worktree prune -> cleanup-branches.sh <branch>
```

## Output format

```
Worktrees (git worktree list --porcelain):
  /repo/.claude/worktrees/coder-auth-refresh
      branch: agent/coder/auth-refresh  state: clean
      no open PR, last commit 2d ago
  /repo/.claude/worktrees/coder/billing-page
      branch: agent/coder/billing-page  state: OPEN-PR
      branch 'agent/coder/billing-page' has 1 open PR(s)
  /repo/.claude/worktrees/tester/old-spike
      branch: agent/tester/old-spike  state: STALE
      last commit 23d ago (threshold 14d), no open PR
```

## Don'ts

- Never delete a worktree with uncommitted changes without explicit user
  approval (`--force`).
- Never `git branch -D` (force-delete) — the unified lifecycle routes every
  branch deletion through `cleanup-branches.sh`'s `-d`/SHA-guarded path; there
  is no second, parallel force path to reach for.
- Never delete the worktree you're currently running inside, or the main
  checkout. `worktree-clean.sh` refuses both unconditionally.
- Never run this tool's bulk/dry-run modes against a repo you have not
  verified you mean to sweep — `--all --execute` only ever touches entries
  classified `clean`, but "clean" is computed, not assumed; read `--status`
  first if in doubt.

## Codex managed worktrees (DOC adapt 2026-09-20 — UNVERIFIED)
This skill targets RavenClaude / Sleipnir agent worktrees — and, since
discovery is now porcelain-wide, any OTHER worktree on the box too. Codex
0.155's agents overview owns **managed** worktree hide/archive/confirmed-delete
for its own worktrees, and there is no verified on-disk marker that
distinguishes one deterministically from an ordinary worktree in
`git worktree list --porcelain`. The mitigation is structural, not detection:
`--all` defaults to dry-run, so a human reviews the full porcelain-wide list
(which may include a Codex-managed path) before `--execute` can touch
anything. If `git worktree list` shows a Codex-managed path still owned by the
overview, prefer the overview's own confirmed-delete path; do not assume this
tool knows the difference. Do not conflate Sleipnir hygiene with Codex
managed-worktree lifecycle. Guardian approval evidence KEEP elsewhere is
unchanged by this note.

## Why a skill, when the Agent tool has built-in `isolation: "worktree"`?
The Agent tool's native worktree isolation auto-cleans up its own ephemeral worktrees. This skill cleans up the *managed* worktrees created by [`new-worktree`](../new-worktree/SKILL.md) — predictable paths, predictable branch names, persisting across multiple sub-agent runs so the Team Lead can hand a worktree off between agents — **and, as of the porcelain-wide discovery above, any other worktree on the box**. Those won't be cleaned by the harness, so the Team Lead runs this skill (or lets the SessionEnd report surface it) at the end of a multi-agent session and weekly as hygiene.
