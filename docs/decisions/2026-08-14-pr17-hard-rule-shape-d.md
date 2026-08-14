# Decision record — PR 17 hard-rule shape (D2)

**Date:** 2026-08-14 · **Owner:** Matt · **Method:** `/forge` keep-going + `security-reviewer` red-team
**Status:** **CLEAR d** — keep the existing Write / prose / `printf`-assembled-fixture workaround. Do **not** widen the PreToolUse(Bash) hard-rule ignore-surface.

## What D2 already settled (2026-08-13)

`docs/plans/2026-08-13-recurring-defect-hardening/decisions.md` D2 funded a `security-reviewer` pass and a build. Shape among (a) path prefix, (b) in-file sentinel, (c) diff-scoped exemption, (d) keep the workaround was **the red-team's call**.

## What this review settled

Artifact: `.ravenclaude/runs/forge/harden-pr17/red-team.md` (2026-08-14).
Sign-off: `SECURITY-REVIEWER: CLEAR d`.

| Shape | Verdict |
|---|---|
| (a) `docs/**` + `tests/fixtures/**` prefix on a Bash command scanner | **Rejected.** A live command can `cd` into the prefix, put the substring on a side-effect path, or point `git -C` / `--git-dir` at it. |
| (b) trailing-comment / in-file sentinel on a Bash deny | **Rejected.** A live command can carry the marker as a comment the shell ignores. Reusing `# noport` would couple a portability lint to a history-destroying deny. |
| (c) diff-scoped exemption | **Rejected.** Sticky or mis-keyed, it becomes (a) or (b). |
| (d) keep Write / prose / fragment-assembled fixtures | **Cleared.** Zero new ignore-surface. |

The live planning false-positive is mostly a **described** pattern inside a Bash argument. `guard-destructive.sh` already strips inert `-m` / heredoc bodies. Extending that strip to `echo` / `printf` is the pipe-to-interpreter smuggle. The sanctioned path is the Write tool.

## What shipped with this record

**Gate 209** — a regression lock, not a door. It proves the current fail-closed floor still denies a live dangerous command (including plants that look like (a) or (b)), and it fails closed if a later commit adds a path/sentinel skip to `guard-destructive.sh` or the `thing-concerns.py` Bash deny path, or attaches `guard-destructive.sh` to a Write/Edit/MultiEdit-only matcher.

## Explicit non-goals

- Do not edit `guard-destructive.sh`, `thing-concerns.py`, or `thing-decision.py` to add an exemption.
- Do not give `guard-premise.sh` T-PROSE a `docs/**` blanket (a diagnosis written into docs is the original incident).
- Do not retrofit source-scan PRs 3/6/8/9/11/13 in this change.
- Do not formalize PR 16 / D6 (still deferred).
- Porting the inert-body preprocessor into the tribunal matcher is a **separate** review, not this CLEAR.
