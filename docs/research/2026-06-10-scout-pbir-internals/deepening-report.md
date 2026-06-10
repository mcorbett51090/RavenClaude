# rc-deep-research: PBIR strokeColor + dataViewWildcard + Desktop Sync Lag — Adversarial Verification
_Run date: 2026-06-10 · Seed: Tabular Editor "Hidden secrets in the Power BI report metadata"_
_5 search angles · 8 sources fetched · adversarial verification per claim_

---

## Research Questions

1. Does the `strokeColor` Literal→Measure swap in `visual.json` objects block work in current Fabric PBIR Enhanced after the June 2026 `additionalProperties: false` schema tightening on `visualConfiguration/2.3.0`?
2. Is the `dataViewWildcard` per-segment vs per-series scoping triangle accurately documented — specifically does a third selector mode (per-series, distinct from matchingOption:1 per-data-point) actually exist?
3. Was the Desktop sync lag (C# changes require close/reopen) fixed in any subsequent TE/PBI Desktop release after Nov 2025?
4. What other UI-inaccessible formatting mechanisms exist in PBIR Enhanced visual.json?

---

## Sources Fetched

| URL | Status | Quality |
|---|---|---|
| https://tabulareditor.com/blog/hidden-secrets-in-the-power-bi-report-metadata | 200 OK | blog (primary practitioner) |
| https://tabulareditor.com/blog/c-scripting-pbir | 200 OK | blog (primary practitioner) |
| https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualContainer/2.7.0/schema.json | 200 OK | primary (Microsoft schema) |
| https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualContainer/CHANGELOG.md | 200 OK | primary (Microsoft schema) |
| https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/formattingObjectDefinitions/1.5.0/schema.json | 200 OK | primary (Microsoft schema) |
| https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualConfiguration/2.3.0/schema-embedded.json | 200 OK | primary (Microsoft schema) |
| https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report | 200 OK | primary (Microsoft official docs) |
| https://raw.githubusercontent.com/data-goblin/power-bi-agentic-development/main/plugins/pbip/skills/pbir-format/references/schema-patterns/conditional-formatting.md | 200 OK | blog (practitioner tool docs) |
| https://raw.githubusercontent.com/data-goblin/power-bi-agentic-development/main/plugins/pbip/skills/pbir-format/references/visual-json.md | 200 OK | blog (practitioner tool docs) |

---

## Verification Results

### Claim 1: strokeColor Literal→Measure swap enables UI-inaccessible per-segment line chart coloring

**Original claim (scout):** Setting a formatting property's expression to a Measure binding (not a Literal) in the `objects` block enables per-segment gradient line coloring not available in the PBI UI. The post shows the JSON diff.

**Evidence gathered:**

From the Tabular Editor "Hidden secrets" post (fetched directly): The article confirms this mechanism exists and describes it as "replaces a 'Literal' value with the 'Measure' reference, making it dynamic." However, the article presents this via a screenshot figure (K026 Figure 7) rather than a transcribed JSON block — the exact JSON path is not provided as readable text in the article body.

From `data-goblin/conditional-formatting.md` (fetched from the repo's companion reference): This file provides the **complete JSON structure** for the mechanism:

```json
{
  "properties": {
    "strokeColor": {
      "solid": {
        "color": {
          "expr": {
            "Measure": {
              "Expression": {
                "SourceRef": {
                  "Schema": "extension",
                  "Entity": "_Formatting"
                }
              },
              "Property": "Line Color"
            }
          }
        }
      }
    }
  },
  "selector": {
    "data": [
      {"dataViewWildcard": {"matchingOption": 1}}
    ]
  }
}
```

**Key constraint documented in data-goblin ref:** `strokeColor` only supports conditional formatting in **single-series charts**. Multi-series configurations override segment coloring.

**Schema verification:** The `formattingObjectDefinitions/1.5.0/schema.json` (Microsoft official) shows `DataViewObjectPropertyDefinitions` as `"additionalProperties": {}` — this is **intentionally permissive**, allowing any properties without constraints. The `objects` block for individual visuals also uses an external schema reference (`visualConfiguration/2.3.0/schema-embedded.json`) rather than an inline `additionalProperties: false`. The schema tightening that caused the `prototypeQuery` breaking change (June 2026) applied to the `visual` top-level node, NOT to `visual.objects` property values. Formatting object property expressions remain unconstrained by schema.

**Adversarial verdict: CONFIRMED with precision correction**

The mechanism is real and the JSON structure is verified against the data-goblin companion reference (which itself is consistent with the Tabular Editor article's description). The schema tightening does NOT block this mechanism. The scout's description was slightly imprecise: the article describes the mechanism but the JSON detail comes from the data-goblin companion file (the Tabular Editor post shows a screenshot, not a code block). The single-series constraint is the key fragility — not documented in the scout run.

**Confidence: HIGH** — two independent sources (TE blog + data-goblin companion ref) confirm the mechanism and its constraint.

---

### Claim 2: dataViewWildcard per-segment vs per-series scoping triangle (three distinct modes)

**Original claim (scout):** Three scoping modes exist: all-series (matchingOption:0), per-data-point (matchingOption:1), and per-series (a third variant). The existing reference only covers two. The scout claimed this was "distinct from matchingOption" already in reference §14b.

**Evidence gathered:**

From `formattingObjectDefinitions/1.5.0/schema.json` (Microsoft official, authoritative):

```
DataViewWildcardMatchingOption:
  0 = "Match Identities and Totals (default)"
  1 = "Match Instances with Identities only"
  2 = "Match Totals only"
```

From `data-goblin/conditional-formatting.md`:
- 0 = "All data points including totals"
- 1 = "Per data point evaluation (most common)"
- 2 = "Total/subtotal rows only"

From `data-goblin/visual-json.md`: "0 = identities + totals (series-level); 1 = per data point; 2 = totals only"

**Adversarial verdict: PARTIALLY CONFIRMED — but the scout mischaracterized the "per-series" mode**

There ARE three distinct matchingOption values, not two. The existing reference at §14b documents `matchingOption:1` for per-bar coloring. **What the scout described as a "per-series mode" is actually `matchingOption:0`** (Match Identities and Totals — applies formatting to data points including totals) and **`matchingOption:2`** is "Match Totals only" (not "per-series"). The Tabular Editor article describes `dataViewWildcard` as making CF apply "not by line series but by line part" — this is the distinction between a `metadata` selector (series-level) and `dataViewWildcard matchingOption:1` (per-data-point). The Tabular Editor article does NOT document a three-way scoping triangle — the scout extrapolated this from the article's description.

**The corrected picture:**
- matchingOption:0 — all data points including totals (the "default" when you want CF applied everywhere)
- matchingOption:1 — per-instance only, excluding totals (the per-bar / per-segment mode, already in reference §14b)
- matchingOption:2 — totals/subtotals only (rarely used; not the "per-series" mode the scout claimed)
- `metadata` selector (not `dataViewWildcard`) — series-level CF (one color per series, not per data point)

The existing reference's §14b coverage of `matchingOption:1` is CORRECT. The novel add from this research is: **matchingOption:2 (totals-only) and the full three-option documentation**. The "per-series vs per-segment triangle" framing in the scout was a misread — the distinction is `metadata selector` vs `dataViewWildcard:0` vs `dataViewWildcard:1` vs `dataViewWildcard:2`, not three modes within dataViewWildcard that map to per-series/per-segment/all.

**Confidence: HIGH** — verified against Microsoft's official schema JSON.

---

### Claim 3: Desktop sync lag — C# changes require close/reopen (not fixed)

**Original claim (scout):** C# script changes don't take effect until Desktop is closed and reopened; no incremental sync.

**Evidence gathered:**

From the Tabular Editor "C# scripting PBIR" post (fetched, publish date Nov 27 2025, updated March 17 2026):

**Exact quote:** "Changes aren't automatically visible in Power BI Desktop (yet). There are many potential use cases, but we need to close and open the report to see the differences"

**Recommended workflow from the article:** "1. Save your work and close Power BI Desktop before running the script. 2. Open the model in TE directly from model.bim or TMDL and execute the script. 3. After the script completes, you can open Power BI Desktop to see the changes in the report."

**Key fact about the update:** The article was **updated March 17, 2026** (per the fetch) and still contains this language — meaning as of March 2026, the limitation was not fixed. The "(yet)" in "aren't automatically visible (yet)" is the article's own acknowledgment this is a known limitation being tracked.

**Adversarial verdict: CONFIRMED**

The sync lag is real and was not fixed as of March 2026 (when the article was last updated). The scout's description ("C# script changes require close/reopen, no incremental sync") is accurate. The scout's characterization of "git-only rollback" was a slight overstatement — the article says "modifications to the model can be undone with Ctrl+Z, that's not the case with the modifications on the PBIR files" — so PBIR file changes have no undo, but model changes via TE itself do have Ctrl+Z. Git is the implied recovery for PBIR file changes.

**Confidence: HIGH** — direct quote from the article, updated March 2026, still states the limitation.

---

### Claim 4: Schema fragmentation admission from Tabular Editor

**Original claim (scout):** Tabular Editor uses partial PBIR schema knowledge; some properties discovered by experimentation.

**Evidence gathered:**

Exact quote from C# scripting article: "Even though the schema of these files is technically public, it is so complex (and spread around so many places) that it is very challenging to create a class that accounts for all possible visual object definitions."

**Adversarial verdict: CONFIRMED (with precision)**

The article acknowledges schema complexity and distribution but doesn't say "discovered by experimentation." The honest framing is: "the schema is public but too complex and fragmented to model completely." This is slightly different from the scout's "discovered by experimentation" framing — it's more accurately "the schema is known to exist but difficult to fully implement."

**Confidence: HIGH** — direct quote.

---

### Claim 5: mobile.json is per-visual (co-located with visual.json, not a central mobileState artifact)

**Original claim (scout + data-goblin SKILL.md):** Phone layout stored in `mobile.json` co-located with each `visual.json`, NOT in a central `mobileState` artifact.

**Evidence gathered:**

From Microsoft official docs (learn.microsoft.com/en-us/power-bi/developer/projects/projects-report), confirmed by the PBIR folder structure table:

```
├── pages\
│   ├── [pageName]\
│   |   ├── \visuals
|   │   |   ├── [visualName]\
|   |   │   │   |── mobile.json
|   |   |   └   └── visual.json
```

The official docs also show that `mobileState.json` IS a top-level report file (not under visuals) but it "Contains report appearance and behavior settings when rendering on a mobile device. This file doesn't support external editing." — this is a different file from the per-visual `mobile.json`. Both exist.

**Adversarial verdict: CONFIRMED with important nuance**

There are TWO mobile layout files:
1. `mobileState.json` — top-level report file, report-wide mobile settings, NOT editable externally
2. `[visualName]/mobile.json` — per-visual mobile layout, per the official schema reference "Visual mobile layout metadata, such as mobile position and formatting"

The data-goblin SKILL.md claim that `mobile.json` is per-visual co-located with `visual.json` is **correct and verified against Microsoft official docs**. The "not a central mobileState artifact" framing is also accurate — `mobileState.json` is a different file serving a different purpose.

**Confidence: HIGH** — directly verified against Microsoft official PBIR folder structure documentation.

---

## Synthesis

### Summary

5 claims verified across 9 fetched sources. All 5 core mechanisms survive adversarial scrutiny with precision corrections. The `strokeColor` Literal→Measure swap is real, the JSON structure is documented, and the schema does NOT block it. The `dataViewWildcard` scoping is more accurately a 3-option enum (0/1/2) than a "per-segment vs per-series triangle" — the scout's framing was an overreach. Desktop sync lag is confirmed as of March 2026 update. `mobile.json` per-visual co-location is verified against official docs.

### Verified findings (ranked by confidence × novelty for RC reference update)

| Finding | Confidence | Novel to reference? | Source |
|---|---|---|---|
| `strokeColor` Literal→Measure swap + single-series constraint | HIGH | YES — full JSON + single-series constraint | data-goblin conditional-formatting.md + TE blog |
| `dataViewWildcard` 3-option enum: 0=all+totals, 1=per-point, 2=totals-only | HIGH | PARTIAL — §14b covers matchingOption:1; adds matchingOption:0 semantics and matchingOption:2 definition | Microsoft formattingObjectDefinitions schema |
| Desktop sync lag confirmed as of March 2026 (article updated, limitation still present) | HIGH | YES — debug runbook add | TE C# scripting post (updated March 2026) |
| `mobile.json` per-visual co-location (two distinct files: per-visual mobile.json vs report-level mobileState.json) | HIGH | YES — data-goblin SKILL.md claim now MS-verified | Microsoft official PBIR folder structure docs |
| Schema tightening (June 2026) does NOT block formatting object expressions (additionalProperties permissive on DataViewObjectPropertyDefinitions) | HIGH | YES — clears uncertainty about strokeColor post-June 2026 | Microsoft visualConfiguration schema |

### Refuted / Corrected findings

| Claim | Verdict | Correction |
|---|---|---|
| "Per-series mode distinct from matchingOption:1 exists in dataViewWildcard" | CORRECTED | The three modes are: 0=all+totals, 1=per-point-only, 2=totals-only. There is no separate "per-series" mode within dataViewWildcard. Series-level CF uses a `metadata` selector, not dataViewWildcard. |
| "Git-only rollback" for C# scripting | CORRECTED | PBIR file changes have no undo (Ctrl+Z doesn't work); model changes in TE DO have Ctrl+Z. Git is the implied recovery for PBIR changes specifically. |
| "Schema fragmentation: some properties discovered by experimentation" | CORRECTED | TE's actual statement is the schema is "complex and spread around so many places" — the schema is public but hard to fully implement, not discovered by experimentation. |

### Open questions

1. Does `strokeColor` Measure binding work with multi-series line charts when the measure returns the same color for all points in a series? (The single-series constraint is the main known fragility — extent of multi-series failure modes is undocumented.)
2. What does matchingOption:0 ("Match Identities and Totals") actually render for line chart CF — does it visually differ from matchingOption:1 for a chart with no totals?
3. Is the Desktop sync lag fixed in any TE release after March 2026? (Article was last updated March 17 2026; the "(yet)" marker in the article suggests active work.)

---

## Recommendation for pbir-enhanced-reference.md update

The following verified adds should be written into the reference:

**§14 (conditional formatting) update:**
- Add complete `strokeColor` Measure-binding JSON pattern (from data-goblin conditional-formatting.md)
- Add single-series constraint caveat
- Expand `dataViewWildcard` matchingOption documentation: 0=all+totals (default), 1=per-point-only (already in §14b), 2=totals-only
- Clarify: series-level CF uses `metadata` selector, NOT `dataViewWildcard`

**pbir-enhanced-report-loading.md (debug runbook) update:**
- Add: Desktop sync lag — C# changes require close/reopen (confirmed March 2026, not yet fixed per article update)
- Add: `mobile.json` exists per-visual AND as `mobileState.json` at report level — different files, different purposes

---

```json
{
  "status": "complete",
  "summary": "5 claims verified. strokeColor Literal→Measure swap is real and schema-safe (additionalProperties is permissive on DataViewObjectPropertyDefinitions). dataViewWildcard has 3 modes (0/1/2), not the per-series/per-segment/all triangle the scout described — that framing was an overreach. Desktop sync lag confirmed as of March 2026 update. mobile.json per-visual co-location independently verified against Microsoft official docs.",
  "verified_adds": [
    "strokeColor Measure-binding pattern (full JSON from data-goblin ref)",
    "dataViewWildcard 3-option enum correction (0=all+totals, 1=per-point, 2=totals-only)",
    "Desktop sync lag: C# changes require close/reopen (still present March 2026)",
    "mobile.json per-visual vs mobileState.json report-level distinction"
  ],
  "refuted_claims": [
    "per-series mode as a distinct third dataViewWildcard mode (corrected: it's the metadata selector, not a matchingOption variant)",
    "git-only rollback overstatement (corrected: PBIR file changes only; model changes have Ctrl+Z in TE)"
  ],
  "confidence": 0.9,
  "next_actions": [
    "Update pbir-enhanced-reference.md §14 with strokeColor JSON + single-series constraint + matchingOption 3-way documentation",
    "Update pbir-enhanced-report-loading.md with Desktop sync lag (confirmed March 2026) and mobile.json/mobileState.json distinction",
    "No /forge gate needed — these are reference/runbook updates, not new builds"
  ]
}
```
