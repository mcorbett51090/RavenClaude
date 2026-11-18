# Research pass log (2026-11-16, UTC)

Four passes. Pass 4 was a deliberate search for facts that would change the recommendation. It did not find one.

## Pass 1 — is there an M6 Mac mini, and what are the base specs

- Apple newsroom, 2026-08-25: M6 and M5 Pro Mac mini, pre-order that day, availability 2026-09-22, "macOS 27" in the announcement. https://www.apple.com/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/
- Specs page and support HT 128108: 12-core CPU (2 super, 4 performance, 6 efficiency), 12-core GPU, 16 GB at 153 GB/s, 24/32 GB at 170 GB/s, 256 GB SSD base, Thunderbolt 4 rear, USB 3 front, 2.5 Gb Ethernet, 155 W supply rating, 5 dBA idle with a "may vary" footnote. The ECMA table on the same page is an M5 Pro 18-core / 48 GB / 8 TB config. https://www.apple.com/mac-mini/specs/ https://support.apple.com/en-us/128108
- Power table, published 2026-09-21, row for M6 / 16 GB / 256 GB: 4 W idle, 70 W CPU max, from the wall. M4 mini on the same page: 4 W / 65 W. https://support.apple.com/en-us/103253
- MacRumors 2026-09-22 and IT Home 2026-09-24: soldered single NAND on the 256 GB model; one Blackmagic run, 3,216.8 MB/s read and 3,000.2 MB/s write, about half the 512 GB M6. https://www.macrumors.com/2026/09/22/new-mac-mini-ssd-cant-be-removed/ https://www.ithome.com/1/006/536.htm

Pass 1 verdict: the machine is shipping, and the base SKU is the one in the request. Large.

## Pass 2 — macOS service, FileVault, the two-VM license, the runner plist

- `actions.runner.plist.template` on `actions/runner` main: `RunAtLoad`, no `KeepAlive`, `ProcessType` Interactive, `SessionCreate`. https://github.com/actions/runner/blob/main/src/Misc/layoutbin/actions.runner.plist.template
- GitHub's service doc: custom launchd must exec `runsvc.sh`. https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application
- actions/runner#1959: user agent reported not to load without a GUI login (older macOS; not re-tested here). https://github.com/actions/runner/issues/1959
- Apple login-window help: FileVault turns automatic login off. https://support.apple.com/guide/mac-help/a-login-window-start-mac-mchlp1158/mac
- macOS 27 SLA §2B(iii): still two additional virtual copies, for development, test, macOS Server, or personal non-commercial use. https://www.apple.com/legal/sla/docs/macOS27.pdf
- actions/runner v2.338.2 (2026-10-26) publishes both `osx-arm64` and `linux-arm64` tarballs. https://github.com/actions/runner/releases/tag/v2.338.2
- Live `commerce-ci.yml` on the website repo: `RUNNER_OS` must be Linux, then the legacy `box-…` name regex. Pending pattern is in website PR 1481.

Pass 2 verdict: large. The live guard, not the hardware, is what rules out a native macOS runner for current jobs.

## Pass 3 — VMs, caches, native modules, vitest, the website package

- `VZVirtualMachineConfiguration.memorySize`: the host reserves a virtual range and allocates guest pages on demand. https://developer.apple.com/documentation/virtualization/vzvirtualmachineconfiguration/3656404-memorysize
- apple/container and apple/containerization: one lightweight VM per Linux container; a per-user service start. https://github.com/apple/container/ https://github.com/apple/containerization/
- actions/runner-images#13565: the report says GitHub-hosted macOS images leave nested virtualization off, which keeps `apple/container` off those images. A bare-metal mini is the case that report says can run it.
- npm/cli#1484: concurrent installs sharing one cache corrupt it. The issue's own workaround is a cache directory per job. https://github.com/npm/cli/issues/1484
- esbuild optional per-platform packages, including `darwin-arm64` and `linux-arm64`. https://github.com/evanw/esbuild/pull/1621
- `commerce/package.json` on main: esbuild 0.28.2, sharp ^0.35.5, playwright-core ^1.65.0, wrangler ^4.158.0, vitest ^5.1.0, node >=22.12.0.
- vitest `maxWorkers` defaults to all available parallelism outside watch mode. `VITEST_MAX_WORKERS` overrides it in current `resolveConfig.ts`. A trailing `%` is parsed as an integer (vitest#9631). https://vitest.dev/config/maxworkers https://github.com/vitest-dev/vitest/blob/main/packages/vitest/src/node/config/resolveConfig.ts
- Les Numériques: power button on the underside; their watt and decibel figures are for a review unit whose memory and SSD size the fetched text does not state. https://www.lesnumeriques.com/ordinateur-de-bureau/apple-mac-mini-m6-p78713/test.html

Pass 3 verdict: large. This is where the runner count, the cache layout, and the job list came from.

## Pass 4 — saturation

Looked for anything that would move the recommendation, and for numbers Apple might have published that pass 1 missed.

- Apple's specs and the power table do not list a CPU GHz, a per-core wattage, an SSD MB/s for the 256 GB SKU, or a NAND endurance figure. EveryMac's ~4.8 GHz is third-party. Ars Technica (2026-09) reports `powermetrics` CPU power stuck at 0 on M6, so that tool does not fill the gap. https://arstechnica.com/gadgets/2026/09/apple-m6-mac-mini-review-300-price-hike-spoils-a-nice-upgrade/
- The actions/runner releases list still had v2.338.2 (2026-10-26) at the top. No newer release on that page.
- The macOS 27 license's two-VM sentence is the same rule as Tahoe 26, not a new cap and not a lift of the cap.
- `apple/container` still starts as a per-user service, which does not change the choice of a resident Lima VM under a LaunchDaemon.
- No published PSS for a Commerce CI shard on arm64. That remains the gate for `lane-slow`, not a number to invent.

Pass 4 verdict: **nothing that changes the recommendation.** Stop.
