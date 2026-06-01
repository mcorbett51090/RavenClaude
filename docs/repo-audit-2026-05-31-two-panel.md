# Repo audit — two-panel fine-tooth-comb + gap analysis + remediation plan

**Date:** 2026-05-31 · **Baseline:** `main` @ `c56e0cd` (audit-gates 350/0) · **Branch for fixes:** TBD per workstream
**Method:** two independent 4–5-agent panels (non-overlapping lanes, fresh agents, no shared findings), then a gap analysis, then a security-reviewer **expert adjudication** of every cross-panel severity divergence. Facts the panels asserted were independently reproduced by the Team Lead before being accepted (the guard bypasses were run against the real `deny_patterns` array; 11/11 reproduced).

---

## 1. Panel tallies

| Lane | Panel 1 | Panel 2 |
|---|---|---|
| Security | 3 P0 · 5 P1 · 1 P2 | 0 P0 · 8 P1 · 3 P2 |
| Build-integrity | 0 P0 · 2 P1 · 2 P2 | 1 P0 · 4 P1 · 2 P2 |
| Docs / cross-ref | 0 P0 · 4 P1 · 2 P2 | 0 P0 · 5 P1 · 2 P2 |
| Manifest | 0 P0 · 0 P1 · 2 P2 | (folded into content lane) |
| Content-correctness | 0 P0 · 2 P1 · 2 P2 | 0 P0 · 3 P1 · 2 P2 |

## 2. Gap analysis — agreement raises confidence; divergence was adjudicated

**Corroborated by BOTH panels (high confidence — independent rediscovery):**
- Guard-destructive bypassable by idiomatic variants (`rm -fr`, `${HOME}`, `+refspec` force-push, `curl|sudo bash`, `bash <(curl…)`, `git branch -D`, `mkfs`/`dd of=/dev/disk0`). Facts reproduced by the Team Lead too.
- CI behavioral guard test exercises only **canonical** forms → green CI while bypasses exist.
- `validate-marketplace.yml` `paths:` filter omits `README.md`/`docs/**`/boundary files → claims+guide-fresh+link gates never fire on those edits.
- `validate-layout.yml` scans only **diff-added** files → pre-existing/modified off-allow-list files never caught.
- 4 stale counts in `docs/architecture.md` (11→16 active, 12→15 domain, 13↔14 agents contradiction, Salesforce shipped-but-listed-planned).
- Grok price/context **baked into the persona** — violates the plugin's own house opinion #4 / §7 ("never baked into personas; one file refreshes, not three").
- `.prettierignore` + `.claude/worktrees/.gitkeep` tracked but match no `.repo-layout.json` glob.
- `check-marketplace-claims.py` gates `N skills` but **not** `N agents`/roster counts (latent gate-hole; no live drift today).
- `guard-recursive-spawn.sh` strict mode uses non-blocking `exit 1`.

**Panel-unique (single-panel, accepted after spot-check):**
- P2-build: `guard-recursive-spawn.sh` is **PostToolUse** — fires after the write, so even `exit 2` couldn't block (structural; compounds the exit-1 finding).
- P2-security: the `.claude/settings.json` deny-list is **marketplace-dev-only — NOT in the consumer install payload** (became the deciding fact in adjudication).
- P2-docs: README + architecture.md undercount hooks (11 vs 13 registered — omit `claim-grounding-lint`, `dod-gate`, `runaway-brake`).
- P2-content: 3 `microsoft-graph` knowledge files carry a volatility disclaimer but **no `Last reviewed:` date**.
- P1-build (P2): `validate-layout.yml`'s inline glob matcher has **no audit fixture** (Gate 6 tests the hook, not the workflow's separate matcher).

**Divergences → expert-adjudicated (binding):**
| Item | Panel 1 | Panel 2 | **Adjudicated** |
|---|---|---|---|
| Guard bypasses | P0 | P1 (security) / P0 (build) | **P0** — hook is the consumer's *primary & only* shipped deterministic guard (`hooks.json:33`); deny-list absent from install payload (`.claude/settings.json:6-27` is dev-only); tribunal OFF by default. Fails open on idiomatic irreversible commands behind false-green CI. |
| "Latest Claude" lag | P1 | P2 | **P2** — lineup explicitly scopes to Copilot's picker and defers Claude to the capability map; divergence honestly bounded. |
| `test-author` seam | P2 (uncertain) | P1 | **P1** — `agents/test-author.md` does not exist; dangling in **5** Salesforce files incl. machine-read `works_with` routing frontmatter → mis-routes, not just reads wrong. |

## 3. Final deduplicated severity list

**P0 (1):** Guard-destructive bypass + its false-green CI test.

