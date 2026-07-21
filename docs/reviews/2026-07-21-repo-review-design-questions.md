# Repository review — design-input questions (2026-07-21)

Scheduled autonomous whole-repo review. Three fan-out expert finders (scripts/hooks,
CI workflows, root docs/config) plus a structural sweep across all 167 plugins.
A validation + tie-break pass sorted findings into **auto-fixed** (objectively safe,
shipped in the accompanying PR) and **needs-design** (below — a human decision gates them).

**Headline: the repo is exceptionally healthy.** Every objective gate is green
(prettier@3.9.4, ruff, frontmatter, md-links, model-ids, JSON schemas, layout,
`audit-gates.sh` = 587 pass), and the 167-plugin marketplace is fully consistent
(version parity, required files, entry parity, naming — 167/167 on all four). The
auto-fixed set was small and low-blast; the items below are the only ones that
should not be resolved autonomously.

---

## Auto-fixed in the PR (context, not questions)

| Pri | Fix | File |
|-----|-----|------|
| P2 | Pin `prettier@3.9.4` in the gate-audit (was unpinned → resolved to 3.8.1, false local failures, drift from CI) | `scripts/audit-gates.sh` Gate 9 |
| P2 | Correct un-gated self-description counts (144→166 domain plugins; 43→48 & 21→23 skills; ~100→~165 plugins; layout sketch +validate-schemas) | `.claude-plugin/marketplace.json`, `README.md`, `AGENTS.md` |
| P3 | macOS-absent-`timeout` guard (freshness check + dashboard open silently no-op'd on stock macOS) | `scripts/check-checkout-fresh.sh`, `scripts/open-dashboard.sh` |
| P3 | Refresh stale pin-provenance comment (cited v6.1.0/@v6; pin is actually v8.1.1) | `.github/workflows/quarantine-intake.yml` |

Derivable self-healing counts (e.g. the core-README hooks-table row, which `--fix`
sets to 22 post-merge) were deliberately **left untouched** to avoid the cross-PR
contagion the self-healing design exists to prevent.

---

## Needs design input — 5 open questions

### Q1 — [P2] `format-on-write.sh` uses unpinned `prettier`, can fight the pinned CI check
- **Code:** [`plugins/ravenclaude-core/hooks/format-on-write.sh:42-43`](../../plugins/ravenclaude-core/hooks/format-on-write.sh#L42-L43), wired at [`.claude/settings.json`](../../.claude/settings.json) (PostToolUse dev-mirror).
- **What:** The format-on-write hook runs whatever `prettier` is on `PATH`. CI and the gate pin `prettier@3.9.4`. A maintainer whose global prettier ≠ 3.9.4 gets files silently reformatted to a different style, which then **fails the pinned `--check` gate** — formatting churn that fights CI. No gate checks that the formatter hook matches the pinned version.
- **Why it's a design call:** the hook is *shipped to consumers*, where "use the project's own prettier" is the correct default. Forcing 3.9.4 on consumers would be wrong. Only the marketplace-repo (dev-mirror) invocation should pin.
- **Recommendation:** in the dev-mirror wiring (`.claude/settings.json`), invoke `npx --yes prettier@3.9.4 --write` (or resolve a repo-local `node_modules/.bin/prettier`); leave the plugin default alone. **Question:** confirm the dev-pins-vs-consumer-default split before I change the shipped hook's environment.

### Q2 — [P3] `guard-recursive-spawn.sh` "strict" mode claims a hard-block it can't deliver
- **Code:** [`plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh:37,133-141`](../../plugins/ravenclaude-core/hooks/guard-recursive-spawn.sh#L133-L141); contrast the documented contract in [`guard-destructive.sh:9-14`](../../plugins/ravenclaude-core/hooks/guard-destructive.sh#L9-L14).
- **What:** The header says strict mode (`RC_GUARD_RECURSIVE_SPAWN_STRICT=1`) "hard-block[s]," but the implementation does `exit 1`. Claude Code treats every non-2 exit as a *non-blocking* error — only `exit 2` blocks. So the advertised block is a no-op. Compounding it: this is a **PostToolUse** hook, where the spawn has already happened — a true "block" is impossible from that event regardless of exit code.
- **Why it's a design call:** the fix depends on intent. If strict is meant to *surface a warning*, the docs are simply wrong (→ doc correction). If it's meant to *feed the violation back to Claude*, it should `exit 2` (which shows stderr to the model) and the "hard-block" wording should become "surfaces a blocking-style stderr notice, post-hoc."
- **Recommendation:** correct the header to state strict mode surfaces a stderr notice (it cannot undo a completed spawn), and switch `exit 1`→`exit 2` in strict mode so the notice actually reaches Claude. **Question:** is that the intended behavior, or should strict stay purely advisory (docs-only fix)?

### Q3 — [P3] No `concurrency` on the three required checks
- **Code:** [`validate-marketplace.yml`](../../.github/workflows/validate-marketplace.yml), [`validate-layout.yml`](../../.github/workflows/validate-layout.yml), [`validate-schemas.yml`](../../.github/workflows/validate-schemas.yml) — none declares `concurrency:`.
- **What:** rapid pushes to a PR branch leave superseded runs executing to completion on stale SHAs (wasted minutes; the long `audit-gates.sh` run is the expensive one). The mutating workflows (`quarantine-intake.yml:33`, `regenerate-artifacts.yml:76`) correctly use `cancel-in-progress: false`; only the read-only validators should cancel.
- **Why it's a design call:** this touches **required** checks, and this repo is (correctly) very deliberate about required-check triggers — the whole "never add `paths:` to a required check" rule is in `AGENTS.md`. `cancel-in-progress: true` is the standard, safe pattern (a cancelled run on a non-head SHA never blocks merge, which is evaluated on the head SHA), but I'm not going to modify all three required workflows autonomously for a pure cost win.
- **Recommendation:** add `concurrency: { group: <wf>-${{ github.ref }}, cancel-in-progress: true }` to the three read-only validators. **Question:** approve, or is run-to-completion intentional?

### Q4 — [P2] Self-heal auto-merge PR may hang forever if the ruleset binds bot PRs
- **Code:** [`regenerate-artifacts.yml:278-314`](../../.github/workflows/regenerate-artifacts.yml#L278-L314) — opens a PR with `github.token` then `gh pr merge --squash`.
- **What:** PRs opened by the automatic `GITHUB_TOKEN` **do not trigger `pull_request` workflows**, so validate-marketplace/-layout/-schemas never run on the self-heal PR. The workflow's own comments assert the `main` ruleset "requires 0 approvals and no status checks" — in tension with those three being **required** checks. If the ruleset in fact requires them for all PRs to `main`, this self-heal PR stays Pending forever and the merge step fails, leaving `main` un-healed and breaking every subsequent PR's freshness gate.
- **Why it's a design call:** the outcome depends on the branch-protection **ruleset config**, which isn't in the repo tree and needs admin API/settings access to read authoritatively. `CLAUDE.md` notes admin keeps `bypass_mode: always` — but the self-heal path uses `GITHUB_TOKEN`, not an admin identity, and doesn't `--admin`-bypass.
- **Recommendation:** verify whether the ruleset's required checks bind `GITHUB_TOKEN`-authored PRs. If yes: either exclude the `chore/self-heal-artifacts` branch from the required-checks ruleset, or open the PR with a PAT/App token so the `pull_request` checks actually run. **Question:** which route — and can you confirm the current ruleset behavior for bot PRs? (I can re-check via the rulesets API if you want me to.)

### Q5 — [P3] Root README "16 hooks" is stale under every definition
- **Code:** [`README.md`](../../README.md) ravenclaude-core bullet ("…gates, 48 skills, **16 hooks**, templates…").
- **What:** "16" matches nothing: **26** `hooks/*.sh` files, **22** distinct registered commands in `hooks/hooks.json` (the definition the self-healer uses for the core-README table), **6** event keys. The number is stale under every plausible unit.
- **Why it's a design call:** "hook" is undefined here, and — unlike the *core-plugin* README table (which `check-marketplace-claims.py --fix` self-heals to 22) — this **root** README bullet is outside the self-healer's regex scope, so it rots silently with no gate.
- **Recommendation:** adopt the self-healer's unit ("distinct registered hook commands" = 22), fix the bullet to "22 hooks," and **extend `check-marketplace-claims.py` to also manage this root-README bullet** so it can't drift again. **Question:** bless the "22 registered hook commands" unit and the gate extension, and I'll ship both.

---

## Verified clean (so these aren't re-audited)

- **All 167 plugins:** version parity (plugin.json ↔ marketplace.json), required files (README/CLAUDE/plugin.json), entry bijection, name consistency — 167/167 on each.
- **Required CI checks:** none carries a `paths:` filter (they can't hang a PR); whole-tree gates (`prettier`, `ruff`) run unconditionally; 14/14 `uses:` SHA-pinned with version comments; every workflow has a least-privilege `permissions:` block.
- **`.repo-layout.json`:** every committed path matches a glob; no dead globs.
- **Portability:** the bash-3.2 trap classes (`declare -A`/`mapfile`/`globstar`/`${^^}`, BSD `grep -P`/`sed -i`, `set -e` fail-open) are already closed and documented in `_portable.sh`; the two bare-`timeout` scripts above were the only stragglers (now fixed).
- **Root-doc cross-references:** every script/file referenced in `AGENTS.md`/`.repo-layout.json` exists; `README.md` "166 of the 167 plugins declare `requires`" verified true.
