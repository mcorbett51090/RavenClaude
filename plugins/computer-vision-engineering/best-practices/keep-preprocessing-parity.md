# Keep preprocessing parity (no train/serve skew)

**Rule.** The image preprocessing at inference must be **byte-identical** to
training: resize interpolation, normalization mean/std, channel order (RGB vs BGR),
and letterboxing. Share one preprocessing function across train and serve, and test it.

**Why.** Train/serve preprocessing skew is the single most common cause of "great in
the notebook, bad in production". A wrong normalization or a BGR/RGB swap silently
tanks accuracy with no error.

**Smell.** Separate resize/normalize code in the training script and the serving
code; a production accuracy drop investigated as "the model is bad" before skew is
ruled out.

**Cite:** plugin §4.5; Step 0 of the `optimize-cv-inference` skill; the production-bug
note in `knowledge/cv-inference-deployment-and-tooling-2026.md`.
