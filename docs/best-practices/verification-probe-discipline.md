# An empty probe result is a claim about the probe

**Status:** **Primary diagnostic (+1 absolute rule)** — when an ad-hoc verification
command returns *nothing / clean / safe / 0*, check this before you act on it. The
absolute rule is the stderr one in "How to apply".

**Domain:** Agent design, verification discipline, cross-domain.

**Applies to:** `any Claude Code project` — the throwaway `git` / `grep` / `find` /
`gh` one-liners an agent writes mid-task to decide whether something is true, and the
decisions taken on their output. Not committed gates (see the sibling docs below).

---

## Why this exists

In one session an agent ran four ad-hoc verification probes and **all four were broken
in the same direction: toward "nothing there."**

| # | The bug | What it reported |
|---|---|---|
| 1 | Resolved `origin/main` in repo A, used that SHA inside 9 *other* clones | 7 clones "0 unique commits" — `git log --not <unknown-sha>` had errored |
| 2 | `git diff M b -- $F --stat` — flag *after* `--`, so git read it as a pathspec | raw diff lines printed as findings; a failed pathspec prints nothing |
| 3 | `$T="$(git ls-remote --tags …)"` captured the tag *and* its `^{}` deref line | "0 bytes" |
| 4 | `git show --stat` on an **annotated** tag prints a tag header first | parsed the literal word `tag` as a filename → "0 bytes" |

Three of the four carried `2>/dev/null`. That is not incidental — **suppression converts
an error into an empty string, and an empty string is what "nothing found" looks like.**

The near-miss is the point. Probe 1 was about to authorise deleting **7.8 GB across nine
repository clones**. Re-running it against each clone's own refs showed every clone held
200+ commits not reachable from `origin/main`, and one held a branch tip no other copy
had. The first version of that cleanup would have reported all nine as safe to delete.

**Scrutiny was scaling with how *interesting* the answer was, not with what depended on
it.** Surprising results got dug into; empty results were accepted instantly. That is
backwards: "nothing there" and "the probe did not run" are the same bytes.

## How to apply

> **ABSOLUTE RULE — never `2>/dev/null` a probe whose output you will act on.**
> Use `2>&1` and read it. Suppression is for known-noisy output, never for an answer
> that gates a decision.

> **An empty / negative / zero result is not a finding until a positive control shows
> the same probe can return non-empty.**

The control is one extra command: run the identical probe shape against something you
already know returns a hit. If it comes back empty too, the probe is broken, not the
subject.

```bash
# The probe (this is the answer you'll act on)
git diff --stat "$MAIN" "$BRANCH" -- $FILES | tail -1     # -> empty. Merged? Or broken?

# The control (must be NON-empty, or the probe proves nothing)
git diff --stat "$MAIN" "$KNOWN_DIFFERENT_REF" -- README.md | tail -1
```

**Do:**
- Resolve refs, paths and env values **where they are consumed**. Bug 1 was a variable
  computed in repo A and used in repo B; the SHA was simply unknown there.
- Print the raw output once, look at its shape, *then* write the parser. Bugs 2–4 were
  all parsing an output shape that had never been inspected.
- Before anything irreversible, name the load-bearing assumption in one line and the
  probe that would falsify it.
- Say "the command exited 0", not "I verified X", unless you checked the thing rather
  than the exit code.

**Don't:**
- Report clean/safe/empty without being able to name the control you ran.
- Treat a passing pipeline as evidence — `set -o pipefail` is off by default, and
  `cmd | wc -l` reports `0` for both "no matches" and "cmd failed".
- Assume a pattern found in one instance holds across siblings. Nine clones looked
  identical; one had a different branch tip.

### The same defect, in shipped code

This is not only an agent-behaviour rule — the pattern ships. `scripts/worktree-clean.sh`
gated **deletion** on `[ -z "$(git -C "$d" status --porcelain 2>/dev/null)" ]`. A failed
`git status` — a stale linked worktree whose admin dir under `.git/worktrees/` is gone, a
corrupt `.git`, git off PATH — writes nothing and exits non-zero, so the failed inspection
was indistinguishable from a clean tree and the worktree was **deleted unexamined**.

