> **FORGE handoff to Ultraplan** — synthesized 2026-06-23 from a cross-model two-panel review (opus architecture lens + sonnet pragmatism lens), critic + red-team, with the per-prompt-hook conflict resolved to Panel B's session-boundary-first + sticky-active-stream path. Route: `consider_ultraplan` (large, research-done), landing `pr`. Execute phase-by-phase; each phase ships its own PR + bidirectional audit-gate; the prompt-never-egresses + hook-fail-open invariants are non-negotiable. Owner: Matt (verifies + merges each PR).

# FORGE plan — Agentic Work-Streams (ravenclaude-core)

A portable way (this repo + any consumer repo) to organize streams of agentic AI work, so prompts
target the correct stream and each stream's work is trackable + crash-resumable.

## Locked requirements (Matt)
1. stream = **named logical workstream** under `.ravenclaude/streams/` (portable, spans branches/sessions).
2. **Auto-classify by prompt content**; significantly-different prompt → new stream. **Auto-infer + override.**
3. **Crash-resilient history** — resume an abruptly-terminated session from the stream.
4. **Dashboard "Streams" tab (Observe) + `rc streams` CLI.**

## Cross-model convergence (both panels agree)
- **ravenclaude-core extension**, not a new plugin (streams are domain-neutral session infra; reuse runs//dashboard/rc/_emit-event).
- **Store = registry.json (small, hot, read to classify) + per-stream history.jsonl (append-only, cold) + state.md (resume snapshot).**
- **Classifier = deterministic stdlib TF-IDF/cosine**, no deps; optional `claude -p` LLM-assist behind an off-by-default posture toggle.
- **Privacy invariant (load-bearing):** the prompt NEVER egresses; history stores derived labels/terms/word-count + summaries ONLY (NOT prompt substrings — _scrub.sh catches secrets, not free-form PII, so the stored field must be derived, never raw). Mirror the capability-banner / run-state-monitor "derived-labels-only" rule. Hook is **fail-open** (classifier error/timeout never blocks the prompt). These two are the never-regress invariants → the highest-value gate (no-prompt-egress tripwire).
- Distinct from `team-portfolio` (cross-repo GitHub rollups). Don't duplicate runs/: per-stream history carries a `session_id` FK back to `runs/<id>/`.
- Per-phase gate (bidirectional), version bump + dashboard/index/copilot regen discipline, Copilot #2540 → repo-level `.github/hooks/` via the adapter + a parity gate.

## Tiebreak verdict (the per-prompt-hook conflict) → SYNTHESIS (Panel B's path, adopted)
**Ship session-boundary classification first; per-prompt is an opt-in toggle. Always sticky.**
- `SessionStart` classifies once (branch + recent git log + stream centroids) → suggests/sets the active stream in the capability banner; user confirms/overrides with `/stream` or `rc streams set-active`. **Zero per-prompt overhead.**
- **Sticky active stream:** when `active-stream` is set, prompts are *attributed* to it; the classifier does NOT re-run per prompt. Reclassification fires only when no stream is active or the user asks. This kills the false-new-stream-spawn failure mode AND makes a future per-prompt hook a cheap `test -f` short-circuit.
- `stream_hook: session_boundary (default) | per_prompt` posture toggle; `stream_classify: off | label_only (default) | auto` — auto-switch the active stream only on explicit opt-in.
- Rationale: lower blast radius, no per-prompt latency debate, delivers the stated value (organize + track), and per-prompt mid-session switching is added only if session-boundary proves insufficient.

## Phases + DAG
- **P0** store schema + pure classifier lib (`stream-classify.py`, `stream-ops.py`) — **Gate 110** (determinism + scrub + classify-accuracy on a labeled fixture). *Universal blocker.*
- **P1** `rc streams` CLI (list/show/create/set-active/status) + `active-stream` pointer + SessionStart banner injection + Stop-hook session-close event — **Gate 111** (slug anti-traversal, read-only summary). *Delivers MVP value with zero prompt-hook.*
- **P2** SessionStart classifier wiring (sticky, label_only default) + `/stream` override command + threshold config — **Gate 112** (override round-trip + threshold bounds + sticky-no-reclassify).
- **P3** Dashboard "Streams" tab + `/__streams` endpoint in BOTH serve-dashboards.py copies (CSRF-guarded, derived-only) — **Gate 113** (render + parity + no-prompt-egress).
- **P4 (opt-in)** per-prompt `UserPromptSubmit` hook (sticky short-circuit, fail-open, latency ceiling) + Copilot `.github/hooks` parity — **Gate 114** (fail-open + no-egress + latency + Copilot parity).
- DAG: P0 → P1 → P2 → (P3 ∥ P4). P3/P4 parallelize after P2. Critical path P0→P1→P2.

## Top risks (critic + red-team, mitigations in-plan)
1. **Prompt-egress regression** (privacy) → the no-egress gate is a permanent tripwire (grep history for a distinctive prompt phrase → must be absent). HIGHEST priority.
2. **False new-stream spawns / ambiguous-short prompts** ("fix it", "continue") → sticky active stream + confidence floor + low-info prompts inherit current stream.
3. **Per-prompt latency** (P4 only) → sticky `test -f` short-circuit, hard time budget, fail-open, latency-ceiling gate.
4. **Centroid poisoning** → EMA with small α + override emits corrective adjustment.
5. **Copilot #2540** → repo-level adapter wiring + parity gate; until then Copilot gets manual `/stream` + dashboard (graceful).
6. **Two-server-copy drift** → extend Gate 32 parity.
7. **Duplicating runs//`/wrap`/`remember`** → history is derived events with a session_id FK; `/wrap` can read the active stream to enrich a scenario (additive); `remember` stays user-prefs.

## DoD
Each phase: bidirectional gate green, bash -n / ruff / prettier clean, version bump + regen, no plugin-manifest drift, the no-egress invariant proven. Core stays domain-neutral (stream names are example data only).
