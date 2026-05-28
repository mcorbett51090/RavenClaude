# Fabric ALM / CI-CD

**Last reviewed:** 2026-05-28 · **Confidence:** high (first-party Microsoft Learn, retrieved 2026-05-28).
**Owner:** `fabric-admin`.
**Source:** [What is ALM in Fabric](https://learn.microsoft.com/fabric/cicd/cicd-overview), [Choose a CI/CD workflow](https://learn.microsoft.com/fabric/cicd/manage-deployment), [Best practices for lifecycle management](https://learn.microsoft.com/fabric/cicd/best-practices-cicd), [Fabric CLI](https://learn.microsoft.com/rest/api/fabric/articles/fabric-command-line-interface), [Fabric REST APIs](https://learn.microsoft.com/rest/api/fabric/articles/using-fabric-apis).

## The two complementary mechanisms

1. **Git integration (CI)** — sync a **workspace ↔ a Git repo** (Azure DevOps or GitHub) for version control, branching, history. Items are stored as Infrastructure-as-Code; commit from the workspace, update the workspace from Git.
2. **Deployment pipelines (CD)** — promote content across **dev → test → prod** stages, each linked to its own workspace. **Only metadata is copied** during deployment, not data. Compare stages, review changes before deploying.

> **House opinion #7:** ALM is Git + deployment pipelines, dev/test/prod. **No hand-editing prod workspaces.** Connect the *developer* workspace to Git; deploy from it via pipelines.

## Choosing a workflow

Microsoft's [choose-a-workflow guide](https://learn.microsoft.com/fabric/cicd/manage-deployment) lays out options; the most common enterprise pattern (Option 3) is: **Git only during development**, then deploy dev→test→prod through Fabric **deployment pipelines** (using the deployment-pipeline APIs in an Azure DevOps release or GitHub workflow for gates/approvals). Both Git integration and deployment pipelines link **one workspace to one stage** — so create separate workspaces per stage.

Supported-item caveat: some item types are still in preview for Git integration / deployment pipelines — check the [supported-items lists](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration#supported-items) before assuming full coverage.

## Automation tooling (2026)

- **Fabric CLI (`fab`)** — **v1.5 GA (March 2026)**. `pip install ms-fabric-cli` (Python 3.10+). `fab auth login` supports interactive, **service principal (secret or cert)**, and **managed identity**. v1.5 adds one-command workspace deployments with **fabric-cicd** integration, Power BI scenarios (report rebinding, semantic-model refresh), pre-installed in Fabric Notebooks, an AI-agent execution layer + REPL, Python 3.13, 30+ item types. ([CLI docs](https://microsoft.github.io/fabric-cli/))
- **fabric-cicd** — Python library for code-first deployment of Fabric items from a repo to a workspace.
- **Fabric REST APIs** — **Core APIs** (CRUD across all item types, batch) + **Workload APIs** (per-item). Auth via Entra OAuth bearer token; honors the same workspace/item permissions as the UI (automation never bypasses security).
- **Bulk import/export item-definition APIs** (**preview**, March 2026) — export/import many item definitions in one call for workspace migration / template provisioning / CI-CD.
- **Azure DevOps Pipelines extension for Fabric** — native tasks that run `fab` commands in DevOps jobs (workspace sync, item export, promotion); authenticate via a service connection.

## Runbook shape (see [`../templates/fabric-alm-runbook.md`](../templates/fabric-alm-runbook.md))
1. Dev workspace ↔ Git (feature branches).
2. Commit items; PR-review; merge to main.
3. Deployment pipeline dev→test: review changes, deploy (metadata only), run validation.
4. Test→prod: gated approval, deploy, smoke-test.
5. Automate steps 3-4 with `fab`/fabric-cicd in a DevOps/GitHub pipeline using a service principal.

> Service-principal credentials / tenant-setting changes route through `ravenclaude-core/security-reviewer`.
