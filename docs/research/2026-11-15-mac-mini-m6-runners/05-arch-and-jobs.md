# 05: Which jobs can run on this machine

Checked 2026-11-16 against `commerce/package.json` and the runner guard in `.github/workflows/commerce-ci.yml` on `main`.

## Three architectures, and they are not interchangeable

| | `linux` / `x64` (the box) | `linux` / `arm64` (the VM) | `darwin` / `arm64` (the Mac itself) |
|---|---|---|---|
| Commerce CI guard | Allowed, if the name matches | Allowed, if the name matches | Refused. The guard exits on `RUNNER_OS` |
| Case sensitivity | Case-sensitive filesystem | Case-sensitive filesystem | Default APFS is case-insensitive. A test can pass here and fail on Linux |
| Shell | bash is bash 4+ | bash is bash 4+ | `/bin/bash` is 3.2. Scripts that need bash 4 fail, or silently do the wrong thing |
| Native packages | `@esbuild/linux-x64`, `@img/sharp-linux-x64`, workerd linux-x64 | the `linux-arm64` twins of those packages | the `darwin-arm64` twins |
| Playwright | The baselines this suite already has | Chromium arm64, different fonts and rendering from the box | A third browser build |

The authoritative result for a shard, a build, or a browser test stays on the box. The mini is extra capacity for jobs that have been shown to agree with the box, plus the light jobs that do not compile native code.

## What `package.json` actually depends on

Read from `commerce/package.json` on main, 2026-11-16. Versions are ranges; `npm ci` installs whatever the lockfile resolved.

| Package | In package.json | Why the architecture matters |
|---|---|---|
| `astro` `^5.6.0` | dependency | Pulls Vite, and Vite pulls esbuild and often Rollup. Both ship per-platform optional packages |
| `esbuild` `0.28.2` | devDependency, exact | Optional dependencies `@esbuild/darwin-arm64`, `@esbuild/linux-arm64`, `@esbuild/linux-x64`, and the rest. npm installs the one matching the current OS and CPU. `npm ci --omit=optional` installs none, and esbuild then has no binary ([esbuild's optionalDependencies change](https://github.com/evanw/esbuild/pull/1621)) |
| `sharp` `^0.35.5` | dependency | `@img/sharp-linux-arm64` plus `@img/sharp-libvips-linux-arm64`, and the darwin-arm64 pair. Prebuilt. No Xcode if the right optional package is in the lockfile |
| `playwright-core` `^1.65.0` | devDependency | The npm package is not the browser. Browsers download separately into `PLAYWRIGHT_BROWSERS_PATH` |
| `wrangler` `^4.158.0` and `@astrojs/cloudflare` | dev / dependency | Pull `@cloudflare/workerd`, which publishes `linux-arm64` and `darwin-arm64` builds. The November research already noted the linux-arm64 package |
| `vitest` `^5.1.0` | devDependency | JavaScript, plus whatever the suite imports (sharp, for image tests) |
| `jpeg-js`, `qrcode`, `linkedom`, `jose` | various | Pure JavaScript. Safe on any of the three |
| Node | `engines.node` `>=22.12.0` | Install a current 22.x arm64 build in the guest `[verify-at-use]` |

Rollup is not a direct dependency. It arrives through Astro / Vite, as `@rollup/rollup-linux-arm64` or `@rollup/rollup-darwin-arm64`, same optional-dependency pattern as esbuild.

The lockfile was not fully read in this session (it is large, and the question is empirical). The dry-run is the test that matters:

```bash
npm ci
node -e "require('esbuild'); require('sharp')"
```

A failure that names a missing `@esbuild/linux-arm64` or `@img/sharp-*` means the lockfile was produced without that platform's optional entry. The repair is to regenerate the lock entry so the platform packages are recorded, on a branch, and to re-run `npm ci` on the box as well so the x64 entries stay. A machine-local `npm install` of one platform package leaves every other machine broken.

## Job by job

| Job | On the mini? | Why |
|---|---|---|
| `changes`, alerts, factory event jobs (`lane-fast`) | Yes, after the name guard accepts `rp-macmini-fast-1` | Short bash and Node. No native build. Still Linux, because of the guard |
| Static checks, unit tests that are not the browser matrix (`lane-medium`) | After `npm ci` and one run whose pass/fail matches the box | sharp and esbuild must load. Path and timer tests can still differ; one green comparison run is the bar |
| `build` (Astro) | Same bar as the medium tests, and not on day one | Needs esbuild, sharp, and workerd. A successful `astro build` in the VM, compared with the box's build, is the evidence |
| One vitest shard | Only with `lane-slow` on a single runner, after the build bar is met, and with `VITEST_MAX_WORKERS=2` | One shard at a time. The other three stay on the box. Faster cores can expose races the box hides, and can hide timeouts the box hits. "It finished" is not "it matches" |
| Portal / Playwright matrix | No | Rendering, fonts, and screenshots differ between x64 Linux and arm64 Linux. Keep it on the box. That is also why `lane-slow` stays off this machine while Playwright shares that label |
| Anything with `container:` or `services:` | No | No Docker daemon in the recommended setup |
| Deploy, secrets, `raven-deploy`, `raven-secrets` | No | Different runners, on the Yoga. See [06](06-security-names-and-comparison.md) |
| A coding-agent Actions job | Only as the one medium slot, and only if that job's workflow accepts this name and `RUNNER_OS=Linux` | A local agent on the Mac is not a runner. It shares the 16 GB, so it should not overlap a medium job ([04](04-sizing-and-storage.md)) |
| Native macOS, including signing | Not with these labels | Needs a workflow that does not use this guard |

## Determinism, beyond the native binary

- **Filesystem case.** Run the suite in the VM, where the filesystem is case-sensitive, like the box. A case-sensitive APFS volume is the workaround only if a native macOS experiment is ever required.
- **Timers.** The M6's fast cores make a 20 s timeout less likely to trip and a race more likely to show. `RP_TIMEOUT_SCALE` is already a repo variable (the November finding F2). Do not add a third timeout mechanism on this host.
- **`process.platform` branches.** Any test that snapshots a path or an error string that includes the OS will differ on darwin and match on linux-arm64. Another reason the guest is Linux.
- **Lockfile optional dependencies.** npm records every platform's optional package when the installing npm is recent, and it can omit them when it is not. The dry-run is the check. Do not assume the box's lockfile already contains `linux-arm64` without seeing `npm ci` succeed.
