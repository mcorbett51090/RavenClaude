# Scope a review seat to correctness — a gap-finding reviewer always finds gaps

**Status:** Pattern
**Domain:** Multi-agent review / panels & tribunals / agent-prompt design
**Applies to:** `ravenclaude-core` (any panel, tribunal seat, or reviewer sub-agent the Team Lead convenes)

---

## Why this exists

This repo runs **review by panel everywhere** — the command-review tribunal (Forseti/Mímir/Heimdall/Thor seats), `decision-review`, `two-panel-plan-review`, the `code-review` skill in a fresh sub-agent, `agent-dispatch-evaluator`, the accuracy panels. Every one of those is a model **asked to find problems**. That framing has a built-in bias that is easy to miss: **a reviewer prompted to find gaps will report some, even when the work is sound — because reporting gaps is the task it was given.** A blank report *feels* like the reviewer failed to do its job, so it manufactures findings to look diligent.

The cost is not the noise itself — it's what an obedient implementing agent does with it. It treats every finding as a defect to fix and **over-engineers**: extra abstraction layers, defensive code for inputs that can't occur, tests for impossible states, "just in case" config knobs. Each fix looks like progress and each one adds surface area, and the diff drifts away from the actual requirement into a reviewer's wish-list. In an unattended run (the place this repo leans hardest on panels) there's no human to say "that one doesn't matter" — so the gap-inflation compounds unchecked.

The rule needs to be named because the fix is **counter-intuitive**: you don't get a better review by asking for a more thorough one. You get a better review by **telling the reviewer what counts as a finding** — and by telling the implementer that not every finding must be chased.

## How to apply

**Set the bar in the review prompt, on both sides of the seat.**

| Side | Instruction that closes the gap-inflation loop |
|---|---|
| **The reviewer's prompt** | "Flag only gaps that affect **correctness** or a **stated requirement**. Style, taste, and speculative hardening are out of scope — say *no blocking findings* when that's the truth." A clean pass must be an allowed, expected outcome. |
| **The implementer's handling** | Triage findings before acting: a correctness/requirement gap → fix; a taste/speculative one → note and move on. "The reviewer raised it" is **not** sufficient reason to change code. |
| **The criteria handed to the seat** | Name what the work is checked **against** — the spec, the plan, the acceptance test. A reviewer with no bar invents one; a reviewer pointed at `PLAN.md` measures against it. |

**Do:**

- Give every review seat an explicit **scope of finding** ("correctness + stated requirements") and an explicit **permission to pass clean**. This is the single highest-leverage line in a reviewer prompt.
- Point the reviewer at the **criteria** (spec / plan / requirement list), so "is this a gap?" has an objective referent instead of the reviewer's appetite.
- Keep the **fresh-context** value of the reviewer (it should see the diff and the criteria, not the reasoning that produced the change) — that independence is real and worth preserving; this rule sharpens *what* it reports, not *whether* to review.
- In a **panel**, let the confidence/abstain machinery carry "nothing to flag" — an honest abstain or a clean ALLOW is a valid verdict, not a seat that under-performed.

**Don't:**

- Don't prompt a reviewer to "find everything that could be improved" / "be maximally thorough" and then treat its output as a defect list. That phrasing *guarantees* a non-empty list regardless of the work's quality.
- Don't let an implementing agent auto-apply review findings. Chasing every one is how a tight diff turns into an over-abstracted one; the reviewer flags, the implementer **decides**.
- Don't read a clean review as a failed review. If a seat can never come back empty, it isn't measuring quality — it's measuring its own instruction to produce findings.
- Don't confuse this with lowering the bar on **security/correctness** floors — those findings are exactly the ones that *are* in scope and *do* gate. This rule narrows speculative gaps, never the hard floor.

## Edge cases / when the rule does NOT apply

- **Security and high-blast review.** The command-review tribunal's `security_deny` floor, force-push/`curl|sh` hard-denies, and injection screens are **not** speculative findings — they bind regardless. This rule scopes the *judgment* seats (taste, "could be cleaner," defensive-coding suggestions), never the deterministic safety floor.
- **Explicit exploratory asks.** "What would you improve here?" is a deliberately open prompt — useful when you *want* the wish-list to think with. The anti-pattern is only when that open framing is fed into an unattended fix loop that treats the output as mandatory.
- **A genuinely thin spec.** If the reviewer keeps surfacing real ambiguities, the gap may be in the *criteria*, not the reviewer — tighten the spec (see `focused-task-delegation-beats-full-context-dumps.md`) rather than muting the seat.

## See also

- [`./structured-output-protocol-for-all-agent-handoffs.md`](./structured-output-protocol-for-all-agent-handoffs.md) — the handoff envelope a reviewer's scoped findings ride back in (`status` / `risks` / `next_actions`).
- [`./focused-task-delegation-beats-full-context-dumps.md`](./focused-task-delegation-beats-full-context-dumps.md) — give the seat the criteria (spec/plan), not the full history; a reviewer with a clear bar doesn't invent one.
- [`./command-review-when-to-enable.md`](./command-review-when-to-enable.md) — the tribunal whose judgment seats this rule scopes (and whose security floor it deliberately leaves untouched).
- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the Last-Mile ceiling ("finish the automatable work") read alongside this rule's floor ("don't manufacture work to finish").

## Provenance

Distilled from a 2026-06-15 scan of Claude Code community discussion (r/ClaudeAI + practitioner write-ups on adversarial-review skills) cross-checked against [Anthropic's Claude Code best-practices guide](https://code.claude.com/docs/en/best-practices) § "Add an adversarial review step", whose own callout states it plainly: *"A reviewer prompted to find gaps will usually report some, even when the work is sound… Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional."* The repo ships a deep **review** stack (tribunal, two-panel review, code-review, dispatch-evaluator) but no consumer-facing rule on **how to scope a review seat so it doesn't manufacture work** — this closes that gap. Research + panel record: [`docs/research/2026-06-15-claude-subreddit-scan/README.md`](../../../docs/research/2026-06-15-claude-subreddit-scan/README.md).

---

_Last reviewed: 2026-06-15 by `claude`_
