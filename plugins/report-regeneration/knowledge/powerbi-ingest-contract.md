# Power BI ingestion contract

> Phase-0 deliverable for the `powerbi-ingest` adapter (FORGE plan §2/§3/§4 — the raw
> planning record `plan.md` stays in the local `.ravenclaude/runs/forge/report-regeneration/`
> run dir, not committed; the committed spec is [`core-architecture-spec.md`](core-architecture-spec.md)).
> Power BI is an **input source only** — no PBIR/.pbix is parsed or emitted. This document settles
> **(a)** XMLA vs REST `executeQueries` (limits, auth, tenant settings), **(b)** how a pulled figure
> becomes a verifiable V1 source, **(c)** how the embedded screenshot is a `regenerate` asset guarded by
> the stale-screenshot period-coherence check, and **(d)** the auto-capture-vs-user-provided decision
> with graceful fallback. All web sources below were retrieved **2026-07-16** (this session); no claim
> here rests on training-data recall alone unless explicitly marked `[unverified]`.

---

## 1. Two REST endpoints, not one — the claims-table conflation, corrected

The plan's G1 claims table (claim 7) and the plugin's `plugin.json` description both refer to a single
"REST `executeQueries` (DAX) endpoint... returns Apache Arrow." **That conflates two distinct, currently
documented endpoints.** Corrected this session:

