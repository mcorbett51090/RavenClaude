# Contract Collection Playbook — P0a

**Target:** n ≥ 15–20 contracts per product, 45–60 total across 2–3 candidate SaaS products, **stratified
by contract-size band** and deliberately including **sub-threshold** contracts (plan.md P0a step 1–2,
CE1). This is the raw material for both the dispersion analysis (step 4) and the seedability measurement
(step 3 / acceptance test (b)).

**Before collecting anything:** the 2–3 products, the sampling frame (including size bands and
sub-threshold inclusion), the model, thresholds and exclusion rules must already be locked in the
`p0_preregistration` decision record (plan.md P0a step 1). Do not start pulling contracts before that
record is signed — collecting first and defining the frame after is exactly the kind of post-hoc
flexibility the pre-registration exists to prevent.

---

## 1. Source types, fastest to slowest

Use all four in parallel where possible; don't wait for the slowest to start the fastest.

### 1a. Check registers (fastest — gives actual totals) — CE1

- Most districts post monthly check/warrant registers (often a PDF or searchable table on the district's
  finance/business-office page, or via a state transparency portal).
- Search the register for the vendor name and pull actual payment amounts across the fiscal year — this
  gives you a *real* total, not a contract ceiling.
- Cross-reference the total against the number of licenses/seats (from the district's website, a board
  agenda item, or a district staff count if you have to estimate) to back into a rough per-seat price.
- **Caveat:** check registers rarely state contract terms (multi-year? escalator?) — you'll usually need
  to pair this with a board packet or the order form itself for those fields.
- **This is your primary source for the seedability measurement** — it's the fastest way to get a real
  number, so lean on it first for both above- and below-threshold contracts.

### 1b. Board packets / board meeting minutes (fast, but often ceiling-only) — C43

- Board agendas and packets are typically posted publicly (BoardDocs, Diligent, or a plain PDF on the
  district site) and are searchable by vendor name or agenda-item keyword ("software," "subscription,"
  "renewal").
- **Known limitation:** many board approvals show a **not-to-exceed** ceiling, not the actual negotiated
  price — record this explicitly as a `ceiling` field, don't treat it as `actual_total`. If you can find
  the corroborating check-register entry, prefer that number for analysis and keep the board figure as a
  secondary/ceiling data point.
- Board packets are your best source for term length and sometimes escalator clauses, since multi-year
  agreements are usually described in the resolution language.

### 1c. Formal public-records requests (slowest — for order forms/contracts not found above) — K8

Use this only for contracts you can't get from 1a/1b, since it's the slowest path.

- **Timeline to plan around:** 10 business days of required notice to the vendor (if the request implicates
  vendor pricing information that might be confidential/proprietary), then, if the vendor formally
  objects, 45 days plus another 10 days for an Attorney General ruling if the district's records custodian
  refers the dispute for an opinion. Budget for the full ~65-business-day worst case if a request is
  contested; plan requests early enough that this doesn't block your P0a timeline.
- **Draft your request narrowly** (see the template letter below) — ask for the specific order
  form/contract/pricing schedule for a named vendor and date range, not "all technology purchases," to
  reduce both processing time and the odds the request gets flagged as overbroad.
- **Track every request from day 1** in the tracking spreadsheet (§3) — date requested, date acknowledged,
  date received or denied, and whether it was contested — this data feeds directly into the seedability
  metric (contested-request rate) required by plan.md step 3.
- **If a vendor asserts confidentiality and the district notifies you it's withholding records or seeking
  an AG ruling**, log it as `contested = true` and move on to another sample contract rather than waiting
  — you can circle back if the ruling comes through inside your P0a window.

### 1d. Pilot-org direct sharing under NDA (for private orgs, or as a supplement) — plan.md step 2

- For private schools/orgs identified as candidate pilots in the buyer interviews, ask directly whether
  they'll share their own contract (quantity, price, term, escalator) under an NDA, for internal analysis
  only — never for republication or display without further clearance.
- **This requires counsel scoping to confirm first** (plan.md: "if counsel scoping confirms") — don't
  make this ask until N1/counsel has cleared the terms of the NDA and confirmed there's no exposure in
  how the shared data will be used, even internally.
- A GovSpend trial subscription is acceptable **for internal validation only** (cross-checking your
  public-records numbers), never as a substitute for the actual public-records-sourced sample, and never
  redistributed.

## 2. Stratification — don't just grab the easiest 15–20

