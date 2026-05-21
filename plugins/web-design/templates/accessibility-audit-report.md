# Accessibility audit report — [Site / scope]

**Audit scope:** [pages / templates / components covered]
**Standard:** WCAG 2.2 AA (default) | AAA (where noted)
**Auditor:** [...]
**Audit date:** [YYYY-MM-DD]
**Tools used:** [axe-core / Lighthouse / Wave / Pa11y + manual + NVDA / VoiceOver / etc.]
**Confidentiality:** internal | client-confidential

---

## Executive summary

- **Total findings:** [count]
- **By severity:** P0 [N] / P1 [N] / P2 [N] / P3 [N]
- **Headline issues:** [3-4 highest-impact findings, one line each]
- **Recommendation:** Ship-ready | Ship after P0 + P1 remediation | Significant rework needed
- **Time-to-remediate estimate:** [hours / days]

---

## Methodology

- **Pass 1 (automated):** [tools run; ~30-40% of issues caught]
- **Pass 2 (semantic / structural):** [manual DOM inspection]
- **Pass 3 (keyboard):** [tab-through every interactive surface]
- **Pass 4 (screen reader):** [VoiceOver + NVDA on N flows]
- **Pass 5 (color + motion):** [contrast checks + reduced-motion check]

---

## Findings

| # | Severity | SC | Page / component | Issue | Remediation | Owner | Target date | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | P0 | 1.4.3 | Homepage hero | Body text 2.1:1 contrast on overlay | Add 60% black tint to hero overlay | [name] | YYYY-MM-DD | Open |
| 2 | P0 | 4.1.2 | Newsletter form | Submit button is `<div>` — not keyboard / screen-reader accessible | Change to `<button>` | [name] | YYYY-MM-DD | Open |
| 3 | P1 | 1.1.1 | All blog posts | Author photo missing `alt` | Add author name as alt | [name] | YYYY-MM-DD | Open |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Severity breakdown

### P0 — blocks primary user task

[Detailed write-up of each P0 finding: WCAG SC, where, what the issue is, screen-reader / keyboard impact, remediation specifics.]

### P1 — significant degradation for affected users

[...]

### P2 — non-critical surface failures

[...]

### P3 — improvable; not a current AA failure

[...]

---

## Tested coverage

| Surface | Browsers tested | Devices tested | Screen readers tested |
|---|---|---|---|
| Homepage | Chrome 120, Safari 17, Firefox 121 | iPhone 15, Pixel 8, MacBook | VoiceOver (macOS + iOS), NVDA |
| ... | ... | ... | ... |

---

## Areas not audited

- [Surface] — [reason: out of scope / will audit next cycle / requires different tooling]

---

## Remediation plan

1. **P0 (within 2 weeks):** [list]
2. **P1 (within 4 weeks):** [list]
3. **P2 (within current quarter):** [list]
4. **P3 (backlog):** [list]

## Re-audit

- **Scheduled:** [YYYY-MM-DD — typically 30 days after P0 + P1 remediation]
- **Scope:** Re-test all P0 + P1 findings; spot-check P2

---

**Sources cited:**
- WCAG 2.2 Quick Reference: <https://www.w3.org/WAI/WCAG22/quickref/>
- ARIA Authoring Practices Guide: <https://www.w3.org/WAI/ARIA/apg/>
- [Any specific SC pages referenced]

**Auditor sign-off:** [name] — [YYYY-MM-DD]
**Stakeholder review:** [name] — [YYYY-MM-DD]
