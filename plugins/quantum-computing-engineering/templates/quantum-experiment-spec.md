# Quantum experiment spec — <algorithm / experiment name>

> The one-page spec captured **before** building and running a circuit, for a problem that
> already passed [`quantum-use-case-assessment.md`](quantum-use-case-assessment.md).
> The order matters: **circuit → transpilation → depth-vs-coherence → hybrid loop → mitigation → execution → benchmark.**
> A quantum result is **not done** until the benchmark row is green with an error bar and a reference.

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Algorithm:** <VQE / QAOA / quantum kernel / Grover / QPE / sampling> · **Status:** draft / running / benchmarked · **Last reviewed / verify-at-use:** <YYYY-MM-DD — backend/qubit/fidelity claims are volatile>

## Goal & algorithm
- **What this computes:** <one line — e.g. ground-state energy of H2 / MaxCut on graph G>
- **Algorithm family:** <VQE / QAOA / quantum kernel / Grover / QPE / sampling> · **Regime:** <NISQ (mitigation only) / fault-tolerant (future)>
- **Success criterion:** <target accuracy + the reference it's measured against>

## Circuit design
- **Qubits:** <count> · **Native/logical gate set:** <gates> · **Measurement:** <basis / observables>
- **Ansatz / oracle / feature-map:** <hardware-efficient / UCCSD / QAOA cost+mixer (p=?) / oracle> — **barren-plateau risk:** <note>
- **Logical depth & two-qubit-gate count:** <values>

## Transpilation (to the real device)
- **Target backend:** <modality · connectivity · native gates> _(verify-at-use)_
- **Routing / SWAP overhead:** <all-to-all → few SWAPs · fixed lattice → SWAP chains>
- **TRANSPILED depth & two-qubit count:** <values — NOT the logical ones> · **Optimizer level:** <0–3>
- **Depth vs coherence budget:** <fits / overruns — if overruns, shrink ansatz or re-triage>

## Hybrid quantum-classical loop (variational only)
- **Classical optimizer:** <SPSA / COBYLA / Adam> · **Gradient method:** <parameter-shift / gradient-free>
- **Cost function:** <expectation value from shots> · **Convergence / measurement budget:** <note>

## Error mitigation (NISQ — NOT correction)
| Technique | For which error | Applied? | Cost |
|---|---|---|---|
| Measurement-error mitigation | readout error | yes / no | cheap |
| Zero-noise extrapolation (ZNE) | gate error | yes / no | moderate variance |
| Probabilistic error cancellation (PEC) | gate error (needs noise model) | yes / no | steep variance |
| Dynamical decoupling | idle decoherence | yes / no | cheap |

## Execution (simulators FIRST)
- **Statevector sim:** <ran? exact result> · **Noise-model sim:** <ran? previewed behavior>
- **QPU:** <backend (Qiskit-Runtime / Cirq / PennyLane / Braket) · shots · queue/cost> _(verify-at-use)_
- **Shots for target statistical error:** <count — error ∝ 1/√shots, budgeted for the MITIGATED estimator>

## Benchmark (numbers, not "it ran")
| Measurement | Reference | Raw | Mitigated | Error bar | Pass? |
|---|---|---|---|---|---|
| <e.g. ground-state energy> | <exact / statevector> | <value> | <value> | <±> | ☐ |
| **Did mitigation actually help?** | | | | <yes/no> | ☐ |

## Seams (not this team)
- **Post-quantum crypto (defense):** security-engineering / cybersecurity-grc · **Classical ML:** ml-engineering · **Control HW/cryo:** hardware-electronics-engineering · **HPC simulation:** performance-engineering

## Open issues / follow-ups
- <list>

**Signed off:** <reviewer> · <date>
