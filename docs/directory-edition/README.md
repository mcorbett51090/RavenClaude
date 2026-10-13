# Directory edition of `ravenclaude-core`

A smaller, reviewable build of [`plugins/ravenclaude-core`](../../plugins/ravenclaude-core) for Anthropic's Plugin Directory, generated from the same source so there is one place to change things. It is built by [`scripts/build-directory-edition.py`](../../scripts/build-directory-edition.py), driven by [`ravenclaude-core/manifest.json`](ravenclaude-core/manifest.json), and held to its own claims by Gate 301 ([`scripts/check-directory-edition.py`](../../scripts/check-directory-edition.py)).

## Why a separate edition

The full plugin cannot be submitted as it is. Measured against the Directory's documented checks (2026-10-13):

| Directory rule | Full plugin | Edition |
|---|---|---|
| Repo under 10,000 files | the monorepo has 10,872 | its own repo |
| Plugin at most 512 files (more is a reviewer hold on every version) | 1,871 | 169 |
| No file over 5 MiB (blocks) | `dashboard.html` is 10,992,418 bytes | largest file 69 KB |
| No non-image file over 256 KiB (hold) | five (`CLAUDE.md`, `CHANGELOG.md`, `concepts.json`, `skill-index/SKILL.md`, `dashboard.html`) | none |
| `experimental` must not declare components | `experimental.monitors` | absent |
| `claude plugin validate --strict` | fails on the root `CLAUDE.md` | passes |
| Security scan: undisclosed behaviour | 57 registered hooks, several always on; nested `claude -p`; `bin/` that edits shell startup files | 9 hooks, all measured, all disclosed |

## What the edition is

Agents, skills and commands that the manifest allow-lists **with a reason each**, plus whatever those reference (closure), minus anything the manifest denies. `--explain` prints why each referenced file ships. An executable file that references a denied file is a build failure, not a silent dangling reference.

**Hooks are the part that needs defending, so they get a structural guarantee.** Every shipped hook except the one setup prompt is registered as `bash "${CLAUDE_PLUGIN_ROOT}/hooks/posture-gate.sh" <hook>`. The gate is three lines of code: no `.ravenclaude/comfort-posture.yaml`, exit 0 before the hook starts. That makes "does nothing until you opt in" true by construction rather than by each hook remembering to check. It was chosen after the first measurement showed why per-hook checking cannot be trusted: with payloads shaped like each guard's trigger, `guard-premise.sh`, `guard-memory-compaction.sh` and `guard-foreground-suite.sh` all deny with no posture file.

Which hooks ship is a judgement the manifest records, then a harness checks:

- **Shipped:** nudges and local guards whose posture-present behaviour is advisory text, a counter or a deny.
- **Not shipped:** anything that spawns `claude -p` (the tribunal, the dispatch evaluator, the cheap lane), executes a string from the posture file (`dod-gate.sh`), rewrites a tool's input or output (`explore-tier-pin.sh`, the output sanitizers), pre-approves a call from a repo file (`guard-web-access.sh`), rewrites permission rules from a repo file at session start (`reapply-posture.sh`), launches a server (`dashboard-autostart.sh`), or is specific to another tool.

The reason for the second half: **a posture file in a cloned repo is attacker-controlled input.** A hook that acts on it is a way for a stranger's repo to act on your machine.

## The measurement

[`scripts/directory-edition-hook-audit.py`](../../scripts/directory-edition-hook-audit.py) runs every shipped hook from the built `hooks.json`, in a scratch project under a minimal environment, with a payload for every event and tool it is registered for (including trigger-shaped ones), in two lanes:

- **No posture file:** exit 0, empty stdout, no file created or changed in the project, `HOME`, `TMPDIR` or the plugin, no network, no `claude`.
- **Hostile posture file:** every knob on, with commands, spawns and approvals planted. The posture arrives the way a repo that controls its history can deliver it (the command in one commit, `trusted: true` in a later one). No planted string runs, no `claude` or network, no `allow`/`updatedInput`/`updatedToolOutput`, no write outside `.ravenclaude/`, no edit to `.claude/settings.json`, no missing file inside the plugin.

