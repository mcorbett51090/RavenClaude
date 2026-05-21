---
scenario_id: 2026-05-21-flow-clientdata-shape-drift
contributed_at: 2026-05-21
plugin: power-platform
product: dataverse-web-api
product_version: "v9.2 (2026.04)"
scope: version-specific
tags: [dataverse-web-api, workflow-entity, clientdata, flow-import, json-shape]
confidence: high
reviewed: false
---

## Problem

Creating Power Automate cloud flows programmatically via Dataverse `POST /workflows` succeeded (HTTP 201 with the new workflow ID), but the flows **imported clean and ran broken** — they had structural defects only visible at first execution (missing triggers, malformed actions, connection references not resolved).

The root cause: copying the `clientdata` JSON shape from a **PA Management API export** verbatim into the Dataverse Web API `workflows` POST body. The two surfaces use different `clientdata` structures, even though the field name is the same.

## Permissions context

- Customer DEV environment, bulk-flow-creation engagement (~136 flows in scope)
- SPN authenticated as Application User in the target environment (per [`./2026-05-21-spn-flow-create-403.md`](2026-05-21-spn-flow-create-403.md))
- Workflow created with `category=5, type=1, primaryentity="none"` per Dataverse spec
- Engagement attempted to template the flows from prior PA Management API exports

## Attempts

- Tried: POSTing the PA-Management-API-export-shaped JSON directly as `clientdata` → workflow created (HTTP 201) but failed at first trigger run with "missing trigger" or "could not resolve connection reference"
- Tried: Wrapping the export in additional metadata fields per the Dataverse spec → still broken
- Tried: Capturing a live Dataverse `workflow` record (`GET /workflows({fid})?$select=clientdata`) and comparing the shape to the PA export → discovered the structural differences (top-level `properties` wrapper, nested `connection` sub-object on `connectionReferenceLogicalName`, etc.)
- Tried: Using the live-record shape as the template instead of the PA export → flows imported clean and ran correctly

## Resolution

**The Dataverse `clientdata` shape is NOT the same as the PA Management API export shape.** Both are valid JSON; both nominally represent the same flow; the Dataverse surface wraps the entire definition in a `properties` block and nests connection references differently. A PA-export-shaped `clientdata` will create a workflow record that *looks* fine in the API but is structurally broken at execution time.

**The reliable pattern is to template from a live Dataverse record, not a PA Management API export.** Specifically:

1. Manually build one canonical flow in the target environment via the Power Automate maker portal
2. `GET /workflows({fid})?$select=clientdata` to capture the live shape
3. Parse the captured `clientdata` (it's a JSON string inside a JSON field — yes, double-encoded)
4. Use *that* shape as the template for programmatic creation
5. Inject the engagement-specific variations (trigger entity, action parameters, connection references) into the live template, not into an export-shaped template

**Action for the next consultant hitting this pattern:** if you're scripting cloud-flow creation via Dataverse, your first step before any programmatic POST is to grab a live `clientdata` from the target environment. Never assume PA exports are a drop-in template — they're not.

Cross-reference: this scenario is the operational complement to [`../knowledge/programmatic-flow-creation.md`](../knowledge/programmatic-flow-creation.md), which covers the `category=5 / type=1 / primaryentity="none"` schema in depth. The knowledge file mentions the `clientdata` shape gotcha; this scenario is the field-note version that surfaces the *specific failure mode* (created-clean / runs-broken) so the next engagement recognizes the symptom.
