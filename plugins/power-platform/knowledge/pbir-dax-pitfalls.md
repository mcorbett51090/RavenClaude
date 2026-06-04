# PBIR / DAX — measure-evaluation pitfalls that silently blank visuals

> **Last reviewed:** 2026-06-04. Source: production session on the BMA-CSP-Risk-Scoring report (Bermuda Monetary Authority CSP engagement, `mcorbettbma/BTCSIReporting`, 2026-06-04). Five separate measure-design / TMDL pitfalls each cost hours of debug time because the failure mode is **silent visual blank with no error toast** — the report just *is* wrong. Refresh when (a) DAX semantics change in a Power BI release, (b) TMDL parser tightens or relaxes format-string handling, or (c) a new silent-fail shape surfaces in production.
>
> **Claim-grounding note.** Every pitfall below was reproduced 2026-06-04 against the live BMA-CSP semantic model and resolved in the same session. The DAX behaviors (REMOVEFILTERS arity, CONCATENATEX filter-context circularity, `formatString: @` for text measures, `0.0\%` for literal percent) are documented on Microsoft Learn — [verify-at-use] for the exact Power BI / Fabric version on the consumer's side, since DAX is one of the surfaces where Microsoft has tightened semantics across releases. The Domain Max Ceiling pattern (entity-context vs population-context measure naming) is a design lesson, not a contract.
>
> **When to read this file.** When a Power BI visual is **silently blank** and the DAX measure(s) "look fine" in the editor — or when you're authoring a TMDL `_Measures.tmdl` and want to avoid the four most common parse / type / context traps before they reach a visual. **The REST API ([`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md)) is the diagnosis tool** for every one of these — the pitfalls below are the design rules that prevent them from showing up at all.

---

## 1. `REMOVEFILTERS` does not accept multiple table arguments (Lesson 8)

**Symptom:** A measure using `REMOVEFILTERS(Questions, Licences)` silently blanks the entire visual it appears in. No error toast, no broken indicator — the visual just renders empty.

**Why:** `REMOVEFILTERS` is **unary** with respect to a table argument when used this way. Passing multiple tables in one call is a malformed expression; the engine evaluates the whole measure to BLANK and the visual treats BLANK-everywhere as "no data".

**Fix — use separate arguments OR `ALL()`:**

```dax
// WRONG — silently blanks the visual
Avg Score Per Question =
    CALCULATE(
        AVERAGE(Responses[Score]),
        REMOVEFILTERS(Questions, Licences)   // ← multiple tables in one call
    )

// RIGHT — pass each table as a separate REMOVEFILTERS argument
Avg Score Per Question =
    CALCULATE(
        AVERAGE(Responses[Score]),
        REMOVEFILTERS(Questions),
        REMOVEFILTERS(Licences)
    )

// ALSO RIGHT — ALL() handles multiple tables natively when the semantics fit
Avg Score Per Question =
    CALCULATE(
        AVERAGE(Responses[Score]),
        ALL(Questions, Licences)
    )
```

**Anti-pattern guard:** when writing a multi-table filter-stripping CALCULATE, always think in **separate `REMOVEFILTERS(T)` arguments**, not in "REMOVEFILTERS takes a list". Adopt as a measure-authoring checklist item.

---

## 2. `CONCATENATEX` over mixed filter contexts can silently blank a visual (Lesson 8 follow-on)

**Symptom:** A diagnostic measure built with `CONCATENATEX` against a join of Licences + Responses returns a string in DAX Studio but silently blanks the visual it lives in.

**Why:** `CONCATENATEX` evaluates its expression per row of its iterator, but in a visual with cross-filtering between two unrelated dimension tables (Licences and Responses), the per-row filter context can become **circular or ambiguous** — the engine returns blank to avoid a wrong answer.

**Fix:** for diagnostics, **prefer a raw column table with a slicer** over a `CONCATENATEX`-string measure. The visual's table-binding gives a clean filter context per row; the diagnostic does not have to flow through a measure that has to resolve the ambiguity itself. See [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) — REST queries are the diagnostic surface, not in-report measures.

**Anti-pattern guard:** if a diagnostic measure adds a `CONCATENATEX` over a multi-table filter, swap to a raw-column-table + slicer pattern in the diagnostics page. Don't iterate to "fix" the CONCATENATEX — the design itself is the bug.

---

## 3. TMDL format string for literal `%` on 0–100 scale (Lesson 13)

