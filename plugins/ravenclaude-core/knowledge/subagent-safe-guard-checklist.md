# Subagent-safe guard checklist

Work through this before shipping any `PreToolUse` guard that **records something and
reads it back**. Gate 201 (`scripts/check-guard-state-scope.py`) enforces the parts
that can be checked statically; the rest is here because it cannot be.

The failure this prevents is not a crash. It is a guard that keeps working, keeps
reporting green, and quietly denies the wrong agent.

---

## Why this exists — the measured incident

The premise ledger was keyed on `(project, session_id)`. Neither component varies
per agent. Measured against a real 6-agent parallel run:

| What was assumed | What was measured |
| --- | --- |
| one session ≈ one agent ≈ one working tree | **one `session_id` carried 14,322 transcript events across 49 distinct `cwd` values in 15+ worktrees** |
| the ledger holds this agent's probes | **2,825 entries, 50 unresolved negative families, in one file** |
| a negative blocks the agent that recorded it | a negative recorded in worktree A **denied an unrelated new module in worktree B** |

Two second-order effects, both worse than the denial itself:

- One agent **lost finished work** rather than tunnel the guard.
- One agent **wrote files through Bash heredocs** to dodge the `Write` hook entirely.

That second line is the real lesson. **A guardrail whose only exit is unreachable
does not get respected — it gets tunnelled**, and a tunnelled guard protects nothing
while still reporting that it is on.

---

## 1. State key — declare it, and make it as fine-grained as the decision

Every stateful guard carries three markers in its header. Gate 201 fails the build
without them:

```bash
# rc-state-key: <the expression the state path is keyed on>
# rc-state-scope: worktree | project | session | global
# rc-state-rationale: <why that key is right for what the guard decides>
```

**The rule:** the key must vary with *the resource the decision is about* — not
with the session, and not blindly per worktree either.

| Your guard decides about… | Scope | The key must carry |
| --- | --- | --- |
| files in one working tree | `worktree` | `cwd`, or a per-checkout digest (`PATH_KEY = sha256(toplevel)`) |
| the repo as a whole | `project` | the project root |
| this conversation's choices | `session` | `session_id` / `CLAUDE_SESSION_ID` |
| one genuinely global resource | `global` | nothing — **but the rationale must say why** |

`global` is legitimate and three of the five live guards are *not* worktree-scoped.
`guard-memory-compaction.sh` protects one memory directory that every worktree
shares; keying it per worktree would fragment the history its restore path reads.
**A blanket "must vary per worktree" rule would be wrong about most of the
population** — which is exactly why the scope is declared and then checked against
the key, rather than inferred.

> **The trap:** a key that looks per-agent but is not. `session_id` is the one that
> has actually burned this repo — it *reads* like "this agent" and is measurably
> "these fifteen worktrees."

## 2. Escape — it must be reachable from where the denial happens

A dispatched subagent hits your guard from inside a `Bash` call. Ask literally:
**can the thing that got denied perform the escape?**

- ❌ **An environment variable cannot.** A variable exported inside a `Bash` call
  never reaches the hook process. `RC_PREMISE_CONTROL` was unreachable for exactly
  this reason, and the agents tunnelled instead.
- ✅ **A file can.** A control file under the run dir, or a posture key in
  `.ravenclaude/comfort-posture.yaml`, is writable by the denied agent and leaves a
  record of who escaped and why.
- ✅ **"No escape" is a valid answer** — declare it and say why:
  `# rc-state-escape: none — <reason>`. A runaway brake with a user-side exit is
  not a brake. A security deny should not have one.

Gate 201 **corroborates** a declared escape against a real file read in the source.
A marker on its own is a claim, not an implementation — the same shape as a comment
quoting a config key while nothing is actually bound.

Test the **refusal** paths before the success path: a missing key, an empty value,
and a control from the wrong scope must each still deny. An escape that opens on an
incomplete control file is not an escape, it is an off switch.

## 3. Prove the isolation with two worktrees, and assert BOTH halves

```
worktree A records a negative  →  A is still blocked        (it is not a weakening)
                               →  B is NOT blocked          (it is scoped)
```

**Neither half means anything alone.** Scoping without the first assertion is
indistinguishable from switching the guard off — and it will pass a test suite that
only checks B. `plugins/ravenclaude-core/hooks/tests/test-premise-scoping.sh` is the
working template (22 assertions; collapsing the scope key turns exactly the
cross-worktree ones red).

## 4. Fail closed

Deny with **exit 2**. The harness treats exit 2 as BLOCK and any other non-zero as a
non-blocking error — so `exit 1` on an unexpected input is a **silent fail-open**.
Gate 199 (`scripts/check-hook-failclosed.sh`) drives every `PreToolUse` hook against
hostile payloads and asserts this.

## 5. Write the gate's teeth against the LIVE tree, not only fixtures

A checker that quietly stopped reading the real hooks would still pass its own
fixtures. Mutate a real guard's declaration in a temp copy, assert red — **and
assert the unmutated copy is clean**, or the red proves nothing about the mutation.

---

## Building the checker itself — four instrument bugs found by dry-running first

Gate 201's checker was run over the live tree **before** it was wired in (the M5
step). Every one of these produced a confident, wrong reading:

| Bug | What it reported | Root cause |
| --- | --- | --- |
| discovery scoped to `.ravenclaude/runs/` | `worktree-guard.sh` **STATELESS** — it keys a real registry on `sha256(toplevel)` under `$HOME/.ravenclaude/` | the probe's scope was an assumption, never measured |
| one-pass "assigned a `.ravenclaude/` path" | **10 of 11** hooks stateful, up from 5 | matched config **reads** (`comfort-posture.yaml`) |
| comments scanned as code | a hook with **zero** write lines called stateful | prose satisfies a source scan — the third time in this repo |
| loose write pattern | `"$mode) auto-resolved…"` counted as a write | the variable was not in write-target position |

The two shapes worth carrying forward:

- **A near-uniform result across a population is a claim about the instrument.**
  10-of-11 was the tell.
- **An empty or expected-looking result is a claim about the PROBE** until you show
  the probe can return the opposite. Discovery is now verified in *both* directions
  by hand: 5 stateful, 6 not, all 11 confirmed.

---

## Known scope limit (named, not silently dropped)

A guard that **reads** a record some other component **writes** is out of scope
here — the key belongs to whoever writes it. `guard-web-access.sh` reads
`runs/<sess>/web-allow.txt` and never writes it. If that writer is not itself a
`PreToolUse` hook, **no gate currently asks it to declare a key.** Widening
discovery past `PreToolUse` is follow-up work, not something this gate covers.

## Related

- Gate 190 — the premise-ledger scoping proof (the two-worktree template)
- Gate 199 — `PreToolUse` fail-closed exit-code audit
- `plugins/ravenclaude-core/knowledge/verification-discipline.md`
- `docs/best-practices/ci-gate-audit.md` — how to give a gate teeth
