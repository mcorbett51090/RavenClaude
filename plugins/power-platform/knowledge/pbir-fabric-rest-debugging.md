# PBIR / Fabric / Dataverse — REST API as the FIRST debugging move

> **Last reviewed:** 2026-06-04. Source: production session on the BMA-CSP-Risk-Scoring report (Bermuda Monetary Authority CSP engagement, `mcorbettbma/BTCSIReporting`, 2026-06-04). Multiple debugging cycles were resolved much faster by querying the dataset directly via Fabric REST API than by iterating deploy → check in PBI Desktop → redeploy. Refresh when (a) the Fabric REST endpoint shape changes, (b) `executeQueries` adds/removes capabilities, or (c) the Dataverse Web API version surfaces a new debugging anchor.
>
> **Claim-grounding note.** The endpoint paths, auth chain, and `executeQueries` payload shape below were used in production on 2026-06-04 against the BMA-CSP dataset. They are also documented on Microsoft Learn (the `executeQueries` REST API has been GA since 2021). Specific scope strings (`https://analysis.windows.net/powerbi/api/.default`, `https://api.fabric.microsoft.com/.default`) match what `az account get-access-token --resource ...` accepts in `az` CLI v2.50+ — [verify-at-use] for the exact `az` version on the consumer's machine. The "tokens cached in `~/.azure/msal_token_cache.json` on Linux/macOS as plaintext" caveat is the same one documented in [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md).
>
> **When to read this file.** **The portal UI is hiding/rewriting the real error.** Power BI Desktop, the Fabric portal, the PBIR loading dialog — all of them collapse or paraphrase the real error envelope the engine returned. The REST API returns it verbatim. If a measure is silently returning BLANK / 0, if a visual is silently blank with valid JSON, if a deploy "succeeded" but the report renders wrong, if a flow run "succeeded" with empty data — **stop iterating in the UI and hit the REST endpoint**. The diagnosis is almost always 5 minutes of `curl`. The companion lessons that motivated this file: [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) (silent-zero scoring; FIX A diagnosis is an `EVALUATE SUMMARIZE`), [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) (`REMOVEFILTERS(T1, T2)` blanks a visual with no error — REST returns the real arity error), and the BMA-CSP Lessons 3 / 4 (gateway question numbers and SWITCH routing were assumed wrong for hours before a 30-second REST query enumerated the actual `(Question_Number, Value)` combinations and showed which Yes/No questions were misrouted to A/B/C scorers).

---

## 1. The principle — read this first

The portal collapses error envelopes; the REST API does not. The portal also forces a deploy round-trip to test a hypothesis; REST tests the hypothesis against the live model in seconds. Three concrete shapes:

| Symptom you see in the portal | What the portal tells you | What REST returns |
|---|---|---|
| Visual is blank, no error | Nothing — visual just doesn't render | Measure result (empty? blank? the actual rows) |
| Measure returns 0 / BLANK | "It works, the answer is just zero" | The full evaluated rowset — you see whether the filter context produced 0 rows or the calc itself returned 0 |
| `REMOVEFILTERS(T1, T2)` blanks the visual | Silent visual blank, no error toast | "Function REMOVEFILTERS does not accept multiple table arguments in one call" (or equivalent) |
| Deploy "succeeded" but renders wrong | Green checkmark | Run `EVALUATE` against the deployed model, get the real data shape |
| Flow run "succeeded" with empty output | Green checkmark, empty results | Hit the connector's underlying REST endpoint, see whether the API returned 0 rows or whether the connector filter dropped them |

**The rule, derived from BMA-CSP 2026-06-04:** when a PBIR / Fabric / Dataverse problem is non-obvious from the UI, the REST API is the **FIRST** debugging move, not the last. Three of the four production debugging cycles in that session were resolved in <10 minutes by hitting REST directly; the same investigations had spent 30-90 minutes each in the portal.

---

## 2. Endpoint cheat-sheet — Fabric / Power BI

### `executeQueries` — run a DAX query against a deployed semantic model

The single most useful endpoint for debugging measures, filter context, and data shape:

```bash
POST https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}/executeQueries
Authorization: Bearer <token>
Content-Type: application/json

{
  "queries": [{
    "query": "EVALUATE SUMMARIZECOLUMNS(Questions[Question_Number], \"Val\", MAX(Responses[Value]))"
  }]
}
```

Per-workspace variant when the dataset lives in a non-personal workspace:

```bash
POST https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets/{datasetId}/executeQueries
```

