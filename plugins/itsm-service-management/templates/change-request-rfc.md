# Change Request (RFC) — <id / short title>

> Output of the `change-and-release-manager`. Set the ceremony to the risk; standard changes don't need this (§2 #2, #3).

## Headline
<what changes + the change type, in one line>

## Change type
- standard (pre-authorized model — no CAB) / normal (assess + CAB) / emergency (expedited + retrospective)

## Risk assessment
| Dimension | Rating | Note |
|---|---|---|
| Impact | | affected services/CIs (from the CMDB) |
| Likelihood of failure | | |
| Reversibility | | rollback available? |
| **Approval level** | | matched to the risk above |

## The change
- **What + why:** <description>
- **Implementation steps:** <ordered>
- **Rollback plan:** <how to undo>
- **Schedule / window:** <when>

## Authorization
- **Authorized by:** <delegated / CAB / ECAB> — <date>
- **Deployment automation:** → `devops-cicd`
