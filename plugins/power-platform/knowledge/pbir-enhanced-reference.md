# PBIR Enhanced format — full reference for programmatic visual creation

> **Last reviewed:** 2026-06-10. Sources: original 2026-06-02 research (7+ repos + Microsoft schemas) plus a scout-run enrichment on 2026-06-10 from Kurt Buhler's Tabular Editor blog ("Hidden secrets in the Power BI report metadata", Nov 2025), data-goblin `conditional-formatting.md` companion reference, and Microsoft's official `formattingObjectDefinitions/1.5.0/schema.json`. Refresh when (a) Microsoft ships a new visualContainer / page / report schema major, (b) a visual type used here is renamed or its `queryState` role-names change, or (c) the `objects` vs `visualContainerObjects` split shifts again.
>
> **Claim-grounding note.** Every specific visualType string, role-name, and schema URL in this file was either taken from a real file fetched from a cited public repo or verified against Microsoft's schema CDN on 2026-06-02. Where this file says "real verified example", that means the JSON block was pulled from the repo's actual file at that date — not paraphrased. The places where verification was indirect are flagged inline as `[verify-at-use]`. Re-check before quoting any of this into customer code; Microsoft tightens these schemas between releases (see the companion lesson [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) for the May→June 2026 `prototypeQuery` breaking change).
>
> **When to read this file.** When you are *building* a PBIR Enhanced `visual.json`, `page.json`, or `report.json` from scratch — you need the canonical shape, the role names, the literal-suffix rules, the filter syntax, or the gotcha table. When you are *debugging* a Fabric Enhanced report that won't load, read [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) **first** — that file's decision tree resolves 90% of "deployed fine, won't render" cases (`resourcePackages`, `version.json`, `prototypeQuery`). The two files complement each other: that one is the debug runbook, this one is the build reference.

---

## 0. Schema-version note (added during 2026-06-02 spot-check)

Microsoft's schema CDN serves multiple major versions of the report-definition schemas side-by-side. Both of the following pairs were live and returning `HTTP 200` on 2026-06-02:

| Newer (recommended for new reports) | Older (still valid; older real-world reports use these) |
|---|---|
| `report/3.2.0/schema.json` | `report/3.1.0/schema.json` |
| `page/2.1.0/schema.json` | `page/2.0.0/schema.json` |
| `visualContainer/2.7.0/schema.json` | (only 2.7.0 in use at time of writing) |

**Rule of thumb.** For a *new* PBIR Enhanced report this team authors, default to `report/3.2.0` + `page/2.1.0` + `visualContainer/2.7.0` — those are what the existing [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) decision tree was verified against. For an *existing* report you are extending, **match what's already in `version.json` and the file headers** — don't silently upgrade the schema. Schema majors mix poorly.

The visual.json examples in this file all carry `visualContainer/2.7.0` because that is universal across the real files inspected. The `report.json` template here uses `report/3.2.0` to align with the companion lesson; the original Copilot research used `report/3.1.0`, which is also valid.

---

## 1. Visual type → `queryState` role mapping

The single most useful page when authoring a visual is "which roles does this visual accept?" Sources: `lukasreese/powerbi-claude-skills`, `rechedev9/granrapower`, `data-goblin`, `wardawgmalvicious/claude-config`.

### Cards & KPIs

| `visualType` | Display name | Query roles | Notes |
|---|---|---|---|
| `card` | Card (legacy) | `Values` (1 measure) | Still widely used; simple |
| `cardVisual` | New Card | `Data`, `ReferenceLabels`, `AdditionalMeasure` | Supports small multiples |
| `multiRowCard` | Multi-Row Card | `Values` (1+ measures/columns), `Category` (opt) | Array order = display order |
| `kpi` | KPI Visual | `Indicator` (req measure), `Goal` (opt measure), `TrendLine` (opt column — date) | TrendLine drives sparkline. **Confirmed `kpi`, not `kpiVisual`** — verified against `data-goblin/power-bi-agentic-development/plugins/pbip/skills/pbir-format/examples/visuals/default/kpi.json`. |
| `animatedNumber` | Animated Number | `Fields` | |

### Bar & Column charts

| `visualType` | Display name | Query roles |
|---|---|---|
| `clusteredBarChart` | Clustered Bar (horizontal) | `Category`, `Y`, `Series`, `Tooltips` |
| `barChart` | Stacked Bar | `Category`, `Y`, `Series`, `Tooltips` |
| `hundredPercentStackedBarChart` | 100% Stacked Bar | `Category`, `Y`, `Series`, `Tooltips` |
| `clusteredColumnChart` | Clustered Column (vertical) | `Category`, `Y`, `Series`, `Tooltips` |
| `columnChart` | Stacked Column | `Category`, `Y`, `Series`, `Tooltips` |
| `hundredPercentStackedColumnChart` | 100% Stacked Column | `Category`, `Y`, `Series`, `Tooltips` |
| `waterfallChart` | Waterfall | `Category`, `Y`, `Breakdown` (opt), `Tooltips` |
| `ribbonChart` | Ribbon | `Category`, `Y`, `Series`, `Tooltips` |

### Line & Area charts

| `visualType` | Display name | Query roles |
|---|---|---|
| `lineChart` | Line | `Category`, `Y`, `Y2` (secondary axis), `Series`, `Tooltips` |
| `areaChart` | Area | `Category`, `Y`, `Series`, `Tooltips` |
| `stackedAreaChart` | Stacked Area | `Category`, `Y`, `Series`, `Tooltips` |
| `hundredPercentStackedAreaChart` | 100% Stacked Area | `Category`, `Y`, `Series`, `Tooltips` |
| `lineClusteredColumnComboChart` | Line + Clustered Column | `Category`, `Y` (columns), `Y2` (line), `Series`, `Tooltips` |
| `lineStackedColumnComboChart` | Line + Stacked Column | `Category`, `Y` (columns), `Y2` (line), `Series`, `Tooltips` |

### Scatter, gauge, other

| `visualType` | Display name | Query roles | Notes |
|---|---|---|---|
| `scatterChart` | Scatter / Bubble | `Category` (opt bubble label), `X` (req measure), `Y` (req measure), `Size` (opt measure), `Series` (opt legend), `PlayAxis`, `Tooltips` | X and Y must be measures |
| `gauge` | Gauge | `Y` (actual — req measure), `MinValue`, `MaxValue`, `TargetValue` (all opt measures) | |
| `pieChart` | Pie | `Category`, `Y`, `Details`, `Tooltips` | |
| `donutChart` | Donut | `Category`, `Y`, `Details`, `Tooltips` | |
| `funnel` | Funnel | `Category`, `Y`, `Tooltips` | |
| `treemap` | Treemap | `Category`, `Details`, `Y`, `Tooltips` | |
| `decompositionTreeVisual` | Decomposition Tree | `Analyze` (measure), `Explain` (columns) | |

### Tables and matrix

| `visualType` | Display name | Query roles | Notes |
|---|---|---|---|
| `tableEx` | Table | `Values` (1+ — any order, **column-only OR measure-only, NOT mixed**) | Array order = column order. **Never use `table`.** **See "tableEx vs pivotTable" callout below — mixing column projections (`active:true`) with measure projections silently blanks the visual in Fabric.** |
| `pivotTable` | Matrix | `Rows` (1+), `Columns` (opt), `Values` (1+ measures) | `active: true` on Rows projection enables drill. **Default to `pivotTable` (matrix) the moment a table needs more than one measure with different formatters — see callout below.** |

> ### Callout — `tableEx` vs `pivotTable` for mixed dimension+measure content (BMA-CSP Lesson 5, 2026-06-04)
>
> `tableEx.Values` does **NOT** support mixing **column projections** (carrying `active: true`) and **measure projections** (no `active`) in the same `Values` array. The renderer silently shows **blank** — no error toast, no broken indicator, no warning in the deploy logs. All five SummaryTable / QuestionDetailTable / QuestionTable_LW / RankTable / Domain Performance visuals in the BMA-CSP report failed this way; the DAX measures all returned valid data when queried via REST, but every visual was blank.
>
> **The rule:**
> - **Column-only table** (filing links, reference data, diagnostics) → `tableEx` is fine.
> - **Measure-only summary table** → `tableEx` is fine.
> - **Mixed (a dimension column + one or more measures)** → use `pivotTable` (matrix) from the start: `Rows = [{column, active:true}]` + `Values = [measures]`. Mirrors the proven `EntityRiskMatrix` pattern.
>
> **Why `active: true` belongs only on `axis` / `slicer` roles, not `tableEx.Values`:** the `active` flag drives drill / cross-filter participation, which `tableEx.Values` does not support for a mixed-projection set. The renderer can't reconcile the column drill semantics with the measure projection semantics in one array, and it fails closed to "render nothing".
>
> **Diagnosis when you suspect this:** [`pbir-fabric-rest-debugging.md`](pbir-fabric-rest-debugging.md) — query the measures via `executeQueries` to confirm they return data, then visually compare the broken visual's `tableEx.Values` JSON to a working `pivotTable`'s `Rows` / `Values` split.

### Slicers

| `visualType` | Display name | Query roles | Notes |
|---|---|---|---|
| `slicer` | Slicer (legacy) | `Values` (1 column) | Mode via `objects.data` |
| `advancedSlicerVisual` | Button Slicer | `Rows` (NOT `Values`) | **Different role name!** Verified against `data-goblin/.../advancedSlicer.json`. |

