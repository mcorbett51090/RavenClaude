# Configure a definition-of-done gate — it makes "done" mean "passing tests"

**Status:** Pattern
**Domain:** Agent design / Quality / Automation
**Applies to:** `ravenclaude-core`

---

## Why this exists

An agent that stops after writing code and reports "done" without running the test suite has shifted verification to the human. That shift is invisible when it happens — the human must remember to run tests, and if they don't, a broken change may land in main. The `dod-gate.sh` Stop hook closes this loop deterministically: when source files change in a session and a `definition_of_done.cmd` is configured, the gate runs that command at Stop and blocks the session from ending until it passes. "Looks done" becomes "is done" — without making the human the verification loop.

## How to apply

Add the gate configuration to `.ravenclaude/comfort-posture.yaml`:

```yaml
# .ravenclaude/comfort-posture.yaml
definition_of_done:
  cmd: "npm test && npm run lint"   # adjust to the project's test command
  max_blocks: 8                      # consecutive Stop-blocks before force-allow (anti-deadlock)
```

Tuning the command:
- **Fast feedback loop:** prefer a command that runs in under 60 seconds — the gate fires at Stop, which is the agent's natural pause point; a 10-minute command will feel obstructive.
- **Use the project's existing CI command** if one exists — the gate is most trustworthy when it runs exactly what CI runs, not a subset.
- **Separate the gate from the reminder:** without `cmd` set, the `remind-tests.sh` advisory hook still fires a nudge to run tests. The gate is for enforcement; the reminder is for advisory posture.

Common configurations:
```yaml
# Node/TypeScript project
definition_of_done:
  cmd: "npm test && npx --yes prettier --check ."

# Python project
definition_of_done:
  cmd: "python -m pytest && python -m json.tool .claude-plugin/marketplace.json > /dev/null"

# Shell/JSON project (this marketplace)
definition_of_done:
  cmd: "bash scripts/audit-gates.sh"
```

**Do:**
- Configure the gate on any project where the test suite runs in under 2 minutes.
- Set `max_blocks` to at least 3; a single flaky test should not permanently block the session.
- Run the gate command manually before configuring it, to confirm it exits 0 on the current clean state.

**Don't:**
- Configure a `cmd` that requires user input or opens a browser — the gate runs non-interactively at Stop.
- Set `max_blocks: 0` — that disables the anti-deadlock cap and can permanently block a session on a failing test.
- Use the gate as a substitute for CI — it catches agent-introduced regressions in the session; CI catches everything else.

## Edge cases / when the rule does NOT apply

- Read-only or research-only sessions (no source file changes) — the gate is inert because it only fires when source files changed.
- Projects with no automated test suite — configure the gate with a lint or format check (`prettier --check .`) to at least catch formatting regressions.

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — "Auto-mode guardrails — runaway brake + definition-of-done gate" section (the full specification).
- [`./three-epistemic-protocols.md`](./three-epistemic-protocols.md) — the definition-of-done gate is described there as an "enforced complement" to the Last-Mile Completion Protocol.

## Provenance

Distilled from `plugins/ravenclaude-core/CLAUDE.md` §"Auto-mode guardrails — runaway brake + definition-of-done gate (added 2026-05-29, v0.56.0)". The `dod-gate.sh` Stop hook is the enforced implementation.

---

_Last reviewed: 2026-06-05 by `claude`_
