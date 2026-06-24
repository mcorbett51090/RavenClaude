# Accessibility Engineering Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible accessibility figures come from

WCAG criteria, levels, and the laws that reference them (ADA Title III, Section 508 / the Revised 508 standards adopting WCAG 2.0 AA, AODA, EN 301 549) are **versioned and jurisdiction-specific** and change over time. **Cite the WCAG version + date for any criterion, and mark unsourced figures `[unverified — training knowledge]` (§3 #8).** The most defensible evidence is a dated audit against a named target plus AT-session recordings — not a tool's summary number.

## Regulatory drivers (dated — `[unverified — training knowledge]`)

Accessibility is increasingly a hard market gate, not only a US-ADA / Section 508 concern. The driver most likely to be newly in scope for an EU-market product:

- **European Accessibility Act (EAA, Directive (EU) 2019/882)** — its accessibility obligations have **applied since 28 June 2025**, making accessibility a binding requirement for in-scope consumer products and services placed on the EU market (e-commerce, consumer banking, e-books / e-readers, transport and ticketing apps/websites, and more). The presumptive conformance standard is **EN 301 549** — note its current harmonized version (**v3.2.1**) maps to **WCAG 2.1 AA** (not 2.2; EN 301 549 is itself versioned and a later revision may shift the benchmark). Some existing service contracts and self-service terminals carry a **transition tail to 2030**. Treat "is this product in EU-market scope?" as a standard intake question. The exact scope, exemptions, member-state transposition, and whether a specific gap creates liability remain **qualified counsel's determination** (§2, §3 #6). `[unverified — training knowledge]`

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Automated-tool coverage | Often cited around a third of WCAG issues | Depends on tool, ruleset, and content; treat as a floor |
| Legal floor | AA is the commonly-referenced contractual/regulatory level | The applicable law/version is counsel's determination (§2 #6) |
| Contrast thresholds | AA 4.5:1 normal / 3:1 large; AAA 7:1 / 4.5:1 | Fixed by WCAG version — compute the ratio (§3 #5) |
| Cost-to-fix | Cheapest in design, escalating through code, QA, post-release | Org-specific; the direction is robust (§3 #7) |

## Operating rhythm

- **Design-time** — contrast-checked tokens, accessible components, a11y in the definition-of-done (§3 #7).
- **Per-PR** — automated scan + keyboard pass in code review (a floor, not a conformance claim, §3 #2).
- **Per-release** — manual + AT audit against the named target, weighted score, remediation re-ranked (§3 #1 #2).

## The standing caution

Whether a given accessibility gap creates ADA / Section 508 / AODA / EN 301 549 **legal liability** is qualified counsel's determination (§2 #6) — the team scopes the technical gap to a conformance target and frames remediation, it does not render legal or certification verdicts. Keep user PII and assistive-tech session recordings out of deliverables (§2).
