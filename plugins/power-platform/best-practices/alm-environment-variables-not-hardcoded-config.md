# Environment variables for config that varies per environment, never hard-coded

**Status:** Absolute rule — a SharePoint URL, list ID, or feature flag baked into a solution component is config that should have travelled as data, and it will be wrong in every environment except the one it was authored in.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

A solution is supposed to be the *same* artifact in dev, test, and prod — only the configuration differs. The instant a maker types a literal SharePoint site URL into a flow, a list GUID into a Power Fx formula, or an API base address into a custom connector, that value is frozen into the shipped component and the solution stops being environment-portable. On import to test the flow still points at the dev SharePoint site; nobody notices until prod writes land in the dev list. Environment variables are the platform's first-class mechanism for "this value differs per environment": the *definition* ships in the solution, the *value* is supplied per environment at (or after) import. That keeps one artifact promotable across the whole pipeline.

## How to apply

Create an environment variable for every value that changes across environments — URLs, IDs, feature flags, tenant-specific endpoints. Reference it from the flow/app/plug-in. Supply the per-environment value through the deployment settings file so import is non-interactive.

```bash
# Generate the deployment-settings skeleton; it enumerates every env var in the solution
pac solution create-settings --solution-zip ./out/MySolution_managed.zip \
    --settings-file ./deploymentSettings-test.json
```

The generated file has an `EnvironmentVariables` array — fill the `Value` per target environment (these are config values that live in the repo, **not** secrets — see the Key Vault sibling rule):

```json
{
  "EnvironmentVariables": [
    { "SchemaName": "mc_PartnerSiteUrl", "Value": "https://contoso.sharepoint.com/sites/partners-test" },
    { "SchemaName": "mc_FeatureXEnabled", "Value": "true" }
  ],
  "ConnectionReferences": []
}
```

```bash
pac solution import --path ./out/MySolution_managed.zip --settings-file ./deploymentSettings-test.json
```

**Do:**
- Use the **default value** for dev convenience and the **current value** (supplied at import) for test/prod — never rely on the default in a downstream env.
- Pick the right type: `String`, `Number`, `Boolean`, `JSON`, `Data source`, or `Secret` (Key Vault reference). A JSON env var is the clean way to ship a small per-env config bag.
- Name with your publisher prefix and an env-neutral purpose (`mc_PartnerSiteUrl`), describing what it is, not what it equals in dev.

**Don't:**
- Type a site URL, list GUID, or environment ID directly into a flow action, Power Fx formula, or plug-in.
- Ship an env var with a dev default and forget to supply the test/prod value — a flow reading an unset current value falls back to the dev default and silently runs against dev data.
- Put a secret in a `String` env var default. Secrets are a different rule.

## Edge cases / when the rule does NOT apply

- **A truly tenant-wide constant** that is identical in every environment (e.g. a fixed ISO currency code) is not config-that-varies and doesn't need an env var — but be honest about whether it's *actually* invariant across every future environment before hard-coding it.
- **Data-source env vars** bind a connector to a specific source (e.g. a specific SharePoint site or SQL database) and are the right tool when the *source itself* differs per env, not just a URL string.
- **Secrets** belong in a `Secret`-typed env var backed by Key Vault, governed by [`./alm-secrets-in-key-vault-not-env-var-defaults.md`](./alm-secrets-in-key-vault-not-env-var-defaults.md), not here.

## See also

- [`./alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md) — the sibling rule for credential bindings
- [`./alm-secrets-in-key-vault-not-env-var-defaults.md`](./alm-secrets-in-key-vault-not-env-var-defaults.md) — where secrets actually belong
- [`./alm-pipeline-stages-dev-test-prod.md`](./alm-pipeline-stages-dev-test-prod.md) — the pipeline that injects these values per stage
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns env-var schema and per-env value injection
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §4 — env-var injection at import

## Provenance

Codifies house opinion §3 #2 ("Environment variables for everything that varies across environments") and §4 anti-pattern ("Hard-coded environment IDs, site URLs, list GUIDs"). The `power-platform` PostToolUse hook `check-house-opinions.sh` mechanically flags hard-coded `.sharepoint.com` / `.dynamics.com` URLs against this rule. `pac solution create-settings`, the `EnvironmentVariables` settings shape, and env-var types verified against Microsoft Learn (`conn-ref-env-variables-build-tools`, environment-variables overview), retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
