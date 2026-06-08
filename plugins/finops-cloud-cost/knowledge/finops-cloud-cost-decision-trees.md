# FinOps & Cloud Cost — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `finops-cloud-cost`. **Traverse the relevant Mermaid tree
> top-to-bottom before recommending** — the proactive complement to the Capability Grounding
> Protocol. Volatile product/pricing/version facts carry a retrieval date and a re-verify-at-use
> rider. Market positions and prices change faster than any training corpus.

---

## Decision Tree: Commitment vs on-demand (covering the steady-state baseline)

```mermaid
flowchart TD
  A[Has rightsizing been completed in the last 30 days?] -->|No| Z1[Stop. Rightsize first — committing to an over-sized instance locks in waste.]
  A -->|Yes| B[Is there ≥14 days of utilization data?]
  B -->|No| Z2[Gather utilization data first. Estimate without P90 data is unreliable.]
  B -->|Yes| C{What is the P0 floor — the minimum consistent hourly usage?}
  C -->|Zero or near-zero| Z3[Workload is bursty or ephemeral. On-demand or Spot only. No commitment.]
  C -->|Stable non-zero baseline| D{How stable is this workload over the next 12–36 months?}
  D -->|Uncertain / fast-changing| E[1-year term, Compute Savings Plan or Convertible RI. Flexibility > savings.]
  D -->|Stable — same instance family expected| F{Is instance-family flexibility needed?}
  F -->|Yes| G[Compute Savings Plan — covers any EC2/Fargate/Lambda family. verify-at-use.]
  F -->|No| H[EC2 Instance Savings Plan or Standard RI — deepest savings on a known family. verify-at-use.]
  D -->|Very stable, 3+ years confident| I{Does the savings gain of 3-year justify the lock-in risk?}
  I -->|No / growth uncertain| E
  I -->|Yes| J[3-year term — run the break-even months first. verify-at-use on rates.]
  E --> K[Commit to the P0 floor only. On-demand the rest.]
  G --> K
  H --> K
  J --> K
```

**Leaf rule:** commit only to the P0 steady-state floor — the usage you would have anyway in your
worst week. Everything above runs on-demand or spot. A commitment beyond the floor is a stranded
cost if usage drops. Use `finops_calc.py break_even()` and `commitment_coverage()` for the math
before any purchase.

---

## Decision Tree: Rightsize before you commit

```mermaid
flowchart TD
  A[Is there a cost optimization opportunity?] --> B{What is the P90 CPU utilization?}
  B -->|≤25% — clearly oversized| C[Downsize first. Recommended: P90 CPU target 40-70%.]
  B -->|26-70% — in the target band| D{What is the P90 memory utilization?}
  B -->|>70% — may be undersized or correctly sized| E[Verify memory too. Do not downsize on CPU alone.]
  D -->|≤30% — memory oversized| C
  D -->|30-80% — in target band| F[Instance is reasonably sized. Proceed to commitment evaluation.]
  D -->|>80% — memory pressure| G[Do NOT downsize. Possible memory leak or legitimate sizing.]
  E --> D
  C --> H[Phased approach: resize one instance, monitor 48h, roll out fleet]
  H --> I[After rightsizing: re-measure baseline, then evaluate commitments]
  F --> I
  I --> J{Are there idle or orphan resources?}
  J -->|Yes| K[Eliminate idle resources before committing — they inflate the baseline]
  J -->|No| L[Proceed to commitment-vs-on-demand tree]
  K --> L
```

**Leaf rule:** the optimization sequence is invariant — rightsize, then eliminate idle, then commit.
Compressing or skipping steps means committing to waste. The savings from each step are not additive
if you buy commitments before rightsizing; they must be calculated on the post-rightsizing baseline.

---

## Decision Tree: Allocation model (tag → showback → chargeback)

```mermaid
flowchart TD
  A[Is there a tagging policy enforced at resource creation?] -->|No| Z1[Stop. Design and enforce a tagging policy first. See tagging-policy.md template.]
  A -->|Yes| B{What percentage of spend is tagged?}
  B -->|<60% tagged| Z2[Tagging coverage is too low for reliable allocation. Improve enforcement before showback.]
  B -->|60-80% tagged| C[Showback is viable but note the untagged % in every report. Target >95% in 90 days.]
  B -->|>80% tagged| D{Is chargeback a firm requirement from Finance?}
  D -->|No| E[Start with showback. Deliver weekly team-spend digest to engineers. Measure behavior change.]
  D -->|Yes| F{Have teams had ≥2 months of showback visibility?}
  F -->|No| G[Showback first. Charging without visibility creates resentment, not ownership.]
  F -->|Yes| H[Advance to chargeback. Define GL mapping, allocation keys, reconciliation process.]
  E --> I{Is behavior changing? Are engineers reducing waste?}
  I -->|Yes| J[Showback is working. Consider advancing to chargeback if Finance requires.]
  I -->|No| K[Investigate: are engineers seeing the report? Is it in their workflow? Adjust delivery.]
  C --> D
  H --> L[Hand off GL booking to finance plugin]
  J --> M[Define unit economics. cost-per-customer, cost-per-request, cost-per-feature.]
  L --> M
```

