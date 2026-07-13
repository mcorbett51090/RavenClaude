# Knowledge — Community association decision tree

> **Last reviewed:** 2026-07-13 · **Confidence:** Medium-High (consensus on the finances-vs-governance framing, the reserve-study / percent-funded spine, the fair-and-consistent enforcement ladder, and the general shape of the collections-to-lien sequence; **specific state HOA/COA statutes, reserve-study standards, election rules, CAM-software features, and insurance norms are volatile — re-verify with a state + retrieval date before a board commitment. Reserve adequacy is a professional determination; enforcement/lien/fiduciary-scope mechanics here are operational guidance, NOT legal advice.**).
> The first question in any community-association engagement is "is this a *finances/operations* problem or a *governance/enforcement* problem?" This is the decision tree the `association-management-lead` traverses to scope and route, and the `governance-and-covenant-specialist` traverses to reach its governance sub-branch — **before** prescribing a budget number, an enforcement action, or a collections step.

The team's discipline: **name the branch before the fix; read percent funded before any assessment call; run every enforcement through notice + hearing + consistency; flag state + retrieval date and "not legal advice" on any enforcement/lien/fiduciary-scope step.** Owner/tenant residential leasing leaves this plugin for `property-management`; the investment asset is `commercial-real-estate`; the legal determination is the association's counsel.

---

## Decision Tree: scope & route a community-association engagement

Traverse top-to-bottom. Gate on **finances/operations vs governance/enforcement** first, then the sub-branch.

```mermaid
graph TD
  Start([What is the presenting problem?]) --> KIND{Finances/operations,<br/>or governance/enforcement?}

  KIND -->|Budget / dues / reserves / vendors / insurance| FIN{Which finance/ops sub-branch?}
  KIND -->|Rules / board / elections / delinquency| GOV{Which governance sub-branch?}

  %% ---- Finance / operations branch (lead) ----
  FIN -->|What should dues be?| BUD[Annual budget + assessment<br/>· operating lines + reserve contribution<br/>· set off the reserve study, not "keep dues low"]
  FIN -->|Are reserves adequate?| RES{Reserve funding<br/>full / baseline / threshold?}
  FIN -->|Component failing, reserve short| SPEC[Special assessment vs loan<br/>· lump sum vs financed-through-assessments<br/>· per-owner impact · approval/notice steps]
  FIN -->|Contracts / management company| VEND[Vendor & contract management<br/>· competitive bids · scope · term<br/>· board control, not a rubber stamp]
  FIN -->|Coverage / master policy| INS[Insurance & master policy<br/>· property · liability · D&O · fidelity<br/>· condo unit-boundary question]

  %% ---- Governance / enforcement branch (specialist) ----
  GOV -->|Owner breaking the rules| ENF[Covenant/architectural/rules enforcement<br/>· cite → notice → HEARING → consistent penalty → record<br/>· selective-enforcement guardrail · NOT legal advice]
  GOV -->|Election / quorum problem| ELEC[Elections & quorum<br/>· proxies / adjournment / reduced-quorum<br/>· notice + ballot defects to avoid]
  GOV -->|Board decision / conflict / records| FID[Fiduciary duty & open meetings<br/>· care/loyalty · business-judgment PROCESS<br/>· conflict check · notice/quorum/minutes/records]
  GOV -->|Owner not paying assessments| COLL[Delinquency → collections/lien ladder<br/>· prevention first · STATE-SPECIFIC sequence<br/>· late fee→demand→plan→pre-lien→lien→foreclosure · NOT legal advice]

  RES -->|Fully funds the liability| FULL[Full funding<br/>· target ~100% funded over time]
  RES -->|Level contributions to a floor| BASE[Baseline funding<br/>· keep balance above zero — higher special-assessment risk]
  RES -->|Contribute to a % threshold| THRESH[Threshold funding<br/>· fund to a chosen % floor — middle path]

  %% ---- Seams (out of plugin) ----
  BUD --> SEAM
  RES --> SEAM
  SPEC --> SEAM
  VEND --> SEAM
  INS --> SEAM
  ENF --> SEAM
  ELEC --> SEAM
  FID --> SEAM
  COLL --> SEAM
  FULL --> SEAM
  BASE --> SEAM
  THRESH --> SEAM

  SEAM{Does it leave this plugin?} -->|Legal determination on enforcement/lien/fiduciary| LAW[Association's counsel — not legal advice]
  SEAM -->|Reserve study CERTIFICATION / component condition| RSVP[Reserve specialist / engineer]
  SEAM -->|Owner/tenant residential leasing| PM[property-management]
  SEAM -->|Asset-level investment / acquisition| CRE[commercial-real-estate]
  SEAM -->|Newsletter / member-comms creative| MKT[marketing-operations]
  SEAM -->|Books / audit / tax return| ACC[accounting-bookkeeping]
```

