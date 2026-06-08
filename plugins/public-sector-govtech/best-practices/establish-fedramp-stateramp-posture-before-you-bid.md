# Establish FedRAMP / StateRAMP posture before you bid

**Status:** Pattern
**Domain:** Cloud security / public procurement
**Applies to:** `public-sector-govtech`

---

## Why this exists

Government cloud procurements routinely require FedRAMP (federal) or StateRAMP (state/local)
authorization as a mandatory requirement. An organization that bids on a cloud-based government
contract without an existing authorization — or without a credible timeline to obtain one — is
bidding on work it cannot deliver. FedRAMP Moderate authorization takes 6–18 months on average;
a High authorization longer. Discovering this constraint after contract award is a program-breaking
finding, not a manageable risk.

Conversely, organizations with an existing FedRAMP or StateRAMP authorization have a significant
competitive advantage in government cloud procurements: they can respond to a mandatory security
requirement immediately rather than promising a timeline, and agency buyers prefer the certainty of
an already-authorized platform.

## How to apply

1. **Determine the required impact level** (FIPS 199 categorization: Low / Moderate / High) for the
   data and systems in scope. Most commercial cloud services land at FedRAMP Moderate.
2. **Check the FedRAMP Marketplace** (marketplace.fedramp.gov) and StateRAMP Authorized Product List
   (stateramp.org) — if you can build on an already-authorized IaaS/PaaS (AWS GovCloud, Azure
   Government, Google Cloud GovCloud), inherit controls from that platform and scope your own
   authorization to the delta.
3. **Decide: pursue your own authorization or use an authorized platform?** Building on an already-
   authorized cloud reduces the control count you must independently test — typically 40–60% of
   controls can be inherited from a properly documented CSP platform.
4. **Start the authorization process before the procurement, not during it.** If the target RFP
   requires FedRAMP Moderate and you are not yet authorized, begin the 3PAO engagement and SSP
   preparation now.
5. **Traverse the FedRAMP/StateRAMP-needed tree** in
   [`../knowledge/govtech-decision-trees.md`](../knowledge/govtech-decision-trees.md) before
   advising on posture.

**Do:**

- Check marketplace.fedramp.gov and stateramp.org before estimating authorization timelines.
- Build on an already-authorized cloud layer and inherit controls where possible.
- Start 3PAO engagement 12–18 months before the expected award date on a major federal cloud contract.
- Include FedRAMP authorization status in the bid-no-bid analysis.

**Don't:**

- Bid on a FedRAMP-required contract with only a "we plan to pursue authorization" statement and
  no 3PAO engaged.
- Assume FedRAMP Low authorization satisfies Moderate requirements — they are distinct
  authorization paths with different control sets.
- Confuse FedRAMP "In Process" (a voluntary designation from the PMO) with "Authorized" — agencies
  may or may not accept In-Process designations.

## Edge cases / when the rule does NOT apply

- **On-premises deployments:** if the product is deployed entirely within the agency's own data
  center with no CSP involvement, FedRAMP does not apply. The agency's own ATO process applies.
- **DoD IL4/IL5 requirements:** DoD uses its own cloud authorization framework (DISA Cloud
  Authorization) on top of FedRAMP. A FedRAMP Moderate authorization is necessary but not
  sufficient for DoD IL4/IL5 work.
- **Pilot / proof-of-concept contracts:** some agencies allow short-term pilots on non-authorized
  platforms under a formal ATO exception with limited data and time-bounded authority. Confirm
  with the agency's ISSM.

## See also

- [`./meet-every-mandatory-rfp-requirement-or-be-disqualified.md`](./meet-every-mandatory-rfp-requirement-or-be-disqualified.md)
- [`../knowledge/govtech-decision-trees.md`](../knowledge/govtech-decision-trees.md) — FedRAMP/StateRAMP-needed tree

## Provenance

FedRAMP Authorization Act (codified at 44 U.S.C. §§ 3607–3616, enacted Dec. 2022). OMB Memo M-23-22
(FedRAMP authorization requirements). NIST SP 800-53 Rev 5 (security control catalog).
StateRAMP program: stateramp.org `[verify-at-use]`.

---

_Last reviewed: 2026-06-08 by `claude`._
