# Use feature branches and structured commits for Fabric items — one branch per ticket, not per developer

**Status:** Pattern
**Domain:** Fabric ALM / Git integration
**Applies to:** `microsoft-fabric`

---

## Why this exists

Fabric Git integration allows workspace items to be committed to and synced from a Git repository. Without a branching discipline, multiple developers editing the same notebook or pipeline directly on the main branch create merge conflicts in the item JSON that the Fabric UI cannot resolve — the sync fails silently or one developer's change overwrites another's. The "one branch per ticket, not per developer" rule keeps conflicts small and makes deployment-pipeline promotion deterministic: you promote the branch-specific diff, not a mixed bag of everyone's simultaneous edits.

## How to apply

Branching workflow:

```
main          ← auto-synced to prod workspace (read-only for developers)
  └── dev     ← synced to dev workspace; base for all feature branches
       └── feature/TICK-123-add-silver-transform  ← developer branch
       └── feature/TICK-456-update-dax-measure     ← another developer
```

Daily workflow:
1. **Create** a branch from `dev` named `feature/<ticket>-<slug>`.
2. **Sync** the feature branch to a personal workspace (each developer has their own).
3. **Build and test** in the personal workspace.
4. **Commit** via `Commit` in the Fabric Git panel — write conventional commit messages: `feat(lakehouse): add silver transform for orders`.
5. **PR** from `feature/*` into `dev`; reviewer syncs `dev` to the shared dev workspace and validates.
6. **Promote** `dev` to test and prod via the Fabric deployment pipeline.

**Do:**
- Commit after every logical unit of work (one notebook, one pipeline change) — not at end of day with multiple unrelated changes.
- Use the `fab` CLI `workspace sync` to automate branch-to-workspace sync in CI.
- Protect the `main` and `dev` branches from direct push — require PRs and at least one reviewer.

**Don't:**
- Commit directly to `dev` or `main` from the Fabric portal UI for any change that belongs in a ticket — the portal commit bypasses PR review.
- Mix pipeline parameterization changes with notebook logic changes in a single commit — keep diffs small and reviewable.
- Use a personal workspace as the long-running "dev" workspace — personal workspaces have capacity limits and may be cleaned up by Fabric; use a team dev workspace for shared validation.

## Edge cases / when the rule does NOT apply

A solo developer on a small project with a single workspace may commit directly to `main` — document the decision and add the branching discipline before the second developer joins.

## See also

- [`../agents/fabric-admin.md`](../agents/fabric-admin.md) — owns Fabric ALM, Git integration, and deployment pipelines
- [`./alm-deploy-via-pipelines-parameterize-sources.md`](./alm-deploy-via-pipelines-parameterize-sources.md) — the deployment-pipeline promotion that follows this branching discipline

## Provenance

Codifies CLAUDE.md house opinion #7 ("ALM is Git + deployment pipelines, dev/test/prod; no hand-editing prod; metadata-only deploys") applied to the Git-integration branching surface; Microsoft Learn Fabric Git integration documentation.

---

_Last reviewed: 2026-06-05 by `claude`_
