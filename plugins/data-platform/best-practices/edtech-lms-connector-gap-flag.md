# Flag the EdTech LMS connector gap at engagement start and route to a custom build

**Status:** Pattern
**Domain:** Connector / EdTech
**Applies to:** `data-platform`

---

## Why this exists

No first-class managed ELT connector (Fivetran, Airbyte Cloud catalog) ships production-grade support for Canvas, Moodle, Schoology, Blackboard, or D2L. An engagement that starts by searching the Fivetran or Airbyte connector catalog will not find these and may conclude incorrectly that the data can't be pulled. The correct answer is a custom Airbyte connector (the `connector-developer` agent owns the implementation) combined with a handoff acknowledgment to `edtech-partner-success` for the partner-health layer above the data. Missing this flag at engagement start wastes discovery time and delays the correct architecture decision.

## How to apply

When the engagement context contains any of these signals, raise the flag before the stack selection:

**Trigger signals:**
- Client is a school district, edtech vendor, or higher-ed institution
- Source system is Canvas, Moodle, Schoology, Blackboard, or D2L
- Client asks "can we pull our LMS data?"
- Engagement uses student performance, course completion, or learning-analytics metrics

**Flag message (in the `stack-decision-record.md` Connector Selection section):**

```markdown
## Connector Selection

**Source:** Canvas LMS

**Connector gap:** No first-class managed connector available on Fivetran or Airbyte Cloud
(verified: knowledge/edtech-lms-connector-gap.md, last reviewed [date]).

**Recommended path:** Custom Airbyte source connector via `connector-developer` agent.

**Handoff:** Partner-success layer (QBR health scoring, renewal signals) routes to
`edtech-partner-success` after the data layer is built.

**Estimate impact:** Add [N] days to pipeline build estimate for custom connector work.
```

**Do:**
- Check the LMS gap knowledge file before recommending any managed connector for EdTech sources.
- Involve `connector-developer` in the engagement scoping call if LMS data is a primary source.
- Document the custom connector scope as a distinct deliverable with its own acceptance criteria.

**Don't:**
- Assume a managed connector exists because the source is popular (Canvas has millions of users but no first-class connector).
- Use the "REST API" generic connector as a long-term substitute for a purpose-built Airbyte source.
- Omit the EdTech-partner-success handoff — the data layer and the partner layer are different deliverables.

## Edge cases / when the rule does NOT apply

- If the client is a large enterprise using a commercial EdTech platform that has since added a managed connector (verify at build time), the custom build may no longer be necessary.
- If the LMS data is only a minor signal (e.g., one of ten source systems) and the client can accept delayed/manual export, a file-based connector may be an acceptable stopgap — document the limitation.

## See also

- [`../agents/connector-developer.md`](../agents/connector-developer.md) — builds the custom Airbyte source connector
- [`./connector-document-the-handoff-at-design-time.md`](./connector-document-the-handoff-at-design-time.md) — the handoff documentation rule that applies to the custom connector

## Provenance

Codifies data-platform CLAUDE.md §3 house opinion #11 ("EdTech LMS is a connector-gap") and knowledge from `knowledge/edtech-lms-connector-gap.md`. Listed as the plugin's highest-leverage proprietary claim.

---

_Last reviewed: 2026-06-05 by `claude`_
