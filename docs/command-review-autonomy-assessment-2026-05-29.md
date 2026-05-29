# Command review ("the Thing") as an autonomy guardrail — honest assessment, gap analysis & score (2026-05-29)

> Commissioned by Matt. Assessor: **the Claude engineer** (the `claude-app-engineering` plugin) — `agent-sdk-engineer` lens (permissions/hooks/sandboxing) reinforced by `claude-app-ops-engineer` (cost/latency/observability) and `eval-engineer` (is the judgment actually measured?). **Scored against bounded autonomy, NOT implementation-completeness.** A separate code map already found the implementation ~production-complete (9/10); this asks the harder question Matt asked: *does command review deliver bounded autonomy, and where are the gaps?*
>
> Rubric = the 7-layer bounded-autonomy model in [`autonomous-guardrails-research-2026-05-29.md`](autonomous-guardrails-research-2026-05-29.md). Every claim below is grounded in the committed code (file:line).

## 1. Verdict

Command review is an **excellent containment-and-audit layer wearing the costume of a general autonomy guardrail** — and the costume is the problem. Against Matt's actual goal it closes the **"destroying things"** failure mode with real, enforced, deterministic rigor (a category-independent hard-rule floor, a self-disable guard, fail-closed-on-error everywhere, an inline-secret egress backstop, a never-relaxable `security_deny` posture), but it **barely touches "hallucinating"** (it gates the *safety of commands*, never the *correctness of work* — no test-gate, no definition-of-done, no evidence-before-done) and **barely touches "rabbit holes"** (no hard iteration/runaway brake — only an *advisory* session-fatigue nudge). Worse for the stated goal: as shipped in this checkout it is **100% inert** — there is no `.ravenclaude/comfort-posture.yaml`, so the orchestrator short-circuits on a single `grep` and provides zero guardrail until the operator opts in. And on the layer it *does* cover, the native **`auto` permission mode** now does the containment job more cheaply and with *harder* guarantees (non-configurable 3/20 runaway brake, server-side injection probe, tool-results stripped from the classifier) than a 45–75s, up-to-4-`claude -p`-call panel can. The Thing should be **repositioned from "the autonomy guardrail" to "the domain-concern + audit + yes/no-defer layer that sits beside `auto` mode,"** and the genuinely missing layers (verification, scope, runaway brake) added as the deterministic, no-interrupt pieces they were always meant to be.

## 2. What command review IS — and is NOT

**IS:** an opt-in, per-category `PreToolUse` tribunal. When a comfort-posture category carries `thing: on`, `thing-orchestrator.sh` classifies the call (`thing-decision.py`), runs a zero-cost deterministic screen (`thing-concerns.py`: hard-rule pre-deny, self-disable guard, base64-decoded re-screen, severity routing), and for anything above the `low` tier convenes a parallel panel of up to three `claude -p` seats (Forseti/security, Mímir/correctness, Heimdall/injection) plus Thor on a split. An EDIT is re-validated against the deterministic `concerns(revised) ⊆ concerns(original) − {cited}` invariant (`revalidate`, `thing-concerns.py:267`) before it can run; non-Bash shapes coerce EDIT→DENY. Every verdict is Sága-logged under `.ravenclaude/runs/thing/`, with a permissive verdict whose audit write fails downgraded to DENY (`orchestrator:565`). It fails closed on essentially every internal error path. Routing, the screen, and the EDIT invariant are CI-testable with no model in the loop.