---

## Reserves: the two numbers you must not conflate

| Metric | Definition | What it tells you |
|---|---|---|
| **Reserve balance** | Cash currently in the reserve account | How much is *there* — flatters, because it ignores the liability behind it |
| **Percent funded** | Reserve balance ÷ **fully-funded balance** (the accrued share of every component's replacement cost) | The *honest* number — how prepared the association actually is for the components coming due |

An association can hold a healthy-looking reserve *balance* and still be **35% funded** — meaning it has accrued only a third of what its aging roofs, roads, and elevators will cost. That gap is a **special assessment** waiting to happen. Read **percent funded** and the **funding plan**, not the bank line, before any assessment call. **Adequacy *certification* is a reserve specialist's/engineer's determination — this team frames it, it does not certify it.**

---

## The reserve-funding sub-choice (after "are reserves adequate?")

| Funding plan | What it does | Watch out for |
|---|---|---|
| **Full funding** | Targets ~100% funded — contributions accrue each component's share as it ages | Highest dues; the lowest special-assessment risk |
| **Baseline (cash-flow) funding** | Keeps the reserve balance above zero across the projection — never runs dry, but stays under-funded | Lowest dues; the **highest special-assessment risk** when several components cluster |
| **Threshold funding** | Funds to a chosen percent-funded floor (a middle path between baseline and full) | The threshold is a policy choice — document why the board picked it |

The reserve study models these; the board picks the funding plan as a policy decision. Don't default to baseline because it keeps dues lowest — that is exactly the choice that produces the surprise special assessment.

---

## Seams (this plugin runs the ASSOCIATION — not residential leasing, the investment asset, or the legal determination)

- **The legal determination** on an enforcement action, a fine, a lien, a foreclosure, an election dispute, or the scope of fiduciary duty → the association's **counsel** (operational guidance, not legal advice).
- **The reserve-study *certification* / component condition assessment** → a **reserve specialist / engineer** (this team frames adequacy and reads the study).
- **Owner/tenant residential leasing** (apartments, single-family rentals) → `property-management`.
- **Asset-level real-estate investment / acquisition / cap-rate** → `commercial-real-estate`.
- **Newsletter / member-communications creative, brand** → `marketing-operations` (this team decides *what must be noticed*).
- **The books, the audit/review, the tax return** → `accounting-bookkeeping`.

---

## Provenance

- Durable framing (finances-vs-governance, the reserve-study / percent-funded spine, full/baseline/threshold funding plans, the fair-and-consistent enforcement ladder of cite→notice→hearing→consistent penalty→record, board fiduciary duty and the business-judgment rule, the general delinquency-to-lien sequence) is consensus community-association operating practice, reviewed 2026-07-13 — **Medium-High confidence**.
- **State HOA/COA statutes (e.g. Davis-Stirling in CA, and every state's own act), reserve-study standards, election and open-meeting rules, CAM-software feature sets (AppFolio, Vantaca, TOPS/CINC), and insurance/master-policy norms are volatile** — treat any specific claim as a 2026-07 snapshot, attach a state and/or retrieval date, and re-verify with `ravenclaude-core/deep-researcher` before a board commitment. Reserve adequacy is a professional determination; enforcement/lien/fiduciary-scope mechanics are **operational guidance, not legal advice** — route the legal determination to counsel.
