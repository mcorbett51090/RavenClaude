---
name: dataverse-payload-preflight
description: Validate a Dataverse create/update payload against LIVE entity metadata in ONE pass — before you POST/PATCH — so you never fix-one-field-and-retrigger. Catches nonexistent columns, invalid option-set values, malformed/missing lookup binds, missing required fields, and the owner-not-provided (SPN-create) trap together. Run it on the FIRST create failure, or up front when a human re-fire or long run gates each test.
allowed-tools: Bash, Read
---

# dataverse-payload-preflight — one-pass payload validation against live metadata

> **Why this exists.** The Contoso assumption-rework retro (2026-06-24): a `Create_BalanceSheet` failed
> **four times in a row, each on a different field** — empty lookup bind `/accounts()` → invalid
> `sourcechannel` option value → undeclared `extractionrun` columns → "Owner was not provided" — each
> needing a costly human re-fire. **A single metadata-vs-payload sweep finds them all at once.** This
> is the deterministic instrument of *default-to-verification*: don't reason about the schema, read it.

## When to run it (the discipline — expensive-test front-loading)

- **Before the first create/update** of an entity you didn't author the payload for (an inherited
  payload, a prior session's, a new entity). Don't assume the schema — validate it.
- **On the FIRST create/update failure** — not after the second. One pass finds every remaining issue.
- Whenever each test costs a **human re-fire or a long run**: those are scarce resources; spend cheap
  static-validation tokens to conserve them (see [`../../../ravenclaude-core/best-practices/expensive-test-front-loading.md`](../../../ravenclaude-core/best-practices/expensive-test-front-loading.md)).

## Run it

```bash
# 1. Acquire a Dataverse token (see knowledge/dataverse-token-acquisition.md for the decision tree).
export DATAVERSE_TOKEN="$(az account get-access-token --resource https://yourorg.crm.dynamics.com --query accessToken -o tsv)"

# 2. Validate the whole payload against LIVE metadata, in one pass:
python3 preflight.py --org https://yourorg.crm.dynamics.com --entity contoso_balancesheet --payload payload.json

# Offline / in a test (skip the live fetch — feed metadata you captured):
python3 preflight.py --entity contoso_balancesheet --metadata metadata.json --payload payload.json
```

Output is JSON `{entity, ok, error_count, warning_count, violations[]}` (each violation has
`field · kind · severity · detail · fix`) plus a human summary. **Exit 0** = no error-severity
violations; **exit 3** = fix-these-before-you-POST.

## What it checks (against the entity's live `EntityDefinitions`)

| kind | catches |
|---|---|
| `nonexistent-column` | a payload key that isn't an attribute (the `extractionrun` undeclared-fields trap) |
| `missing-required` | an `ApplicationRequired`/`SystemRequired` attribute absent from the payload |
| `invalid-option-set` | a Picklist value not in the attribute's declared options (the `sourcechannel` trap) |
| `malformed-lookup-bind` | an `@odata.bind` whose value isn't `/<entityset>(<non-empty-id>)` (the `/accounts()` trap) |
| `lookup-needs-bind` | a Lookup attribute given a raw value instead of a `<nav>@odata.bind` |
| `unknown-lookup-target` *(warn)* | a bind to an entity-set that isn't a known target of the entity's lookups |
| `owner-not-provided` *(warn)* | a User/Team-owned entity with no `ownerid` — the SPN-create "Owner was not provided" trap |

## Honest limits
- **The live-fetch query shapes are version-sensitive** (`…/Attributes/Microsoft.Dynamics.CRM.<Type>AttributeMetadata`, the `OptionSet` expand) — if a sub-query 400s the script **degrades that one check class** (a note on stderr) rather than failing; confirm against your org's `$metadata` `[verify-at-use]`.
- **Lookup *navigation-property* names** (the `X` in `X@odata.bind`) often differ from the lookup's logical name; the validator verifies the bind **value** shape + target entity-set but treats an unknown nav-name as a warning, not an error (no false-fail). It does not (yet) probe `prvCreate`/`prvAssign` privileges — `owner-not-provided` is a warning pointing you to verify the SPN's role **live** (don't design around an assumed privilege; test it — the retro's incident #4).
- The pure `validate(payload, metadata)` is deterministic + unit-tested (`hooks/tests/test-preflight.sh`); the live fetch is best-effort.

## Cross-references
- Token acquisition: [`../../knowledge/dataverse-token-acquisition.md`](../../knowledge/dataverse-token-acquisition.md).
- REST-first debugging (read the real error envelope, not the portal): [`../../knowledge/pbir-fabric-rest-debugging.md`](../../knowledge/pbir-fabric-rest-debugging.md).
- The advisory `hooks/nudge-dataverse-preflight.sh` reminds you to run this when it sees a Dataverse create/update Bash command.
