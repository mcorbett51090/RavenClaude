# Template — agent app-package + publish checklist

Copy + fill. Source of truth: [`../knowledge/copilot-admin-governance-2026.md`](../knowledge/copilot-admin-governance-2026.md). Every agent ships as a validated app package; org-catalog publish is admin-gated.

## The package
- [ ] **App manifest** (Teams/M365) — id, name, description, version, icons (color + outline).
- [ ] **Declarative agent manifest** (pinned schema) — or custom-engine bot endpoint.
- [ ] **Plugin manifest + OpenAPI + adaptive cards** (if it has API actions).
- [ ] **Connector definition** (if it grounds via a Copilot connector).
- [ ] Icons meet size/format requirements.

## Validation (before sideload)
- [ ] Manifest schema validation passes.
- [ ] **Responsible-AI validation** passes.
- [ ] **Golden-prompt regression set** passes (`copilot-agent-eval-harness`).
- [ ] `operationId` mapping verified; connector semantic labels present; ACLs ingested.

## Publish path (admin-gated)
```
sideload (dev)  →  org catalog (AI-Admin / Global-Admin approves)  →  AppSource (optional)
```
- [ ] **Sideload** in a dev tenant; smoke-test with a real + a low-privilege identity.
- [ ] Submit to the **org catalog**; the **AI-Admin / Global-Admin approves in the Agent Registry**.
- [ ] **MCP tools** (if any) have **separate tenant consent**.
- [ ] Source-controlled the Agents-Toolkit project (don't lose source to Agent Builder).

## Governance sign-off (→ `copilot-admin-governance`)
- [ ] Oversharing remediated for any grounded org data (see `oversharing-remediation-runbook.md`).
- [ ] Purview DLP / sensitivity labels considered for the grounded content.
- [ ] Data residency confirmed acceptable.

**Licensing impact:** <Copilot seats; connector quota; PAYG; E5/Suite for Purview; or "none">
