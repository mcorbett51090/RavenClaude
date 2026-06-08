# Insurance — Life / Health / Employee Benefits

The **insurance-life-health-benefits** plugin — the group life, health, and employee-benefits side of insurance: designing the benefits program, pressure-testing the rating and renewal math behind it, and running the enrollment and compliance operations that keep it live. Distinct from property & casualty (`insurance-pc`), HR benefits administration (`people-ops-hr`), and provider-side medical billing (`medical-revenue-cycle`).

> **Educational scaffolding, not advice.** Every agent frames trade-offs and surfaces the questions a licensed broker, credentialed actuary, or ERISA counsel must answer and sign. Nothing here is legal, tax, or actuarial advice.

## Agents

- **`benefits-advisor`** — The benefits package shape: plan design per line (medical / dental / vision / group life / short- & long-term disability), plan-type mechanics (HMO / PPO / HDHP+HSA; deductible / coinsurance / OOP-max), a funding strategy (fully-insured vs self-funded vs level-funded) sized to the group, contribution structure, and the ACA / ERISA basics a plan sponsor must respect.
- **`underwriting-and-actuarial-analyst`** — The numbers: rating factors, manual vs experience rating by credibility, loss ratios and the ACA medical-loss-ratio (MLR) rebate rule, and decomposing/sanity-checking a renewal projection (trend, experience, pooling, demographic drift, plan change).
- **`enrollment-and-compliance-lead`** — Operations and filings: the open-enrollment cycle (timeline, eligibility, QLE/special enrollment, communications), carrier/EDI coordination, and the recurring compliance calendar (COBRA, HIPAA, ACA Forms 1095-C/1094-C, ERISA Form 5500 + SPD/SBC distribution).

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install insurance-life-health-benefits@ravenclaude
```

## Seams

- **Property & casualty lines (property, liability, auto, workers' comp)** → `insurance-pc`; this plugin is life/health/benefits only.
- **Day-to-day HR benefits administration / HRIS workflow** → `people-ops-hr`; we design and review the program, they run the ongoing administration.
- **Provider-side medical billing / claims adjudication / revenue cycle** → `medical-revenue-cycle`; we are the plan-sponsor/payer side, not the provider's revenue cycle.
- **PHI/PII handling and the security posture of a benefits system** → `ravenclaude-core/security-reviewer`.
- **Any binding legal / tax / actuarial opinion** → a licensed broker, credentialed actuary, or ERISA counsel; this plugin never gives advice.

Inherits `ravenclaude-core` protocols (Capability Grounding + Structured Output). Requires `ravenclaude-core@>=0.7.0`. Designed to be installed alongside `people-ops-hr` and `insurance-pc`.
