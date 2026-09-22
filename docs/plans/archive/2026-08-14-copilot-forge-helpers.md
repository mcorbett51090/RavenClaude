# Plan — `copilot-forge-helpers`

**Slug:** `copilot-forge-helpers`
**Depth:** quick
**Landing pre-commitment:** `forge/copilot-forge-helpers` draft PR; bump `ravenclaude-core` `0.264.0` → `0.265.0`; reserve **Gate 211**.
**Branch:** `fix/ravenclaude-core-copilot-forge-helpers`

---

## 1. Diagnosis

Matt saw this in VS Code Copilot Chat, in a *consumer* repo (not this marketplace clone):

> FORGE helper set is only partially available in this environment (routing script exists, premise/worktree scripts do not)

**Primary cause: (d) a closeable RavenClaude packaging/citation gap.** Secondary remainder: **(b)** a real, accepted host limit — VS Code Chat is not a first-class RavenClaude host, and `/forge` is a Claude Code slash command. A thinner **(a)** remainder is installer-by-design: `ravenclaude install` never promised to copy plugin `scripts/` into the consumer. **Not (c)** if `.claude/skills/forge-pipeline` is present — that means install did its job for skills.

What actually happened, in one pass:

The `forge-pipeline` skill *does* load in Chat (VS Code reads `.claude/skills`). Agent mode *can* run Python and bash. The three helpers (`forge-route.py`, `premise-gate.py`, `forge-worktree.sh`) already ship together under `plugins/ravenclaude-core/scripts/`. The skill and `/forge` command cite them only as `${CLAUDE_PLUGIN_ROOT}/scripts/…`. Claude Code interpolates that variable. Copilot Chat does not have that contract. The installer never copies `scripts/` into the consumer, so a Chat session that follows the cited invocations finds nothing and *composes* a warning RavenClaude does not emit.

The “routing exists, premise/worktree do not” split is **not** a product that ships 1-of-3 helpers. After PR #915 / v0.263.0, G3b already cites `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/premise-gate.py` — same form as the other two. Claims-table row **8** (marketplace-root `scripts/premise-gate.py`) is **stale in this checkout**. Do not plan a “fix C8” phase.

Closing (d) means one host-agnostic resolver plus citation updates so Chat can invoke the same three files Claude Code already ships. It does **not** mean making Chat a first-class host.

**One-sentence success signal:** it was (d), with an honest (b) remainder — Chat is not Claude Code, but the three helpers resolve without `${CLAUDE_PLUGIN_ROOT}`.

---

## 2. G3b exits (recorded)

| id | kind | exit | how this plan treats it |
|---|---|---|---|
| **10** | inference | **owner-gated / design-around** | “Chat does not set `CLAUDE_PLUGIN_ROOT`.” `[unverified — premise not disconfirmed: no live VS Code env]`. The resolver **must work whether the var is set or unset**. Do not block P1 on a live Chat probe. Optional owner probe later: `echo "${CLAUDE_PLUGIN_ROOT-unset}"` in a VS Code Copilot Agent terminal. |
| **12** | inference | **probe-run, settled 2026-08-14** | Scratch consumer: skill symlink present; `scripts/forge-route.py`, `scripts/premise-gate.py`, `scripts/forge-worktree.sh` all absent from the consumer tree; `CLAUDE_PLUGIN_ROOT` unset. Walking `realpath(.claude/skills/forge-pipeline)/../../scripts/` finds all three. |
| **16** | inference | **owner-gated** | Diagnostic only: the 2-of-3 split is a probe artifact. Not a construction premise. |
| **17** | inference | **owner-gated** | Diagnostic only: skill present ⇒ not an incomplete install. |
| **19** | inference | **owner-gated** | This is the G0 success signal / DoD, not an empirical premise. |

Row **8** is observation-tier and **false-in-this-tree**. It is **not a build input**.

---

## 3. Alternatives (pick)

