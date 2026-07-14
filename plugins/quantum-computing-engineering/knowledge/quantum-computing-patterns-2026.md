# Knowledge — Quantum-computing patterns (2026)

> **Last reviewed:** 2026-07-14 · **Confidence:** High on the durable concepts (the NISQ depth-vs-coherence contract, algorithm-family taxonomy, error mitigation vs correction, the surface-code/threshold framing, the hybrid quantum-classical loop, simulators-first, shots-as-statistics); **Medium-to-Low on any specific hardware number — qubit counts, fidelities, coherence times, threshold figures, and the SDK/provider map move MONTHLY. Every such claim below carries a retrieval date + [verify-at-use] and MUST be re-verified before use.**
> The reference the `quantum-algorithm-engineer` reads when building and running circuits: the NISQ reality, the algorithm families and which regime they need, error mitigation and correction, the hybrid loop, execution/access, and the honest hype check — plus a dated 2026 landscape snapshot.

The team's discipline: **on NISQ, depth is the enemy (no error correction); pick the algorithm family to the regime; mitigate but don't call it correction; run the classical loop where the real work is; prove it on a simulator before a QPU; budget shots for the statistical error; benchmark against a reference; and be relentlessly honest that quantum advantage is narrow and mostly unproven for business problems.**

---

## The reality check — quantum advantage is narrow and, for most business problems, unproven

Read this first, because the field is hype-heavy:

- **Most enterprise problems have no quantum advantage today.** A *proven* asymptotic speedup exists for a *small* set of problems (factoring, some simulation/chemistry, certain search/linear-algebra) — **not** generic optimization, analytics, or most ML. The triage default is "classical wins today."
- **The advantage must be over the BEST classical method.** Many "quantum beats classical" claims use a weak classical baseline. Simulated/parallel-tempering annealing, Gurobi, and specialized heuristics are strong; QAOA/annealing rarely beats them at useful sizes.
- **State preparation can eat the whole speedup.** An exponentially faster algorithm behind an exponential-cost data-load has no net advantage — always check the I/O.
- **NISQ demonstrations ≠ practical advantage.** "Quantum utility" experiments are real science but rarely a defensible, cost-effective win over classical for a business task.
- **Fault-tolerant algorithms are not near.** Shor/HHL/QPE need error correction that today's hardware cannot do — treat them as roadmap, not product.

---

## The NISQ contract — depth is the enemy

Today's machines are **NISQ**: Noisy, Intermediate-Scale (roughly tens to low-thousands of *physical* qubits — _2026-07-14, [verify-at-use]_), and **without error correction**. The governing invariant:

| Constraint | Why | Do instead |
|---|---|---|
| **Every gate injects error** | No error correction catches it on NISQ | Use the **shallowest** circuit that expresses the algorithm |
| **Circuit depth ≤ coherence budget** | Qubits decohere over time; a too-deep circuit returns noise | Cap depth; reduce ansatz; better qubit mapping |
| **Two-qubit gates dominate error** | They're noisier than single-qubit gates | Minimize entangling gates and **SWAP** overhead from routing |
| **No mid-circuit fixes** | Mitigation is post-hoc, not corrective | Design for the noise, then mitigate the estimate |

**Depth vs coherence is the budget you spend.** A logically-correct circuit that transpiles too deep for the device's coherence time produces noise, and **no amount of error mitigation recovers it** — that's a fault-tolerance need.

---

## Algorithm families — which regime each needs

| Family | Algorithm | Regime | What it's for | Honest status _(2026-07-14, verify-at-use)_ |
|---|---|---|---|---|
| **Fault-tolerant** | **Shor** | FT | Integer factoring (breaks RSA) | Proven exponential advantage; **not practical yet** — needs many logical qubits |
| | **Grover** | FT (useful sizes) | Unstructured search | Quadratic speedup; overhead makes small-scale gains marginal |
| | **HHL** | FT | Linear systems | Exponential *caveated* speedup; **state-prep + readout often kill it** |
| | **QPE** (quantum phase estimation) | FT | Eigenvalues / precise energies | The FT chemistry workhorse; needs deep coherent circuits |
| **NISQ** | **VQE** | NISQ | Molecular ground-state energies | Shallow variational; advantage over the best classical **unproven** |
| | **QAOA** | NISQ | Combinatorial optimization (QUBO) | Variational; rarely beats strong classical solvers at useful sizes |
| | **Quantum kernels / QML** | NISQ | Machine-learning feature maps | Active research; defensible advantage **largely unproven** |

**The dividing line:** the algorithms with *proven exponential* advantage (Shor, HHL, QPE) are **fault-tolerant** and not practical yet; the algorithms that *run today* (VQE, QAOA, quantum kernels) are **NISQ variational** with **unproven** advantage. That tension is the honest center of the field.

---

## Circuit engineering — qubits, gates, depth, transpilation

- **A circuit is qubits + gates + measurement.** A universal **gate set** = single-qubit rotations + one entangling (two-qubit) gate; everything decomposes to the backend's **native** set.
- **Depth** = the longest gate path; it's the coherence-budget spend. **Two-qubit-gate count** is the dominant error driver.
- **Transpilation** maps a logical circuit to a real device: decompose to native gates + **route** to the device **connectivity**. Non-adjacent two-qubit gates need **SWAP** insertions that deepen the circuit — **all-to-all** (trapped-ion) needs far fewer than a **fixed lattice** (superconducting). Always report the **transpiled** depth/2-qubit count, not the logical one.
- **Shots / sampling:** a quantum computer is sampled; an expectation value is estimated from many measurement **shots**, with statistical error ∝ **1/√shots**. Quote the shot count and the error bar.

---

## Error mitigation (NISQ) — reduce bias, at a variance cost

