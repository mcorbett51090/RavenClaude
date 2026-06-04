# Power BI Copilot — AI Instructions & Description Template

**Fill-in-the-blanks template for telling Power BI Copilot what the model is _for_.** Drop a copy next to a semantic model (or paste each block into the product surface noted), replace every `<…>` placeholder, delete the guidance call-outs, and you have the goal/domain/quality context Copilot needs to stop producing generic reports.

**Why this exists:** Copilot report quality is a function of how well the **semantic model is grounded for AI**, not of the report visuals. A well-modeled star schema with no AI context still yields thin, generic narratives because Copilot has to _guess_ the goal, the preferred metric, and what "good" looks like. This template is the goal-statement channel. It is the authoring artifact behind Power BI's **Prep data for AI** feature (Home ribbon → **Prep data for AI**, next to the Copilot button — in both Desktop and the service).

> **Owners:** `power-bi-engineer` (primary), `power-platform-tester` (validates that authored instructions actually change Copilot output). Companion to [`../best-practices/enforce-measure-metadata.md`](../best-practices/enforce-measure-metadata.md) (the description/format/folder triad that grounds the field-level layer) and the [`../skills/power-bi/`](../skills/power-bi/SKILL.md) skill.

---

## Where each block goes (and the hard limits)

Author in this order — it is **Microsoft's recommended implementation sequence**, not arbitrary (source: [Prep-data-for-AI FAQ](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-faq#in-what-order-should-i-implement-copilot-in-power-bi-tooling-features), retrieved 2026-06-04):