**The `datasetId` is the semantic-model GUID** (Fabric portal → workspace → semantic model → … → Settings → Settings → URL parameter, OR `pbi-tools` / DAX Studio). **The `groupId` is the workspace GUID** (Fabric portal → workspace → Manage workspace → URL).

DAX query results come back as `{"results": [{"tables": [{"rows": [...]}]}]}`. For one-row scalars use a `ROW()` wrapper:

```dax
EVALUATE ROW("Result", [My Measure])
```

### Other Fabric REST endpoints worth knowing

| Purpose | Endpoint |
|---|---|
| List items in a workspace (datasets, reports, lakehouses, notebooks) | `GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items` |
| Trigger a dataset refresh | `POST https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets/{datasetId}/refreshes` |
| Refresh history (was the refresh actually a clean success, or a partial?) | `GET .../datasets/{datasetId}/refreshes?$top=10` |
| Dataset metadata (tables, columns, measures) | `GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets/{datasetId}` |
| List dataset users / permissions | `GET .../datasets/{datasetId}/users` |
| Workspace capacity SKU + tenant | `GET .../groups/{groupId}` |

The full Power BI REST surface is huge ([`learn.microsoft.com/rest/api/power-bi/`](https://learn.microsoft.com/rest/api/power-bi/)). The Fabric REST surface is at [`learn.microsoft.com/rest/api/fabric/`](https://learn.microsoft.com/rest/api/fabric/). The 5 above carry the bulk of debugging usage.

---

## 3. Dataverse Web API — the analogue

When the data lives in Dataverse (Tables-as-source-of-truth, not just a Power BI semantic model), the Dataverse Web API is the same shape of escape hatch:

```bash
# List 10 questions, showing only the question-number column.
GET https://yourorg.crm.dynamics.com/api/data/v9.2/cr_questions?$select=cr_question_number&$top=10
Authorization: Bearer <token>
```

```bash
# Count rows in a custom table matching a filter — the "is the integration loading anything?" check.
GET .../api/data/v9.2/cr_questions?$filter=cr_question_number eq 14&$count=true
```

The auth chain is identical in shape to the Power BI side (see §4) — different `--resource` parameter, same overall flow. The full Dataverse auth-acquisition decision tree lives in [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md); read that file *first* when you need a Dataverse bearer token, because it covers the "client-credentials vs `az account get-access-token` vs reuse PAC's MSAL cache vs interactive" ladder ordered by what's already authenticated on this machine.

---

## 4. Auth chain — bearer token in one command

Fabric / Power BI:

```bash
TOKEN=$(az account get-access-token \
  --resource https://analysis.windows.net/powerbi/api \
  --query accessToken -o tsv)
```

(For the newer Fabric API surface — `api.fabric.microsoft.com` — use `--resource https://api.fabric.microsoft.com`. Both work; the Power BI resource URL accepts the legacy Power BI REST API and the most-used Fabric endpoints.)

Dataverse:

```bash
TOKEN=$(az account get-access-token \
  --resource https://yourorg.crm.dynamics.com \
  --query accessToken -o tsv)
```

**This assumes `az login` has been run.** If you don't have an interactive Azure CLI session, walk [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md) for the client-credentials / SPN / PAC-MSAL-cache fallbacks. The full decision tree is in that file; cross-link rather than duplicate.

**Cache caveat (Linux/macOS):** `az` writes the access token (and refresh token) to `~/.azure/msal_token_cache.json` in **plaintext**. On Windows it uses DPAPI. If the consumer is on Linux/macOS and the box is multi-tenant or shared, treat the cache as a secret-equivalent. Documented in [`dataverse-token-acquisition.md`](dataverse-token-acquisition.md).

**Scope cheat-sheet** for `az account get-access-token --resource <X>`:

| `--resource` | Used by |
|---|---|
| `https://analysis.windows.net/powerbi/api` | Power BI REST API + `executeQueries` |
| `https://api.fabric.microsoft.com` | Fabric REST API (newer surface; works for `executeQueries` too) |
| `https://yourorg.crm.dynamics.com` | Dataverse Web API |
| `https://service.flow.microsoft.com` | Power Automate Management API (often permission-blocked for SPN — see [`programmatic-flow-creation.md`](programmatic-flow-creation.md)) |
| `https://service.powerapps.com` | Power Apps Management API |

---

## 5. Worked example — BMA-CSP question-number diagnosis (Lessons 3 / 4)

Production case, 2026-06-04. The scoring report deployed cleanly and all 60 entities showed Low Risk. Iteration in PBI Desktop had spent ~2 hours assuming the SWITCH-based scorer DAX was wrong somewhere. The 5-minute REST query that closed it:

```bash
TOKEN=$(az account get-access-token \
  --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv)

curl -s -X POST \
  "https://api.powerbi.com/v1.0/myorg/groups/$WORKSPACE_ID/datasets/$DATASET_ID/executeQueries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [{
      "query": "EVALUATE SUMMARIZECOLUMNS(Questions[Question_Number], Questions[Question_Text], \"Sample_Answer\", FIRSTNONBLANK(Responses[Value], 1))"
    }]
  }' | jq '.results[0].tables[0].rows'
```

The output enumerated every `(Question_Number, Question_Text, Sample_Answer)` combination across all entities. Result: `Q1` was "Acting as company formation agent" not "Does your company hold or receive money on behalf of clients" — the gateway-applicability DAX had been pinned to the wrong question number from the project's design doc, never against the live data. Same pattern (REST → enumerate live values → spot the assumed-string mismatch) closed Lesson 4's SWITCH routing bugs: a query of `SUMMARIZE(Responses, [Question_Number], [Value])` showed which Yes/No questions had been misrouted to A/B/C scorers because their actual values were `"Yes"`/`"No"` not `"A"`/`"B"`/`"C"`.

The general shape: **before writing string-literal filters in DAX or M, run a SUMMARIZE against the live model and confirm the actual values match the assumption.** The same anti-pattern is documented at [`dax-category-name-mismatch-zero-scores.md`](dax-category-name-mismatch-zero-scores.md) for the Category case — this file's Lessons 3/4 are the Question_Number variant.

---

## 6. Owners + secondary consumers

- **Primary:** `power-bi-engineer` (PBIR / Fabric / DAX work).
- **Secondary:** `dataverse-architect` (when the silent-zero / wrong-value pattern is rooted in Dataverse-side filter strings — Dataverse-Web-API analogue in §3).
- **Tertiary:** `flow-engineer` (when a flow's "success but empty" surfaces the same root cause at the connector layer — hit the underlying REST endpoint to see what it actually returned), `power-platform-admin` (refresh history / capacity / permission audits).

The compact inline prior on each of those agents points at this file as the **first** debugging move when a Fabric/PBIR/Dataverse problem isn't obvious from the UI.

---

## 7. Reusable `query_dataset.sh` pattern

A small bash script in the consumer repo's `scripts/` folder collapses the diagnosis step to one command. Pattern:

```bash
#!/usr/bin/env bash
# query_dataset.sh — run a DAX query against a Fabric semantic model.
#
# Usage:
#   ./query_dataset.sh "EVALUATE SUMMARIZECOLUMNS(Questions[Question_Number])"
#   ./query_dataset.sh @query.dax           # read query from file
#
# Env: WORKSPACE_ID, DATASET_ID (set in .envrc or shell).

set -euo pipefail
: "${WORKSPACE_ID:?set WORKSPACE_ID}"
: "${DATASET_ID:?set DATASET_ID}"

QUERY="$1"
if [[ "$QUERY" == @* ]]; then
  QUERY=$(cat "${QUERY#@}")
fi

TOKEN=$(az account get-access-token \
  --resource https://analysis.windows.net/powerbi/api \
  --query accessToken -o tsv)

curl -s -X POST \
  "https://api.powerbi.com/v1.0/myorg/groups/$WORKSPACE_ID/datasets/$DATASET_ID/executeQueries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg q "$QUERY" '{queries:[{query:$q}]}')" \
  | jq '.results[0].tables[0].rows'
```

Drop this in a project early — it eliminates the friction tax that keeps people in the portal when REST would be 10x faster.

---

## 8. Anti-patterns

- **Iterating in the portal when the UI gives no error.** The portal swallowed the real error envelope; REST has it. Stop, hit REST.
- **Assuming "deploy succeeded" means "data is correct".** Deploy success is structural; data correctness needs an `EVALUATE` query.
- **Writing string-literal DAX filters without confirming the strings.** `Questions[Category] = "Core"` is a hardcoded assumption; one REST `SUMMARIZE` query confirms (or refutes) it.
- **Adding diagnostic measures inside the report instead of querying REST.** A `CONCATENATEX`-based diagnostic measure in a visual can itself blank the visual (see [`pbir-dax-pitfalls.md`](pbir-dax-pitfalls.md) §3). REST has none of that filter-context risk — it's the unambiguous diagnostic surface.
- **Forgetting to refresh `$TOKEN` mid-session.** `az` tokens expire (~60-90 min). Just re-run the `az account get-access-token` line.
