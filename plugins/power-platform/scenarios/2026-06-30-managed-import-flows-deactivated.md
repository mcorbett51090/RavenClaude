---
scenario_id: 2026-06-30-managed-import-flows-deactivated
contributed_at: 2026-06-30
plugin: power-platform
product: "pac-cli / dataverse-web-api"
product_version: "pac 2.7.x; Dataverse Web API v9.2"
scope: environment-specific
tags: [pac-cli, solution-import, cloud-flows, flow-reactivation, spn, alm, managed-solution, connection-references]
confidence: high
reviewed: false
---

## Problem

A customer's CI/CD pipeline imported a **managed** solution into TEST/PROD using a **service
principal**. Every `pac solution import` reported success, but afterward **all Power Automate cloud
flows in the solution were in Draft** — the automations had silently stopped firing. Nobody noticed
until a downstream user reported that an expected automated action never happened. The import was
green; the system was broken.

## Permissions context

- Unattended **service-principal** (client-credentials) auth in a CI/CD environment.
- The solution's flows use **connection references**; the SPN did **not** own / lack permission to
  some of the underlying connections at import time, and `--settings-file` binding had not fully
  propagated when the import completed.
- The standing team rule "reactivate flows after import" existed only as a memory note — nothing in
  the pipeline enforced it, so it was forgotten.

## Attempts

- Assumed the managed import would **auto-reactivate** the flows (it does — but only when the flow was
  exported On AND the connection refs are bound AND the importing identity has connection permission;
  the SPN failed the third condition).
- Toggled a couple of flows On manually in the portal → worked for those, but doesn't scale to dozens
  and doesn't survive the next import.
- Tried a blanket "turn on every Draft flow" reactivation → wrong: it would re-enable flows that were
  **intentionally** Draft, and matching flows by `workflowid` **missed** flows the managed import had
  **recreated with a new GUID**.

## Resolution

A **baseline-aware** reactivation pass over the **Dataverse Web API**, run as a pipeline step after
every managed import (full detail + the shipped script in the
[`managed-solution-import`](../skills/managed-solution-import/SKILL.md) skill;
mechanics in [`../knowledge/managed-import-flow-reactivation.md`](../knowledge/managed-import-flow-reactivation.md)):

1. **Baseline before the import** — record which `category=5` flows are Active, keyed by **stable
   name** (`uniquename`), not `workflowid`.
2. **After the import** — reactivate only flows that are now Draft **and** were Active in the baseline;
   PATCH `{statecode:1, statuscode:2}`.
3. **Verify** — re-query and assert **both** codes (a `204` is not proof); a flow still Draft fails the
   gate.
4. On `403 ConnectionAuthorizationFailed`, **retry** the transient case with backoff; if it persists,
   report the **durable** cause — the SPN lacks permission to the connection — and the fix (share the
   connection with the SPN), instead of a generic retry-failed.

**Three lessons for the next consultant:**

- **"Import succeeded" ≠ "flows are running."** In SPN-driven CI/CD, treat explicit flow reactivation as
  a mandatory release step, not an assumption — and **enforce it in the pipeline**, not in a memory note.
- **Key the baseline on a stable name, never the GUID** — a managed import can recreate a flow with a new
  `workflowid`, and GUID-matching silently skips it (the "worse than before" trap).
- **A 403 has two causes.** Transient (binding propagating — retry) vs durable (missing connection
  permission — share the connection). Retrying the durable one just wastes time and points at the wrong
  fix.

Cross-reference: the house rule is
[`../best-practices/alm-reactivate-flows-after-managed-import.md`](../best-practices/alm-reactivate-flows-after-managed-import.md);
the conditional model (when the platform *does* auto-reactivate) is in
[`../knowledge/managed-import-flow-reactivation.md`](../knowledge/managed-import-flow-reactivation.md).