| # | Approach | One-line trade-off |
|---|---|---|
| **A ★ Resolver + citation rewrite** | Add `resolve-plugin-root.sh`; rewrite FORGE citations to resolve-once then `$FORGE_PLUGIN_ROOT/scripts/…`. | Smallest reversible close. Claude Code path unchanged. Chat gets a recipe without a new host. |
| **B. Copy/symlink helpers into the consumer** | Installer plants `scripts/` (or skill-dir copies) so bare relative paths work. | Pollutes the consumer tree, fights the live-clone model (claims 6, 17), and risks C15 skill-context bloat if linked. |
| **C. Document-only** | Banner: “helpers require Claude Code / `CLAUDE_PLUGIN_ROOT`; Chat is skills-only.” | Cheap honesty; freezes a packaging bug as a permanent host fiction. |
| **D. New `vscode-copilot-chat` host adapter** | Add a `host-support.json` row and pretend Chat is a first-class host. | Out of scope. No verified hook/slash wiring path. Gate 154 would demand a full component matrix for a surface we are not claiming. |

**Pick A.** Reject B, C, and D.

Panel B’s installer-written `.ravenclaude/plugin-root` pointer is a **follow-on**, not MVP. It only becomes interesting if `cp -r` (Windows / no-symlink) shows up in the wild. The MVP resolver already loud-fails that case instead of inventing a path.

---

## 4. Phased implementation

### P0 — Record G3b exits; do not wait on live Chat

`depends_on_claims: [6, 8, 9, 10, 12, 16, 17]`

No shipped marketplace edit required here. Claim 12 is already probe-settled. Claim 10 is design-arounded. Claim 8 is stale.

- Write the C10 `[unverified]` marker into this plan (done, §2). **Do not** require a live VS Code Agent terminal before P1.
- Optionally re-run the scratch-install fixture if the implementer wants a fresh log. Do **not** commit the scratch dir.
- Confirm in writing: no “fix mixed citation / C8” phase will be added.

**Acceptance tests**

- Plan header and §2 carry the C10 design-around and the C12 settled date.
- No later phase *requires* Chat to leave the var unset.

**Pre-build gates**

- `python3 plugins/ravenclaude-core/scripts/premise-gate.py --run-dir .ravenclaude/runs/forge/copilot-forge-helpers` — claims 10/12 either probed, design-arounded, or owner-gated.

---

### P1 — Resolver script (the only new executable)

`depends_on_claims: [7, 9, 10, 12, 18, 19]`

Add **`plugins/ravenclaude-core/scripts/resolve-plugin-root.sh`** (new; glob already allowed: `.repo-layout.json` `plugins/*/scripts/**`). Stdlib bash 3.2, same portability contract as `forge-worktree.sh`. Prints the absolute **plugin root** (`…/ravenclaude-core`) so callers append `/scripts/<name>`.

Resolution order — first hit that contains **all three** of `scripts/forge-route.py`, `scripts/forge-worktree.sh`, and `scripts/premise-gate.py`:

1. `$CLAUDE_PLUGIN_ROOT` if set and the three files exist there.
2. `$PLUGIN_ROOT` (Codex / `_portable.sh` alias family) if set and the three files exist there.
3. Walk from a live skill symlink: `readlink` `.claude/skills/forge-pipeline` (cwd or `$CLAUDE_PROJECT_DIR` / `$PWD`) → `../..` = plugin root. Also try `.agents/skills/forge-pipeline` (Codex install path) — cheap and the same walk. This is the consumer-Chat path after a normal `ravenclaude install` (claim 6). Normalize relative `readlink` targets against `.claude/skills/` (or `.agents/skills/`).
4. `command -v rc` → resolve `bin/rc` → `dirname/..` (same trick `rc` already uses).
5. `$RAVENCLAUDE_MARKET/plugins/ravenclaude-core` if set.
6. Loud fail: exit 2, stderr names every candidate tried. Never exit 0 on a miss.

**Partial set is a fail.** Missing any one of the three is exit 2, not a “routing exists” warning. That is how we stop claim-16-shaped false splits from becoming product.

Do **not** copy or symlink the three helpers into the consumer tree. That would reverse claims 6/17.

