# Data-store selection decision trees — Dataverse vs Dataverse for Teams vs Lists vs Excel

> Canonical decision tree for the **upstream** data-platform choice: *before* any table is modeled, which store should hold the data? This is the question that precedes everything in [`dataverse-decision-trees.md`](dataverse-decision-trees.md) (which decides *within* Dataverse once it's chosen). Format follows the marketplace convention in [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md): observable entry condition, `Last verified:` date, a Mermaid flowchart, per-leaf rationale, and a tradeoffs table. **Traverse top-to-bottom before selecting a store — do NOT pattern-match on keywords in the user's situation description; the first branch whose condition resolves cleanly is the leaf to apply.**
>
> Owned by `dataverse-architect`; secondary `power-platform-admin` (capacity/licensing), `power-fx-engineer` / `model-driven-engineer` (the app that consumes the store). The Power-Automate-vs-Logic-Apps integration-platform tree lives in [`flow-decision-trees.md`](flow-decision-trees.md) (`## Decision Tree: Integration platform — Power Automate cloud flow vs Azure Logic Apps`) and is the canonical owner of that branch — this file does not duplicate it, only points at it.

---

## Decision Tree: Data store — Dataverse vs Dataverse for Teams vs Lists vs Excel

**When this applies:** you are starting a new app/solution (or re-platforming one) and must pick where the data lives. Observable triggers: "should this be Dataverse or SharePoint?", "can we just use a list?", "we have a 50,000-row Excel workbook to turn into an app", "the client wants a Teams app for the team". Not for choosing a column type or relationship *inside* Dataverse (that's [`dataverse-decision-trees.md`](dataverse-decision-trees.md)).

**Last verified:** 2026-06-08 against Microsoft Learn [*Comparing Microsoft Lists, Dataverse for Teams, and Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/compare-data-sources) (first-party, `updated_at 2025-05-07`) and [*Dataverse for Teams vs. Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/data-platform-compare) (first-party). Capacity numbers and licensing are volatile — `[verify-at-use]`. Research: `docs/research/2026-06-08-power-platform-best-practices/` (local-only, not committed).

```mermaid
flowchart TD
    START[New app / solution — pick the data store] --> Q0{Is the data CURRENTLY in Excel / a flat file?}
    Q0 -->|YES| MIGRATE["Excel is a MIGRATION SOURCE, not a backend<br/>— continue the tree to pick the real store"]
    Q0 -->|NO| Q1
    MIGRATE --> Q1{Need ANY of: auditing · field-level/hierarchical security · business units · CMK ·<br/>plug-ins · multi-environment managed-solution ALM ·<br/>a surface beyond Teams (Power Pages / model-driven / Dynamics 365)?}
    Q1 -->|YES| DV["Dataverse (full)<br/>— only it offers these"]
    Q1 -->|NO| Q2{Is the data RELATIONAL (real relationships, lookups, business rules)?}
    Q2 -->|NO — flat tracking list| Q3{Volume + write pattern within SharePoint's healthy range?<br/>(lightweight tracking, not a high-write transactional app)}
    Q3 -->|YES| LISTS["Microsoft Lists / SharePoint<br/>(flat data, Teams/Lists/custom-code surface)"]
    Q3 -->|NO — transactional / past a few thousand rows| DV2["Dataverse (full)<br/>— SharePoint is not a transactional DB at scale"]
    Q2 -->|YES — relational| Q4{Teams-scoped app, < ~1M rows, no premium license,<br/>one unmanaged solution per env acceptable?}
    Q4 -->|YES| DFT["Dataverse for Teams<br/>(relational, Teams-only, included w/ qualifying M365+Teams)"]
    Q4 -->|NO| DV3["Dataverse (full)<br/>— scale / licensing / ALM / surface exceeds for-Teams"]
```

**Rationale per leaf:**

- *Excel = migration source (MIGRATE)* — Excel appears in the comparison only as an *import/export* path, never as a data-source column; a workbook is a migration target, not a store. This plugin routes "migrate this 50,000-row Excel workbook" to `dataverse-architect` first (CLAUDE.md §2). `[Excel-as-backend exclusion is inference from the comparison page's framing + CLAUDE.md §4 anti-pattern, not a single quoted sentence.]`
- *Dataverse full (DV / DV2 / DV3)* — the **only** store offering auditing, field-level/hierarchical security, business units, CMK, plug-ins, unlimited managed-solution ALM, and surfaces beyond Teams (Power Pages, model-driven, Dynamics 365). Required the moment any of those is in scope, or when SharePoint would be a transactional DB at scale, or when a relational app exceeds for-Teams limits. **requires:** appropriate Power Apps / Dataverse capacity + premium licensing `[verify-at-use]`.
- *Dataverse for Teams (DFT)* — relational storage for a **Teams-scoped** app, up to ~1M rows / 2 GB per team, included with qualifying M365 + Teams (no premium Power Apps license for in-Teams use), but **Teams-only** surface and **one unmanaged solution per environment**. Upgradeable in place to full Dataverse when you outgrow it ("more granular control for security and governance, or capacity beyond the approximately 1 million rows" — first-party). **requires:** Teams + qualifying M365.
- *Microsoft Lists / SharePoint (LISTS)* — flat, lightweight team tracking (up to 30M rows, but >100k needs indexing/large-list discipline), surfaced in Lists/Teams/custom-code. Not for relational integrity or high-write transactional apps.

**Tradeoffs summary:**

| Store | Data shape | Capacity | Security depth | Surfaces | ALM | Use when |
|---|---|---|---|---|---|---|
| Microsoft Lists / SharePoint | Flat (File, Image) | 30M rows (>100k indexed) | Site roles + custom perms | Lists, Teams, custom code | Package & deploy Lists | Lightweight flat team tracking |
| Dataverse for Teams | Relational | ~1M rows / 2 GB/team | Owner/Member/Guest + Entra group | **Teams only** | 1 unmanaged solution / env | Relational Teams app, no premium license |
| Dataverse (full) | Relational + Lake/Log/Virtual | No specified row limit | Roles, BUs, auditing, FLS, hierarchical, CMK | Teams, Apps, **Pages, D365**, code | Unlimited managed ALM | Enterprise security / scale / ALM / non-Teams surface |
| Excel | — | — | — | — | — | **Never a backend** — migration source only |

First branch that resolves cleanly wins. The order front-loads the two cheapest-to-get-wrong forcing conditions: "is this Excel?" (re-frame to a real store) and "does it need enterprise security/ALM/non-Teams surface?" (only full Dataverse). This tree is the **upstream** of [`dataverse-decision-trees.md`](dataverse-decision-trees.md) — once it terminates on a Dataverse leaf, those trees decide column types, relationships, security mechanism, and logic placement within it.

---

## Citations / sources

- Store-selection tree: Microsoft Learn [*Comparing Microsoft Lists, Dataverse for Teams, and Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/compare-data-sources) (first-party, `updated_at 2025-05-07`) — the full comparison table (data types, capacity, security, clients, ALM, pro-dev) — and [*Dataverse for Teams vs. Dataverse*](https://learn.microsoft.com/en-us/power-apps/teams/data-platform-compare) (first-party) — the ~1M-row / 2 GB-per-team capacity, one-environment-per-team model, and the upgrade trigger. Both retrieved 2026-06-08; corroborated in `docs/research/2026-06-08-power-platform-best-practices/` (local-only, not committed).
- Adjacent named rule: [`../best-practices/data-store-dataverse-vs-sharepoint-vs-teams.md`](../best-practices/data-store-dataverse-vs-sharepoint-vs-teams.md).
- Within-Dataverse decisions (downstream): [`dataverse-decision-trees.md`](dataverse-decision-trees.md). Integration-platform decision (sibling): [`flow-decision-trees.md`](flow-decision-trees.md) `## Decision Tree: Integration platform — cloud flow vs Azure Logic Apps`.
- Decision-tree format convention: [`../../../docs/best-practices/decision-trees-in-knowledge-files.md`](../../../docs/best-practices/decision-trees-in-knowledge-files.md).
