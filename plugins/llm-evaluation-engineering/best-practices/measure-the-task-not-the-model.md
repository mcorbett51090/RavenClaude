# Measure the task, not the model

**Rule.** Build every eval from *your* task's real inputs and *your* definition of good. A benchmark or
leaderboard score (MMLU, an arena ranking) is evidence about a model in general, not about your prompt
on your data.

**Why.** The model that tops a public benchmark can lose on your task because your inputs, your format
constraints, and your failure modes aren't in the benchmark. The only score that predicts your users'
experience is one measured on your task.

**Anti-pattern it kills.** "We picked the model with the highest MMLU" — then shipped a feature that
fabricates citations, because MMLU never tested groundedness on support tickets.

**In practice.** Start the eval set from real (or realistic) task traffic; define good as the failure a
user would notice; only then choose a method and metric.
