# 04: How many runners, and where the 256 GB goes

Checked 2026-11-16. The sizing formula in the [November research](../2026-11-15-self-hosted-runners/04-resource-limits-and-sizing.md) still applies. The inputs for this SKU are tighter than that doc's "Mac mini, 16 GB / 10 cores" row, because the cores are not all fast, the disk is 238 GiB and soldered, and the guest memory cap is reserved under load even though the host allocates it on demand ([03](03-virtualization.md)).

## Memory budget

| Consumer | Budget during a job | Notes |
|---|---|---|
| macOS, WindowServer, Lima | 4 GB | The November doc's desktop reserve. Not re-measured on M6 |
| Linux VM cap | 6 GB | What the guest can occupy. Idle is less |
| Headroom | 6 GB | Compression, a spike, or a person using the Mac |
| A local coding agent on the host | taken from the headroom | Stop the medium runner, or stop the VM, while an agent session is active |

One runner runs one job. A Commerce CI test shard is the heavy job. The November research measured the Linux box, also 16 GB, as fitting 2–3 full shards and about 0.4 GB per agent-shaped job. Those numbers are the box, on x64, not this VM. Until a shard's PSS is measured inside the guest, the mini runs **one** medium job and **one** fast job, and it does not run a shard at all.

Fast jobs in this factory (the `changes` probe, alerts, factory events) are bash plus a short-lived Node process, well under 0.5 GB. They can sit beside the medium job. Two medium jobs, or a medium job plus a shard, are the pair that pushes the guest into its own swap and then the Mac into host swap.

## vitest workers

`commerce/package.json` on main (read 2026-11-16) pins `vitest` `^5.1.0` and does not set `maxWorkers` (the November doc, finding F3). Vitest's default when not in watch mode is every CPU `os.availableParallelism()` reports ([vitest maxWorkers](https://vitest.dev/config/maxworkers)).

Current vitest `resolveConfig.ts` on `main` applies `VITEST_MAX_WORKERS` over the configured value (read 2026-11-16). The runner's `.env` is loaded into every job, so:

```bash
VITEST_MAX_WORKERS=2
```

is the cap, with no workflow edit. Confirm it on the version `npm ci` installs. The VM has 3 vCPU so that, if the variable is ignored, the guest reports 3 rather than 12. `VITEST_MAX_THREADS` and `VITEST_MAX_FORKS` are the pre-v4 names; this range is v5.

A percentage in `VITEST_MAX_WORKERS` is parsed as an integer and does the wrong thing ([vitest#9631](https://github.com/vitest-dev/vitest/issues/9631)). Use `2`, not `50%`.

The Yoga sandbox stays at 1 worker. That knob is the proposed website change L4. Until it exists, the Yoga's cap is its cgroup, which Node can over-report (November doc, the libuv nested-cgroup bug). The VM avoids that bug by being a real 3-CPU machine rather than a nested cgroup.

## npm caches, one per runner

The November doc said a shared `~/.npm` is usually fine because the cache is content-addressed. This factory has already hit the case where it is not: concurrent `npm ci` against one cache produced corrupt tarballs and `ETXTBSY` ("text file busy") when one job executed a binary another job was replacing. npm/cli[#1484](https://github.com/npm/cli/issues/1484) is the same failure, and the workaround npm's own issue discusses is a cache directory per job:

```bash
npm_config_cache=/home/ghrunner/runner-fast/.npm
```

and a different path for `runner-medium`. Do not point both runners at `/home/ghrunner/.npm`. Do not share a `node_modules` tree. `npm ci` deletes and recreates the job's own `node_modules`; the race is the cache, and any directory both jobs write.

Playwright browsers are large and read-mostly. One directory, `/opt/ms-playwright`, installed once under `flock`, then `PLAYWRIGHT_BROWSERS_PATH` pointed at it. Two `playwright install` runs at once is the same class of race. The mini should not be the machine that installs those browsers on every job, and it should not run the portal matrix until [05](05-arch-and-jobs.md) says so.

`actions/cache` still uploads to GitHub (10 GB per repo included, billed above that; November doc). Prefer the local per-runner directories. They do not touch that quota.

## Disk budget

Apple's footnote makes the 256 GB SSD about **238 GiB** after the decimal-versus-binary conversion ([01](01-hardware.md)).

| Use | Plan |
|---|---|
| macOS, the admin user, updates, local snapshots | Keep 40 GB aside. Measure with `df -h /` on day one; the installed size of macOS 27 was not published as a single number |
| Free-space floor | Another 40 GB always free. APFS snapshots, a swap file, and a macOS update all land here. Below that, stop taking jobs |
| Linux VM disk | 48 GB sparse cap on the internal SSD. A fresh Ubuntu plus two runner trees, two npm caches, and one Playwright tree should sit nearer 15–25 GB. The cap is the ceiling, not the day-one use |
| Xcode | Do not install. Node, Astro, vitest, esbuild, sharp, and Playwright do not need it. Sharp 0.35 and esbuild 0.28 ship prebuilt binaries. The Xcode Command Line Tools are a fallback if some package falls through to `node-gyp`. Install them only when a build asks, and expect on the order of a gigabyte or two |
| Docker Desktop, image caches | Do not install |
| Time Machine on the internal SSD | Off. It will fill the disk |
| Host Homebrew | Lima, and little else |

That leaves on the order of 100 GiB unallocated after the reserves and the VM cap. It disappears quickly if Xcode or a Docker disk image arrives. The check is `df`, not the arithmetic.

### Cleanup

- Ephemeral runners remove their work directory by construction. Persistent ones rely on the website's "empty the workspace" step plus the job-completed hook in the [runbook](README.md).
- A weekly `npm cache verify` **inside each runner's own cache**, not `npm cache clean --force` on a shared cache.
- `tmutil listlocalsnapshots /` and delete local snapshots if they appear. They show up when Time Machine has ever been on.
- Alert, do not auto-delete the VM, when the Mac has under 40 GB free.

### External SSD

When the internal disk is the thing that is full, add storage on a **rear Thunderbolt 4** port (40 Gb/s). Format it APFS if the Mac will own the volume. Put archives and an overflow Playwright or npm tree there. Keep the VM disk and the runner credentials on the internal SSD: an external disk can be unplugged, and a runner whose disk vanished mid-job fails like a sleep.

The front USB-C ports are USB 3 at 10 Gb/s, below the internal SSD's roughly 3 GB/s sequential write ([01](01-hardware.md)). They are a poor place for the VM disk.

Swap wear is the other storage risk. Steady memory pressure writes the swap file on the internal NAND. Endurance in terabytes written is unpublished, so the control is to stay out of swap rather than to budget a write lifetime nobody has published. The 3 vCPU / 6 GB / two-runner cap is that control.
