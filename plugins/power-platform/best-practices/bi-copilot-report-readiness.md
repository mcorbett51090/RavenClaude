# Ground the semantic model for AI before relying on Power BI Copilot

**Status:** Pattern/Absolute — a semantic model that will be consumed through Power BI **Copilot** (report narratives, "answer a question about the data", page generation, DAX-query assist) must be **grounded for AI** before Copilot is relied on for real reporting. An ungrounded model produces generic, thin, or confidently-wrong Copilot output even when the model is functionally correct. Grounding the model — not redesigning visuals — is the fix.

**Domain:** Power BI / Fabric semantic models · Copilot for Power BI

**Applies to:** `power-bi-engineer` (primary), `power-platform-tester` (validates that grounding actually changed Copilot output), any agent asked "why are our Copilot reports generic / unhelpful?"

> **The one-line diagnosis:** Copilot report quality is a function of how well the **semantic model is grounded for AI**, not of the report visuals. If Copilot output is weak, reach for the grounding layers below — not the visual canvas.

---

## Why this exists

Microsoft is explicit: *"Model owners need to invest in prepping their data for AI… Without this prep, Copilot can struggle to interpret data correctly — leading to generic, inaccurate, or even misleading outputs"* ([Copilot for Power BI overview](https://learn.microsoft.com/power-bi/create-reports/copilot-introduction), retrieved 2026-06-04). A correct star schema with clean DAX is necessary but **not sufficient**: Copilot still has to guess the model's purpose, which metric the team means by an ambiguous word, what named business periods mean, and what a good answer looks like. Every one of those guesses is a grounding gap the author can close.

This is the AI-consumption complement to [`enforce-measure-metadata.md`](enforce-measure-metadata.md): that rule grounds the **field level** (description/format/folder); this rule grounds the **model level** (purpose, terminology, verified answers, schema scope) and names the product feature that carries it.

---

## The four grounding layers (apply in this order)

Power BI's **Prep data for AI** feature (Home ribbon → *Prep data for AI*, in Desktop and the service) plus the **Approved for Copilot** setting are the supported mechanism. Author in **Microsoft's recommended order** — each layer narrows what the next has to fix ([Prep-data-for-AI FAQ](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-faq), retrieved 2026-06-04):

| # | Layer | Fixes the symptom | Saved at | Hard limit |
|---|---|---|---|---|
| 1 | **AI data schema** | Copilot reaches for the wrong field / reasons over noise | Semantic model | Deselect only |
| 2 | **Verified answers** | A specific recurring question is answered inconsistently | Semantic model | 250/model · 15 triggers each · 500 chars/trigger · 10 filter permutations |
| 3 | **AI instructions** | Missing goal, terminology, or priority context | Semantic model | **10,000 characters**; model-level only |
| 4 | **Descriptions + synonyms** | Similar fields can't be told apart by name | Model objects | — |
| → | **Approved for Copilot** | Removes the standalone-Copilot friction treatment | Model setting | Author after 1–4 test clean |

1. **AI data schema — deselect, don't add.** Remove surrogate keys, sort-helper columns, audit/ETL columns, and shadow measures so Copilot focuses on the house metric. The classic failure this fixes: a user asks for "sales", Copilot returns `Total GPM` (a legitimate reading), but the team means `Net Revenue` — deselect the shadow measure and the ambiguity disappears.
2. **Verified answers — pin the trusted visual.** For a recurring or nuance-prone question, build the visual that answers it correctly, then *Set up a verified answer* with trigger phrases. Matching is exact **or semantic** (synonyms, reordered words, added filters match; **swapping the measure or a dimension does not**). **Not** supported on DirectQuery or local Composite; **web-only** for Direct Lake.
3. **AI instructions — the goal channel.** Free-text, model-level (≤10,000 chars), so every report on the model inherits it. State the model's **purpose**, map **user vocabulary → model fields**, and **define named terms Copilot can't infer** ("busy season = June–August"; "active = ordered in last 90 days"). Spend the character budget on **disambiguation**, not business prose — the one right measure per ambiguous word moves output most. Author it from [`../templates/power-bi-copilot-ai-instructions.md`](../templates/power-bi-copilot-ai-instructions.md).
4. **Descriptions + synonyms — the floor.** Copilot grounds on DAX, field properties (descriptions, data types, format strings), and synonyms. Every surviving table/column/measure needs a one-sentence description; add synonyms for the terms in the AI-instructions map; keep names unique, human-readable, consistently cased.

Then mark the model **Approved for Copilot** once it tests clean — this removes the friction treatment that warns users to double-check standalone-Copilot answers.

---

## Preconditions (verify before authoring)

- **Capacity:** paid Fabric **F2+** or Power BI Premium **P1+**; tenant admin *Users can use Copilot…* setting on; a [supported region](https://learn.microsoft.com/fabric/admin/region-availability); not a trial/free SKU or sovereign cloud. If this gate fails, no grounding helps — fix the gate first. `[volatile — re-verify; Microsoft ships capacity/region changes monthly]`
- **Q&A must be enabled** on the model, or the Prep-data-for-AI tabs are greyed out.

---

## Do

- **Treat "Copilot reports are generic" as a modeling task**, route it to `power-bi-engineer`, and apply the four layers — don't tweak visuals.
- **Author in Microsoft's order** (schema → verified answers → instructions → descriptions); skipping to instructions over a noisy schema wastes the character budget papering over ambiguity the schema layer removes for free.
- **Spend AI-instructions budget on disambiguation** — term→field maps and the one right measure per ambiguous word.
- **Test in the Copilot pane after every change** (in Desktop, close/reopen the pane to reload instructions; use the skill picker → *Answer data question*). Confirm the change actually altered the answer, and test the **known-wrong-interpretation** prompts, not just one happy path.
- **Mark Approved for Copilot only after it tests clean** — the badge is a quality signal to consumers, not a default.

## Don't

- **Don't rely on instructions to paper over a flat/ambiguous model.** Instructions are the last ~10%; fix naming, descriptions, and schema scope first.
- **Don't author per report.** AI instructions and verified answers save on the **semantic model** — every report inherits them. Author once per model.
- **Don't promise determinism.** Copilot is nondeterministic; grounding raises the floor and tightens the distribution, it doesn't pin one exact answer. Set that expectation with stakeholders.
- **Don't author verified answers on a DirectQuery or local Composite model** expecting them to work — they're unsupported there (Direct Lake is web-only). Reach for AI instructions + descriptions instead.
- **Don't quote capacity/region/billing rules from memory** — they're volatile; cite a this-session check or mark `[unverified]`.

---

## See also

- [`../templates/power-bi-copilot-ai-instructions.md`](../templates/power-bi-copilot-ai-instructions.md) — the fill-in-the-blanks authoring artifact for all four layers
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — the *"Copilot returns generic / wrong reports — which grounding layer"* decision tree
- [`enforce-measure-metadata.md`](enforce-measure-metadata.md) — the field-level grounding floor (description/format/folder triad)
- [`../skills/power-bi/SKILL.md`](../skills/power-bi/SKILL.md) — the Power BI skill (Copilot-readiness section)

---

## Provenance

Authored 2026-06-04 to fill the Copilot-readiness gap in the `power-platform` Power BI coverage (engineering-deep, AI-grounding-absent). Grounded against Microsoft Learn (retrieved 2026-06-04): [Prepare your data for AI](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai), [AI instructions](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-instructions), [Verified answers](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-verified-answers), [Prep-data-for-AI FAQ](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-faq), [Optimize your semantic model for Copilot](https://learn.microsoft.com/power-bi/create-reports/copilot-evaluate-data), [Copilot for Power BI overview](https://learn.microsoft.com/power-bi/create-reports/copilot-introduction). Codifies the house stance that Copilot quality is a modeling problem, not a visuals problem.

---

_Last reviewed: 2026-06-04._
