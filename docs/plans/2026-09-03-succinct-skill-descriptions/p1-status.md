# P1 status — blocked on instrument availability

**2026-09-08.** P1 (claim-6 effect-size study) was authorized (P0 fully green, both G-P0.1
arms confirmed — see `rendering-audit.md`). Before building the study, `claude plugin
eval init --bare` was run as a cheap pre-flight probe (per this repo's own "verify the
load-bearing assumption before a high-impact activity" discipline) — the plan's
specified instrument.

**Result:** the command printed `` `plugin eval` is currently in early access `` and
wrote no files. Confirmed via web search this is an **account-level Anthropic
enrollment gate**, not a local config flag — the command recognizes its syntax but
exits without running on an account that hasn't been granted access. Nothing in this
repo or this local environment can enable it.

**Owner decision (2026-09-08):** check/enable early access on the Anthropic account,
then resume P1 exactly as specified in `plan.md` (§P1 — 40 skills / ≥12 confusable
clusters / 3 arms / ≥5 runs, pre-registered power calculation, positive control).
Two rejected alternatives, recorded so they aren't re-proposed without cause: a
manual Agent-dispatch substitute instrument (weaker than the native grader — the
`tool_used: Skill` ablation-scoring semantics `plan.md` P1's spec depends on are not
trivially reproducible by hand) and skipping straight to the P8 fallback (linter +
ratchet + top-decile pass only, no preservation apparatus).

**To resume:** re-run `claude plugin eval init --bare probe --eval-dir <scratch>` as
the cheap confirmation probe (do not re-derive the whole gate design) — once it writes
`prompt.md` + `graders/criteria.md` instead of printing the early-access notice, P1's
build steps in `plan.md` are unblocked. No other repo-side gate is holding this up.

---

## Update 2026-09-08 — substitute-instrument pilot run, then CLOSED

Built and ran a manual substitute (real `Agent`-tool dispatches, no
`claude plugin eval` dependency) rather than waiting on early access. Full record:
`.ravenclaude/runs/succinct-skill-descriptions-p1/pilot-summary.md` (local, gitignored
— summary here for the committed record).

**Result: closed as inconclusive-by-construction**, per `plan.md` AT-P1.1's own
vocabulary — 30 dispatches / ~1.45M tokens / 5 independent trigger-construction
methods never established genuine base-case ambiguity for any tested pair, so no arm
comparison was ever scored. Claim 6 was **not** tested; this is not a null result.

**Owner decision:** proceed to the **P8 fallback** — linter + ratchet + top-decile
pass only, per `plan.md`'s own P2 conditionality rule (`G-P2.3`: the preservation
apparatus is built only if P1 earned it; the linter half is built regardless). The
preservation apparatus (category budgets, IDF guard, exemplar bank, 100%-human-review)
is not built. Formal claim-6 testing stays available if/when native `plugin eval`
access is confirmed — the pilot's pre-registrations and trigger examples are reusable
inputs for that future attempt.
