# Give the agent a verification signal it can read — the loop beats the prompt

**Status:** Pattern
**Domain:** Agent behavior / Verification discipline / Task framing
**Applies to:** `ravenclaude-core` (every agent and the Team Lead)

---

## Why this exists

An agent stops when the work **looks** done. Without a check it can run, "looks done" is the only signal it has — so every mistake waits for a human to notice it, and the human silently becomes the verification loop. The single highest-leverage move against that failure is **not** a cleverer prompt: it's handing the agent a check that returns a machine-readable **pass/fail** it can read back in the conversation. Then the loop closes on its own — the agent does the work, runs the check, reads the result, and iterates until the check passes. Claude Code's own creator estimates this is worth a **2–3× quality improvement**, and the official guide leads with it: *"the difference between a session you watch and one you walk away from."* `[verify-at-use — community-attributed 2-3× figure; the principle itself is in the primary doc cited below]`

This repo already ships the *enforcement leaves* of this idea — the definition-of-done Stop gate, the expensive-test front-load, the visual render→see→iterate loop, the adversarial reviewer — but no single rule names the **principle they all instantiate**: *every task should carry a verification signal the agent can read, and the agent should iterate to green before handing back.* Naming it is what lets an agent reach for the right leaf instead of shipping unverified work because "the tests weren't mentioned."

The trap this kills is the **trust-then-verify gap**: a plausible-looking implementation that doesn't handle the edge cases, handed back as "done" because nothing ever told the agent what "done" could be checked against.

## How to apply

**Construct (or demand) a check that emits a signal the agent can read in-conversation, then iterate against it.** The check is anything that returns pass/fail: a test suite, a build exit code, a linter, a script that diffs output against a fixture, or a screenshot compared to a design. If a task arrives with no verification signal, **the first move is to build the cheapest one that fits** — not to start coding blind.

Pick how hard the signal gates the stop, cheapest-first:

| Level | Mechanism | Reach for it when |
|---|---|---|
| **In-prompt** | Tell the agent to run the check and iterate in the same brief ("write the tests, run them, fix failures"). | Any task, today — zero setup. The default for a focused dispatch. |
| **Across a session** | A standing pass/fail condition re-checked every turn until it holds (`/goal`-style). | A multi-turn change where "done" is one stable, re-checkable condition. |
| **Deterministic gate** | A Stop hook runs the check as a script and blocks the turn from ending until it passes — see [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md). | Unattended / auto-mode runs where the agent must not be able to stop on red. |
| **Second opinion** | A fresh-context reviewer sub-agent tries to refute the result, so the agent doing the work isn't the one grading it. | The work ran unattended for a while and an independent check matters before counting it done. |

**Show the evidence, don't assert success.** The final report carries the test output, the command run and what it returned, or the screenshot — not "it works." Reviewing evidence is faster than re-running the verification, and it's the only honest report shape for a session nobody watched. (Reporting failures faithfully is the [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) floor — a check that came back red is reported red, with its output.)

**Do:**

- Treat a task with **no** verification signal as incomplete framing — construct the cheapest fitting check (a unit test, a `bash -n`, a fixture diff) *before* doing the work.
- Match the signal's cost to the task: an in-prompt "run the tests and iterate" for routine work; the Stop gate for unattended runs that must not stop on red.
- Hand the check the **criteria** — example inputs/outputs, the spec, the acceptance condition — so "did it pass?" has an objective referent.
- Put the evidence (command + output) in the handoff, every time.

**Don't:**

- Don't hand back a plausible-looking implementation as "done" when nothing checkable was ever run against it — that's the trust-then-verify gap.
- Don't reach for a deterministic Stop gate when an in-prompt "run it and iterate" would do; each level trades setup for attention, so spend the cheapest one that fits.
- Don't let the agent that wrote the code be the *only* grader on a long unattended run — a fresh-context refuter catches what self-review won't.
- Don't confuse "the check passed" with "the work is good" when the check is weak — a green linter is not a green test suite. The signal is only as strong as what it actually exercises.

## Edge cases / when the rule does NOT apply

- **Genuinely unverifiable output** (a judgement call, an open-ended exploration, prose with no acceptance criterion) — there's no pass/fail to construct. Say so honestly and surface the residue for human judgement rather than fabricating a hollow check. Abstention here is the [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) move, not a defect.
- **Expensive checks** (a human re-fire, a long run, a billed turn, a deploy) — the loop still applies, but *invert it*: front-load cheap static validation so each expensive run exercises an already-validated change. That's its own rule — [`./expensive-test-front-loading.md`](./expensive-test-front-loading.md).
- **Pure read-only / research sessions** — no artifact changes, so there's nothing to verify-and-iterate; the discipline is dormant.
- **A reviewer is not a verification signal you must chase to zero.** A gap-finding seat manufactures findings; scope it to correctness and triage its output — [`./scope-the-reviewer-to-correctness-or-it-manufactures-work.md`](./scope-the-reviewer-to-correctness-or-it-manufactures-work.md).

## See also

- [`./definition-of-done-gate-makes-done-mean-done.md`](./definition-of-done-gate-makes-done-mean-done.md) — the **deterministic** instance of this principle: a Stop hook that blocks the turn until the check passes.
- [`./expensive-test-front-loading.md`](./expensive-test-front-loading.md) — the **cost-management** variant: when the check is expensive, validate exhaustively first so each run counts.
- [`../knowledge/visual-feedback-loop.md`](../knowledge/visual-feedback-loop.md) — the **visual** instance: render→see→critique→iterate against objective stopping signals for visual-output agents.
- [`./scope-the-reviewer-to-correctness-or-it-manufactures-work.md`](./scope-the-reviewer-to-correctness-or-it-manufactures-work.md) — the **second-opinion** instance, scoped so it doesn't invent work.
- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — report the evidence, including red checks; abstain honestly when there's nothing to verify against.

## Provenance

Distilled from a 2026-07-02 scan of Claude Code community discussion (r/ClaudeAI + practitioner write-ups aggregating it — the "verification beats prompting" thread is the most-cited workflow lesson), cross-checked against [Anthropic's Claude Code best-practices guide](https://code.claude.com/docs/en/best-practices) § "Give Claude a way to verify its work" (fetched this session), whose four enforcement levels — in-prompt, `/goal` condition, Stop hook, second-opinion subagent — map exactly onto the four leaves this repo already ships. The repo had the leaves (`definition-of-done-gate`, `expensive-test-front-loading`, the visual-feedback-loop knowledge file, `scope-the-reviewer`) but **no consumer-facing rule naming the umbrella principle** that an agent should always carry a readable verification signal and iterate to green — this closes that gap. (The internal architecture doc [`docs/autonomous-guardrails-research-2026-05-29.md`](../../../docs/autonomous-guardrails-research-2026-05-29.md) § "Layer 5 — verification + termination" frames the *guardrail-enforcement* angle; this rule is the *task-framing* companion.) The community-attributed 2–3× figure is marked `[verify-at-use]`; the principle is grounded in the primary doc. Research + panel record: [`docs/research/2026-07-02-claude-subreddit-scan-verification-loop/README.md`](../../../docs/research/2026-07-02-claude-subreddit-scan-verification-loop/README.md).

---

_Last reviewed: 2026-07-02 by `claude`_