| | `executeQueries` (the one this probe calls) | `executeDaxQueries` (Arrow) |
|---|---|---|
| **Endpoint path** | `POST /v1.0/myorg/groups/{groupId}/datasets/{datasetId}/executeQueries` | `.../executeDaxQueries` |
| **Response format** | JSON (row-oriented) | Apache Arrow IPC only (columnar, streamed) |
| **Capacity requirement** | Works on **Pro, PPU, and Premium/Fabric** | **Premium or Fabric capacity only** |
| **Query input shape** | `queries[]` array, **one query per call** | single `query` string (multiple `EVALUATE` statements allowed) |
| **Row/value limit** | hard cap: **100,000 rows or 1,000,000 values per query, whichever is hit first**; **15 MB** per-query data cap | no fixed limit (use `resultsetRowcountLimit` to bound) |
| **Rate limit** | **120 query requests/minute/user**, regardless of dataset — documented explicitly | not documented in the fetched page `[unverified — not stated in the source below; do not assume it inherits 120/min]` |
| **Query language** | DAX only (no MDX/DMX/INFO) | DAX only |
| **Client library needed** | none — plain JSON over HTTPS, stdlib-parseable | **yes** — an Arrow library (`pyarrow`, `Apache.Arrow`, …) is required to deserialize the response |
| **Tenant setting(s)** | **Dataset Execute Queries REST API** (page text says "found under Integration settings"; the newer Arrow-overview page's comparison table says the *same-named* setting is "under Developer settings" — **the two MS Learn pages disagree on the settings blade name** `[unverified — MS Learn internal inconsistency, not resolved by this session's fetch; verify against the live Admin Portal before relying on it]`) | the same **Dataset Execute Queries REST API** setting **AND** **Allow XMLA endpoints and Analyze in Excel with on-premises semantic models** (an Integration setting) |
| **Auth (service principal)** | supported if the tenant's **Allow service principals to use Power BI APIs** (Developer settings) is on; SPNs are NOT supported for RLS-enabled or SSO-enabled datasets | same SPN caveat, "required only when authenticating with a service principal" |
| **Required scope** | `Dataset.ReadWrite.All` or `Dataset.Read.All` | not restated on the fetched page; assume the same `[unverified]` |

Sources (retrieved 2026-07-16):
- [Datasets — Execute Queries In Group](https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/execute-queries-in-group) — the JSON endpoint's full contract (limits, permissions, request/response shape).
- [Mastering the Execute DAX Queries REST API](https://learn.microsoft.com/en-us/power-bi/developer/execute-dax-queries-arrow/overview) — the Arrow endpoint + the side-by-side comparison table this section is built from.

**Why this matters for the plugin's macOS fallback design:** the plan's rev. 2 language ("macOS fallback
to the Power BI REST `executeQueries` (DAX) endpoint... Arrow results") describes the **Arrow** endpoint's
response format but the **JSON** endpoint's name and rate limit. The two do not compose — you cannot get
Arrow results from `executeQueries`. **The corrected fallback for a Pro/PPU tenant (i.e., a tenant that
does NOT have Premium/Fabric capacity, so XMLA and `executeDaxQueries` are both unavailable) is the plain
JSON `executeQueries` endpoint** — which is also the one this probe's `data` subcommand implements,
because it needs no Arrow library and works on the widest range of tenant tiers. A Premium/Fabric tenant
that specifically wants the Arrow endpoint's higher row ceiling and native typing can add an
`executeDaxQueries` branch later; it is not implemented in the Phase-0 probe.

---

## 2. XMLA — the confirmed tenant route, and why it has no macOS code path yet

**What XMLA requires (verified against the primary doc, retrieved 2026-07-16):**
- The workspace must be on a **Premium, Premium Per User (PPU), or Fabric capacity** — XMLA endpoints do
  not exist for a Pro-only workspace.
- The tenant-level setting **"Allow XMLA endpoints and Analyze in Excel with on-premises semantic
  models"** (an Integration setting) must be enabled — it is enabled by default.
- **Read-only** is enabled by default for the semantic-models workload; **read-write** must be explicitly
  turned on per capacity/PPU if metadata mutation is needed (the plugin only needs read-only — value
  pulls, never model writes).
- Client applications never talk to the XMLA endpoint directly; they go through **client libraries**
  — the same ones used for Azure Analysis Services / SQL Server Analysis Services (MSOLAP, AMO, ADOMD.NET).
  "Client libraries are updated monthly," and third-party tools "require the latest versions of MSOLAP
  client libraries, but some can use ADOMD."
- A specific version floor is documented for XMLA-based clients: **MSOLAP 17.0.40.18 or higher, ADOMD
  19.104.2.0 or higher.**

Source: [Semantic model connectivity and management with the XMLA endpoint in Power BI](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools) (retrieved 2026-07-16).

**Why no macOS-runnable native XMLA client exists today, concretely:**
- The popular Python wrapper is **`pyadomd`**, which loads the **classic .NET-Framework**
  `Microsoft.AnalysisServices.AdomdClient` assembly via `pythonnet`. That classic client library is
  Windows/.NET-Framework-only (COM-registered, no macOS build). `doctor.py` already labels `pyadomd`
  "EXPECTED-ABSENT on macOS."
- A **`.NetCore`** variant of the same client library does exist on NuGet
  (`Microsoft.AnalysisServices.AdomdClient.NetCore.retail.amd64`) — so the underlying protocol client
  is not architecturally Windows-only. But (a) its package name and published builds are **amd64-only**
  with no documented macOS or Apple-Silicon (ARM64) target `[unverified — not exhaustively checked
  against every published NuGet version; treat "no macOS build" as the working assumption until a
  specific version is confirmed to ship one]`, and (b) **no Python wrapper binds to it** — using it from
  Python on macOS would require hand-rolling a `pythonnet`-on-.NET-8 bridge, or shelling out to a small
  C#/.NET console helper, neither of which is in scope for a Phase-0 probe.
- **Net effect:** `powerbi_probe.py`'s `data` subcommand does **not** attempt XMLA. It documents this in
  its own docstring and always reports `route: null` for the XMLA leg — the REST `executeQueries` path
  is the only one it exercises. If a future revision adds a working macOS ADOMD.NET binding (e.g. via a
  shelled-out `dotnet` helper), it becomes a second attempted route inside `probe_data()`, tried first,
  falling through to REST on failure — but that is explicitly **out of scope for Phase 0**.

**Fail-closed consequence (binding, plan §3 "Fail-closed data-read degrade"):** on a tenant where neither
XMLA nor `executeQueries` is reachable, V1 (value accuracy) degrades from "recompute against source" to
"binding-correctness only," and the Accurate rubric dimension **fails closed to "unverified," never
PASS** for the affected nodes. The probe's `data` receipt's `verdict: "not_captured"` is exactly the
signal that should trigger this degrade in the fidelity harness (Phase 1+).

---

## 3. How a pulled figure becomes a verifiable V1 source

The report-regeneration plan's V1 leg ("did value V from source S land in region R?") requires a
**genuinely independent second execution path** — not the same inference/binding path that produced the
manifest. For a Power BI-sourced value, that second path is: **re-run the DAX query against the live
semantic model, right before the fidelity gate runs**, and compare.

```
manifest binding: node X <- DAX query Q, dataset D
                       │
                       ├── (binding-time) evaluate Q against D  →  value V_bound  →  written into output at anchor X
                       │
                       └── (V1-time, INDEPENDENT) re-execute Q against D via the SAME
                           `powerbi_probe.py data` path  →  value V_recomputed

           V1 PASS  iff  V_recomputed == V_bound  (typed-value compare, per plan §3 R9)
                     AND  V_bound appears at anchor X (position check)
                     AND  V_bound appears SOMEWHERE in the output (position-agnostic
                          set-membership — catches a mis-anchored value, plan §3 RT1-F5)