**Symptom:** A measure named `System Score` returns values in the range 0–100 (it's already a percent-of-max, not a 0–1 proportion). Visual displays "1500%" for a score of 15.

**Why:** TMDL `formatString: 0.0%;-0.0%;0.0%` triggers Power BI's **percent formatter**, which multiplies the value by 100 before applying the `%` suffix. A measure that is already 0–100 gets multiplied to 0–10000.

**Fix — escape the `%` as a literal character:**

```tmdl
// WRONG — multiplies × 100
measure 'System Score' = [System Score Raw]
    formatString: '0.0%;-0.0%;0.0%'

// RIGHT — backslash escapes % as a literal suffix (no × 100)
measure 'System Score' = [System Score Raw]
    formatString: '0.0\%'

// RIGHT for a TRUE 0–1 proportion that you want displayed as a percent — × 100 is the right behavior
measure 'Family Activation Rate' = DIVIDE([Activated], [Invited])
    formatString: '0.0%;-0.0%;0.0%'
```

**Rule:** before setting a format string, ask **"what scale is this value on?"** 0–1 → use `0.0%` (multiplies × 100). 0–100 → use `0.0\%` (literal suffix, no multiplication). Mixing these is silent and produces visuals that read 100x wrong.

---

## 4. Color / string measures need `formatString: @` (Lesson 14)

**Symptom:** A measure that returns a string (e.g. a hex color `"#D64550"` or a status label `"At risk"`) throws a type error or shows wrong / aggregated values when consumed by a visual that expects a measure.

**Why:** Power BI infers a measure's type from its `formatString`. With no `formatString` (or a numeric one), the engine treats the result as a number and applies numeric aggregation — which fails or produces nonsense on a string. The TMDL convention for **text-type** is `formatString: @`.

**Fix:**

```tmdl
// Color measure (returns hex string for a per-bar fill expression — see pbir-enhanced-reference.md §10)
measure 'Risk Color' =
    SWITCH(TRUE(),
        [Risk Score] >= 75, "#D64550",
        [Risk Score] >= 50, "#F4A100",
        [Risk Score] >= 25, "#F0D000",
        "#28A745"
    )
    formatString: '@'           // ← text type — required for color/label/URL measures

// Status label (similar — returns text, not a number)
measure 'Risk Tier' =
    SWITCH(TRUE(),
        [Risk Score] >= 75, "Very High",
        [Risk Score] >= 50, "High",
        [Risk Score] >= 25, "Medium",
        "Low"
    )
    formatString: '@'
```

**Rule:** any DAX measure that returns a **string** (color, label, URL, category text) needs `formatString: @` in TMDL. Add this to your measure-authoring checklist when writing color/label measures.

---

## 5. Entity-context vs population-context measure design (Lesson 11)

**Symptom:** A measure named `Selected Domain Ceiling` works correctly on entity-scorecard pages (which have an entity slicer) but renders BLANK on a "Domain Performance" page that has no entity selection.

**Why:** The measure uses entity-level applicability values that resolve to BLANK without an entity in the filter context. On a population page (no entity slicer), the measure has nothing to resolve against.

**Fix — design two measures with explicit names, not one that "depends on context":**

```dax
// Entity-context measure (BLANK without an entity selection — appropriate for entity-scorecard pages)
Selected Domain Applicable Ceiling =
    VAR _CM_Applicable = [Client Money Applicable]   // returns 1 or BLANK per entity
    VAR _Dir_Applicable = [Directorship Applicable]
    RETURN
        SWITCH(SELECTEDVALUE(Domains[Name]),
            "Client Money", IF(_CM_Applicable = 1, 35, BLANK()),
            "Directorship", IF(_Dir_Applicable = 1, 30, BLANK()),
            BLANK()
        )

// Population-context measure (returns the domain weight as a constant — appropriate for population pages)
Domain Max Ceiling =
    SWITCH(SELECTEDVALUE(Domains[Name]),
        "Core", 15,
        "Client Money", 35,
        "Directorship", 30,
        "Nominee", 20,
        BLANK()
    )
```

**Naming convention:** make the context **explicit in the measure name** — `Selected …`, `Applicable …`, or `Per-Entity …` for entity-context measures; `Max …`, `Population …`, or `Constant …` for measures that work without entity selection. Pick the right one per page. Don't reuse one measure across both page types and hope filter context resolves it.

---

## 6. Anti-pattern guard summary (paste into your measure-authoring checklist)

Before committing any new measure to `_Measures.tmdl`:

- [ ] If the measure uses `REMOVEFILTERS`, every table argument is a separate `REMOVEFILTERS(T)` — never `REMOVEFILTERS(T1, T2)` in one call.
- [ ] If the measure is a diagnostic for a multi-table relationship, it is a **raw column table + slicer** in the report, not a `CONCATENATEX` measure that has to resolve cross-table filter context.
- [ ] If the measure value is on a 0–100 scale and you want a `%` suffix, the format string is `0.0\%` (literal); reserve `0.0%` for true 0–1 proportions where × 100 is correct.
- [ ] If the measure returns a string (color, label, URL), the TMDL declaration carries `formatString: @`.
- [ ] If the measure depends on a specific filter context (e.g. an entity selection), its name says so (`Selected …` / `Applicable …`); the page-it-renders-on actually provides that context, OR a sibling population-context measure exists for population pages.

The diagnostic tool for any of the above pitfalls IS the Fabric REST API — see [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) for the `executeQueries` pattern that lets you `EVALUATE` a measure against the live model and see the real evaluation, bypassing the visual layer entirely.

---

## 7. Cross-links

- **Diagnosis tool for any of these silent-blank-visual pitfalls:** [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) (REST `executeQueries` against the live model — the first debugging move).
- **The other DAX silent-failure shape (string-literal vs actual-column-value mismatch):** [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md). Same family — the report deploys, the visual renders, the values are wrong.
- **PBIR visual structure rules** (when the failure is in the JSON, not the DAX): [`pbir-enhanced-reference.md`](pbir-enhanced-reference.md) §1 (visual type / role mapping) and §"Tables" (the `tableEx` vs `pivotTable` rule — same family of "silent blank visual" failures, but structural not measure-level).
- **TMDL measure-metadata discipline** (description / formatString / displayFolder enforcement): [`../best-practices/enforce-measure-metadata.md`](../best-practices/enforce-measure-metadata.md).

---

## 8. Owners

- **Primary:** `power-bi-engineer` (DAX authoring, TMDL, measure design).
- **Secondary:** `power-platform-tester` (the regression-test discipline that catches these silent-fail shapes before deploy — DAX semantic correctness is in this agent's mandate).
