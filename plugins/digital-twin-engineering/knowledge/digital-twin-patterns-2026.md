# Knowledge — Digital-twin patterns (2026)

> **Last reviewed:** 2026-07-09 · **Confidence:** High on the durable concepts (the taxonomy, the fidelity principle, modeling approaches, state sync & drift/calibration, validation, the ingestion patterns); **Medium on the dated platform/standards map — features, pricing, and spec revisions are volatile and carry retrieval dates below.**
> The reference the `twin-integration-engineer` reads when designing and building a twin: the taxonomy, the fidelity-to-the-decision principle, modeling approaches, telemetry ingestion & sync, the modeling standards, simulation & what-if, drift/calibration/reconciliation, fidelity validation, and a 2026 platform snapshot.

The team's discipline: **scope the twin to a decision, buy only the fidelity that decision needs, ingest to the model, keep the twin in sync, and validate it against the real asset with stated error bounds.**

---

## The twin taxonomy

Three orthogonal axes — a twin is a point in this space, not a single label:

**Axis 1 — scope:**

| Scope | Models | Example |
|---|---|---|
| **Asset / component twin** | One physical thing or a part of it | A pump, a motor, a turbine blade |
| **Process twin** | A process / production flow | An assembly line, a batch reactor, a logistics flow |
| **System-of-systems twin** | Many twins interacting | A plant, a fleet, an energy grid, a city district |

**Axis 2 — direction (shadow vs true twin):**

- **Digital shadow** — a **one-way** flow, asset → model. The model mirrors the asset (monitor, predict) but does not act back. Most value lives here, and it carries no closed-loop safety burden.
- **True bidirectional twin** — a **two-way** flow. The model also actuates back to the asset (control, closed-loop optimization). This inherits real-time, safety, latency, and control-authority obligations — and the seam to `robotics-autonomous-systems-engineering`.
- (A **digital model** with *no* automatic data flow — a manually-updated CAD/sim — is the degenerate case: useful for design, but not a live twin.)

**Axis 3 — maturity (what question it answers):**

| Maturity | Answers | Needs |
|---|---|---|
| **Descriptive / informative** | "What is happening now?" | Live state, remote monitoring |
| **Predictive** | "What will happen?" | A model that forecasts (RUL, failure, throughput) |
| **Prescriptive** | "What should we do?" | Simulation + optimization / what-if to recommend an action |

---

## The fidelity principle — only as much as the decision needs

Fidelity is a **cost**, not a virtue. A photoreal 3D scene and a full-physics solver are expensive to build, run, and maintain; they are justified only when a coarser model can't support the decision within its error tolerance.

The method:

1. **State the decision and its error tolerance.** "Service this pump within a week" tolerates ±1 day of RUL error; "collision-avoid a robot at 2 m/s" tolerates centimetres and milliseconds.
2. **Find the lowest fidelity that clears the tolerance.** A reduced-order/lumped-parameter model often does. Escalate to full physics + 3D only where spatial/dynamic behavior is what the decision hinges on.
3. **Name what a fidelity increase would buy — and cost.** So the trade is explicit, not a reflex toward realism.

Photoreal ≠ useful. A twin's worth is the decision it improves, not the frames it renders.

---

## Modeling approaches

| Approach | Use when | Trade-off |
|---|---|---|
| **Physics / first-principles** (CFD, FEA, thermodynamic, kinematic) | Governing equations are known and calibration data is scarce; you must extrapolate beyond observed conditions | Compute-heavy; needs the equations + parameters; slow for real-time without reduction |
| **Data-driven / surrogate / reduced-order model (ROM)** | Rich telemetry history; you need fast inference (real-time, many what-ifs) | Can't extrapolate past its training envelope; needs enough representative data |
| **Hybrid (physics-informed / calibrated surrogate)** | Most real programs — physics for structure, data to calibrate the parameters | More moving parts; you must track which parts are physics and which are learned |

A **reduced-order model (ROM)** is the workhorse for real-time twins: it approximates an expensive physics model cheaply enough to run in the loop, trading a stated amount of accuracy for speed. **Hybrid** is the default in practice — start from physics for structure and extrapolation, calibrate its parameters against telemetry.

---

## Telemetry ingestion & state sync

**Protocols (get the signal off the asset and into the model):**

- **OPC-UA** — the industrial standard for machine/PLC data; rich information model, common on the plant floor.
- **MQTT** — lightweight pub/sub for device telemetry; ubiquitous in IoT, good over constrained links.
- **Kafka** — the high-throughput stream backbone once data is off the edge; buffering, replay, fan-out to the twin and the warehouse.

**Edge vs cloud:** pre-aggregate/filter at the **edge** where bandwidth, latency, or intermittent connectivity demand it (send features, not every raw sample); do the heavy modeling in the **cloud** where compute is cheap. The split is a design decision, not a default.

**Sampling & sync latency:** sample at the rate the **decision** needs — over-sampling is cost, under-sampling is blindness. The **sync-latency budget** (how stale the twin may be) follows the decision's timescale: minutes/hours for a maintenance decision, sub-second for a control decision.

