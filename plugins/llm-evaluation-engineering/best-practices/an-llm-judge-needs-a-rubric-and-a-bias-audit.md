# An LLM judge needs a rubric and a bias audit

**Rule.** Before you trust an LLM-as-judge, give it anchored criteria (not "rate 1-10"), calibrate it
against human labels on a sample, and audit it for position, verbosity, self-preference, and leniency
bias. Pin the judge model + version.

**Why.** A judge is itself a model whose output can be wrong or biased. Longer answers win on verbosity
bias; the option shown first wins on position bias; a judge favors its own family on self-preference
bias. Uncalibrated, its scores are confident noise.

**Anti-pattern it kills.** Reporting "the judge says the new prompt wins 60%" as fact when the new
prompt just produced longer answers and the judge has an unaudited length bias.

**In practice.** ~30-50 human-labeled examples for calibration; side-randomized pairwise where absolute
scoring is noisy; a documented bias-check result per judge.
