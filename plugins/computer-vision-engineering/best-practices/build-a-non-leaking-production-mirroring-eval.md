# Build a non-leaking, production-mirroring eval

**Rule.** Split train/val/test by **scene / clip / camera / site**, never at the
frame level, and make the test set mirror production variation (lighting, camera,
angle, season). Decide the acceptance threshold before you see the number.

**Why.** Adjacent video frames are near-duplicates; frame-level splitting leaks the
test set into training and inflates the metric. An eval that doesn't mirror
production reports fiction. A held-out set that mirrors production is worth more than
a bigger model.

**Smell.** `train_test_split` over a flat folder of frames; a test set that's all
daytime when production runs at night; a single aggregate metric with no failure
slices.

**Cite:** plugin §4.2; the `design-cv-dataset-and-eval` skill.
