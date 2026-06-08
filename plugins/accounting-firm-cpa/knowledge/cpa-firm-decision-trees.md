# CPA Firm — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `accounting-firm-cpa`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
> Volatile product/pricing/regulatory facts carry a retrieval date and a `[verify-at-use]` rider.

---

## Decision Tree 1: Engagement type and independence check

```mermaid
flowchart TD
  A[What engagement is being proposed for this client?] --> B{Is it an attest engagement?}
  B -->|No - tax or advisory only| Z1[No independence requirement under AICPA ET §1.200.\nDocument scope in engagement letter; proceed.]
  B -->|Yes - audit / review / compilation / AUP| C{Does the firm perform any non-attest service\nfor this client?}
  C -->|No other services| D[Independence intact. Document and proceed.\nSign engagement letter.]
  C -->|Yes - tax prep only| E{Does tax prep require judgment that\ncould be audited in the financial statements?}
  E -->|No - clerical / ministerial| F[Low threat. Apply standard safeguards:\nclient makes all significant decisions;\nfirm does not make management decisions.]
  E -->|Yes - involves estimates or positions| G[Self-review threat. Assess magnitude.\nSafeguard: management reviews and approves\nevery tax position independently.]
  C -->|Yes - CAS / bookkeeping| H{Does CAS include preparing financial\nstatements the firm will audit?}
  H -->|No - data entry / coding only| F
  H -->|Yes - firm prepares statements| I[Self-review threat - HIGH.\nSafeguard options: separate engagement teams\n+ client review of every entry.\nIf safeguards insufficient: restructure or decline attest.]
  C -->|Yes - firm performs management function| J[Independence IMPAIRED.\nManagement participation threat - no safeguard available.\nDecline attest engagement or terminate management-function service.]
  C -->|Yes - advisory / CFO advisory| K{Does advisory include making decisions\nor signing authority over client assets?}
  K -->|No - analysis and recommendations only| F
  K -->|Yes - management participation| J
```

**Leaf rule:** a management-participation threat (the firm makes business decisions, signs checks,
controls assets, supervises client employees) has NO available safeguard — decline the attest
engagement or restructure the non-attest service before issuing any attest report. For
self-review threats, safeguards must ensure the client independently understands and approves
every entry/position; if management lacks the competence to review meaningfully, the safeguard
fails.

---

## Decision Tree 2: Fixed-fee vs. hourly pricing

```mermaid
flowchart TD
  A[Is the scope of this engagement well-defined?] -->|No - open-ended, evolving| B[Time-and-materials.\nSet a not-to-exceed estimate;\ndefine scope-change notification trigger.]
  A -->|Yes - defined deliverables| C{Is the work highly repeatable for this client\ne.g. same return type, same CAS scope annually?}
  C -->|No - first year or complex / variable| D{Is the complexity well-understood\nbased on prior-year data or scoping?}
  D -->|No - unknown complexity| E[Time-and-materials first year.\nCapture actuals. Price fixed-fee from year 2\nusing realization data.]
  D -->|Yes - complexity understood| F[Fixed-fee with defined scope and overage triggers.\nDocument included services explicitly.]
  C -->|Yes - repeatable, known scope| G{Does the client's transaction volume\nor complexity change materially year-to-year?}
  G -->|Yes - high variability| H[Fixed-fee base + overage triggers\ne.g. transactions above threshold, additional entities.\nReview annually.]
  G -->|No - stable| I[Fixed-fee annual retainer.\nAnnual scope review to catch scope creep.]
  F --> J[Set floor: standard hours × rate ÷ target realization.\nDo not set fixed-fee below floor.]
  H --> J
  I --> J
```

**Leaf rule:** fixed-fee engagements must be grounded in a hours-estimate × standard-rate ÷
target-realization floor. A fixed fee set without this floor is a guess that becomes a write-down.
Overage triggers protect margin on variable-complexity clients. Capture actuals in the first year
if the scope is genuinely unknown — do not guess a flat fee and absorb the difference.

---

## Decision Tree 3: Tax return review-tier routing

