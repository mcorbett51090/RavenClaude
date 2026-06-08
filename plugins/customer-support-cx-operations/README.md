# customer-support-cx-operations

Contact-center and CX operations specialists for deflection strategy, quality programs, knowledge-base
management, and staffing/queue design. This plugin helps you build and optimize a support operation
that resolves issues efficiently, measures the right signals, and staffs to the actual shape of demand.

> **The one-line philosophy:** great support is efficient resolution at the right cost. Deflect with
> answers (not walls), measure effort and satisfaction separately, staff to the queue curve, and treat
> the knowledge base as a product that earns its own roadmap.

---

## When to use this plugin (vs. its neighbours)

| You're asking… | Use |
|---|---|
| "Design our support operating model / channel strategy / tiering" | **customer-support-cx-operations** (`cx-ops-lead`) |
| "Build a QA scorecard / design our CSAT or CES program / root-cause CSAT drops" | **customer-support-cx-operations** (`support-quality-analyst`) |
| "Improve deflection / audit our knowledge base / fix our macros" | **customer-support-cx-operations** (`knowledge-and-deflection-strategist`) |
| "How many agents do we need? / We're missing SLA / forecast peak staffing" | **customer-support-cx-operations** (`contact-center-workforce-analyst`) |
| "Normalize ticket data / build ticket pipelines for analytics" | `data-platform` |
| "Account health, churn risk, NPS-to-health-score model" | `customer-success-analytics` |
| "Build the AI support agent / wire the LLM" | `claude-app-engineering` |
| "FTE cost modeling / headcount approval" | `finance` |

---

## What's inside

- **4 agents** — `cx-ops-lead`, `support-quality-analyst`,
  `knowledge-and-deflection-strategist`, `contact-center-workforce-analyst`.
- **3 skills** — `deflection-and-knowledge-strategy`, `support-quality-and-csat`,
  `workforce-and-queue-design`.
- **3 commands** — `/customer-support-cx-operations:design-support-queue`,
  `:build-qa-scorecard`, `:plan-deflection`.
- **2 templates** — `qa-scorecard.md`, `sla-and-escalation-matrix.md`.
- **Knowledge bank** — `knowledge/cx-ops-decision-trees.md`: Mermaid decision trees for
  channel strategy, deflect-vs-staff tradeoffs, and escalation tier design, plus a dated 2026
  CX platform capability map (Zendesk, Intercom, Freshdesk, Gladly, Salesforce Service Cloud,
  AI deflection tools).
- **6 best-practices** and **1 advisory hook** (flags SLA targets without queue basis, CSAT/CES
  conflation, macros with PII or unconditional walls, AI deflection without handoff).
- **`scripts/cx_calc.py`** — Erlang C staffing, deflection ROI, CSAT/CES, shrinkage-adjusted FTE.

---

## House opinions (the short list)

1. CSAT and CES measure different things — never conflate them.
2. Staff to the curve, not the average (Erlang C, not averages).
3. The knowledge base is the product — own its roadmap.
4. Every escalation carries a reason code.
5. Deflect with answers, not walls.
6. AI deflection must know when to hand off.

---

## Requires

`ravenclaude-core@>=0.7.0`. See [`CLAUDE.md`](CLAUDE.md) for the full team constitution and seams.