### Decorative

| `visualType` | Display name | Query roles |
|---|---|---|
| `textbox` | Text Box | None (uses `objects.general.paragraphs`) |
| `basicShape` / `shape` | Shape | None |
| `image` | Image | None |
| `actionButton` | Button | None (uses `objects.visualLink`) |

---

## 2. Universal `visual.json` structure

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "unique_visual_name",
  "position": {
    "x": 24,
    "y": 120,
    "z": 1000,
    "width": 400,
    "height": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "clusteredBarChart",
    "query": {
      "queryState": {
        /* role → projections */
      },
      "sortDefinition": {
        /* optional */
      }
    },
    "objects": {
      /* visual-level formatting */
    },
    "visualContainerObjects": {
      /* container-level: title, border, background */
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": {
    "filters": []
  }
}
```

### Critical structural rules

- **`filterConfig` is a *sibling* of `visual`** at the root, **NOT** nested inside `visual`. This is the #1 gotcha — see §6.1.
- `visual` and `visualGroup` are mutually exclusive — one per file.
- `name` must be unique across the entire report; **the visual's folder name must match this `name` value**.
- Valid chars for `name`: `[A-Za-z0-9_-]` only. Many real files use a 16-20 char hash (e.g. `"79523ed91e7fb66cbb63"`); kebab-case is also fine.
- The allowed `visual` keys (after the ~June 2026 Fabric tightening) are: `visualType`, `autoSelectVisualType`, `query`, `expansionStates`, `objects`, `visualContainerObjects`, `syncGroup`, `drillFilterOtherVisuals`. **`prototypeQuery` is no longer allowed** — see [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) §FIX 4 for the breaking change.

**`expansionStates`** — records which hierarchy nodes are currently expanded in drill-capable visuals (matrix, decomposition tree). Written by Desktop on save when a user has expanded rows; leave absent or as `[]` when authoring new visuals programmatically — the visual starts fully collapsed. Do not set by hand; the serialised format is internal and varies by visual type.

**`syncGroup`** — links slicer visuals across pages. Slicers sharing the same `syncGroup` string value synchronize their filter selection whenever any one of them changes. The string is arbitrary — choose something descriptive. Place it directly inside the `visual` object:

```json
"visual": {
  "visualType": "slicer",
  "syncGroup": "year-filter-group",
  "query": { "queryState": { ... } },
  "drillFilterOtherVisuals": true
}
```

### Position properties

| Property | Type | Notes |
|---|---|---|
| `x`, `y` | number | Pixels from top-left of canvas |
| `z` | number | Layer order — higher = front. Real files commonly use `0`, `1`, `6`, `1000`, `2000` — there's no required range. |
| `width`, `height` | number | Pixels |
| `tabOrder` | number | Tab-key navigation order, 0-based. *Optional* — real files sometimes omit it (see §11). |

---

## 3. Field projection — canonical shape

```json
// Column reference (dimension)
{
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "ColumnName"
    }
  },
  "queryRef": "TableName.ColumnName",
  "nativeQueryRef": "ColumnName",
  "active": true
}

// Measure reference (metric)
{
  "field": {
    "Measure": {
      "Expression": { "SourceRef": { "Entity": "TableName" } },
      "Property": "MeasureName"
    }
  },
  "queryRef": "TableName.MeasureName",
  "nativeQueryRef": "MeasureName"
}

// Aggregation wrapper (needed for raw numeric columns used as values)
{
  "field": {
    "Aggregation": {
      "Expression": {
        "Column": {
          "Expression": { "SourceRef": { "Entity": "TableName" } },
          "Property": "NumericColumn"
        }
      },
      "Function": 0
    }
  },
  "queryRef": "Sum(TableName.NumericColumn)",
  "nativeQueryRef": "NumericColumn"
}
```

**Aggregation `Function` codes:** `0`=Sum, `1`=Avg, `2`=DistinctCount, `3`=Min, `4`=Max, `5`=Count, `6`=Median.

**Both `queryRef` and `nativeQueryRef` are required on every projection** — missing either can corrupt the visual on save. `queryRef` is `Table.Field`; `nativeQueryRef` is just the field/measure name with no table prefix. The companion [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) §FIX 5B is the debugging counterpart to this rule.

**`active` flag**:
- On column projections in axis-shaped roles (`Category`, `Series`, slicer `Values` / `Rows`, matrix `Rows` / `Columns`): **`active: true` required**.
- On measure projections: **never** include `active`. Doing so corrupts the query state.

---

## 4. Verified `visual.json` examples for advanced visual types

> **Provenance.** Examples §4.1–§4.3 (KPI, Matrix, Scatter) and §4.6–§4.7 are illustrative shapes derived from the Copilot research. Examples §4.4 (Waterfall) and §4.5 (Gauge) are the **raw real files** fetched from `data-goblin/power-bi-agentic-development` on 2026-06-02 — use these as the canonical shape and adapt for your tables.

### 4.1 KPI (`kpi`)

**Source:** `data-goblin/.../examples/visuals/default/kpi.json` — verified fetch 2026-06-02. The file uses a hash for `name` and `z: 1`; this example uses friendlier values.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "kpi_order_lines",
  "position": {
    "x": 32,
    "y": 224,
    "z": 1000,
    "height": 192,
    "width": 320,
    "tabOrder": 1
  },
  "visual": {
    "visualType": "kpi",
    "query": {
      "queryState": {
        "Indicator": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Orders" } },
                  "Property": "Order Lines"
                }
              },
              "queryRef": "Orders.Order Lines",
              "nativeQueryRef": "Order Lines"
            }
          ]
        },
        "Goal": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Orders" } },
                  "Property": "Order Lines PY"
                }
              },
              "queryRef": "Orders.Order Lines PY",
              "nativeQueryRef": "Order Lines PY"
            }
          ]
        },
        "TrendLine": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Date" } },
                  "Property": "Calendar Year Number"
                }
              },
              "queryRef": "Date.Calendar Year Number",
              "nativeQueryRef": "Calendar Year Number"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { "filters": [] }
}
```

**Key facts:**
- `Indicator` = main value (current period; measure)
- `Goal` = target/comparison (last year, budget; measure)
- `TrendLine` = a **date column** (not a measure) that drives the sparkline
- KPI direction can be reversed for cost metrics: `objects.indicator[0].properties.directionReverse`

### 4.2 Matrix (`pivotTable`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "matrix_customer_product",
  "position": {
    "x": 144,
    "y": 576,
    "z": 2000,
    "height": 408,
    "width": 672,
    "tabOrder": 2
  },
  "visual": {
    "visualType": "pivotTable",
    "query": {
      "queryState": {
        "Rows": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Customers" } },
                  "Property": "Key Account"
                }
              },
              "queryRef": "Customers.Key Account",
              "nativeQueryRef": "Key Account",
              "active": true
            },
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Customers" } },
                  "Property": "Account Name"
                }
              },
              "queryRef": "Customers.Account Name",
              "nativeQueryRef": "Account Name",
              "active": false
            }
          ]
        },
        "Columns": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Products" } },
                  "Property": "Brand Class"
                }
              },
              "queryRef": "Products.Brand Class",
              "nativeQueryRef": "Brand Class",
              "active": true
            }
          ]
        },
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Orders" } },
                  "Property": "Order Lines"
                }
              },
              "queryRef": "Orders.Order Lines",
              "nativeQueryRef": "Order Lines"
            },
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Orders" } },
                  "Property": "Order Lines PY"
                }
              },
              "queryRef": "Orders.Order Lines PY",
              "nativeQueryRef": "Order Lines PY"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { "filters": [] }
}
```

**Key facts:**
- First `Rows` projection has `"active": true` (expanded by default; click to drill to next level).
- Subsequent `Rows` projections have `"active": false`.
- `Columns` projections also get `"active": true`.
- `Values` projections (measures) do NOT use `active`.

### 4.3 Scatter (`scatterChart`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "scatter_product_perf",
  "position": {
    "x": 24,
    "y": 120,
    "z": 1000,
    "height": 400,
    "width": 500,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "scatterChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Products" } },
                  "Property": "Product Name"
                }
              },
              "queryRef": "Products.Product Name",
              "nativeQueryRef": "Product Name",
              "active": true
            }
          ]
        },
        "X": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Revenue"
                }
              },
              "queryRef": "Sales.Revenue",
              "nativeQueryRef": "Revenue"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Profit Margin"
                }
              },
              "queryRef": "Sales.Profit Margin",
              "nativeQueryRef": "Profit Margin"
            }
          ]
        },
        "Size": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Units Sold"
                }
              },
              "queryRef": "Sales.Units Sold",
              "nativeQueryRef": "Units Sold"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { "filters": [] }
}
```

**Key facts:**
- `Category` = the label/tooltip for each dot (column, not measure). `active: true` required.
- `X` and `Y` = **must be measures** (not columns).
- `Size` = bubble size (optional measure).
- `Series` = optional — adds color by group (a column dimension).
- `PlayAxis` = optional — enables animation by a time column.

### 4.4 Waterfall (`waterfallChart`) — verified real file