```

This qualifies as "partly inference-independent" exactly as the plan's V1 row states: the **recompute**
half is a real second query execution (not touching the classifier/manifest inference at all), while the
**set-membership** half is a pure string/typed-value scan (fully ML-free). Neither half depends on the
same model call that produced the binding, so V1 over a PBI-sourced node is one of the plan's stronger
legs, not a weaker one — **provided the recompute genuinely re-queries the model and does not read a
cached result from binding time.** `powerbi_probe.py data` never caches; every invocation is a fresh
HTTP round-trip, which is what makes it usable as the V1 recompute path.

**When there is no live route** (neither XMLA nor `executeQueries` reachable — auth expired, tenant
setting disabled, network unavailable), there is no second execution path to recompute against, so V1
cannot run at all for that node. Per plan §3 R14 (binding), this is not silently skipped: the Accurate
dimension is marked "unverified" for that node and the review-ready label is withheld until a human
either supplies the figure manually (labeled unverified) or the route is restored.

---

## 4. The screenshot is a `regenerate` asset — never transplanted, always period-coherence-guarded

**Why `regenerate`, not `frozen`/`surgical` (plan §2/§3, binding — RT1-F3):** any node that renders as a
raster or carries embedded binary data cannot be *proven* data-free by a text/AST scan — a transplanted
screenshot PNG carries the old client's `$1.23M` as pixels, invisible to every string-based check. So a
Power BI report visual embedded as an image is, by construction, **always** the `regenerate` class: it is
either freshly captured from the new source this run, or supplied by the human this run. It is **never**
copied forward from the old template, no matter how visually similar the new report would otherwise be.

**The stale-screenshot period-coherence check (plan §3, binding — R32/D14):** a successful capture is
*not* proof the screenshot is current. The check that gates shipping is:

1. Extract every reporting-period label present in the rendered output (e.g. a "Q4 2026" header near the
   image's anchor).
2. Determine the screenshot's **source period** — for an auto-captured image, this MUST come from
   provenance recorded at capture time (e.g. a timestamp query against the report/dataset, or a
   filter/slicer state visible in the capture), not assumed from "we captured it today."
3. Assert the image's source period matches the nearest governing label. A mismatch is a **BLOCKER**
   (D14) — a fresh "Q4 2026" header over a stale "Q3 2026" screenshot must not ship, even though the
   *capture itself* succeeded moments ago (the underlying report can still be showing a stale reporting
   period if the semantic model hasn't refreshed, or if the wrong bookmark/filter state was captured).

`powerbi_probe.py`'s `shot` receipt deliberately sets `"period_coherence_checked": false` on every
successful capture, with an inline comment that the caller MUST still run this check before the image
ships — the probe proves *capture feasibility*, not *period correctness*. Wiring the actual
period-coherence checker is a Phase-1+ harness concern (`report-fidelity-harness`), not this probe's job.

---

## 5. Auto-capture vs. user-provided — the decision, with graceful fallback

> **CORRECTION (2026-07-16, reconciled with the code — read this, not the ASCII below):** the PRIMARY capture route is the Power BI REST **`ExportToFile`** endpoint (server-side PNG render, service-principal/token auth, **no browser** — the maintainer's chosen "log in and grab" for a Premium/PPU/Fabric tenant), as implemented `ExportToFile`-first in `scripts/powerbi_probe.py` and `skills/powerbi-ingest/powerbi_ingest.py`. **Playwright is the FALLBACK only**, attempted if `ExportToFile` is unavailable/failed; a **user-provided image** is the always-available last resort. The flow diagram below depicts the Playwright fallback path and predates that decision — the code and §1 carry the authoritative `ExportToFile`-first ordering. (Tree redraw is a v0.2.0 doc-polish item.)

```
                    ┌─────────────────────────────┐
                    │ need a Power BI report image │
                    └───────────────┬─────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │ Is `playwright` importable AND  │
                    │ is POWERBI_REPORT_URL set AND   │
                    │ is POWERBI_SHOT_AUTH_TOKEN set? │
                    └───────┬─────────────────┬──────┘
                         yes│                  │no
                            ▼                  ▼
              ┌─────────────────────┐   ┌────────────────────────────┐
              │ attempt Playwright  │   │ verdict: not_captured       │
              │ capture (headless   │   │ fallback: ask the human for │
              │ Chromium, injected  │   │ a screenshot (always        │
              │ auth header)        │   │ available, no auth needed)  │
              └──────────┬──────────┘   └────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │ capture succeeded   │
              │ AND file is a real, │
              │ non-empty PNG?      │
              └───┬─────────────┬───┘
                yes│             │no
                   ▼             ▼
        ┌─────────────────┐  ┌────────────────────────────┐
        │ verdict: PASS   │  │ verdict: not_captured        │
        │ node_class:     │  │ fallback: ask the human for │
        │ regenerate      │  │ a screenshot                 │
        │ period_coherence│  └────────────────────────────┘
        │ _checked: false │
        │ (still pending) │
        └─────────────────┘
