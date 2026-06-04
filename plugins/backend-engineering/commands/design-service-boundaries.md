---
description: "Decide monolith vs services and draw domain-driven boundaries; choose sync vs async per seam."
argument-hint: "[system + scale + team shape]"
---

You are running `/backend-engineering:design-service-boundaries`. Use `backend-architect` + the `service-boundary-design` skill.

## Steps
1. Traverse the boundary tree; default to a modular monolith.
2. If splitting, draw bounded contexts that own their data; name the trade.
3. Choose sync vs async per seam; own each failure model.
4. Route the contract to api-engineering, the schema to database-engineering.
5. Emit + Structured Output block.