Mitigation reduces *bias in an estimate*; it does **not** correct the computation. Match the technique to the error:

- **Measurement-error mitigation** — characterize the readout assignment/confusion matrix and invert it. Cheap; almost always worth it.
- **Zero-noise extrapolation (ZNE)** — run at amplified noise (gate folding / stretched pulses), extrapolate the expectation value to the zero-noise limit. General-purpose; moderate cost.
- **Probabilistic error cancellation (PEC)** — sample a quasi-probability decomposition of the inverse noise channel (needs a characterized noise model). Higher accuracy, **steep sampling/variance overhead**.
- **Dynamical decoupling** — insert idle-time pulse sequences to suppress decoherence on idling qubits. Cheap; complements the others.

All of these **trade shots/variance for less bias** and **break down past a depth threshold** — beyond it, you need error *correction*.

---

## Error correction (fault-tolerant) — the future, and why it's far

- **Logical vs physical qubits:** a **logical** qubit is encoded across **many physical** qubits so errors can be detected and corrected via redundancy + syndrome measurement.
- **Surface code:** the leading error-correcting code — a 2D lattice of physical qubits realizing one logical qubit; the **physical-per-logical overhead is large** (many physical qubits per logical qubit — _figures verify-at-use_).
- **The threshold theorem:** error correction only *helps* once physical error rates are **below a threshold**; above it, adding qubits makes things worse. Beating the threshold with enough qubits at scale is the core unsolved engineering problem.
- **Why FT is far:** running Shor/HHL/QPE on useful problems needs **many** logical qubits × a **large** physical overhead = physical-qubit counts far beyond today's — hence "not practical yet." _(2026-07-14, verify-at-use.)_

---

## The hybrid quantum-classical loop — where the real engineering is

Variational algorithms (VQE, QAOA, QML) are a **classical optimizer wrapped around a parameterized quantum circuit**:

1. Prepare a **parameterized ansatz** (angles θ). Watch **barren plateaus** — over-deep/over-parameterized ansätze have vanishing gradients and won't train.
2. Measure the **cost** (an expectation value estimated from shots).
3. A **classical optimizer** updates θ — **SPSA** (robust to shot noise), COBYLA, or gradient-based (Adam) using the **parameter-shift rule** for gradients.
4. Repeat to convergence, managing the **measurement/shot budget** (most of the wall-clock and cost).

**Most of the engineering effort is the classical loop** — the quantum circuit is small; the optimizer, gradients, shot budgeting, and convergence are where the work and the bugs live.

---

## Execution & access — simulators first, then QPU

- **Statevector simulator** — exact, free bug-catching, up to **~30ish qubits** (memory doubles per qubit). Always the first target.
- **Noise-model simulator** — previews real-device behavior before spending QPU time.
- **QPU** — the real run, via cloud SDKs: **Qiskit / Qiskit Runtime** (IBM), **Cirq** (Google), **PennyLane** (hybrid/differentiable, hardware-agnostic), **Amazon Braket** (multi-provider access). Expect **queue latency** and **per-shot cost**; calibration drifts between runs.
- **Rule:** prove the circuit on a simulator first — a bug found on a statevector sim is free; the same bug after a queued, paid QPU run is expensive and slow. _(SDK/provider surface: 2026-07-14, verify-at-use.)_

---

## Benchmarking — a quantum result is not trusted until measured

- Compare against an **exact/statevector reference** (or a smaller tractable instance, or a known analytic value).
- Report the **shots**, the **statistical error bar**, the **residual bias** (mitigated vs exact), and **whether mitigation actually helped** (sometimes it doesn't — say so).
- "It ran on hardware" proves nothing about correctness — a result needs an **error bar and a reference**.

---

## 2026 landscape snapshot (dated — volatile, re-verify before quoting)

- **SDKs / access:** **Qiskit / Qiskit Runtime** (IBM), **Cirq** (Google), **PennyLane** (Xanadu; differentiable, hardware-agnostic hybrid), **Amazon Braket** (multi-provider). _(Retrieved 2026-07-14 — [verify-at-use].)_
- **Modalities & example vendors:** superconducting (IBM, Google, Rigetti), trapped-ion (IonQ, Quantinuum), neutral-atom (QuEra, Pasqal), photonic (PsiQuantum, Xanadu). **Vendor positioning and qubit/fidelity numbers change monthly.** _(Retrieved 2026-07-14 — [verify-at-use].)_
- **Scale:** NISQ devices span roughly tens to low-thousands of *physical* qubits with no error correction; fault-tolerant machines with useful *logical* qubit counts are not yet available. **Treat every count as a snapshot.** _(Retrieved 2026-07-14 — [verify-at-use].)_

---

## Provenance

- Durable concepts (the NISQ depth-vs-coherence contract, the fault-tolerant vs NISQ algorithm-family split, transpilation/SWAP/native-gate framing, shots-as-1/√N statistics, error mitigation — ZNE/PEC/measurement-mitigation/dynamical-decoupling — vs error correction, logical-vs-physical qubits + surface code + threshold theorem, the hybrid quantum-classical loop and barren plateaus, simulators-first, benchmark-against-a-reference, and the quantum-advantage-is-narrow honesty check) are consensus practice across the quantum-computing literature, reviewed 2026-07-14 — **High confidence**.
- All specific hardware figures — qubit counts, gate fidelities, coherence times, error-correction thresholds and overheads, vendor positioning, and the SDK/provider map — are a **2026-07-14 snapshot and volatile**; they carry retrieval dates and **[verify-at-use]** throughout and must be re-verified with `ravenclaude-core/deep-researcher` before pinning in a deliverable. _(Retrieved 2026-07-14.)_
