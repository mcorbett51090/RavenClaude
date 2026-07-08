# NetSuite integration landscape — the gold-standard bar

> **Tier:** REFERENCE. This is the market-landscape catalog the `netsuite-close` build is judged against — the 20 integrations (10 external tools, 10 installable plugins/SuiteApps) a well-run NetSuite close ecosystem actually uses, plus the 12 criteria that separate a "gold-standard" integration from a brittle one.
>
> **Last reviewed:** 2026-07-07 · **Confidence:** the settled NetSuite platform facts (auth, SuiteQL, roles, native close) were retrieved from Oracle primary docs this session (2026-07-07) and are marked accordingly below. The two catalog tables (which vendor does what) are **TRAINING KNOWLEDGE, NOT browser-verified this session** — treat vendor *capability shape* (auth model, sync pattern, category) as durable and any specific claim about certification status, pricing, or SLA as `[unverified — settling gate]`. Re-verify against the vendor's current NetSuite-listing page before citing any of this externally (a partner deck, a vendor bake-off).

## Honest framing — read before using this catalog

This doc is **market context, not an endorsement or a procurement recommendation.** None of the 20 items below are bundled, wired, or tested by this plugin — the plugin wires exactly one of the 10 tool patterns (a governed ELT pull via SuiteQL) as a **reference implementation + offline harness**, described in [`../skills/netsuite-close/SKILL.md`](../skills/netsuite-close/SKILL.md). The value this plugin adds is **not** "governance NetSuite lacks" — NetSuite's native Period Close Checklist and Intelligent Close Manager already cover a lot of ground (see the whitespace section below). The value-add is an **ERP-neutral, tamper-evident control ledger** ([`close_state.py`](../scripts/close_state.py)) with NetSuite wired as the first source system, feeding a correctly-shaped trial balance via SuiteQL.

---

## 10 integrated tools (external systems that call NetSuite)

| Tool | What / mechanism | Auth | What makes it gold-standard | Close relevance |
|---|---|---|---|---|
| **Celigo integrator.io** | NetSuite-native iPaaS SuiteApp; pre-built "flows" for common object sync | OAuth2 / NetSuite-managed | Mature **error management**: bulk retry, auto-resolve rules, per-record error queue — the reference for error handling in this space `[unverified — settling gate]` | Movement-data template (the pattern other tools mirror for transactional sync) |
| **Workato** | General-purpose iPaaS; NetSuite "recipes" (pre-built automation templates) | OAuth2 M2M `[unverified — settling gate]` | Recipe marketplace + enterprise-grade orchestration across 1,000+ connectors, not NetSuite-only | Cross-system close orchestration (e.g., NetSuite ↔ HRIS ↔ CRM) |
| **Dell Boomi** | iPaaS; connects via SuiteTalk SOAP web services and SuiteQL | Token-based / OAuth2 `[unverified — settling gate]` | Account-level governance and process monitoring built for enterprise IT, not just finance | Large multi-subsidiary / multi-system integration landscapes |
| **Jitterbit** | iPaaS with a dedicated NetSuite connector | HMAC-SHA256 signed TBA `[unverified — settling gate]` | Purpose-built connector with pre-mapped NetSuite object schemas | Mid-market NetSuite-to-anything integration |
| **Fivetran** | Managed ELT; pulls via **SuiteAnalytics Connect** (JDBC) | Credentialed JDBC connection `[unverified — settling gate]` | **Incremental sync + cursor rollback** — the reference pattern for warehouse-bound extraction; this is **the ELT template** this plugin's `netsuite-close` skill follows conceptually | Landing NetSuite data in a warehouse for BI / consolidated reporting, not a direct close action |
| **Airbyte** | Open-source / managed ELT; also via SuiteAnalytics Connect | Credentialed JDBC connection `[unverified — settling gate]` | **CDC (change-data-capture) + schema evolution** handling — the self-hosted alternative to Fivetran's managed pattern | Same warehouse-landing use case, open-source / self-hosted preference |
| **FloQast** | Close-management platform; layers on top of the GL | SSO / OAuth2 `[unverified — settling gate]` | **Tie-out enforcement**, **changed-after-sign-off alerts**, and a **Completeness Check** — this is **the close-semantics template**: it defines what "gold-standard close governance" looks like at the workflow layer, which is the direct conceptual ancestor of this plugin's `close_state.py` submit/verify_source pinning | Close-task tracking, reconciliation sign-off, cross-system tie-out |
| **BlackLine** | Reconciliation & matching platform | SSO / OAuth2 `[unverified — settling gate]` | **Rule-based auto-certification** of low-risk reconciliations, freeing reviewer time for exceptions | Account reconciliation at scale, especially high-volume/high-count entities |
| **Trintech Cadency / Adra** | Reconciliation + close automation with **real-time two-way** NetSuite sync | Token/OAuth2 `[unverified — settling gate]` | **Journal-entry post-back** — writes JEs into NetSuite, not just reads from it; a rarer, higher-trust integration pattern | Automated reclass / adjusting entries flowing back into the GL |
| **Vena** | Excel-native FP&A / consolidation platform | OAuth2 `[unverified — settling gate]` | **COA-preserving consolidation** — keeps the native chart of accounts intact through roll-up, avoiding the "translate then reconcile" trap | Multi-entity consolidation for finance teams who live in Excel |

