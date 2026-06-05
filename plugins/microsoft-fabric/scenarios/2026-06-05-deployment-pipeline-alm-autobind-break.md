---
scenario_id: 2026-06-05-deployment-pipeline-alm-autobind-break
contributed_at: 2026-06-05
plugin: microsoft-fabric
product: alm
product_version: "2026.05"
scope: likely-general
tags: [alm, deployment-pipeline, autobind, parameterize, git-integration, prod]
confidence: medium
reviewed: false
---

## Problem

A team promoted a Direct Lake semantic model from **dev → test** through a Fabric deployment pipeline. The deploy reported success, but the test-stage report showed **dev data** — and a few hours later a dev-side gold reload made the test report numbers shift, alarming a stakeholder reviewing test. The instinct was to "open the test workspace and repoint the model," and someone had already started doing exactly that in the prod-adjacent test workspace by hand.

## Constraints context

- Fabric **Git integration** on the dev workspace + **deployment pipelines** for dev→test→prod (CLAUDE.md §3 #7).
- The promoted item was a **Direct Lake semantic model** paired with its own lakehouse in each stage.
- Deploy "succeeded" — no error surfaced; the binding was just wrong.
- Capacity admin + pipeline access available; a mirrored database was also in the pipeline (separate symptom, same root cause class).

## Attempts

- Tried: reading *why* test showed dev data rather than re-pointing by hand. A **Direct Lake semantic model does not auto-bind** to the target-stage lakehouse on deploy — the test-stage model stayed bound to the **dev-stage lakehouse** because no **data-source rule** existed for it. (Most non-Direct-Lake models *do* auto-bind, which is why the team assumed this one had too.) Outcome: identified the missing deployment rule as the root cause, not a corrupt deploy.
- Tried (rejected, and caught mid-action): hand-editing the test workspace to repoint the model. This "works" once but **drifts the stage from Git/the pipeline** and trains the team to fix prod by hand — the exact §3 #7 anti-pattern. Outcome: stopped; reverted the manual change.
- Tried (the move that worked): added a **data-source rule** on the pipeline mapping the model to the *target-stage* lakehouse/warehouse, then **re-deployed** (rules apply only on the *next* deploy — the "different" indicator meant "deploy again to apply"). Test now read test data. While there, parameterized the **mirrored database's source connection ID** with a data-source rule (it also doesn't auto-follow) and noted that **mirrored databases are not started after deployment** — started it via API. Outcome: clean, repeatable promotion with no hand-edits.

## Resolution

The "wrong data after a successful deploy" was a **missing data-source rule**, not a broken pipeline: Direct Lake models (and mirrored DBs, and notebook default lakehouses) **do not auto-bind** to the target stage. The fix is to set a deployment rule for every per-stage binding and **re-deploy so the rule applies** — never to hand-edit the target workspace, which drifts it from Git.

**Action for the next consultant hitting this pattern:** when a deployment-pipeline promotion "succeeds" but the target stage shows the wrong (source-stage) data, suspect a **missing data-source rule on a Direct-Lake model / mirrored DB / notebook**, not a corrupt deploy — and **do not repoint the target workspace by hand** (that defeats ALM and drifts prod from Git). Add the rule, re-deploy to apply it, and remember mirrored DBs aren't auto-started post-deploy. Apply [`../best-practices/alm-deploy-via-pipelines-parameterize-sources.md`](../best-practices/alm-deploy-via-pipelines-parameterize-sources.md), and route any SPN/tenant change through `ravenclaude-core/security-reviewer`. Field-note complement to that canonical rule + the [`../templates/fabric-alm-runbook.md`](../templates/fabric-alm-runbook.md).

**Sources (Microsoft Learn, retrieved 2026-06-05 — `[verify-at-use]`, supported-item lists shift monthly):** [Understand the deployment process — autobinding](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/understand-the-deployment-process) ("a Direct Lake semantic model … doesn't automatically bind to items in the target stage … Use datasource rules") · [Create deployment rules](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/create-rules) · [CI/CD for mirrored databases](https://learn.microsoft.com/fabric/mirroring/mirrored-database-cicd) (parameterize source connection; not started after deployment). Re-confirm Git-integration/pipeline preview-vs-GA item coverage before quoting (house opinion #9).
