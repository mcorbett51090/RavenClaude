# 03: macOS and Apple Silicon runners

## Options on one Mac

| Option | Isolation | Parallel slots | Notes |
|---|---|---|---|
| Native runner on macOS (`osx-arm64` tarball) | none, shares the user's machine | as many runner processes as RAM allows | fastest; state persists; needs a dedicated non-admin user; keychain care for signing |
| **Tart** VMs (Cirrus Labs) + Tartelet / own loop | a VM per job, ephemeral | **max 2 macOS VMs per host** | clone → boot → register → 1 job → delete. Two VMs run about 12% slower than one ([Tartelet](https://github.com/framna-dk/tartelet)) |
| **Linux arm64 VM** (Lima, Colima, OrbStack, UTM, all on Virtualization.framework) | a VM; runners inside can be ephemeral | not capped by Apple's limit | the right home for general Linux CI on a Mac; Docker works inside |

- The two-VM cap is **macOS guests only**. It's in the macOS EULA ("up to two (2) additional copies or instances … within virtual operating system environments") and enforced by Virtualization.framework ([tart#237](https://github.com/cirruslabs/tart/issues/237), [apple/container#234](https://github.com/apple/container/discussions/234), [Joseph Duffy](https://josephduffy.co.uk/posts/self-hosting-macos-github-runners)).
- Linux on Apple Silicon is **arm64**. Most Node tooling is fine (Cloudflare ships `@cloudflare/workerd-linux-arm64`). Watch for x64-only binaries, Docker images without arm64 variants, and lockfiles missing optional native packages for the other arch ([ARM gotchas](https://dev.to/kalemi/github-actions-arm-runners-what-breaks-when-you-switch-1kb2)). Route by the automatic `ARM64`/`X64` labels if a job is arch-sensitive.
- Container jobs (`container:`, `services:`) need **Linux plus Docker**. They won't run on a native macOS runner ([reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners)).

## Keeping a Mac runner up

- `./svc.sh install` on macOS writes a **user LaunchAgent** (`~/Library/LaunchAgents`, RunAtLoad, no KeepAlive). It only runs while that user is logged in. After a reboot, an OS update, or a power cut, the runner stays offline until login, and with FileVault on, a login is required at every boot ([keepmacawake](https://keepmacawake.com/blog/github-runner-mac-sleep), [aipps.dev](https://aipps.dev/articles/self-hosted-mac-mini-runner-github-actions-keychains-xcodes)).
- For a headless Mac mini, use a **LaunchDaemon** in `/Library/LaunchDaemons` with `UserName` set to the runner user, `RunAtLoad`, `KeepAlive`, `ThrottleInterval` ~30 s, started through **`runsvc.sh`** (GitHub requires that entry point for custom services; template at `bin/actions.runner.plist.template`) ([GitHub docs](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application)).
- Sleep:
  - `sudo pmset -a sleep 0` (plus `disksleep 0`) stops idle sleep. On a desktop Mac, also turn on "Start up automatically after a power failure".
  - **A MacBook still sleeps when the lid closes.** `sudo pmset disablesleep 1` keeps it awake system-wide, on battery too. `caffeinate -s` keeps it awake only on AC power. Treat a laptop as a part-time runner either way.
- Network changes (Wi-Fi, VPN) drop the long-poll. The runner reconnects, but a job in flight may be lost ("lost communication with the server", [actions/runner#3862](https://github.com/actions/runner/issues/3862)).

## Sizing a 16 GB Mac mini

- macOS plus the desktop needs about 3–4 GB. That leaves about 12 GB for CI.
- Suggested split: **one Linux arm64 VM at 8 GB / 4–6 vCPU** with 2 `lane-web` runners plus 1 `lane-heavy` token, **plus one macOS slot** (native or one Tart VM at 4 GB) for `lane-macos` and the ephemeral deploy runner if that's where it lives.
- On a 16 GB MacBook used as a laptop: 1–2 `lane-light` runners, only while it's on AC power. No heavy work and no secrets.