```mermaid
flowchart TD
  A[Determine return type and complexity] --> B{Entity type}
  B -->|Individual 1040| C{Complexity indicators?}
  C -->|W-2 only, standard deduction, no investments| D[Tier 1 - Simple.\nPreparer: staff. Reviewer: senior.\nNo second review needed.]
  C -->|Schedule A + moderate investments or rental| E[Tier 2 - Standard.\nPreparer: staff or senior.\nReviewer: senior or manager.]
  C -->|K-1 passthroughs, schedule E multi-prop,\nbusiness income Schedule C, complex investments,\nAMT exposure, foreign income| F[Tier 3 - Complex.\nPreparer: senior.\nReviewer: manager + partner sign-off.]
  B -->|Partnership 1065 or S-Corp 1120-S| G{Size and complexity?}
  G -->|<10 partners, simple operations, no K-2/K-3| E
  G -->|Multi-member, complex allocations, K-2/K-3,\nforeign partners or income| F
  B -->|C-Corp 1120| H{Size and complexity?}
  H -->|Small closely-held, simple ops| E
  H -->|Multi-state, significant deferred tax,\nR&D credits, M&A activity| F
  B -->|Trust / Estate 1041| F
  B -->|Nonprofit 990| I{Program complexity?}
  I -->|Simple - single program, no 990-T| E
  I -->|Multi-program, unrelated business income,\nscheduled footnote disclosures| F
```

**Leaf rule:** complexity tier is assigned at intake, not after preparation. Discovering K-2/K-3
requirements or complex Schedule E items at first-review stage means the return was mis-tiered
and the review queue was mis-planned. The cost is a staff-level preparer doing work that needs
senior judgment. Sort at intake; route correctly; protect the senior/manager review constraint.

---

## 2026 Capability Map: Tax, Workflow, and CAS Software

> All product names, pricing tiers, and feature descriptions are based on publicly available
> information as of 2026-06-08 `[verify-at-use]`. The CPA software market evolves; confirm
> current pricing, feature sets, and integration availability before recommending to a client.

### Tax software

| Product | Vendor | Typical firm size | Notes |
|---|---|---|---|
| UltraTax CS | Thomson Reuters | Small to large | Deep integration with CS suite (Workpapers CS, Practice CS); strong individual and business return support; annual subscription `[verify-at-use]` |
| Lacerte | Intuit | Small to mid-size | Widely used for individual returns; strong 1040 workflow; Intuit Link for client document collection `[verify-at-use]` |
| CCH Axcess Tax | Wolters Kluwer | Mid-size to large | Cloud-native; integrates with CCH Axcess Workflow and Document; strong for larger practices with complex business returns `[verify-at-use]` |
| Drake Tax | Drake Software | Small firms, value-focused | Lower price point; full-featured; widely used by solo and small-firm practitioners `[verify-at-use]` |
| ProSeries | Intuit | Small firms | Desktop-based; accessible for smaller practices; integrates with QuickBooks `[verify-at-use]` |

### Workflow management

| Product | Vendor | Notes |
|---|---|---|
| Karbon | Karbon | Cloud-based practice management; work items, client tasks, email integration; widely used in CAS and tax firms `[verify-at-use]` |
| Canopy | Canopy | Combines practice management, document management, client portal, and billing; growing adoption in small to mid-size firms `[verify-at-use]` |
| CCH Axcess Workflow | Wolters Kluwer | Native integration with CCH Axcess Tax; best for firms already in the CCH ecosystem `[verify-at-use]` |
| Thomson Reuters Practice CS | Thomson Reuters | Native integration with UltraTax and CS suite `[verify-at-use]` |

### CAS tech stack

| Function | Products | Notes |
|---|---|---|
| General ledger (small business) | QuickBooks Online (QBO), Xero | QBO dominant for SMB; Xero strong in service industries and internationally `[verify-at-use]` |
| General ledger (mid-market) | Sage Intacct | Multi-entity, fund accounting, dimensional reporting; standard for complex SMB and non-profits `[verify-at-use]` |
| AP automation | Bill.com (BILL), AvidXchange | Bill.com dominant in SMB; AvidXchange for higher volume / multi-location `[verify-at-use]` |
| Expense management | Ramp, Expensify, Brex | Ramp growing rapidly; Expensify entrenched for reimbursement-heavy; Brex for VC-backed companies `[verify-at-use]` |
| Payroll | Gusto, ADP Run, Paychex Flex | Gusto preferred for SMB CAS clients; ADP/Paychex for larger or more complex payroll needs `[verify-at-use]` |
| Reporting / FP&A | Fathom, LivePlan, Jirav | For controller-tier CAS clients needing management reporting above QBO standard reports `[verify-at-use]` |
| Client portal / document exchange | Canopy, SmartVault, ShareFile | Depends on firm's practice management ecosystem `[verify-at-use]` |

---

_Last reviewed: 2026-06-08 by `claude`._
