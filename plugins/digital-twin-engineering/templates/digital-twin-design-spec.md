# Digital-twin design spec — <asset / process name>

> The one-page design captured **before** building. Pairs with
> [`twin-fidelity-validation-report.md`](twin-fidelity-validation-report.md) (proving the built twin matches the asset).

**Owner:** <name / team> · **Date:** <YYYY-MM-DD> · **Platform:** <Azure Digital Twins+DTDL / Eclipse Ditto / AAS / Omniverse / Unity-Unreal / Bentley-Siemens> · **Status:** draft / approved / built

## The decision this twin serves
- **Decision it must inform:** <the question the twin exists to answer — e.g. "service this pump before it fails" / "throughput if we add a station">
- **Error tolerance the decision accepts:** <e.g. "±1 day of RUL" / "±5% throughput" — this sets the fidelity ceiling>
- **Consumers:** <who acts on the twin's output — maintenance / operations / planning>

> A twin that answers no decision is a rendering. If this section is empty, stop.

## Twin scope & type
- **Scope:** <asset/component · process · system-of-systems>
- **Direction:** <digital shadow (one-way) · true bidirectional (actuates back)> — if bidirectional, note the safety/latency/control-authority implications + the `robotics-autonomous-systems-engineering` seam
- **Maturity:** <descriptive/informative · predictive · prescriptive>

## Modeling approach & fidelity
- **Modeling approach:** <physics/first-principles · data-driven/surrogate/reduced-order (ROM) · hybrid> — and which parts are physics vs calibrated
- **Fidelity level:** <the LOWEST fidelity that clears the decision's error tolerance>
- **What more fidelity would buy / cost:** <so the trade is explicit, not a reflex toward realism>

## Telemetry & sync model
| Signal | Sampling rate | Transport (MQTT/OPC-UA/Kafka) | Edge or cloud | Binds to (DTDL property / AAS submodel) |
|---|---|---|---|---|
| <vibration features> | <rate> | <OPC-UA→Kafka> | <edge pre-aggregate> | <spindle.vibration> |
| <temperature> | <rate> | <MQTT> | <cloud raw> | <spindle.temperature> |
| <load> | <rate> | <OPC-UA> | <cloud raw> | <spindle.load> |

- **Sync cadence:** <periodic (minutes/hours) · streaming (sub-second)>
- **Sync-latency budget:** <how stale the twin may be and still serve the decision>
- **Edge-vs-cloud rationale:** <what computes where, and why (bandwidth/latency/connectivity)>

## Standards
- **Model standard:** <DTDL · AAS submodels · ISO 23247 reference architecture — or bespoke, with a reason>
- **Interoperability need:** <cross-vendor / lifecycle portability — or none>

## Simulation & what-if
- **Scenarios to drive:** <the what-ifs the decision needs, run from live twin state>
- **Simulator:** <physics solver · ROM/surrogate for real-time>

## Visualization
- **Level:** <3D scene (Omniverse/Unity/Unreal) · dashboard/graph> — and WHY that level (space matters vs a number answers it)

## Drift & calibration policy
- **Drift SLI:** <the predicted-vs-actual error monitored for drift>
- **Tolerance:** <e.g. ±10%>
- **Recalibration:** <parameter re-fit / data assimilation — and the root-cause triage: sensor vs model vs asset>

## Validation plan
- **Validation SLIs:** <predicted-vs-actual on the decision-relevant outputs>
- **How error bounds are computed:** <hold-out / live comparison window · MAE/RMSE/% + CI>
- **Fit-for-decision bar:** <the tolerance the twin must clear — from "the decision this twin serves" above>

## Seams (not this team)
- **Device firmware / sensors / edge / connectivity:** embedded-iot-engineering
- **Robot control / motion / autonomy (bidirectional actuation):** robotics-autonomous-systems-engineering
- **Warehouse / BI for twin history:** data-platform
- **Shop-floor MES / OEE:** manufacturing-operations

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
