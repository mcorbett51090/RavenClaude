# Data-science-research best-practices

Atomic, enforceable rules the data-science-research agents apply. Each file is one rule with a short rationale; the agents cite them by filename. Canonical decision logic lives in [`../knowledge/data-science-research-decision-trees.md`](../knowledge/data-science-research-decision-trees.md); these rules are the always-on priors.

| Rule | Gist |
|---|---|
| profile-before-you-model | No model is fit before the data is profiled |
| leakage-is-the-cardinal-sin | Fit every transform inside the fold; split before any fit |
| cross-validate-a-single-split-lies | k-fold with the spread, never one point estimate |
| the-metric-must-match-the-decision | Choose the metric from the decision and cost, not habit |
| every-finding-carries-its-uncertainty | Sample size + confounders + the caveat, never a bare headline |
| reproducible-or-it-didnt-happen | Pinned env + versioned data + fixed seed, or it's an anecdote |
| baseline-before-the-fanciest-model | A dumb baseline is the bar; classical before deep |
| generate-hypotheses-dont-decide-significance | Exploration generates; applied-statistics rules on real |