`--self-test` (scratch dirs, no network):

| fixture | expect |
|---|---|
| `CLAUDE_PLUGIN_ROOT` set to a fake plugin with the three files | prints that root, exit 0 |
| unset + `.claude/skills/forge-pipeline` → symlink into a fake plugin | prints the fake plugin root |
| unset + `.agents/skills/forge-pipeline` symlink (Codex path) | prints the fake plugin root |
| unset + `cp -r` skill (Windows fallback, no symlink) | does **not** silently invent a path; exit 2 unless another candidate hits |
| all candidates empty | exit 2, stderr lists tries |
| plugin root missing one of the three | exit 2 |

**Acceptance tests**

- `bash plugins/ravenclaude-core/scripts/resolve-plugin-root.sh --self-test` exit 0 in this checkout (candidate 1 or 3 will hit).
- Unset `CLAUDE_PLUGIN_ROOT` and run from a scratch consumer that only has the skill symlink; resolver still prints the marketplace plugin root.
- Missing-one-of-three fixture exits 2.

**Pre-build gates**

- `bash -n plugins/ravenclaude-core/scripts/resolve-plugin-root.sh`
- File is executable.
- No `declare -A` / `mapfile` / `${x^^}` / `grep -P` (macOS bash 3.2 door).
- Claim 12 remains settled (consumer does not already have the helpers).

---

### P2 — Citation update (skill + command + classify path)

`depends_on_claims: [7, 14, 15, 18, 19]`

Edit only the operational surfaces that tell a runner *how to invoke* the FORGE helpers. Keep `${CLAUDE_PLUGIN_ROOT}` as a documented *equivalent* for Claude Code; lead with the resolver so Chat does not have to know the var.

**Confirmed files (do not invent others):**

| file | current cite | change |
|---|---|---|
| `plugins/ravenclaude-core/skills/forge-pipeline/SKILL.md` | §0.5 worktree, §G1 `classify_claim.py`, §G3b `premise-gate.py`, §G7 `forge-route.py` | One **§0.4 “Resolve helpers once”** block: run the resolver, export `FORGE_PLUGIN_ROOT`, then `bash "$FORGE_PLUGIN_ROOT/scripts/forge-worktree.sh …"` / `python3 "$FORGE_PLUGIN_ROOT/scripts/…"`. Rewrite the four operational cites to use that export. |
| `plugins/ravenclaude-core/commands/forge.md` | steps 2.5 / 4 / 5 | Same recipe. Note that `/forge` is Claude-Code-only (claims 13, 14); Chat invokes the **skill** `forge-pipeline`. |
| `plugins/ravenclaude-core/skills/forge-pipeline/reference/premise-gate.md` | line 40 `classify_claim.py` | Resolver-prefixed path (same family; cited by the same skill). |

**Defer** `reference/gates-standard.md` / `thing-decide.py`. That is the tribunal stack, not FORGE’s three helpers. Scope allows pattern reuse; it is not this slug.

**Honest Chat invocation (one paragraph in SKILL.md, not a new host):**

- Load skill `forge-pipeline` (VS Code slash-invokes by the `name` field — there is no skill named `forge`, claim 14).
- Terminal is required (claim 18). A Chat pane with no Bash cannot run FORGE; that remains (b), accepted.
- Do **not** markdown-link the `.py`/`.sh` helpers from SKILL.md as skill resources (claim 15). Loading them into context wastes tokens and does not make them executable.

Leave every other `${CLAUDE_PLUGIN_ROOT}/scripts/…` citation in dashboard / set-posture / branch-archive / decision-review **untouched**.

**Acceptance tests**

- `rg 'CLAUDE_PLUGIN_ROOT/scripts/(forge-route|forge-worktree|premise-gate|classify_claim)' plugins/ravenclaude-core/skills/forge-pipeline plugins/ravenclaude-core/commands/forge.md` returns **zero** *bare* invocations that are not preceded by the resolver recipe (the var may still appear as “Claude Code equivalent”).
- `python3 scripts/check-shipped-references-resolve.py` still exit 0 (Check A: resolver lives in-plugin; Check C: no new bare `scripts/forge-*.py` in operational surfaces).
- Skill still has only `SKILL.md` + `reference/*` as loaded docs; no helper script copied into the skill dir.

