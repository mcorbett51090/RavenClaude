# Customer-Support & CX Operations Plugin — Team Constitution

> Team constitution for the `customer-support-cx-operations` Claude Code plugin — **4** specialist agents
> for the **contact-center and CX operations** layer: support operating model and channel strategy,
> support quality and voice-of-customer programs, knowledge base as a product, and
> workforce/queue design. The Team Lead (typically running `ravenclaude-core`) dispatches the right
> specialist(s) and integrates their reports.
>
> **Orientation:** this file is **domain-specific**. For the domain-neutral team constitution inherited
> by every plugin, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the
> meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`cx-ops-lead`](agents/cx-ops-lead.md) | Support operating model, channel strategy, tiering/escalation design, the CX metric tree (CSAT/CES/NPS + ops metrics), build-vs-buy support stack | "Design our support operating model", "which channels should we staff?", "how do we tier support?", "which helpdesk platform should we use?" |
| [`support-quality-analyst`](agents/support-quality-analyst.md) | QA scorecards, conversation review, CSAT/CES program design, root-cause/VOC analysis, agent coaching loops | "Build a QA scorecard", "design our CSAT program", "why is CSAT dropping?", "close the loop on negative feedback" |
| [`knowledge-and-deflection-strategist`](agents/knowledge-and-deflection-strategist.md) | Knowledge base as a product, self-service deflection, macro/canned-response hygiene, content gaps from ticket data | "Improve our self-service deflection rate", "audit our knowledge base", "which articles are missing?", "our macros are stale" |
| [`contact-center-workforce-analyst`](agents/contact-center-workforce-analyst.md) | Staffing/queue design (Erlang C), occupancy/shrinkage, schedule adherence, SLA/abandonment, demand forecasting for contacts | "How many agents do we need?", "we're missing SLA — why?", "forecast staffing for peak season", "our occupancy is too high" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. If work crosses specialist
boundaries, each specialist returns its slice and the Team Lead re-dispatches.

---

## 2. Routing rules (Team Lead)

- **"Design our support model / what channels should we run?"** → `cx-ops-lead` (model + channel
  strategy); pull in `contact-center-workforce-analyst` for the staffing model behind the channel mix.
- **"CSAT is dropping / our quality is inconsistent"** → `support-quality-analyst` (scorecard + VOC
  root-cause); pull in `knowledge-and-deflection-strategist` if the cause is knowledge gaps.
- **"Self-service rate is low / deflection isn't working"** → `knowledge-and-deflection-strategist`
  (KB gap analysis + deflection strategy); pull in `cx-ops-lead` if the channel model needs redesign.
- **"We're missing SLA / agents are overloaded"** → `contact-center-workforce-analyst` (Erlang C +
  queue analysis); pull in `cx-ops-lead` if the escalation tiers are contributing.
- **"Build a QA program from scratch"** → `support-quality-analyst` (scorecard + calibration design);
  pull in `cx-ops-lead` for the coaching-loop governance.
- **"AI agent / bot deflection isn't performing"** → `knowledge-and-deflection-strategist` (content +
  intent coverage); escalate AI-agent _build_ to `claude-app-engineering`.
- **Anything touching customer PII, ticket data pipelines, or data warehouse schemas** → also route to
  `data-platform`.

---

## 3. Cross-cutting house opinions (every agent enforces)

1. **CSAT and CES measure different things — never conflate them.** CSAT measures outcome satisfaction
   (did we solve the problem?); CES measures interaction effort (was it easy?). Running only one misses
   the other signal. Treat them as complementary, not interchangeable.
2. **Staff to the curve, not the average (Erlang).** Average handle time and average volume are the
   wrong inputs for a staffing model — you staff for the shape of demand. Erlang C is the floor; any
   staffing plan that doesn't account for queue dynamics under load is incomplete.
3. **The knowledge base is the product.** A knowledge base that isn't owned, maintained, and gap-filled
   from ticket data is a liability. Content gaps in the KB are the root cause of most avoidable
   contacts; treat the KB roadmap as a product backlog.
4. **Every escalation carries a reason code.** An escalation without a structured reason code is
   unauditable and unimprovable. The reason code is the unit of escalation analysis.
5. **Deflect with answers, not walls.** Deflection that returns "we cannot help with that" without
   attempting to answer the question is not deflection — it is abandonment. Self-service must deliver a
   resolution path, not a dead end.
6. **AI deflection must know when to hand off.** An AI agent that can't escalate to a human when it
   reaches the edge of its confidence is a support failure. The handoff path is non-negotiable.

---

## 4. Seams (bridges to neighbouring plugins)

- **Ticket data pipelines and normalization** → `data-platform`; this plugin consumes structured
  ticket data for deflection gap analysis and CSAT trend work; that plugin owns the pipelines.
- **Account health, churn risk, and NPS-based customer health scoring** → `customer-success-analytics`;
  NPS *collection* is CX's job, but the account-level health model that turns NPS into churn risk lives
  there.
- **AI-agent / bot build and LLM wiring** → `claude-app-engineering`; this plugin designs the
  deflection strategy and handoff specification; that plugin builds the model.
- **Staffing and labor finance (FTE cost modeling, headcount approvals)** → `finance`; this plugin
  produces the FTE requirements and occupancy targets; finance owns the cost build.
- **Security review for any change touching customer PII in tickets or surveys** →
  `ravenclaude-core/security-reviewer`.

---

## 5. Inheritance

This plugin **inherits `ravenclaude-core` protocols**: the Capability Grounding Protocol
(decision-tree-first + alternate-methods enumeration + honest blocked-reporting), the Structured Output
Protocol for handoffs, and the security/review escalations. Domain-specific rules live in each agent
file and in `best-practices/`; the knowledge bank carries the decision trees and the dated capability
map.

---

## 6. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/cx-ops-decision-trees.md`](knowledge/cx-ops-decision-trees.md) | Picking the right method for channel strategy, deflect-vs-staff tradeoffs, escalation tier design, and AI-deflection handoff. Traverse top-to-bottom before recommending. Also contains the dated 2026 CX platform capability map. |

---

## 7. Calculator

[`scripts/cx_calc.py`](scripts/cx_calc.py) (stdlib-only, Python 3.8+) removes arithmetic error from
five recurring CX decisions: Erlang C agents-needed for a target service level, occupancy,
deflection ROI (deflected contacts × cost per contact), CSAT and CES from rating counts, and
shrinkage-adjusted FTE. It is a **calculator, not a data source** — the user supplies every input.

---

## 8. Milestones

- **v0.1.0** — initial build: 4 agents (cx-ops-lead, support-quality-analyst,
  knowledge-and-deflection-strategist, contact-center-workforce-analyst), 3 skills, 3 commands,
  2 templates, 6 best-practices, 1 advisory hook, 1 knowledge file with decision trees and 2026
  capability map, and `scripts/cx_calc.py`. Created 2026-06-08.
