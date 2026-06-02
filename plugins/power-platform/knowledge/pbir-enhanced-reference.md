# PBIR Enhanced format — full reference for programmatic visual creation

> **Last reviewed:** 2026-06-02. Source: research synthesized by Matt's GitHub Copilot pass over 7+ open-source repos (data-goblin, contoso-examples, wardawgmalvicious, lukasreese, rechedev9, MinaSaad1, microsoft/mcp) plus Microsoft schema docs, spot-checked the same day against the actual cited files. Refresh when (a) Microsoft ships a new visualContainer / page / report schema major, (b) a visual type used here is renamed or its `queryState` role-names change, or (c) the `objects` vs `visualContainerObjects` split shifts again.
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
| `tableEx` | Table | `Values` (1+ — any order) | Array order = column order. **Never use `table`.** |
| `pivotTable` | Matrix | `Rows` (1+), `Columns` (opt), `Values` (1+ measures) | `active: true` on Rows projection enables drill |

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
| `TopN` | Top / bottom N by measure | `VisualTopN` |
| `RelativeDate` | Rolling window from today | `DateSpan` / `DateAdd` |
| `RelativeTime` | Rolling time window | `DateSpan` with hour / minute units |
| `Tuple` | Multi-column composite | Rare |

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

```json
"objects": {
  "calloutValue": [
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

The original research was sourced and verified against the following public repos and Microsoft docs. Live-checked 2026-06-02.

| Source | What it provided |
|---|---|
| [`bernatagulloesbrina/contoso-examples`](https://github.com/bernatagulloesbrina/contoso-examples) | Real verified `visual.json` files (card, `clusteredBarChart`) — see §5, §11 |
| [`data-goblin/power-bi-agentic-development`](https://github.com/data-goblin/power-bi-agentic-development) | Verified `visual.json` examples — KPI (§4.1), Matrix (§4.2 derived from same repo's `pivotTable.json`), Scatter (§4.3), **Gauge (§4.5, real file)**, **Waterfall (§4.4, real file)**, **Button Slicer (§7.6, real file)** |
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
