# Tax Coordination Calendar — <ENTITY> — <YEAR>

> **Fill-in template.** This is a controller **coordination tickler**, not tax advice and not a determination of any obligation, due date, rate, nexus, or election. **Confirm every date with the relevant agency (IRS / state / local) and route every determination to a licensed CPA / tax advisor.** Companion checklist: [`../knowledge/tax-close-calendar.md`](../knowledge/tax-close-calendar.md).
>
> Prepared by: `<name>`  |  Reviewed by: `<name>`  |  Date prepared: `<YYYY-MM-DD>`  |  Tax advisor of record: `<firm / contact>`

## Entity facts (confirm annually)

| Field | Value |
|---|---|
| Legal entity / type (C-corp / S-corp / partnership / LLC / …) | `<...>` |
| Fiscal year-end | `<MM-DD>` |
| Federal EIN | `<on file — do not paste here>` |
| States with an established filing footprint (income / franchise) | `<...>` |
| States/localities with sales & use tax registration | `<...>` |
| Payroll provider (handles deposits / W-2) | `<...>` |
| Nexus-trigger watch items this year (new state, remote hires, threshold crossings) | `<...>` |

## Recurring filings — cadence & owner (confirm each due date)

| Obligation | Cadence | Jurisdiction(s) | Data owner (controller side) | Filer / preparer | Confirm due date with |
|---|---|---|---|---|---|
| Sales & use tax | `<monthly/qtrly/annual>` | `<...>` | `<...>` | `<...>` | State/local DOR |
| Payroll tax deposits | `<per IRS schedule>` | Federal + `<states>` | `<...>` | Payroll provider | Provider / IRS |
| Income tax — estimated payments (Q1–Q4) | Quarterly | Federal + `<states>` | `<...>` | Tax advisor | Tax advisor |
| Income tax provision (ASC 740) inputs | Quarterly + annual | `<...>` | `<...>` | Tax advisor | Tax advisor |
| Franchise / margin / gross-receipts tax | `<annual/qtrly>` | `<states>` | `<...>` | Tax advisor | State DOR |
| Business personal property tax | Annual | `<counties>` | `<fixed-asset owner>` | Tax advisor | County assessor |
| 1099-NEC / 1099-MISC | Annual | Federal + `<states>` | `<AP owner>` | `<...>` | IRS (current-year date) |
| W-2 / W-3 | Annual | Federal + `<states>` | `<payroll owner>` | Payroll provider | SSA / IRS |

## Quarter grid (enter the CONFIRMED dates — the ones below are placeholders)

| Item | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Fed est. income tax payment | `<date>` | `<date>` | `<date>` | `<date>` |
| State est. income tax payment | `<date>` | `<date>` | `<date>` | `<date>` |
| Sales-tax return(s) | `<date>` | `<date>` | `<date>` | `<date>` |
| ASC 740 interim provision handoff | `<date>` | `<date>` | `<date>` | `<date>` |

## Year-end information-return runway (1099 / W-2) — confirm current-year dates

| Step | Target | Owner | Status |
|---|---|---|---|
| Vendor W-9 / TIN validation swept (year-round) | ongoing → `<Dec>` | `<...>` | ☐ |
| Reportable-payment classification reviewed | `<Dec / early Jan>` | `<...>` | ☐ |
| 1099 batch reconciled to AP subledger | before transmit | `<...>` | ☐ |
| 1099-NEC recipient + IRS copies filed | `<~Jan 31 — CONFIRM>` | `<...>` | ☐ |
| Other 1099 copies filed | `<CONFIRM>` | `<...>` | ☐ |
| W-2 batch reconciled to payroll GL / 941s | before transmit | `<...>` | ☐ |
| W-2 / W-3 filed | `<~Jan 31 — CONFIRM>` | `<...>` | ☐ |
| E-file threshold checked (aggregate return count) | `<Dec>` | `<...>` | ☐ |

## Book-vs-tax difference candidates handed to the provision (from the close schedules)

| Difference | Book source | Perm / Temp | Notes | Determined by advisor? |
|---|---|---|---|---|
| Depreciation (book SL vs. tax MACRS/§179/bonus) | close-schedules `depreciation` | Temp | book side only from the engine | ☐ |
| Deferred revenue (ASC 606 vs. tax timing) | close-schedules `deferred-revenue` | Temp | `<...>` | ☐ |
| Prepaids / accruals / allowances | close-schedules `prepaid` + recon | Temp | `<...>` | ☐ |
| Non-deductible items (M&E, fines, certain stock comp) | GL | Perm | `<...>` | ☐ |
| R&D capitalization (§174) | GL / model | Temp | `<...>` | ☐ |

## Coordination log (audit trail)

| Date | Data pulled | Period | Sent to | Confirmation # | By |
|---|---|---|---|---|---|
| `<YYYY-MM-DD>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

---

**Reminder:** every date above is a placeholder until confirmed with the agency, and every taxability / nexus / classification / election call is the tax advisor's determination, not the controller's. This calendar coordinates the handoff; it does not decide the tax answer.