For each product, before you start pulling, define size bands in the pre-registration record (e.g.,
small/mid/large by annual spend or seat count) and **deliberately include sub-threshold contracts** —
those below your state's formal-bid/public-notice threshold, which are often invisible in board packets
because they don't require board approval at all. Sub-threshold contracts are exactly where check
registers matter most, since they may be the *only* public trace.

Track your running count per band per product so you notice a stratification gap early rather than at
the end of the collection window.

## 3. Tracking spreadsheet — column layout

One row per contract. Suggested columns (a shared spreadsheet or lightweight database works fine — the
important thing is consistency across all 45–60 rows so the dispersion analysis in step 4 doesn't have to
reconcile inconsistent formats):

| Column | Notes |
|---|---|
| `product` | One of the 2–3 pre-registered candidate products |
| `org_name` | District/school/org name |
| `org_type` | public / private |
| `state` | For launch-state re-ranking (step 9) |
| `size_band` | As defined in pre-registration (e.g., small/mid/large; flag `sub_threshold = true/false`) |
| `source_type` | `check_register` / `board_packet` / `records_request` / `pilot_nda` / `govspend_trial` |
| `date_requested` | Blank if not applicable (check register/board packet found directly) |
| `date_received` | Date the actual data was in hand |
| `contested` | true/false — did the vendor or district resist/delay the request |
| `days_to_obtain` | `date_received` − `date_requested` (or date search started, for direct sources) |
| `quantity_obtained` | Y/N — seats/licenses/units |
| `metric_obtained` | Y/N — the unit the price is measured against (per-seat, per-district, etc.) |
| `term_obtained` | Y/N — contract length |
| `escalator_obtained` | Y/N — annual increase clause, if any |
| `total_value` | The actual total, if known |
| `total_is_ceiling` | true/false — flag board-packet not-to-exceed figures explicitly |
| `acquisition_channel` | direct / reseller / co-op — feeds the null-model regression (step 4) |
| `fiscal_year_end_proximity` | For the timing sensitivity analysis (C48) — days between signing and FY end |
| `notes` | Anything ambiguous — flag for the dual-normalization noise-floor exercise (step 4) |

**Seedability tracking:** the four `_obtained` columns plus `days_to_obtain` and `contested` are exactly
what feeds the acceptance-test (b) metric — "at least 40% of above-threshold contracts yield quantity,
metric and term from public records within 60 days," with the sub-threshold rate reported separately.
Keep these columns clean from day one; don't reconstruct them retroactively.

---

## 4. Template public-records-request letter (generic — adapt per state)

Replace bracketed fields. Check your launch state's specific public-records statute name/number and any
required form before sending — some states require a specific submission channel (online portal, named
records officer) rather than a generic letter.

```
[Your name / organization]
[Address]
[Email / phone]
[Date]

[District/Agency Name]
Attn: Public Information / Records Custodian
[Address]

Re: Public Information Request under [State Public Records Act citation — confirm with counsel or the
    agency's own posted public-records procedure]

Dear Records Custodian,

Under [state]'s public records law, I am requesting copies of the following records:

1. The executed contract, purchase order, and/or order form between [District/Agency Name] and
   [Vendor Name] for [Product/Service Name], covering the period [start date] through [end date or
   "present"], including any pricing schedule, quantity/unit count, and term-length information.
2. Any amendments, renewals, or addenda to the above contract that affect price, quantity, or term.

If any portion of this request implicates pricing or other information the vendor may claim as
confidential or proprietary, I understand you may be required to notify the vendor and allow an
opportunity to object before releasing the records, per [state's] notice procedure. I am willing to
receive responsive, non-exempt records on a rolling basis rather than waiting for the complete set.

If any part of this request is denied, please cite the specific statutory exemption relied upon, and
advise me of my right to appeal or seek an opinion, per [state]'s procedure.

I am willing to pay reasonable copying/production fees up to $[cap, e.g., 25]. Please contact me before
incurring fees above that amount.

If you need clarification of this request, please contact me at [email/phone]. Thank you for your
time.

Sincerely,
[Name]
```

**Notes on adapting this letter:**
- Confirm the exact statute name/number for the launch state with counsel (N1) before sending at volume —
  don't guess a citation into a real request letter.
- Some states require the request to go through a specific web portal (e.g., NextRequest, GovQA) rather
  than email/letter — check the agency's site first.
- If a vendor notice-and-objection period applies, expect the slower K8 timeline described in §1c above.
- Keep a copy of every letter sent and every response received in the run-directory evidence folder
  (`.ravenclaude/runs/<task-id>/`), not just logged in the spreadsheet, so a contested request has a full
  paper trail if it needs to go to appeal.
