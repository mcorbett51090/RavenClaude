---
name: synthesize-research-into-insight
description: "Turn raw notes into evidence-weighted, bias-checked, prioritized, decision-ready insight — affinity/thematic analysis, keeping observation ('6 of 8 abandoned at step 3') strictly separate from interpretation ('because the CTA is unclear'), weighting each finding by evidence strength (n, consistency, behavioral vs attitudinal, directional vs conclusive), ranking by severity, actively seeking disconfirming evidence, and ending every insight in a prioritized recommendation tied to a decision. Guards against confirmation, recency, and availability bias. Reach for this when the ask is 'turn these notes/sessions into findings we can act on' or 'what did we actually learn?'. Used by `research-execution-and-synthesis-specialist` (primary), consulted by `ux-research-lead`."
---

# Skill: synthesize-research-into-insight

> **Invoked by:** `research-execution-and-synthesis-specialist` (primary). Consulted by `ux-research-lead`, who owns the question the synthesis must answer and the decision it feeds.
>
> **When to invoke:** "Turn these notes/sessions into findings"; "what did we actually learn?"; "synthesize the interviews/tests"; any move from raw data to insight.
>
> **Output:** an evidence-weighted, bias-checked, prioritized set of insights — observation separated from interpretation — each tied to a recommendation and a decision, captured in the findings report.

## Procedure

1. **Ingest and normalize the raw data.** Pull the clean capture (behavior lines and self-report lines kept separate) from [`run-usability-and-interview-sessions`](../run-usability-and-interview-sessions/SKILL.md). Traverse [`../../knowledge/ux-research-decision-tree.md`](../../knowledge/ux-research-decision-tree.md) for the synthesis and bias-guard rules.
2. **Affinity / thematic analysis.** Cluster observations into themes bottom-up (let themes emerge from the data, don't sort into pre-decided buckets — that's confirmation bias). Name each theme by what the data shows, not by the hypothesis you hoped to confirm.
3. **Keep observation and interpretation on separate lines — always.** For each finding: the **observation** ("6 of 8 participants abandoned at the shipping step") is data; the **interpretation** ("likely because the total cost first appears there") is a hypothesis. Never print them fused as one sentence — the reader must be able to challenge the inference.
4. **Weight by evidence strength.** For each finding record: how many participants, how consistent, **behavioral vs attitudinal** (what they did outweighs what they said), and **directional vs conclusive** (small-sample = directional signal, not proof). Never quote "3 of 5" as a percentage.
5. **Actively seek disconfirming evidence.** For each emerging theme, go looking for the participants/data that would *break* it. Confirmation bias is the house enemy; a theme that survived a disconfirmation pass is stronger. Check recency bias (the last session isn't the loudest signal) and availability bias (the vivid quote isn't the most representative).
6. **Rank by severity × evidence, and attach a decision.** Prioritize findings; every insight ends in a **prioritized recommendation tied to a specific decision**. An insight with no decision attached is trivia. Capture in [`../../templates/research-findings-report.md`](../../templates/research-findings-report.md).
7. **State evidence caveats and seams.** Say plainly what is directional vs conclusive. The roadmap prioritization of the recommendations → `product-management`; the visual/IA fix → `web-design`; significance-at-scale → `experimentation-growth-engineering`; advanced modeling → `data-science-research`.

## Worked example

> User: "We ran 8 moderated usability sessions on checkout. My notes say 'people hated it' and 'the button is the problem'. Write up the findings."

- **"People hated it" is an interpretation with no observation under it** — and "the button is the problem" is a conclusion, not data. Go back to the capture and separate:
  - **Observation:** 6 of 8 participants paused >20s and re-read the page at the shipping-cost step; 4 of those 6 clicked back to the cart. **Interpretation (hypothesis):** the first appearance of shipping cost at that step is the friction, not the button.
  - **Observation:** 3 of 8 said "I wasn't sure it went through" after submitting. **Interpretation:** the confirmation state is too weak.
- **Evidence weighting:** the shipping-step finding is **6/8, behavioral, consistent → strong directional signal** (still 8 users, not a statistic — report as directional, not "75%"). The confirmation-state finding is **3/8, attitudinal → weaker, worth a cheap fix + follow-up.**
- **Disconfirmation pass:** did any participant sail through the shipping step? 2 did — both were returning users with saved addresses. That *sharpens* the theme (it's a first-time/new-address problem) rather than breaking it.
- **Recency check:** the loudest complaint came from P8, the last session — but it's a 1-of-8 edge case; don't let its freshness inflate it above the 6/8 pattern.
- **Prioritized recommendations tied to decisions:** (P0) surface shipping cost earlier / on the cart page — decision: pre-launch blocker fix; (P1) strengthen the confirmation state — decision: fast-follow. Both directional; validate the shipping-cost fix with a follow-up test or an `experimentation-growth-engineering` A/B at scale.

## Guardrails

- **Observation and interpretation are never fused** — data on one line, the hypothesis it supports on another; the reader must be able to challenge the inference.
- **Every finding carries its evidence strength** — n, consistency, behavioral vs attitudinal, directional vs conclusive; **never quote a small sample as a percentage.**
- **Actively seek disconfirming evidence** — confirmation bias is the house enemy; a theme that survived a disconfirmation pass is the one you trust.
- **Guard recency and availability bias** — the last session and the vivid quote are not automatically the strongest signal; weight the whole corpus.
- **Themes emerge bottom-up** — don't sort data into pre-decided buckets.
- **Every insight ends in a prioritized recommendation tied to a decision** — an insight with no decision is trivia.
- **Small-sample findings are labeled directional, not proof** — say so explicitly.
- **Prioritization-into-roadmap, the design fix, significance-at-scale, and advanced modeling leave this layer** → `product-management` / `web-design` / `experimentation-growth-engineering` / `data-science-research`. Volatile facts carry a **retrieval date**. See [`../../knowledge/ux-research-patterns-2026.md`](../../knowledge/ux-research-patterns-2026.md).