Network and programs started are observed with `strace` when present. Every check is itself tested against hooks built to misbehave that way, and Gate 301 additionally requires that real `guard-destructive.sh` and real `dod-gate.sh` are classified unsafe, so the payloads and seeds provably reach real triggers. That second half earned its place: its first run showed the hostile lane did not make `dod-gate.sh` execute anything, because `dod-gate.sh` refuses a trust flag written in the same commit as its command. The two-commit delivery above is the fix.

**Limits, stated rather than hidden.** The payloads are a corpus, not a proof over all inputs. The no-posture lane is guaranteed by the shim; the hostile lane is a measurement, so a reviewer should still read the nine hook scripts. In CI without `strace` the syscall lane is NOT RUN (reported, not passed); set `RC_EDITION_REQUIRE_STRACE=1` for the release check. `claude plugin validate --strict` is likewise NOT RUN without the `claude` CLI.

## Day to day

```shell
python3 scripts/build-directory-edition.py --check            # freshness, limits, parity, network, secrets
python3 scripts/build-directory-edition.py --report           # closure breaks, sizes, largest files
python3 scripts/build-directory-edition.py --explain          # why each referenced file ships
python3 scripts/build-directory-edition.py --write-file-list  # refresh file-list.txt after a deliberate change
python3 scripts/build-directory-edition.py --out /tmp/edition # build it
python3 scripts/check-directory-edition.py                    # Gate 301 (about 40 s)
```

`file-list.txt` records paths only, so a version bump or a content edit to a shipped file never churns it; adding or removing a shipped file does, and that diff is the review surface. The edition's version is the source plugin's version (`plugin.json` stays the single source of truth).

## Releasing (owner steps)

Nothing here publishes anything. The Directory needs a **public GitHub repo with the plugin at its root**, so:

1. Create `mcorbett51090/ravenclaude-core` (public; the Directory accepts a private repo while validating, public at publish).
2. Build with `RC_EDITION_REQUIRE_STRACE=1 python3 scripts/check-directory-edition.py`, then `build-directory-edition.py --out <clone>` and commit to the repo's `main` (staging).
3. Move the `release` branch, the one the Directory tracks, only deliberately. `ravenclaude-core` bumps near weekly; tracking `main` would hand the reviewer a new version every time.
4. On claude.ai (paid plan): connect GitHub, install the Claude GitHub App on the repo, run **Validate** in the portal on the private repo and fix every **Blocks**, complete the Data-handling and Compliance steps (the answers are in the edition's `PRIVACY.md`), then **Submit**.
5. After it publishes, install it from the Directory in a clean account and confirm it arrives as `ravenclaude-core@synced`, hooks inert, one prompt line.

**Unknown until step 4 reports** (the portal sits behind the owner's claude.ai login, a route the build did not have): how the portal's scanner treats the hook `comment` keys and the newer hook events (`StopFailure`, `PermissionDenied`, `PostCompact`), whether the substring "claude" in the name draws a brand-confusion hold, and the scan and policy outcome itself. A failed first scan is a rejection, which is why the first listing is the opt-in-only edition. Names are permanent once listed.

## The posture editor the edition points at

The edition's `/dashboard` sends people to the hosted page (`https://mcorbett51090.github.io/RavenClaude/#/settings`) instead of a local server. Observed in headless Chromium on 2026-10-13: the page's YAML preview updates as options change; **Copy** is inside the collapsed **Alternative ways to save** section at the bottom of the YAML panel (the edition's instructions say so); across ten routes the only request off its own origin was one `GET` to `api.github.com/repos/mcorbett51090/RavenClaude/actions/runs`, made when the Guardrails card opens. That is a sample of the page, not an audit of every route.