**P1 (10):**
1. CI behavioral guard test asserts wrong contract (any-nonzero, positional) — a regression to `exit 1` stays green.
2. `validate-marketplace.yml` paths-filter omits README/docs/boundary → claims+guide+link gates don't fire.
3. `validate-layout.yml` diff-only scan → pre-existing/modified off-allow-list files uncaught.
4. `validate-layout.yml` inline matcher has no audit fixture (gate-not-proven-bidirectional).
5. Node-dependent render gates silently skip without CI hard-fail (violates ci-gate-audit.md "a skip is not a pass").
6. `guard-recursive-spawn.sh` exit-1 strict mode + PostToolUse wiring = unachievable enforcement (fix or delete the claim).
7. `deep-researcher` + `code-reviewer` carry no prompt-injection guidance (shipped agents consuming untrusted web/diffs).
8. `docs/architecture.md` 4 stale counts/contradictions.
9. Grok price/context baked into persona (single-source-of-truth violation, 7 sites).
10. `ravenclaude-core/test-author` dead seam across 5 Salesforce files.
+ latent: `check-marketplace-claims.py` doesn't gate agent/roster counts.

**P2 (8):** `.prettierignore` + `.claude/worktrees` allow-list gaps · README/architecture hook undercount (11→13) · 3 microsoft-graph files missing date · manifest `name`-field unaudited · prettier audit fixture silent-skip · `docs/concepts.md` outside trigger filter · deny-list not shipped to consumers (defense-in-depth seed) · enforce-layout fails-open without jq.

## 4. Remediation plan — sequenced, batched by blast radius

### Workstream A — P0 security ✅ DONE (branch `fix/ravenclaude-core-guard-destructive-bypass`, core 0.90.2)
Hardened `guard-destructive.sh` with a normalization pass + order-independent matchers; all 21 audit bypass variants now block (exit 2), 9 canonical forms still block, 9 benign controls still pass. Extended BOTH test surfaces (CI behavioral `must_block` + audit-gates Gate 5, now stdin-JSON + assert-exit-2). Seeded whole-disk/branch-delete denies into `comfort-posture-balanced.yaml`. audit-gates 371/0.

#### Original spec:
Harden `guard-destructive.sh`: **normalize before matching** (collapse flag order + whitespace, expand `~`/`$HOME`/`${HOME}`, strip quotes); add patterns for `rm` with any cluster of `r`+`f` in any order; `git push … +<refspec>`; `git branch -D <branch>`; `bash <(…)` / `<cmd> | sudo? (bash|sh|zsh|python|perl|ruby|node)`; `mkfs`/`shred`/`wipefs`/`> /dev/…`; broaden `dd of=/dev/` device class (+`disk`,`vd`,`xvd`,`mmcblk`). **Then extend BOTH** the CI behavioral `must_block` array AND audit-gates Gate 5 with every bypass variant + stdin-JSON + assert-exit-2 (this is what let it ship). Seed the same hardened denies into `templates/comfort-posture-balanced.yaml` so `ravenclaude setup` consumers get the second layer. Ship as a `ravenclaude-core` patch bump with a migration note.

### Workstream B — P1 CI structural integrity (own PR)
- Add `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/**` to both `paths:` blocks in `validate-marketplace.yml`.
- Add a full-tree `git ls-files` allow-list scan (push-to-main or a periodic job) beside the diff-only check.
- Extract `validate-layout.yml`'s inline matcher to a script both the workflow and a new audit gate call; add the bidirectional fixture.
- Mirror Gate 10's `$CI`→hard-fail pattern into the node/npx skip branches (no silent skips); add `actions/setup-node`.
- Fix the CI behavioral guard test to feed stdin-JSON + assert exit 2 (folds into Workstream A's test work).
- Add `AGENTS_RE`/`actual_agent_count()` to `check-marketplace-claims.py`; optionally scan CLAUDE.md roster lines.
- Decide `guard-recursive-spawn.sh`: move detection to PreToolUse+exit 2, **or** delete the "set STRICT=1 to enforce" claim.

### Workstream C — P1 docs/content (straight to main, no PR — docs-only per AGENTS.md)
- `docs/architecture.md`: 11→16 active, 12→15 domain (×2) + add the 3 missing names, 13→14 agents, remove Salesforce from Planned, 11→13 hooks.
- README.md: 11→13 hooks + add `claim-grounding-lint`/`dod-gate`/`runaway-brake`.
- Rename `ravenclaude-core/test-author` → `tester-qa` across all 5 Salesforce files (this is plugin content → **PR**, not docs-only).
- microsoft-graph: add `Last reviewed:` to the 3 decision-tree files.

### Workstream D — P1 my-own-plugin + P2 cleanup (own PR)
- Strip the 7 baked-in numbers from `grok-model-strategist.md`; replace with tier names + "see dated lineup, verify-at-use" (match codex/copilot personas).
- Add injection-handling block to `deep-researcher.md` + `code-reviewer.md`.
- Add `.prettierignore` + `.claude/worktrees/**` to `.repo-layout.json`.
- Optional P2s: `name`-field fixture, prettier/concepts skip-hardening, lineup Claude-lag note.

### Sequencing
A → B (B's test fix depends on A's patterns) · C in parallel (independent) · D last. A+B are the load-bearing pair: they close the P0 *and* the false-green-CI class that hid it.

## 5. Verified clean (no action)
No committed live secrets (all hits are labeled fixtures / AWS's documented example key). Capability hook never emits env values (names only — `capability-orientation.py:116-131`). Zero version drift across 16 plugins. All relative links resolve. All dated knowledge within staleness tiers. Decision-router + event helpers fail safe. Every CI step except the layout-workflow-matcher maps to a bidirectional audit fixture.
