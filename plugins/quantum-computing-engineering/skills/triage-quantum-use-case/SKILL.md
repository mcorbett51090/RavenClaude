---
name: triage-quantum-use-case
description: "Decide whether a problem should use quantum computing at all — and if so, which paradigm, qubit modality, NISQ-vs-fault-tolerant placement, SDK/provider, and resource estimate — by traversing the quantum triage decision tree (classical-vs-quantum gate → paradigm → modality → NISQ-vs-FT → SDK/provider), returning a go/no-go verdict that defaults to 'classical wins today' unless a proven advantage, an in-regime problem size, and an affordable state-prep cost all hold. Reach for this when the user asks 'should we solve this with quantum?', 'gate-model or annealing?', 'which qubit hardware?', 'is this NISQ-doable or does it need fault tolerance?', or 'Qiskit/Cirq/PennyLane/Braket?'. Used by `quantum-solutions-architect` (primary)."
---

# Skill: triage-quantum-use-case

> **Invoked by:** `quantum-solutions-architect` (primary). Also consulted by `quantum-algorithm-engineer` when a build reveals the problem can't fit the depth/coherence budget and needs a re-triage.
>
> **When to invoke:** "should we use a quantum computer for this?"; "gate-model or annealing?"; "which qubit modality?"; "is this NISQ-doable or does it need fault tolerance?"; "how many qubits would this take?"; "Qiskit / Cirq / PennyLane / Braket — and whose hardware?"; any "is this a quantum problem, and how would we approach it?" question.
>
> **Output:** a go/no-go triage verdict (defaulting to "classical wins today") + IF it survives: the paradigm + qubit modality + NISQ-vs-FT placement + order-of-magnitude resource estimate + SDK/provider + the flip conditions — every volatile fact dated and marked verify-at-use.

## Procedure

1. **Restate the problem in the tree's terms.** Capture: the **workload** (combinatorial optimization / quantum chemistry / linear systems / factoring-cryptanalysis / search / machine learning / sampling), the **problem size** (variables, qubits it would need), the **data-loading shape** (does the algorithm need a large classical dataset loaded into a quantum state?), and the **best classical method** it would have to beat.
2. **Run the triage gate FIRST — this is the whole point.** Three killer questions, all must be "yes" to proceed:
   - **(a) Proven advantage?** Is there a *known quantum algorithm* with a proven asymptotic advantage for *this* problem (not a hope, a theorem)? Chemistry/simulation and factoring have one; generic business optimization mostly does not.
   - **(b) Size in the advantage regime?** Does the advantage appear at problem sizes reachable on real hardware, or only asymptotically at qubit counts that don't exist? Many advantages are "someday," not "now."
   - **(c) State-prep affordable?** Does loading the classical data into a quantum state (state preparation) cost *less* than the speedup buys? An exponential algorithm behind an exponential data-load has **no** advantage.
   - **If any answer is no → verdict: "classical wins today — revisit as hardware matures."** Say it plainly and name the classical baseline. Most enterprise asks end here, and that is the correct, valuable outcome.
3. **Only if it survives, choose the paradigm.** Traverse [`../../knowledge/quantum-computing-decision-tree.md`](../../knowledge/quantum-computing-decision-tree.md): QUBO/Ising optimization → **quantum annealing** *or* gate-model **QAOA** (and still check classical solvers first); universal algorithms (chemistry, factoring, HHL, search) → **gate/circuit model**; specific photonic/cluster-state schemes → **measurement-based**.
4. **Choose the qubit modality as a trade-off.** Superconducting (fast gates, short coherence), trapped-ion (high fidelity, all-to-all, slower), neutral-atom (reconfigurable, scaling), photonic (room-temp, networking, probabilistic gates). Frame fidelity-vs-connectivity-vs-speed-vs-scale for *this* workload; **mark specific qubit counts/fidelities verify-at-use.**
5. **Place it on the NISQ-vs-fault-tolerant timeline honestly.** Needs error correction (Shor / HHL / QPE) → **fault-tolerant → not practical yet**; shallow variational (VQE / QAOA / quantum kernels) → **NISQ-doable with error mitigation only**. Name the physical-vs-logical qubit distinction and the surface-code overhead if FT.
6. **Estimate resources at order-of-magnitude.** Physical (and logical, if FT) qubit count, circuit depth vs coherence budget, shots for the target statistical error. Often the estimate *is* the verdict ("needs millions of physical qubits" = no-go today).
7. **Select the SDK/provider and demand simulators first.** Qiskit/Qiskit Runtime (IBM), Cirq (Google), PennyLane (hybrid/differentiable, hardware-agnostic), Braket (multi-provider). Prove on a **simulator** before any QPU spend. Name the queue/cost reality.
8. **State the flip conditions** — usually a hardware milestone (e.g., "if a device with N logical fault-tolerant qubits ships, this no-go becomes a go"). Date every volatile claim.

## Worked example

> User: "We want to optimize our delivery-truck routing with a quantum computer. QAOA on a real QPU — which one?"

- **Workload:** combinatorial optimization (vehicle routing / a QUBO). **Best classical baseline:** mature solvers — Gurobi/OR-Tools, LKH, simulated/parallel-tempering annealing — that solve industrial routing at scale *today*.
- **Triage gate:** (a) proven advantage? **No** — QAOA has *no* proven asymptotic advantage over the best classical heuristics for generic routing. (b) size in regime? The instances that matter need far more clean qubits than NISQ offers. (c) state-prep? The QUBO encoding is large and the results are noise-dominated at useful sizes.
- **Verdict: CLASSICAL WINS TODAY.** Recommend a classical solver now; revisit QAOA only as a research track, not a production plan. This is the honest, valuable answer — the team saves the QPU budget.
- **Flip condition:** if fault-tolerant hardware with thousands of logical qubits and a demonstrated routing advantage over the best classical solver appears, re-triage. **(Every hardware claim here is dated and verify-at-use.)**

## Guardrails

- **Run the triage gate before anything else** — never brand-match a quantum solution to a request that classical wins. "Classical wins today" is the default, not a cop-out.
- **Compare against the BEST classical method, not a strawman.** An advantage over a weak baseline is not an advantage.
- **Always check the state-preparation cost** — an exponential speedup behind an exponential data-load is no speedup.
- **NISQ ≠ fault-tolerant.** Don't place a Shor/HHL/QPE problem as if today's hardware could run it; say "not practical yet."
- **Modalities are trade-offs, not winners** — name what each buys and costs for the workload.
- **Post-quantum *cryptography* migration is NOT this skill** — that's the defensive switch to quantum-resistant algorithms → route to `security-engineering` / `cybersecurity-grc`.
- Every qubit count, fidelity, coherence time, and SDK/provider fact carries a **retrieval date + [verify-at-use]** — this landscape moves monthly. See [`../../knowledge/quantum-computing-patterns-2026.md`](../../knowledge/quantum-computing-patterns-2026.md).
