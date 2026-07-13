---
name: plan-the-research-study
description: "Frame a fuzzy research ask into a researchable question, run the research-theater gate (is this a real question or a decision already made?), select the method (generative/evaluative, qual/quant, attitudinal/behavioral, moderated/unmoderated) from the question rather than the reverse, size the sample to the claim it must bear (directional ~5 vs statistically-powered), plan the recruit/screener/incentive/panel, set the informed-consent + data-minimization + de-identification + retention ethics plan, and tie every finding to the decision it informs. Reach for this when the ask is 'how should we study X?', 'run a study that confirms Y', 'how many participants and from where?', or 'what do we need for consent/PII?'. Used by `ux-research-lead` (primary)."
---

# Skill: plan-the-research-study

> **Invoked by:** `ux-research-lead` (primary). Consulted by `research-execution-and-synthesis-specialist` for feasibility (can the plan actually be run) before execution.
>
> **When to invoke:** "How should we study X?"; "run a study that confirms Y"; "which method?"; "how many participants and where from?"; "what do we need for consent/PII?"; any move to stand up a study.
>
> **Output:** a researchable question + a method call (with what it cannot answer) + a sample/recruit + a consent/PII plan, all tied to the decision it informs, captured in the research plan template.

## Procedure

1. **Run the research-theater gate FIRST.** Traverse [`../../knowledge/ux-research-decision-tree.md`](../../knowledge/ux-research-decision-tree.md) Tree C: is there a genuine open question, or is the decision already made and someone wants cover? If it's decided, name it — kill the study or reframe it into a real question. A study that only confirms a made decision burns budget and credibility.
2. **Reframe the ask into a researchable question.** "Do users like it?" / "Is it good?" are not researchable. Convert to a specific, answerable question ("where do first-time users abandon checkout, and why?"). State **the decision it informs** — an insight with no decision attached is trivia, so if no decision hangs on it, stop.
3. **Select the method from the question** via Tree A — never the reverse. Generative (why/what — interviews, diary studies, field) vs evaluative (does-it-work — usability tests); qualitative (why/how) vs quantitative (how-many/how-much — surveys, analytics); attitudinal (what they say) vs behavioral (what they do); moderated vs unmoderated. Name **what the chosen method CANNOT answer** (you can't A/B your way to "why", or interview your way to "how many").
4. **Size the sample to the claim** via Tree B. ~5 users is enough for **directional** usability discovery; a **statistic** needs a powered quant sample. Set the size the claim requires and state explicitly what that sample can and cannot support — never launder qual into quant.
5. **Plan the recruit.** Screener (criteria that match the real user, with anti-fraud/anti-professional-tester checks), panel/source, incentive, and scheduling cadence. Name ≥2 recruit sources before declaring a segment unreachable.
6. **Set the ethics & participant-PII plan BEFORE collecting anything** via Tree D: informed consent (purpose, recording, withdrawal), data minimization (collect only what the question needs), de-identification/anonymization, a **retention limit set now**, and extra care for sensitive populations. Capture in [`../../templates/research-plan.md`](../../templates/research-plan.md).
7. **State the seams and flip conditions.** The roadmap decision → `product-management`; visual/IA → `web-design`; A/B-at-scale → `experimentation-growth-engineering`; advanced stats → `data-science-research`. Name the 1-2 facts that would change the plan.

## Worked example

> User: "Leadership wants us to test the new dashboard to prove users love it before we ship. Can you run a study?"

- **Research-theater gate (Tree C):** "prove users love it" after the ship decision is made = theater. Reframe: the decision *is* made, so a "do they love it?" study is cover, not inquiry. Two honest paths: (a) if the ship is truly locked, run **evaluative usability** to *de-risk* it — find what will break for users so we fix it pre-launch (a real decision: what to fix); (b) if leadership will genuinely reconsider, frame a real comparative question.
- **Reframe (path a):** "Where do users fail or hesitate on the new dashboard's top 3 tasks, and how severe is each issue?" Decision it informs: **which issues block launch vs ship-and-iterate.**
- **Method (Tree A):** evaluative, qualitative, behavioral, moderated usability test — because the question is "does it work and why does it fail", which A/B and surveys cannot answer. It *cannot* tell us "what % of all users love it" — that's a separate quant question, don't conflate.
- **Sample (Tree B):** 5-8 target users per key segment — **directional**, enough to surface most severe usability issues, not a satisfaction statistic.
- **Ethics/PII (Tree D):** consent covering screen + audio recording, collect no more than task performance + role, de-identify (P1..P8), delete recordings after synthesis + 90 days.
- **Seam:** the ship/no-ship and roadmap call is `product-management`'s; we inform it, we don't make it.

## Guardrails

- The **research-theater gate runs first** — never stand up a study whose answer is already decided; kill or reframe it.
- **Method follows the question**, never the reverse — naming the method before the question is the tell of a reflex study.
- **Sample is sized to the claim** — ~5 is directional, a statistic needs power; state what the sample cannot support, never launder qual into quant.
- **Every question names the decision it informs** — no decision, no study (it's trivia).
- **Ethics/PII plan is set BEFORE collection** — consent, minimize, de-identify, retention limit; sensitive populations get extra care.
- **Recruit real users** — screen out professional testers and fraud; name ≥2 sources before calling a segment unreachable.
- The **roadmap decision, the visual design, A/B-at-scale, and advanced stats leave this layer** — route to `product-management` / `web-design` / `experimentation-growth-engineering` / `data-science-research`.
- Method benchmarks and tooling facts carry a **retrieval date** and are re-verified before a stakeholder commitment. See [`../../knowledge/ux-research-patterns-2026.md`](../../knowledge/ux-research-patterns-2026.md).
