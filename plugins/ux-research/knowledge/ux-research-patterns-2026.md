# Knowledge — UX-research patterns (2026)

> **Last reviewed:** 2026-07-13 · **Confidence:** High on the durable concepts (the method matrix, moderation & survey best practices, the bias catalog and its counters, evidence-strength framing, research-ops/repository patterns, the research-ethics/PII discipline); **Medium on the dated tooling map — research-platform/panel names, features, and pricing are volatile and carry retrieval dates below.**
> The reference the two agents read when planning, running, and synthesizing research: the method matrix, how to moderate and write surveys without contaminating the data, the bias catalog and its counters, how to frame evidence strength honestly, the research-ops substrate, and a 2026 tooling snapshot.

The team's discipline: **research-theater gate first; method follows the question; sample follows the claim; observation stays separate from interpretation; participant data is PII from first contact; small samples are directional, not statistics; every insight ends in a decision.**

---

## The method matrix

The two orienting axes every method sits on, plus the two cross-cuts:

| | **Qualitative** (why / how) | **Quantitative** (how many / how much) |
|---|---|---|
| **Generative** (discover the problem) | Interviews, contextual inquiry, diary studies, open card sorts | Surveys, analytics, quant card sorts, desirability studies |
| **Evaluative** (assess the solution) | Moderated usability tests, think-aloud, concept tests | Unmoderated usability at scale, A/B tests, tree tests, benchmark studies |

**Cross-cut 1 — attitudinal vs behavioral:** attitudinal = what people *say* (interviews, surveys); behavioral = what people *do* (usability tests, analytics, A/B). **Said ≠ did** — weight behavior heavier when they conflict.

**Cross-cut 2 — moderated vs unmoderated:** moderated buys depth and follow-up probing but carries observer effect and scale limits; unmoderated buys scale and natural context but no ability to ask "why did you do that?".

> The single most common failure is **method-first thinking** — reaching for the familiar method (usually a survey or "let's do some interviews") before the question is framed. Method follows the question, every time.

---

## Framing the researchable question

- **Fuzzy asks are not researchable.** "Do users like it?", "Is it good?", "Should we build X?" have no knowable answer. Convert to a specific question with an observable answer and a decision behind it.
- **The decision test:** for every proposed question, name the decision that changes based on the answer. No decision → it's trivia, don't run it.
- **Question → hypothesis (where appropriate):** a generative study opens the space (no hypothesis needed); an evaluative study often has one ("first-time users will fail task 2") — state it so the study can disconfirm it, not just confirm it.

---

## Moderation best practices (the moderator's job is to NOT lead)

- **Think-aloud protocol** — ask participants to narrate their thinking; it surfaces mental models without the moderator injecting them.
- **Neutral, open probes** — "tell me more", "what were you expecting there?", "walk me through what you're thinking", and **silence** (the most underused tool). Let the pause do the work.
- **Ban the leading forms** — "was that easy?", "you liked that, right?", "most people click here — did you?", "don't you think…". Each pre-loads the answer and manufactures the finding.
- **Separate the task from the interview** — during a task, stay quiet and observe; probe *after*, so you don't contaminate the behavior you're measuring.
- **Watch the observer effect** — participants perform for the moderator; behavioral + unmoderated data corrects for it.

## Survey best practices (a bad item is a fabricated statistic)

- **Single-barreled items** — one question per item. "Was it fast and easy?" is two questions wearing one; split them.
- **Neutral, non-leading wording** — strip loaded adjectives ("our excellent new design"); a neutral scale ("very difficult … very easy").
- **Guard social-desirability** — people flatter the maker; use neutral framing, avoid first-person-maker phrasing, and prefer behavioral questions where possible.
- **Balanced scales & response options** — symmetric labels, a considered midpoint decision, and mutually-exclusive/exhaustive options.
- **Sampling frame honesty** — name who the frame excludes. A post-completion survey never hears from abandoners; an email-list survey never hears from churned users.
- **Sample for the claim** — a survey makes a *statistic*, so it needs a representative, powered sample; a convenience sample yields directional signal only, and must say so.

---

## Evidence strength — framing findings honestly

Every finding carries its weight, stated explicitly:

| Dimension | Stronger | Weaker |
|---|---|---|
| **Sample size / consistency** | Many participants, consistent | Few, mixed |
| **Behavioral vs attitudinal** | Observed behavior | Self-reported attitude |
| **Directional vs conclusive** | Powered quant → conclusive | Small qual → **directional signal only** |
| **Triangulation** | Multiple methods agree | Single method, single source |
| **Disconfirmation** | Survived a hunt for counter-evidence | Never stress-tested |

- **Never quote a small qualitative sample as a percentage** — "4 of 5 participants" is directional; "80% of users" is a fabricated statistic. This is the cardinal rigor sin.
- **Separate observation from interpretation on the page** — "6 of 8 abandoned at step 3" (observation) vs "because the CTA is unclear" (interpretation/hypothesis). The reader must be able to challenge the inference.

