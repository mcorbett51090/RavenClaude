# Dataverse HTTP errors — an access error is NOT a schema error

> **Last reviewed:** 2026-05-29. Source: a real engagement incident — an agent got a **403 reading the `account` table** in the Dataverse Web API, **assumed the field it wanted didn't exist**, and reported the (non-existent) missing field as the root cause. The actual problem was access/privilege. This is the canonical Power Platform case of the confident-reasoning error the core [Claim Grounding & Source Honesty protocol](../../ravenclaude-core/CLAUDE.md) targets: a flawed causal inference stated as fact.

## The trap

An HTTP error reading Dataverse data tells you about **access, authentication, or routing** — it tells you **nothing** about whether a column or table *exists*. Schema existence is a metadata fact, completely independent of whether your principal can read the data. Conflating the two produces a confident wrong diagnosis and sends the fix in the wrong direction (e.g. "add the missing field" when the field was there all along and the SPN just lacked a read privilege).

## What each error actually means (and what it does NOT mean)

| Error | What it actually means | What it does **NOT** mean |
| --- | --- | --- |
| **401 Unauthorized** | Token missing / expired / wrong audience / wrong tenant. | Not "the table/field is gone." |
| **403 Forbidden** | Authenticated, but the principal lacks the privilege (security role missing the table's Read, row not shared, column-level security, or an environment/DLP restriction). | **Not "the field doesn't exist."** This is the incident above. |
| **404 Not Found** | Wrong entity set name (it's the **logical collection name** — `accounts`, not `Account`), a wrong row GUID, or a wrong API path. | Usually a routing/name error, not a missing column. |
| **400 Bad Request** with `Could not find a property named '<x>'` | **This** is the one that actually indicates a bad/absent column name — and only on a request that already passed auth + access. | — |

The single load-bearing distinction: **only a 400 "could not find a property" (on an otherwise-authorized request) is evidence about a column name.** A 401/403/404 is an access/routing problem first.

## The discipline — verify schema and access as TWO separate checks

A claim like "the field doesn't exist" is consequential (it gates the diagnosis and the fix). Per the Claim Grounding protocol, do not state it from a 403; verify it this session, on two independent axes:

1. **Does the column exist? (schema — independent of your access to data.)** Query entity **metadata**, which a read-data 403 does not gate:
   - Web API: `GET [org]/api/data/v9.2/EntityDefinitions(LogicalName='account')/Attributes?$select=LogicalName` (or `$metadata`).
   - SDK: `RetrieveEntityRequest` with `EntityFilters.Attributes`.
   - Maker portal table designer / `pac`.
     If the attribute is in the metadata, the field **exists** — regardless of the 403 on the data.
2. **Can this principal read the data? (access — independent of schema.)** Check the SPN/user **security role** has Read on the table (and the right access level — User/BU/Org), whether the row is **shared**, whether **column-level security** hides the field, and whether an **environment / DLP** policy blocks it.

If you cannot verify, **abstain and say so** (Capability Grounding Protocol): a 403 is a "blocked" signal → enumerate the access causes above before concluding anything about schema. Never report a missing field off an access error.

## One-line rule

> A 401/403/404 reading Dataverse is an **access/auth/routing** problem; a field's existence is a **metadata** fact — check them **separately**, and only a 400 "could not find a property" speaks to a column name. <!-- claim-lint-ok: error-semantics reference, verified Dataverse Web API behavior -->
