# G4a Critic Brief — Unified Data Hub Platform (correlated-error + premise attack)

> Authored neither plan. No third plan. Hunts the SPINE (where A and B agreed) — two models
> converging on overlapping training consensus is weak evidence, and that consensus was written for
> different products (multi-tenant SaaS / engineer-users), so the mismatch with THIS product (layman
> user, solo-consultant delivery) is where correlated errors hide.

## Correlated errors (both plans, identically wrong)
- **CE-1 / R2 — Vault shares one trust boundary with the analytics DB.** Both put the credential vault
  AND the analytics tables Claude/vibecoder write SQL against in **one Postgres**. App holds the
  plaintext DEK in memory; any path with DB-read + in-process memory (sync engine, dashboard data
  loader, a SQL-injected dashboard param) can decrypt. Failure: Claude writes
  `SELECT ... FROM credentials` into an Evidence page because it's in the same schema. **De-risk:**
  analytics role = distinct Postgres role with ZERO grant on the vault schema; ideally vault in a
  separate DB/instance. The OLTP/OLAP split should be a hard **security** boundary, not a perf one.
- **CE-2 / R3 — Per-customer KMS/IAM isolation silently collapses for a solo operator at N>3.** "KMS
  off the app DB" is true but the bootstrap secret just moved to an AWS access key on each VPS; hand-
  managing N KMS keys + N IAM principals means one over-broad/ reused policy lets instance 4 decrypt
  customer 3's KEK. Negative tests check "deny KMS → fail," never "instance B can't read instance A's
  key." **De-risk:** cross-tenant negative test in the provisioning gate; one reviewed IAM policy
  template, not a script flag.
- **CE-3 / R4 — Evidence static site ≠ "easy, customizable" for a NON-TECHNICAL viewer.** Both
  optimized Evidence for the Claude-*author*, not the layman *viewer* who wants filter/drill/group/
  export. Failure: "show me just Q2, West region" → "I'll have Claude rebuild it" — broken at the
  magic moment. **De-risk:** 1-hr spike on the real first customer's top-5 questions vs Evidence's
  input model; if ≥2 fail, add Metabase/Lightdash on the same marts as a **v1** decision (with its own
  scoped DB role per CE-1).
- **CE-4 / R6 — "Claude builds dashboards" — unpriced reproducibility, cost-at-N, Claude-dependency.**
  Per-customer LLM-authored dashboards drift (layout/labels/charts) with no shared template lineage;
  every filter/metric/schema change = another per-customer Claude invocation = uncounted recurring
  cost; vibecoder is hard-blocked when Claude is wrong/unavailable. The "platform identical /
  per-customer varies" bright line is applied to connectors but abandoned for dashboards. **De-risk:**
  versioned dashboard-**template** library as the source artifact (config-driven, renders without an
  LLM in the loop); Claude generates config + net-new only; put rebuild-cost in the DoD.
- **CE-5 / R5 — Per-instance ops tail is under-counted; only connector-maintenance was priced.** G1's
  B.4 anchored "maintenance" on connectors; both inherited it and ignored OS/Postgres/npm CVE
  patching, KMS rotation, backup-restore drills, TLS, monitoring × N. At N=8 the non-connector tail
  plausibly dominates B's 48hr/yr connector figure. **De-risk:** set an explicit ops ceiling; make
  `upgrade-all` + automated patching + restore-tests a first-class deliverable before scaling past ~3.
- **CE-6 / R7 — The SDK+registry mitigation is itself solo-operator platform infra that may not get
  built/sustained** — the same sustainability bet as the connectors it de-risks. A over-builds (manifest
  compiler + fleet advisory + canary from P2 = iPaaS-vendor-sized substrate); B under-builds (a JSON
  file won't carry fleet audit/rollback). **De-risk:** build 2 plain connectors, let one break in prod,
  MEASURE fix time, then decide registry depth from evidence (tie to B's DoD break-fix threshold).
- **CE-7 / R1 (sharpest premise attack) — the LAYMAN cannot create the OAuth *app registrations*.**
  Both designed only the easy end-user-consent flow (click→redirect→authorize). But that requires an
  OAuth **app** already registered in the provider's developer portal — Salesforce Connected App
  (admin-gated), QuickBooks/Intuit production app (review process, days), HubSpot app, Google consent-
  screen verification. That step is hard, per-provider, sometimes admin/review-gated, and designed by
  **neither** plan. Phase-1 acceptance ("layman completes OAuth for 2+ sources unassisted") **can't
  pass** for Salesforce/QuickBooks as written. **De-risk (reshapes architecture):** the consultant
  registers ONE OAuth app per provider (one client_id/secret per source, consultant-owned); the layman
  only ever does end-user consent. Flags: (a) introduces a **global** per-provider client_secret NOT
  per-customer-isolated (tension with CE-2); (b) Salesforce/QuickBooks may still need a consultant-run
  onboarding step — those sources are **not** layman-self-serve and must be designed as such.

## Premise verdict
Sound but mis-scoped: both bundled "connectors from scratch" (Matt's defensible pin + data-sovereignty
differentiator) WITH "build the connector PLATFORM infra from scratch" (the unexamined liability). The
billable core is **dashboards + data model** — name it, give it the effort; build connectors as a
bounded/curated/measured cost and platform infra REACTIVELY from measured pain. B's instinct (vendor
SDK clients + defer the compiler) is closer to right than A's full-compiler-from-P2.

## Risk matrix (High-prob cluster R1/R4/R5/R6 are ALL correlated — the spine, not the forks, holds the top risks)
| # | Risk | P | I | Type |
|---|------|---|---|------|
| R1 | Layman can't self-register OAuth apps (Salesforce/QuickBooks) → headline promise false | High | High | CE-7 |
| R2 | Vault & analytics share one trust boundary → SQL reads credential table | Med | High | CE-1 |
| R3 | Per-customer KMS/IAM isolation collapses at N>3 | Med | High | CE-2 |
| R4 | Static Evidence can't satisfy layman interactivity | High | Med | CE-3 |
| R5 | Per-instance ops tail overwhelms solo consultant ~N=5–10 | High | High | CE-5 |
| R6 | Dashboard drift + uncounted recurring LLM rebuild cost | High | Med | CE-4 |
| R7 | Connector break-fix is archaeology, not one-line edit (registry bet unproven) | Med | High | CE-6 |
| R8 | A over-builds infra before a customer validates shape | Med | High | A |
| R9 | B's JSON registry under-serves fleet audit/rollback at >2 instances | Med | Med | B |
| R10 | Reverse-ETL double-writes corrupt a customer's CRM | Low | High | shared-mitigated |
| R11 | Granola/Planhat/long-tail API + OAuth-app availability | Med | Med | shared (G1) |
| R12 | Metric drift across instances ("Revenue" means different things) | Med | Med | shared-mitigated |

## The ONE change that most improves the odds
**Resolve OAuth-app-ownership at G0 before architecture (R1/CE-7):** consultant registers one OAuth app
per provider; layman only does consent; Salesforce/QuickBooks explicitly flagged consultant-onboarded.
Upstream of everything — it determines whether the headline promise is true, reshapes the persona/UX,
forces the per-provider client_secret into the threat model, and makes the Phase-1 test real.
