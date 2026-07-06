---
name: optimize-cv-inference
description: "Get a CV model to hit an edge or real-time latency budget: export to ONNX/TensorRT/OpenVINO/CoreML, FP16/INT8 quantization with an accuracy-delta gate, input-resolution & batching tuning, and thermal/throttling awareness — all measured on the TARGET hardware, not the dev GPU. Also diagnoses train/serve preprocessing skew. Driven by cv-implementation-engineer."
---

# Skill: Optimize CV Inference

Latency is a first-class constraint. This skill takes a working-but-slow model to
the target frame rate without silently trading away accuracy. Driven by
`cv-implementation-engineer`.

## Step 0 — Rule out the skew bug first

Before optimizing, confirm the model is actually correct in production: the #1 CV
production bug is **train/serve preprocessing skew** (resize interpolation,
normalization mean/std, RGB-vs-BGR, letterboxing). If accuracy dropped in
production, fix skew *before* touching performance — you may not have a latency
problem at all. Share one preprocessing function; test it against a known example.

## Step 1 — Measure the baseline on the TARGET hardware

- Benchmark on the actual deployment device (Jetson / CPU / phone / browser), not
  the dev GPU. A dev-GPU number is meaningless for an edge budget.
- Separate the cost: preprocessing, model forward pass, post-processing
  (NMS/decoding). Optimize the dominant one — often it's *not* the forward pass.

## Step 2 — Export to the right runtime

Pick the runtime for the target (see
[`../../knowledge/cv-inference-deployment-and-tooling-2026.md`](../../knowledge/cv-inference-deployment-and-tooling-2026.md)):
TensorRT for NVIDIA/Jetson, OpenVINO for Intel CPU, CoreML for Apple, ONNX Runtime
Web for the browser. **Build the engine on the target** (TensorRT engines are
hardware-specific). Re-measure.

## Step 3 — Quantize behind an accuracy gate

- FP16 is usually near-free — try it first.
- INT8 can be free or cost several points. **Re-run the full eval on the quantized
  model** and report the accuracy delta. Never ship a quantized model without it.
- Use calibration data drawn from the production distribution for INT8.

## Step 4 — Tune resolution and batching

- **Input resolution** is often the biggest latency lever and a direct
  accuracy/speed trade — sweep it and re-eval, don't guess.
- **Batching** helps throughput (cloud) but adds latency (real-time) — batch for
  server throughput, keep batch=1 for a live stream.

## Step 5 — Watch thermal throttling

On edge devices, sustained inference throttles the clock — the frame rate you
measure in a 10-second test isn't the frame rate after 10 minutes. Measure a
sustained run.

## Step 6 — Output

An optimization report: **before/after latency on the target hardware, the
accuracy delta after each export/quantization step, the resolution/batching choice,
and the sustained (not burst) frame rate.** If the budget still can't be hit, escalate
to `cv-systems-architect` to re-frame the model choice — with this evidence.