**Pre-build gates**

- Gate 187 (`check-shipped-references-resolve.py`) clean.
- `scripts/check-frontmatter.py` still happy (no agent frontmatter change).
- P1 self-test green (citations name a file that exists).

---

### P3 — Optional `rc` verbs (time-boxed; skippable)

`depends_on_claims: [13, 18, 19]`

Small additive case arms on existing `plugins/ravenclaude-core/bin/rc` (already resolves `PLUGIN_ROOT` from its own location). Convenience only — **not** the close. Chat that cannot find `rc` on PATH still has P1+P2.

```
rc forge-worktree init|checkpoint|path|--self-test …
rc forge-route --plan … | --self-test
rc premise-gate --run-dir … | --self-test | --must-fail
rc classify-claim --text …
```

Each `exec`s `"$PLUGIN_ROOT/scripts/<name>"`. Unknown-command help line gains the four verbs.

Do not make Chat depend on the installer `alias rc='ravenclaude update && copilot --plugin-dir …'` — that alias is a Copilot **CLI** launcher, not `bin/rc`.

**Acceptance tests**

- From this checkout: `bash plugins/ravenclaude-core/bin/rc forge-route --self-test` exit 0.
- `bash plugins/ravenclaude-core/bin/rc premise-gate --self-test` exit 0.
- `bash plugins/ravenclaude-core/bin/rc forge-worktree --self-test` exit 0.
- `rc nosuch` still exit 1.

**Pre-build gates**

- `bash -n plugins/ravenclaude-core/bin/rc`
- P1 exists (`rc` keeps using its own `PLUGIN_ROOT`; do not create a third scheme).

**Parallel with P2** once P1 lands. Skip if time-boxed — P2 alone closes claim 19.

---

### P4 — Honesty surface (not a new host)

`depends_on_claims: [2, 4, 5, 13, 14]`

Do **not** add a `vscode-copilot-chat` (or `copilot-chat` / `vscode-copilot`) row to `host-support.json`. There is no verified wiring path for hooks, slash commands, or `CLAUDE_PLUGIN_ROOT`. Gate 154 requires every host × component cell; a new host is a product, not this fix. `hosts.copilot` stays **GitHub Copilot CLI** (claim 2).

Minimal honesty, in places that already talk about Copilot:

- `plugins/ravenclaude-core/skills/forge-pipeline/SKILL.md` — the Chat paragraph from P2.
- `plugins/ravenclaude-core/knowledge/copilot-cli-customization.md` §3 (skills) — one dated note: VS Code Chat/agent mode can *load* project skills from `.claude/skills` (claims 3, 5, `[docs-verified 2026-08-14]`) but is **not** the `copilot` host row; helper scripts resolve via `resolve-plugin-root.sh`, not `${CLAUDE_PLUGIN_ROOT}`.
- Optional one-liner in `plugins/ravenclaude-core/CLAUDE.md` packaging-move milestone (v0.263.0) pointing at v0.265.0 as the Chat-resolution follow-up.

Any new “VS Code Copilot Chat supports / does not support X” sentence **must** carry a provenance marker or Gate 208 (`check-host-capability-citations.py`) will fail.

**Acceptance tests**

- `python3 scripts/check-host-support.py` exit 0 (host set unchanged).
- `python3 scripts/check-host-capability-citations.py` exit 0.
- No new `hosts.` key.

**Pre-build gates**

- Gate 154 + Gate 208.
- Do not run `scripts/generate-copilot-plugin.py` unless `copilot/AGENTS.md` is edited (it is not in this plan).

---

### P5 — Version, changelog, Gate 211

`depends_on_claims: []`

User-visible skill + helper change.

