# PSM Command Center — Deployment Notes

> How to host the PSM Command Center rendering layer at each tier of the migration path. One section per tier; cost / complexity / governance comparison at the bottom.
>
> Source research: [`rendering-layer.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/rendering-layer.md) §§1.1, 1.5, 1.6, 3, 6. The tiering matches §5 "Migration paths (Evidence v0 → Superset v1 → multi-tenant v2)".

---

## Tier 1 — Single PSM (Evidence.dev → Cloudflare Pages)

**When to use:** today's reality is one PSM, hourly refresh is acceptable, $0 license budget. Per `rendering-layer.md` §6: "Evidence buys you a polished, version-controlled console in 2–4 hours, costs nothing, and locks you into nothing."

### Architecture

```
Snowflake (warehouse)
   │  build-time SQL (creds via env)
   ▼
Evidence (npm run build)
   │  static HTML + baked query results
   ▼
Cloudflare Pages (static host)
   │  basic-auth or IdP proxy
   ▼
PSM browser (one user)
```

The published static site **never holds warehouse credentials** — queries run at build time and bake into the HTML output. The deploy artifact is plain HTML + JS + JSON data files. See `rendering-layer.md` §1.1.

### Hosting

**Cloudflare Pages** is the recommended target — free tier covers a single-PSM project comfortably ($0/mo), and it ships first-class scheduled builds via `Settings > Builds > Cron`.

Hourly refresh is the sweet spot per `rendering-layer.md` §1.1: "Static-site model means rebuild → redeploy. 10-min refresh = scheduled build every 10 min, which is workable but wasteful. Better fit: hourly."

### GitHub Actions workflow (hourly cron)

Drop the following at `.github/workflows/evidence-build.yml` of the consumer repo:

```yaml
name: Evidence build + Cloudflare Pages deploy

on:
  schedule:
    - cron: "0 * * * *" # hourly, on the hour, UTC
  workflow_dispatch: {} # manual trigger button in the Actions tab
  push:
    branches: [main]
    paths:
      - "plugins/edtech-partner-success/dashboard-evidence/**"

permissions:
  contents: read
  deployments: write

concurrency:
  group: evidence-build-${{ github.ref }}
  cancel-in-progress: false # never cancel a build mid-Snowflake-query

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20 # bounded so a Snowflake hang never burns Actions minutes
    env:
      # Snowflake creds come from repo secrets — never committed.
      SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
      SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
      SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
      SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
      SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
      SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: plugins/edtech-partner-success/dashboard-evidence/package-lock.json

      - name: Install Evidence deps
        working-directory: plugins/edtech-partner-success/dashboard-evidence
        run: npm ci

      - name: Build site (queries Snowflake at build time)
        working-directory: plugins/edtech-partner-success/dashboard-evidence
        run: npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: >-
            pages deploy plugins/edtech-partner-success/dashboard-evidence/build
            --project-name=psm-command-center
            --branch=main
```

**Auth at the edge:** Cloudflare Access (Zero Trust) wraps the Pages URL with SSO or one-time-PIN email auth. Configure via the Cloudflare dashboard; no code change needed.

### Cost (Tier 1)

| Line item | Monthly |
|---|---|
| Cloudflare Pages (free tier) | $0 |
| GitHub Actions (≤24 runs × ~5 min) | $0 (well under the 2000-min free tier) |
| Snowflake compute (24 small build queries) | ~$5–20 |
| Evidence.dev (OSS, local build) | $0 |
| **Total** | **~$5–20/mo** |

### Governance posture (Tier 1)

- Single PSM → single Cloudflare Access policy → no per-user RLS needed.
- Warehouse creds are GitHub Actions secrets; rotation is GitHub UI + a Snowflake `ALTER USER`.
- Build logs are GitHub Actions artifacts (90-day default retention).
- No PII exfiltration risk — the static site holds query *results* only; the SQL never runs client-side.

### When to migrate (out of Tier 1)

Per `rendering-layer.md` §5: "'Three users want different views of the same dashboard' → time to move v0 → v1." Tier 1 ends when (a) a second PSM joins, (b) sub-hour refresh becomes load-bearing, or (c) the renewal-cycle live-ops panel ships (which Tier 2 owns).

---

## Tier 2+ — Live operational panel (Streamlit-in-Snowflake)

**When to use:** the renewal-cycle live ops panel needs sub-hour refresh AND the operational data lives in Snowflake AND the PSM is already a Snowflake user. Per `rendering-layer.md` §6: "If sub-hour refresh is load-bearing (it is, per the spec), keep Evidence for the narrative/snapshot pages and add **Streamlit-in-Snowflake for the live operational panels**."

### Architecture

Streamlit-in-Snowflake (SiS) runs **inside** Snowflake — no egress, no warehouse-creds-in-app, packages from the Snowflake Anaconda channel. The PSM is already authenticated as a Snowflake user via Snowsight, so the auth surface collapses to zero. See `rendering-layer.md` §1.5.

```
PSM (Snowflake user, Snowsight session)
   │  Streamlit app loads from a Snowflake stage
   ▼
SiS runtime (warehouse-attached)
   │  st.cache_data + st.fragment for the 10-min refresh loop
   ▼
Snowflake tables / views (caller-rights queries)
```

### Stage + Streamlit object creation (Snowflake SQL)

Run as a role that owns the target schema (or has the equivalent `CREATE STREAMLIT` privilege):

```sql
-- 1. Database + schema that holds the operational console.
--    Use a dedicated schema so RBAC grants stay scoped.
CREATE DATABASE IF NOT EXISTS PSM_CONSOLE;
CREATE SCHEMA IF NOT EXISTS PSM_CONSOLE.LIVE_OPS;

-- 2. A dedicated warehouse, XS, auto-suspend 60s.
--    Keeps the bill bounded; the live panel rarely needs a hot warehouse.
CREATE WAREHOUSE IF NOT EXISTS PSM_CONSOLE_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'PSM Command Center live ops panel — see deployment-notes.md';

-- 3. Internal stage holding the Streamlit app source files
--    (streamlit_app.py + environment.yml + assets).
CREATE STAGE IF NOT EXISTS PSM_CONSOLE.LIVE_OPS.APP_STAGE
    DIRECTORY = ( ENABLE = TRUE )
    COMMENT = 'Source files for the PSM live ops Streamlit app';

-- 4. Upload app source to the stage from your local machine:
--      PUT file://plugins/edtech-partner-success/dashboard-streamlit-reference/app.py
--          @PSM_CONSOLE.LIVE_OPS.APP_STAGE
--          AUTO_COMPRESS = FALSE
--          OVERWRITE = TRUE;
--      PUT file://plugins/edtech-partner-success/dashboard-streamlit-reference/environment.yml
--          @PSM_CONSOLE.LIVE_OPS.APP_STAGE
--          AUTO_COMPRESS = FALSE
--          OVERWRITE = TRUE;
--    (Run from snowsql; do NOT use the Snowsight UI — it re-encodes line endings.)

-- 5. Create the Streamlit object.
--    NOTE on owner-rights vs caller-rights — see governance pitfall below.
CREATE OR REPLACE STREAMLIT PSM_CONSOLE.LIVE_OPS.LIVE_PANEL
    ROOT_LOCATION = '@PSM_CONSOLE.LIVE_OPS.APP_STAGE'
    MAIN_FILE = 'app.py'
    QUERY_WAREHOUSE = PSM_CONSOLE_WH
    COMMENT = 'PSM live ops panel — Tier 2 of the rendering migration';

-- 6. Grant USAGE so the PSM role can open the app from Snowsight.
GRANT USAGE ON DATABASE PSM_CONSOLE TO ROLE PSM_ROLE;
GRANT USAGE ON SCHEMA PSM_CONSOLE.LIVE_OPS TO ROLE PSM_ROLE;
GRANT USAGE ON WAREHOUSE PSM_CONSOLE_WH TO ROLE PSM_ROLE;
GRANT USAGE ON STREAMLIT PSM_CONSOLE.LIVE_OPS.LIVE_PANEL TO ROLE PSM_ROLE;
```

### Governance pitfall — owner-rights vs caller-rights

`rendering-layer.md` §1.5 cites Ignatius Soputro's Feb 2026 SiS review (Medium, "Evaluating Streamlit in Snowflake (SiS): the Good, the Bad, and the Ugly"):

> SiS uses Snowflake's RBAC — your PSM is already authenticated as a Snowflake user. **For multi-tenant you need caller-rights setup or one-app-per-tenant.** The app runs as the owner's identity, not the caller's.

**The consequence for a single PSM (Tier 2):** owner-rights is *fine* — the PSM is the owner. Switch to **caller-rights** as soon as a second user has even read access, otherwise the second user's queries silently execute as the original owner and any column-level masking / row-access policies tuned to *their* role do not apply.

To make the app run **as the calling user** (recommended for any deployment with >1 viewer):

```sql
-- Caller-rights execution — the app runs in the session of whoever opened it.
-- This is the correct setting for any deployment where viewers have different RBAC.
ALTER STREAMLIT PSM_CONSOLE.LIVE_OPS.LIVE_PANEL
    SET RUN_AS_OWNER = FALSE;

-- Verify (any of these confirm the switch):
SHOW STREAMLITS LIKE 'LIVE_PANEL' IN SCHEMA PSM_CONSOLE.LIVE_OPS;
-- Look for OWNER_ROLE_TYPE = 'CALLER' in the output.
```

The default is owner-rights. **Flip it before adding a second user**; the Soputro review names this as the most common SiS production trap.

### Refresh cadence in the app

Per `rendering-layer.md` §1.5: "`st.cache_data(ttl=600)` plus auto-rerun; or scheduled refresh. SiS runs serverless." The reference [`dashboard-streamlit-reference/app.py`](../dashboard-streamlit-reference/app.py) uses 10-minute cache for KPI cards (cheap warehouse queries) and 1-minute cache for the live action-center queue, plus `@st.fragment(run_every=60)` to avoid full-app reruns.

### Cost (Tier 2)

| Line item | Monthly |
|---|---|
| Snowflake compute (XS warehouse, ~8h business hours × 22 days) | ~$50–200 |
| Streamlit-in-Snowflake (included in Snowflake bill) | $0 incremental |
| Cloudflare Pages (still hosts the Tier 1 narrative pages) | $0 |
| **Total** | **~$50–200/mo** |

Numbers from `rendering-layer.md` §3 cost matrix row "Streamlit-in-Snowflake."

### Governance posture (Tier 2)

- Auth is Snowflake RBAC — no separate identity provider to integrate.
- Caller-rights execution + Snowflake row-access policies = real per-user isolation.
- Egress: zero. The app runs inside Snowflake.
- **Pitfall:** owner-rights default (Soputro, see above). Flip before viewer #2.
- **Limitations:** 32 MB single-command output cap; packages constrained to Snowflake Anaconda channel in warehouse runtime ([SiS limitations doc](https://docs.snowflake.com/en/developer-guide/streamlit/limitations)).

---

## Tier 5+ — Productized SaaS (React + Tremor + Cube on Vercel)

**When to use:** the console becomes a customer-facing product with N tenants, hard per-tenant row-level security from day 1, mobile-first PSMs, custom branding. Per `rendering-layer.md` §6: "When/if productizing: Cube + Tremor is the textbook multi-tenant pattern."

### Architecture (the JWT + Cube securityContext pattern)

`rendering-layer.md` §1.6 cites Querio's multi-tenant embedded analytics architecture as the textbook reference:

```
Browser (React + Tremor UI, mobile-first via Tailwind)
   │  Authorization: Bearer <JWT with tenant_id claim>
   ▼
Vercel (Next.js — JWT issuance + Cube proxy)
   │  passes JWT as securityContext to Cube
   ▼
Cube (semantic layer; speaks Snowflake natively)
   │  pre-aggregations cached in Cube Store
   ▼
Snowflake (one warehouse, partitioned-by-tenant_id tables)
```

### JWT + Cube securityContext pattern

```javascript
// 1. JWT issuance — Next.js API route (e.g. app/api/auth/token/route.ts).
//    The tenant_id claim is what Cube reads as securityContext.tenant_id.
import jwt from "jsonwebtoken";

export async function POST(req) {
  const { user } = await authenticate(req); // Auth0 / Clerk / NextAuth
  const token = jwt.sign(
    {
      sub: user.id,
      tenant_id: user.tenant_id, // ← drives RLS in Cube
      role: user.role, // ← drives column masking in Cube
      exp: Math.floor(Date.now() / 1000) + 60 * 60, // 1h TTL
    },
    process.env.CUBE_JWT_SECRET,
  );
  return Response.json({ token });
}
```

```javascript
// 2. Cube config — cube.js (server-side).
//    securityContext.tenant_id flows from the JWT claim above.
module.exports = {
  contextToAppId: ({ securityContext }) =>
    `CUBEJS_APP_${securityContext.tenant_id}`,
  preAggregationsSchema: ({ securityContext }) =>
    `pre_aggregations_${securityContext.tenant_id}`,
  queryRewrite: (query, { securityContext }) => {
    if (!securityContext.tenant_id) {
      throw new Error("tenant_id missing from JWT — refusing query");
    }
    // Inject RLS filter into every query, regardless of what the React app asked for.
    query.filters = query.filters || [];
    query.filters.push({
      member: "Partners.tenant_id",
      operator: "equals",
      values: [securityContext.tenant_id],
    });
    return query;
  },
};
```

```typescript
// 3. React app — fetch with the JWT.
//    Tremor cards render the Cube response; URL state is filter persistence.
import { CubeProvider } from "@cubejs-client/react";
import cubejs from "@cubejs-client/core";

const cubeApi = cubejs(
  async () => {
    const res = await fetch("/api/auth/token", { method: "POST" });
    const { token } = await res.json();
    return token;
  },
  { apiUrl: process.env.NEXT_PUBLIC_CUBE_API_URL },
);

export default function App() {
  return <CubeProvider cubejsApi={cubeApi}>{/* Tremor cards */}</CubeProvider>;
}
```

### Hosting

- **Vercel** for the Next.js app (Tremor + Cube client). ~$20/mo Pro tier covers a single-customer rollout; Vercel acquired Tremor (Oct 2025) so the chart-component story is first-party. See `rendering-layer.md` §1.6.
- **Cube** either self-hosted (Apache 2.0, OSS) or Cube Cloud (consumption-based, $0 starting). Cube case study claims 2× Snowflake cost reduction via pre-aggregations.

### Cost (Tier 5)

| Line item | Monthly (1 customer) | Monthly (10 customers) |
|---|---|---|
| Vercel Pro | $20 | $20 (same project) |
| Cube Cloud (consumption) | $0–50 | $200–500 |
| Snowflake (with Cube pre-aggregations — 2× cheaper) | $X / 2 | $X / 2 × 10 |
| **Engineering weeks (one-time)** | **2–10 weeks** | n/a |

Numbers from `rendering-layer.md` §3 cost matrix row "React + Tremor + Cube OSS."

### Governance posture (Tier 5)

- JWT lifetime (1h default) — short enough that revocation latency is bounded.
- Cube `queryRewrite` is the **non-bypassable** RLS injection point. The React app *cannot* ask for cross-tenant data; the rewrite layer rejects.
- Vercel preview deployments inherit the same JWT issuance — no test-env credential leak.
- Audit log: Cube logs every query with `securityContext`; ship to Snowflake or a SIEM.
- **Pitfall:** Cube schema mistakes (join cardinality, pre-aggregation tuning) silently produce wrong numbers per `rendering-layer.md` §4 Codex-buildability ranking #7. A Cube schema review (cardinality + null handling per dimension) is mandatory before customer #1.

---

## Tier comparison — cost / complexity / governance

Single-PSM column matches `rendering-layer.md` §3 "Single PSM" column verbatim; SaaS columns are the 10-tenant and 100-tenant cells.

| Dimension | **Tier 1 — Evidence + Cloudflare Pages** | **Tier 2 — Streamlit-in-Snowflake** | **Tier 5 — React + Tremor + Cube + Vercel** |
|---|---|---|---|
| **Cost (1 PSM)** | ~$5–20/mo (mostly Snowflake build queries) | ~$50–200/mo (XS warehouse) | ~$20/mo Vercel + Cube + engineering weeks |
| **Cost (10 tenants)** | $50/mo per-tenant builds — operationally heavy | Same — Snowflake credit-scaled | $200–500/mo Cube + Vercel + Snowflake |
| **Cost (100 tenants)** | Switch to dynamic renderer | Per-tenant role isolation needed | Same architecture; Cube Cloud or self-host |
| **Time to first dashboard** | 2–4 hours | 3–8 hours | 2–10 days |
| **Auth (single user)** | Cloudflare Access basic-auth or SSO | Snowflake RBAC (no separate auth) | Bring-your-own (Auth0/Clerk/NextAuth) |
| **Auth (multi-tenant)** | Per-build site or token-gated routes | Caller-rights + Snowflake row-access policies | JWT `tenant_id` claim → Cube `securityContext` → query-time RLS |
| **Refresh cadence** | Hourly (rebuild + redeploy) — sub-hour is wasteful | Sub-minute with `st.fragment(run_every=60)` | Cube pre-aggregations on schedule + React polling |
| **Mobile responsive** | Built-in Evidence responsive grid | Weak — documented limitation ([Streamlit #6592](https://github.com/streamlit/streamlit/issues/6592)) | Excellent — Tremor is Tailwind, mobile-first by default |
| **Lock-in** | Low — SQL + Markdown are trivially portable | Medium-high — SiS-specific package channel + 32 MB cap | Low — every layer OSS + swappable |
| **Codex-buildability** | Very high (small component surface) | Highest — `streamlit/agent-skills` first-party | High (UI) / medium (Cube schema is the failure mode) |
| **Governance pitfall to watch** | Build creds in GH Actions secrets — rotate quarterly | **Owner-rights vs caller-rights** (Soputro Feb 2026) — flip before viewer #2 | Cube schema cardinality silently wrong numbers — schema review mandatory |
| **Egress** | Build-time only (zero at runtime) | Zero (runs inside Snowflake) | Cube proxies all Snowflake queries; JWT-gated |
| **Audit trail** | GitHub Actions build logs (90d) | Snowflake `QUERY_HISTORY` view | Cube query log + Vercel access log |
| **When to migrate up** | Second PSM joins / sub-hour live-ops needed | Customer-facing product / hard RLS / mobile-first | n/a (top of the path) |

---

## When to skip a tier

`rendering-layer.md` §6 counter-arguments considered and rejected:

- **"Pure React + Cube from day 1, skip Evidence."** Wastes 1–2 weeks before any value lands. Migrating SQL files is cheap; building UI from scratch is not.
- **"Superset has guest tokens and RLS today, just start there."** Five processes for one PSM is operational waste; Superset mobile is weaker than Tremor. Acceptable for an internal v1 scale-up; over-built for v0.
- **"Metabase Cloud Pro at $575/mo is a one-shot answer."** It is — pick this if engineering time is the bottleneck and the team would rather not write Markdown components.

---

## Sources

All claims trace to [`rendering-layer.md`](../../../../docs/research/2026-06-04-psm-dashboard-research/rendering-layer.md):

- **§1.1** Evidence.dev platform deep-dive (Snowflake build-time queries, Pages auth, hourly cadence sweet spot).
- **§1.5** Streamlit-in-Snowflake (caller-rights vs owner-rights — Soputro Feb 2026 review; `st.cache_data` + `st.fragment`; 32 MB cap; SiS limitations doc).
- **§1.6** React + Tremor + Cube (JWT + `securityContext` pattern via Querio multi-tenant architecture; Tremor Vercel-acquired Oct 2025; Cube Snowflake 2× cost-reduction case study).
- **§3** Cost model side-by-side (the per-tenant cost cells).
- **§6** Specific recommendation for the PSM Command Center (the migration narrative + counter-arguments).
