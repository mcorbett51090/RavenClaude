# Sensor fusion beats a better sensor

**Status:** Pattern
**Domain:** Perception / state estimation
**Applies to:** `robotics-autonomous-systems-engineering`

> Engineering pattern. Sensor specs and accuracy numbers are `[verify-at-use]` against the datasheet and a measurement on the target. No PII.

---

## Why this exists

Every sensor has a failure mode: lidar struggles with glass and rain, cameras with low light and motion blur, IMUs drift, wheel odometry slips, GPS drops out indoors and under canopy. Spending more on one sensor buys a better version of the same failure mode. Fusing **complementary** modalities — so each covers the others' blind spots — usually delivers a more robust state estimate at lower cost than a single premium sensor. The leverage is in the fusion, not the price tag.

## How to apply

- Choose the sensor set so each modality covers another's failure mode (geometry + semantics + high-rate motion + global fix).
- Fix time synchronization and frames **before** the fusion math — most fusion problems are a timestamp or a frame, not the filter.
- Match the estimator to the nonlinearity (EKF / UKF / particle filter) and tune process/measurement noise; gate outliers.
- Check estimate consistency (NEES/NIS) rather than trusting the covariance blindly.
- Confirm any accuracy number on the target data — `[verify-at-use]`; benchmark numbers rarely transfer.

**Do:** fuse complementary sensors; fix sync and frames first.
**Don't:** buy a better single sensor to paper over a fusion or tuning gap.

## Edge cases / when the rule does NOT apply

If a single sensor is genuinely the bottleneck (e.g. no depth information at all in the suite), add the missing modality — that's not "a better sensor," it's covering a gap.

## See also

- [`../skills/perception-and-state-estimation/SKILL.md`](../skills/perception-and-state-estimation/SKILL.md)
- Decision tree (localization stack): [`../knowledge/robotics-decision-trees.md`](../knowledge/robotics-decision-trees.md)

## Provenance

Codifies the `perception-and-autonomy-engineer` house opinion. Sensor/compute options: [`../knowledge/robotics-reference-2026.md`](../knowledge/robotics-reference-2026.md) (verify-at-use).

---

_Last reviewed: 2026-07-02 by `claude`_
