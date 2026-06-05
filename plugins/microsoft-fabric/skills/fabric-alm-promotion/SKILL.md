---
name: fabric-alm-promotion
description: "Playbook for promoting Fabric workspace items from dev to test to prod using Git integration, deployment pipelines, and the Fabric CLI — covers branch strategy, metadata-only deploys, and the pre-promotion checklist."
---

# Fabric ALM Promotion

## When to Use This Skill

Use when setting up CI/CD for a Fabric workspace for the first time, when promoting a set of changes through dev → test → prod, or when diagnosing a failed deployment pipeline run.

## 1. The Two ALM Mechanisms

| Mechanism | What it does | When to use |
|---|---|---|
| **Git integration** | Syncs workspace items to/from a Git branch (Azure DevOps or GitHub) | Developer workflow — commit changes, review diffs, pull updates |
| **Deployment pipelines** | Promotes items from one stage (workspace) to the next with rule-based overrides | Release workflow — move from dev → test → prod |

They complement each other: Git integration handles developer collaboration; deployment pipelines handle environment promotion.

## 2. Recommended Branch and Workspace Strategy

```
main branch          ← production workspace
  ↑ merge via PR
test branch          ← test workspace
  ↑ merge via PR
feature/my-change    ← developer workspace (personal or team dev)
```

Each workspace is connected to its corresponding branch. Deployment pipelines are configured between the three workspaces (dev → test → prod).

## 3. Git Integration Setup (Azure DevOps example)

```
Workspace settings → Git integration → Connect
  Organization: myorg
  Project: DataPlatform
  Repository: fabric-workspace
  Branch: feature/my-change     (developer) or main (prod)
  Root folder: /workspaces/analytics
```

After connecting, `Commit` pushes local changes to Git. `Update all` pulls remote changes into the workspace.

**Items that sync to Git:** Notebooks, Pipelines, Dataflows, Semantic models (TMDL), Reports (PBIR), Lakehouses (metadata only — not data), Warehouses (metadata only).

**Items that do NOT sync:** Data itself (Delta tables, files in OneLake), connections, capacity assignments.

## 4. Deployment Pipeline Promotion

```bash
# Using the Fabric REST API to trigger a deployment pipeline stage
# [verify-at-build: Fabric CLI deploy command availability]
curl -X POST \
  "https://api.fabric.microsoft.com/v1/deploymentPipelines/{pipelineId}/stages/{stageId}/deploy" \
  -H "Authorization: Bearer $FABRIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceStageId": "dev-stage-id",
    "items": [
      { "sourceItemId": "notebook-guid", "itemType": "Notebook" }
    ],
    "note": "Release 2.3.1 — add customer churn features"
  }'
```

**Or via the Fabric CLI (fabric-cicd):**
```bash
pip install semantic-link-labs fabric-cicd
# fabric-cicd deploy --workspace-id <prod-ws-id> --item-type Notebook --item-id <id>
```

[verify-at-build: `fabric-cicd` API surface changes frequently.]

## 5. Deployment Rule Overrides

Deployment rules allow you to override connection strings, workspace parameters, and data source credentials per stage without changing the item definition:

| Rule type | Example |
|---|---|
| Data source rule | Point a pipeline to the prod SQL server instead of dev |
| Parameter rule | Override a notebook parameter (e.g. `target_schema = "gold_prod"`) |
| Connection rule | Override a connector credential to the prod service principal |

Configure rules in: Deployment pipeline → stage → Rules → Add rule.

## 6. Pre-Promotion Checklist

Before promoting from dev → test → prod:

- [ ] All changed items committed to the feature branch and PR approved
- [ ] Feature branch merged to test branch; test workspace refreshed (`Update all`)
- [ ] Regression test run: key pipelines, notebooks, and semantic model refreshes executed in test
- [ ] Deployment rules verified for the target stage (correct data sources, credentials)
- [ ] No hand-edits in the test or prod workspace — all changes come through the pipeline
- [ ] Rollback plan documented: which Git commit to revert to and which pipeline run was last good

## 7. Fabric CLI Automation (GitHub Actions)

```yaml
- name: Deploy to Prod
  uses: Azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

- name: Trigger Fabric Deployment Pipeline
  run: |
    TOKEN=$(az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv)
    curl -X POST \
      "https://api.fabric.microsoft.com/v1/deploymentPipelines/$PIPELINE_ID/stages/$STAGE_ID/deploy" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{ "sourceStageId": "$TEST_STAGE_ID", "note": "Automated deploy from CI" }'
```

## Pitfalls

- Hand-editing a prod workspace instead of promoting through the pipeline — changes are overwritten on the next deployment and lost
- Connecting the prod workspace to `main` and pushing directly — bypasses the test stage and PR review
- Forgetting that Git sync is metadata-only — Delta table data and OneLake files are not versioned by Git integration; data migrations need a separate strategy
- Not setting deployment rules — dev pipeline connections pointing to prod data sources in the test stage, or vice versa

## See Also

- [`../../agents/fabric-admin.md`](../../agents/fabric-admin.md) — ALM, Git integration, deployment pipelines, and Fabric CLI
- [`../../agents/fabric-architect.md`](../../agents/fabric-architect.md) — workspace/domain/capacity topology
- [`../../CLAUDE.md`](../../CLAUDE.md) — house opinion: ALM is Git + deployment pipelines; no hand-editing prod