**Source:** `data-goblin/.../examples/visuals/default/waterfallChart.json` — fetched verbatim 2026-06-02. Note the `position` block has no `tabOrder` and uses `z: 6`; this is valid.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "bb6479538b364437",
  "position": {
    "x": 28,
    "y": 464,
    "z": 6,
    "height": 586,
    "width": 736
  },
  "visual": {
    "visualType": "waterfallChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Customers" } },
                  "Property": "Transaction Type"
                }
              },
              "queryRef": "Customers.Transaction Type",
              "nativeQueryRef": "Transaction Type",
              "active": true
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Orders" } },
                  "Property": "Order Lines"
                }
              },
              "queryRef": "Orders.Order Lines",
              "nativeQueryRef": "Order Lines"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

**Key facts:**
- `Category` is a column projection with `active: true`.
- `Y` accepts only ONE measure.
- `Breakdown` (optional) — a column that adds a decomposition sub-bar. Not present in this real file; supported per the role catalog.
- Sentiment colors: `objects.sentimentColors[0].properties.increaseFill / decreaseFill / totalFill`.
- The real file omits `filterConfig: { filters: [] }` — an empty `filterConfig` is implicit.

### 4.5 Gauge (`gauge`) — verified real file

**Source:** `data-goblin/.../examples/visuals/default/gauge.json` — fetched verbatim 2026-06-02. The real file uses only `Y` + `TargetValue` (the minimum useful gauge).

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "gauge_default_example",
  "position": {
    "x": 24,
    "y": 120,
    "z": 0,
    "height": 300,
    "width": 350,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "gauge",
    "query": {
      "queryState": {
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Revenue"
                }
              },
              "queryRef": "Sales.Revenue",
              "nativeQueryRef": "Revenue"
            }
          ]
        },
        "TargetValue": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Targets" } },
                  "Property": "Revenue Target"
                }
              },
              "queryRef": "Targets.Revenue Target",
              "nativeQueryRef": "Revenue Target"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

**Key facts:**
- `Y` is the actual value (**required; 1 measure only**).
- `TargetValue` is optional but typical (1 measure).
- `MinValue` and `MaxValue` are also optional measures — add them when the gauge needs explicit bounds. The real file omits them, which makes the gauge auto-scale.
- If min/max are hard constants, create DAX measures that return those constants (`Min = 0`, `Max = 1000000`).

### 4.6 Multi-Row Card (`multiRowCard`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "multirow_summary",
  "position": {
    "x": 24,
    "y": 120,
    "z": 1000,
    "height": 200,
    "width": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "multiRowCard",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Total Revenue"
                }
              },
              "queryRef": "Sales.Total Revenue",
              "nativeQueryRef": "Total Revenue"
            },
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Profit Margin"
                }
              },
              "queryRef": "Sales.Profit Margin",
              "nativeQueryRef": "Profit Margin"
            },
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Units Sold"
                }
              },
              "queryRef": "Sales.Units Sold",
              "nativeQueryRef": "Units Sold"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { "filters": [] }
}
```

**Key facts:**
- Role is `Values` (not `Fields` — that was an older version). Confirmed by `MinaSaad1/pbi-cli` changelog: *"`card` and `multiRowCard` queryState role corrected from `Fields` to `Values`."* (Repo verified live 2026-06-02.)
- Can include both measures and dimension columns in `Values`.
- Optional `Category` role: if present, creates a separate card per category value.

### 4.7 100% Stacked Bar (`hundredPercentStackedBarChart`)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "stacked100_by_category",
  "position": {
    "x": 24,
    "y": 120,
    "z": 1000,
    "height": 300,
    "width": 500,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "hundredPercentStackedBarChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Products" } },
                  "Property": "Brand"
                }
              },
              "queryRef": "Products.Brand",
              "nativeQueryRef": "Brand",
              "active": true
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Sales" } },
                  "Property": "Revenue"
                }
              },
              "queryRef": "Sales.Revenue",
              "nativeQueryRef": "Revenue"
            }
          ]
        },
        "Series": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Products" } },
                  "Property": "Category"
                }
              },
              "queryRef": "Products.Category",
              "nativeQueryRef": "Category",
              "active": true
            }
          ]
        }
      },
      "sortDefinition": {
        "sort": [
          {
            "field": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "Sales" } },
                "Property": "Revenue"
              }
            },
            "direction": "Descending"
          }
        ]
      }
    },
    "drillFilterOtherVisuals": true
  },
  "filterConfig": { "filters": [] }
}
```

---

## 5. `sortDefinition` syntax

Located inside `visual.query.sortDefinition`:

```json
"sortDefinition": {
  "sort": [
    {
      "field": {
        "Measure": {
          "Expression": { "SourceRef": { "Entity": "Sales" } },
          "Property": "Revenue"
        }
      },
      "direction": "Descending"
    }
  ],
  "isDefaultSort": true
}
```

**Rules:**

- The sort `field` must reference a field **already projected** in the visual's `queryState` (same `Entity` + `Property`).
- You cannot sort by a measure that's not in the visual.
- `direction`: `"Ascending"` or `"Descending"`.
- `isDefaultSort: true` lets Power BI override the sort at runtime during drill-down operations.
- The sort applies to the default render order; users can still click columns to re-sort in reading view.

**Real verified example** (from `bernatagulloesbrina/contoso-examples`, `Contoso.Report/definition/pages/Overview/visuals/by-brand/visual.json`):

```json
"sortDefinition": {
  "sort": [
    {
      "field": {
        "Measure": {
          "Expression": { "SourceRef": { "Entity": "Order Rows" } },
          "Property": "Margin"
        }
      },
      "direction": "Descending"
    }
  ],
  "isDefaultSort": true
}
```

---

## 6. `filterConfig` — complete syntax reference

### 6.1 Placement and scopes

```
Report:  report.json → filterConfig.filters[]    (all pages/visuals)
Page:    page.json   → filterConfig.filters[]    (all visuals on page)
Visual:  visual.json → filterConfig.filters[]    (SIBLING of "visual", not inside it!)
```

**The #1 gotcha**: `filterConfig` at visual level is at the ROOT of `visual.json`, NOT nested inside `"visual": {...}`.

```json
{
  "$schema": "...",
  "name": "my_visual",
  "position": { ... },
  "visual": { ... },          // ← visual is here
  "filterConfig": {           // ← filterConfig is here (sibling level)
    "filters": [ ... ]
  }
}
```

### 6.2 Filter types

| `type` | Use case | Key condition |
|---|---|---|
| `Categorical` | In / NotIn a list | `In` or `Not` → `In` |
| `Advanced` | Measure / column comparison | `Comparison`, `Between`, `And` / `Or` |
| `TopN` | Top / bottom N by measure | `VisualTopN` — see §6.5 |
| `RelativeDate` | Rolling window from today | `DateSpan` / `DateAdd` — see §6.6 |
| `RelativeTime` | Rolling time window (hours / minutes) | `DateSpan` with sub-day time units — see §6.10 |
| `Tuple` | Multi-column composite key (e.g. Country + City pair) | `In` with multi-column `Expressions` — see §6.11 |

### 6.3 Categorical filter — include (`statecode = 0`)

```json
{
  "name": "f1a2b3c4d5e6f7a8b9c0",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Licences" } },
      "Property": "statecode"
    }
  },
  "type": "Categorical",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "l", "Entity": "Licences", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "In": {
            "Expressions": [
              {
                "Column": {
                  "Expression": { "SourceRef": { "Source": "l" } },
                  "Property": "statecode"
                }
              }
            ],
            "Values": [[{ "Literal": { "Value": "0L" } }]]
          }
        }
      }
    ]
  },
  "howCreated": "User"
}
```

**Critical rules:**

- `From[]` defines aliases. `Where` uses `SourceRef.Source` (the alias `"l"`) — **NEVER** `SourceRef.Entity`.
- Integer literals use `L` suffix: `"0L"`, `"1L"`, `"2022L"`.
- String literals use inner single quotes: `"'EUR'"`, `"'Active'"`.
- Each value in `Values` is double-wrapped: `[[{...}], [{...}]]`.

### 6.4 Categorical filter — exclude (Not In)

```json
{
  "name": "a1b2c3d4e5f6a7b8c9d0",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Customers" } },
      "Property": "Key Account"
    }
  },
  "type": "Categorical",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "c", "Entity": "Customers", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "Not": {
            "Expression": {
              "In": {
                "Expressions": [
                  {
                    "Column": {
                      "Expression": { "SourceRef": { "Source": "c" } },
                      "Property": "Key Account"
                    }
                  }
                ],
                "Values": [[{ "Literal": { "Value": "'No Key Account'" } }]]
              }
            }
          }
        }
      }
    ]
  },
  "objects": {
    "general": [
      {
        "properties": {
          "isInvertedSelectionMode": {
            "expr": { "Literal": { "Value": "true" } }
          }
        }
      }
    ]
  }
}
```

### 6.5 Top N filter — top 10 by measure

```json
{
  "name": "topn_customers_01",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Customers" } },
      "Property": "Customer Name"
    }
  },
  "type": "TopN",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "c", "Entity": "Customers", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "VisualTopN": {
            "Expression": {
              "Column": {
                "Expression": { "SourceRef": { "Source": "c" } },
                "Property": "Customer Name"
              }
            },
            "Count": { "Literal": { "Value": "10L" } },
            "OrderBy": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "Sales" } },
                "Property": "Revenue"
              }
            },
            "IsAscending": false
          }
        }
      }
    ]
  }
}
```

**Notes:** `IsAscending: false` = Top N (largest first). `IsAscending: true` = Bottom N.

### 6.6 Relative date filter — last 3 months