**IS NOT:** a correctness checker (never runs the project's tests/build/lint, never inspects the *result* of an edit — only whether a *command* is dangerous). A runaway brake (no hard iteration cap). A scope enforcer (no SPEC/diff-budget gate). A blast-radius sandbox (a permission gate, not OS isolation). And, as shipped here, **not active at all** — a capability that is off until configured.

## 3. Coverage matrix — 7 bounded-autonomy layers × command review

| # | Layer | Coverage | Code-grounded justification |
|---|---|---|---|
| 1 | **Permission rules (deny floor)** | **Covered (but separate)** | The hard floor lives in `.claude/settings.json` `deny[]` (force-push, `rm -rf`, publish, secret reads) — enforced by Claude Code, not the Thing. The Thing complements it: `screen_always` (`thing-concerns.py:305`) re-denies force-push/`curl\|sh` **category-independently**, even if the command routes to an untoggled category. A hook `allow` cannot loosen a settings `deny` (`orchestrator:16`). |
| 2 | **Permission mode (incl. native `auto`)** | **Not covered / orthogonal** | The Thing is a hook, not a mode. Nothing in the code reads or composes with `permission_mode`; no interaction with `auto`'s classifier, 3/20 brake, or injection probe. This is the redundancy axis (§5). |
| 3 | **Hooks (deterministic enforcement)** | **Covered — its native layer** | The Thing *is* a `PreToolUse` deny/`modifiedInput` hook with an LLM "agent"-type gate inside it — exactly the research doc's Layer 3 pattern. EDIT → `emit_edit` with `updatedInput.command` (`orchestrator:54`). **But the Stop-hook definition-of-done gate is absent:** `remind-tests.sh` is the only Stop hook and it is `exit 0` advisory (`remind-tests.sh:40`) — it prints a reminder, never `block`s the turn. |
| 4 | **OS sandbox / blast-radius** | **Not covered** | No Seatbelt/bubblewrap, no `denyWrite`/`denyRead`, no worktree isolation, no `autoAllowBashIfSandboxed`. An injected or mis-allowed command runs with full host privilege. The research doc's strongest containment property ("the OS enforces the boundary regardless of what the model chose to run") is unaddressed. |
| 5 | **Anti-hallucination & anti-rabbit-hole** | **Not covered (headline gap)** | The EDIT invariant only proves a *rewritten command is not more dangerous than the original* (`thing-concerns.py:267-299`) — nothing about whether the work is correct. No test-gating, no evidence-before-done, no adversarial fresh-context diff review, no `/goal` re-check. The seats review *command/payload text*, never the result of executing it. For rabbit-holes the only mechanism is `fatigue_threshold` — **advisory only** (`orchestrator:512-525`): it appends a nudge string and does nothing else. **No hard iteration cap anywhere.** |
| 6 | **Scope confinement** | **Partial, indirect** | Seats *may* cite `xc.scope-too-broad`/`xc.outside-project-tree` (`thing-seat.sh:155`); `_path_scope` (`thing-decision.py:265`) routes out-of-project edits to a stricter tier. But no SPEC.md ingestion, no "in-scope vs out-of-scope for *this task*," no subagent `tools:` allowlisting. Bounds *where* a command writes, not *whether the change is in the task's scope*. |
| 7 | **Observability / checkpoints / rollback** | **Covered (logging) / Not covered (rollback)** | Strong audit: per-verdict Sága JSON with per-seat verdicts, confidence, citations, injection flags, duration (`orchestrator:531-560`); audit-or-deny. **But** bespoke JSON, not OpenTelemetry — no traces/metrics to a collector. No checkpoint/`/rewind` integration, no commit-per-step. Rollback relies entirely on the operator's git hygiene, which the Thing neither enforces nor encourages. |

## 4. Gap analysis — Matt's three failure modes

| Failure mode | Status | Severity | Justification |
|---|---|---|---|
| **Destroying things** (containment) | **Largely closed** | **Low residual** | The Thing's strength. Deny floor + category-independent `always_screen` hard rules + `xc.tribunal-self-disable` (file-shape + hardlink defeat, `thing-decision.py:560`) + critical-concern veto on ALLOW (`orchestrator:490`) + egress secret backstop (`thing-seat.sh:81-103`) + fail-closed-everywhere + high-blast-always-surfaces (`orchestrator:502`) = a tight, mostly-deterministic box. Residual: **no OS sandbox** (a mis-allowed command runs with full privilege) and **off-by-default**. |
| **Rabbit holes** (termination/scope) | **Open** | **High** | No hard iteration cap, no Stop-hook DoD gate, no runaway brake. `fatigue_threshold` is advisory text. An unproductive loop is reviewed command-by-command (adding latency) but **never stopped** — per-command review can actively *prolong* a rabbit hole. Native `auto`'s 3/20 brake is the only runaway protection available, and the Thing neither provides nor composes with it. |
| **Hallucinating** (verification) | **Open** | **High** | Gates command *safety*, not work *correctness*. It will ALLOW a `pytest` invocation whose failure the agent then ignores; it never sees the diff's correctness, never requires evidence, never runs an adversarial review. An `eval-engineer` red flag: **no golden set, no measured pass-rate, no before/after delta** proving the panel catches what it claims — judgment quality is asserted, not measured. (The *deterministic* pieces are gated by `audit-gates.sh`; the *LLM verdict quality* is not.) |

## 5. Scored table — fitness as a *bounded-autonomy guardrail*

Weights reflect Matt's goal (containment + the two harder failure modes + usability for *unattended* runs), not implementation polish.

| Dimension | Weight | /10 | Weighted | Rationale |
|---|---:|---:|---:|---|
| **Containment ("destroying things")** | 20 | 9 | 18.0 | Hard floor + self-disable + secret backstop + fail-closed + critical veto. −1: no OS sandbox. |
| **Runaway prevention ("rabbit holes")** | 15 | 2 | 3.0 | No hard cap; only an advisory nudge. Per-command review can *lengthen* a rabbit hole. |
| **Verification / correctness ("hallucinating")** | 18 | 2 | 3.6 | Gates command safety, never work correctness. No DoD, test-gate, diff review, evidence. EDIT invariant ≠ correctness. |
| **Scope confinement** | 8 | 4 | 3.2 | Path-scope tiering + scope concerns the seats *may* cite; no SPEC/task-scope notion. |
| **Cost/latency fitness for unattended autonomy** | 12 | 3 | 3.6 | Up to 4 `claude -p` calls, 45–75s/command. Cache exists but defaults off (TTL 0) and only helps *identical* repeats. Reads short-circuit (good); any mutate tier pays the full panel. |
| **Observability / audit** | 8 | 7 | 5.6 | Excellent bespoke Sága log + audit-or-deny. −: no OTel, no rollback/checkpoint integration. |
| **Off-by-default risk** | 10 | 2 | 2.0 | As shipped: zero guardrail until `comfort-posture.yaml` exists. The dangerous default (no gate) is the active one. |
| **Non-redundancy vs native `auto` mode** | 9 | 5 | 4.5 | Containment now substantially duplicated (and out-done) by `auto`. Unique value is real (domain concerns, yes/no defer, Sága, model diversity, EDIT-rewrite) but not *positioned* to complement `auto`. |
| **Total** | **100** | | **≈ 43.5 / 100** | |

**Headline: ~44/100 as a bounded-autonomy guardrail**, against the ~9/10 it earned for *implementation completeness*. The gap is not bugs; it's that the goal exposes three whole layers (verification, runaway brake, sandbox) the Thing never set out to cover, plus off-by-default and redundancy. As an *audit-and-containment* layer it scores in the 8s; this is deliberately the harder rubric Matt asked for.

## 6. Prioritized recommendations — turning "command review" into bounded autonomy

Ranked by leverage. **[D]** = deterministic/no-interrupt · **[H]** = interrupts-human.

1. **Add a Stop-hook definition-of-done gate. [D]** *Highest leverage; closes "hallucinating" + half of "rabbit holes."* Augment/replace the advisory `remind-tests.sh` with a Stop hook that `decision:"block"`s (or exit-2) until the project's quality gate passes (tests/build/lint → pass/fail). The research doc's Layer 5 (claimed 2–3× quality) — the mechanism that lets the loop close on its own without the human as the verification loop. The team already writes fail-closed gated hooks (the Thing); point the same discipline at *correctness*.
2. **Flip the default — ship a balanced `comfort-posture.yaml` (or wire `auto` on) so the guardrail exists out of the box. [D]** A `templates/comfort-posture-balanced.yaml` already exists; make it the default for the autonomy use-case. An inert-until-configured guardrail fails the goal's safety premise on the most common path.
3. **Adopt native `auto` mode as the containment layer; reposition the Thing on top. [D]** Let `auto`'s classifier + non-configurable 3/20 brake + injection probe + tool-results-stripping own generic containment (harder + cheaper than a 4-seat panel) — *this also delivers the missing hard runaway brake for free.* Narrow the Thing to where it's additive: **domain concerns** (the catalog — `auto` has no notion of your `srm.publish-without-tag` / MCP allowlist), **yes/no defer-routing** of `AskUserQuestion`, the **Sága audit**, **model diversity**, **EDIT-rewrite**. Stop running the panel on categories `auto` already contains.
4. **Add OS sandbox config to the autonomy posture. [D]** `autoAllowBashIfSandboxed: true`, `denyWrite` outside cwd, `denyRead:["~/.aws","~/.ssh"]`, recommend a git worktree. The containment property the Thing structurally cannot provide (permission gate, not OS isolation) and the one that survives a mislabeled/injected command. Low effort, high containment.
5. **Stop reviewing what doesn't need an LLM; make the gate usable for unattended runs. [D]** (a) Ensure reads never convene a panel (already true via the `low`-tier short-circuit — keep + document it). (b) For autonomy mode, lean on the deterministic screen + `bypass` list + a non-zero `cache_ttl_seconds` default so the expensive panel fires only on genuinely novel mutates. As-is, 45–75s/command makes the Thing unfit for the long unattended sessions that are the use-case.
6. **Add adversarial fresh-context diff review as a pre-done gate. [D, optional H]** A scoped reviewer subagent (`Read, Grep, Glob` only) sees the diff + acceptance criteria, not the reasoning that produced it. Complements #1 (tests prove behavior; the reviewer catches what tests miss). Surface to the human only on a found correctness gap.
7. **Measure the panel. [D]** *(eval-engineer)* A small golden set of {dangerous, benign, injection, scope-violating} commands with known verdicts, run as a regression gate with pinned seat models. The deterministic pieces are gated; the *LLM verdict quality* is asserted, not proven — a model swap could silently regress it.
8. **Add a SPEC/scope gate for the rabbit-hole remainder. [D]** Have the layout hook (or a new scope hook) reject writes outside a task-declared scope set, and require a SPEC.md for autonomous runs. Cheap deterministic complement: it bounds *exploration breadth* where #1 bounds *exploration depth*.

**Bottom line:** the Thing is the right *kind* of thing (deterministic-first, fail-closed, audited) built for the wrong *single* job. Keep it for domain concerns + yes/no-defer + audit; let `auto` mode own containment + the runaway brake; add the one layer nobody currently owns — a Stop-hook definition-of-done gate — to close the hallucination hole. **That combination is bounded autonomy; the Thing alone is bounded destruction.**

## 6a. Does the `design_checkins` feature cover the gaps? (addendum, 2026-05-29)

Matt asked whether the **design check-in** feature covers the hallucination + rabbit-hole gaps that command review leaves open. **Partially — but at a different layer, and in the advisory/high-touch way the goal is trying to move away from.**

`design_checkins` is a **behavioral flag** (on by default in the balanced posture), read by the Team Lead at session start (`CLAUDE.md:346`) — explicitly *"a behavioral commitment, not a machine-enforced lock."* Confirmed: **no hook enforces it** (it's wired only into the dashboard UI + the model's session-start instructions). When ON, Claude pauses for Keep/Update/Deny on structural/architectural decisions at any permission level.

| Failure mode | Design check-ins catch | Do **not** catch |
|---|---|---|
| **Rabbit-holing** | *Direction-level*: a wrong architectural path surfaced for Keep/Update/Deny before commitment. | *Execution-level*: looping/thrashing, chasing a fabricated error, infinite exploration — none are "design decisions," so the pause never fires. **No iteration cap.** |
| **Hallucinating** | A *premise* hallucination surfaced as a design choice (e.g. building on a non-existent API). | A *correctness* hallucination — code that looks done but is wrong. Check-ins confirm **intent before building**, never **results after building** (no test run, evidence, or diff review). |

Two structural problems for the goal: (1) it's the **same category of mechanism as plan mode** — advisory + human-interrupting, just fired less often — so it's "plan-mode-lite," movement *along* the high-touch axis, not off it; (2) it's **not enforced**, so it inherits the advisory-boundary fragility (lost to compaction on long runs) — unlike command review, which is a deterministic hook.

**Verdict:** a useful complement (reduces wrong-*direction* risk at decision points), **not the missing layer**. The hallucination + execution-rabbit-hole gaps are closed deterministically and without interruption by rec **#1 (Stop-hook DoD gate)** and the hard iteration cap from native `auto` (rec #3). Keep `design_checkins` as the optional "confirm the plan" layer above those; don't count it as covering the gap. If even direction-confirmation must survive long autonomous runs, promote it from an advisory flag to something a hook re-asserts.

## 7. How this maps to the build queue

The recommendations above are deliberately concrete and mostly **[D]eterministic**, so they fit the "bounded by up-front input, no per-edit babysitting" goal. Suggested sequencing for follow-up PRs: **#1 (Stop-hook DoD gate)** and **#2 (default-on posture)** first — together they convert the marketplace from "bounded destruction, opt-in" to "bounded autonomy, default" — then **#4 (sandbox posture)** and **#3 (reposition vs `auto`)**, with **#7 (measure the panel)** as the standing regression gate. These are tracked against the not-yet-implemented plans in the companion plan-reconciliation note.

## 8. Panel re-assessment under the Copilot-CLI / multi-model constraint (2026-05-29)

> **This section CORRECTS §1–§7's load-bearing error.** A two-reviewer panel (security-engineer + systems-architect) re-ran the analysis after the owner clarified the real setup: **he runs GitHub Copilot CLI, routing across Claude + ChatGPT + Grok.** Native Claude Code `auto` mode is **Anthropic-API/Claude-only** (research doc Layer 2) → **unavailable to him.** Every §6 recommendation that delegates to `auto` (esp. #3 "adopt auto for containment + the free 3/20 brake") is **invalid for his stack**; the gaps must be closed in the **portable hook layer**.

### Redundancy verdict: NOT redundant (both panelists, independently)

The §5 "redundancy vs native `auto`" penalty was an artifact of assuming a competitor the owner cannot run. Remove `auto` and the charge collapses; the strong form (from the code) is that the tribunal is the **sole provider** in his stack of: (1) a deterministic, vendor-independent catastrophe floor (`thing-concerns.py:305 screen_always` — force-push / `curl|sh` denied category-independently, pre-LLM, no model needed → runs identically under Grok/GPT/Claude); (2) the self-tamper guard (`thing-decision.py:560`, inode + parsed-YAML); (3) domain concerns + the **secret-egress backstop** (`thing-seat.sh:81-103`, denies locally before any API call); (4) **low-touch** autonomous ALLOW/EDIT/DENY disposition (the only alternative in his stack is `default` per-edit babysitting or `bypassPermissions` blank check); and (5) the Sága audit. **Unique opportunity:** the model-diversity rule (`thing-decision.py:940`) is today Claude-only (`_DIVERSITY_PREF`), but the per-seat-subprocess architecture is exactly the shape to seat **Claude + GPT + Grok** — cross-vendor anti-correlated review, the strongest anti-correlated-hallucination posture available, which single-vendor `auto` structurally cannot offer. His "limitation" is here an advantage.

### Re-score: ≈ 48–51 / 100 (panel range), up from 44 — honestly, by re-weighting, not gap-closure

| Dimension | Prior (44) | Panel | Why it moved |
|---|---|---|---|
| Non-redundancy / unique value in the stack | 5/10 | **9/10** | Inverts — `auto` unavailable; tribunal is sole provider (above). |
| Off-by-default risk | 2/10 | **5/10** | `ravenclaude setup` seeds `comfort-posture-balanced.yaml` — the real install flow is **not** inert (only a raw marketplace checkout is). |
| Low-touch security fitness (owner's stated value) | (undervalued) | **8/10** | The deterministic screen delivers silent containment with near-zero interruption — exactly what the owner praises. |
| Cost/latency | 3/10 | 4/10 | Seat fan-out could route to cheaper vendor models; reads short-circuit free. Still weakest non-gap. |
| **Runaway prevention ("rabbit holes")** | 2/10 | **2/10 (UNCHANGED)** | Still no hard brake — and the §6 escape hatch ("auto's 3/20 covers it") is **gone**, making this gap *more* urgent. |
| **Verification ("hallucinating")** | 2/10 | **2/10 (UNCHANGED)** | Still gates command safety, never work correctness. |

**The two real gaps did not move** — the score rose only because redundancy + off-by-default were mis-weighted for his actual stack. As a containment+audit+low-touch layer it scores 8–9; as a full bounded-autonomy guardrail it's low-50s with two layers unbuilt and the panel layer environmentally fragile.

### The decisive new finding (both panels, code-grounded): the Copilot bridge has NO Stop path

The Copilot installer (`scripts/ravenclaude:160-171`) wires only **SessionStart / PreToolUse / PostToolUse**; `copilot-hook-adapter.sh` has **no `stop` mode** (modes: `bash-pretool | file-pretool | sessionstart | posttool`), and the `posttool` mode **discards hook output**. The plugin's `hooks.json` Stop hook is the *Claude Code* path, which Copilot bug #2540 says doesn't fire. **Consequence:** under Copilot today, **Stop is not wired and PostToolUse cannot block** — so the "headline" Stop-hook DoD gate **does not port until the bridge is extended.** And `remind-tests.sh:40` is confirmed advisory `exit 0`, not a gate. **Sharpest risk:** the seats hard-require the `claude` CLI (`thing-seat.sh:146,240`) on Anthropic auth — in a GPT/Grok-routed Copilot session the panel may abstain entirely → high-stakes mutates deny (safe) but the *judgment layer is absent and unmeasured*. What the owner feels "helping" is almost certainly the deterministic screen, not the panel.

**Full sequenced gap-closure plan (portable hook layer) → [`command-review-gap-closure-plan-2026-05-29.md`](command-review-gap-closure-plan-2026-05-29.md).**
