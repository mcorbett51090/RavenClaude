# Promote Power BI Reports via Deployment Pipeline, Not Publish-Overwrite

**Status:** Absolute rule
**Domain:** Power BI / ALM
**Applies to:** `power-platform`

---

## Why this exists

"Publish from Desktop" to a production workspace is the Power BI equivalent of hand-editing a production database. It overwrites the live semantic model and report in one click — no review, no test stage, no rollback. If the new model breaks a dashboard, the only recovery is to re-publish the previous `.pbix` (if you still have it). It bypasses any dataset parameters or workspace variables that differ between environments, so the published model often points at the wrong data source. Worse, it resets the scheduled refresh configuration, RLS roles, and any endorsement labels the workspace curator applied. This pattern looks fast in dev; it is a reliability and governance anti-pattern in production.

## How to apply

Use **Power BI Deployment Pipelines** (Fabric workspace deployment pipelines) for every dev → test → prod promotion. Source-control the PBIP unpacked tree; let the pipeline — not a desktop publish — carry the artifact forward.

```
Dev workspace → [Deployment Pipeline] → Test workspace → [Deployment Pipeline] → Prod workspace
     ↑
 PBIP committed to git / ADO
 Publish to Dev only from source (PBIP → Desktop → Publish OR fab CLI)
```

**Do:**
- Configure workspace parameters or deployment-pipeline rules to override data-source connections per stage (test vs prod lakehouse URL, gateway, etc.).
- Retain scheduled-refresh config, RLS roles, and sensitivity labels by managing them in the pipeline, not in Desktop.
- Use the Fabric REST API (`POST /pipelines/{pipelineId}/stages/{stageOrder}/deploy`) for CI-triggered promotions.
- Gate test → prod promotion on a UAT sign-off and a `pac solution check`-equivalent (`pbi scan` or semantic model validation).
- Keep a record of every production deployment: who promoted, what commit, when.

**Don't:**
- Publish from Power BI Desktop directly to test or prod workspaces — reserve Desktop publish for the **dev** workspace only.
- Overwrite a production semantic model without checking that the data-source parameters point at the production source.
- Treat "I published and the report looks right" as a deployment test — verify scheduled refresh fires, RLS rows are filtered correctly (tested as role), and gateway credentials are valid.

## Edge cases / when the rule does NOT apply

- A personal BI report in "My Workspace" (no shared consumers, no refresh, personal use) can be published directly — there is no prod environment to protect.
- During the initial PBIP project setup, publishing to a dev workspace directly from Desktop is expected — the pipeline governs promotion beyond dev.

## See also

- [`../agents/power-bi-engineer.md`](../agents/power-bi-engineer.md) — owns PBIP git + deployment pipeline design
- [`./tmdl-pbip-source-control-hygiene.md`](./tmdl-pbip-source-control-hygiene.md) — the source-control discipline that feeds the pipeline
- [`./bi-refresh-and-gateway-reliability.md`](./bi-refresh-and-gateway-reliability.md) — what breaks after promotion if refresh/gateway isn't validated

## Provenance

Codifies `power-bi-engineer`'s ALM opinion (referenced in `skills/power-bi/` and `CLAUDE.md` §4 anti-patterns: "Checking binary .pbix files into git/ADO repos"). Standard Power BI ALM practice per Microsoft Learn *Deployment pipelines, the ultimate guide* (May 2026).

---

_Last reviewed: 2026-06-05 by `claude`_
