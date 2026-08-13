# Repo review 2026-08-07 — maintainer-action items (ready-to-apply patches)

These confirmed fixes were **not** applied by the autonomous review run for one of two reasons:

1. **Tribunal-substrate protection (4 items).** They edit files under `plugins/ravenclaude-core/hooks/`
   or `plugins/ravenclaude-core/scripts/`, which the Thing's `xc.tribunal-self-disable` guard
   (`always_screen` + `pre_llm_deny`) blocks — correctly. An autonomous session editing the Thing's own
   guard files, or flipping `command_review.enabled: false` / `dev_repo_exempt: true` to get around the
   guard, is exactly the scenario that protection exists to prevent, so the run **did not** do it. These
   need a **maintainer** to apply them (edit by hand, or set `command_review.enabled: false` in
   `.ravenclaude/comfort-posture.yaml` for the session, apply, then turn it back on — the documented A3
   escape hatch).
2. **Test-hygiene, low-risk (2 items).** Gate-teeth improvements with marginal value and some
   regression risk; left for a deliberate maintainer call rather than churned autonomously.

None of these require a **design** decision — each is a mechanical correction matching an existing
in-repo precedent. They are ordered by priority.

> **Note on this doc itself:** the first write of this file was blocked by the Thing's `srm.force-push`
> hard rule, because a patch description quoted a force-push regex verbatim. That is the guard working as
> intended (it screens content category-independently); the prose below describes the sibling patterns by
> name and line number instead of quoting the command form.

---

## P1 — `guard-destructive.sh`: `git reset --hard` deny is position-anchored (FAIL-OPEN)

`plugins/ravenclaude-core/hooks/guard-destructive.sh:451`. The `--hard` deny anchors the flag to the
token *immediately* after `reset`, unlike the sibling force-push patterns at lines 448–449, which were
deliberately made order-independent (a `.*` between the subcommand and the flag). Each of these is valid,
destructive (red / irrecoverable tier per CLAUDE.md), and currently **ALLOWED**:

- `git reset --quiet --hard`
- `git reset -q --hard HEAD~1`
- `git reset HEAD~1 --hard`

**Patch** — replace line 451:

```
-  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]+|$)'
+  'git[[:space:]]+reset[[:space:]]+.*--hard([[:space:]]|$)'
```

(New pattern with an inline comment: `# --hard in ANY position, order-independent like the force-push
patterns; --hard([[:space:]]|$) keeps --hardcore etc. from matching`.)

This gives `reset` the same order-independent treatment the force-push patterns at 448–449 already have.
The `.*`-crosses-a-chained-command over-block is the same accepted exposure those patterns carry and
fails **safe** (over-blocks, never under-blocks) — the correct direction for a destructive-command guard.
`--hardcore`-style non-flags don't match (the `--hard([[:space:]]|$)` boundary); `-m` message bodies are
already stripped by the preprocessor.

## P2 — `guard-destructive.sh`: `git clean` force deny is position-anchored (FAIL-OPEN)

`guard-destructive.sh:452`. Same shape. Bundled (`-fd`) and force-first (`--force`) are caught, but a
**leading non-force flag** slips past — currently ALLOWED: `git clean -d -f`, `git clean -x -f`,
`git clean -d --force`.

**Patch** — replace line 452:

```
-  'git[[:space:]]+clean[[:space:]]+(-[a-z]*f|--force)'
+  'git[[:space:]]+clean[[:space:]]+(.*[[:space:]])?(-[A-Za-z]*f[A-Za-z]*|--force)([[:space:]]|$)'
```

(Inline comment: `# -f in any bundled cluster OR after a leading flag (git clean -d -f, -x --force),
order-independent; -n/-i dry-run without an f still allowed`.)

Dry-run/interactive (`git clean -n`, `-i`) without an `f`-flag stay allowed.

> **After applying P1+P2:** re-run the guard-destructive coverage in `scripts/audit-gates.sh` and confirm
> the new evasion forms are now denied (exit 2) while `git reset --soft` and `git clean -n` still pass.
> Consider adding the three reset and three clean evasion strings as `must_fail` fixtures so the
> order-independence has teeth.

## P2 — `thing-denial-kb.py`: unsanitized fields reach SessionStart context (frame-break/injection)

