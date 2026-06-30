---
name: managed-solution-import
description: Hardened pac solution import plus explicit baseline-aware cloud-flow reactivation for SPN-driven CI/CD — preflight, baseline, import, reactivate, verify. Managed imports leave flows Draft when the importing identity lacks connection permission; this reactivates only flows that were Active, splits transient vs durable 403s, and verifies state. Run on any managed import to TEST/PROD, or use reactivate/verify standalone.
allowed-tools: Bash, Read
---

# managed-solution-import — hardened import + verified flow reactivation

> **Why this exists.** A managed `pac solution import` turns its cloud flows off-and-on, and the
> platform only auto-reactivates a flow when it was **exported-on AND its connection references are
> bound AND the importing identity has permission to those connections** (Microsoft Learn, "Import a
> solution" FAQ, verified 2026-06-30). An **SPN-driven CI/CD** import routinely fails those conditions,
> so flows land **Draft** and automations silently stop — nobody finds out until a user complains. This
> skill makes the reactivation **explicit, baseline-aware, and verified**, and ships a domain-neutral
> script that externalizes every customer specific to a config file.

## The shape (what's the spine)

The **reactivation + verify pass over the Dataverse Web API is the spine** — fully usable on its own,
no `pac` required (most pipelines already run `pac solution import` their own way via Build Tools / ADO).
The `import` subcommand is an **optional convenience** that composes the whole pipeline.

```
import = prod-guard → preflight → baseline → pac solution import → poll → reactivate → verify
```

## When the platform DOES reactivate for you (and when it doesn't)

| Situation | Auto-reactivates? | What to do |
|---|---|---|
| Interactive maker import, flows exported-on, connections bound, importer owns them | Yes | nothing — built-in |
| Update-import of an existing flow | No state change | import preserves the target's current state |
| **SPN/CI import, connection refs not yet bound or SPN lacks connection permission** | **No → Draft** | **run `reactivate` (this skill)** |

Full mechanics: [`../../knowledge/managed-import-flow-reactivation.md`](../../knowledge/managed-import-flow-reactivation.md).

## Run it

```bash
# Auth comes from env vars (CI path) — see knowledge/dataverse-token-acquisition.md for the full ladder.
export AZURE_CLIENT_ID=...  AZURE_TENANT_ID=...  AZURE_CLIENT_SECRET=...   # SPN; secret stays in env

SK=plugins/power-platform/skills/managed-solution-import/managed_import.py

# Standalone spine — reactivate flows that an import left Draft (baseline-aware):
python3 "$SK" baseline   --env-url https://yourorg.crm.dynamics.com         # capture Active flows FIRST
python3 "$SK" reactivate --env-url https://yourorg.crm.dynamics.com         # PATCH only those back Active
python3 "$SK" verify     --env-url https://yourorg.crm.dynamics.com         # exit 10 if any still Draft

# Full pipeline with a committable, secret-free config (per-env URLs/settings/timezone):
python3 "$SK" import --config ./pp-import-config.json --env prod \
    --solution-path ./out/MySolution_managed.zip            # blocked in PROD business hours unless --approved

python3 "$SK" import --config ./pp-import-config.json --env test \
    --solution-path ./out/MySolution_managed.zip --dry-run  # prints the plan, changes nothing
```

### Config file (commit it — it holds NO secrets)

```json
{
  "environments": {
    "test": { "url": "https://yourorg-test.crm.dynamics.com", "settings_file": "./deploymentSettings-test.json" },
    "prod": { "url": "https://yourorg.crm.dynamics.com", "settings_file": "./deploymentSettings-prod.json" }
  },
  "prod_guard": { "environments": ["prod"], "timezone": "America/New_York",
                  "business_hours": { "window": "09:00-17:00" }, "blocked_weekdays": [0,1,2,3,4] }
}
```
The loader **rejects** any secret-shaped key (`client_secret`, `password`, …) — credentials live in env
vars only. Override any value with an explicit flag (`--env-url`, `--settings-file`, `--impersonate-oid`).

## pac import flags — flag economy (the Microsoft correction)

| Flag | Default | Why |
|---|---|---|
| `--activate-plugins` | **on** | activates plug-ins + workflows during import |
| `--settings-file` | **on** (if configured) | binds connection references + env vars per environment |
| `--publish-changes` | **opt-in** | Microsoft **discourages** it for *managed* imports (slows deploy) |
| `--force-overwrite` | **opt-in** | Microsoft **discourages** it (slows import; overwrites active customizations) |

(Verified against Microsoft Learn [performance-recommendations](https://learn.microsoft.com/power-platform/alm/performance-recommendations), 2026-06-30.)

## Exit codes

`0` success · `2` usage/config · `10` partial (some flows still Draft) · `20` all reactivation attempts
failed · `40` auth · `50` pac import failed · `60` PROD guard blocked · `70` preflight failed.

## Honest limits

- The `statecode=1`/`statuscode=2`/`category=5` Dataverse contract is **`[unverified — training
  knowledge]`**; the tool **re-queries after every PATCH and asserts both codes**, degrading to a loud
  warning rather than asserting success, so a tenant that behaves differently fails visibly, not silently
  green. Confirm against your org's `workflow` `EntityDefinitions` if reactivation reports never converge.
- A `403 ConnectionAuthorizationFailed` has two causes — **transient** (connection-ref binding still
  propagating → the retry/backoff clears it) and **durable** (the SPN genuinely lacks permission to the
  connection → retry never fixes it; **share the connection with the SPN / bind the connection reference**).
  The tool retries, then names the durable case with that remediation.
- **Impersonation** (`--impersonate-oid`) is **off by default**, GUID-validated, and gated — it makes the
  SPN act as another Dataverse user (needs `prvActOnBehalfOfAnotherUser`; flows then run under that user's
  connections). Don't enable it without a reason.
- The pure decision logic (guard, SSRF host check, baseline-aware targeting, flag economy, exit-code map)
  is deterministic + unit-tested ([`../../hooks/tests/test-managed-import.sh`](../../hooks/tests/test-managed-import.sh));
  the live Dataverse/pac calls are best-effort and need a real tenant.
- Verified against **pac 2.7.x / Dataverse Web API v9.2 on 2026-06-30** — re-verify on pac upgrades.

## Cross-references

- Why flows go Draft + the conditional model: [`../../knowledge/managed-import-flow-reactivation.md`](../../knowledge/managed-import-flow-reactivation.md)
- The house rule: [`../../best-practices/alm-reactivate-flows-after-managed-import.md`](../../best-practices/alm-reactivate-flows-after-managed-import.md)
- Token acquisition ladder: [`../../knowledge/dataverse-token-acquisition.md`](../../knowledge/dataverse-token-acquisition.md)
- Fresh-import smoke test (the import *before* this one): [`../../best-practices/alm-fresh-import-smoke-test-before-release.md`](../../best-practices/alm-fresh-import-smoke-test-before-release.md)
- Pipeline architecture context: [`../alm-pipeline-design/SKILL.md`](../alm-pipeline-design/SKILL.md)
- **Any shipped use of the SPN secret is reviewed by `ravenclaude-core/security-reviewer`.**
