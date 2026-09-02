# Copilot CLI hook incompatibility — the incident, what's verified, and what ships

**Last reviewed:** 2026-09-02

## The report

A user reported a hook error blocking every tool call in a **GitHub Copilot CLI** session. Their
own diagnosis: running Copilot CLI **1.0.3** — a version well below the **1.0.52** floor
`copilot_version_check()` (`scripts/ravenclaude`, Gate 157) already checks and warns on for
sub-agent tool-call hooking — and malformed hook output that broke the Copilot hook adapter
(`hooks/copilot-hook-adapter.sh`).

**`[unverified — user-reported symptom, not independently reproduced this session]`** — no Copilot
CLI 1.0.3 binary was available to test against, so the exact failure mechanism (a malformed
`.github/hooks/ravenclaude.json` structural rejection vs. a runtime crash in the adapter vs.
something else entirely) is not confirmed here. This file records what **is** verified, and treats
the reported mechanism as a hypothesis the prevention work is designed to be robust to, not a fact
to build a narrow fix against.

## What's independently verified this session

`[web-sourced 2026-09-02]`, against `github.com/github/copilot-cli`'s own changelog and issue
tracker:

- Copilot CLI reached GA at **1.0.2** (2026-02-25). Hooks (`preToolUse`/`postToolUse`/etc.) were a
  GA-era feature.
- **1.0.52** (2026-05-23) is where `subagentStart`/`subagentStop` hooks were fixed to fire
  correctly for sub-agent tool calls — the floor this repo's Gate 157 already checks.
- **1.0.62** is where PascalCase Claude-matcher semantics started being honored (see
  `generate-copilot-hooks.py`'s own header for the full reasoning on why degradation below that
  version is safe **for matchers specifically**).
- GitHub's own hooks-configuration docs state: *"Structural errors (invalid JSON, a bad version, or
  a non-array event list) still reject the entire file."* — i.e. Copilot's hooks loader validates
  the whole config and, on any structural problem, drops it wholesale rather than degrading
  per-hook. This is a real, documented failure mode independent of the specific incident.

**1.0.3 sits between GA (1.0.2) and the sub-agent floor (1.0.52)** — deep in the version range this
repo's `generate-copilot-hooks.py` design comment already reasons about ("degradation below 1.0.62
is safe... old Copilot is no worse than today"), but that reasoning was written and verified against
the **matcher-honoring** gap specifically, not against whether a version this early can safely
*load* the generated hook config file at all. The report is new information the prior design didn't
have.

## What already existed before this incident

- `copilot_version_check()` (Gate 157) — warns when the running Copilot CLI is below 1.0.52,
  called **before** hooks are wired during `ravenclaude install`. It deliberately **never aborts**
  the installer or `status` — an earlier revision did, and that was reverted (owner ruling
  2026-08-13, documented above `COPILOT_FLOOR` in `scripts/ravenclaude`). Any fix here must respect
  that ruling: the check stays advisory, always `return 0`.
- `generate-copilot-hooks.py`'s deliberate choice **not** to make hook *generation* conditional on
  the installer machine's Copilot version, because doing so "would make the generated guardrails
  depend on who ran setup" — a correctness argument about consistency across installs, not a claim
  that every conceivable old version can safely load the result.

Neither of these gives a user **already stuck** in a broken session anything to do.

## What ships now — the recovery escape hatch

`ravenclaude repair --host copilot [--project DIR]` (`scripts/ravenclaude`, `cmd_repair`):

1. If `.github/hooks/ravenclaude.json` is absent, reports "nothing to repair" and exits 0 — the
   cause is elsewhere; points at `ravenclaude status`.
2. If present, **renames** it to `ravenclaude.json.disabled-<UTC-timestamp>` — never deletes,
   fully recoverable, and Copilot's repo-hook loader only reads files literally in
   `.github/hooks/`, so the rename is exactly what takes it out of the loader's view.
3. Prints next steps: start a **new** Copilot session (a running one already loaded the broken
   config and won't notice a rename mid-session), check `copilot --version`, update if needed, then
   re-run `ravenclaude install` to regenerate a clean hooks file.
4. `--host` other than `copilot` refuses (exit 2) — Codex's hook-trust story (MH-17, see the
   `CLAUDE.md` milestone) is a different mechanism (`/hooks` re-trust inside Codex), not a file to
   repair here.

`copilot_version_check()`'s below-floor warning now also names the reported failure mode and points
at `ravenclaude repair --host copilot` as the recovery path, without changing its own exit-code
contract (still always `return 0` — the 2026-08-13 ruling is untouched).

Proven by **Gate 257** (`hooks/tests/test-gate257-copilot-repair.sh`): nothing-to-repair exits 0;
a present hooks file is renamed with content preserved byte-for-byte; `--host codex` refuses and
leaves the file untouched; a must-fail teeth half (a mutant that always reports "nothing to repair")
is caught by a real file being left in place.

## What this deliberately does NOT do, and why

- **Does not add a second, harder version floor that skips writing the hooks file for critically
  old versions.** Pinning an exact "safe to load" cutoff below 1.0.52 would be guessing at a
  boundary this session could not verify (no 1.0.3 binary to test against), and a wrong guess could
  either strand a working install (false positive) or ship the identical incident one version lower
  (false negative). The recovery escape hatch is robust to the exact boundary being unknown —
  whatever the mechanism, `ravenclaude repair` gets a user unstuck without RavenClaude needing to
  correctly predict, for every possible ancient Copilot build, whether it is safe.
- **Does not change `copilot_version_check()`'s exit-code contract.** It still always returns 0.
  Reintroducing a hard-blocking check on this file is the exact regression the 2026-08-13 ruling
  and Gate 157's fail-safe assertions exist to prevent.

## Follow-up, named honestly rather than left silent

If a future incident report comes with reproduction access (a pinned old Copilot CLI binary), the
next step is to drive the **real** install path against it (not just `status`, which Gate 157
already covers) and confirm whether the generated `.github/hooks/ravenclaude.json` is silently
dropped (safe — matches the documented "reject the whole file" behavior) or actively breaks the
CLI (would justify revisiting whether hook generation should be skipped below some verified
version). Until then, treat the exact mechanism as unverified and lean on the recovery path.
