# A Dataverse 401/403/404 is an access error, never proof a field is missing

**Status:** Primary diagnostic — the first wrong turn when a Dataverse read fails.

**Domain:** Dataverse / Web API

**Applies to:** `power-platform`

---

## Why this exists

An HTTP error reading Dataverse data tells you about **access, authentication, or routing** — it tells you **nothing** about whether a column or table *exists*. Schema existence is a metadata fact, entirely independent of whether your principal can read the data. Conflating the two produces a confident wrong diagnosis that sends the fix in the wrong direction. The canonical incident: an agent got a **403 reading the `account` table**, assumed the field it wanted didn't exist, and reported a (non-existent) missing field as the root cause — when the real problem was a missing read privilege. This is the textbook confident-reasoning error the core Claim Grounding protocol targets.

## How to apply

Read the status code for what it actually means, then verify schema and access as **two separate checks**.

| Error | What it means | What it does **NOT** mean |
|---|---|---|
| **401** | Token missing / expired / wrong audience / wrong tenant | Not "the table/field is gone" |
| **403** | Authenticated, but the principal lacks the privilege (security role, sharing, column-level security, DLP) | **Not "the field doesn't exist"** |
| **404** | Wrong entity-set name (`accounts`, not `Account`), wrong row GUID, or wrong path | Usually routing, not a missing column |
| **400** `Could not find a property named '<x>'` | The one error that actually speaks to a bad/absent column — and only after auth + access passed | — |

```http
# Schema check (metadata — a read-data 403 does NOT gate this):
GET /api/data/v9.2/EntityDefinitions(LogicalName='account')/Attributes?$select=LogicalName
# If the attribute is in metadata, the field EXISTS regardless of the 403 on the data.
```

**Do:**
- Verify column existence via **entity metadata** (`EntityDefinitions`, `$metadata`, `RetrieveEntityRequest`, or the maker portal) — independent of data access.
- Verify access separately: does the SPN/user's **security role** have Read (at the right level), is the row **shared**, is there **column-level security**, does a **DLP / environment policy** block it.
- If you can't verify, **abstain and say so** — a 403 is a "blocked" signal; enumerate access causes before concluding anything about schema.

**Don't:**
- Report "the field is missing" off a 401/403/404. Only a 400 "could not find a property" (on an otherwise-authorized request) is evidence about a column name.

## Edge cases / when the rule does NOT apply

- A **400 "Could not find a property named '<x>'"** on a request that already passed auth and access **is** legitimately about the column name — that's the one status code that speaks to schema.
- A **404 on `EntityDefinitions(LogicalName='...')`** itself does indicate a genuinely non-existent *table* (vs. a 404 on a data row, which is routing) — match the 404 to *what* you queried.

## See also

- [`../knowledge/dataverse-http-error-attribution.md`](../knowledge/dataverse-http-error-attribution.md) — the full error-semantics table and the source incident
- [`../knowledge/dataverse-token-acquisition.md`](../knowledge/dataverse-token-acquisition.md) — for the 401 branch: acquiring the right token/audience
- [`../agents/dataverse-architect.md`](../agents/dataverse-architect.md) — owner of the Dataverse data + security surface

## Provenance

Extracted from [`../knowledge/dataverse-http-error-attribution.md`](../knowledge/dataverse-http-error-attribution.md) (real engagement incident: a 403 read misdiagnosed as a missing field). Aligns with the Claim Grounding & Source Honesty worked examples in [`../CLAUDE.md`](../CLAUDE.md) §5a.

---

_Last reviewed: 2026-05-30 by `claude`_
