# Reactivate cloud flows explicitly after a managed import (SPN-driven CI/CD)

**Status:** Absolute rule for SPN-driven pipelines — never assume a managed import left your cloud flows Active. A flow that imported clean but stayed Draft is a dead automation nobody notices until a user complains.

**Domain:** ALM

**Applies to:** `power-platform`

---

## Why this exists

A managed `pac solution import` turns its cloud flows off-and-on. The platform *attempts* to restore each flow's exported state, but auto-reactivation only fires when the flow was **exported On**, its **connection references are bound**, AND **the importing identity has permission to those connections** (verified: Microsoft Learn, "Import a solution" FAQ, 2026-06-30). An **unattended service principal** in CI/CD routinely fails the third condition — it often does not own or have permission to the connections behind the connection references, and `--settings-file` binding may not have propagated at import time. The flows land **Draft**, the automations stop firing, and because the import itself *succeeded*, every status board is green. The cost of discovering this at the customer is an emergency and a credibility hit; the cost of an explicit reactivation pass is seconds. It is a release step, not a nice-to-have.

## How to apply

After every managed import in an SPN/CI pipeline, run an explicit **baseline-aware** reactivation pass: capture which flows were Active *before* the import, then reactivate only those that the import left Draft, and verify. Use the [`managed-solution-import`](../skills/managed-solution-import/SKILL.md) skill (inline as the full pipeline, or its standalone `reactivate`/`verify` subcommands in a pipeline that already runs `pac solution import` its own way).

```bash
SK=plugins/power-platform/skills/managed-solution-import/managed_import.py
# Inline (full pipeline does baseline -> import -> reactivate -> verify):
python3 "$SK" import --config ./pp-import-config.json --env prod --solution-path ./out/MySolution_managed.zip

# Standalone, in a pipeline that imports elsewhere:
python3 "$SK" baseline   --env-url https://yourorg.crm.dynamics.com   # BEFORE the import
# ... your existing `pac solution import` step ...
python3 "$SK" reactivate --env-url https://yourorg.crm.dynamics.com   # AFTER the import
python3 "$SK" verify     --env-url https://yourorg.crm.dynamics.com   # gate: non-zero if any still Draft
```

**Do:**
- Capture the **baseline before the import** — reactivation is keyed on a **stable name** (`uniquename`), not the `workflowid`, because a managed import can recreate the flow with a new GUID.
- Reactivate **only flows that were Active pre-import** — never blast-reactivate every Draft flow (some are intentionally off).
- Treat a `403 ConnectionAuthorizationFailed` as **two** problems: retry the transient one (binding still propagating), but a **durable** 403 means the SPN lacks permission to the connection — **share the connection with the SPN**; retrying won't fix it.
- Keep the pac flag set lean: `--activate-plugins` + `--settings-file`. Microsoft **discourages** `--publish-changes` and `--force-overwrite` for managed imports — make them deliberate opt-ins, not standing defaults.

**Don't:**
- Assume "import succeeded" means "flows are running."
- Verify activation by the PATCH's `204` alone — re-query and confirm the flow is actually Active.
- Hard-code env URLs, settings-file paths, a timezone, or an impersonation OID in the script — externalize them to the (secret-free) config file; secrets stay in env vars.

## Edge cases / when the rule does NOT apply

- **Interactive maker imports** where the importer owns the connections and flows were exported On — the platform auto-reactivates; the explicit pass is then a no-op (and safe to run as a verification).
- **Update-imports over an existing flow** — import preserves the target's current state, so a flow intentionally Off stays Off; baseline-aware targeting already respects this.
- **Classic Dataverse workflows / never-provisioned flows** (`resourcecontainer=null`) — these are not category=5 cloud-flow reactivations and are out of scope (they need portal Turn-On by a licensed user).

## See also

- [`../skills/managed-solution-import/SKILL.md`](../skills/managed-solution-import/SKILL.md) — the playbook + the shipped script
- [`../knowledge/managed-import-flow-reactivation.md`](../knowledge/managed-import-flow-reactivation.md) — the conditional model + the algorithm
- [`./alm-fresh-import-smoke-test-before-release.md`](./alm-fresh-import-smoke-test-before-release.md) — the import test *before* this reactivation
- [`./alm-connection-references-not-hardcoded-connections.md`](./alm-connection-references-not-hardcoded-connections.md) — why the SPN/connection-permission gap exists

## Provenance

Generalized from the Contoso managed-import flow-activation engagement (2026-06-30). Auto-reactivation conditions and the `--publish-changes`/`--force-overwrite` managed-import guidance verified against Microsoft Learn ("Import a solution" FAQ; ALM performance-recommendations), retrieved 2026-06-30. Extends house opinion §3 #13 (test the import) and §3 #3 (connection references) into the post-import flow-state step.

---

_Last reviewed: 2026-06-30 by `claude`_
