# quantum-computing-engineering

> The **quantum algorithm/software-engineering layer** for Claude Code — the team that answers *"is this even a quantum problem, and if so — which paradigm, modality, and algorithm, and how do we run it and trust the result?"* and then builds and benchmarks the circuit. Two agents: the **quantum-solutions-architect** (triages the problem — usually to *"classical wins today"* — then chooses the paradigm, qubit modality, NISQ-vs-fault-tolerant roadmap, provider/SDK, and resource estimate) and the **quantum-algorithm-engineer** (designs & transpiles circuits, builds VQE/QAOA hybrid loops, applies error mitigation, and runs/benchmarks on simulators and QPUs).

Part of the [RavenClaude](../../README.md) marketplace. Extends `ravenclaude-core`.

## The honest stance up front

**Most business problems do not need a quantum computer today.** This team's #1 discipline is **triage**, and its default verdict is *"classical wins today — revisit as hardware matures."* Quantum advantage is narrow and, for most enterprise asks, unproven against the best classical method. The most valuable thing this plugin often delivers is talking a team *out* of a hype-driven quantum project. The field also moves monthly, so every hardware/SDK/qubit-count claim carries a **retrieval date + [verify-at-use]** — this is engineering judgment, not a hardware benchmark.

## What it does

| You ask | It returns |
|---|---|
| "Should we solve this with a quantum computer?" | A go/no-go triage verdict — proven advantage? size in the regime? state-prep affordable? — usually *"classical wins today"*, said plainly, with the classical baseline named |
| "Gate-model or annealing, and which qubit hardware?" | A paradigm choice (gate/circuit · annealing · measurement-based) and a qubit-modality trade-off (superconducting / trapped-ion / neutral-atom / photonic), specifics marked verify-at-use |
| "Is this NISQ-doable or does it need fault tolerance?" | A NISQ-vs-fault-tolerant placement (VQE/QAOA run today; Shor/HHL/QPE need fault tolerance that isn't practical yet), with logical-vs-physical qubit overhead |
| "Qiskit, Cirq, PennyLane, or Braket?" | An SDK + provider recommendation with a simulators-first plan and the queue/cost reality |
| "Design and transpile this circuit for a backend." | A circuit transpiled to the device's native gates + topology, with the SWAP overhead and the *transpiled* depth vs the coherence budget |
| "Set up a VQE/QAOA hybrid loop." | A parameterized ansatz + classical-optimizer loop (SPSA/COBYLA/Adam, parameter-shift gradients), with the barren-plateau and unproven-advantage caveats |
| "The results are noisy — can I trust them?" | An error-mitigation plan (ZNE/PEC/measurement-mitigation/dynamical-decoupling — not correction), the shot budget, and a benchmark vs an exact/simulated reference with an error bar |

**Two rules it never breaks:** *triage first — classical wins by default, and quantum advantage must beat the best classical method* (not a strawman), and *a quantum result isn't done until it's benchmarked* (against an exact/simulated reference with an error bar and a shot count, not "it ran on hardware").

## What's inside

- **2 agents** — `quantum-solutions-architect` (triages the problem, then chooses paradigm, qubit modality, NISQ-vs-FT roadmap, provider/SDK, and resource estimate) and `quantum-algorithm-engineer` (designs & transpiles circuits, builds VQE/QAOA hybrid loops, applies error mitigation, and runs/benchmarks on simulators and QPUs).
- **3 skills** — `triage-quantum-use-case`, `design-and-transpile-quantum-circuit`, `select-error-mitigation-and-benchmark`.
- **2 knowledge files** — a Mermaid quantum decision tree (classical-vs-quantum triage gate → paradigm → modality → NISQ-vs-FT → SDK/provider, + trade-off tables) and a dated 2026 quantum-patterns reference (the advantage reality check, the NISQ depth-vs-coherence contract, algorithm families, transpilation, error mitigation vs correction, the surface code / logical-vs-physical qubits / threshold, the hybrid loop, execution, benchmarking, and a landscape snapshot).
- **2 templates** — a quantum use-case assessment (the triage) and a quantum experiment spec (the build & benchmark).

## Where it sits in the stack

```
quantum-computing-engineering (HERE)  →  BUILD the quantum algorithm & run it       ("is it quantum, which one, and can we trust the result?")
ml-engineering                        →  classical machine learning / MLOps         ("the classical ML")
hardware-electronics-engineering      →  the control board / cryogenics             ("the fridge and the wiring")
security-engineering / cybersec-grc   →  post-quantum CRYPTOGRAPHY migration         ("the DEFENSE against quantum")
performance-engineering               →  large-scale classical simulation / HPC     ("simulating the circuit classically")
```

This plugin is the **quantum algorithm/software layer**: it decides whether a problem is even quantum and builds/benchmarks the circuit, and stays clear of classical ML (`ml-engineering`), the physical control hardware (`hardware-electronics-engineering`), the *defensive* post-quantum-cryptography migration (`security-engineering` / `cybersecurity-grc` — a security question, not a build-quantum-algorithms one), and large-scale classical simulation (`performance-engineering`).

## Domain stance

Concept-first (the classical-vs-quantum triage gate, gate-model vs annealing vs measurement-based, the qubit-modality trade-off axes, NISQ vs fault-tolerant, logical-vs-physical qubits + surface code + threshold, circuit design & transpilation, error mitigation vs correction, the hybrid quantum-classical loop, simulators-first + shots-as-statistics, benchmarking against a reference), fluent across **Qiskit / Qiskit Runtime, Cirq, PennyLane, and Amazon Braket** and the **superconducting / trapped-ion / neutral-atom / photonic** modalities. Because the device/SDK/qubit-count landscape is volatile, every version carries a **retrieval date + [verify-at-use]** — re-verify before pinning in a client deliverable.

## Install

```shell
/plugin marketplace add mcorbett51090/RavenClaude
/plugin install quantum-computing-engineering@ravenclaude
```

Requires `ravenclaude-core@>=0.7.0`.
