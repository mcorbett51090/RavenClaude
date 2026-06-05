---
name: content-promotion-runbook
description: "Step-by-step runbook for promoting Tableau workbooks and data sources from development through test to production using the Content Migration Tool, REST API, and tabcmd — with pre-promotion checklists, rollback steps, and the governance gates that prevent silent data breaks. Owned by tableau-admin."
---

# Content Promotion Runbook

## When to invoke

- Promoting a new or updated workbook from dev → test → prod.
- Onboarding a new project to a repeatable promotion pipeline.
- Debugging a promotion that broke a dashboard (broken data source connections, wrong extracts, missing permissions).
- Replacing a manual hand-republish workflow with an automated one.

## Principle: promote, never rebuild

Hand-republishing a workbook in each environment (open Tableau Desktop, reconnect to the prod server, republish) is the highest-risk promotion method — connection strings, credentials, and permissions are reset by hand, producing silent differences. Use CMT or REST API to promote as an artifact.

## Pre-promotion checklist (fill out before every promotion)

- [ ] Workbook version bumped (Description field or an embedded version calc updated).
- [ ] Performance Recording shows load time < 5 s on dev data at representative volume.
- [ ] RLS tested with a named test user account in the source environment (not the publisher's account).
- [ ] Upstream data source (extract or live connection) exists in the target environment under the same logical name.
- [ ] Published data source (if used) exists and is tested in the target environment.
- [ ] Permissions reviewed: which groups/users need Viewer vs Explorer vs Creator in the target project.

## Option A — Content Migration Tool (CMT) — recommended for most promotions

CMT is the Tableau-supported GUI + CLI tool for promoting content between sites and environments.

```
Plan steps:
1. Source: Site/Project/Workbook or Data Source
2. Target: Site/Project in the target environment
3. Mapping: map data source connection strings dev→prod (Connections tab)
4. Options: overwrite existing, preserve permissions, include extract OR reconnect to published DS
5. Run → review the migration report for errors
```

Key mapping rules:
- Always map **connection strings** explicitly — CMT will not auto-discover prod credentials.
- If the workbook uses embedded credentials, rotate them post-promotion and use a service account, not a personal credential.
- Select "Preserve permissions" only if the target project's permission model matches the source — mismatched models silently over-grant.

## Option B — REST API promotion (for CI/CD pipelines)

```python
import tableauserverclient as TSC

# Authenticate to target server
server = TSC.Server("https://prod-tableau.company.com", use_server_version=True)
tableau_auth = TSC.PersonalAccessTokenAuth("svc_deploy", PAT_SECRET, "DefaultSite")

with server.auth.sign_in(tableau_auth):
    # Download from source (already authenticated)
    workbook_path = source_server.workbooks.download(workbook_id, filepath="/tmp")
    
    # Publish to target project
    target_project = find_project(server, "Production/Finance")
    publish_mode = TSC.Server.PublishMode.Overwrite
    new_wb = TSC.WorkbookItem(target_project.id)
    server.workbooks.publish(new_wb, workbook_path, publish_mode,
                             connections=prod_connection_credentials)
```

Connection credentials must be supplied at publish time — never embedded in the `.twbx` or the script. Use a secrets manager or CI/CD environment variable.

## Option C — tabcmd (for scripted, low-complexity promotions)

```bash
tabcmd login --server https://prod-tableau.company.com \
             --username svc_deploy --password "${TABCMD_PASSWORD}" \
             --site "DefaultSite"

tabcmd publish "Finance_Dashboard.twbx" \
  --project "Production/Finance" \
  --overwrite \
  --db-username "$PROD_DB_USER" \
  --db-password "$PROD_DB_PASS"
```

tabcmd is simpler than REST API but does not support connection mapping for multi-source workbooks. Use CMT or REST API for workbooks with > 1 data source.

## Post-promotion verification steps

1. **Load test**: open the promoted workbook as a non-admin user in the target environment. Confirm it loads within 5 s.
2. **Data spot-check**: compare 3 key metrics between the newly promoted view and the source environment. Flag any difference > 0.1 % for investigation.
3. **RLS spot-check**: log in as the designated test user in the target environment. Confirm the user sees only their authorised data.
4. **Permission spot-check**: confirm one Viewer, one Explorer, and one non-member can or cannot access the workbook as expected.

## Rollback procedure

If the promoted workbook is broken:

1. In Tableau Server/Cloud, navigate to the workbook → Revisions → Restore to the previous version.
2. Tableau retains the last 25 revisions (default) — confirm the retention policy before relying on this.
3. If revision history was disabled or the previous version is too old: restore from CMT backup (CMT can export content to a local archive before migration — always enable this).
4. File a post-mortem: which promotion gate was missing that would have caught this?

## Pitfalls

- Manually republishing from Tableau Desktop to the production server — connection strings, credentials, and permissions are reset differently each time; the workbook diverges from the dev canonical.
- Skipping the data spot-check because "the query is the same" — a connection string mapped to the wrong schema, or an extract pointing to the old dev data, passes a load test and fails silently on data.
- Storing the service-account PAT in the `tabcmd` script — use environment variables or a secrets manager.
- Promoting a workbook without testing RLS in the target environment — RLS entitlement tables often differ between environments; a test in dev passes while prod exposes unintended rows.
