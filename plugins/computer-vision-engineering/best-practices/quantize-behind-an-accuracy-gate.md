# Quantize behind an accuracy gate

**Rule.** Never ship a quantized or exported model without re-running the full eval
on it and reporting the accuracy delta — measured on the target hardware with
production-distribution calibration data. FP16 first (usually near-free), then INT8
if needed.

**Why.** FP16 is usually near-free, but INT8 can cost several accuracy points — and
you don't know which until you re-eval. Trusting a vendor's "lossless quantization"
slide instead of your own eval ships a silent regression.

**Smell.** An exported/quantized model deployed with the pre-quantization accuracy
number attached to it; INT8 calibrated on random data instead of the production
distribution.

**Cite:** plugin §4.6; Step 3 of the `optimize-cv-inference` skill.
