# Leakage is the cardinal sin — fit every transform inside the fold

Any information unavailable at prediction time that touches training invalidates the score: target-derived features, scaling/imputing/encoding fit *before* the train/test split, future data, or group leakage across folds. Split before any fit, fit every transform inside the cross-validation fold (a scikit-learn `Pipeline` enforces this by construction), and use grouped/time-aware folds when the data has structure. A suspiciously high score is a leakage alarm, not a win — audit it before celebrating.
