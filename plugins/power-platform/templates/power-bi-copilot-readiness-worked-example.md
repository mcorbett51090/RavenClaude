# Power BI Copilot Readiness — Worked Example (all four layers, filled)

**This is a complete, end-to-end worked instance** of [`power-bi-copilot-ai-instructions.md`](power-bi-copilot-ai-instructions.md) — every grounding layer filled for one representative model, so you can see what "done" looks like and adapt it rather than start from blank placeholders.

> **⚠️ Illustrative, not real data.** The model below ("Partner Revenue & Attainment") is a **representative fiction** built to exercise every layer — measure names, terms, and thresholds are invented. Replace each value with your model's real fields, real user questions, and real definitions before pasting anything into a production model. Do **not** ship these strings verbatim.

---

## 0. Model context (the inputs you'd normally gather)

| Input | Value (example) |
|---|---|
| Model / report | **Partner Revenue & Attainment** |
| Source of truth for | "How is partner-sourced revenue tracking vs target, and where should enablement effort go?" |
| Primary audience | Regional partner managers + VP of Partnerships |
| Storage mode | **Import** (so verified answers are fully supported) |
| Capacity | Fabric **F8** (≥ F2 → Copilot available) |
| Grain | One row per closed deal line |

> If this were a **DirectQuery or local Composite** model, **skip §4 (verified answers)** — unsupported there — and lean harder on §1 (AI instructions) + §6 (descriptions). Direct Lake supports verified answers **web-only**.

---

## 1. AI instructions  *(paste into Prep data for AI → Add AI instructions — 2,180 / 10,000 chars used)*

```text
PURPOSE
This model is the source of truth for "how is partner-sourced revenue tracking vs target, and where should we invest enablement next quarter?".
Primary audience: regional partner managers and the VP of Partnerships.
Decisions it drives: where to direct partner-enablement spend and which regions need intervention.

DEFAULT INTERPRETATION (apply unless the user overrides)
- When the user says "revenue", they mean [Net Partner Revenue], NOT [Gross Bookings] or [Total GPM].
- When the user says "attainment" or "vs target", they mean [Attainment vs Target %].
- Default time grain: month. Default period: last 12 complete months (exclude the partial current month).
- Currency: USD, displayed as $#,##0. Never mix currencies in one visual.
- Default segmentation: by Region, then Partner Tier.
- Prefer these measures over raw column sums: [Net Partner Revenue], [Partner Revenue YTD], [Attainment vs Target %], [MoM Revenue Growth %].

BUSINESS TERMINOLOGY (terms not present anywhere in the schema)
- "busy season" = June through August inclusive.
- "active partner" = a partner with at least one closed deal in the last 90 days.
- "tier" = Partner Tier (Platinum / Gold / Silver), NOT customer segment.
- "at-risk region" = a region whose Attainment vs Target % is below 85%.

WHAT A GOOD ANSWER LOOKS LIKE
- Lead with Net Partner Revenue vs target and vs the same period last year, then the top 3 regions by variance.
- For any trend question, always show month-over-month.
- For composition/mix questions, use % of total.
- Round currency to whole dollars, percentages to one decimal.

WHAT TO AVOID / EXCLUDE
- Do not use [Legacy Revenue] — it predates the 2025 restatement and is kept only for audit.
- Exclude partners where Partner Tier = "Internal" from all totals.
- Do not infer causation; report the movement and the largest contributing dimension only.

DATA CAVEATS
- The current month is partial; the model refreshes nightly at 02:00 UTC.
- Region "Unknown" means the CRM record predates territory tagging (~3% of rows pre-2024).
```

---

## 2. Semantic model description  *(model → File → Settings → Description)*

```text
The Partner Revenue & Attainment model is the source of truth for partner-sourced revenue
performance against target. It covers closed deal lines (fact) across Partner, Region, Product,
and Date dimensions, at one row per deal line. It supports analysis of net partner revenue,
attainment vs target, month-over-month growth, and revenue mix by tier and region. Search it
for: partner revenue, attainment, tier performance, regional variance, enablement targeting.
```

---

## 3. Report description  *(report → File → Settings → Description)*

```text
A partner-performance report for regional partner managers and the VP of Partnerships, covering
revenue vs target, regional variance, and tier mix across the trailing 12 months. Use it to
decide where to direct partner-enablement spend and which regions need intervention.
```

---

## 4. Verified answers  *(Import model → fully supported. 6 seeded; limit 250/model)*