Measured: a stale linked worktree yields **exit 128 with empty stdout**; a healthy one
exits 0. The fix is to capture the exit code separately and emit a third state:

```bash
worktree_state() { # $1=dir -> prints clean|DIRTY|UNKNOWN
  local out rc=0
  out="$(git -C "$1" status --porcelain 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ]; then printf 'UNKNOWN'          # could not look — fail toward NOT deleting
  elif [ -z "$out" ]; then printf 'clean'            # looked, and it is clean
  else printf 'DIRTY'; fi
}
```

**"I could not look" is a distinct state from "I looked and it is clean."** Collapsing
them is the whole bug. The same shape sat in
[`branch-hygiene.sh`](../../plugins/ravenclaude-core/scripts/branch-hygiene.sh) —
`git status … | wc -l` yields `0` on failure, so a broken worktree passed its gate 2 —
though there the downstream `git worktree remove` (no `--force`) and `git branch -d`
vetoes close the actual loss path. Same pattern, honestly different severity.

## Edge cases / when this does NOT apply

- **Fail-safe hooks keep their suppression.** This repo's hooks exit 0 on every error
  path by contract, so a guardrail can never wedge a session. `2>/dev/null` there is the
  design, not a defect. The rule is scoped to paths where a suppressed error's empty
  result becomes a **verdict**.
- **A control is not free on every command.** Reserve it for results you will act on,
  and always for irreversible ones. A `ls` to see what is in a directory does not need
  ceremony.
- **A true observation can still carry a false inference.** Two further errors in the
  same session were not probe bugs at all: "absent from the check list" → "the macOS
  suite never ran on this PR, that's a gap" (it is deliberately `paths:`-filtered and
  correctly skipped), and a `git check-ignore` reading that was accurate for a
  47-commits-behind tree but was generalised to the repo. Grounding an observation is
  not grounding an inference drawn from it — the split
  [FORGE G1](../../plugins/ravenclaude-core/skills/forge-pipeline/SKILL.md) exists for.

## See also

- [`validating-a-measuring-instrument.md`](./validating-a-measuring-instrument.md) — the
  mirror image, and read it if your tool is *producing findings*. That doc covers a
  committed checker that floods you with **false positives** ("does it invent bad?");
  this one covers an ad-hoc probe returning **false negatives**, where empty and
  didn't-run are the same string. Its "your conclusion is bounded by your coverage" and
  "a verifier that caches its input will lie in both directions" are adjacent.
- [`ci-gate-audit.md`](./ci-gate-audit.md) — the committed-gate equivalent: every gate
  must fail on known-bad and pass on known-good. A positive control is that discipline
  applied to a one-off command.
- [`prefer-a-deterministic-gate-over-a-prose-rule.md`](../../plugins/ravenclaude-core/best-practices/prefer-a-deterministic-gate-over-a-prose-rule.md)
  — this doc is prose and prose has no teeth. The gate that does is **Gate 216**
  (`scripts/check-worktree-state.sh`), which carries an external teeth mode:
  with the fix removed it must fail on a *deletion* assertion, not merely a
  display one. Deliberately named rather than linked, so this doc can land on
  `main` on its own schedule without a dangling reference in either direction.

## Provenance

Extracted 2026-08-17 from a session in which the four probes above were each caught and
corrected in-session, after the user observed the agent was "making assumptions and going
with it more than you used to." The defect is **ordering** — act-then-verify — not absence
of verification, which is why it survived: every individual claim was eventually checked.

The rule then found a real one. Applying it deliberately turned up the
`worktree-clean.sh` data-loss path above, which had been live and unnoticed. And while
building its gate, the first fixture used a plain non-git subdirectory as the
"un-inspectable" case — git's discovery walks *upward*, finds the parent repo, and
reports it merely dirty, so the gate passed **without ever exercising the defect**. The
corrected fixture orphans a real linked worktree's admin dir. That mistake, made while
writing the doc's own gate, is the most honest evidence that the rule is not obvious.

---

_Last reviewed: 2026-08-17 by `mcorbett51090`_
