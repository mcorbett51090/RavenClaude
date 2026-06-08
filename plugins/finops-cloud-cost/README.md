# finops-cloud-cost

The **cross-cloud cost engineering and governance** layer. This plugin's team helps you stand up a
FinOps practice, rightsize and commit intelligently, design a tagging and allocation strategy, and
govern AI/token inference costs before they grow from a line item to a budget crisis.

> **The one-line philosophy:** every cloud cost has an owner, and anonymous cost is unmanaged cost.
> Tag at birth, rightsize before you commit, show engineers their bill, and treat AI token spend
> as a first-class budget line — not a catch-all "misc API fees."

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Assess our FinOps maturity / stand up a FinOps practice" | **finops-cloud-cost** (`finops-practice-lead`) |
| "Rightsize our compute / buy RIs or Savings Plans / kill idle resources" | **finops-cloud-cost** (`cost-optimization-engineer`) |
| "Design our tagging strategy / implement showback-chargeback / calculate unit costs" | **finops-cloud-cost** (`cost-allocation-engineer`) |
| "Govern LLM/GenAI spending / set token budgets / right-size our model tier" | **finops-cloud-cost** (`ai-cost-governance-engineer`) |
| "Configure AWS Cost Explorer / CUR / Budget Alerts (AWS-specific)" | `aws-cloud` |
| "Configure Azure Cost Management / Budgets / EA billing (Azure-specific)" | `azure-cloud` |
| "Configure GCP Billing export / BigQuery cost tables (GCP-specific)" | `gcp-cloud` |
| "Which Claude model / SDK to use, prompt engineering tradeoffs" | `claude-app-engineering` |
| "Wire cost anomaly alerts into our observability platform" | `observability-sre` |
| "Book showback chargebacks to cost centres in the GL" | `finance` |
| "Write the Terraform modules that enforce the tagging policy" | `terraform-iac` |

## What's inside

- **4 agents** — `finops-practice-lead`, `cost-optimization-engineer`, `cost-allocation-engineer`,
  `ai-cost-governance-engineer`.
- **3 skills** — `cost-allocation-and-tagging`, `rightsizing-and-commitments`,
  `ai-and-token-cost-governance`.
- **3 commands** — `/finops-cloud-cost:assess-finops-maturity`,
  `:optimize-cloud-spend`, `:design-cost-allocation`.
- **2 templates** — `tagging-policy.md`, `showback-chargeback-model.md`.
- **Knowledge bank** — `knowledge/finops-cloud-cost-decision-trees.md`: Mermaid trees for
  commitment-vs-on-demand, rightsize-before-you-commit, and the allocation model (tag → showback →
  chargeback), plus a dated 2026 capability map of cross-cloud cost tooling.
- **6 best-practices** — tag-at-birth, commit-to-steady-state-baseline, rightsize-before-commit,
  every-cost-has-an-owner, ai-token-first-class-budget-line, anomaly-detection-beats-surprise.
- **1 advisory hook** — flags untagged resources, on-demand with no commitment note,
  hard-coded cost figures without a date, and RI/SP purchase without break-even analysis.
- **`scripts/finops_calc.py`** — stdlib-only calculator: RI/SP break-even months, blended vs
  effective hourly rate, unit cost (cost ÷ units), commitment coverage %, anomaly z-score threshold.

## House opinions (the short list)

1. Tag at birth or you cannot allocate — tagging is infrastructure-as-code, not a quarterly clean-up.
2. Rightsize before you commit — an RI on an over-sized instance locks in waste.
3. Commit only to your steady-state baseline — over-committing makes the discount a stranded cost.
4. Every cost has an owner — even read-only showback changes engineer behavior.
5. AI token cost is a first-class budget line — it can grow 10–100x in a quarter.
6. Anomaly detection beats the monthly surprise — catch spikes in hours, not weeks.

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
