# Cross-validate — a single train/test split lies

A point estimate from one train/test split has no error bar; resampling a different split can move it by more than the difference you're claiming. Use k-fold (stratified for imbalance, grouped or time-series-aware when the data demands) and report the spread, not just the mean. When hyperparameters are tuned, use nested cross-validation and report the nested estimate — the test set is touched once, and every peek to tune is a leak that overstates the score.
