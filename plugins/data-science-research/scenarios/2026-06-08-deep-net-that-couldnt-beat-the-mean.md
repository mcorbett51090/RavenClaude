---
scenario_id: 2026-06-08-deep-net-that-couldnt-beat-the-mean
contributed_at: 2026-06-08
plugin: data-science-research
product: xgboost
product_version: "unknown"
scope: likely-general
tags: [baseline, modeling, tabular, deep-learning, model-selection]
confidence: high
reviewed: false
---

## Problem

A team spent six weeks building and tuning a deep neural network for a tabular demand-forecasting problem, then reported it as a success. When someone finally asked "what does it beat?", there was no baseline — the project had never established the bar. A quick check showed the network's RMSE barely edged out the column mean and was *worse* than a five-minute gradient-boosted tree. Weeks of GPU time had bought a model that didn't clear a trivial bar.

## Constraints context

- ~200k rows, ~60 tabular features — classic structured-data regression, no images or text.
- The deep model had grown elaborate (embeddings, dropout schedules, a custom learning-rate warmup) and demanded a GPU to retrain.
- "It's deep learning so it must be better" had gone unchallenged because nothing cheap had been measured first.

## Attempts

- Tried: tuning the network harder — more layers, more epochs, more hyperparameter search. Failed — marginal gains at large cost, and still no reference point to say whether any of it mattered.
- Tried: comparing the network only to a constant (predict-the-mean) baseline. Helped reveal it barely beat the mean, but a too-weak baseline can flatter a mediocre model — the mean is a floor, not a fair competitor.
- Tried: establishing a proper ladder of baselines — mean, a linear model, then a gradient-boosted tree (XGBoost) with light tuning — and comparing honestly on the same CV scheme. This worked: the boosted tree beat the network on accuracy, trained in minutes on CPU, and was far simpler to operate.

## Resolution

The gradient-boosted tree won outright — lower RMSE, minutes to train on CPU, no GPU dependency — and the deep model was retired. The real finding was about the data (well-engineered tabular features didn't need a deep net), not a modeling victory. Six weeks would have been one afternoon if the baseline had come first.

## Lesson

Start with a baseline, not the fanciest model: a dumb baseline (mean/majority/linear) plus a gradient-boosted tree is the bar a complex model must clear, and on tabular data classical methods are the honest default. Establish the bar *before* investing in complexity — a fancy model that barely beats the mean is a finding about the data, not a win.
