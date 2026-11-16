# Sources (checked 2026-11-16 unless noted)

## Apple, this machine

- Newsroom, 2026-08-25, M6 and M5 Pro Mac mini, shipping 2026-09-22, macOS 27: https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/
- Tech specs: https://www.apple.com/mac-mini/specs/
- Support specs (HT 128108), including the ECMA acoustic footnote: https://support.apple.com/en-us/128108
- Power and thermal output, the 16 GB / 256 GB M6 row, published 2026-09-21: https://support.apple.com/en-us/103253
- macOS 27 software license, §2B(iii), two virtual copies: https://www.apple.com/legal/sla/docs/macOS27.pdf
- Login window, FileVault disables automatic login: https://support.apple.com/guide/mac-help/a-login-window-start-mac-mchlp1158/mac
- Mac User Guide, titled for macOS 27: https://support.apple.com/guide/mac-help/set-sleep-and-wake-settings-mchlp2401/mac
- `VZVirtualMachineConfiguration.memorySize` (host reserves virtual memory, allocates on demand): https://developer.apple.com/documentation/virtualization/vzvirtualmachineconfiguration/3656404-memorysize
- `pmset(1)` on the machine is the source for the energy keys. Read it there `[verify-at-use]`

## Third-party hardware measurements

- MacRumors, 2026-09-22, soldered NAND and the AAPL Ch. Blackmagic numbers for 256 GB versus 512 GB: https://www.macrumors.com/2026/09/22/new-mac-mini-ssd-cant-be-removed/
- IT Home, 2026-09-24, the same AAPL Ch. table: https://www.ithome.com/1/006/536.htm
- Les Numériques, M6 review (power, chassis temperature, fan, power-button placement; SKU not stated in the fetched text): https://www.lesnumeriques.com/ordinateur-de-bureau/apple-mac-mini-m6-p78713/test.html
- Ars Technica, 2026-09, `powermetrics` CPU power reads 0 on M6: https://arstechnica.com/gadgets/2026/09/apple-m6-mac-mini-review-300-price-hike-spoils-a-nice-upgrade/
- EveryMac's ~4.8 GHz note is third-party software, not an Apple spec, and is not used as one: https://everymac.com/systems/apple/mac_mini/specs/mac-mini-m6-12-core-cpu-12-core-gpu-2026-specs.html

## GitHub Actions runner

- Configure the service (`svc.sh`, custom service via `runsvc.sh`): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application
- Launchd template (no `KeepAlive`, `ProcessType` Interactive, `SessionCreate`): https://github.com/actions/runner/blob/main/src/Misc/layoutbin/actions.runner.plist.template
- actions/runner#1959, LaunchAgent needs a GUI login: https://github.com/actions/runner/issues/1959
- Lost communication when the host sleeps or the network drops: https://github.com/actions/runner/issues/3862
- v2.338.2 release, 2026-10-26, includes `actions-runner-osx-arm64` and `actions-runner-linux-arm64`: https://github.com/actions/runner/releases/tag/v2.338.2
- Secure use of self-hosted runners: https://docs.github.com/en/actions/reference/security/secure-use
- This repo's November research, which this pack extends: [../2026-11-15-self-hosted-runners/](../2026-11-15-self-hosted-runners/README.md)

## Virtualization

- Tart and the two-VM limit: https://github.com/cirruslabs/tart/issues/237
- apple/container: https://github.com/apple/container/
- apple/containerization (a VM per container, Virtualization.framework on the Mac): https://github.com/apple/containerization/
- GitHub-hosted macOS images cannot run `apple/container` (no nested virtualization): https://github.com/actions/runner-images/issues/13565

## Node, npm, vitest, native packages

- npm/cli#1484, cache corruption when several installs share a cache: https://github.com/npm/cli/issues/1484
- esbuild optional per-platform packages: https://github.com/evanw/esbuild/pull/1621
- vitest `maxWorkers`: https://vitest.dev/config/maxworkers
- vitest v4 rename of `VITEST_MAX_THREADS` / `VITEST_MAX_FORKS` to `VITEST_MAX_WORKERS`: https://v4.vitest.dev/guide/migration
- vitest `resolveConfig.ts` applying `VITEST_MAX_WORKERS`: https://github.com/vitest-dev/vitest/blob/main/packages/vitest/src/node/config/resolveConfig.ts
- Percentage in `VITEST_MAX_WORKERS` is parsed as an integer: https://github.com/vitest-dev/vitest/issues/9631
- `@cloudflare/workerd-linux-arm64`, from the November research: https://www.npmjs.com/package/@cloudflare/workerd-linux-arm64

## This factory's files, read 2026-11-16

- `mcorbett51090/RavenPower-Website` `.github/workflows/commerce-ci.yml` on `main`: the Linux-only runner guard and the legacy name regex
- `commerce/package.json` on `main`: astro, esbuild 0.28.2, sharp ^0.35.5, playwright-core, wrangler, vitest ^5.1.0, `engines.node` `>=22.12.0`
- Website PR 1481, `docs/RUNNER-FLEET-GUIDE.md` on `docs/runner-fleet-guide-2026-11-15`: the pending `rp-<host>-<lane>-<n>` pattern, the lane table, and the Yoga label finding
