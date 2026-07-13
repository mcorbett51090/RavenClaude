---
name: run-usability-and-interview-sessions
description: "Design and run the study without contaminating it — protocol & task design (goal-based tasks, not step instructions), think-aloud and non-leading moderation (open probes, silence, 'tell me more' — never 'was that easy?'), usability-test instrumentation (task-success criteria + severity ratings), survey design that avoids leading, double-barreled, and social-desirability-loaded items, and clean data capture that keeps what participants DID separate from what they SAID. Reach for this when the ask is 'write the protocol/tasks', 'moderate this interview without leading', or 'design/fix this survey'. Used by `research-execution-and-synthesis-specialist` (primary)."
---

# Skill: run-usability-and-interview-sessions

> **Invoked by:** `research-execution-and-synthesis-specialist` (primary). Consulted by `ux-research-lead` for plan feasibility (can the method actually be run as scoped).
>
> **When to invoke:** "Write the protocol and tasks"; "moderate this interview/test"; "how do I ask this without leading them?"; "design/review this survey"; any move to build or run the instrument.
>
> **Output:** a protocol + goal-based tasks + a non-leading moderation script, or a bias-audited survey instrument, with clean-capture rules that separate behavior from self-report.

## Procedure

1. **Anchor to the plan's question and method.** Read the research-lead's plan ([`../../templates/research-plan.md`](../../templates/research-plan.md)) — the instrument must execute *that* question at *that* rigor, not a new one. Traverse [`../../knowledge/ux-research-decision-tree.md`](../../knowledge/ux-research-decision-tree.md) for the method's craft rules.
2. **Design tasks goal-based, not instruction-based.** "Buy a size-M blue jacket and get it shipped to your home" (goal) — never "click Add to Cart, then click Checkout" (which tests reading, not usability). Order tasks realistically; avoid tasks that leak the answer.
3. **Write a think-aloud + non-leading moderation script.** Open the session with warm-up + consent confirmation; prompt think-aloud ("say what you're thinking as you go"); use neutral probes ("tell me more", "what were you expecting there?", silence). Ban the leading forms: "was that easy?", "you liked that, right?", "most people click here — did you?". A leading question manufactures the finding it "discovers".
4. **Instrument usability for signal.** Define **task success** up front (binary pass/fail, or graded with partial), and a consistent **severity scale** (e.g. 0 cosmetic → 4 catastrophic/blocker). Capture time/errors/paths as behavior; capture verbatims separately as self-report.
5. **Design or audit surveys against the four quiet killers.** Leading items ("How much did you enjoy our excellent new design?"), double-barreled items ("Was the app fast and easy?" — two questions), social-desirability loading, and sampling bias (who is and isn't in the frame). Rewrite each to neutral, single-barreled; state the sample's limits.
6. **Capture clean data.** Keep **observation and self-report on separate lines** from the moment of capture — "P3 clicked back twice" (did) vs "P3 said it felt slow" (said). Timestamp, tag to participant ID (de-identified), and store per the plan's retention limit.
7. **Hand off to synthesis and name the seams.** Feed the capture to [`synthesize-research-into-insight`](../synthesize-research-into-insight/SKILL.md). Significance-at-scale → `experimentation-growth-engineering`; advanced modeling → `data-science-research`.

## Worked example

> User: "Here's our post-launch survey — 'How much do you love the fast, intuitive new checkout? (1-5)'. Everyone scores us 4-5. Why?"

- **The item manufactures its own answer.** It is **leading** ("love", "fast, intuitive" pre-loads the verdict) *and* **double-barreled** (fast AND intuitive — a user who finds it fast but confusing can't answer honestly) *and* **social-desirability-loaded** (few people rate down a friendly-sounding product to its maker).
- **Sampling bias too:** a post-*completion* survey only reaches users who *finished* checkout — everyone who abandoned (the people with the real problem) is structurally excluded. The 4-5 skew is an artifact of the frame, not a finding.
- **Rewrite:** split into single-barreled, neutral items — "How easy or difficult was completing checkout?" (1 = very difficult … 5 = very easy) and a separate "How fast or slow did checkout feel?"; add an open "What, if anything, was frustrating?". Sample abandoners via a separate intercept, not just completers.
- **Rigor note:** even fixed, a satisfaction survey tells you *how many/how much* attitudinally — to learn *why* users abandon, pair it with moderated usability (behavioral), because a survey can't answer "why".
- **Seam:** if the team wants a statistically-significant A/B of two checkout flows at scale, that's `experimentation-growth-engineering`.

## Guardrails

- **Tasks are goal-based, never step-by-step** — instruction-following isn't usability.
- **The moderator does not lead** — think-aloud, open probes, and silence; ban "was that easy?"/"you liked that, right?". The cleanest session is the one where you barely spoke.
- **Survey items are single-barreled and neutral** — no leading, no double-barreled, no social-desirability loading; a question that contains its answer yields worthless data.
- **Sampling bias is checked at design time** — name who the frame excludes (e.g. surveying only completers).
- **Observation and self-report are captured on separate lines** — what they DID is not what they SAID.
- **Success and severity are defined before the session**, not rationalized after.
- **Data capture respects the plan's consent + retention limit** — de-identified participant IDs, no over-collection.
- **Significance-at-scale and advanced modeling leave this layer** → `experimentation-growth-engineering` / `data-science-research`. Method/tool facts carry a **retrieval date**. See [`../../knowledge/ux-research-patterns-2026.md`](../../knowledge/ux-research-patterns-2026.md).