| # | Block | Product surface | Saved at | Hard limit |
|---|---|---|---|---|
| 1 | **AI data schema** (§5) | Prep data for AI → *Define AI data schema* | Semantic model | — (deselect, don't add) |
| 2 | **Verified answers** (§4) | Select a visual → `…` → *Set up a verified answer* | Semantic model | 250 / model · 15 triggers each · 500 chars/trigger · 10 filter permutations |
| 3 | **AI instructions** (§1) | Prep data for AI → *Add AI instructions* | Semantic model | **10,000 characters total** |
| 4 | **Descriptions** (§2, §3, §6) | Model/report Settings + field properties | Model & report objects | — |

**Preconditions (verify before authoring — these silently disable the tabs):**

- **Q&A must be enabled** on the model, or the Prep-data-for-AI tabs are greyed out.
- **Capacity:** paid Fabric **F2+** or Power BI Premium **P1+**; the *Users can use Copilot…* admin setting on; a [supported region](https://learn.microsoft.com/fabric/admin/region-availability); not a trial/free SKU or sovereign cloud.
- **Verified answers** are **not** supported on DirectQuery or local Composite models, and are **web-only** for Direct Lake. AI instructions + descriptions work regardless of storage mode.

After authoring, mark the model **Approved for Copilot** (model → Settings → *Approved for Copilot*) to remove the standalone-Copilot friction treatment. Changes can take up to ~1 hour (24 h with many attached reports) to propagate.

> **Set expectations:** Copilot is **nondeterministic** — the same prompt + same grounding can return different output. These blocks raise the floor and tighten the distribution; they do not pin a single exact answer.

---

## 1. AI instructions  *(the goal channel — ≤ 10,000 chars, model-level)*

> Paste the filled block below into **Prep data for AI → Add AI instructions**. Unstructured natural-language guidance the LLM interprets. Use it to: state the model's purpose, **map user vocabulary → model fields**, **define named business terms** Copilot can't infer, and say which metric/grain to prefer. It does **not** modify theming/visuals and can't disable other Copilot features.

```text
PURPOSE
This model exists to answer: <the 1–2 core business questions this model is the source of truth for>.
Primary audience: <who asks — e.g. regional sales managers, CS leadership, regulators>.
Decisions it drives: <what action a good answer should enable>.

DEFAULT INTERPRETATION (apply unless the user overrides)
- When the user says "<ambiguous word, e.g. sales>", they mean the measure [<exact measure, e.g. Net Revenue>], NOT [<the wrong-but-plausible measure, e.g. Gross Sales / GPM>].
- Default time grain: <e.g. month>. Default period: <e.g. last 12 complete months>.
- Currency: <e.g. GBP>, displayed as <e.g. £#,##0>. Do not mix currencies in one visual.
- Default segmentation: <e.g. by Region, then Product Category>.
- Prefer these measures when several could apply: <ranked list of the "house" measures>.

BUSINESS TERMINOLOGY (terms not present anywhere in the schema)
- "<term, e.g. busy season>" = <definition, e.g. June through August inclusive>.
- "<term, e.g. active customer>" = <definition, e.g. ordered in the last 90 days>.
- "<acronym>" = <expansion + which field/measure it maps to>.

WHAT A GOOD ANSWER LOOKS LIKE
- Lead with <e.g. the headline KPI vs. its prior-period and target>, then the top <N> drivers.
- Always show <e.g. a period-over-period comparison> for trend questions.
- Use <e.g. % of total> when the user asks about composition/mix.
- Round to <e.g. whole £ for currency, 1 decimal for %>.

WHAT TO AVOID / EXCLUDE
- Do not use [<deprecated/internal measure>] — it is <reason, e.g. pre-restatement>.
- Exclude <e.g. test accounts where Account Type = "Internal"> from totals.
- Do not infer causation; report movement and the largest contributing dimension only.

DATA CAVEATS
- <e.g. Current month is partial; refreshed nightly at 02:00 UTC.>
- <e.g. Region "Unknown" means the CRM record predates territory tagging.>
```

> **Keep it tight.** 10,000 chars is generous but finite; spend it on disambiguation (term→field maps, the one right measure per ambiguous word) — that is where it changes output most. Naming, descriptions, and the schema carry the rest.

---

## 2. Semantic model description  *(model → File → Settings → Description)*

> One descriptive paragraph. Copilot uses the model **name + description** for discovery — distinct keywords help it know what this model can answer.

```text
<This semantic model provides … for … . It covers <subject areas: facts + key dimensions>,
supporting analysis of <core questions>. Grain: <e.g. one row per order line>.
It tracks <list the entities/measures a consumer would search for>.>
```

---

## 3. Report description  *(report → File → Settings → Description)*

```text
<A <one-line what> report for <audience>, covering <pages/themes> across
<dimensions/time range>. Use it to <the decision it supports>.>
```

---

## 4. Verified answers  *(curate the known questions — ≤ 250/model)*

> For each common or nuance-prone question, build the **visual that answers it correctly**, then select it → `…` → *Set up a verified answer* → add trigger phrases. Copilot returns the curated visual on a matching/semantically-similar prompt instead of guessing. Triggers match **exactly or semantically** (synonyms, reordered words, added filters all match; **swapping the measure or a dimension does not**).

| # | Question users actually ask | Backing visual (page · visual) | Trigger phrases (≤15, ≤500 chars each) | Default filter / permutation |
|---|---|---|---|---|
| 1 | `<e.g. sales by region this year>` | `<Overview · Map of Net Revenue by Region>` | `<sales by region; revenue by location; regional sales YTD>` | `<Year = current>` |
| 2 | `<…>` | `<…>` | `<…>` | `<…>` |
| 3 | `<…>` | `<…>` | `<…>` | `<…>` |

> **Seed the ambiguous ones first.** A verified answer is the highest-precision lever for a question where Copilot reliably picks the wrong field (the classic "sales = area? → product area, not region" trap).

---

## 5. AI data schema  *(remove noise — deselect, don't add)*

> Prep data for AI → *Define AI data schema*. **Deselect** fields Copilot should never reason over so it focuses on the meaningful ones and stops returning a legitimate-but-wrong interpretation (e.g. surfacing `Total GPM` when the team means `Net Revenue`).

Deselect:

- [ ] Surrogate/relationship keys (`*ID`, `*Key`) not meant for display
- [ ] Sort-order helper columns (`Month (Sort Order)`, etc.)
- [ ] Deprecated / pre-restatement / internal-only measures that shadow the house metric
- [ ] Duplicate field names across tables — rename to unique, human-readable, or deselect the one not for end users
- [ ] Audit/technical columns (`_loadedAt`, `RowHash`, ETL scratch)

---

## 6. Field description backfill  *(the grounding floor)*

> Every **table, column, and measure** that survives §5 needs a one-sentence `Description`. This is the [measure-metadata triad](../best-practices/enforce-measure-metadata.md) — author it in TMDL (`///` lines) or Tabular Editor. Copilot uses descriptions, data types, format strings, and **synonyms** as grounding; consistent human-readable naming + synonyms is what lets it resolve `Revenue` vs `Revenue YTD` vs `Revenue LY`.

- [ ] Every surviving measure has `Description` + `FormatString` + `DisplayFolder`
- [ ] Synonyms added for the terms in §1's terminology map (Model view → field → Synonyms)
- [ ] Technical columns hidden; unique human-readable names; correct, consistent data types
- [ ] A small set of **predefined KPI measures** (YTD, MoM growth, the house ratios) exists so Copilot composes from them instead of inventing DAX

---

## Worked example (filled — delete before shipping)

> For a **complete, all-four-layers-filled** instance (AI instructions + descriptions + verified answers + schema deselect + validation prompts) for one representative model, see the companion [`power-bi-copilot-readiness-worked-example.md`](power-bi-copilot-readiness-worked-example.md). The condensed AI-instructions-only block below shows the altitude for a fictional partner-revenue model:

```text
PURPOSE
This model is the source of truth for "how is partner-sourced revenue tracking vs target?".
Primary audience: regional partner managers and the VP of Partnerships.
Decisions it drives: where to invest partner-enablement effort next quarter.

DEFAULT INTERPRETATION
- "revenue" means [Net Partner Revenue], NOT [Gross Bookings] or [Total GPM].
- Default time grain: month. Default period: last 12 complete months (exclude the partial current month).
- Currency: USD, displayed as $#,##0. Never mix currencies in one visual.
- Default segmentation: by Region, then Partner Tier.
- Prefer [Net Partner Revenue], [Partner Revenue YTD], [Attainment vs Target %] over any raw column sums.

BUSINESS TERMINOLOGY
- "busy season" = June through August inclusive.
- "active partner" = a partner with at least one closed deal in the last 90 days.
- "tier" = Partner Tier (Platinum / Gold / Silver), NOT customer segment.

WHAT A GOOD ANSWER LOOKS LIKE
- Lead with Net Partner Revenue vs target and vs same period last year, then the top 3 regions by variance.
- For trend questions always show month-over-month.
- Round currency to whole dollars, percentages to one decimal.

WHAT TO AVOID / EXCLUDE
- Do not use [Legacy Revenue] — it predates the 2025 restatement.
- Exclude partners where Partner Tier = "Internal" from all totals.

DATA CAVEATS
- Current month is partial; model refreshes nightly at 02:00 UTC.
```

---

## Do / Don't

**Do**
- Spend the AI-instructions budget on **disambiguation** — the one right measure per ambiguous word, and term→field maps. That moves output more than prose about the business.
- Author in Microsoft's order (schema → verified answers → instructions → descriptions); each layer narrows what the next has to fix.
- **Test in the Copilot pane after every change** (close/reopen the pane in Desktop to reload instructions; use the skill picker → *Answer data question*). Confirm the instruction actually changed the answer.
- Mark the model **Approved for Copilot** only once it tests clean — the badge removes the friction treatment that was warning users to double-check.

**Don't**
- Don't write instructions that try to disable other Copilot features, set persona-specific behavior, or theme visuals — out of scope; the LLM ignores them.
- Don't rely on instructions to paper over a flat/ambiguous model — fix naming, descriptions, and the schema (§5/§6) first; instructions are the last 10%, not the first.
- Don't assume report-level scope: **AI instructions and verified answers save on the _semantic model_**, so every report on that model inherits them. Author once per model, not per report.
- Don't treat a single good test as done — Copilot is nondeterministic; test the awkward phrasings and the known-wrong-interpretation prompts.

---

## Provenance

Authored 2026-06-04 to fill the Copilot-readiness gap in the `power-platform` Power BI coverage (engineering-deep, AI-grounding-absent). Grounded against Microsoft Learn (retrieved 2026-06-04):

- [Prepare your data for AI to improve Copilot results](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai) — the three features + Approved-for-Copilot
- [Prep data for AI: AI instructions](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-instructions) — 10,000-char limit, model-level, considerations
- [Prep data for AI: Verified answers](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-verified-answers) — 250/model, 500-char triggers, match semantics, storage-mode support
- [Prep-data-for-AI FAQ](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-faq) — recommended implementation order + worked disambiguation examples
- [Optimize your semantic model for Copilot](https://learn.microsoft.com/power-bi/create-reports/copilot-evaluate-data) — naming/relationship/KPI considerations
- [Copilot for Power BI overview](https://learn.microsoft.com/power-bi/create-reports/copilot-introduction) — capacity/region requirements, 10,000-char prompt limit

---

_Last reviewed: 2026-06-04._
