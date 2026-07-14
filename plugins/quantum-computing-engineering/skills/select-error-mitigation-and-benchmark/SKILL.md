---
name: select-error-mitigation-and-benchmark
description: "Select NISQ error-mitigation techniques for a noisy circuit and benchmark the result honestly — zero-noise extrapolation, probabilistic error cancellation, measurement-error mitigation, dynamical decoupling (mitigation, NOT the error correction fault tolerance will provide), the shots for a target statistical error, and a benchmark against an exact/simulated reference with the residual bias/variance quantified. Reach for this when the user asks 'the results are noisy — can I trust them?', 'which error mitigation?', 'how many shots?', or 'benchmark this vs the exact answer'. Used by `quantum-algorithm-engineer` (primary)."
---

# Skill: select-error-mitigation-and-benchmark

> **Invoked by:** `quantum-algorithm-engineer` (primary). Also consulted by `quantum-solutions-architect` to confirm mitigation can plausibly rescue a NISQ result before promising a usable answer.
>
> **When to invoke:** "the results are noisy — can I trust them?"; "which error mitigation should I use?"; "how many shots do I need?"; "benchmark this against the exact / simulated answer"; "did mitigation actually help?"; any "make this noisy quantum result trustworthy and prove it" question.
>
> **Output:** an error-mitigation plan (ZNE / PEC / measurement-mitigation / dynamical-decoupling — explicitly *not* correction), the shot budget for the target statistical error, and a benchmark vs an exact/simulated reference with the residual bias/variance and whether mitigation improved the estimate.

## Procedure

1. **Restate the noise situation.** Capture: the **quantity being estimated** (an expectation value, a bitstring distribution, a ground-state energy), the **dominant error sources** (gate error, readout/measurement error, decoherence over the circuit depth), and the **target accuracy** the result must hit to be useful.
2. **Confirm this is MITIGATION, not correction.** State plainly: NISQ has **no error correction** — you are *reducing bias in the estimate*, not making the computation fault-tolerant. Mitigation trades **more shots/variance** for **less bias**; it does not scale to arbitrary-depth circuits.
3. **Select the mitigation technique(s) to the error**, per [`../../knowledge/quantum-computing-patterns-2026.md`](../../knowledge/quantum-computing-patterns-2026.md):
   - **Measurement-error mitigation** — for readout error; characterize the assignment/confusion matrix and invert it. Cheap, almost always worth it.
   - **Zero-noise extrapolation (ZNE)** — for gate error; run the circuit at amplified noise levels (gate folding / stretched pulses) and extrapolate the expectation value back to the zero-noise limit. Moderate cost, general-purpose.
   - **Probabilistic error cancellation (PEC)** — for gate error with a characterized noise model; sample a quasi-probability decomposition of the inverse noise. Higher accuracy but a **steep sampling-overhead** (variance) cost.
   - **Dynamical decoupling** — insert idle-time pulse sequences to suppress decoherence on idling qubits. Cheap, complements the above.
4. **Set the shot budget for the target statistical error.** Sampling error on an expectation value falls as **1/√shots**; mitigation (especially PEC/ZNE) *inflates* the variance, so budget shots for the *mitigated* estimator's error bar, not the raw one.
5. **Benchmark against a reference — this is non-negotiable.** Compare the (mitigated) result to an **exact/statevector simulation** where the size allows, or a smaller tractable instance, or a known analytic value. Report the **residual bias** (mitigated vs exact) and the **variance/error bar**, and state **whether mitigation actually improved** the estimate (sometimes it doesn't — say so).
6. **Report simulators-first provenance and cost.** Note that the reference came from a simulator and that the QPU run's shots/queue/cost were budgeted; a result without an error bar and a reference is not a result.
7. **State the flip conditions** — e.g., "beyond depth D no mitigation recovers the signal; this needs fault-tolerant hardware," or "if readout error dominates, measurement mitigation alone suffices and ZNE/PEC aren't worth their variance cost."

## Worked example

> User: "My VQE ground-state energy is off from the known value and noisy. What mitigation, how many shots, and how do I know it's better?"

- **Quantity:** a ground-state **energy** (expectation value of a Hamiltonian). **Errors:** readout error on the Pauli-term measurements + gate error accumulating over the ansatz depth.
- **Mitigation stack:** start with **measurement-error mitigation** (cheap, corrects readout bias on every Pauli term), add **ZNE** for the gate error (amplify noise, extrapolate the energy to zero-noise), and **dynamical decoupling** on idling qubits. Hold **PEC** in reserve — its variance cost may not be worth it here.
- **Shots:** budget per-term shots so the *ZNE-extrapolated* energy's error bar is below chemical-accuracy-scale target; ZNE inflates variance, so more shots than the raw estimate.
- **Benchmark:** compute the **exact** ground-state energy by statevector diagonalization for this (small) Hamiltonian; report **raw vs mitigated vs exact** with error bars, and confirm the mitigated energy is *closer to exact with an acceptable error bar* — if it isn't, mitigation didn't help and you say so.
- **Flip condition:** if the ansatz is too deep for the coherence budget, no amount of mitigation recovers the energy — kick back to `design-and-transpile-quantum-circuit` to shrink the circuit.

## Guardrails

- **Mitigation is NOT correction** — say it explicitly; you reduce bias at a variance cost, you do not make NISQ fault-tolerant.
- **Match the technique to the error** — measurement mitigation for readout, ZNE/PEC for gate error, dynamical decoupling for idle decoherence; don't pay PEC's variance cost when readout mitigation suffices.
- **Budget shots for the MITIGATED estimator** — ZNE/PEC inflate variance; the raw-estimator shot count is too low.
- **Always benchmark against an exact/simulated reference** — a hardware number without an error bar and a reference is not a result.
- **Report whether mitigation actually helped** — sometimes it doesn't move the estimate; that's a valid, honest finding.
- **Beyond a depth threshold, no mitigation saves the circuit** — that's a fault-tolerance need, not a mitigation-tuning problem.
- Noise characteristics, backend calibration, and mitigation-tooling APIs are volatile — carry a **retrieval date + [verify-at-use]** and re-verify against the live backend.
