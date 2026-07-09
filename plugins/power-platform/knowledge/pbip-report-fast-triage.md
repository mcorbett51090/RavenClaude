# PBIP / PBIR report fast-triage router

> **Last reviewed:** 2026-06-10. Sources: all linked knowledge files in this plugin; official Microsoft PBIR/PBIP docs (verified via Microsoft Learn MCP 2026-06-10); `github.com/microsoft/json-schemas` (referenced by MS Learn docs); data-goblin `pbir-format/references` (GPL — re-expressed). This is a **debug hub, not a build reference** — it links out to the detailed files rather than duplicating their content. Refresh when a new symptom shape surfaces in production or a target file is substantially reorganised.
>
> **Purpose.** Route the agent from observed symptom → correct reference file in 1–2 steps, not 6. Every cell is a file-level link + plain-text §N.N pointer; no `#anchor` links (they drift past CI silently — the file-level link is what CI's `check-md-links.py` validates).
>
> **MCP-optional design (load-bearing).** This router works when **all MCPs are banned** (e.g. ContosoReporting). Tier 1 (our captured reference) and Tier 2 (cited direct MS URLs) are the load-bearing tiers. The Learn MCP (Tier 3) is an **optional accelerator only** — it is never the only path to a fact.

---

## Table 1 — Symptom → cause → fix-location

Route by what you **observe** in the deployed report or build output, not by hypothesis.

| Observed symptom | Most likely cause | Fix: read this file | Pointer |
|---|---|---|---|
| **Infinite spinner** — report deploys with no error but never renders; Fabric stalls on load | `resourcePackages` missing from `definition/report.json`, OR `definition/version.json` value is `"1.0.0"` instead of `"2.0.0"` | [`knowledge/pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) | §Decision Tree FIX 1 + FIX 2 |
| **Zero or BLANK across all measures** — report renders cleanly, visuals show 0 / blank, no error; looks like "data not loaded yet" | Hardcoded string/integer literals in DAX filters don't match actual column values; CALCULATE/SUMX over empty filter returns BLANK() silently | [`knowledge/dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) | §TL;DR + §FIX B |
| **Missing rows** — some entities/submissions absent from the report with no warning | M Query `Table.RemoveRowsWithErrors` silently drops workbooks that lack a specific named table; OR Dataverse lookup display field not split at load boundary | [`knowledge/pbir-m-query-pitfalls.md`](pbir-m-query-pitfalls.md) | §1 (Excel/folder drop) + §3 (Dataverse lookup) |
| **Wrong or missing formatting / color** — a visual-container property (title text, border, shadow, background color) is set but silently ignored | Property written to `objects` instead of `visualContainerObjects`, OR wrong literal-value suffix (`"14"` instead of `"14D"`) | [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md) | §9.1 (objects split) + §9.2 (literal suffixes) |
| **Visual silently blank** — DAX measures "look fine" but the visual renders empty, no error toast | `REMOVEFILTERS(T1, T2)` arity bug; CONCATENATEX over mixed filter contexts; wrong `formatString` on a color/text measure; entity-context vs population-context confusion | [`knowledge/pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) | §1 (REMOVEFILTERS) + §2 (CONCATENATEX) + §4 (formatString `@`) |
| **First deploy fails / parameter rules not applied** — CI/CD deployment works on subsequent runs but fails or skips env-var substitution on the very first deploy | Deployment-pipeline parameter rules don't exist until the item is present in the target stage; first deploy must land the item first | [`knowledge/pbip-fabric-deployment-variables.md`](pbip-fabric-deployment-variables.md) | §The load-bearing distinction: Layer A vs Layer B |
| **Filter wrong scope / filter no-ops silently** — a `filterConfig` entry is present in the JSON but has no visible effect on the visual | `filterConfig` is nested **inside** `visual` instead of as its sibling at root; OR wrong literal suffix (`"0"` not `"0L"`); OR `SourceRef` uses `Entity` not `Source` alias | [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md) | §6 (filterConfig complete syntax) + §2 critical structural rules |
| **Deployment variable ignored** — `find_replace` or `key_value_replace` runs without error but display names in `.platform` files are unchanged | `fabric-cicd` `find_replace`/`key_value_replace` silently skip `.platform` files (issue #839); must preprocess `.platform` separately before `publish_all_items()` | [`knowledge/pbip-fabric-deployment-variables.md`](pbip-fabric-deployment-variables.md) | §The #839 gotcha |

> **Diagnosis not narrowed yet?** The Fabric REST API closes every one of these in <10 minutes: run `POST .../executeQueries` against the deployed semantic model to see what the measure actually returns vs what the visual is plotting. Read [`knowledge/pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) §1 before iterating further in the portal UI — the portal hides the real error envelope.

---

## Table 2 — Formatting / theming property-location decision rule

Use this table when you know **which property** you want to set but are unsure whether it goes in `objects`, `visualContainerObjects`, or the report theme file.

**The generalizing rule** (catches new bugs, not just the 6 known ones):

| Property category | What it controls | Correct location | Silent failure if wrong |
|---|---|---|---|
| **Chrome** — title text, subtitle, border width/color, drop shadow, background color/transparency | The visual *container* | `visual.visualContainerObjects` | Property set in `objects` → silently ignored |
| **Data content** — axis labels, legend, data labels, data colors, bar/line formatting, gridlines, value/category axis scale | The visual *rendering* | `visual.objects` | Property set in `visualContainerObjects` → silently ignored |
| **Container extras** — `lockAspect`, `spacing`, `visualLink` (action-button target) | Visual container metadata | `visual.visualContainerObjects` | Property set in `objects` → silently ignored |
| **Report-wide defaults** — default colors, font families, background, theme | Applied at report load from the theme JSON | `StaticResources/` theme file + `themeCollection` in `report.json` | Wrong `baseTheme.name` / missing `resourcePackages` → infinite spinner (see Table 1) |
| **Setting silently no-ops despite correct location** | Open-schema silent-discard: unknown property name, OR wrong literal-value type suffix | Verify property name in [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md) §9.2 (suffix table) + the Microsoft schema repo (Tier 2 below) | Always a property-name or suffix mismatch |

**Literal-value suffix quick-reference** (wrong suffix = silent no-op or schema-rejected):

| Value type | Required suffix | Example |
|---|---|---|
| String / color / enum | Inner single-quotes | `"'#FF0000'"`, `"'left'"`, `"'Segoe UI'"` |
| Double / decimal (font sizes, transparency 0–1) | `D` | `"14D"`, `"0.5D"` |
| Integer / long (pixel counts, enum ints) | `L` | `"0L"`, `"1L"` |
| Boolean | bare lowercase | `"true"`, `"false"` |

Full property tables (with known exceptions like `transparency` using `L` not `D`): [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md) §9.

---

## Source chain — graceful degradation (MCP-optional by design)

Use sources in this order. Tier 1 requires **nothing** — it always works, even with MCPs and network egress both banned.

### Tier 1 — Our captured reference (zero network / zero MCP — always works)

These files hold the official-schema facts statically, plus the production gotchas that are **not** in official docs (the spinner root cause, the silent-zero pattern, the M-query drop):

| File | Read when |
|---|---|
| [`knowledge/pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) | Debugging a deployed PBIR Enhanced report that won't render |
| [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md) | Authoring any PBIR visual / page / report JSON from scratch |
| [`knowledge/pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) | DAX measure silently blanks a visual |
| [`knowledge/dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) | Measures return 0 / BLANK silently |
| [`knowledge/pbir-m-query-pitfalls.md`](pbir-m-query-pitfalls.md) | Silent row drops at the M Query load stage |
| [`knowledge/pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) | Any PBIR/Fabric/Dataverse problem not obvious from the portal UI |
| [`knowledge/pbip-fabric-deployment-variables.md`](pbip-fabric-deployment-variables.md) | PBIP deploy across environments / parameterization / first-deploy failures |

### Tier 2 — Official Microsoft, non-MCP (needs network; cite and WebFetch directly)

Use these when the question is **"what IS the current property / schema / literal value?"** — i.e., a canonical-property question where the official schema leads. Fetch directly with `WebFetch` — no MCP needed.

| Question | Official source | Verified URL |
|---|---|---|
| PBIR Enhanced format overview + folder structure | Microsoft Learn — Power BI Developer | `https://learn.microsoft.com/power-bi/developer/projects/projects-report` |
| PBIR Enhanced format getting started | Microsoft Learn — Power BI Embedded | `https://learn.microsoft.com/power-bi/developer/embedded/projects-enhanced-report-format` |
| All PBIR JSON schemas (visual.json, page.json, report.json, version.json, etc.) | GitHub — microsoft/json-schemas | `https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition` |
| `formattingObjectDefinitions` schema (data-point colors, conditional formatting, `DataViewWildcardMatchingOption`) | Microsoft JSON schema CDN — verified in `pbir-enhanced-reference` §17 2026-06-02 | `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.5.0/schema.json` `[verify-at-use]` |
| Report theme JSON schema (visualStyles, textClasses, color properties) | GitHub — microsoft/powerbi-desktop-samples | `https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema` |
| Creating custom report themes (theme JSON structure, visualStyles, textClasses) | Microsoft Learn — Power BI Desktop | `https://learn.microsoft.com/power-bi/create-reports/report-themes-create-custom` |
| Deployment pipeline parameter rules (data source rules, parameter rules, first-deploy requirement) | Microsoft Learn — Fabric CICD | `https://learn.microsoft.com/fabric/cicd/deployment-pipelines/create-rules` |
| PBIP deployment with fabric-cicd (parameter.yml, environment-specific parameterization) | Microsoft Learn — Power BI Developer | `https://learn.microsoft.com/power-bi/developer/projects/projects-deploy-fabric-cicd` |

> **Against a Desktop-saved `.pbip` file:** for any property whose canonical shape is uncertain, save the report from Desktop with the property set, then read the resulting `visual.json` — that is always the ground truth. No network required.

### Tier 3 — Official Microsoft via Learn MCP (optional accelerator — only if your org permits MCPs)

Same authority as Tier 2, faster lookup. Use `microsoft_docs_search` / `microsoft_docs_fetch` / `microsoft_code_sample_search` from the `Microsoft_Learn` MCP server. **Do not use this tier if your org bans MCPs** — Tier 2 reaches the same canonical source via `WebFetch`.

```
# Example (only if MCP is available):
microsoft_docs_search: "PBIR visual.json filterConfig syntax SourceRef"
microsoft_docs_fetch: "https://learn.microsoft.com/power-bi/developer/projects/projects-report"
```

### Tier 4 — data-goblin `pbir-format/references` (GPL — deep-practitioner complement)

Real-world examples and edge cases not covered in official docs. **Read for reference, re-express in your own words, never copy prose.** Official MS (Tier 2/3) wins every conflict with this source.

- Repository: `https://github.com/data-goblin/power-bi-agentic-development/tree/main/plugins/pbip/skills/pbir-format/references`
- License: GPL-3.0 — facts may be re-expressed; code/prose must not be copied.
- Best used for: visual-type `queryState` role confirmation, edge-case `filterConfig` shapes, conditional-formatting patterns not yet in official schemas.

---

## Quick diagnosis protocol

Before editing any report file, run this two-step check:

1. **Hit the REST API first** — run `POST /v1.0/myorg/groups/{groupId}/datasets/{datasetId}/executeQueries` with a DAX `EVALUATE` against the deployed model. The portal hides error envelopes; REST returns them verbatim. Full endpoint cheat-sheet: [`knowledge/pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) §2.

2. **Match the fix to the symptom** — use Table 1 above. If the REST query confirms the measure returns valid data but the visual is blank: the bug is in the visual JSON shape (wrong role name, wrong `objects`/`visualContainerObjects` bucket, wrong `filterConfig` placement), not the DAX. Read [`knowledge/pbir-enhanced-reference.md`](pbir-enhanced-reference.md). If the REST query confirms the measure returns 0 / BLANK: the bug is in the DAX or the data filter. Read the DAX files.

**Never guess-and-check on report metadata.** A single REST query costs 5 minutes; a deploy-iterate-deploy loop on a wrong hypothesis costs hours.
