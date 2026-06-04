# Experiment design

**Hypothesis (from product-management):** <if we do X, metric Y improves because Z>
**Unit of assignment:** <user/account/session>  **Assignment:** deterministic, sticky (hash)
**Primary metric:** <metric>  **MDE / power / duration:** <set WITH applied-statistics>
**Guardrail metrics:** <latency, error rate, revenue — must not harm>
**Exposure logging:** <how we record who saw the variant>
**Trustworthiness checks:** SRM, exposure validity, no peeking
**Significance verdict:** applied-statistics (do NOT call it here)
