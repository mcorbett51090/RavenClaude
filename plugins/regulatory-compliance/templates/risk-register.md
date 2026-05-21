# Risk register — [Entity / Domain]

> Enterprise / ORM / AML risk register. Every row carries inherent + residual ratings, named owner, and target rating.

**Domain:** Enterprise | Operational | AML | Cyber | Compliance | Strategic | Reputational | [other]
**Last refresh:** [YYYY-MM-DD]
**Owner (overall):** [name + role]
**Framework:** COSO ERM 2017 | ISO 31000 | NAIC ORSA | BMA CISSA | [other]
**Risk-rating scale source:** [reference to firm's documented rubric]
**Confidentiality:** internal | regulator-only

---

## Risk-rating scale (replicate the firm's rubric)

| Score | Likelihood (annual probability) | Impact ($ / event) |
|---|---|---|
| 5 (Critical) | > 50% | > $10M |
| 4 (High) | 25-50% | $1M-$10M |
| 3 (Medium) | 10-25% | $100K-$1M |
| 2 (Low) | 1-10% | $10K-$100K |
| 1 (Minimal) | < 1% | < $10K |

(Adjust to firm's actual rubric.)

---

## Risk register

| # | Risk title | Category | Inherent L | Inherent I | Inherent (L×I) | Controls (IDs) | Control effectiveness (1-5) | Residual L | Residual I | Residual (L×I) | Target | Within appetite? | KRI | KRI value | Owner | Last reviewed |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|:---:|---|---|---|---|
| 1 | [risk] | Operational | 4 | 3 | 12 | C-001, C-007 | 4 | 2 | 3 | 6 | 4 | ✅ | [KRI] | [value] | [name] | YYYY-MM-DD |
| 2 | ... | ... | | | | | | | | | | | | | | |

---

## Heat map note

Heat maps mask correlated risks. Risks #N and #M correlate (rationale: ...); jointly they should be treated as [aggregate rating], not separately.

---

## Risks above appetite (priority remediation)

| # | Risk | Residual | Target | Gap | Remediation plan | Owner | Target date |
|---|---|---|---|---|---|---|---|

---

## Risk-register hygiene

- **Pruning:** quarterly review removes resolved / immaterial risks.
- **Aging:** any row not reviewed in 12 months requires re-rating or removal.
- **New-event sweep:** incidents and near-misses since last refresh trigger new-row consideration.
- **Top-N reporting:** top 10 by residual (L×I) escalated to executive / board / committee.

---

**Sources:** [Where each risk-row data point came from — incident logs, control-test results, KRI feeds, peer benchmarks.]
