---
name: perception-and-state-estimation
description: "Build the perception stack: sensor fusion of complementary modalities (lidar/camera/IMU/odometry/GPS), SLAM vs known-map localization, EKF/UKF/particle-filter state estimation, object detection with propagated uncertainty, and behavior-tree / state-machine autonomy that fails safe. Time sync and frames come before the fusion math. Benchmark accuracy is verify-at-use."
---

# Perception & State Estimation

A robot acts on its state estimate. This skill builds one that is stable, fuses sensors that cover each other's failure modes, and feeds an autonomy that fails safe.

> **Engineering, not certification.** Any detection/estimation accuracy number is `[verify-at-use]` against a measurement on the target data — vendor/benchmark numbers rarely transfer. A perception failure that bears on safety is handled by the safety architecture, not hidden in the filter. No PII.

## The workflow

1. **Fix time sync and frames before fusion.** Timestamp every measurement in a common time base and express it in the right frame (REP 105) — most "the filter is broken" bugs are a timestamp or a frame.
2. **Fuse complementary modalities.** Lidar (geometry), camera (semantics), IMU (high-rate motion), wheel odometry (scale), GPS/RTK (global fix) — choose the set so each covers the others' failure modes ([`../../best-practices/sensor-fusion-beats-a-better-sensor.md`](../../best-practices/sensor-fusion-beats-a-better-sensor.md)).
3. **Pick the estimator to the nonlinearity.** EKF for mildly nonlinear systems; UKF when linearization error hurts; a particle filter (AMCL-style) for map-based localization with a multimodal belief. Tune process/measurement noise and gate outliers.
4. **Decide SLAM vs known-map localization.** Traverse the **localization-stack choice** tree in [`../../knowledge/robotics-decision-trees.md`](../../knowledge/robotics-decision-trees.md): build a map online (SLAM, with loop closure) when none exists; localize against a known map when you have one — cheaper and more stable.
5. **Propagate detection uncertainty.** A detection carries confidence and covariance — pass them to the consumer (planner, safety monitor); don't threshold-and-forget.
6. **Structure autonomy to fail safe.** A behavior tree (reactive, composable) or a hierarchical state machine, with explicit recover / degraded / safe-stop branches reachable from every state.

## Metrics

| Metric | Reads | Note |
|---|---|---|
| Localization drift | Estimated vs ground-truth pose over distance | Growing drift → covariance, timestamps, or missing loop closure |
| Estimate consistency (NEES/NIS) | Whether the filter's covariance matches its error | Over/under-confident → retune noise before swapping filters |
| Detection precision/recall | On the target data | `[verify-at-use]` — benchmark numbers don't transfer to your scene |
| Time-sync error | Skew across sensor streams | Nonzero → fix before trusting fusion |

## Anti-patterns

- Tuning the filter algorithm before checking timestamps and covariance.
- Chasing a more expensive single sensor instead of fusing complementary ones.
- Thresholding a detection to a hard yes/no and dropping its uncertainty.
- An autonomy state machine with no explicit degraded/safe-stop branch.

## See also

- The planner/controller that consumes the pose & map: [`../motion-planning-and-control/SKILL.md`](../motion-planning-and-control/SKILL.md).
- Training the detection model itself → [`../../../ml-engineering/CLAUDE.md`](../../../ml-engineering/CLAUDE.md).
- Best practice: [`../../best-practices/sensor-fusion-beats-a-better-sensor.md`](../../best-practices/sensor-fusion-beats-a-better-sensor.md).
