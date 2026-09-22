# Autonomous repo review — open items for your review (2026-09-22)

A scheduled multi-panel repository review ran on branch `claude/awesome-wright-nm0kzm`.
Four independent expert panels (Python scripts, shell hooks/guards, CI/config, docs) scanned
for **gate-invisible** defects — bugs the existing ~917-gate CI battery and the passing
`audit-gates.sh` meta-test cannot see. No P0 surfaced; the tree is unusually well-hardened.

This doc lists what the PR **did not** apply and why, with ready-to-paste patches for the two
that need a deliberate maintainer action, plus three systemic recommendations. Everything a
panel verified and that was safely applicable is in the accompanying PR.

## Implemented in the PR (no decision needed)

| ID | Sev | Fix | Files |
|---|---|---|---|
| A1 | P2 | `check-description-count-literals.py` self-test's "empty scope fails closed" assertion was a dead `pass` — now drives `main()` against an empty tree and asserts exit 2 (verified: teeth catch a `return 0` mutant) | `scripts/check-description-count-literals.py` |
| A2 | P3 | `check-host-support.py` crashed `AttributeError`→exit 1 (a *non-blocking* error per its own contract) on a non-dict host cell — now returns exit 2 with a clear message | `scripts/check-host-support.py` |
| A3 | P3 | `check-marketplace-claims.py` — 22 `read_text`/`write_text` calls omitted `encoding="utf-8"` (outlier vs house style); the `--fix` self-heal would `UnicodeDecodeError` on a non-UTF-8 host | `scripts/check-marketplace-claims.py` |
| C1 | P2 | 3 plugin-canonical hooks were never mirrored into the dev-mirror `.claude/settings.json` (`triage-outcome.sh`, `guard-foreground-suite.sh`, `keep-awake.sh`) — silently inert while editing the marketplace itself; now mirrored (parity: 0 missing) | `.claude/settings.json` |
| D1 | P2 | 6 README plugin skill-counts drifted (finance 9→23, power-platform 21→23, web-design 11→13, edtech 16→17, data-platform 13→14, regulatory-compliance 10→11) | `README.md` |
| D2 | P2 | `power-platform/CLAUDE.md` "18 skills total" → 23 | `plugins/power-platform/CLAUDE.md` |
| D3 | P3 | `ravenclaude-core/CLAUDE.md` said "One registered hook body lives OUTSIDE this directory" — a `grep` of `hooks.json` for `scripts/` bodies returned four (`preflight-command-review.sh`, `guard-remediation-cause.sh`, `guard-cause-closure.sh`, `ask-on-ambiguity.sh`); corrected to name all four | `plugins/ravenclaude-core/CLAUDE.md` |

## Needs your action — two verified fixes the tribunal correctly blocked

Both edit the Thing's own substrate (`plugins/ravenclaude-core/hooks/` and `.../scripts/`), so
`xc.tribunal-self-disable` hard-denied them (§B.9.5). The maintainer exemption
(`command_review.dev_repo_exempt: true`, already set) validates ownership via a **`gh`-authenticated
check** — and `gh` is absent in the remote web/Codespaces environment (GitHub is via MCP), so the
exemption cannot activate and the guard fails closed. This is the guard working as designed; an
unattended remote session should not flip a self-protection guard to edit the self-protection layer.
**Apply these from a local session where `gh` is authenticated as `mcorbett51090`, or by hand.**

### B1 (P1) — `guard-memory-compaction.sh`: the shrink-deny is dead for `MultiEdit`

**Verified end-to-end by the shell panel** (and confirmed by reading the code): the measure block reads
`.tool_input.old_string`/`.tool_input.new_string`, but a `MultiEdit` payload carries
`.tool_input.edits[]` instead — so `new_bytes` is never set and the size check silently `exit 0`s
(allow). A 97%-shrink `MEMORY.md` rewrite delivered as `MultiEdit` is **not** blocked, exactly the
incident class the hook exists to stop. (The *snapshot* half still runs for `MultiEdit`, so bytes remain
recoverable — the missing piece is only the proactive deny, which is why this is safe to hold for a
deliberate apply.)

Fix: add a `MultiEdit` byte-delta helper and branch the measure block. Paste after the `_field()`
helper (≈ line 104):

```bash
# --- MultiEdit delta helper --------------------------------------------------
# MultiEdit's payload carries `.tool_input.edits[]` (an array of {old_string,new_string}),
# NOT a top-level old_string/new_string — so the single-path `_field` cannot see it. Without
# this, `new_bytes` stayed empty for every MultiEdit and the size check silently no-op'd (allow).
# Echoes "<approved>|<byte-delta>": approved=1 iff any new_string carries the compaction-approved
# escape; byte-delta = sum(new-old) in UTF-8 bytes. Fail-safe: any error path yields empty -> allow.
_multiedit_bytes() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$payload" | jq -r '
      (if any(.tool_input.edits[]?; (.new_string // "") | contains("compaction-approved")) then "1" else "0" end)
      + "|"
      + ([.tool_input.edits[]? | ((.new_string // "" | utf8bytelength) - (.old_string // "" | utf8bytelength))] | add // 0 | tostring)
    ' 2>/dev/null || true
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c '
import json,sys
try:
    ti=(json.load(sys.stdin) or {}).get("tool_input") or {}
    edits=ti.get("edits") or []
    approved=any("compaction-approved" in (e.get("new_string") or "") for e in edits if isinstance(e,dict))
    delta=sum(len((e.get("new_string") or "").encode("utf-8"))-len((e.get("old_string") or "").encode("utf-8"))
              for e in edits if isinstance(e,dict))
    sys.stdout.write(("1" if approved else "0")+"|"+str(delta))
except Exception:
    pass' <<RC_PAYLOAD_EOF 2>/dev/null || true
$payload
RC_PAYLOAD_EOF
  fi
}
```

