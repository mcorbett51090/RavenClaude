# AR/VR/XR Engineering Plugin — Team Constitution

> Team constitution for the `ar-vr-xr-engineering` Claude Code plugin. Three specialist agents — **xr-architect-lead**, **xr-interaction-engineer**, **spatial-rendering-engineer** — plus a decision-tree knowledge bank, skills, templates, best-practices, and 2 commands, aimed at the three engines of an XR build: **system architecture** (target + engine + OpenXR + perf/comfort envelope), **interaction** (input, locomotion, 3D UI, accessibility), and **spatial rendering & performance** (frame budget, foveation, reprojection, passthrough, thermal).
>
> Designed for an XR lead, engineer, or technical director building for headsets and spatial devices who wants real judgment on the platform bet, comfort, and holding the frame — not an intro to VR.
>
> **Orientation:** this file is **domain-specific** to AR/VR/XR engineering. For the domain-neutral team constitution every plugin inherits, see [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For the meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 0. Scope & verify-at-use (read first)

This plugin ships **XR engineering judgment — not legal, medical, or safety-certification advice.** The agents:

- give architecture, interaction, and performance guidance; they do **not** certify a device or experience for medical, automotive, or safety-critical use — that goes to the appropriate authority;
- treat the **headset / runtime / engine landscape as volatile**: every device spec, OpenXR/WebXR support claim, engine version, per-eye perf number, and comfort mitigation carries a **retrieval date + `[verify-at-use]`** and must be confirmed against the vendor/runtime/engine docs before it drives a build commitment;
- store **no PII** — they work in architecture, budgets, and interaction patterns, not user data.

The dated specifics live (flagged) in [`knowledge/xr-reference-2026.md`](knowledge/xr-reference-2026.md).

---

## 1. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`xr-architect-lead`](agents/xr-architect-lead.md) | Target selection, engine choice, OpenXR strategy, perf-budget & comfort architecture | "Quest or PC-VR, Unity or Unreal?"; "support several headsets without three codebases"; "smooth in editor, drops frames on device" |
| [`xr-interaction-engineer`](agents/xr-interaction-engineer.md) | Hand/controller/gaze input, locomotion, 3D UI, grab/physics, accessibility | "playtesters get nauseous moving"; "grabbing feels floaty"; "how do I lay out a VR menu?" |
| [`spatial-rendering-engineer`](agents/spatial-rendering-engineer.md) | Frame budget, reprojection, foveated rendering, passthrough/anchors/occlusion, draw-call batching, thermal budget | "we're dropping frames — where's the time?"; "what budget for Quest standalone?"; "foveated rendering and reprojection?" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates. Per the marketplace house rule, this plugin ships specialist *doing*-agents and does not fork core's *review* roles. Team growth ships as skills + knowledge + templates, not a fourth parallel agent.

---

## 2. Routing rules (Team Lead)

- **"Target / engine / runtime / OpenXR / overall architecture / perf-budget envelope / editor-vs-device"** → `xr-architect-lead`.
- **"Input / hands / controllers / gaze / locomotion / sim-sickness / 3D UI / grab / accessibility"** → `xr-interaction-engineer`.
- **"Frame budget / dropped frames / reprojection / foveated rendering / passthrough / anchors / occlusion / draw calls / thermal"** → `spatial-rendering-engineer`.
- **Engine gameplay systems / asset pipeline beyond XR** → `game-development`.
- **WebXR inside a broader web app / bundling / hosting** → `frontend-engineering`.
- **Deep CPU/GPU/thermal profiling methodology** → `performance-engineering`.
- **General accessibility standards / WCAG-adjacent guidance** → `accessibility-engineering`.

---

## 3. Knowledge & verify-at-use

Agents **traverse the relevant decision tree before choosing** ([`knowledge/xr-decision-trees.md`](knowledge/xr-decision-trees.md)) — the target/engine/locomotion/perf-triage trees — rather than keyword-matching. The volatile device/runtime/engine/perf specifics carry a retrieval date + `[verify-at-use]` and live in [`knowledge/xr-reference-2026.md`](knowledge/xr-reference-2026.md); re-verify against vendor/runtime/engine docs before quoting or committing. This is the proactive complement to the inherited Capability Grounding Protocol.

---

## 4. House opinions (the team's standing biases)

1. **Hold the frame budget above all else.** A dropped frame is a comfort bug, not a perf nit — the per-eye budget is the top constraint.
2. **Comfort is a requirement, not a setting.** Default to the comfortable, accessible locomotion; make the intense mode opt-in.
3. **Design for the tracking volume and guardian.** The user's eyes are covered — physical safety is a design input, not an afterthought.
4. **Target OpenXR first, optimize per-device last.** The vendor-neutral core is the cheap hedge; per-device work goes behind seams.
5. **Test on device early and often.** Editor framerate is a comforting lie; the SoC and thermal envelope are the truth.
6. **Cite the source + retrieval date for every device/runtime/engine/perf specific, and flag it `[verify-at-use]`** — this landscape moves fast; quote it dated or mark `[unverified — training knowledge]`.

---

## 5. Output contract

```
Question: <what was asked, in the team's terms>
Read: <architecture / interaction / rendering read + the metric or budget and its baseline>
Decision: <the target/engine, interaction, or budget call + WHY>
Verify-at-use: <every device/runtime/engine/perf specific relied on, dated>
Recommendation: <owner + expected movement (ms recovered / comfort / reach) + by when>
Seams handed off: <xr-architect-lead / xr-interaction-engineer / spatial-rendering-engineer / game-development / frontend-engineering / performance-engineering>
```

**Plus the cross-plugin Structured Output Protocol JSON block** ([`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)).

---

## 6. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/xr-target-and-engine-selection/SKILL.md`](skills/xr-target-and-engine-selection/SKILL.md) | `xr-architect-lead` | Target class + engine + runtime choice, OpenXR-first, deriving the per-eye budget |
| [`skills/xr-interaction-and-locomotion/SKILL.md`](skills/xr-interaction-and-locomotion/SKILL.md) | `xr-interaction-engineer` | Input abstraction, comfortable locomotion, 3D UI, grab/physics |
| [`skills/spatial-rendering-and-performance/SKILL.md`](skills/spatial-rendering-and-performance/SKILL.md) | `spatial-rendering-engineer` | Per-eye budget, CPU/GPU/thermal bound, draw-call/overdraw cuts, foveation/reprojection |
| [`skills/comfort-safety-and-accessibility/SKILL.md`](skills/comfort-safety-and-accessibility/SKILL.md) | all three | Sustained framerate, comfort, guardian/play-space safety, accessibility defaults |

---

## 7. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/xr-decision-trees.md`](knowledge/xr-decision-trees.md) | Choosing a target/engine, a locomotion scheme, or triaging a frame-budget miss — the Mermaid decision trees |
| [`knowledge/xr-reference-2026.md`](knowledge/xr-reference-2026.md) | Quoting a headset/runtime/engine detail or a per-eye perf target — the dated reference (each row verify-at-use; re-confirm before quoting) |

---

## 8. Templates & commands

| Template | Use for |
|---|---|
| [`templates/xr-project-architecture.md`](templates/xr-project-architecture.md) | The target/engine/runtime decision + OpenXR-first architecture |
| [`templates/xr-perf-budget-plan.md`](templates/xr-perf-budget-plan.md) | A per-eye frame budget + ordered optimization plan |

Commands: [`/choose-xr-stack`](commands/choose-xr-stack.md), [`/plan-xr-perf-budget`](commands/plan-xr-perf-budget.md).

---

## 9. Best-practices

Five named, citable rules — see [`best-practices/README.md`](best-practices/README.md): hold the frame budget above all else, comfort is a requirement not a setting, design for the tracking volume and guardian, target OpenXR first then optimize per-device, test on device early and often.

---

## 10. Escalating out of the XR team

- **`game-development`** — engine gameplay systems, asset pipeline, and general Unity/Unreal architecture beyond the XR layer ([`../game-development/CLAUDE.md`](../game-development/CLAUDE.md)).
- **`frontend-engineering`** — WebXR delivered as part of a broader web app: bundling, hosting, browser support ([`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md)).
- **`performance-engineering`** — deep CPU/GPU/memory/thermal profiling methodology beyond the XR frame loop ([`../performance-engineering/CLAUDE.md`](../performance-engineering/CLAUDE.md)).
- **`accessibility-engineering`** — general accessibility standards and assistive-tech patterns ([`../accessibility-engineering/CLAUDE.md`](../accessibility-engineering/CLAUDE.md)).
- **`ravenclaude-core/security-reviewer`** — security/privacy verdicts (e.g. handling of any captured spatial or user data).

---

## 11. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Structured Output Protocol: [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Engine & web seams: [`../game-development/CLAUDE.md`](../game-development/CLAUDE.md), [`../frontend-engineering/CLAUDE.md`](../frontend-engineering/CLAUDE.md)
- Performance & accessibility seams: [`../performance-engineering/CLAUDE.md`](../performance-engineering/CLAUDE.md), [`../accessibility-engineering/CLAUDE.md`](../accessibility-engineering/CLAUDE.md)

---

## 12. Milestones

- **v0.1.0** — initial build-out: 3 agents (xr-architect-lead, xr-interaction-engineer, spatial-rendering-engineer), 4 skills, a decision-tree knowledge bank (4 Mermaid trees: target platform choice, engine choice, locomotion scheme to reduce sim-sickness, rendering perf-budget triage) + a dated 2026 reference (verify-at-use), 5 best-practices, 2 templates, 2 commands. Engineering judgment, not certification advice; device/runtime/engine landscape is volatile (verify-at-use); no PII. Seams to game-development, frontend-engineering, performance-engineering, and accessibility-engineering.
