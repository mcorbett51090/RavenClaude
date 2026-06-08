---
description: "Run a Section 508 / WCAG 2.x conformance audit on a digital product, document, or service: identify applicable standards, recommend a testing approach (automated + manual + AT), produce a gap list with priority order, and generate a VPAT/ACR outline."
argument-hint: "[product type and context, e.g. 'web application for SSA benefit claimants, WCAG 2.1 AA required, no current VPAT']"
---

You are running `/public-sector-govtech:audit-508-accessibility`. Use the
`gov-accessibility-and-records-advisor` discipline and the `accessibility-508-and-records` skill.

## Steps

1. **Applicability determination:** confirm that the product/service is subject to the 508 Technical
   Standards. Identify the applicable edition (WCAG 2.0 AA / 2.1 AA / 2.2 AA) based on the
   solicitation or agency requirement. Traverse the 508-conformance-path tree in
   `knowledge/govtech-decision-trees.md`.

2. **Testing plan:** recommend an automated + manual + AT testing approach appropriate to the product
   type (web / software / mobile / document / video). Name specific tools (axe-core, ANDI, WAVE,
   PAC 3) and AT combinations (NVDA+Firefox, JAWS+Chrome, VoiceOver+Safari).

3. **Gap assessment:** based on any test results or product description provided, identify failures
   by WCAG success-criterion number and severity (Blocker / Major / Minor).

4. **Remediation plan:** prioritize gaps — blockers in the current sprint, majors next sprint, minors
   in the backlog. For each blocker: describe the failure, the affected user population, and the
   recommended fix.

5. **VPAT/ACR outline:** produce a VPAT 2.x skeleton with per-criterion conformance levels populated
   for the tested criteria, remarks explaining each partial/non-support finding, and placeholders for
   untested criteria with the testing method recommended.

6. Emit the Structured Output block with handoffs (govtech-delivery-lead to integrate testing into
   the sprint cadence; web-design to implement code-level fixes).