---

## The bias catalog and its counters

| Bias | What it does | Counter |
|---|---|---|
| **Confirmation** | You see what confirms the pre-decided answer | Themes emerge bottom-up; **actively seek disconfirming evidence** |
| **Leading** | The question supplies its own answer | Open/neutral phrasing; think-aloud + silence; single-barreled items |
| **Sampling** | The frame systematically excludes people who matter | Screen to the real user; name who's excluded (e.g. only completers) |
| **Recency** | The last session dominates the write-up | Weight the whole corpus, tag findings by frequency across sessions |
| **Social-desirability** | Participants flatter the maker | Neutral framing; behavioral over self-report; independent-feeling moderation |
| **Availability** | The vivid quote feels representative | Weight by frequency/consistency, not memorability |

> The two house enemies are **confirmation bias in synthesis** and **leading questions in moderation** — one contaminates the read, the other contaminates the collection. Guard both by name in every study.

---

## Research operations & the repository

- **Recruiting & panels** — a screener that matches the *real* user, anti-fraud/anti-professional-tester checks, and ≥2 recruit sources so a single dry panel doesn't stall the study. Incentives sized fairly and paid reliably (a reputation asset).
- **Cadence** — a repeatable rhythm (e.g. a standing research sprint, a continuous-discovery interview cadence) so research is a habit, not a heroic one-off.
- **The research repository** — a searchable, tagged store of studies, evidence, and insights so findings **compound** instead of evaporating. Tag by product area, method, and evidence strength; link insight → the decision it informed. A repository that no one can search is a graveyard.
- **Democratization with guardrails** — non-researchers can run lightweight studies *if* the method/bias/ethics guardrails travel with the templates; ungoverned "everyone does research" reintroduces every bias this discipline exists to prevent.

---

## Research ethics & participant-PII discipline

- **Informed consent** — before any recording or collection: purpose, what's recorded, how it's used, that participation is voluntary and withdrawable. No recording without it.
- **Data minimization** — collect only what the research question needs; every extra field is a liability, not an asset.
- **De-identification / anonymization** — key data to participant IDs (P1..Pn), strip direct identifiers from stored findings, and never share raw PII in a report.
- **Retention limits** — set a deletion date **before** collecting; delete raw recordings/PII on schedule, retain only de-identified findings.
- **Sensitive populations & topics** — minors, health, vulnerable groups, and protected data get heightened consent (guardian where relevant), extra minimization, and ethics review where applicable.
- **The rule:** participant data is PII from first contact — the ethics plan is set *before* recruiting, never bolted on after.

---

## 2026 research tooling map (dated — volatile, re-verify before quoting)

- **Usability testing / research platforms** — moderated + unmoderated testing, recruiting panels, and analysis tooling exist across several vendors (e.g. UserTesting, Maze, Lookback, Dovetail-style analysis/repository tools, and others); specific feature sets, panel quality, and pricing are volatile. _(Retrieved 2026-07-13.)_
- **Survey tools** — general survey platforms (Qualtrics, Typeform, Google Forms, and others) differ in logic, sampling, and analysis depth; match the tool to the sampling rigor the claim needs. _(Retrieved 2026-07-13.)_
- **Research repositories** — dedicated repository/insight-management tools tag and make studies searchable so findings compound; adoption and features evolve fast. _(Retrieved 2026-07-13.)_
- **Recruiting panels** — panel providers vary widely in quality, fraud controls, and reach; always screen, and never trust a panel's self-description over a screener. _(Retrieved 2026-07-13.)_
- **AI-assisted analysis** (adjacent) — automated transcription, tagging, and theme-suggestion tools speed synthesis but **reintroduce confirmation/availability bias if trusted uncritically** — treat AI clusters as a first pass a human must challenge, not a finding. _(Retrieved 2026-07-13.)_

> **Volatile:** research-platform features, panel quality, repository tooling, and pricing change frequently; AI-analysis capabilities are moving fast. Treat the map above as a 2026-07 snapshot and re-verify with `ravenclaude-core/deep-researcher` before a stakeholder or vendor commitment.

---

## Provenance

- Durable concepts (the method matrix, the generative/evaluative + qual/quant + attitudinal/behavioral + moderated/unmoderated framing, moderation & survey best practices, the bias catalog, evidence-strength framing, observation-vs-interpretation, research-ops/repository patterns, and the research-ethics/PII discipline) are consensus practice across the UX-research literature (Nielsen Norman Group; the *Just Enough Research*, *Interviewing Users*, *Measuring the User Experience*, and *Rocket Surgery Made Easy* lineage; standard human-subjects/research-ethics guidance), reviewed 2026-07-13 — **High confidence**.
- The tooling/panel map is a **2026-07 snapshot**; product features, panel quality, and pricing are volatile and carry the retrieval dates above — re-verify before pinning in a deliverable.