**Bind to the model, not to a database.** Ingested signals bind to **DTDL properties** / **AAS submodel elements** — a twin is a live model of the asset, not a data lake of its readings.

---

## Modeling standards

- **DTDL (Digital Twins Definition Language)** — JSON-LD models (interfaces, properties, telemetry, relationships, components) that define a twin's shape; native to **Azure Digital Twins**, which hosts the live twin *graph* (twins + relationships). _(Reviewed 2026-07-09.)_
- **ISO 23247** — the international framework for a digital twin in manufacturing (reference architecture: observable manufacturing elements, data collection, the digital-twin entity, and user entities). Use it as the architecture backbone. _(Reviewed 2026-07-09 — spec detail volatile, re-verify.)_
- **AAS / Asset Administration Shell** (Industrie 4.0 / IDTA) — a standardized, portable digital representation of an asset built from **submodels**; the interoperability play across vendors. _(Reviewed 2026-07-09 — ecosystem maturing, verify tool support.)_

Standards give the twin a **portable, interoperable shape** — reach for them over a bespoke schema when interoperability or lifecycle portability matters.

---

## Simulation & what-if

A twin earns "predictive/prescriptive" by **simulating** — running the model forward from the *current twin state* to answer "what if?". The rule: a simulation whose inputs aren't the live twin state is a disconnected model, not a twin. Common what-ifs: "throughput if we add a station?", "temperature if this fan fails?", "RUL if we run 10% hotter?". Physics models simulate from equations; surrogate/ROM models simulate fast enough for many scenarios or real-time optimization.

---

## State sync, drift & calibration — the silent failure mode

A twin **drifts** from its asset over time: the asset wears, sensors degrade, and configurations change, so a model that matched at commissioning slowly stops matching.

- **Drift detection** — monitor the **predicted-vs-actual error** on the decision-relevant outputs; alert when it exceeds the tolerance. This is the twin's equivalent of a freshness monitor.
- **Root-cause the drift to one of three causes** — a **sensor** change (miscalibration, fault), a **model** limitation (regime the model was never fit for), or a real **asset** change (wear, damage, reconfiguration). "Recalibrate and move on" without naming which is symptom-chasing.
- **Calibration / reconciliation** — re-fit the model's parameters to the current asset (parameter estimation, data assimilation, Kalman-filter-style state reconciliation). Record what was recalibrated and why.

A twin with no drift monitor quietly lies with growing confidence.

---

## Fidelity validation — does the twin match the asset?

The step most teams skip, and the one that makes a twin trustworthy:

1. **Choose validation SLIs** — the predicted-vs-actual on the *decision-relevant* outputs (not every variable). If the decision is RUL, validate predicted vs realized time-to-failure; if throughput, validate predicted vs measured rate.
2. **Compute error bounds** — quantify the gap (MAE / RMSE / % error, and a confidence interval), against a **hold-out** or a live comparison window. State it, don't hand-wave "looks close."
3. **Calibrate to close the gap** — tune parameters where the error exceeds tolerance.
4. **Give a fit-for-decision verdict** — is the twin accurate enough *for the decision it serves*, within its stated tolerance? A twin can be "wrong" in absolute terms and still fit-for-decision, or photoreal and unfit.

Capture it in the [`twin-fidelity-validation-report.md`](../templates/twin-fidelity-validation-report.md) template.

---

## 2026 platform map (dated — volatile, re-verify before quoting)

- **Twin graph / state:** **Azure Digital Twins** (DTDL models + twin graph + telemetry routing); **Eclipse Ditto** (open-source device-twin state + APIs). _(Retrieved 2026-07-09.)_
- **Interoperability standard:** **AAS / Asset Administration Shell** (IDTA submodels), **ISO 23247** reference architecture for manufacturing. _(Retrieved 2026-07-09 — spec revisions volatile.)_
- **3D / physics / visualization:** **NVIDIA Omniverse** (OpenUSD, physics-accurate 3D, real-time sim), **Unity** / **Unreal** (real-time 3D twins & operator visualization). _(Retrieved 2026-07-09.)_
- **Engineering / infrastructure twins:** **Bentley** (iTwin) and **Siemens** (Xcelerator / Teamcenter) for BIM/CAD-anchored, plant & built-asset twins. _(Retrieved 2026-07-09 — vendor feature sets and pricing vary, re-verify with `ravenclaude-core/deep-researcher` before a client commitment.)_
- **Telemetry transport:** **OPC-UA** (plant floor), **MQTT** (device pub/sub), **Kafka** (stream backbone). _(Stable protocols; versions/profiles evolve.)_

---

## Provenance

- Durable concepts (twin taxonomy, shadow-vs-bidirectional, fidelity-to-the-decision, physics/data-driven/hybrid modeling, ROM, ingestion protocols, drift/calibration, validation) are consensus practice across the digital-twin and simulation literature, reviewed 2026-07-09 — **High confidence**.
- The platform/standards map is a **2026-07 snapshot**; platform features, pricing, connectors, and ISO 23247 / AAS / DTDL revisions are volatile and carry the retrieval dates above — re-verify before pinning in a deliverable.
