# Scenario: per-seat pricing is capping an AI product

**The ask:** "We charge per seat. We just shipped an AI feature that does work a
human used to do — and customers are *removing* seats while using us more. Revenue is
flat while value is climbing. What pricing model should we move to?"

**Routes to:** `pricing-strategist` → `value-metric-design` + `pricing-model-selection`.

**The answer shape:**
1. Diagnose the trap with the **failure question**: per-seat *shrinks the account as
   the product succeeds* — the AI feature is the trigger. The value metric is wrong,
   not the number.
2. Run the **value-metric tree** (§2): the value now scales with AI *consumption*, not
   headcount. Candidate metrics: tasks completed, items processed, AI runs.
3. Run the **model tree** (§1): consumption is high-variance and partly unpredictable →
   land on **hybrid** — keep a predictable per-seat (or per-workspace) base for the
   platform value, add metered AI usage with an included allowance + overage.
4. Flag the **migration** (this is a model change, the riskiest kind): bill-shock and
   trust are the risks → hand to `price-change-rollout` with cohort sequencing and
   usage alerts.
5. **Seams:** dollar-impact model → `finance`; the AI cost-to-serve that sets the
   overage floor → `finance` + engineering; significance of any pricing A/B →
   `applied-statistics`.

**Why it's a good illustration:** the highest-leverage fix is the *value metric*, not
the price number — and the answer is the 2026 hybrid pattern, not a pure model.
