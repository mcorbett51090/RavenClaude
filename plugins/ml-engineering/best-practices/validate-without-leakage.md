# Validate without leakage

Guard against target leakage and future information, use time-aware splits for temporal problems, and reserve the test set for a single final evaluation. An offline metric inflated by leakage is a promise production cannot keep, and the gap surfaces only after launch when the model underperforms its glowing validation numbers. Honest validation is cheaper than a failed deployment.