```json
{
  "name": "reldate_last3months",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Date" } },
      "Property": "Date"
    }
  },
  "type": "RelativeDate",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "d", "Entity": "Date", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "Comparison": {
            "ComparisonKind": 2,
            "Left": {
              "Column": {
                "Expression": { "SourceRef": { "Source": "d" } },
                "Property": "Date"
              }
            },
            "Right": {
              "DateAdd": {
                "Expression": {
                  "DateSpan": {
                    "Expression": { "Now": {} },
                    "TimeUnit": 2
                  }
                },
                "TimeUnit": 2,
                "Amount": -3
              }
            }
          }
        }
      }
    ]
  }
}
```

**TimeUnit codes:** `0`=Day, `1`=Week, `2`=Month, `3`=Year, `4`=Decade, `5`=Second, `6`=Minute, `7`=Hour.

**ComparisonKind codes:** `0`=Equal, `1`=GreaterThan, `2`=GreaterThanOrEqual, `3`=LessThanOrEqual, `4`=LessThan.

### 6.7 Advanced filter — column comparison

```json
{
  "name": "adv_statecode_zero",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Licences" } },
      "Property": "statecode"
    }
  },
  "type": "Advanced",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "l", "Entity": "Licences", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "Comparison": {
            "ComparisonKind": 0,
            "Left": {
              "Column": {
                "Expression": { "SourceRef": { "Source": "l" } },
                "Property": "statecode"
              }
            },
            "Right": { "Literal": { "Value": "0L" } }
          }
        }
      }
    ]
  }
}
```

### 6.8 Page-level filter in `page.json`

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "Overview",
  "displayName": "Overview",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280,
  "filterConfig": {
    "filters": [
      {
        "name": "pg_statecode_filter",
        "field": {
          "Column": {
            "Expression": { "SourceRef": { "Entity": "Licences" } },
            "Property": "statecode"
          }
        },
        "type": "Categorical",
        "filter": {
          "Version": 2,
          "From": [{ "Name": "l", "Entity": "Licences", "Type": 0 }],
          "Where": [
            {
              "Condition": {
                "In": {
                  "Expressions": [
                    {
                      "Column": {
                        "Expression": { "SourceRef": { "Source": "l" } },
                        "Property": "statecode"
                      }
                    }
                  ],
                  "Values": [[{ "Literal": { "Value": "0L" } }]]
                }
              }
            }
          ]
        }
      }
    ]
  }
}
```

### 6.9 Filter visibility / lock options

```json
{
  "name": "hidden_bg_filter",
  "field": { ... },
  "type": "Categorical",
  "isHiddenInViewMode": true,
  "isLockedInViewMode": true,
  "filter": { ... }
}
```

**Force single-select:**

```json
{
  "objects": {
    "general": [
      {
        "properties": {
          "requireSingleSelect": {
            "expr": { "Literal": { "Value": "true" } }
          }
        }
      }
    ]
  }
}
```

---

## 7. Slicer configuration

### 7.1 List mode (default)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_status",
  "position": {
    "x": 24,
    "y": 24,
    "z": 1000,
    "height": 200,
    "width": 200,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Licences" } },
                  "Property": "statecode"
                }
              },
              "queryRef": "Licences.statecode",
              "nativeQueryRef": "statecode",
              "active": true
            }
          ]
        }
      }
    },
    "objects": {
      "data": [
        {
          "properties": {
            "mode": { "expr": { "Literal": { "Value": "'List'" } } }
          }
        }
      ]
    },
    "drillFilterOtherVisuals": true
  }
}
```

### 7.2 Dropdown mode

```json
"objects": {
  "data": [
    {
      "properties": {
        "mode": { "expr": { "Literal": { "Value": "'Dropdown'" } } }
      }
    }
  ]
}
```

### 7.3 Between mode (numeric / date ranges)

```json
"objects": {
  "data": [
    {
      "properties": {
        "mode": { "expr": { "Literal": { "Value": "'Between'" } } }
      }
    }
  ]
}
```

**All slicer mode values:** `'List'` (default), `'Dropdown'`, `'Between'`, `'Before'`, `'After'`.

### 7.4 Single-select slicer

```json
"objects": {
  "data": [
    {
      "properties": {
        "mode": { "expr": { "Literal": { "Value": "'Dropdown'" } } }
      }
    }
  ],
  "general": [
    {
      "properties": {
        "selfFilterEnabled": {
          "expr": { "Literal": { "Value": "false" } }
        }
      }
    }
  ]
}
```

And add `requireSingleSelect` in the matching `filterConfig` filter's `objects` block (see §6.9).

### 6.10 Relative time filter — last 4 hours

Use `RelativeTime` (not `RelativeDate`) when you need a rolling sub-day window.

```json
{
  "name": "reltime_last4hours",
  "field": {
    "Column": {
      "Expression": { "SourceRef": { "Entity": "Events" } },
      "Property": "EventTimestamp"
    }
  },
  "type": "RelativeTime",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "e", "Entity": "Events", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "Comparison": {
            "ComparisonKind": 2,
            "Left": {
              "Column": {
                "Expression": { "SourceRef": { "Source": "e" } },
                "Property": "EventTimestamp"
              }
            },
            "Right": {
              "DateAdd": {
                "Expression": {
                  "DateSpan": {
                    "Expression": { "Now": {} },
                    "TimeUnit": 7
                  }
                },
                "TimeUnit": 7,
                "Amount": -4
              }
            }
          }
        }
      }
    ]
  }
}
```

**`TimeUnit` codes for `RelativeTime`:** `5`=Second, `6`=Minute, `7`=Hour. Use `0`=Day / `1`=Week / `2`=Month / `3`=Year for day-or-longer windows with `RelativeDate`.

### 6.11 Tuple filter — multi-column composite key

A `Tuple` filter matches rows by a combination of column values treated as a single composite key. Use when you need to filter on (Country, Region) = ('US', 'West') rather than two independent column filters. `[verify-at-use]` — re-confirm the exact `Expressions` nesting against your Fabric schema version before production use.

```json
{
  "name": "tuple_country_region",
  "type": "Tuple",
  "filter": {
    "Version": 2,
    "From": [{ "Name": "g", "Entity": "Geography", "Type": 0 }],
    "Where": [
      {
        "Condition": {
          "In": {
            "Expressions": [
              {
                "Column": {
                  "Expression": { "SourceRef": { "Source": "g" } },
                  "Property": "Country"
                }
              },
              {
                "Column": {
                  "Expression": { "SourceRef": { "Source": "g" } },
                  "Property": "Region"
                }
              }
            ],
            "Values": [
              [
                { "Literal": { "Value": "'US'" } },
                { "Literal": { "Value": "'West'" } }
              ],
              [
                { "Literal": { "Value": "'CA'" } },
                { "Literal": { "Value": "'Ontario'" } }
              ]
            ]
          }
        }
      }
    ]
  }
}
```

**Key rules for Tuple:**
- `Expressions` lists the participating columns in order.
- Each entry in `Values` is an array of literals with the same length as `Expressions` — index-matched.
- The `field` key is omitted at the filter root (no single "primary" field for a composite key).

### 7.5 Default selected values (CRITICAL)

**Slicer pre-selections are stored in `objects.general.properties.filter`** — **NOT** in `filterConfig`.