| # | Question users actually ask | Backing visual (page · visual) | Trigger phrases (≤15, ≤500 chars each) | Default filter |
|---|---|---|---|---|
| 1 | Revenue vs target this year | Overview · Net Partner Revenue vs Target gauge | `revenue vs target; attainment this year; are we hitting target; partner revenue vs goal` | Year = current |
| 2 | Revenue by region | Overview · Map of Net Partner Revenue by Region | `revenue by region; partner revenue by location; regional revenue; where is revenue coming from` | Last 12 months |
| 3 | At-risk regions | Regions · Bar of Attainment vs Target % by Region (sorted asc) | `at-risk regions; which regions are behind; regions below target; underperforming regions` | Attainment < 85% |
| 4 | Revenue by tier | Tiers · 100% stacked column, Net Partner Revenue by Partner Tier | `revenue by tier; platinum vs gold vs silver; tier mix; revenue share by partner tier` | Last 12 months |
| 5 | Revenue trend | Trend · Line of Net Partner Revenue by month + MoM % | `revenue over time; revenue trend; monthly revenue; how has revenue changed` | Last 12 months, monthly |
| 6 | Top partners | Partners · Top-10 table of Net Partner Revenue by Partner | `top partners; best partners; biggest partners by revenue; who are our top partners` | Top 10 by Net Partner Revenue |

> Seeded the **ambiguous / wrong-interpretation** ones first: #2 (so "by region/location" never resolves to "product area") and #3 (so the org term "at-risk" maps to the 85% rule, not a guess).

---

## 5. AI data schema — deselect  *(Prep data for AI → Define AI data schema)*

Deselected so Copilot can't reason over them:

- [x] `Deal[DealLineID]`, `Partner[PartnerID]`, `Region[RegionID]`, `Date[DateID]` — surrogate keys
- [x] `Date[Month (Sort Order)]`, `Date[Day (Sort Order)]` — sort helpers
- [x] `[Gross Bookings]`, `[Total GPM]` — shadow measures that get returned when the user means [Net Partner Revenue]
- [x] `[Legacy Revenue]` — pre-restatement, audit-only
- [x] `Deal[_loadedAt]`, `Deal[SourceRowHash]` — ETL/audit columns

Kept + unique-named: `Net Partner Revenue`, `Partner Revenue YTD`, `Attainment vs Target %`, `MoM Revenue Growth %`, `Partner Tier`, `Region`, `Product Category`.

---

## 6. Field descriptions + synonyms  *(the grounding floor — TMDL `///` or Tabular Editor)*

```tmdl
table 'Deal'
    /// Closed partner deal lines. One row per deal line; source: CRM Opportunities, nightly.

    measure 'Net Partner Revenue' =
        SUMX(Deal, Deal[Quantity] * Deal[NetUnitPrice])
        formatString: "$#,##0"
        displayFolder: "Revenue"
        /// Net revenue from partner-sourced closed deals (quantity x net unit price). Excludes
        /// returns and Internal-tier partners. The house "revenue" measure — use this, not Gross Bookings.

    measure 'Attainment vs Target %' =
        DIVIDE([Net Partner Revenue], [Revenue Target])
        formatString: "0.0%"
        displayFolder: "Targets"
        /// Net Partner Revenue divided by the period Revenue Target. "Attainment". Below 85% = at-risk.
```

- **Synonyms** (Model view → field → Synonyms): `Net Partner Revenue` → "revenue, partner revenue, net revenue"; `Attainment vs Target %` → "attainment, vs target, to goal"; `Partner Tier` → "tier, partner level".

---

## 7. Validate in the Copilot pane  *(test BEFORE marking Approved)*

Run these — including the **known-wrong-interpretation** prompts — closing/reopening the Copilot pane after each instruction edit:

| Prompt | Expected (grounded) result | Catches |
|---|---|---|
| "show me revenue by area" | Net Partner Revenue **by Region** (verified answer #2) | "area" → product-area misread |
| "which regions are at risk?" | Regions with Attainment < 85% (verified answer #3) | org term not in schema |
| "revenue during busy season" | Net Partner Revenue for **Jun–Aug** | named-period term |
| "how are partners doing?" | Leads with revenue vs target + vs LY, then top-3 region variance | "what good looks like" |
| "total revenue" | [Net Partner Revenue], **not** [Gross Bookings]/[Total GPM] | shadow-measure pick |

If any prompt returns the wrong reading, adjust the corresponding layer (wrong measure → §5 deselect or §1 default-interpretation; wrong term → §1 terminology; inconsistent → §4 verified answer) and re-test.

---

## 8. Mark Approved for Copilot

Once §7 tests clean: model → Settings → **Approved for Copilot** → check → Apply. Removes the standalone-Copilot friction treatment; propagation up to ~1 hour (24 h with many attached reports).

---

## How to adapt this to your model

1. Replace the §0 context with your real model/domain/storage-mode/capacity.
2. Rewrite §1's DEFAULT INTERPRETATION and BUSINESS TERMINOLOGY from **your** ambiguous words and named terms — this is where Copilot output moves most.
3. Seed §4 from the questions your users **actually** type, ambiguous ones first (skip §4 entirely on DirectQuery/local Composite).
4. Deselect your real noise/shadow fields in §5; backfill §6 on what survives.
5. Run §7 against your real known-wrong prompts before §8.

---

_Last reviewed: 2026-06-04. Companion to [`power-bi-copilot-ai-instructions.md`](power-bi-copilot-ai-instructions.md) and [`../best-practices/bi-copilot-report-readiness.md`](../best-practices/bi-copilot-report-readiness.md). Grounded against the same Microsoft Learn Prep-data-for-AI sources cited there (retrieved 2026-06-04)._