## 10 plugins / SuiteApps (installed into NetSuite)

| Plugin / SuiteApp | What / mechanism | Auth | What makes it gold-standard | Close relevance |
|---|---|---|---|---|
| **Period Close Checklist + Intelligent Close Manager** | Native NetSuite close task orchestration; 2026 R1 adds an **AI task board** `[unverified — settling gate]` | N/A (native) | Ships with the platform — no integration risk at all; the AI task board is the newest native investment in this space | The backbone every NetSuite close already runs on top of — see the whitespace section |
| **NetSuite Account Reconciliation** | EPM-based module for automated account matching | N/A (native EPM) | **Auto-match** built directly into the platform's own EPM suite, no external recon tool required | Alternative/complement to BlackLine/Trintech for shops that want to stay single-vendor |
| **Advanced Revenue Management (ARM)** | Native revenue-recognition engine | N/A (native) | Purpose-built for **ASC 606** multi-element arrangement recognition | Revenue-recognition schedules and reclass entries feeding the close |
| **Fixed Assets Management** | Managed bundle for asset lifecycle + depreciation | N/A (native bundle) | Native depreciation rollforward tied directly to the GL, no export/import step | Fixed-asset schedule that ties beginning + additions/disposals = ending |
| **Multi-Book Accounting** | Native module for parallel books (e.g., GAAP vs. tax vs. management) | N/A (native) | Lets one transaction post correctly to multiple books simultaneously, avoiding a shadow-ledger reconciliation | Dual-GAAP or tax-book divergence during close |
| **OneWorld consolidation** | Native multi-subsidiary consolidation via the **Elimination Subsidiary** construct | N/A (native) | Elimination entries live in their own dedicated subsidiary — auditable, isolated from operating subsidiaries' books | Intercompany elimination as part of the native close, the same job this plugin's `consolidate.py` performs for non-NetSuite GLs |
| **SuiteApprovals** | Free managed SuiteApp for approval routing | N/A (native, free) | **JE approval routing + SoD** built into the platform at no extra license cost | The native analog to this plugin's `close-approval-workflow` review→approve→lock spine |
| **FloQast for NetSuite** | Native SuiteApp wrapper around FloQast's close-management platform | OAuth2 (NetSuite-side) `[unverified — settling gate]` | Bidirectional sync so close tasks reference live NetSuite balances without manual export | In-NetSuite close-task tracking without leaving the ERP |
| **BlackLine for NetSuite** | Native SuiteApp wrapper around BlackLine's recon platform | OAuth2 (NetSuite-side) `[unverified — settling gate]` | Same bidirectional-sync pattern as FloQast, for reconciliation instead of task tracking | In-NetSuite reconciliation without a separate export step |
| **Avalara AvaTax for SuiteTax** | Native SuiteApp for tax calculation, integrated with NetSuite's SuiteTax engine | N/A (native integration) | Real-time tax calculation at transaction time, not a post-hoc reconciliation | Sales/use tax accuracy feeding tax-account balances at close |