| surface | edit |
|---|---|
| `plugins/ravenclaude-core/.claude-plugin/plugin.json` | `0.264.0` → `0.265.0` |
| `.claude-plugin/marketplace.json` `ravenclaude-core` entry | same |
| `plugins/ravenclaude-core/CHANGELOG.md` | new top `## 0.265.0` (file exists — keep it current) |
| `scripts/audit-gates.sh` | **Gate 211**: `resolve-plugin-root.sh --self-test` plus a must-fail mutant (delete the three-file conjunct; assert exit 2) and a must-pass on this checkout with `CLAUDE_PLUGIN_ROOT` unset |
| `plugins/ravenclaude-core/CLAUDE.md` | short milestone, not a restatement of the skill |

**No** `.repo-layout.json` change. **No** new top-level dir. **No** `generate-dashboards.py` / `generate-copilot-plugin.py` regen.

**Acceptance tests**

- `python3 -m json.tool` on both manifests.
- `scripts/check-marketplace-claims.py` (version alignment) exit 0.
- `scripts/audit-gates.sh --check 211` pass + fail fixtures (match Gate 210’s `--check` registration pattern).
- `npx prettier@3.9.4 --write` on any touched JSON; ruff N/A unless a `.py` is added (it is not).

**Pre-build gates**

- P1–P4 landed or explicitly waived (P3 may be waived).
- `scripts/audit-gates.sh` whole suite before push (AGENTS.md step 5).

---

### P6 — Consumer replay (DoD, not a live Chat promise)

`depends_on_claims: [12, 18, 19]`

Scratch consumer after a simulated install:

1. Skill symlink present.
2. `CLAUDE_PLUGIN_ROOT` unset.
3. Resolver prints plugin root.
4. `python3 "$ROOT/scripts/forge-route.py" --self-test` exit 0.
5. `python3 "$ROOT/scripts/premise-gate.py" --self-test` exit 0.
6. `bash "$ROOT/scripts/forge-worktree.sh" --self-test` exit 0.

Optional owner-only: same four commands inside a real VS Code Copilot Agent terminal. **Not** a CI gate (no VS Code in CI). Failure of the optional probe does not reopen P1 if the scratch replay is green.

**Acceptance tests** = the six steps above in CI-able scratch (Gate 211 can embed 1–6).

**Pre-build gates**

- P2 citations name the resolver.
- Scratch install from claim 12 still valid or re-created.

---

### Follow-on (not MVP) — installer pointer for `cp -r`

`depends_on_claims: [6, 12, 17, 19]`

Only if a no-symlink / Windows `cp -r` consumer is observed in the wild: write a gitignored machine-local `<project>/.ravenclaude/plugin-root` from `wire_plugin_skills`, and teach the resolver one extra candidate. Do **not** ship this in the 0.265.0 close. Do **not** commit absolute marketplace paths into any consumer template.

---

## 5. Dependency DAG

```
P0 record G3b exits (C12 already settled; C10 design-around)
 └── P1 resolve-plugin-root.sh
      ├── P2 citations          ┐
      ├── P3 rc verbs (optional)├── parallel
      └── P4 honesty notes      ┘
           └── P5 version + Gate 211
                └── P6 scratch replay (fixtures may live in Gate 211)
```

| | blocks | parallelizes with |
|---|---|---|
| P0 | everything (documentation only — not a live-Chat gate) | — |
| P1 | P2, P3, P4, P5 | — |
| P2 / P3 / P4 | P5 | each other |
| P5 | merge | P6 fixtures may be written in P5 |
| P6 | merge (DoD) | — |

**Critical path:** P0 → P1 → P2 → P5 → P6.

P3 is skippable. P2 alone closes claim 19. P4 is small and should not slip — a fix that still lets `host-support.json` be read as “Copilot = Chat” is how MH-27-shaped lies start.

P0 does **not** wait on a live VS Code session. Misreading it as “open Chat first” would over-serialize; the design-around is the point.

---

## 6. Risk matrix

