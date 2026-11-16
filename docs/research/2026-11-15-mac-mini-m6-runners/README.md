# Mac mini M6 (16 GB / 256 GB) as a GitHub Actions runner

Research date: 2026-11-16. This is the setup for one specific machine: the base Mac mini with Apple's M6, 16 GB of unified memory, and a 256 GB SSD, running Commerce CI and light coding-agent jobs for `mcorbett51090/RavenPower-Website`.

It builds on [the 2026-11-15 runner research](../2026-11-15-self-hosted-runners/README.md). That doc's "16 GB Mac mini" line assumed a generic 10-core desktop and a macOS runner slot. Two facts change the plan. The machine that shipped is a 12-core M6 with a small soldered SSD, and the live Commerce CI guard accepts **Linux only**. Four research passes were run. The last one found nothing that changes the recommendation ([pass log](passes.md)).

Facts are tagged with the source and the day they were checked. Rows that can move are marked `[verify-at-use]`.

## Files

| File | What it covers |
|---|---|
| [01-hardware.md](01-hardware.md) | What Apple publishes for this SKU, plus the third-party SSD and noise numbers, and what is still unpublished |
| [02-macos-service.md](02-macos-service.md) | launchd, sleep, power loss, FileVault, Gatekeeper, TCC, SSH, Screen Sharing |
| [03-virtualization.md](03-virtualization.md) | Linux VM versus native macOS, the two-macOS-VM license, Tart, Lima, UTM, OrbStack, colima, Docker Desktop, Apple's container tool, Anka, Orka, Cirrus |
| [04-sizing-and-storage.md](04-sizing-and-storage.md) | How many runners 16 GB / 256 GB can hold, vitest workers, per-runner npm caches, the disk budget, external SSD |
| [05-arch-and-jobs.md](05-arch-and-jobs.md) | Which Commerce CI jobs can move, esbuild / sharp / Playwright / workerd, darwin versus linux arm64 versus the x64 box |
| [06-security-names-and-comparison.md](06-security-names-and-comparison.md) | Isolation, the live name guard, power and noise versus the Yoga and the Linux box |
| [sources.md](sources.md) | Every source |
| [passes.md](passes.md) | The pass log |

## Recommendation

**Two runners, inside one Linux arm64 VM. No native macOS runner. No deploy runner. No secrets runner.**

| | `rp-macmini-fast-1` | `rp-macmini-medium-1` |
|---|---|---|
| When it may take jobs | After the pending name-guard change is on main | After `npm ci` succeeds in the VM and one non-browser job matches the x64 box |
| Labels | `host-macmini`, `lane-fast`, `trust-pr` (plus the automatic `self-hosted`, `Linux`, `ARM64`) | those, plus `lane-medium` |
| vitest | `VITEST_MAX_WORKERS=2` in that runner's `.env` | same |
| npm cache | its own directory | its own directory |

The VM is Ubuntu 24.04 LTS arm64 `[verify-at-use]`, **3 vCPU, 6 GB RAM, 48 GB sparse disk**. Three vCPU is the backstop: vitest sizes workers from `os.availableParallelism()` when `VITEST_MAX_WORKERS` is unset, and a VM that sees all 12 cores will start 12 workers inside 6 GB.

Do not register `rp-macmini-slow-1` yet. `lane-slow` is the build, the test-shard matrix, and Playwright. One of those shards may run here later, after an arm64 result matches the box. The other shards stay on the Linux box. Four shards in parallel need four runners; this machine has memory for one heavy job.

Register with `host-macmini` only until the guard change has merged. A runner that already carries `lane-fast` will be handed light jobs, and the **live** guard will fail them. The live regex, copied from `commerce-ci.yml` on main on 2026-11-16, is:

```
^box-((fast|large|web)[0-9]+|raven-(web|light)-[0-9]+)$
```

The same step refuses anything whose `RUNNER_OS` is not `Linux`. The pending change adds `^rp-(box|yoga|macmini|mbp)-(slow|medium|fast)-[0-9]+$` and still requires Linux. This research does not widen either pattern. `box-*` names on the mini would collide with the box fleet and would put this machine on the box's lanes. Don't use them.

## What Matthew does on the machine

These steps need a person at the hardware. The software steps below can be run over SSH after step 4.