---

## The 12 gold-standard criteria (the DoD checklist)

Use this to score any NetSuite integration — including this plugin's own `netsuite-close` build (see the honest disposition column).

| # | Criterion | What "meets it" looks like | This plugin's `netsuite-close` build |
|---|---|---|---|
| 1 | **Prebuilt / certified connector, no-code** | Install from a marketplace, configure via UI, no custom code | ❌ Reference-implementation Python, not no-code — deliberate: the plugin is a controls layer, not a connector vendor |
| 2 | **Wizard auth surviving token rotation** | Auth setup is a guided flow; the integration self-heals through token expiry/rotation | ⚠️ Partial — `oauth_client.py` handles the token *lifecycle* (persist-then-use, per-entity lock) programmatically; M2M has no rotation to survive (no refresh token) but cert renewal is manual (documented, not automated) |
| 3 | **Right API surface per operation** | Uses SuiteQL for queries, REST records for CRUD, SOAP only where SuiteQL/REST don't cover the object | ✅ SuiteQL for the TB pull, matching the operation to the surface |
| 4 | **Incremental sync + safe rollback + idempotent upsert** | Delta pulls, not full re-pulls; a failed sync can be retried without duplicating records | ⚠️ Partial — the TB pull is a full re-pull per close period (trial balances are inherently full-snapshot, not incremental); `close_state.verify_source` provides the rollback-relevant "did the source change" signal, not delta sync |
| 5 | **Per-record error isolation + retry/replay + auto-retry** | One bad record doesn't fail the whole batch; retries are automatic within policy | ✅ `oauth_client.py`'s error-cause routing (401/429/invalid_grant) + `suiteql.py`'s serial pager with `Retry-After` backoff; **not** per-record isolation (a TB pull is one query, not a batch of independent records) |
| 6 | **No-code field mapping + validation** | A UI lets a non-engineer map source fields to destination fields | ❌ `netsuite/column-map.json` is authored as JSON, not through a UI — consistent with the plugin's stdlib-only, no-UI posture |
| 7 | **Monitoring + alerting** | Sync failures page someone; dashboards show sync health | ⚠️ Partial — the `alert_hook` seam fires on `invalid_grant`/no-assertion-config; there is no dashboard, only hook-driven alerting |
| 8 | **Tie-out-to-GL enforcement** | The pulled data is proven to net/tie against the GL before it's trusted | ✅ `suiteql.tie_out()` — hard-fails (loud, non-zero) on a non-tying pull, never silently stages a broken TB |
| 9 | **Sign-off + changed-after-sign-off detection** | Once a preparer signs off, a later source change is flagged, not silently absorbed | ✅ `close_state.submit(source_tb_sha256=...)` + `verify_source()` — pins the TB hash at submit, flags drift on re-check |
| 10 | **Audit lineage** | Every number traces back to its source document/transaction | ⚠️ Partial — `gl_lineage.py` (built for the generic connector tier) provides drill-through when wired; the NetSuite-specific `netsuite_lineage.py` extends this for SuiteQL sourcing `[unverified — see deviation note in the SKILL.md]` |
| 11 | **Governance-aware throttling** | Respects the platform's concurrency/rate limits by design, not by accident | ✅ Serial paging (no fan-out) matches NetSuite's account-level concurrency governance |
| 12 | **Fast template deployment** | A new entity/subsidiary can be onboarded in hours, not weeks | ⚠️ Partial — the *recurring* close can approach a day once wired (see the honest close-in-a-day framing below); **initial** wiring (cert issuance, role provisioning) needs a NetSuite admin and change-control, measured in days, not hours |

