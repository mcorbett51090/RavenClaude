# Quantum use-case assessment — <problem / initiative name>

> The one-page triage captured **before** any quantum build. This is the gate: most
> problems should exit here with **"classical wins today."** Pairs with
> [`quantum-experiment-spec.md`](quantum-experiment-spec.md) (used only for problems that survive triage).

**Owner:** <name> · **Date:** <YYYY-MM-DD> · **Verdict:** classical-wins-today / quantum-candidate / needs-fault-tolerance-(future) · **Last reviewed / verify-at-use:** <YYYY-MM-DD — every hardware/SDK claim below is volatile>

## Problem & classical baseline
- **What we want to solve:** <one line>
- **Workload type:** <combinatorial optimization / quantum chemistry / linear systems / factoring / search / ML / sampling>
- **Problem size:** <variables · qubits it would need>
- **Best classical method it must beat:** <e.g. Gurobi / OR-Tools / simulated annealing / DFT / a specialized heuristic> — **and does quantum actually beat it?** <yes/no/unknown>

## The triage gate (ALL three must be "yes" to proceed)
| # | Killer question | Answer | Evidence |
|---|---|---|---|
| a | **Proven advantage?** Is there a known quantum algorithm with a proven asymptotic advantage for THIS problem? | yes / no | <algorithm / theorem, or "none">|
| b | **Size in the advantage regime?** Does the advantage appear at a problem size reachable on real hardware? | yes / no | <regime note> |
| c | **State-prep affordable?** Is the data-loading / state-prep cost smaller than the speedup? | yes / no | <I/O cost note> |

> **Any "no" → verdict: CLASSICAL WINS TODAY.** Record the classical recommendation and stop here. This is the correct, valuable outcome for most enterprise asks.

## If it survives — the quantum approach
- **Paradigm:** <gate/circuit · quantum annealing · measurement-based> — **why:** <decision-tree leaf>
- **Qubit modality (trade-off):** <superconducting / trapped-ion / neutral-atom / photonic> — **what it buys / costs here:** <fidelity·connectivity·speed·scale> _(specifics verify-at-use)_
- **NISQ vs fault-tolerant:** <NISQ-doable (mitigation only) · needs-FT (not practical yet)> — **why:** <does the algorithm need error correction?>
- **Resource estimate (order-of-magnitude):** <physical qubits · logical qubits if FT · depth vs coherence · shots> _(dated · verify-at-use)_
- **SDK / provider:** <Qiskit-Runtime / Cirq / PennyLane / Braket · backend family> · **simulators-first plan:** <statevector + noise model before any QPU>

## Seams (not this team)
- **Post-quantum cryptography migration (the DEFENSE):** security-engineering / cybersecurity-grc
- **Classical ML / MLOps:** ml-engineering
- **Control electronics / cryogenics / the board:** hardware-electronics-engineering
- **Large-scale classical simulation / HPC:** performance-engineering

## Flip conditions
- <the 1-2 facts — usually a hardware milestone — that would change this verdict, e.g. "if a device with N logical FT qubits and a demonstrated advantage ships, re-triage">

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
