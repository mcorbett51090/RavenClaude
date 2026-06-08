---
description: "Run the full leasing and tenant lifecycle: marketing to inquiry, screening, application, move-in, lease administration, renewals, move-out, and deposit disposition. Covers funnel conversion analysis, consistent-criteria screening policy, renewal pricing economics, and disposition documentation discipline."
---

# Leasing and Tenant Lifecycle

**Purpose:** execute a leasing and tenant lifecycle that fills units fast, screens consistently,
retains good tenants, and exits cleanly — minimizing liability at every handoff point.

---

## The lifecycle phases

### Phase 1 — Marketing and traffic

1. **Set the asking rent** — benchmark against comparable units in the submarket (ILS search + PM
   software market-survey tool). Price to lease within 30–45 days; adjust if no applications in
   14 days.
2. **Build the listing** — unit features, professional photos, floor plan, pet policy, and parking.
   **Send to `pm-compliance-advisor` for fair-housing language review before publishing.**
3. **Choose channels** — ILS platforms (Zillow/Trulia, Rent./Apartments.com, Zumper), Google
   Business Profile, social media, signage. Lease-up properties add paid digital + referral bonus.
4. **Set traffic targets** — inquiries/week and tours/week needed to hit absorption goals. Track
   weekly and adjust channel mix if below target.

### Phase 2 — Application and screening

1. **Written screening criteria** — income multiple (typically 2.5–3× monthly rent), credit score
   floor, rental history (eviction record, prior landlord reference), criminal history policy
   (individualized assessment per HUD 2016 guidance). **Written and approved before the first
   application is accepted.**
2. **Application intake** — use PM software (AppFolio, Buildium, Yardi) to collect application,
   authorization for credit/background pull, and income verification. Never email SSNs or income
   docs — handle within the PM software only.
3. **Screening run** — pull credit and background via integrated service. Document the result
   against each criterion. **Apply identically to every applicant in the same property.**
4. **Decision memo** — approve / conditional / deny with the criterion-by-criterion rationale.
   Retain in the tenant file. Issue adverse action notice per FCRA if denied based on consumer
   report.

### Phase 3 — Move-in

1. **Lease execution** — use the PM software's standard lease with addenda (pet, parking,
   storage, utility responsibility, renters insurance requirement).
2. **Move-in inspection** — walk the unit with the resident, document condition on a signed
   move-in inspection form with photos. This is the baseline for deposit disposition at move-out.
3. **Security deposit collection** — collect per the lease and hold per state statute (separate
   account in some states; confirm jurisdiction). Document receipt.
4. **Utility transfer and key handoff** — confirm utilities are in the resident's name. Provide
   emergency maintenance contact and work-order portal instructions.

### Phase 4 — Tenancy

1. **Work order intake** — resident submits via portal; maintenance-operations-analyst owns
   SLA compliance.
2. **Rent collection** — PM software auto-charges on due date. Late fee assessed per lease after
   grace period.
3. **Lease compliance** — monitor for lease violations (unauthorized occupants, pets, parking);
   issue written notice per jurisdiction requirements.
4. **Mid-lease check-in** — inspection at 6 months (confirm unit condition, catch maintenance issues
   early, build relationship). Document and retain.

### Phase 5 — Renewal

1. **Renewal outreach at 90 days before expiration** — not 30. The lead time is the margin.
2. **Run the renew-vs-turn economics** — use `scripts/pm_calc.py` to compute turn cost (days-vacant
   × daily rent + make-ready cost) vs. renewal concession. A $200/month below-market renewal on a
   $2,000/month unit costs $2,400/year; a turn costs $3,000–$6,000+. The math usually favors
   renewal within a range.
3. **Renewal offer** — flat renewal / CPI increase / market increase with supporting data.
4. **Non-renewal** — if the tenant will not renew, begin pre-turn planning immediately; don't wait
   for move-out notice.

### Phase 6 — Move-out and deposit disposition

1. **Move-out inspection** — walk with the departing resident (or unilaterally if they no-show);
   compare to move-in inspection form; photograph all damage.
2. **Disposition memo** — itemize all charges vs. security deposit. Normal wear and tear is not
   chargeable. All charges must have invoices or estimates.
3. **Return within statutory timeline** — state law typically requires return (or written itemization
   + remainder) within 14–30 days of move-out or key surrender. **Verify jurisdiction's deadline.**
4. **Retain documentation** — move-in form, move-out form, photos, invoices, disposition letter —
   in the tenant file for the statutory retention period.

---

## Anti-patterns

- Listing published without a fair-housing language review.
- Screening criteria documented after an applicant is in the pipeline.
- SSN or income documents handled outside the PM software (email, chat, paper).
- Renewal decision made without running the renew-vs-turn economics.
- Security deposit withheld without itemized documentation and statutory-compliant timeline.

---

## Output

A complete lifecycle artifact for one or more phases: a listing draft with compliance flag, a
screening criteria policy document, a move-in checklist, a renewal offer memo, or a deposit
disposition letter. Structured Output Protocol block per `ravenclaude-core`.
