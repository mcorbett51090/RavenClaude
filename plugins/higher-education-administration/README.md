# higher-education-administration

The **enrollment-to-completion operating engine** for a college or university — designing the
institutional operating model, managing the enrollment funnel and financial aid, building student
success and retention systems, and running academic operations and compliance.

> **The one-line philosophy:** net tuition revenue is the real number and retention beats
> recruitment on ROI — every enrollment, aid, and student-success decision is judged by its effect
> on net revenue per retained student, not on headline applications or sticker price.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our enrollment / institutional operating model" | **higher-education-administration** (`higher-ed-administration-lead`) |
| "Model our admissions funnel, yield, or financial-aid leverage" | **higher-education-administration** (`enrollment-and-financial-aid-strategist`) |
| "Improve retention / build an early-alert system" | **higher-education-administration** (`student-success-and-retention-analyst`) |
| "Registrar / accreditation / FERPA / course scheduling" | **higher-education-administration** (`academic-operations-and-compliance-coordinator`) |
| "Run a K-12 school / district" | `k12-school-administration` |
| "Sell or renew an EdTech product to an institution" | `edtech-partner-success` |
| "Plan a workforce / corporate L&D program" | `people-operations-hr` |

---

## What's inside

- **4 agents** — `higher-ed-administration-lead`, `enrollment-and-financial-aid-strategist`,
  `student-success-and-retention-analyst`, `academic-operations-and-compliance-coordinator`.
- **3 skills** — [`enrollment-funnel-and-yield`](skills/enrollment-funnel-and-yield/SKILL.md),
  [`student-retention-and-early-alert`](skills/student-retention-and-early-alert/SKILL.md),
  [`financial-aid-and-net-revenue`](skills/financial-aid-and-net-revenue/SKILL.md).
- **3 commands** — `/model-enrollment-funnel`, `/design-early-alert-system`, `/analyze-net-tuition-revenue`.
- **2 templates** — an enrollment-funnel model and an early-alert playbook.
- **5 best-practices** — see [`best-practices/README.md`](best-practices/README.md).
- **A decision-tree knowledge bank** — [`knowledge/higher-ed-decision-trees.md`](knowledge/higher-ed-decision-trees.md).
- **An advisory hook** flagging anti-patterns (discount/aid decisions with no net-revenue basis,
  retention claims with no cohort/persistence basis, student-data handling with no FERPA note).
- **A calculator** — [`scripts/higher_ed_calc.py`](scripts/higher_ed_calc.py) (stdlib only): yield,
  net tuition revenue, discount rate, retention/persistence, early-alert risk scoring.

---

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install higher-education-administration@ravenclaude
```

Requires `ravenclaude-core` (inherited protocols). See [`CLAUDE.md`](CLAUDE.md) for the team
constitution and house opinions.

> **Compliance note:** FERPA, Title IV, and accreditation requirements change and vary by
> institution and jurisdiction. This plugin gives operational decision-support, not legal or
> compliance advice — verify against current regulation and your institution's counsel.