**Leaf rule:** tagging is the prerequisite for everything downstream. Showback before chargeback —
charging teams for costs they cannot verify creates political resistance, not ownership. Unit
economics is the mature outcome: a single cost-per-unit metric that connects engineering decisions
to business outcomes.

---

## FinOps maturity staging (crawl/walk/run)

| Stage | What it looks like | Gap to fix |
|---|---|---|
| **Crawl** | No tagging policy or <60% tagged; cloud bill is Finance's problem; no team-level visibility; no commitments; cost reviews quarterly if at all. | Tagging policy + enforcement; showback to engineers; anomaly alerts. |
| **Walk** | Tagging >80%; weekly showback to teams; some commitments purchased but ad hoc; rightsizing done occasionally; FinOps function exists but informal. | Systematic rightsizing before commitment purchase; commitment coverage tracked; anomaly detection automated. |
| **Run** | Tagging >95%; automated anomaly alerts; commitments reviewed monthly; unit economics tracked (cost-per-customer); FinOps team has a charter and an OKR; AI token cost is budgeted. | Continuous optimization loop; forecasting; AI cost governance; chargeback to cost centres. |

---

## 2026 capability map — cross-cloud FinOps tooling (dated, re-verify at use)

_Retrieved 2026-06-08. Product capabilities, pricing, and availability are volatile — re-confirm
before making a purchase recommendation. This is orientation, not a procurement evaluation._

| Category | Tools (2026) | Notes |
|---|---|---|
| **Native cloud billing & cost management** | AWS Cost Explorer + Cost and Usage Report (CUR 2.0), AWS Budgets, AWS Compute Optimizer; Azure Cost Management + Billing (formerly Cost Management + Billing); GCP Cloud Billing + BigQuery billing export | First stop. Must be configured before buying third-party. CUR 2.0 (parquet, hourly) is the modern AWS data layer. [verify-at-use] |
| **FinOps Foundation FOCUS spec** | FinOps Foundation FOCUS (FinOps Open Cost and Usage Specification) — normalizes billing data across clouds into a common schema. v1.0 ratified 2024; v1.1 in progress 2025-2026. [verify-at-use] | Adopted by AWS, Azure, GCP, Oracle, and major third-party tools. Column names and schema version evolve — always check the current spec before implementing. |
| **Third-party cost management platforms** | CloudHealth (VMware/Broadcom, acquired) / Apptio Cloudability (IBM); Vantage (strong developer UX, AWS-first, expanding); Finout (virtual tagging, showback); Anodot (anomaly detection-focused); Spot.io (CloudCheckr + optimization) [verify-at-use: acquisition/product status changes fast] | All marked verify-at-use — acquisition activity in this space is high. Validate current company/product status before recommending. |
| **Kubernetes cost allocation** | OpenCost (CNCF, open source, Prometheus-native); Kubecost (commercial + OSS, OpenCost upstream contributor) | OpenCost is the CNCF-blessed spec; Kubecost is the commercial implementation. Use either for namespace-level cost attribution in shared clusters. [verify-at-use] |
| **RI/SP management & optimization** | AWS native RI/SP recommendations (Cost Explorer); CloudHealth RI management; Spot.io Eco (RI/SP automation); ProsperOps (automated RI/SP management, AWS-focused) [verify-at-use] | Automated RI/SP management tools can over-commit — always verify the steady-state baseline before delegating commitment purchases to automation. |
| **Anomaly detection** | AWS Cost Anomaly Detection (native, ML-based); Azure Cost Management alerts; Anodot (third-party, ML anomaly); custom z-score/percentage-baseline via CloudWatch Metrics Insights / Pub/Sub [verify-at-use] | Native tools are the first layer; third-party for cross-cloud aggregation. See `scripts/finops_calc.py anomaly_z_score()` for the roll-your-own calculation. |
| **AI/LLM inference cost** | AWS Bedrock Cost Explorer (per-model usage); Azure AI Foundry (Azure OpenAI) billing; GCP Vertex AI billing; Anthropic Console usage dashboard; OpenAI usage dashboard; LangSmith (LangChain observability, includes token cost); Helicone (open-source LLM observability + cost); Portkey [verify-at-use: all rapidly evolving] | Provider dashboards are the first stop. Token cost observability tooling is nascent — verify availability and capabilities at use. |
| **FinOps practice and framework** | FinOps Foundation (finops.org) — the authoritative framework, maturity model, and FOCUS spec. The crawl/walk/run model, the inform/optimize/operate loop, and persona definitions all originate here. | Foundation membership and certification are legitimate signals of FinOps practice maturity. [verify-at-use for membership structure] |

> Provenance: FinOps Foundation framework documentation, AWS/Azure/GCP billing documentation, CNCF
> landscape, and vendor websites retrieved 2026-06-08. Acquisition status, product names, and
> pricing are volatile — re-verify at use. No invented products or capabilities.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution & seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- Neighbour decision trees: `aws-cloud`, `azure-cloud`, `gcp-cloud`, `observability-sre`,
  `terraform-iac`, `finance`.

_Last reviewed: 2026-06-08 by `claude`._
