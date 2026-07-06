# Design brief — [Project name]

> Project kickoff / discovery deliverable. The brief that everyone agrees on before the wireframe / token / code work starts.

**Project:** [...]
**Client / stakeholder:** [...]
**Lead designer:** [...]
**Timeline:** [...]
**Status:** Draft | Approved | In progress | Shipped
**Last updated:** [YYYY-MM-DD]
**Confidentiality:** internal | client-confidential

---

## 0. Pipeline gate G1 — archetype, stack & budgets (required to pass G1)

> The [`gold-standard-website-pipeline`](../skills/gold-standard-website-pipeline/SKILL.md) **G1** gate requires every field below filled with a **number or a named choice**, not an adjective. A brief with "fast" / "accessible" instead of numbers **fails G1** and cannot proceed to G2.

- **Archetype (declare exactly one):** marketing | web-app | ecommerce — _re-weights every later gate and selects the seams._
- **Stack decision + ≥2 alternatives considered** (not "we picked Next because Next"):

  | Chosen | Rendering (SSG/SSR/RSC/CSR) | Why | Alternative 1 (why not) | Alternative 2 (why not) |
  | ------ | -------------------------- | --- | ----------------------- | ----------------------- |
  |        |                            |     |                         |                         |

  _Static-first bias: SSG > SSR > CSR unless a reason is stated. **Web-app caveat:** hosting/CDN is provisional until `frontend-engineering`'s rendering-strategy call at the G5 seam._

- **Hosting / CDN:** [named; note any `azure-cloud` seam split if Azure SWA]
- **Numeric performance budget (per template — declared now, enforced at G7; seeds [`performance-budget.md`](performance-budget.md)):**

  | Template  | LCP (s) | INP (ms) | CLS   | Critical-path KB (compressed) |
  | --------- | ------- | -------- | ----- | ----------------------------- |
  | Home      | ≤ 2.5   | ≤ 200    | ≤ 0.1 | ≤                             |
  | [others…] |         |          |       |                               |

- **Accessibility target:** WCAG 2.2 **AA** floor; AAA stretch items adopted on primary flows: [list or "none"]
- **Success metric + measurement mechanism:** [metric — conversion rate / task-completion / AOV] measured via [analytics event / RUM / funnel instrumentation] — named so G4/G7 can wire it.
- **Escalation flags raised now (not discovered mid-build):**
  - [ ] web-app with substantial custom interactivity → `frontend-engineering` handoff boundary noted before G5
  - [ ] any login / auth surface → `auth-identity` seam (OAuth/OIDC flow, session/token strategy, MFA — reviewed **before** G5 builds it; `auth-identity` if installed, else a documented non-specialist stand-in, re-run once installed)
  - [ ] ecommerce → platform-vs-headless decision scheduled before G5 (`ecommerce-dtc` if installed; else a documented non-specialist stand-in, re-run once installed)
  - [ ] auth / sessions / payments / PII / untrusted input → `security-reviewer` **review before G5 closes** + mandatory G9 sign-off
  - [ ] native mobile in scope → `mobile-engineering`

## 1. Purpose

[2-3 sentences: what we're making and why. Outcome-language, not feature-language.]

## 2. Audience

- **Primary:** [Who? Demographics + role + level of sophistication.]
- **Secondary:** [...]
- **Excluded:** [Who this is *not* for — clarifies design tone.]

### User scenarios

| Scenario | Trigger | User goal | Success looks like |
|---|---|---|---|
| | | | |

## 3. Goals & success metrics

- **Business goals:** [...]
- **Success metrics:** [Concrete, measurable. "Reduce form-abandonment by 20%."]
- **Anti-goals:** [What we're explicitly *not* optimizing for.]

## 4. Constraints

- **Brand:** [link to brand system or note: TBD this engagement]
- **Tech stack:** [Astro / Next / etc., or "TBD"]
- **Hosting:** [...]
- **Timeline:** [milestone dates]
- **Budget:** [hours / $ if relevant]
- **Accessibility floor:** WCAG 2.2 AA (default) | AAA (stretch)
- **Performance floor:** CWV "Good" (LCP ≤ 2.5s, CLS ≤ 0.1, INP ≤ 200ms) at P75
- **Browser / device support:** [last 2 versions of Chrome / Safari / Firefox / Edge; specific mobile devices]
- **Locale / i18n:** [single-language launch + plan, or multi-language from day 1]

## 5. Scope

### In scope

- [Pages / sections / features]

### Out of scope

- [Explicit exclusions]

## 6. Content

- **Content source:** [client-supplied | content-strategist-authored | hybrid]
- **Content style guide:** [link or "TBD"]
- **Word count estimate:** [per page or total]
- **Content delivery deadline:** [Date — late content compresses build]

## 7. References / inspiration

- [Sites we like, with notes on *why* (not just "looks good")]
- [Anti-references: sites we want to avoid emulating, with why]

## 8. Team

| Role | Owner | Backup |
|---|---|---|
| Web architect | [...] | |
| UX designer | [...] | |
| Visual designer | [...] | |
| Frontend implementer | [...] | |
| Content strategist | [...] | |
| Accessibility auditor | [...] | |
| Performance engineer | [...] | |
| Client lead | [...] | |

## 9. Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|

## 10. Open questions

- [...]

---

**Sign-off:**

- Client lead: [name] — [YYYY-MM-DD]
- Project lead: [name] — [YYYY-MM-DD]
