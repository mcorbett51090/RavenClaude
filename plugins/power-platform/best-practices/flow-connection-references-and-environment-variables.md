# Every solution-aware flow uses connection references and environment variables — never embedded connections or hard-coded values

**Status:** Absolute rule — a solution-aware flow that ships an embedded connection or a hard-coded site URL / list ID / env GUID is a broken import in the next environment. (House rule §3 #2 and #3.)

**Domain:** Power Automate / ALM

**Applies to:** `power-platform`

---

## Why this exists

A **connection** is a credential bound to a specific user in a specific environment. If a flow embeds it, importing that solution into test or prod either fails ("connection not found") or — worse — silently binds to the wrong connection and runs as the wrong identity. A **connection reference** is a solution component that the *consumer* re-binds on import, so you ship the flow's *shape* without shipping anyone's credentials. Likewise, any value that differs per environment — a SharePoint site URL, a list ID, a Dataverse org URL, a feature flag, a secret — belongs in an **environment variable** whose value is set per environment, not baked into an expression. Hard-coding these is the #1 reason "it worked in dev" doesn't survive promotion. This is non-negotiable for anything that leaves a developer's own environment.

## How to apply

**Connection references** — every connector in the flow points at a connection *reference* (`connectionReferenceLogicalName`), which the consumer binds at import. In the unpacked flow JSON the reference lives under the connector's `connection` object:

```json
"connectionReferences": {
  "shared_sharepointonline": {
    "connection": { "connectionReferenceLogicalName": "mc_SharePointConnRef" }
  }
}
```

> Note the shape: `connectionReferenceLogicalName` is nested under `connection`, **not** at the top level — the PA-export shape that puts it at top level imports clean but fails at runtime (the same gotcha called out in `create-cloud-flows-via-dataverse-web-api.md`).

**Environment variables** — reference them in expressions instead of literals. Read the *current value* (falling back to default) in a flow expression:

```
# SharePoint site from an env var, not a hard-coded URL:
@{first(outputs('Get_env_var_value')?['body/value'])?['schemavalue']}
```

…or, more simply, retrieve the env var with the Dataverse *Get a row* / environment-variable pattern at flow start and reference its output downstream.

**Do:**
- Create the connection reference and environment variable **in the same solution** as the flow, so they travel together on export.
- Use the env var's **default value** for dev and set a **current value** per environment in the deployment settings / pipeline — never overwrite the default with a prod value.
- Store secrets as a **Key Vault reference** (`@Microsoft.KeyVault(...)`) env var, not a plaintext string env var (house-rule §4 anti-pattern; the house-opinion hook flags plaintext secrets).
- Re-bind connection references and set env-var current values as a **documented post-import step** (or pipeline deployment-settings file).

**Don't:**
- Embed a connection directly in a solution-aware flow — it ships your credential and breaks on import.
- Hard-code a `.sharepoint.com` URL, a list GUID, a Dataverse `.crm*.dynamics.com` URL, or an env ID anywhere in an expression or HTTP action (the house-opinion hook flags these).
- Set a secret as the *default* value of a string env var — defaults are exported with the solution, so the secret leaks into source control.

## Edge cases / when the rule does NOT apply

- **A throwaway personal flow** in My Flows (not solution-aware, never promoted) can use a direct connection — but the moment it joins a solution, this rule applies.
- **Some connectors don't yet support connection references** — rare in 2026, but if one genuinely doesn't, document the manual post-import connection step and flag it for review.
- **A value that's truly invariant across all environments** (a public, stable constant) doesn't need an env var — but "the prod URL happens to equal the dev URL today" is not invariance; if it *could* differ, make it a variable.

## See also

- [`../skills/power-automate/resources/solution-aware-flows-connection-refs.md`](../skills/power-automate/resources/solution-aware-flows-connection-refs.md) — connection-reference rules, common import failures, git-review focus
- [`./create-cloud-flows-via-dataverse-web-api.md`](./create-cloud-flows-via-dataverse-web-api.md) — the `connectionReferenceLogicalName`-under-`connection` shape gotcha (same trap, programmatic-create context)
- [`./flow-error-handling-and-retry-policy.md`](./flow-error-handling-and-retry-policy.md) — a missing connection reference surfaces as a self-off flow, not a hard error
- [`../knowledge/flow-decision-trees.md`](../knowledge/flow-decision-trees.md) — `## Decision Tree: Programmatic flow creation — Approach A vs B`
- [`../agents/flow-engineer.md`](../agents/flow-engineer.md) · [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — flow + ALM owners

## Provenance

Codifies house rules §3 #2 (env vars for everything that varies) and #3 (connection references over connections), the `power-automate` skill's solution-aware-flows resource, and the house-opinion hook's hard-coded-URL / plaintext-secret checks. The `connectionReferenceLogicalName`-under-`connection` shape is cross-referenced from the production lesson in `programmatic-flow-creation.md` (verified there against ~136 live flow records).

---

_Last reviewed: 2026-05-30 by `claude`_