1. Put the mini on the rear **2.5 Gb Ethernet** port, not Wi-Fi. The power button is on the underside of the chassis (Les Numériques, 2026 review). A display and keyboard are needed for first boot.
2. Create his own admin account. Create a **standard** user named `ghrunner`. No Apple ID, no iCloud, no browser signed into a personal account, on either user that the runners can reach.
3. Turn on **FileVault**, and turn on **Start up automatically after a power failure**. Apple's login-window help says FileVault turns automatic login off. The reboot test in the runbook is the check for whether SSH answers before a password is typed. Until that test says otherwise, plan on one keyboard unlock after each power cut. That is the trade for keeping a private checkout encrypted at rest.
4. Turn on **Remote Login** and **Screen Sharing** for the admin user, on the home LAN only. Do not forward those ports to the internet. Unplug the display after SSH works.
5. Run the energy commands in [02](02-macos-service.md) once, as admin.
6. Do not install Xcode. Do not install Docker Desktop. Do not register a `raven-secrets` or `raven-deploy` runner here. Those stay on the Yoga.
7. Mint the runner registration token in the website repo's Actions settings, paste it into `config.sh` over SSH, and do not commit it. The token expires in about an hour.
8. Leave the runners labelled `host-macmini` only until the name-guard pull request is on main. Then add `lane-fast`. Add `lane-medium` on the second runner only after the dry-run in [05](05-arch-and-jobs.md).

## Setup runbook

Admin steps are marked. Everything else runs as `ghrunner` on the Mac, then as `ghrunner` inside the VM.

### 1. Keep the Mac awake, and bring it back after power loss

As admin:

```bash
sudo pmset -a sleep 0 disksleep 0 displaysleep 10 \
  womp 1 tcpkeepalive 1 autorestart 1 \
  powernap 0 standby 0 autopoweroff 0
pmset -g
```

`sleep 0` is the system sleep timer. `autorestart 1` is "start up after a power failure". `displaysleep 10` blanks an attached display and does not sleep the system. Read `man pmset` on the machine before changing a key: the man page is the source, and Energy settings in System Settings can reset these after a macOS update `[verify-at-use]`.

`caffeinate -s` is the laptop tool. On this desktop it is only a backup if an update turns sleep back on. A LaunchDaemon that runs `caffeinate -ims` is enough for that backup. The `pmset` line is the setting that has to be right.

### 2. Install the Linux VM

Install Lima from Homebrew as admin (`brew install lima`) `[verify-at-use]`. As `ghrunner`:

```bash
limactl create --name=ci template://ubuntu-24.04
limactl edit ci
```

Set `vmType: vz`, `arch: aarch64`, `cpus: 3`, `memory: 6GiB`, `disk: 48GiB`. Then `limactl start ci`.

Lima is the right tool for one long-lived Linux guest. Tart is the right tool later if a job needs a fresh VM per run. Apple's `container` tool, Docker Desktop, colima, and OrbStack are the wrong host for these runners. The reasons are in [03](03-virtualization.md).

Keep the VM disk on the internal SSD. A rear Thunderbolt 4 disk is the overflow, and only after free space on the internal disk drops below 40 GB. The front USB-C ports are USB 3 at 10 Gb/s, slower than the internal SSD. Details in [04](04-sizing-and-storage.md).

### 3. Start the VM at boot