```

**Why no unauthenticated capture attempt (a deliberate design choice, not an oversight):** Power BI
Service reports are not publicly viewable by default. An unauthenticated `page.goto()` against a
published-report URL will almost always land on a Microsoft sign-in redirect, and headless Chromium will
happily "successfully" screenshot *that* — producing a **worse** failure than `not_captured`: a
plausible-looking PNG of a login page that could be mistaken for a real capture downstream. So
`probe_shot()` refuses to attempt the capture at all when `POWERBI_SHOT_AUTH_TOKEN` is absent, and reports
`not_captured` with the reason spelled out, rather than trying and risking a false-positive-shaped file.

**The always-available fallback is not a workaround — it is the plan's own design (plan §2/§4):** "the
user-provided image is the always-available fallback regardless" of whether Service auto-capture proves
feasible on macOS. `probe_shot()`'s `fallback` field names this path explicitly on every `not_captured`
receipt so a caller (or a human reading the JSON) never has to go look it up. A user-supplied image is
classed `regenerate` exactly like an auto-captured one, and is subject to the identical period-coherence
gate (§4 above) — there is no lower bar for a human-supplied screenshot.

---

## 6. What this contract does NOT settle (explicitly deferred)

- **Whether the client's actual tenant is Premium/PPU/Fabric or Pro-only** — this is the Phase-0 memo's
  job (plan §5-P0 "G0-b Power BI tenant/XMLA + screenshot-route probe"), not this document's. This
  contract describes what each route *requires*; it does not assert which route the specific client's
  tenant will support. That is `[verify-at-use]` once tenant details arrive.
- **The exact tenant-settings blade name** for "Dataset Execute Queries REST API" — MS Learn's own pages
  disagree (Integration settings vs. Developer settings, §1 above); verify directly in the Admin Portal
  when a real tenant is available rather than trusting either page's prose.
- **Whether `executeDaxQueries` (Arrow) carries the same 120/min rate limit as `executeQueries`** — not
  stated on the fetched page; do not assume it without a fresh check.
- **A working macOS-native XMLA client** — this remains a real gap (§2), not a solved problem. The REST
  fallback is what ships; XMLA is "confirmed as the route when the tenant supports it AND a macOS client
  exists," and the second half of that AND is currently false.
- **Wiring the period-coherence checker itself** — this is a Phase-1+ `report-fidelity-harness` concern;
  this probe only marks the field `false` so nothing downstream can mistake "captured" for "verified
  current."