`plugins/ravenclaude-core/scripts/thing-denial-kb.py`, `cmd_recall` (lines 376/380/382). The Muninn
recall digest is injected verbatim as SessionStart `additionalContext` by `thing-denial-kb-recall.sh`,
but `category`, `resolution`, and `doc` are interpolated **without** the newline/frame-break stripping
the repo requires of every SessionStart surface (cf. `capability-orientation._sanitize_banner_field`).
`category` flows from `_event_from_command` (untrusted); a planted `.ravenclaude/runs/thing/denial-kb.jsonl`
line (gitignored but process-writable / clone-plantable, per the repo's own threat model) with a
multi-line `category` lands attacker text straight into session context. (`sample`/`reasoning` are
already safe — they pass through `_clip`; these digest fields never do.)

**Patch** — route the three fields through the existing `_clip()` (its `" ".join(text.split())` already
collapses CR/LF **and** U+2028/U+2029/VT/FF, because Python's `str.split()` splits on all Unicode
whitespace):

```
-        tag = f"[{r.get('source')}/{r.get('category')}] ×{r.get('count', 1)}"
+        tag = f"[{_clip(str(r.get('source')), 40)}/{_clip(str(r.get('category')), 60)}] ×{r.get('count', 1)}"
         lines.append(f"\n• {tag}  (sig {r.get('signature')})")
         if r.get("resolution"):
             src = r.get("resolution_source") or "seed"
-            lines.append(f"    ✅ resolution ({src}): {r['resolution']}")
+            lines.append(f"    ✅ resolution ({_clip(str(src), 40)}): {_clip(str(r['resolution']), 200)}")
             if r.get("doc"):
-                lines.append(f"    ↪ see: {r['doc']}")
+                lines.append(f"    ↪ see: {_clip(str(r.get('doc')), 200)}")
```

Optionally also normalize `category` at capture (`_event_from_command`, line 179) so the stored value is
already single-line. Extend Gate 143 with a planted multi-line `category` fixture asserting the injected
newline / `SYSTEM:` payload does not reach the emitted digest.

## P3 — `stream-ops.py get_centroids`: breaks the "never raise" contract on a malformed centroid

`plugins/ravenclaude-core/scripts/stream-ops.py:558`. `read_registry` hardens the entry shape (drops
non-dict stream values) but not the nested `centroid`. A hand-edited / planted `registry.json`
(**not** gitignored → reachable via a normal clone) with `"centroid": "x"` makes `dict("x")` raise
`ValueError`; `"centroid": 5` raises `TypeError`. Today's only hot caller wraps it in `try/except`, but
the documented read-helper contract is broken and any future/direct caller crashes.

**Patch** — guard each centroid defensively:

```
-    return {sid: dict(meta.get("centroid", {})) for sid, meta in registry["streams"].items()}
+    out: dict[str, dict[str, float]] = {}
+    for sid, meta in registry["streams"].items():
+        c = meta.get("centroid")
+        out[sid] = (
+            {str(k): float(v) for k, v in c.items() if isinstance(v, (int, float))}
+            if isinstance(c, dict)
+            else {}
+        )
+    return out
```

Add a malformed-centroid case to the stream-ops read-helper test (Gate 110/111 area).

## P3 — `remind-tests.sh`: `awk '$2 ~ …'` under-counts renamed/spaced paths

`plugins/ravenclaude-core/hooks/remind-tests.sh:19-22`. The identical `git status --porcelain`
field-parse bug that `dod-gate.sh:86-88` already fixed with `--porcelain=v1 -z` + null-delimited
parsing. `$2` splits on whitespace, so a source path with a space, or a rename record (`R old -> new`),
is mis-counted and the reminder is skipped. **Advisory-only** (a Stop nudge, exit 0) → P3; worth
aligning with the `dod-gate.sh` precedent for consistency (reuse its `-z` parse loop and match the
extension list against the NUL-delimited path field).

---

## Test-hygiene (low-risk, maintainer's call — not defects that pass bad output)

These do not let broken output through today; they mean a gate's *teeth* are weaker than advertised.
The related `check-prompt-builder-render.mjs` `+=` SINK_RE hole is already **fixed in this PR**.

### `check-stepper-render.mjs:121-128` — islanded must-fail half is a tautology (P2 test-quality)
On an islanded surface the must-fail path calls `checkStepper(brokenDecoded)` single-arg, so `jsSrc`
defaults to the decoded markup, which contains none of the JS-contract strings — the four JS assertions
fail *unconditionally*, so `checkStepper(brokenDecoded).length === 0` is never true and the
"gate has no teeth" guard can never fire. If the active-frame/dot/caption invariants were removed, this
half would stay green and certify nothing. **Fix:** pass the real JS source and compare against a
baseline, e.g. `if (checkStepper(brokenDecoded, raw).length <= checkStepper(decoded, raw).length) …`,
or assert the specific "exactly one active frame per stepper" message appears.

### `check-shell-router.mjs:142,162` — dead/tautological assertions (P3)
`assert(NAV_IDS.includes(target), …)` / `assert(NAV_IDS.includes(owner), …)` iterate over constants
defined in the test file, so they can never fail against any `index.html`. Harmless (the companion
`re.test(...)` assertions on the same lines read the artifact and have real teeth) but dead. **Fix:**
delete both, or move them outside the artifact-assertion loop labeled as internal-consistency checks.
