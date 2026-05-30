# Avoid per-viewer and per-row pricing traps — flag the cost math before recommending the tool

**Status:** Pattern — the plugin's standing stance for SMB consulting (4-6 engagements/year); deviate only when a specific client constraint (handoff, brand, compliance) outweighs the cost math, and say so in writing.

**Domain:** Cost predictability / tool economics

**Applies to:** `data-platform`

---

## Why this exists

The two pricing models that quietly destroy a fixed-fee consulting margin are **per-viewer** BI licensing and **per-row (MAR/event)** ELT billing — both because the variable that drives the bill (viewers, row churn) is the variable the consultant least controls and the client most expands. At 5-50 viewers × 4-6 clients × `$400+/viewer/yr`, Looker / Tableau Embedded / Sigma / Metabase Pro turn a `$25-50k` engagement into a recurring loss. On the ELT side, Fivetran's 2026 change counting **deletes** toward MAR makes change-heavy sources (Salesforce, HubSpot deal updates) cost-unpredictable on exactly the fixed-fee work where a surprise invoice is a relationship problem. The discipline isn't "never use these tools" — it's: when a user starts down one of these paths, **show the math at the engagement's real viewer/row scale before recommending**, so the choice is made with eyes open. The hook enforces a slice of this on `stack-decision-record.md` templates.

## How to apply

Before recommending a per-viewer BI tool or a per-row ELT tool, compute the bill at the engagement's actual scale and put it in the decision record next to the OSS alternative.

```
Per-viewer trap (BI)                    Free OSS / flat alternative
──────────────────────────────────────────────────────────────────────
Looker ~$400/viewer/yr                  Apache Superset OSS (free, JWT embed)
Tableau Embedded ~$420/viewer/yr        Metabase OSS static embed (free)
Sigma — $61k median deployment          Cube OSS + custom React (free)
Metabase Pro $575/mo + $12/viewer       Evidence.dev OSS for Case A (free)
Power BI Embedded F2 — FLAT ~$156/mo    (no per-viewer — App-Owns-Data; fine for M365)

Per-row trap (ELT)                      Flat / handoff-friendly alternative
──────────────────────────────────────────────────────────────────────
Fivetran (2026: deletes count → MAR)    Airbyte (Cloud Standard $10/mo or self-host OSS)
Hevo (per-event)                        Fivetran FREE tier (<500k MAR, client takes over)
```

```yaml
# stack-decision-record.md — show the math, name the alternative.
proposed_tool: metabase-pro
cost_at_scale: "50 viewers × 6 clients → $575/mo base + 300 × $12 = ~$74k/yr"   # [verify-at-build]
oss_alternative: "Metabase OSS static embed OR Superset OSS — $0 license, $20-40/mo VPS/client"
decision: "OSS — per-viewer math fails for SMB consulting"
```

**Do:**
- Compute the bill at the engagement's real viewer count and row-churn, and write it in the decision record beside the OSS alternative.
- Flag the **Fivetran 2026 deletes-count-as-MAR** change explicitly when proposing Fivetran on change-heavy sources.
- Treat Power BI Embedded F-SKU as the *flat-capacity* exception (no per-viewer in App-Owns-Data) — it's not a per-viewer trap.
- Reach for free OSS (Superset / Metabase / Evidence / Cube / Airbyte) as the default; pay only where a constraint earns it.

**Don't:**
- Recommend a per-viewer BI tool for an SMB engagement without surfacing the 5-50 viewers × 4-6 clients math.
- Default above 500k MAR on Fivetran for change-heavy sources without the cost-unpredictability flag.
- Quote any tier without a retrieval date (pricing moves quarterly).

## Edge cases / when the rule does NOT apply

- **Client takes over the infra at handoff AND MAR < 500k** — Fivetran free tier's managed simplicity can beat self-hosted Airbyte's ops burden; ease-of-handoff is a legitimate override.
- **M365-stack client** — Power BI Embedded F2 (flat capacity, brand familiarity, Entra-ID RLS) is often correct even when not cheapest; it isn't per-viewer-priced.
- **Genuine enterprise scale** where a per-viewer enterprise tool's features are actually required — then the model fits the engagement; that's the rule applied with eyes open, not broken.

## See also

- [`../knowledge/embedded-analytics-landscape-2026.md`](../knowledge/embedded-analytics-landscape-2026.md) — the per-viewer-pricing-trap zone with retrieval-dated figures
- [`../knowledge/ipaas-connector-landscape-2026.md`](../knowledge/ipaas-connector-landscape-2026.md) — Fivetran 2026 MAR change + Airbyte default
- [`../knowledge/data-platform-decision-trees.md`](../knowledge/data-platform-decision-trees.md) — the ELT-tool and BI/embed-tool decision trees
- [`../skills/stack-selection/SKILL.md`](../skills/stack-selection/SKILL.md) — the per-viewer-pricing heuristic table
- [`../hooks/flag-data-platform-smells.sh`](../hooks/flag-data-platform-smells.sh) — flags per-viewer-priced tools in decision-record templates

## Provenance

Distilled from CLAUDE.md house opinion #2 + #9 + anti-patterns (per-viewer pricing, Fivetran MAR), the `embedded-analytics-landscape-2026.md` per-viewer-trap zone, and `ipaas-connector-landscape-2026.md` (Fivetran 2026 deletes-count-as-MAR). `[verify-at-build]` every pricing figure here — Looker/Tableau/Sigma/Metabase/Fivetran/Airbyte tiers all move; re-confirm before quoting a client.

---

_Last reviewed: 2026-05-30 by `claude`_
