# Eliminate training-serving skew

Features must be computed by identical logic in training and serving — use a feature store or a shared transformation library and enforce point-in-time correctness for temporal features. Training-serving skew is the single most common reason a model that scores beautifully offline fails in production, and it is invisible until real traffic hits the differently-computed serving features.