- `filterConfig` on a slicer = restricts which values appear in the list (filters the slicer's DATA).
- `objects.general.properties.filter` = pre-selects values (as if the user had already clicked them).

```json
"objects": {
  "general": [
    {
      "properties": {
        "filter": {
          "Version": 2,
          "From": [{ "Name": "l", "Entity": "Licences", "Type": 0 }],
          "Where": [
            {
              "Condition": {
                "In": {
                  "Expressions": [
                    {
                      "Column": {
                        "Expression": { "SourceRef": { "Source": "l" } },
                        "Property": "statecode"
                      }
                    }
                  ],
                  "Values": [[{ "Literal": { "Value": "0L" } }]]
                }
              }
            }
          ]
        }
      }
    }
  ]
}
```

### 7.6 Button slicer (`advancedSlicerVisual`) — verified real file

**Source:** `data-goblin/.../examples/visuals/default/advancedSlicer.json` — fetched verbatim 2026-06-02.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "advancedSlicer_default_example",
  "position": {
    "x": 24,
    "y": 24,
    "z": 0,
    "height": 56,
    "width": 300,
    "tabOrder": 0
  },
  "visual": {
    "visualType": "advancedSlicerVisual",
    "query": {
      "queryState": {
        "Rows": {
          "projections": [
            {
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Products" } },
                  "Property": "Category"
                }
              },
              "queryRef": "Products.Category",
              "nativeQueryRef": "Category",
              "active": true
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}
```

**Key difference:** `advancedSlicerVisual` uses role `Rows` (not `Values`).

---

## 8. Cross-filtering and interactions

### 8.1 `drillFilterOtherVisuals` (per-visual)

Set inside `visual` (not at root level):

```json
"visual": {
  "visualType": "clusteredBarChart",
  "query": { ... },
  "drillFilterOtherVisuals": true   // true = clicking this visual filters other visuals
}
```

- `true` (default): clicking a data point on this visual cross-filters other visuals on the page.
- `false`: clicking a data point on this visual does NOT cross-filter others.

**Report-level default:** in `report.json → settings.defaultDrillFilterOtherVisuals: true`.

### 8.2 Visual interactions (per pair) — in `page.json`

Cross-filtering behavior between specific pairs of visuals is configured in **`page.json`**, NOT in `visual.json`:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "Overview",
  "displayName": "Overview",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280,
  "visualInteractions": [
    {
      "source": "slicer_status",
      "target": "bar_chart_revenue",
      "type": "NoFilter"
    },
    {
      "source": "bar_chart_revenue",
      "target": "line_chart_trend",
      "type": "Highlight"
    },
    {
      "source": "bar_chart_revenue",
      "target": "table_detail",
      "type": "Filter"
    }
  ]
}
```

**Interaction types:**

- `"Filter"` — source selection directly filters target (hides non-matching rows).
- `"Highlight"` — source selection highlights matching data in target (dims others).
- `"NoFilter"` — source has NO effect on target at all (blocks default behavior).

**Note:** `source` and `target` values are the `name` property from each visual's `visual.json`.

**Important:** you only need to define entries that OVERRIDE the default behavior. By default:

- Slicers → all other visuals: Filter
- Charts → charts: Highlight
- Charts → tables: Filter

---

## 9. Formatting objects (`objects` and `visualContainerObjects`)

### 9.1 Key distinction

Both live INSIDE the `visual` object (not at root), but control different things:

```json
"visual": {
  "visualType": "clusteredBarChart",
  "query": { ... },
  "objects": {
    // Visual-type-specific: axes, legend, data labels, data colors, line styles
    "categoryAxis": [{ "properties": { ... } }],
    "valueAxis": [{ "properties": { ... } }],
    "legend": [{ "properties": { ... } }],
    "labels": [{ "properties": { ... } }],
    "dataPoint": [{ "properties": { ... } }]
  },
  "visualContainerObjects": {
    // Container-level: title, subtitle, background, border, shadow, padding
    // Additional: lockAspect, spacing, visualLink (action button target) — see §9.9
    "title": [{ "properties": { ... } }],
    "background": [{ "properties": { ... } }],
    "border": [{ "properties": { ... } }],
    "dropShadow": [{ "properties": { ... } }]
  }
}
```

**This is a critical schema split in v2.4.0+.** Container properties placed in `objects` fail silently.

### 9.2 Literal value type suffixes

| Type | Format | Example |
|---|---|---|
| String | Inner single quotes | `{ "Value": "'Segoe UI'" }` |
| Double / Decimal | Number + `D` | `{ "Value": "14D" }` (font sizes, %) |
| Integer / Long | Number + `L` | `{ "Value": "0L" }` (pixel counts, enum values) |
| Boolean | Bare lowercase | `{ "Value": "true" }` |
| Hex color | Inner single-quoted | `{ "Value": "'#FF0000'" }` |
| Enum string | Inner single-quoted | `{ "Value": "'Top'" }` |
| DateTime | `datetime'...'` | `{ "Value": "datetime'2024-01-01T00:00:00.0000000'" }` |

**Known exceptions:**

- `transparency` inside `dropShadow` uses `L` (not `D`).
- `labelPrecision` always uses `L`.
- `labelDisplayUnits` always uses `D`.

### 9.3 Title formatting

```json
"visualContainerObjects": {
  "title": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "text": { "expr": { "Literal": { "Value": "'Sales Overview'" } } },
        "fontColor": {
          "solid": {
            "color": {
              "expr": { "Literal": { "Value": "'#333333'" } }
            }
          }
        },
        "fontSize": { "expr": { "Literal": { "Value": "12D" } } },
        "fontFamily": { "expr": { "Literal": { "Value": "'Segoe UI'" } } },
        "bold": { "expr": { "Literal": { "Value": "true" } } },
        "alignment": { "expr": { "Literal": { "Value": "'left'" } } }
      }
    }
  ]
}
```

### 9.4 Axis formatting

```json
"objects": {
  "categoryAxis": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "fontColor": {
          "solid": {
            "color": {
              "expr": { "Literal": { "Value": "'#666666'" } }
            }
          }
        },
        "showAxisTitle": { "expr": { "Literal": { "Value": "false" } } }
      }
    }
  ],
  "valueAxis": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "showAxisTitle": { "expr": { "Literal": { "Value": "false" } } },
        "gridlineShow": { "expr": { "Literal": { "Value": "true" } } },
        "gridlineColor": {
          "solid": {
            "color": {
              "expr": { "Literal": { "Value": "'#F0F0F0'" } }
            }
          }
        }
      }
    }
  ]
}
```

### 9.5 Data labels

```json
"objects": {
  "labels": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "fontSize": { "expr": { "Literal": { "Value": "9D" } } },
        "color": {
          "solid": {
            "color": {
              "expr": { "Literal": { "Value": "'#333333'" } }
            }
          }
        },
        "labelDisplayUnits": {
          "expr": { "Literal": { "Value": "0D" } }
        }
      }
    }
  ]
}
```

**`labelDisplayUnits` values:** `0D`=Auto, `1D`=None (exact), `1000D`=Thousands, `1000000D`=Millions, `1000000000D`=Billions.

### 9.6 Static data colors (`dataPoint`)

Apply a fixed color to all bars / data points:

```json
"objects": {
  "dataPoint": [
    {
      "properties": {
        "fill": {
          "solid": {
            "color": {
              "expr": { "Literal": { "Value": "'#4472C4'" } }
            }
          }
        }
      },
      "selector": {
        "data": [{ "dataViewWildcard": { "matchingOption": 0 } }]
      }
    }
  ]
}
```

### 9.7 Conditional formatting — color from measure

Use the **real object name for the visual** (see the callout below — `labels` for a card's value, a chart's data labels, etc.; **not** `calloutValue`, which exists only on `gauge`):

```json
"objects": {
  "labels": [
    {
      "properties": {
        "color": {
          "solid": {
            "color": {
              "expr": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "_Measures" } },
                  "Property": "KPI Color Measure"
                }
              }
            }
          }
        }
      }
    }
  ]
}
```

The measure `KPI Color Measure` should return a hex string like `"#D64550"` or `"#118DFF"`.

> ### ⚠️ Callout — Card text color: the `calloutValue` trap (Fabric/PBIR, verified 2026-06-10)
>
> **`calloutValue` is NOT a property of the legacy `card` visual — it belongs to `gauge`.** A `card`'s text-color objects are **`labels`** (the big callout number) and **`categoryLabels`** (plural — the small label below); the color property inside each is **`color`**, and legacy-card objects take **no `$id`**. `[verified 2026-06-10]` against Microsoft's official [`reportThemeSchema-2.137.json`](https://github.com/microsoft/powerbi-desktop-samples/blob/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.137.json), where `calloutValue` appears **only** under `gauge`.
>
> ```json
> "objects": {
>   "labels":         [{ "properties": { "color": { "expr": { "Literal": { "Value": "'#EDF2F7'" } } } } }],
>   "categoryLabels": [{ "properties": { "color": { "expr": { "Literal": { "Value": "'#EDF2F7'" } } } } }]
> }
> ```
>
> **Why a wrong object name fails SILENTLY (no error, just the default grey):** the PBIR `objects` block is an **open schema** — any key is syntactically accepted, then matched against the visual's registered capabilities **at render time and discarded if it doesn't match**. So `objects.calloutValue` on a `card` is dropped with no validation error. This is also exactly why **`visualContainerObjects.background` applies but `objects.<text>` does not** on the same visual: `background` is **container-layer** (always rendered); `labels`/`categoryLabels` are **visual-layer** (rendered only if the key is real for that visual type). The same rule governs the **theme** — `visualStyles.card.*` must use `labels`/`categoryLabels`, never `calloutValue`, or the theme's text color is silently ignored while its `background` still applies.
>
> **Theme equivalent:** `visualStyles.card.*.labels[].color` + `categoryLabels[].color` (or the theme structural colors: `firstLevelElements` = card value, `fourthLevelElements` = category label — [Microsoft Learn: create custom report themes](https://learn.microsoft.com/power-bi/create-reports/report-themes-create-custom)).
>
> **`cardVisual` (the NEW card) is different and not interchangeable:** its role is **`Data`** (not `Values`), every object item requires **`"$id": "default"`**, and its color property is **`fontColor`** (not `color`). Hand-switching `card`→`cardVisual` without migrating the role + injecting `$id` renders **blank** (the engine queries the `Data` role and finds no projection). Let Power BI Desktop do the conversion via the visual picker.
>
> **Ground-truth capture (the one residual `[verify-at-use]`):** whether `color` accepts a bare `{ "solid": { "color": "#hex" } }` vs the `{ "expr": { "Literal": … } }` wrapper in the `objects` context is not decidable from schema alone. Settle it in ~30s: format the card in **Power BI Desktop**, **Save** the PBIP, and read the serialized `visual.json` — Desktop writes the canonical form. (This also routes around the Fabric `getDefinition → parts:[]` limitation, which is a service-side API gap, not a problem with your JSON.)
>
> **Production lesson:** BMA-CSP-Risk-Scoring-V2 (Fabric DEV), 2026-06-10 — six failed attempts all used `calloutValue` / `categoryLabel` (singular) on a legacy `card`; the working fix was `labels` / `categoryLabels` (plural). The `calloutValue` example in this section's history is what caused it — corrected here.

### 9.8 Gradient conditional formatting (table column)

```json
"objects": {
  "values": [
    {
      "properties": {
        "backColor": {
          "FillRule": {
            "linearGradient3": {
              "min": {
                "color": {
                  "expr": { "Literal": { "Value": "'#FFFFFF'" } }
                },
                "value": { "expr": { "Literal": { "Value": "0D" } } }
              },
              "mid": {
                "color": {
                  "expr": { "Literal": { "Value": "'#FFFF00'" } }
                },
                "value": { "expr": { "Literal": { "Value": "0.5D" } } }
              },
              "max": {
                "color": {
                  "expr": { "Literal": { "Value": "'#FF0000'" } }
                },
                "value": { "expr": { "Literal": { "Value": "1D" } } }
              }
            }
          }
        }
      },
      "selector": { "metadata": "Sales.Revenue" }
    }
  ]
}
```

### 9.9 Additional `visualContainerObjects` properties

Three `visualContainerObjects` properties not shown in earlier examples. Sources: data-goblin `power-bi-agentic-development` SKILL.md (Kurt Buhler); property names are schema facts. `[verify-at-use]` — re-confirm exact inner property names against your Fabric schema version.

**`lockAspect`** — locks the visual container's width-to-height ratio. When set, resizing the container scales both dimensions proportionally.

```json
"visualContainerObjects": {
  "lockAspect": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } }
      }
    }
  ]
}
```

**`spacing`** — sets the inner padding between the container border and the visual content area. Uses `D` suffix (pixels).

```json
"visualContainerObjects": {
  "spacing": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "top": { "expr": { "Literal": { "Value": "8D" } } },
        "bottom": { "expr": { "Literal": { "Value": "8D" } } },
        "left": { "expr": { "Literal": { "Value": "8D" } } },
        "right": { "expr": { "Literal": { "Value": "8D" } } }
      }
    }
  ]
}
```

**`visualLink`** — defines the navigation action for an `actionButton` visual (page navigation, URL, or drill-through target). `[verify-at-use]` — the existing §1 table notes `objects.visualLink` for `actionButton`; verify placement (`objects` vs `visualContainerObjects`) against a Desktop-serialised file for your schema version.

```json
"visualContainerObjects": {
  "visualLink": [
    {
      "properties": {
        "show": { "expr": { "Literal": { "Value": "true" } } },
        "type": { "expr": { "Literal": { "Value": "'PageNavigation'" } } },
        "pageName": { "expr": { "Literal": { "Value": "'DetailPage'" } } }
      }
    }
  ]
}
```

**Other `type` values for `visualLink`:** `'WebUrl'` (opens a URL), `'Back'` (browser back), `'DrillThrough'` (target page + field context).

### 9.10 Theme `textClasses`

Power BI themes support a `textClasses` map that assigns named text styles used by visuals throughout the report. Each class defines a font face, size, and color; visuals that use a named class (like `title` or `label`) pull their default style from it. Source: Microsoft `reportThemeSchema-2.137.json` — verified in §9.7 callout.

```json
{
  "name": "Custom Dark Theme",
  "textClasses": {
    "callout": {
      "fontSize": 40,
      "fontFace": "Segoe UI",
      "color": "#FFFFFF"
    },
    "title": {
      "fontSize": 14,
      "fontFace": "Segoe UI Semibold",
      "color": "#FFFFFF"
    },
    "header": {
      "fontSize": 12,
      "fontFace": "Segoe UI",
      "color": "#CCCCCC"
    },
    "label": {
      "fontSize": 10,
      "fontFace": "Segoe UI",
      "color": "#AAAAAA"
    }
  }
}
```

**Named classes:** `callout` (large KPI number), `title` (visual title), `header` (table/matrix header), `label` (axis labels, data labels). All four are standard; additional custom classes are allowed by the schema.

**Interaction with `visualStyles`:** `textClasses` sets defaults; `visualStyles` (the per-visual-type override layer in the theme) takes precedence for specific visuals. `textClasses` is the right place for broad report-wide font adjustments; `visualStyles` is for visual-type-specific overrides.

---

## 10. `Tooltips` role

Add extra fields shown on hover by adding a `Tooltips` role to any chart's `queryState`:

```json
"queryState": {
  "Category": { ... },
  "Y": { ... },
  "Tooltips": {
    "projections": [
      {
        "field": {
          "Measure": {
            "Expression": { "SourceRef": { "Entity": "Sales" } },
            "Property": "Units Sold"
          }
        },
        "queryRef": "Sales.Units Sold",
        "nativeQueryRef": "Units Sold"
      },
      {
        "field": {
          "Measure": {
            "Expression": { "SourceRef": { "Entity": "Sales" } },
            "Property": "Profit Margin"
          }
        },
        "queryRef": "Sales.Profit Margin",
        "nativeQueryRef": "Profit Margin"
      }
    ]
  }
}
```

**For custom tooltip pages** (more complex layout):

```json
"visual": {
  "visualType": "clusteredBarChart",
  "query": { ... },
  "objects": {
    "tooltip": [
      {
        "properties": {
          "type": { "expr": { "Literal": { "Value": "'Page'" } } },
          "pageName": {
            "expr": { "Literal": { "Value": "'TooltipPage'" } }
          }
        }
      }
    ]
  }
}
```

---

## 11. Real verified `visual.json` from a real report

**Source:** `bernatagulloesbrina/contoso-examples/Contoso.Report/definition/pages/Overview/visuals/by-brand/visual.json`. Repo verified live 2026-06-02. Note the `$schema` appears at the **bottom** — JSON is order-independent so this is valid.

```json
{
  "name": "by-brand",
  "visual": {
    "visualType": "clusteredBarChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "queryRef": "Product.Brand",
              "field": {
                "Column": {
                  "Expression": { "SourceRef": { "Entity": "Product" } },
                  "Property": "Brand"
                }
              },
              "nativeQueryRef": "Brand"
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "queryRef": "Order Rows.Margin",
              "field": {
                "Measure": {
                  "Expression": { "SourceRef": { "Entity": "Order Rows" } },
                  "Property": "Margin"
                }
              },
              "nativeQueryRef": "Margin"
            }
          ]
        }
      },
      "sortDefinition": {
        "sort": [
          {
            "field": {
              "Measure": {
                "Expression": { "SourceRef": { "Entity": "Order Rows" } },
                "Property": "Margin"
              }
            },
            "direction": "Descending"
          }
        ],
        "isDefaultSort": true
      }
    },
    "objects": {},
    "drillFilterOtherVisuals": true,
    "visualContainerObjects": {
      "title": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "true" } } },
            "text": {
              "expr": { "Literal": { "Value": "'Top Brands by Margin'" } }
            },
            "fontSize": { "expr": { "Literal": { "Value": "14D" } } },
            "bold": { "expr": { "Literal": { "Value": "true" } } }
          }
        }
      ],
      "subTitle": [
        {
          "properties": {
            "show": { "expr": { "Literal": { "Value": "false" } } }
          }
        }
      ]
    }
  },
  "position": {
    "x": 652,
    "y": 532,
    "z": 0,
    "width": 604,
    "height": 168,
    "tabOrder": 0
  },
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
}
```

---

## 12. `page.json` with `filterConfig` + interactions

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "Overview",
  "displayName": "Overview",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280,
  "visualInteractions": [
    {
      "source": "slicer_statecode",
      "target": "card_active_licences",
      "type": "Filter"
    }
  ],
  "filterConfig": {
    "filters": [
      {
        "name": "pg_active_only",
        "displayName": "Active Records",
        "field": {
          "Column": {
            "Expression": { "SourceRef": { "Entity": "Licences" } },
            "Property": "statecode"
          }
        },
        "type": "Categorical",
        "filter": {
          "Version": 2,
          "From": [{ "Name": "l", "Entity": "Licences", "Type": 0 }],
          "Where": [
            {
              "Condition": {
                "In": {
                  "Expressions": [
                    {
                      "Column": {
                        "Expression": { "SourceRef": { "Source": "l" } },
                        "Property": "statecode"
                      }
                    }
                  ],
                  "Values": [[{ "Literal": { "Value": "0L" } }]]
                }
              }
            }
          ]
        },
        "isHiddenInViewMode": false,
        "isLockedInViewMode": false,
        "howCreated": "User"
      }
    ]
  }
}
```

**Reliability tip** (from `TemplateMechanics/pbi-pilot/CLAUDE.md`): for externally-authored PBIR, page-level filters are the most reliable way to ensure filters render in the Filter Pane. Canvas slicer visuals are OPTIONAL supplements — do not rely on canvas slicers as the sole filtering mechanism when reliable filtering UX is required, because slicers created outside Power BI Desktop may fail to render. `[verify-at-use]` — re-confirm against your current Fabric build.

---

## 13. `report.json` structure

For the canonical, debug-tested `report.json` template, see [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) §"Correct `definition/report.json` template (schema 3.2.0)" — that file's template is what made a real BTCSI-engagement report load and is the authoritative shape for new reports. The structure below is the Copilot research's version (using `report/3.1.0`) — equivalent shape, slightly older schema.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.2.0/schema.json",
  "themeCollection": {
    "baseTheme": {
      "name": "CY25SU12",
      "reportVersionAtImport": {
        "visual": "2.7.0",
        "report": "3.2.0",
        "page": "2.1.0"
      },
      "type": "SharedResources"
    }
  },
  "filterConfig": { "filters": [] },
  "objects": {
    "outspacePane": [
      {
        "properties": {
          "visible": { "expr": { "Literal": { "Value": "true" } } },
          "expanded": { "expr": { "Literal": { "Value": "false" } } }
        }
      }
    ]
  },
  "settings": {
    "useStylableVisualContainerHeader": true,
    "defaultDrillFilterOtherVisuals": true,
    "useEnhancedTooltips": true,
    "allowChangeFilterTypes": true,
    "allowInlineExploration": true,
    "defaultFilterActionIsDataFilter": true
  },
  "resourcePackages": [
    {
      "name": "SharedResources",
      "type": "SharedResources",
      "items": [
        {
          "name": "CY25SU12",
          "path": "BaseThemes/CY25SU12.json",
          "type": "BaseTheme"
        }
      ]
    },
    {
      "name": "RegisteredResources",
      "type": "RegisteredResources",
      "items": []
    }
  ]
}
```

**Remember** (from the debug lesson): `resourcePackages[0].items[0].name` MUST match `themeCollection.baseTheme.name` exactly, or the renderer stalls during theme resolution (infinite spinner). And `version.json.version` must be `"2.0.0"` even while the `$schema` URL still ends in `/1.0.0/`.

### `settings` property reference

All six properties in the template above are boolean flags. Descriptions verified against the report/3.2.0 schema and real serialised reports; additional platform-reserved properties exist but are schema-internal — only configure the ones below.

| Property | Default | Effect |
|---|---|---|
| `useStylableVisualContainerHeader` | `false` | Enables the modern styled visual header (close / pin / focus icons). Required `true` for `visualContainerObjects.title` to render reliably across visual types. |
| `defaultDrillFilterOtherVisuals` | `true` | Controls whether clicking a data point cross-filters other visuals by default. Can be overridden per-visual with `drillFilterOtherVisuals`. |
| `useEnhancedTooltips` | `false` | Enables the enhanced tooltip experience (supports rich tooltip pages). |
| `allowChangeFilterTypes` | `true` | Lets report consumers switch between filter types (basic / advanced) in the Filters pane. Set `false` to lock the filter type as authored. |
| `allowInlineExploration` | `true` | Allows consumers to expand visuals to full-screen focus mode. |
| `defaultFilterActionIsDataFilter` | `true` | Makes slicer and chart interaction actions apply as data filters (vs highlight). `false` reverts to highlight-first. |

Additional `settings` seen in the wild `[verify-at-use]`:
- `useNewFilterPaneExperience: true` — modern filter pane layout (enabled by default in newer schema versions).
- `isPersistentUserState: true` — preserves a reader's slicer selections between sessions.
- `hidePageNavigation: true` — hides the page tab bar (useful for embedded reports).

---

## 14. Critical gotchas — single-page lookup

| Gotcha | Wrong | Right |
|---|---|---|
| `filterConfig` placement in `visual.json` | Nested inside `"visual": {...}` | Sibling of `"visual"` at root |
| Filter `Where` `SourceRef` | `"SourceRef": {"Entity": "Table"}` | `"SourceRef": {"Source": "alias"}` |
| Filter value wrapping | `{"Literal": {"Value": "0L"}}` | `[[{"Literal": {"Value": "0L"}}]]` |
| Integer filter value | `"0D"` | `"0L"` |
| String filter value | `"Active"` | `"'Active'"` (inner single quotes) |
| `multiRowCard` role name | `Fields` | `Values` |
| `advancedSlicerVisual` role | `Values` | `Rows` |
| `kpi` `TrendLine` field type | measure | column (a date column) |
| Slicer pre-selection | `filterConfig` | `objects.general.properties.filter` |
| Title / border / shadow location | Inside `objects` | Inside `visualContainerObjects` |
| Container formatting schema check | `objects.title` works | Must use `visualContainerObjects.title` (v2.4.0+) |
| Combo chart line series role | `LineY` | `Y2` — Desktop PBIR reader uses `Y2` |
| `scatterChart` X, Y must be | columns | measures |
| Sort field must be | any measure | already in a `queryState` projection |
| `name` field validity | GUID with dashes | `[A-Za-z0-9_-]` only (kebab-case or hash) |
| Page-level filter schema | `filters: []` at root | `filterConfig: { "filters": [] }` |
| `transparency` in `dropShadow` | `"80D"` | `"80L"` (uses `L` suffix) |
| `prototypeQuery` on visual | tolerated (pre-June 2026) | **rejected** (`additionalProperties: false`) — strip it |
| `tabOrder` always present | required everywhere | optional — real files omit it on some visuals |
| Textbox `fontSize` type (added 2026-06-04, BMA-CSP Lesson 1) | integer like `10` (treated as **px** — most text invisible at normal screen sizes) | string with `"pt"` suffix like `"10pt"` — see §14a below |
| `tableEx.Values` with column projections + measure projections (added 2026-06-04, BMA-CSP Lesson 5) | mixed — `active:true` columns alongside measures (silently blanks visual) | use `pivotTable` (Matrix): `Rows = [{column, active:true}]` + `Values = [measures]` — see §1 callout |
| Stacked-bar series field type (added 2026-06-04, BMA-CSP Lesson 9) | raw free-text response column (`Responses[Value]`) — null dominates the legend | compute a normalized rate (`DIVIDE(Score, MaxScore)`) and use a horizontal bar chart per question |
| Per-data-point measure-driven coloring (added 2026-06-04, BMA-CSP Lesson 10) | no `selector` → single solid color for the whole series | `selector: {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}` with an empty placeholder `{"properties": {}}` first — see §14b below |
| `dataViewWildcard.matchingOption` values (corrected 2026-06-10) | 2 values: 0=series, 1=per-bar | THREE values: 0=all data points including totals (default), 1=per data point excluding totals, 2=totals/subtotals only — see §14b |
| Series-level CF (one color per series line, not per segment) | `dataViewWildcard matchingOption:0` | `"selector": {"metadata": "Table.MeasureQueryRef"}` — the `metadata` selector, not `dataViewWildcard`. See §14b |

---

## 14a. Textbox `fontSize` MUST be a string with `"pt"` suffix (BMA-CSP Lesson 1, 2026-06-04)

**Symptom:** subtitles and body text invisible after deploy; cover titles (using larger font sizes) appear; intermediate sizes are barely readable.

**Why:** in PBIR Enhanced, the textbox `fontSize` field accepts a **string with an explicit unit suffix**. A bare integer like `10` is interpreted as **pixels**, not points. 10px text is invisible at normal screen / projector sizes; 22px is barely readable. A pt-suffixed string like `"10pt"` renders as expected.

```json
// WRONG — integer is treated as px; invisible at normal sizes
"objects": {
  "general": {
    "properties": {
      "paragraphs": [{
        "textRuns": [{
          "value": "This is body copy",
          "textStyle": { "fontSize": 10 }
        }]
      }]
    }
  }
}

// RIGHT — string with "pt" suffix renders at the expected point size
"objects": {
  "general": {
    "properties": {
      "paragraphs": [{
        "textRuns": [{
          "value": "This is body copy",
          "textStyle": { "fontSize": "10pt" }
        }]
      }]
    }
  }
}
```

**The rule:** always pass `fontSize` as a **string with the `"pt"` suffix** for textbox content. If you have a helper that emits paragraphs / text runs from a Python or shell generator, add a `_pt()` normalizer at the helper's entry point that coerces `int | str → "Npt"` so the bug cannot recur. The BMA-CSP session spent several deploy cycles assuming wrong colors / z-ordering before catching this; a normalizer at the helper entry-point prevents the entire failure class.

---

## 14b. Per-bar / per-slice measure-driven coloring needs `dataViewWildcard.matchingOption: 1` (BMA-CSP Lesson 10, 2026-06-04)

**Symptom:** applying a color measure to a bar chart without a `selector` gives a single solid color for the entire series, not per-bar coloring. `In` expression selectors for per-category static colors are not confirmed valid in the PBIR schema.

**The correct pattern:**

```json
"objects": {
  "dataPoint": [
    { "properties": {} },
    {
      "properties": {
        "fill": {
          "solid": {
            "color": {
              "expr": {
                "Measure": {
                  "Property": "Risk Color",
                  "Expression": { "SourceRef": { "Entity": "Measures" } }
                }
              }
            }
          }
        }
      },
      "selector": {
        "data": [{ "dataViewWildcard": { "matchingOption": 1 } }]
      }
    }
  ]
}
```

**The three `dataViewWildcard.matchingOption` values** (verified against Microsoft `formattingObjectDefinitions/1.5.0/schema.json`, 2026-06-10):

| Value | Meaning | Use when |
|---|---|---|
| `0` | All data points including totals (default) | You want a single static formatting value that applies everywhere, including matrix subtotal and grand-total rows |
| `1` | Per data point, excluding totals | Per-bar / per-slice / per-segment measure-driven coloring — **always use this for dynamic coloring** |
| `2` | Totals and subtotals only | Applying a distinct format to summary rows only (rarely used) |

**Series-level CF (one color per line series, not per segment)** requires a `metadata` selector instead of `dataViewWildcard`. Use the `queryRef` value of the projected field as the selector key:

```json
"selector": { "metadata": "Sales.Revenue" }
```

This is the pattern shown in §9.8. Do **not** use `matchingOption: 0` for series-level CF — that applies to every data point including totals, not per-series.

**The empty first `{"properties": {}}` entry is required as a placeholder.** It defines the default "no selector" state; the second entry overrides it with the per-data-point measure-driven coloring.

**Companion measure pattern** — see [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) §4: color measures must be declared with `formatString: '@'` in TMDL (text type) or Power BI will attempt numeric aggregation on the hex string and fail. The two rules compose — the visual JSON pattern above only works if the measure it references is text-typed.

Encapsulate this as a `measure_color(measure_name)` helper in any Python / shell generator emitting PBIR visual JSON — same pattern as the `_pt()` normalizer above.

---

## 14c. UI-inaccessible dynamic line chart coloring via `strokeColor` Measure binding (2026-06-10)

> **Credit:** mechanism documented by Kurt Buhler in the Tabular Editor blog ("Hidden secrets in the Power BI report metadata", Nov 2025, updated March 2026) and verified with the JSON structure from the data-goblin `conditional-formatting.md` companion reference (`power-bi-agentic-development`, GPL-3.0 — facts re-expressed here in our own words). Independently verified by the 2026-06-10 scout run against Microsoft `formattingObjectDefinitions/1.5.0/schema.json` (schema remains permissive; not blocked by the June 2026 `additionalProperties: false` tightening).

Power BI's UI only allows selecting a static line color from the format pane. Setting the `strokeColor` property's color expression to a **Measure binding** (instead of the usual `Literal`) makes the line color dynamic — each segment is colored by the value the measure returns for that data point. This is something the UI cannot do.

**How it works:** the `formattingObjectDefinitions` schema uses `"additionalProperties": {}` for `DataViewObjectPropertyDefinitions` — the `objects` block is intentionally permissive and accepts any expression type, including `Measure`. The schema tightening that rejected `prototypeQuery` (June 2026) applied to the `visual` node, not to property expressions inside `objects`.

**The pattern** (place inside the visual's `objects` block, under the relevant object name for the property — typically `lineStyles` for a line chart):

```json
"objects": {
  "lineStyles": [
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
                  "Property": "Segment Color"
                }
              }
            }
          }
        }
      },
      "selector": {
        "data": [{ "dataViewWildcard": { "matchingOption": 1 } }]
      }
    }
  ]
}
```

The `Segment Color` measure must return a hex string (e.g. `"#E74C3C"`) and must be declared with `formatString: '@'` in TMDL (text type — see [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) §4). The `SourceRef.Schema: "extension"` path indicates the measure lives in `reportExtensions.json` (a thin-report / DAX-in-report measure).

**Critical constraint — single-series line charts only:**

The `strokeColor` Measure binding works for **single-series** line charts. On multi-series charts, Power BI overrides segment coloring at the series level, which suppresses the per-segment measure result. If a report has a `Series` role populated, `strokeColor` Measure binding will fail silently — the line renders with its default theme color. There is currently no PBIR workaround for dynamic per-segment coloring on a multi-series line chart; the approach is limited to charts with no `Series` role projection (or a single series).

**Companion DAX pattern** — the color measure typically uses `SWITCH` or `IF` over a classification measure to map values to hex strings:

```dax
Segment Color =
SWITCH(
    TRUE(),
    [Status Score] >= 80, "#27AE60",   // green
    [Status Score] >= 50, "#F39C12",   // amber
    "#E74C3C"                           // red
)
```

This measure is declared with `formatString: '@'` in TMDL to signal the text type and prevent numeric aggregation.

---

## 15. Schema URLs and file versions

Verified live on Microsoft's CDN 2026-06-02 — all returned `HTTP 200`. Both major-version sets coexist; pick the one matching your existing report's `version.json` (or default to the newer for new reports).

| File | Newer (recommended for new) | Older (still valid) |
|---|---|---|
| `visual.json` | `visualContainer/2.7.0/schema.json` | (only 2.7.0 in current use) |
| `page.json` | `page/2.1.0/schema.json` | `page/2.0.0/schema.json` |
| `report.json` | `report/3.2.0/schema.json` | `report/3.1.0/schema.json` |
| `version.json` | `versionMetadata/1.0.0/schema.json` (value: `"2.0.0"`) | same |
| `pages.json` | `pagesMetadata/1.0.0/schema.json` | same |
| `definition.pbir` | `definitionProperties/2.0.0/schema.json` (`version: "4.0"`) | same |
| `reportExtensions.json` | `reportExtension/1.0.0/schema.json` | same |

**Schemas update monthly.** When this reference is next refreshed, re-check both column headers — Microsoft may have published a new minor on the CDN. **Don't upgrade schema majors mid-report** — mixing schema majors can trigger "report has unresolved issues."

---

## 16. Remaining gaps and `[verify-at-use]` flags

After the 2026-06-02 spot-check, the following items in this reference were **not** end-to-end verified against a runtime Fabric render. Treat them as best-effort and confirm with a real test render before relying on them in customer code:

1. **Some `objects.advancedSlicerVisual` properties** (`layout.direction`, `button.unselectedFill`) — documented in `rechedev9/granrapower` but no example file inspected directly. The button-slicer base shape (§7.6) is verified; sub-properties are not.
2. **The slicer single-select toggle** is documented two ways across sources: `requireSingleSelect` in `filterConfig` filter's `objects` (§6.9) AND a separate `selfFilterEnabled: false` in `objects.general` (§7.4). Both are documented; their interaction was not directly tested. If one doesn't work, try the other.
3. **Conditional formatting `selector.metadata` format** — uses the `queryRef` value of the projected field (e.g. `"Sales.Revenue"`). For chart data points, `selector.data` with `dataViewWildcard` is the safer pattern.
4. **`reportExtensions.json`** for dynamic-color measures — must declare the measure AND list all semantic-model measure references in `references.measures`. Not demonstrated in detail here; see the cited sources if you need it.
5. **Font fallback chains** — `"'Segoe UI Semibold'"` works for a single font; multi-font fallback uses inner-triple-quoting (`"'''Segoe UI Semibold'', sans-serif'"`). Reported in `wardawgmalvicious`; quote-escaping is fragile across tools — test before committing.

When a gap closes, move the item out of this list and into the relevant section.

---

## 17. Sources

The original research was sourced and verified against the following public repos and Microsoft docs. Live-checked 2026-06-02; enrichment pass 2026-06-10.

| Source | What it provided |
|---|---|
| [`bernatagulloesbrina/contoso-examples`](https://github.com/bernatagulloesbrina/contoso-examples) | Real verified `visual.json` files (card, `clusteredBarChart`) — see §5, §11 |
| [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) (Kurt Buhler et al., GPL-3.0 — facts re-expressed in our own words) | Verified `visual.json` examples — KPI (§4.1), Matrix (§4.2), Scatter (§4.3), **Gauge (§4.5, real file)**, **Waterfall (§4.4, real file)**, **Button Slicer (§7.6, real file)**; `conditional-formatting.md` companion reference — `strokeColor` Measure-binding JSON structure and single-series constraint (§14c); `visualContainerObjects` additional properties `lockAspect`, `spacing`, `visualLink` (§9.9) |
| Tabular Editor blog — Kurt Buhler, "Hidden secrets in the Power BI report metadata" (Nov 2025, updated March 2026) | `strokeColor` Literal→Measure swap mechanism — verified UI-inaccessible capability (§14c); Desktop sync lag (C# changes require close/reopen, confirmed unfixed as of March 2026 update) |
| Microsoft `formattingObjectDefinitions/1.5.0/schema.json` | `DataViewWildcardMatchingOption` three-value enum: 0=all+totals, 1=per-instance, 2=totals-only (§14b) |
| Microsoft `reportThemeSchema-2.137.json` ([`powerbi-desktop-samples`](https://github.com/microsoft/powerbi-desktop-samples)) | Theme `textClasses` structure (§9.10); `calloutValue` trap for legacy `card` (§9.7 callout) |
| [`wardawgmalvicious/claude-config`](https://github.com/wardawgmalvicious/claude-config) | `sortDefinition`, slicer pre-selection vs `filterConfig`, literal suffix rules |
| [`lukasreese/powerbi-claude-skills`](https://github.com/lukasreese/powerbi-claude-skills) | Visual type → role mapping table (§1); formatting-objects examples (§9) |
| [`rechedev9/granrapower`](https://github.com/rechedev9/granrapower) | Per-`visualType` catalog; advanced slicer documented sub-properties (§16 #1) |
| [`MinaSaad1/pbi-cli`](https://github.com/MinaSaad1/pbi-cli) | Changelog confirming `card`/`multiRowCard` role name correction from `Fields` to `Values` (§4.6) |
| [`microsoft/mcp`](https://github.com/microsoft/mcp) — `tools/Fabric.Mcp.Tools.Docs/.../report-definition.md` | Official Microsoft schema reference + real `visual.json` with `filterConfig` |
| [`TemplateMechanics/pbi-pilot`](https://github.com/TemplateMechanics/pbi-pilot) | Page-level filter reliability guidance (§12) |
| Microsoft `developer.microsoft.com/json-schemas/...` | Schema URLs — all returned `HTTP 200` on 2026-06-02 (§15) |

---

## Owner & cross-reference

**Primary owner:** `power-bi-engineer`. The agent carries the inline knowledge prior for this reference.

**Companion file:** [`pbir-enhanced-report-loading.md`](pbir-enhanced-report-loading.md) — the debug runbook for when a PBIR Enhanced report deploys but won't render (the decision tree resolves `resourcePackages`, `version.json`, `prototypeQuery` and projection-shape root causes). Read that file when you're triaging a broken render; read this file when you're authoring a new visual / page / report.

**Escalation:** when an authored visual fails schema validation and the gotcha table here doesn't cover it, hand off to `ravenclaude-core/deep-researcher` to check whether the Fabric schema has shifted since this file's last refresh. Update the §15 schema table and the §1 role catalog if so.