**Reading the disposition column honestly:** a reference implementation should not claim ✅ on every row — several ⚠️/❌ rows above are the correct, honest self-assessment for a controls-layer reference build, not gaps to be embarrassed about. The rows that matter most for close integrity (3, 8, 9, 11) are ✅.

---

## What NetSuite does natively vs. this plugin's whitespace

NetSuite ships real close-management capability out of the box. Don't rebuild it — build on top of it.

**NetSuite native (don't rebuild):**
- **18-step Period Close Checklist** — the standard sequenced close task list `[unverified — settling gate]`
- **Intelligent Close Manager** (2026 R1) — adds an AI task board on top of the checklist `[unverified — settling gate]`
- **Period lock** — prevents posting to a closed period
- **FX revaluation** + **consolidated-rate calculation** — native multi-currency remeasurement
- **Intercompany elimination + adjustments** — via the OneWorld Elimination Subsidiary construct
- **Revenue recognition + reclass** — via Advanced Revenue Management (ASC 606)
- **Period-end journals** — native JE posting with a **gapless GL audit numbering** sequence

**This plugin's whitespace (the actual value-add):**
- **Segregation-of-duties sign-off + attestation** as an *ERP-neutral* control — `close_state.py`'s review→approve→lock state machine works identically whether the source GL is NetSuite, QBO, Xero, or Intacct
- **A cross-system, tamper-evident control ledger** — the append-only hash-chained audit log persists outside NetSuite, so the sign-off record survives even if the source system's own audit trail is disputed or unavailable
- **A correctly-shaped SuiteQL trial-balance feed** — the BS-cumulative/IS-period distinction (`suiteql.build_tb_query`) closes a specific, silent-wrong-number trap that a naive period-scoped query falls into
- **Board-ready output** — `controller_cycle.py`'s HTML close package is a single review surface a board or auditor can read without NetSuite access

**The honest framing (repeat, because it's easy to overclaim):** this is **not** "governance NetSuite lacks." It is an ERP-neutral control ledger, with NetSuite wired as the first source system. A shop running only NetSuite could reasonably ask "why not just use Intelligent Close Manager?" — the answer is that this plugin's control ledger travels with a multi-entity, multi-GL close (e.g., a NetSuite parent + a QBO-run subsidiary), which a NetSuite-native tool cannot span by definition.

---

## Sources (settled facts — Oracle primary, retrieved 2026-07-07)

- Oracle NetSuite — OAuth 2.0 M2M / client-credentials + X.509-signed JWT assertion setup; TBA (OAuth 1.0a) new-integration cutoff (2027.1) and support-window end (~2028.1)
- Oracle NetSuite — SuiteQL REST endpoint (`POST /services/rest/query/v1/suiteql`), `Prefer: transient` header, `limit`/`offset` paging, 100,000-result hard cap
- Oracle NetSuite — minimum role composition (REST Web Services, Log in using Access Tokens, SuiteAnalytics Workbook, Lists→Accounts View, subsidiary)
- Oracle NetSuite — Period Close Checklist (18 steps) + Intelligent Close Manager (2026 R1)

## Sources (vendor catalog — training knowledge, re-verify before external use)

- Vendor NetSuite-integration listing pages for Celigo, Workato, Boomi, Jitterbit, Fivetran, Airbyte, FloQast, BlackLine, Trintech, Vena — capability descriptions are `[unverified — settling gate]`; auth mechanisms and integration patterns are directionally durable but specific claims (certification tier, pricing, SLA) need a browser check before citing externally
- NetSuite SuiteApp marketplace listings for Account Reconciliation, ARM, Fixed Assets Management, Multi-Book Accounting, SuiteApprovals, FloQast/BlackLine/AvaTax SuiteApps — `[unverified — settling gate]`
