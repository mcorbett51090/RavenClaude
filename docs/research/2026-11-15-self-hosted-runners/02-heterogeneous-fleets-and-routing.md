# 02: Mixed fleets (different machine types and sizes) and job routing

## How GitHub actually picks a runner

From the [self-hosted runners reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners) and [choosing the runner for a job](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job) (checked 2026-11-15):

- `runs-on: [a, b, c]` matches only runners that have **all** of `a`, `b`, `c` (AND). There is **no OR, no negation, and no preference order.**
- An online, idle runner that matches gets the job. If it doesn't pick the job up within **60 s**, the job is requeued.
- If nothing matches, or every match is busy or offline, the job **waits**. After **24 h** it fails. A typo'd label doesn't fail fast; it hangs.
- `runs-on` may be a variable or a `fromJSON(vars.X)` array, which lets you re-route a lane without editing workflows.
- `runs-on: { group: …, labels: … }` exists, but **runner groups are organisation-only**. A user-owned repo has only repo-level runners plus labels ([changelog](https://github.blog/changelog/2024-10-17-actions-runner-groups-now-available-for-organizations-on-free-plan/)).
- Default labels are `self-hosted`, OS (`Linux`/`macOS`/`Windows`), and arch (`X64`/`ARM64`). `--no-default-labels` drops them. ARC scale sets don't carry `self-hosted`.
- Labels are not a capacity signal. GitHub has no idea a runner is small.

## Consequences

1. **Labels must say what a runner can *take*, not where it lives.** If a 1.5-CPU sandbox runner and an 8-core box runner share `[self-hosted, box, web]`, heavy jobs land on the sandbox whenever it is idle first. Name host and lane separately:
   - **lane / capacity** labels (what the job needs): `lane-light`, `lane-web`, `lane-heavy`, `lane-macos`, and also `mem-4g`/`mem-8g` if you want them
   - **host** labels (for debugging and pinning): `host-box`, `host-macmini`, `host-mbp`, `host-yoga`
   - **trust** labels (who may run here): `trust-pr` (untrusted PR code ok), `trust-secrets` (secret lane), `trust-deploy` (deploy only, ephemeral)
   - arch and OS come free (`X64`/`ARM64`, `Linux`/`macOS`)
2. **Superset labelling gives you overflow without OR.** A big runner carries `lane-heavy` *and* `lane-web` *and* `lane-light`. A small one carries only `lane-light`. Light jobs (`[self-hosted, lane-light]`) can run anywhere, heavy jobs only on big runners. That's a one-way fallback: light work spills onto big machines, never the reverse.
3. **Limit heavy-job concurrency per host with "label tokens".** Every runner takes any job it matches, so a host with 12 runners can be handed 12 heavy builds at once. Give `lane-heavy` to only *k* of that host's runners, where *k* is how many heavy jobs it can run in parallel (see [04](04-resource-limits-and-sizing.md)). The rest carry only `lane-web`/`lane-light`. A label is a concurrency semaphore that costs nothing to run.
4. **Preference ordering needs one of these:**
   - a **picker job**: a tiny first job on a light lane decides the label set (for example by reading the runners API, or an input) and outputs it. Later jobs use `runs-on: ${{ fromJSON(needs.pick.outputs.labels) }}` against an allowlist. Listing runners needs a token with Administration read, and the default `GITHUB_TOKEN` can't do it, so keep that token out of PR-triggered jobs.
   - **scale-set capacity**: each host advertises `maxCapacity` and GitHub spreads load accordingly ([01](01-autoscaling-and-ephemeral.md)).
   - **GARM pool priority plus `pack`**: true "fill A, then B".
5. **Separate trust lanes by label sets that never overlap.** Deploy and secrets runners should carry labels no PR job asks for, and should not carry the shared lane labels. Hard-code their `runs-on` (no `vars.*` override).

## Runner-name guards vs labels

- Labels decide **where a job may go**. A name guard (an in-job step that checks `runner.name` against a regex) is **defence in depth**: it catches a mis-set routing variable or a stray runner that happens to carry the right labels.
- Both are set by whoever registers the runner, so neither one authenticates a host. The guard's value is catching mistakes, not stopping an attacker who can already register runners.
- Name guards break when you add new machine types. Every new naming scheme means editing the regex everywhere it's copied (we hit this). Cheaper designs:
  - one structured scheme, `<fleet>-<host>-<lane>-<n>` (for example `rp-macmini-web-1`), so the guard is a single stable pattern with an allowlist of hosts
  - keep the guard in **one** shared script or composite action, not copied into every workflow
  - check what actually matters: `runner.environment == 'self-hosted'`, **not** a deploy or secrets name for PR jobs, and, for trust lanes, an expected label set written to a file at registration (`.runner_labels`)

## Heavy vs light job routing table (template)

| Job type | Typical need | Lane label | Allowed hosts |
|---|---|---|---|
| Lint, format, small scripts, bots, event fan-out | <0.5 GB, 1 core, short | `lane-light` | any, laptops included |
| Unit tests, small builds, agent jobs (CLI and API calls) | 0.5–2 GB, 1–2 cores | `lane-web` | box, Mac mini Linux VM |
| Full test matrix shards, bundlers, Playwright/browsers | 2–4 GB, 2–4 cores, bursty | `lane-heavy` | box (k slots), Mac mini Linux VM (1–2 slots) |
| macOS or iOS builds, signing | Xcode, keychain | `lane-macos` | Mac mini (native or Tart) |
| Deploy, secrets | isolation | `trust-deploy` / `trust-secrets` | a dedicated ephemeral runner, never a PR host |
