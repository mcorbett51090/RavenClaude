# public-sector-govtech

Government and civic-tech delivery for teams building and operating digital services **inside or for government**. Four specialist agents cover the domains that matter most at the intersection of policy, procurement, funding, and accessibility: getting the work contracted, executing under compliance constraints, tracking how the money flows, and making every artifact legally accessible and readable.

> **The one-line philosophy:** compliance and delivery are not opposites — plan for ATO, 508 testing, and procurement checkpoints as sprint events, not end-of-project fire drills. Every mandatory requirement is binary, every grant dollar is restricted, and every document is eventually FOIA-able.

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "How do we run agile under a government contract / ATO / FAR?" | **public-sector-govtech** (`govtech-delivery-lead`) |
| "Help me respond to / write / evaluate an RFP or RFI" | **public-sector-govtech** (`public-procurement-strategist`) |
| "We got a federal grant — how do we manage it?" | **public-sector-govtech** (`grants-management-analyst`) |
| "Is our product Section 508 / WCAG compliant? Write our VPAT." | **public-sector-govtech** (`gov-accessibility-and-records-advisor`) |
| "We got a FOIA request — what do we do?" | **public-sector-govtech** (`gov-accessibility-and-records-advisor`) |
| "Rewrite this for plain language" | **public-sector-govtech** (`gov-accessibility-and-records-advisor`) |
| "Fundraising / private-foundation grants" | `nonprofit-fundraising` |
| "Build an accessible UI in code" | `web-design` |
| "Cross-sector regulatory compliance (AML, banking, environment)" | `regulatory-compliance` |
| "Write / edit the technical docs and prose" | `technical-writing-docs` |

## What's inside

- **4 agents** — `govtech-delivery-lead`, `public-procurement-strategist`, `grants-management-analyst`, `gov-accessibility-and-records-advisor`.
- **3 skills** — `public-procurement-and-rfp`, `grants-management`, `accessibility-508-and-records`.
- **3 commands** — `/public-sector-govtech:respond-to-rfp`, `:manage-grant-lifecycle`, `:audit-508-accessibility`.
- **2 templates** — `rfp-response-outline.md`, `grant-narrative.md`.
- **Knowledge bank** — `knowledge/govtech-decision-trees.md`: Mermaid trees for bid-no-bid, FedRAMP/StateRAMP needed, and the 508 conformance path; plus a dated 2026 capability map (SAM.gov, grants.gov, FedRAMP/StateRAMP, accessibility tooling).
- **6 best-practices** and **1 advisory hook** (flags missing mandatory-requirement markers, absent 508 notes, untracked grant funds, and jargon in citizen-facing text).

## House opinions (the short list)

1. Mandatory requirements are binary — meet them or be disqualified.
2. Section 508 is law, not a nice-to-have.
3. Grant funds are restricted — track them to the dollar.
4. Establish FedRAMP/StateRAMP posture before you bid.
5. Government work is discoverable — write accordingly.
6. Plain language serves the citizen and is required.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
