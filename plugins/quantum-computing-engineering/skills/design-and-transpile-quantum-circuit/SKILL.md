---
name: design-and-transpile-quantum-circuit
description: "Design a quantum circuit for a chosen algorithm and transpile it to a real device's topology and native gate set — qubits/gates/measurement, the VQE/QAOA/quantum-kernel ansatz, decomposition to native gates, routing to qubit connectivity with SWAP overhead, and the transpiled depth checked against the coherence budget so it stays shallow enough for NISQ. Also builds the hybrid quantum-classical optimizer loop for variational algorithms. Reach for this when the user asks 'build/transpile this circuit for <backend>', 'set up a VQE/QAOA', 'what's the depth after routing?', or 'which ansatz/optimizer?'. Used by `quantum-algorithm-engineer` (primary)."
---

# Skill: design-and-transpile-quantum-circuit

> **Invoked by:** `quantum-algorithm-engineer` (primary). Also consulted by `quantum-solutions-architect` to sanity-check that a triaged problem is expressible within the depth/coherence budget before committing to it.
>
> **When to invoke:** "design/build this circuit"; "transpile it for this backend"; "what's the depth after routing to the topology?"; "set up a VQE for this Hamiltonian / QAOA for this QUBO"; "which ansatz / classical optimizer?"; any "turn this algorithm into a runnable circuit on a real device" question.
>
> **Output:** the circuit (qubits/gates/measurement + ansatz), the transpilation to native gates + topology (SWAP overhead, transpiled depth & two-qubit count, optimization level), the depth-vs-coherence check, and — for variational algorithms — the hybrid classical-optimizer loop.

## Procedure

1. **Restate the algorithm and the target device.** Capture: the **algorithm** (VQE ground state / QAOA optimization / Grover search / QPE / a quantum kernel), the **target backend** (modality + connectivity + native gate set + coherence times, all verify-at-use), and the **depth/coherence budget** the architect placed on it.
2. **Design the logical circuit from the algorithm.** Lay out qubits, gates, and measurement: the **ansatz** for variational algorithms (hardware-efficient vs problem-inspired like UCCSD for chemistry; QAOA cost + mixer layers), the oracle for search, the phase-estimation ladder for QPE. Choose the ansatz for **expressibility *and* trainability** — deep/over-parameterized ansätze hit **barren plateaus** where gradients vanish.
3. **Keep it shallow — depth is the NISQ budget.** Count the logical two-qubit gates and depth; the shallowest circuit that expresses the algorithm wins, because every gate injects error with no correction to catch it.
4. **Transpile to the real device** (the step where circuits balloon), per [`../../knowledge/quantum-computing-patterns-2026.md`](../../knowledge/quantum-computing-patterns-2026.md):
   - **Decompose** every gate to the backend's **native gate set** (e.g. a fixed set of single-qubit rotations + one entangling gate),
   - **Route** to the device **connectivity** — each two-qubit gate on non-adjacent qubits needs **SWAP** insertions that deepen the circuit; all-to-all (trapped-ion) needs far fewer SWAPs than a fixed lattice (superconducting),
   - Pick the **transpiler optimization level** and report the resulting **transpiled depth and two-qubit-gate count** (not the logical count),
   - **Check depth vs coherence:** if the transpiled depth exceeds what the coherence time can hold, the result is noise — reduce the ansatz, change qubit mapping, or kick back to the architect for a re-triage.
5. **Build the hybrid loop for variational algorithms.** The classical **optimizer** (SPSA robust to shot noise, COBYLA, gradient-based Adam), the **gradient** method (parameter-shift rule), the **cost function** (expectation value estimated from shots), and convergence + measurement-budget management. This loop is most of the engineering.
6. **Wire it to run simulators-first.** Structure the code so it runs on a **statevector simulator** (exact) and a **noise-model** simulation before any QPU — same circuit object, different backend.
7. **Report the transpiled reality and the flip conditions.** Give the transpiled depth/2-qubit count, whether it fits coherence, and what would change it (e.g., "on an all-to-all trapped-ion backend the SWAP overhead disappears and the depth halves").

## Worked example

> User: "Set up a QAOA (p=2) for this 8-node MaxCut on a superconducting backend. What's the depth after transpilation?"

- **Circuit:** 8 qubits; QAOA with **p=2** → 2 rounds of (cost-Hamiltonian layer of ZZ rotations across the graph edges + a transverse-field mixer), plus initial Hadamards. Logical two-qubit (ZZ) gates = 2 × (number of edges).
- **Transpile to the superconducting lattice:** the ZZ interactions decompose to the native entangling gate; edges between **non-adjacent** qubits on the fixed lattice each need **SWAP** chains → the **transpiled** two-qubit count and depth are markedly higher than logical. Report both, and the transpiler optimization level.
- **Depth vs coherence:** check the transpiled depth against the device coherence budget; if p=2 already overruns it, drop to p=1 or improve the qubit mapping. **(coherence numbers verify-at-use.)**
- **Hybrid loop:** **SPSA** optimizer (robust to shot noise) over the 2×2 = 4 QAOA angles, cost = ⟨C⟩ from shots, parameter-shift gradients if a gradient optimizer is used instead.
- **Flip condition:** on an **all-to-all trapped-ion** backend the SWAP overhead vanishes and the transpiled depth drops sharply — the modality choice directly changes the depth verdict.

## Guardrails

- **Report the TRANSPILED depth and two-qubit count, never the logical one** — routing to a real topology is where circuits go to die.
- **Keep the circuit shallow** — on NISQ every gate adds uncorrected error; a circuit too deep for the coherence budget returns noise and no mitigation saves it.
- **Watch barren plateaus** — an over-deep/over-parameterized ansatz has vanishing gradients and won't train.
- **The classical loop is most of the work** for VQE/QAOA — budget the optimizer, gradients, and shots, not just the circuit.
- **Simulators first** — structure the circuit to run on a statevector then a noise-model simulator before any QPU spend.
- **Transpilation targets are device-specific and volatile** — native gate sets, connectivity, and coherence times carry a **retrieval date + [verify-at-use]**; re-verify against the live backend before committing.
