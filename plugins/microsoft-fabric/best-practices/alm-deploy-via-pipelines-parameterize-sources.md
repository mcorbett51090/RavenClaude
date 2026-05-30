# Promote dev→test→prod through deployment pipelines, and parameterize every per-stage binding

**Status:** Absolute rule (no hand-editing prod) / Pattern (parameterize stage-specific bindings) — hand-editing a prod workspace is a bug; relying on autobind for Direct Lake / data-source connections is the documented gotcha.

**Domain:** ALM / CI-CD

**Applies to:** `microsoft-fabric`

---

## Why this exists

ALM in Fabric is **Git integration (CI)** + **deployment pipelines (CD)**: connect the *developer* workspace to Git, then promote dev→test→prod through pipelines that copy **metadata only, not data** (house opinion #7). The failure mode isn't the promotion — it's the **bindings that don't follow it**. A **Direct Lake semantic model does *not* auto-bind** to the lakehouse/warehouse in the target stage: deploy a model + its lakehouse to test, and the test-stage model **stays bound to the dev-stage lakehouse** unless you add a data-source rule. Same for mirrored-database source connections and notebook default lakehouses. Hand-editing prod to "fix" the binding defeats the whole point and drifts prod from Git. The rule: parameterize/rule every per-stage binding so promotion is clean and prod is never touched by hand.

## How to apply

Connect dev to Git, deploy through pipelines, and set deployment rules for every stage-specific binding.

```text
1. Dev workspace ↔ Git (feature branches); PR-review; merge to main.
2. Deployment pipeline dev→test: deploy (metadata only) → set rules → re-deploy so rules apply.
3. Test→prod: gated approval → deploy → smoke test. Never hand-edit prod.
```

Rules / parameters to set (these don't auto-follow the promotion):

| Item | Binding that needs a rule | Rule type |
|---|---|---|
| **Direct Lake semantic model** | the lakehouse/warehouse it reads | **Data source rule** (does NOT auto-bind) |
| **Mirrored database** | the source DB connection ID | **Data source rule** (parameterize the connection) |
| **Notebook** | its default lakehouse | **Default lakehouse rule** |
| Semantic model / dataflow connection strings | per-stage data source / parameter | Data source or **parameter rule** |

- **Rules apply only on the *next* deploy** from source→target after you create them — a "different" indicator means "deploy again to apply."
- **Parameterize in content prep:** add parameters to any definition that changes between stages (connections, item IDs, filters); set parameter rules per stage. Parameter rules used for rebinding must be **Type = Text**.
- **Test stage = simulate prod** (data volume, usage, a *similar but separate* capacity) so load tests don't destabilize prod.
- **Automate** steps with `fab` / **fabric-cicd** in a DevOps/GitHub pipeline using a **service principal** (route SPN/tenant changes through `ravenclaude-core/security-reviewer`).

**Do:**
- Promote through deployment pipelines; keep prod a deploy target, never a hand-edit surface.
- Add a **data-source rule** for every Direct Lake model and mirrored DB so it binds to the *target-stage* source.
- Use parameters/parameter-rules for connections and item bindings; deploy again to apply rules.

**Don't:**
- Assume a Direct Lake model auto-binds to the target-stage lakehouse — it doesn't; set a data-source rule.
- Hand-edit a prod workspace to fix a binding — fix the rule and re-deploy (house opinion #7).
- Forget that mirrored databases **aren't started after deployment** — start them manually or via API.

## Edge cases / when the rule does NOT apply

- **Most non-Direct-Lake semantic models *do* auto-bind** to the paired target-stage item — the rule is needed specifically for Direct Lake, mirrored DBs, notebooks, and parameter-controlled connections.
- **Pure docs / no-binding items** need no rules.
- **Some item types are still preview** for Git integration / deployment pipelines — check the supported-items list before assuming coverage.

## See also

- [`../knowledge/fabric-alm-cicd.md`](../knowledge/fabric-alm-cicd.md) — Git + deployment pipelines + `fab`/fabric-cicd/REST
- [`workspace-domain-governance-boundary.md`](./workspace-domain-governance-boundary.md) — the workspace-per-stage topology this rides on
- [`../templates/fabric-alm-runbook.md`](../templates/fabric-alm-runbook.md) — the promotion runbook
- [`../agents/fabric-admin.md`](../agents/fabric-admin.md)

## Provenance

Codifies house opinion #7 from [`../CLAUDE.md`](../CLAUDE.md) §3, grounded in [The deployment pipelines process — autobinding & considerations](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/understand-the-deployment-process) ("When a Direct Lake semantic model is deployed, it doesn't automatically bind to items in the target stage … Use datasource rules"; parameter rules must be Type Text), [Create deployment rules](https://learn.microsoft.com/fabric/cicd/deployment-pipelines/create-rules), [CI/CD for mirrored databases](https://learn.microsoft.com/fabric/mirroring/mirrored-database-cicd) (parameterize source connection ID; not started after deployment), and [Best practices for lifecycle management](https://learn.microsoft.com/fabric/cicd/best-practices-cicd) — Microsoft Learn, retrieved 2026-05-30.

---

_Last reviewed: 2026-05-30 by `claude`_