| Risk | Mitigation |
|---|---|
| Claim 10 false (Chat actually sets the var) | Dual-path resolver; Claude path is identity when valid. No rewrite abort needed. |
| Relative `readlink` on the skill symlink | Resolver normalizes against `.claude/skills/` (and `.agents/skills/`). |
| `cp -r` install (no symlink) | MVP: exit 2, do not invent a path. Follow-on pointer only if observed. |
| Skill context bloat if helpers are markdown-linked | Never relative-link helper bodies (claim 15). |
| Resolver becomes a second source of truth vs Claude env | Prefer `$CLAUDE_PLUGIN_ROOT` when the three-file conjunct hits. |
| Over-building a VS Code host | No new `host-support.json` key. Honesty notes only. |
| Reopening claim 8 as a mixed-citation bug | Stale. #915 already moved G3b onto `CLAUDE_PLUGIN_ROOT`. Do not “fix” it. |

---

## 7. Out of scope / what we will NOT claim

- VS Code Copilot Chat will **not** become a full Claude Code host. No `/forge` slash command (claims 13, 14), no plugin-dir, no PreToolUse tribunal in Chat, no `CLAUDE_PLUGIN_ROOT` contract from Microsoft.
- We will **not** claim the three helpers “ship inside the skill.” They ship inside the plugin `scripts/` directory and become *resolvable*.
- We will **not** port FORGE to a no-Bash Chat pane. Terminal is required (claim 18). A Chat-only, no-shell environment remains (b), accepted.
- We will **not** change gate semantics, depth ladder, or the tribunal.
- We will **not** add `vscode-copilot-chat` (or similar) to `host-support.json`.
- We will **not** retarget dashboard / set-posture / branch-archive / decision-review citations in this PR.
- We will **not** rewrite `gates-standard.md` / `thing-decide.py` in this PR.
- We will **not** claim the original “routing exists / premise-worktree missing” split as a shipping product (claim 16).
- We will **not** treat a missing `ravenclaude install` as this bug if `.claude/skills/forge-pipeline` is absent — that *is* (c), and the fix is “run install,” not P1.
- We will **not** plan a “fix C8” as if the old marketplace-root citation still ships here.

---

## 8. Version / layout / regen

- **Bump:** `ravenclaude-core` `0.264.0` → `0.265.0` in `plugin.json` **and** `marketplace.json` (CI fails on drift).
- **CHANGELOG:** new `## 0.265.0` at top of `plugins/ravenclaude-core/CHANGELOG.md`.
- **Layout:** new file only under `plugins/ravenclaude-core/scripts/` — already allowed. No `.repo-layout.json` edit.
- **Regen:** none. Adding one script does not change a counted agent/skill inventory. `generate-copilot-plugin.py` omits skills by design; do not `--check`-fail ourselves by touching `copilot/`.
- **Migration:** none for Claude Code (`CLAUDE_PLUGIN_ROOT` still wins). Consumer Chat: `ravenclaude update` then reload skills. No consumer-repo file overwrite.
- **PR:** `fix/ravenclaude-core-copilot-forge-helpers` (ships inside `plugins/` → PR, not docs-to-main).
- **Gate slot:** **211** (210 is the latest registered in `audit-gates.sh` this session).

---

## 9. Definition of done (G8)

A reader can say: *it was (d), with an honest (b) remainder — Chat is not Claude Code, but the three helpers resolve without `${CLAUDE_PLUGIN_ROOT}`.*

Concrete:

- [ ] P0 recorded: C12 settled; C10 design-arounded; C8 not a build input.
- [ ] `resolve-plugin-root.sh --self-test` green; partial set is exit 2; works with the var set **or** unset.
- [ ] Skill + `forge.md` (+ `reference/premise-gate.md` classify path) invoke via resolver; Gate 187 clean.
- [ ] Unset-var scratch replay runs all three `--self-test`s.
- [ ] Host map unchanged; Gate 154/208 clean. No `vscode-copilot-chat` row.
- [ ] Versions aligned at 0.265.0; CHANGELOG current; Gate 211 has pass + fail fixtures.
- [ ] No claim that VS Code Chat is a supported FORGE host.
- [ ] No FORGE semantics / depth-ladder / tribunal change.
