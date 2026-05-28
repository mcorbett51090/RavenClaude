# Fabric ALM runbook — <PROJECT>

> Owned by `fabric-admin`. See `knowledge/fabric-alm-cicd.md`. Principle: Git + deployment pipelines, dev/test/prod, no hand-edited prod.

## Topology
| Stage | Workspace | Capacity | Git branch |
|---|---|---|---|
| Dev | | | feature/* → main |
| Test | | | (deploy from dev) |
| Prod | | | (deploy from test) |

- **Git provider:** <Azure DevOps | GitHub> · **Connected stage:** dev only (Option 3)

## Promotion flow
1. Develop in the **dev** workspace; commit items to Git from the workspace.
2. PR-review feature branch → merge to main.
3. Deployment pipeline **dev → test**: review changes (metadata only), deploy, run validation.
4. Deployment pipeline **test → prod**: gated approval, deploy, smoke-test.

## Automation
- **Tooling:** Fabric CLI (`fab`, v1.5+) / fabric-cicd, authenticated as a **service principal**.
- **Pipeline:** <Azure DevOps Fabric extension | GitHub workflow> running `fab` tasks (workspace sync / item export / promotion).
- **Bulk moves:** Import/Export item-definition batch APIs (preview) for many-item migrations.

## Guardrails
- [ ] No hand-editing prod workspaces — all changes flow through the pipeline
- [ ] Supported-item check done (some item types are preview for Git/pipelines)
- [ ] Service-principal creds / tenant-setting changes reviewed by `ravenclaude-core/security-reviewer`
- [ ] Rollback plan: <redeploy previous stage state / Git revert>
