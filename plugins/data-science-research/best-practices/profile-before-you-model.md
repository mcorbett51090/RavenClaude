# Profile the data before you fit any model

No model is fit before the data is profiled — shape, types, missingness pattern, cardinality, distributions, duplicates, leakage candidates, and the target definition. A model on un-profiled data is a guess with a confidence interval. Plot distributions rather than trusting summary statistics (the mean of a bimodal column describes nobody), and ask *why* a value is missing before imputing it. The profile is what makes the downstream score interpretable.
