# P&C insurance KPI glossary

The metrics a P&C book is judged on — formulas, the misreads, and where a benchmark needs a date. Read the relevant section in full when a metric is in question. Every external benchmark below carries a source + retrieval date or an `[unverified]` / `[verify-at-use]` mark (§3 #8); validate against the book's own data before any deliverable (CLAUDE.md §2).

## Result metrics

| Metric | Formula | The misread to avoid |
|---|---|---|
| **Combined ratio (CR)** | loss ratio + expense ratio | Reading it as one thing — it blends loss vs expense, attritional vs cat, and (calendar-year) prior-year development. Under 100 = underwriting profit (§3 #1). |
| **Underwriting margin** | 100 − combined ratio | A thin margin in a cat-light year can flip negative the next year — read it with the cat load. |
| **Loss ratio** | (incurred losses + LAE) / earned premium | LAE is *inside* the loss cost — don't double-count it in expense. Split attritional vs cat (§3 #4). |
| **Expense ratio** | underwriting expenses / premium | Two levers: acquisition (commission/marketing) and internal (overhead) — they have different fixes. |
| **Net combined ratio (NCR) by line** | per-line CR, net of reinsurance | The blended CR hides a mix shift toward the worst line — read by line, watch where premium is *growing* (§3 #6). |

**Industry scale (2025 full-year, US P&C — date-volatile, `[verify-at-use]`):** the industry posted its strongest underwriting result in over a decade, with a full-year combined ratio around **92.9** (from ~96.6 in 2024) and an estimated **~$63B** net underwriting gain; policyholders' surplus ~$1.2T. Source: [Reinsurance News — Triple-I/Milliman](https://www.reinsurancene.ws/us-pc-industry-set-for-lowest-net-combined-ratio-in-over-a-decade-triple-i-milliman/) and [Insurance Business — decade-low CR](https://www.insurancebusinessmag.com/us/news/property/property-casualty-combined-ratio-hits-decade-low-as-2025-closes-strong-575604.aspx) (retrieved 2026-06-05). *Note: mid-year Triple-I/Milliman forecasts were higher (personal auto ~96.0, homeowners ~99.6); full-year actuals came in better — cite the specific basis and date.*

| Line (2025, US, `[verify-at-use]`) | Net combined ratio |
|---|---|
| Homeowners | ~88.1 (lowest in over a decade) |
| Personal auto | ~91.8 |
| Workers' compensation | ~91 |
| General liability ("other liability") | above 100 (pressured) |
| Commercial auto | above 100 (pressured) |

Source: [III / Triple-I press release](https://www.iii.org/press-release/triple-i-milliman-2025-us-p-c-insurance-outlook-shows-strength-in-personal-auto-ongoing-pressure-in-general-liability-lines-071025) and [Carrier Management](https://www.carriermanagement.com/news/2026/01/06/283094.htm) (retrieved 2026-06-05). General liability and commercial auto were the only major lines forecast above a 100 NCR — the mix, not the average, tells the story (§3 #6).

## Loss metrics

| Metric | What it is | Why it matters |
|---|---|---|
| **Frequency** | claims per exposure unit | A frequency move is a risk-selection / exposure / mix story (§3 #3). |
| **Severity** | average cost per claim | A severity move is a large-loss / social-inflation story — opposite fix to frequency (§3 #3). |
| **Pure premium** | frequency × severity | The loss cost per exposure; drives the loss ratio at a flat rate. |
| **Attritional vs catastrophe loss ratio** | the non-cat vs cat split | Strip cat to judge the attritional book (§3 #4). Cat ran roughly **7–8 points** of the 2025 combined ratio `[verify-at-use]`. |
| **Loss development** | how an accident year's losses mature toward ultimate | Chain-ladder / Bornhuetter-Ferguson project to ultimate — see [`pc-reserving-method-decision-tree.md`](pc-reserving-method-decision-tree.md). |
| **Reserve adequacy** | are case + IBNR sufficient? | The truth-teller — today's CR is only as honest as the reserves (§3 #5). Read prior-year development separately. |

## Pricing & claims metrics

| Metric | Formula / definition | Note |
|---|---|---|
| **Permissible loss ratio (PLR)** | 1 − (expense ratio + profit & contingency load) | The highest the future loss ratio can be and still hit target profit. |
| **Indicated rate change** | (trended loss ratio / PLR) − 1 | Loss-ratio method; the standard overall rate-adequacy test (CAS Basic Ratemaking). Credibility-weight against the trended PLR when data is thin. |
| **Rate adequacy** | is the filed rate ≥ the indicated rate? | Price to the indication, not the competitor (§3 #2). |
| **LAE (loss adjustment expense)** | cost of recording, investigating, settling claims | Splits into **DCC** (defense & cost containment — legal/litigation) and **AO** (adjusting & other — handling/investigation/settlement) `[verify-at-use]`. |
| **Indemnity leakage** | paid − (what file review says was owed) | The controllable gap — never reduce by under-paying valid claims (§3 #7). |
| **Claims cycle time** | report date → close date (+ open-claim aging) | Long-open claims accrue DCC and drift reserves; open-claim count is a leading severity warning. |
| **Subrogation / salvage recovery** | recovered / recoverable | A claims-unit revenue line, not an afterthought. |

Rate-indication / PLR formulas: [CAS Basic Ratemaking (Werner & Modlin)](https://www.casact.org/sites/default/files/2021-07/Werner_Modlin_Basic_Ratemaking.pdf) and the [loss-ratio method overview](https://metricgate.com/docs/loss-ratio-method/) (retrieved 2026-06-05). LAE / DCC / AO definitions: [Founder Shield](https://foundershield.com/insurance-terms/definition/loss-adjustment-expense/) and [Huggins Actuarial](https://hugginsactuarial.com/reserving-considerations-for-adjusting-and-other-expenses/) (retrieved 2026-06-05).

## Distribution & retention metrics

| Metric | What it is | Benchmark (`[verify-at-use]`) |
|---|---|---|
| **Retention / persistency** | % of policies/premium renewing | Standard P&C agency average ~**88%**; bundled auto+home ~**91%** vs ~**67%** monoline. |
| **New-business vs renewal loss ratio** | the new-business penalty | New business retains worse and runs a worse loss ratio than seasoned renewals — leaning on it while a retention leak runs open grows a loss. |
| **Shopping drivers** | why policyholders leave | Only ~**13%** shop on a rate increase; ~**28%** start shopping over poor service. |

Source: [Agency Performance Partners — insurance policy retention](https://www.agencyperformancepartners.com/blog/insurance-policy-retention/), [WaterStreet — renewal retention analytics](https://www.waterstreetcompany.com/renewal-retention-analytics/), [Bain & Company — P&C retention](https://www.bain.com/insights/how-to-improve-customer-retention-in-property-and-casualty-insurance-snap-chart/) (retrieved 2026-06-05). These are agency-survey benchmarks, not hard rules — validate against the book's own persistency and loss-ratio-by-tenure.

## Regulatory context (US)

P&C rates and forms are regulated at the **state** level; the **NAIC** (National Association of Insurance Commissioners) coordinates model laws and aggregates industry data, but each state insurance department approves rate/form filings (prior-approval, file-and-use, or use-and-file regimes vary by state and line) `[verify-at-use]`. Rate filings must generally not be inadequate, excessive, or unfairly discriminatory. Source: [NAIC mid-year 2025 P&C industry analysis](https://content.naic.org/sites/default/files/2025-mid-year-property-casualty-and-title-insurance-industries-analysis-report.pdf) (retrieved 2026-06-05). Verify the specific state's filing regime and standards at use — they vary materially by state and line.

## Sourcing note

Figures in this file carry a source URL + retrieval date inline, or an `[unverified — training knowledge]` / `[verify-at-use]` / `[ESTIMATE]` mark. Market figures (combined ratios, cat loads, by-line NCR, retention benchmarks) move yearly and by basis (forecast vs actual; calendar vs accident year) — re-verify against a primary source and state the basis before putting any figure in a client deliverable (§3 cite-or-mark rule).
