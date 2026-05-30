# Solution-aware flows use connection references, never hard-coded connections

**Status:** Absolute rule — a flow shipped with a baked-in connection ID is the #1 cause of solution import failures and silently-wrong-credential bugs.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

A *connection* is a concrete, per-user, per-environment object holding credentials (this SharePoint account, in this env). A *connection reference* is an abstraction over it — a placeholder a flow binds to, which the consumer (or the deployment SPN) re-binds when the solution lands in a new environment. Hard-code the connection ID into a flow and one of two things happens on import: the import fails because that connection ID doesn't exist in the target env, or — worse — it succeeds against a *different* connection that happens to exist, and your prod flow now runs as the wrong identity against the wrong data. Connection references make the credential binding a per-environment deployment concern instead of a value frozen into the shipped artifact. They are mandatory for any solution-aware flow on a promotion path.

## How to apply

Author flows against connection references (the modern designer does this by default for solution-aware flows). At deploy time, pre-bind them per environment via the deployment settings file so the import is non-interactive.

```bash
# Generate the deployment settings skeleton from the solution
pac solution create-settings --solution-zip ./out/MySolution_managed.zip \
    --settings-file ./deploymentSettings-test.json
```

The generated JSON has a `ConnectionReferences` array with empty `ConnectionId` values you fill per target env (the connection must already exist in that env, owned by — or shared with — the deploying identity):

```json
{
  "ConnectionReferences": [
    {
      "LogicalName": "mc_sharedsharepointonline_prod",
      "ConnectionId": "9f66d1d455f3474ebf24e4fa2c04cea2",
      "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
    }
  ],
  "EnvironmentVariables": []
}
```

```bash
# Import with the settings file → references pre-bind, no interactive prompt
pac solution import --path ./out/MySolution_managed.zip --settings-file ./deploymentSettings-test.json
```

**Do:**
- Name connection references with your publisher prefix and an env-neutral purpose (`mc_sharedsharepointonline`), not the dev connection's GUID.
- Create the target-env connection *before* import and confirm the deploying identity owns or is shared on it — import validates that the connection-reference owner can use the connection.
- Keep one deployment settings file per target env in the repo (values, not secrets).

**Don't:**
- Reference a raw connection object inside a solution-aware flow.
- Ship a flow whose connection reference has no value and expect a pipeline to update it — *Power Platform Pipelines cannot update a connection reference that has no value in the solution or target env* on first deploy; create the connection and bind it, then subsequent deploys can update it (verified, MS Learn pipelines FAQ, 2026-05-30).

## Edge cases / when the rule does NOT apply

- **Service-principal connections** are valid for connectors that support SPN auth (incl. custom connectors) and are the right choice for unattended pipeline-run flows — still bound via a connection reference, just owned by the SPN.
- **Non-solution (personal) flows** outside any solution don't use connection references — but per house rule §3 #1 those shouldn't exist for anything real; move the flow into a solution first.
- **First deploy to a brand-new env** legitimately requires a human/SPN to create the underlying connection once; the reference automates every deploy *after* that.

## See also

- [`./alm-environment-variables-not-hardcoded-config.md`](./alm-environment-variables-not-hardcoded-config.md) — the sibling rule for non-credential config that varies per env
- [`./alm-secrets-in-key-vault-not-env-var-defaults.md`](./alm-secrets-in-key-vault-not-env-var-defaults.md) — where credentials/secrets actually belong
- [`../agents/solution-alm-engineer.md`](../agents/solution-alm-engineer.md) — owns connection-reference rebinding in pipelines
- [`../skills/alm-pipeline-design/SKILL.md`](../skills/alm-pipeline-design/SKILL.md) §5 — connection-reference rebinding mechanics

## Provenance

Codifies house opinion §3 #3 ("Connection references over connections") and the `solution-alm-engineer` opinion ("Connection references mandatory in solution-aware flows"). `pac solution create-settings`, the `ConnectionReferences` JSON shape, the `--settings-file` import flag, and the "can't update a reference with no value" first-deploy behavior all verified against Microsoft Learn (conn-ref-env-variables-build-tools, pipelines FAQ), retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