`svc.sh` on macOS writes a user LaunchAgent. GitHub's template gives that agent `RunAtLoad` and no `KeepAlive`, and [Apple's login-window help](https://support.apple.com/guide/mac-help/a-login-window-start-mac-mchlp1158/mac) says FileVault turns automatic login off. So the thing that starts at boot is a **LaunchDaemon** whose only job is `limactl start ci`, with `UserName` set to `ghrunner`, `RunAtLoad` and `KeepAlive` set, and `ThrottleInterval` around 30 seconds.

The runners themselves are systemd services **inside** the guest, which is the path GitHub documents. They do not use the macOS LaunchAgent.

Reboot, do not log in, and from another machine run `ssh` and `limactl list`. The VM should be running. If it is not, the daemon did not start before the volume unlocked, or `limactl` needs a login session. Fix that before registering any runner. This reboot test is the one that proves the power-loss story.

### 4. Install two runners inside the guest

`limactl shell ci`, then as the guest user. Download the **linux-arm64** runner tarball from the version the repo's own runner-download page offers `[verify-at-use]`. On 2026-11-16 the newest GitHub release was [v2.338.2](https://github.com/actions/runner/releases/tag/v2.338.2) (2026-10-26), and that release publishes `actions-runner-linux-arm64`. Check the checksum on the release page. The runner auto-updates on job assignment; leave that on (the 63-day rule in the [November research](../2026-11-15-self-hosted-runners/05-availability-sleep-updates.md)).

Two directories, two names:

```bash
mkdir -p ~/runner-fast ~/runner-medium
# extract the tarball into each
```

Each `.env`:

```bash
npm_config_cache=/home/ghrunner/runner-fast/.npm
PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
VITEST_MAX_WORKERS=2
```

Use `runner-medium/.npm` on the other runner. A shared npm cache is how this factory got `ETXTBSY` and corrupt tarballs. One Playwright browser directory is fine if a single install holds a lock first. See [04](04-sizing-and-storage.md).

Register each one with a one-hour token, `--name rp-macmini-fast-1` or `rp-macmini-medium-1`, `--labels host-macmini,trust-pr`, and `--unattended`. Add `lane-fast` and `lane-medium` later, as the table at the top says. Then, inside the guest:

```bash
sudo ./svc.sh install ghrunner
sudo ./svc.sh start
```

`./svc.sh install` on Linux is a systemd unit. That is what we want. Do not copy a macOS LaunchAgent plist for these processes.

A job-completed hook (`ACTIONS_RUNNER_HOOK_JOB_COMPLETED`) should kill processes whose working directory is that runner's `_work` and remove leftover children. The website workflow already empties `GITHUB_WORKSPACE` at the start of a self-hosted job. The hook is the matching cleanup at the end. Ephemeral registration (`config.sh --ephemeral`, one job, then a new registration) is the better shape once a **different** machine mints the tokens. The minting credential stays off this Mac. Until that exists, the two persistent guest services are the config.

### 5. Prove the guest before it takes a lane

Inside the VM, on a checkout of the website repo:

```bash
node -p "process.platform+' '+process.arch+' '+require('os').availableParallelism()"
npm ci
```

`process.platform` must be `linux` and `process.arch` must be `arm64`. `availableParallelism()` must be 3. `npm ci` must finish without a missing `@esbuild/linux-arm64`, `@img/sharp-linux-arm64`, or workerd arm64 package. If it fails, the lockfile does not carry that platform's optional dependency, and the fix is a lockfile change on a branch, not a label. Which jobs may then move is in [05](05-arch-and-jobs.md).

### 6. Watch disk and memory

On the Mac, keep at least 40 GB free (`df -h /`). Inside the guest, the medium runner should be idle whenever `MemAvailable` is under 2 GB. A coding-agent session on the Mac host shares the same 16 GB. Pause the VM, or stop the medium runner, while that session is active. One medium CI job and one local agent at the same time is how this machine starts swapping, and the 256 GB SSD is the wrong place for steady swap ([04](04-sizing-and-storage.md)).

## Open uncertainties

| Topic | What is known | What is not |
|---|---|---|
| CPU clocks and per-core watts | Apple does not publish GHz. Ars Technica (2026-09) reports `powermetrics` CPU power stuck at 0 on M6 | A third-party ~4.8 GHz figure (EveryMac) is not a spec. No core-power number is usable |
| SSD speed | One Blackmagic run, reported by MacRumors from AAPL Ch. (2026-09-22): 256 GB about 3.2 GB/s read and 3.0 GB/s write, about half the 512 GB config | Random IO, and IO under memory pressure, were not measured. NAND endurance (TBW) is unpublished |
| Noise under Node CI | Apple: 5 dBA idle, and that figure "may vary by configuration". The ECMA table on the same page was measured on an M5 Pro, 18-core, 48 GB, 8 TB config | No measurement of this SKU running vitest. Fan-on numbers from reviews are other tests or other SKUs |
| Screen Sharing with no display ever attached | SSH and a LaunchDaemon do not need a display | Whether macOS 27 Screen Sharing works on this mini with no display was not verified |
| `VITEST_MAX_WORKERS` on the installed vitest | Current vitest `resolveConfig.ts` on main overrides `maxWorkers` from that env. Commerce pins `vitest` `^5.1.0` | Confirm on the version `npm ci` actually installs. The 3 vCPU cap still holds if the env is ignored |
| macOS 27 build number | The mini ships with macOS 27 (Apple newsroom, 2026-08-25; the user guide is "for macOS 27") | The exact build was not recorded |
| This repo's shard RSS on arm64 | The box fits 2–3 full shards in 16 GB (November research) | Nobody has measured one shard's PSS on this VM. That measurement is the gate for `lane-slow` |