Then replace the `else` branch of the measure block (the `Edit / MultiEdit` span) with an explicit
three-way split:

```bash
new_bytes=""
if [ "$tool_name" = "Write" ]; then
  _content="$(_field '.tool_input.content')"
  case "$_content" in *compaction-approved*) exit 0 ;; esac
  new_bytes="$(printf '%s' "$_content" | wc -c | tr -d ' ')"
elif [ "$tool_name" = "MultiEdit" ]; then
  _me="$(_multiedit_bytes)"
  _me_approved="${_me%%|*}"
  _me_delta="${_me#*|}"
  [ "$_me_approved" = "1" ] && exit 0
  case "${_me_delta:-}" in
    '' | *[!0-9-]*) : ;;                    # non-integer -> leave new_bytes unset -> fail-safe allow
    *) new_bytes=$((old_bytes + _me_delta)) ;;
  esac
else
  # Edit: single old_string/new_string span
  _old_s="$(_field '.tool_input.old_string')"
  _new_s="$(_field '.tool_input.new_string')"
  case "$_new_s" in *compaction-approved*) exit 0 ;; esac
  if [ -n "$_old_s" ]; then
    _o="$(printf '%s' "$_old_s" | wc -c | tr -d ' ')"
    _n="$(printf '%s' "$_new_s" | wc -c | tr -d ' ')"
    new_bytes=$((old_bytes - _o + _n))
  fi
fi
```

Then **strengthen Gate 184** (`hooks/tests/test-...`) with a `MultiEdit`-shaped shrink fixture so the
fix has teeth — the panel confirmed the gate never exercised `MultiEdit`.

### B2 (P2) — `guard-remediation-cause.sh`: a leading discriminate word disarms the whole check

**Verified end-to-end by the shell panel.** `is_remediating()` (≈ line 293) returns `False` whenever
`_DISCRIMINATE` matches the *leading segment* — but `_DISCRIMINATE` contains common words (`echo`,
`pwd`, `cat`). So `echo about to fix && rm -rf src/thing.ts` classifies as non-remediating and the
whole gate is disarmed (deny never fires; no telemetry). This is the mirror image of the suffix-bypass
the code already fixed; the suffix fix's own self-test (case 7c) doesn't cover the prefix form.
Advisory-only today (`cause_remediation` default warn), but a real fail-open once it becomes `block`.

Fix — evaluate `_REMEDIATE`/`_DISCRIMINATE` per-segment:

```python
def is_remediating(raw):
    for seg in re.split(r";|&&|\|\||\|", raw or ""):
        if _REMEDIATE.search(seg) and not _DISCRIMINATE.search(seg):
            return True
    return False
```

This preserves the suffix-bypass fix (a trailing `# comment` / `&& echo done` sits in its own segment,
which still doesn't independently match `_REMEDIATE`) while closing the prefix bypass. Add a
leading-discriminate case to `_grc_self_test` so it's pinned.

## Recommendations (systemic — your call on whether to build)

1. **A skill-count gate to stop README drift (D1's root cause).** The README plugin-catalog table is
   hand-maintained and ≥6 entries had drifted; more (+1/+2) were near-drift. `check-marketplace-claims.py`
   already reads README with `--fix` — extend it (or add a sibling gate) to compare each plugin's
   `README.md` skill-count claim against `find plugins/<p>/skills -name SKILL.md | wc -l`. This is the
   only durable fix; the numbers I corrected will drift again otherwise.
2. **A dev-mirror parity gate (C1's root cause).** Nothing compares `.claude/settings.json` against
   `plugins/ravenclaude-core/hooks/hooks.json` — which is why 3 hooks silently went unmirrored across
   three commits. A cheap `check-*.py` (pattern of `check-crosshost-hook-coverage.py`) asserting every
   `hooks.json` command resolves to an equivalent dev-mirror entry would prevent recurrence.
3. **D4 (P3, judgment call): README "49 hooks" for ravenclaude-core.** The count includes 7 sourced-only
   helper scripts (`_emit-event.sh`, `_scrub.sh`, …) documented elsewhere as "not a registered hook" and
   omits the 4 hook bodies that live in `scripts/`. The functional/registered count is 42. Left as-is
   because the intended denominator is your call — state it as "42 registered hooks" or clarify "49
   hook-directory files including helpers."

## Incidental observation (not a panel finding)

The `comment` field on the `guard-remediation-cause.sh` entry — in **both**
`plugins/ravenclaude-core/hooks/hooks.json` and the dev-mirror `.claude/settings.json` — describes the
**git-protocol nudge** (`git_protocol` knob, Conventional-Commits subject, branch-prefix), which is
actually `enforce-git-protocol.sh`'s behavior. `enforce-git-protocol.sh`'s own entry has no comment. The
comment appears to belong on `enforce-git-protocol.sh`. Left untouched: `hooks.json` is tribunal
substrate (blocked here), and it's a cosmetic manifest-comment mislabel, not a behavior defect.
