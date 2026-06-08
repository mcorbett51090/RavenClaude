# Start with a baseline; classical before deep

A dumb baseline (mean / majority class / simple linear) is the bar everything else must clear; a gradient-boosted ensemble that barely beats the mean is a finding about the data, not a win. For tabular data, well-engineered features plus regression / trees / gradient boosting is the honest default — reach for deep learning or AutoML only when it beats the baseline by enough to justify its complexity and operational cost. Report the lift over the baseline, not just the absolute score.
